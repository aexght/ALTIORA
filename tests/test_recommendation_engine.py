"""
Regression tests for the college recommendation engine (Phase 7A).

Covers:
  * Science and Commerce predictions
  * Multiple states
  * Government / Private ownership preferences
  * Budget handling (incl. the all-"Unknown" fee dataset)
  * Hostel required / not required
  * Travel preference approximation
  * Missing / unverified data handling (never crash, never "Unknown")
  * /predict response contract (existing fields untouched + recommended_colleges)

Run with:  python -m unittest tests.test_recommendation_engine -v
"""

import json
import os
import sys
import unittest

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO)

import app as app_module  # noqa: E402
from recommendation_engine import (  # noqa: E402
    get_datasets,
    normalize_preferences,
    recommend_colleges,
    recommend_colleges_from_prediction,
    classify_college_type,
    WEIGHTS,
)

# The dataset ships with every fee row marked "Unknown" (Not Verified). These
# tests assert the engine tolerates that without dropping colleges.
ALL_FEES_UNVERIFIED = True


def _valid_answers():
    questions = app_module._load_questions_json()
    return {str(q["id"]): q["options"][0]["id"] for q in questions[:40]}


def _science_academic():
    return {
        "class10Percentage": 85,
        "class12Percentage": 88,
        "stream": "Science",
        "electives": ["Mathematics", "Computer Science"],
        "subjectMarks": {
            "English_Marks": 82, "Mathematics_Marks": 90, "Physics_Marks": 85,
            "Chemistry_Marks": 80, "Computer_Science_Marks": 92, "Biology_Marks": 0,
        },
    }


def _commerce_academic():
    return {
        "class10Percentage": 82,
        "class12Percentage": 85,
        "stream": "Commerce",
        "electives": ["Statistics"],
        "subjectMarks": {
            "English_Marks": 80, "Accountancy_Marks": 88, "Economics_Marks": 84,
            "Business_Studies_Marks": 86, "Mathematics_Marks": 0,
            "Statistics_Marks": 90, "Computer_Science_Marks": 0, "Biology_Marks": 0,
            "Chemistry_Marks": 0, "Physics_Marks": 0,
        },
    }


def _predict(academic, preferences=None):
    client = app_module.app.test_client()
    payload = {"academic": academic, "answers": _valid_answers()}
    if preferences is not None:
        payload["preferences"] = preferences
    resp = client.post(
        "/predict",
        data=json.dumps(payload),
        content_type="application/json",
    )
    return resp.status_code, resp.get_json()


class TestEngineData(unittest.TestCase):
    def test_datasets_load(self):
        d = get_datasets()
        # New master dataset architecture
        self.assertGreaterEqual(len(d["colleges"]), 100)
        self.assertGreaterEqual(len(d["college_by_id"]), 100)
        self.assertGreaterEqual(len(d["mapping_by_college"]), 100)
        self.assertGreaterEqual(len(d["colleges_by_domain"]), 10)
        self.assertIn("master_df", d)
        self.assertIn("course_columns", d)
        self.assertIn("is_yes", d)
        self.assertIn("get_area_state", d)

    def test_weights_sum_to_one(self):
        self.assertAlmostEqual(sum(WEIGHTS.values()), 1.0, places=6)

    def test_expected_weight_values(self):
        self.assertEqual(WEIGHTS["course_match"], 0.40)
        self.assertEqual(WEIGHTS["location_match"], 0.20)
        self.assertEqual(WEIGHTS["budget_match"], 0.15)
        self.assertEqual(WEIGHTS["ownership_match"], 0.10)
        self.assertEqual(WEIGHTS["hostel_match"], 0.05)
        self.assertEqual(WEIGHTS["travel_preference"], 0.05)
        self.assertEqual(WEIGHTS["college_type"], 0.05)

    def test_normalize_preferences_defaults(self):
        p = normalize_preferences(None)
        self.assertEqual(p["ownership"], "Both")
        self.assertEqual(p["hostel"], "Doesn't Matter")
        self.assertEqual(p["collegeType"], "Any")
        self.assertEqual(p["travelPreference"], "Anywhere")
        self.assertIsNone(p["maxFee"])
        self.assertEqual(p["state"], "")

    def test_normalize_preferences_snake_and_camel(self):
        camel = normalize_preferences({"maxFee": "120000", "collegeType": "Autonomous"})
        snake = normalize_preferences({"max_fee": "120000", "college_type": "Autonomous"})
        self.assertEqual(camel["maxFee"], 120000.0)
        self.assertEqual(camel["collegeType"], "Autonomous")
        self.assertEqual(snake["maxFee"], 120000.0)
        self.assertEqual(snake["collegeType"], "Autonomous")

    def test_normalize_preferences_invalid_values_fall_back(self):
        p = normalize_preferences({"ownership": "Nonsense", "hostel": 42, "collegeType": "", "travelPreference": None})
        self.assertEqual(p["ownership"], "Both")
        self.assertEqual(p["hostel"], "Doesn't Matter")
        self.assertEqual(p["collegeType"], "Any")
        self.assertEqual(p["travelPreference"], "Anywhere")

    def test_classify_college_type_known_cases(self):
        d = get_datasets()
        by_id = d["college_by_id"]
        # Use first college from master dataset (index 0)
        first_cid = list(d["college_by_id"].keys())[0]
        # Test that classification works without errors
        for cid in list(d["college_by_id"].keys())[:5]:
            result = classify_college_type(d["college_by_id"][cid])
            self.assertIn(result, ["Autonomous", "University", "Affiliated"])


class TestScoringBehavior(unittest.TestCase):
    def test_state_filter_hard(self):
        d = get_datasets()
        karnataka = recommend_colleges(
            "Engineering", preferences={"state": "Karnataka", "ownership": "Both"}, top_n=50
        )
        self.assertTrue(karnataka)
        self.assertTrue(all(c["state"] == "Karnataka" for c in karnataka))

    def test_district_mismatch_keeps_college(self):
        # A district with no exact match must still return colleges (score reduced, not removed).
        recs = recommend_colleges(
            "Engineering",
            preferences={"state": "Karnataka", "district": "Bengaluru", "ownership": "Both"},
            top_n=50,
        )
        self.assertTrue(recs)

    def test_private_ownership_preferred(self):
        priv = recommend_colleges(
            "Engineering", preferences={"state": "Karnataka", "ownership": "Private"}, top_n=50
        )
        gov = recommend_colleges(
            "Engineering", preferences={"state": "Karnataka", "ownership": "Government"}, top_n=50
        )
        self.assertTrue(priv and gov)
        # Private-preference list must rank a private college first.
        self.assertEqual(priv[0]["ownership"], "Private")

    def test_budget_no_rejection_when_fee_unknown(self):
        # All fees are Unknown -> no college may be dropped for budget reasons.
        no_budget = recommend_colleges(
            "Engineering", preferences={"state": "Karnataka", "ownership": "Both"}, top_n=50
        )
        tiny_budget = recommend_colleges(
            "Engineering",
            preferences={"state": "Karnataka", "ownership": "Both", "maxFee": 10000},
            top_n=50,
        )
        self.assertEqual(len(tiny_budget), len(no_budget))

    def test_hostel_required_keeps_college_even_if_unverified(self):
        recs = recommend_colleges(
            "Engineering",
            preferences={"state": "Karnataka", "ownership": "Both", "hostel": "Required"},
            top_n=50,
        )
        self.assertTrue(recs)

    def test_travel_approximation_uses_state(self):
        within = recommend_colleges(
            "Engineering",
            preferences={"state": "Karnataka", "travelPreference": "Within State", "ownership": "Both"},
            top_n=50,
        )
        anywhere = recommend_colleges(
            "Engineering",
            preferences={"state": "Karnataka", "travelPreference": "Anywhere", "ownership": "Both"},
            top_n=50,
        )
        self.assertTrue(within and anywhere)

    def test_missing_domain_returns_empty(self):
        recs = recommend_colleges("Nonexistent Domain", preferences={})
        self.assertEqual(recs, [])

    def test_missing_state_preference_no_filter(self):
        # No state preference -> colleges from many states may appear.
        recs = recommend_colleges("Engineering", preferences={"ownership": "Both"}, top_n=50)
        states = {c["state"] for c in recs}
        self.assertGreater(len(states), 1)

    def test_scores_are_normalized_0_100(self):
        recs = recommend_colleges(
            "Engineering", preferences={"state": "Karnataka", "ownership": "Both"}, top_n=5
        )
        for c in recs:
            self.assertGreaterEqual(c["match_percentage"], 0.0)
            self.assertLessEqual(c["match_percentage"], 100.0)

    def test_result_fields_complete(self):
        recs = recommend_colleges(
            "Engineering", preferences={"state": "Karnataka", "ownership": "Both"}, top_n=1
        )
        self.assertEqual(len(recs), 1)
        c = recs[0]
        for field in (
            "college_name", "match_percentage", "course", "reason",
            "state", "district", "ownership", "naac", "nirf", "fee",
            "hostel", "website", "image_key", "verification_status",
        ):
            self.assertIn(field, c)
        self.assertIsInstance(c["reason"], list)
        self.assertGreater(len(c["reason"]), 0)

    def test_no_unknown_output(self):
        recs = recommend_colleges(
            "Engineering", preferences={"state": "Karnataka", "ownership": "Both"}, top_n=50
        )
        for c in recs:
            self.assertNotIn(c["naac"], ("Unknown", ""))
            self.assertNotIn(c["nirf"], ("Unknown", ""))
            self.assertNotIn(c["fee"], ("Unknown", ""))
            self.assertNotIn(c["hostel"], ("Unknown", ""))

    def test_recommend_colleges_from_prediction_wrapper(self):
        pred = {
            "Predicted_Domain": "Engineering",
            "Career_Readiness_Ranking": [
                {"domain": "Engineering", "probability": 50.0},
            ],
        }
        recs = recommend_colleges_from_prediction(
            pred,
            recommended_courses=[{"course": "B.Tech Computer Science Engineering"}],
            preferences={"state": "Karnataka", "ownership": "Both"},
        )
        self.assertTrue(recs)


class TestPredictEndpoint(unittest.TestCase):
    def test_science_endpoint_includes_colleges(self):
        status, body = _predict(_science_academic(), preferences={"state": "Karnataka", "ownership": "Both"})
        self.assertEqual(status, 200)
        for field in ("prediction", "top_domains", "recommended_courses", "prediction_explanation"):
            self.assertIn(field, body)
        self.assertIn("recommended_colleges", body)
        self.assertGreaterEqual(len(body["recommended_colleges"]), 1)
        c = body["recommended_colleges"][0]
        self.assertEqual(c["state"], "Karnataka")

    def test_commerce_endpoint_includes_colleges(self):
        status, body = _predict(_commerce_academic(), preferences={"state": "Delhi", "ownership": "Both"})
        self.assertEqual(status, 200)
        self.assertIn("recommended_colleges", body)
        self.assertGreaterEqual(len(body["recommended_colleges"]), 1)
        self.assertTrue(all(c["state"] == "Delhi" for c in body["recommended_colleges"]))

    def test_no_preferences_still_returns_colleges(self):
        status, body = _predict(_science_academic(), preferences=None)
        self.assertEqual(status, 200)
        self.assertIn("recommended_colleges", body)
        self.assertGreaterEqual(len(body["recommended_colleges"]), 1)

    def test_existing_fields_unchanged(self):
        _, body = _predict(_science_academic(), preferences={"state": "Karnataka"})
        self.assertEqual(set(body["prediction"].keys()), {"domain", "probability", "confidence"})
        self.assertIsInstance(body["top_domains"], list)
        self.assertIsInstance(body["recommended_courses"], list)
        self.assertIsInstance(body["prediction_explanation"], list)

    def test_invalid_json_400(self):
        client = app_module.app.test_client()
        resp = client.post("/predict", data="not-json", content_type="application/json")
        self.assertEqual(resp.status_code, 400)

    def test_missing_fields_400(self):
        client = app_module.app.test_client()
        resp = client.post(
            "/predict",
            data=json.dumps({"academic": {}, "answers": {}}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
