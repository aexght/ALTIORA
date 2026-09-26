"""
Regression tests for the stream-eligibility layer (course_eligibility.py).

Verifies:
  * Commerce never receives B.Tech / engineering courses or colleges
  * Arts never receives MBBS / medical courses
  * Science still receives engineering courses and colleges
  * BCA remains available to Commerce
  * filter_eligible_courses works on dict and string entries, preserves order
  * The /predict endpoint returns only eligible recommended courses and
    never recommends a college for an ineligible course
  * Existing prediction fields are unchanged (no prediction regression)

Run with:  python -m unittest tests.test_course_eligibility -v
"""

import json
import os
import sys
import unittest

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO)

import app as app_module  # noqa: E402
from course_eligibility import (  # noqa: E402
    ALL_STREAMS,
    course_allows_stream,
    filter_eligible_courses,
    required_streams_for_course,
)
from recommendation_engine import recommend_colleges  # noqa: E402


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


class TestRequiredStreams(unittest.TestCase):
    def test_csv_is_single_source_of_truth(self):
        # The eligibility CSV exists and is loaded (never an empty dataset).
        import course_eligibility as ce
        rows = ce.get_eligibility_data()["eligibility_rows"]
        self.assertGreater(len(rows), 20)

    def test_engineering_requires_science(self):
        self.assertEqual(
            required_streams_for_course("B.Tech Computer Science Engineering"),
            frozenset(("Science",)),
        )
        self.assertEqual(
            required_streams_for_course(
                "B.Tech Computer Science Engineering",
                eligibility_id="ELIG-BTECH-CS",
            ),
            frozenset(("Science",)),
        )

    def test_medical_requires_science(self):
        self.assertEqual(
            required_streams_for_course("MBBS"),
            frozenset(("Science",)),
        )

    def test_bca_open_to_all_streams(self):
        self.assertEqual(
            required_streams_for_course("BCA"),
            frozenset(("Science", "Commerce", "Arts")),
        )

    def test_commerce_finance_family_open(self):
        # B.Com / BBA resolve via the CSV / domain unanimity to any stream.
        self.assertEqual(
            required_streams_for_course("B.Com"),
            frozenset(("Science", "Commerce", "Arts")),
        )
        self.assertEqual(
            required_streams_for_course("BBA", domain="Business & Management"),
            frozenset(("Science", "Commerce", "Arts")),
        )

    def test_unknown_course_is_permissive(self):
        self.assertIn("Commerce", required_streams_for_course("Some Unknown Course"))

    def test_course_allows_stream_matrix(self):
        # Engineering: Science yes, Commerce/Arts no.
        self.assertTrue(course_allows_stream("Science", "B.Tech Computer Science Engineering"))
        self.assertFalse(course_allows_stream("Commerce", "B.Tech Computer Science Engineering"))
        self.assertFalse(course_allows_stream("Arts", "B.Tech Computer Science Engineering"))
        # Medical: Science yes, Commerce/Arts no.
        self.assertTrue(course_allows_stream("Science", "MBBS"))
        self.assertFalse(course_allows_stream("Commerce", "MBBS"))
        self.assertFalse(course_allows_stream("Arts", "MBBS"))
        # BCA: all streams.
        for stream in ALL_STREAMS:
            self.assertTrue(course_allows_stream(stream, "BCA"))


class TestFilterEligibleCourses(unittest.TestCase):
    def test_technology_plus_computing_for_commerce(self):
        candidates = [
            {"course": "BCA", "domain": "Technology & Computing", "score": 40.5},
            {"course": "B.Tech Computer Science Engineering", "domain": "Technology & Computing", "score": 38.88},
            {"course": "B.Tech Information Technology", "domain": "Technology & Computing", "score": 33.0},
            {"course": "B.Tech Cybersecurity", "domain": "Technology & Computing", "score": 32.0},
        ]
        eligible = filter_eligible_courses("Commerce", "Technology & Computing", candidates)
        names = [c["course"] for c in eligible]
        self.assertEqual(names, ["BCA"])
        self.assertNotIn("B.Tech Computer Science Engineering", names)
        self.assertNotIn("B.Tech Information Technology", names)
        self.assertNotIn("B.Tech Cybersecurity", names)

    def test_string_entries_supported(self):
        eligible = filter_eligible_courses(
            "Commerce", "Technology & Computing",
            ["BCA", "B.Tech Computer Science Engineering", "B.Tech Information Technology"],
        )
        self.assertEqual(eligible, ["BCA"])

    def test_order_and_identity_preserved(self):
        candidates = [
            {"course": "B.Com", "domain": "Commerce & Finance"},
            {"course": "BBA", "domain": "Business & Management"},
            {"course": "MBBS", "domain": "Medical & Health Sciences"},
        ]
        eligible = filter_eligible_courses("Commerce", "Commerce & Finance", candidates)
        self.assertEqual([c["course"] for c in eligible], ["B.Com", "BBA"])
        # Same dict objects come back (no clones).
        self.assertIs(eligible[0], candidates[0])

    def test_arts_never_gets_mbbs(self):
        candidates = [
            {"course": "MBBS", "domain": "Medical & Health Sciences"},
            {"course": "BBA", "domain": "Business & Management"},
            {"course": "BCA", "domain": "Technology & Computing"},
        ]
        eligible = filter_eligible_courses("Arts", "Medical & Health Sciences", candidates)
        self.assertEqual([c["course"] for c in eligible], ["BBA", "BCA"])
        self.assertNotIn("MBBS", [c["course"] for c in eligible])

    def test_science_still_gets_engineering(self):
        candidates = [
            {"course": "B.Tech Computer Science Engineering", "domain": "Technology & Computing"},
            {"course": "BCA", "domain": "Technology & Computing"},
            {"course": "MBBS", "domain": "Medical & Health Sciences"},
        ]
        eligible = filter_eligible_courses("Science", "Technology & Computing", candidates)
        self.assertEqual(
            [c["course"] for c in eligible],
            ["B.Tech Computer Science Engineering", "BCA", "MBBS"],
        )

    def test_missing_candidates_returns_empty(self):
        self.assertEqual(filter_eligible_courses("Commerce", "Technology & Computing", None), [])

    def test_custom_stream_filters_by_prefix(self):
        # Custom stream) unknown stream -> no filtering (cannot determine).
        candidates = [{"course": "MBBS", "domain": "Medical & Health Sciences"}]
        self.assertEqual(
            len(filter_eligible_courses("Unschooled", "Medical & Health Sciences", candidates)), 1
        )


class TestCollegeStreamEligibility(unittest.TestCase):
    def test_engineering_domain_commerce_gets_no_colleges(self):
        # No engineering college may be recommended to a Commerce student.
        recs = recommend_colleges(
            "Engineering",
            recommended_courses=[{"course": "B.Tech Mechanical Engineering"}],
            preferences={"state": "Karnataka", "ownership": "Both"},
            top_n=50,
            stream="Commerce",
        )
        self.assertEqual(recs, [])

    def test_engineering_domain_science_still_gets_colleges(self):
        recs = recommend_colleges(
            "Engineering",
            recommended_courses=[{"course": "B.Tech Mechanical Engineering"}],
            preferences={"state": "Karnataka", "ownership": "Both"},
            top_n=10,
            stream="Science",
        )
        self.assertTrue(recs)
        self.assertTrue(all(c["course"].lstrip().startswith("B.Tech") for c in recs))

    def test_technology_domain_commerce_only_bca_colleges(self):
        recs = recommend_colleges(
            "Technology & Computing",
            recommended_courses=[{"course": "BCA"}],
            preferences={"ownership": "Both"},
            top_n=50,
            stream="Commerce",
        )
        self.assertTrue(recs)
        # No recommended college may present an ineligible engineering course.
        for c in recs:
            self.assertNotIn("B.Tech", c["course"])
            self.assertNotIn("B.Tech", " ".join(c["reason"] or []))

    def test_no_stream_argument_keeps_backward_compat(self):
        # Without a stream the engine does not apply the eligibility filter.
        recs = recommend_colleges(
            "Engineering",
            recommended_courses=[{"course": "B.Tech Mechanical Engineering"}],
            preferences={"state": "Karnataka", "ownership": "Both"},
            top_n=5,
        )
        self.assertTrue(recs)


class TestPredictEndpointEligibility(unittest.TestCase):
    def test_commerce_profile_never_gets_btech(self):
        status, body = _predict(_commerce_academic())
        self.assertEqual(status, 200)
        courses = [c["course"] for c in body["recommended_courses"]]
        self.assertTrue(courses)
        self.assertTrue(all(not c.startswith("B.Tech") for c in courses))
        self.assertIn("BCA", courses)

    def test_science_profile_still_gets_engineering(self):
        status, body = _predict(_science_academic())
        self.assertEqual(status, 200)
        courses = [c["course"] for c in body["recommended_courses"]]
        self.assertIn("B.Tech Mechanical Engineering", courses)

    def test_prediction_fields_unchanged(self):
        _, body = _predict(_science_academic())
        self.assertEqual(set(body["prediction"].keys()), {"domain", "probability", "confidence"})
        self.assertIsInstance(body["top_domains"], list)
        self.assertIsInstance(body["recommended_courses"], list)
        self.assertIsInstance(body["prediction_explanation"], list)

    def test_college_courses_respect_stream(self):
        _, body = _predict(_commerce_academic(), preferences={"state": "Delhi", "ownership": "Both"})
        for c in body["recommended_colleges"]:
            self.assertNotIn("B.Tech", c["course"])
        for c in body["recommended_courses"]:
            self.assertNotIn("B.Tech", c["course"])


if __name__ == "__main__":
    unittest.main()