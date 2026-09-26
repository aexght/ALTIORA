"""
Regression tests for the backend translation layer (stream + electives -> ML
combination) of CareerPath AI.

Covers:
  * every supported Science and Commerce combination (new payloads)
  * backward-compatible legacy payloads (explicit subjectCombination)
  * Economics as an internal compatibility subject (optional marks, default 0)
  * validation errors (clean 400 responses)
  * prediction-pipeline equivalence between legacy and new payloads

Runs with the standard library:  python -m unittest tests/test_translation_layer.py
"""

import json
import os
import sys
import unittest

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO)

import app as app_module  # noqa: E402
from subject_combination_mapper import (  # noqa: E402
    resolve_combination,
    resolve_explicit_label,
    expected_marks_subjects,
    get_elective_options,
    get_core_subjects,
    get_ui_core_subjects,
    get_compatibility_subjects,
    supported_combinations,
)


def _valid_answers():
    """Return one valid answer per question (always picks the first option)."""
    questions = app_module._load_questions_json()
    return {str(q["id"]): q["options"][0]["id"] for q in questions[:40]}


class TestMapperTranslation(unittest.TestCase):
    """Direct unit tests for the centralized translation layer."""

    def test_all_11_trained_combinations_via_electives(self):
        cases = [
            # Science (5)
            ("Science", ["Mathematics"], "PCM"),
            ("Science", ["Biology"], "PCB"),
            ("Science", ["Mathematics", "Biology"], "PCMB"),
            ("Science", ["Mathematics", "Computer Science"], "PCMC"),
            ("Science", ["Mathematics", "Statistics"], "PCMS"),
            # Commerce (6) — Economics is an internal compatibility subject
            ("Commerce", ["Economics"], "Commerce"),
            ("Commerce", ["Computer Science"], "Commerce_CS"),
            ("Commerce", ["Statistics"], "Commerce_Statistics"),
            ("Commerce", ["Computer Science", "Statistics"], "Commerce_CS_Statistics"),
            ("Commerce", ["Mathematics"], "Commerce_Maths"),
            ("Commerce", ["Mathematics", "Computer Science"], "Commerce_Maths_CS"),
        ]
        for stream, electives, expected in cases:
            combo, errs = resolve_combination(stream, electives)
            self.assertEqual(combo, expected, "{} {} -> {}".format(stream, electives, errs))

    def test_commerce_ui_elective_mappings(self):
        """Exactly the mapping table from the task spec."""
        cases = [
            (["Economics"], "Commerce"),
            (["Statistics"], "Commerce_Statistics"),
            (["Computer Science"], "Commerce_CS"),
            (["Economics", "Statistics"], "Commerce_Statistics"),
            (["Economics", "Computer Science"], "Commerce_CS"),
            (["Statistics", "Computer Science"], "Commerce_CS_Statistics"),
        ]
        for electives, expected in cases:
            combo, errs = resolve_combination("Commerce", electives)
            self.assertEqual(combo, expected, str(errs))

    def test_supported_combinations_exactly_11(self):
        self.assertEqual(
            set(supported_combinations()),
            {"PCM", "PCB", "PCMB", "PCMC", "PCMS",
             "Commerce", "Commerce_CS", "Commerce_CS_Statistics",
             "Commerce_Maths", "Commerce_Maths_CS", "Commerce_Statistics"},
        )

    def test_expected_marks_subjects_dynamic(self):
        self.assertEqual(
            expected_marks_subjects("Commerce", ["Statistics"]),
            ["Accountancy", "Business Studies", "English", "Statistics"],
        )
        # Economics is compatibility -> not required, even when selected
        self.assertEqual(
            expected_marks_subjects("Commerce", ["Economics", "Statistics"]),
            ["Accountancy", "Business Studies", "English", "Statistics"],
        )
        self.assertEqual(
            expected_marks_subjects("Science", ["Biology"]),
            ["Physics", "Chemistry", "English", "Biology"],
        )

    def test_core_and_compatibility_lists(self):
        self.assertEqual(get_ui_core_subjects("Commerce"),
                         ["Accountancy", "Business Studies", "English"])
        self.assertEqual(get_compatibility_subjects("Commerce"), ["Economics"])
        self.assertEqual(get_compatibility_subjects("Science"), [])
        self.assertIn("Economics", get_elective_options("Commerce"))
        self.assertEqual(get_core_subjects("Commerce"),
                         ["Accountancy", "Economics", "Business Studies", "English"])

    def test_legacy_labels_still_resolve(self):
        for label, expected in [
            ("PCM", "PCM"),
            ("Commerce with Maths", "Commerce_Maths"),
            ("Commerce without Maths", "Commerce"),
            ("Commerce_CS", "Commerce_CS"),
            ("Commerce_CS_Statistics", "Commerce_CS_Statistics"),
        ]:
            combo, errs = resolve_explicit_label(label)
            self.assertEqual(combo, expected, str(errs))

    def test_legacy_labels_rejected(self):
        for label in ["Humanities", "Arts", "DoesNotExist", ""]:
            combo, _ = resolve_explicit_label(label)
            self.assertIsNone(combo, label)

    def test_model_limitation_not_invented(self):
        """Combinations the model cannot represent must NOT be fabricated."""
        bad = [
            ("Science", ["Computer Science"]),      # PCS not trained
            ("Science", ["Statistics"]),            # PC_S not trained
            ("Science", ["Biology", "Computer Science"]),  # PBC not trained
            ("Commerce", ["Mathematics", "Statistics"]),    # not trained
            ("Science", ["Mathematics", "Computer Science", "Statistics"]),  # 3
            ("Arts", ["History"]),                  # Arts stream unsupported
        ]
        for stream, electives in bad:
            combo, errs = resolve_combination(stream, electives)
            self.assertIsNone(combo, "{} {} should not resolve".format(stream, electives))
            self.assertTrue(errs)


class TestAcademicNormalization(unittest.TestCase):
    """Tests _normalize_academic via the Flask app module."""

    def normalize(self, payload):
        out = app_module._normalize_academic(payload)
        self.assertNotIn("error", out, out.get("error"))
        return out

    def test_new_commerce_statistics(self):
        out = self.normalize({
            "class10Percentage": 85,
            "stream": "Commerce",
            "electives": ["Statistics"],
            "subjectMarks": {
                "Accountancy_Marks": 80, "BusinessStudies_Marks": 82,
                "English_Marks": 90, "Statistics_Marks": 85,
            },
        })
        self.assertEqual(out["Subject_Combination"], "Commerce_Statistics")
        # Economics is a compatibility subject -> defaults to 0 internally
        self.assertEqual(out["Economics_Marks"], 0)

    def test_new_commerce_economics_only(self):
        out = self.normalize({
            "class10Percentage": 85,
            "stream": "Commerce",
            "electives": ["Economics"],
            "subjectMarks": {
                "Accountancy_Marks": 80, "BusinessStudies_Marks": 82,
                "English_Marks": 90,
            },
        })
        self.assertEqual(out["Subject_Combination"], "Commerce")
        self.assertEqual(out["Economics_Marks"], 0)

    def test_new_commerce_economics_statistics(self):
        out = self.normalize({
            "class10Percentage": 85,
            "stream": "Commerce",
            "electives": ["Economics", "Statistics"],
            "subjectMarks": {
                "Accountancy_Marks": 80, "BusinessStudies_Marks": 82,
                "English_Marks": 90, "Economics_Marks": 78, "Statistics_Marks": 85,
            },
        })
        self.assertEqual(out["Subject_Combination"], "Commerce_Statistics")
        # Provided Economics marks are preserved (not clobbered by the default)
        self.assertEqual(out["Economics_Marks"], 78)

    def test_new_science_pcmb(self):
        out = self.normalize({
            "class10Percentage": 85,
            "stream": "Science",
            "electives": ["Mathematics", "Biology"],
            "subjectMarks": {
                "Physics_Marks": 85, "Chemistry_Marks": 80, "English_Marks": 90,
                "Maths_Marks": 88, "Biology_Marks": 84,
            },
        })
        self.assertEqual(out["Subject_Combination"], "PCMB")
        self.assertEqual(out["Mathematics_Marks"], 88)

    def test_legacy_flat_payload(self):
        out = self.normalize({
            "Class10_Percentage": 85, "Class12_Percentage": 88,
            "Class12_Stream": "Commerce",
            "Subject_Combination": "Commerce_CS",
            "Accountancy_Marks": 80, "Economics_Marks": 78,
            "BusinessStudies_Marks": 82, "English_Marks": 90,
            "ComputerScience_Marks": 85,
        })
        self.assertEqual(out["Subject_Combination"], "Commerce_CS")
        self.assertEqual(out["Economics_Marks"], 78)

    def test_legacy_requires_economics_for_commerce(self):
        out = app_module._normalize_academic({
            "Class10_Percentage": 85, "Class12_Stream": "Commerce",
            "Subject_Combination": "Commerce",
            "Accountancy_Marks": 80, "BusinessStudies_Marks": 82,
            "English_Marks": 90,  # no Economics_Marks
        })
        self.assertIn("error", out)  # legacy path keeps model-core requirement

    def test_legacy_and_new_produce_identical_normalization(self):
        legacy = self.normalize({
            "class10Percentage": 85, "class12Percentage": 88,
            "stream": "Commerce", "subjectCombination": "Commerce_CS",
            "subjectMarks": {
                "Accountancy_Marks": 80, "BusinessStudies_Marks": 82,
                "Economics_Marks": 78, "English_Marks": 90,
                "ComputerScience_Marks": 85,
            },
        })
        new = self.normalize({
            "class10Percentage": 85, "class12Percentage": 88,
            "stream": "Commerce", "electives": ["Economics", "Computer Science"],
            "subjectMarks": {
                "Accountancy_Marks": 80, "BusinessStudies_Marks": 82,
                "Economics_Marks": 78, "English_Marks": 90,
                "ComputerScience_Marks": 85,
            },
        })
        self.assertEqual(legacy, new)


class TestValidationErrors(unittest.TestCase):
    """Validation rules -> clean 400 {error} responses."""

    def normalize_error(self, payload):
        out = app_module._normalize_academic(payload)
        self.assertIn("error", out)
        return out["error"]

    def test_missing_stream(self):
        self.normalize_error({
            "class10Percentage": 85, "electives": ["Statistics"],
            "subjectMarks": {},
        })

    def test_missing_combination_info(self):
        self.normalize_error({
            "class10Percentage": 85, "stream": "Commerce",
            "subjectMarks": {},
        })

    def test_zero_electives(self):
        self.normalize_error({
            "class10Percentage": 85, "stream": "Commerce", "electives": [],
            "subjectMarks": {"Accountancy_Marks": 1, "BusinessStudies_Marks": 1,
                             "English_Marks": 1},
        })

    def test_three_electives(self):
        self.normalize_error({
            "class10Percentage": 85, "stream": "Science",
            "electives": ["Mathematics", "Biology", "Statistics"],
            "subjectMarks": {},
        })

    def test_duplicate_elective(self):
        self.normalize_error({
            "class10Percentage": 85, "stream": "Commerce",
            "electives": ["Statistics", "Statistics"],
            "subjectMarks": {},
        })

    def test_duplicate_core_elective(self):
        err = self.normalize_error({
            "class10Percentage": 85, "stream": "Commerce",
            "electives": ["Economics", "Economics"],
            "subjectMarks": {},
        })
        self.assertIn("Duplicate", err)

    def test_unknown_elective(self):
        err = self.normalize_error({
            "class10Percentage": 85, "stream": "Commerce",
            "electives": ["Astrology"], "subjectMarks": {},
        })
        self.assertIn("Unknown", err)

    def test_unsupported_subject(self):
        err = self.normalize_error({
            "class10Percentage": 85, "stream": "Commerce",
            "electives": ["Informatics Practices"], "subjectMarks": {},
        })
        self.assertIn("not supported", err)

    def test_arts_stream(self):
        err = self.normalize_error({
            "class10Percentage": 85, "stream": "Arts",
            "electives": ["History"], "subjectMarks": {},
        })
        self.assertIn("Unsupported stream", err)

    def test_model_limitation(self):
        err = self.normalize_error({
            "class10Percentage": 85, "stream": "Science",
            "electives": ["Computer Science"],
            "subjectMarks": {"Physics_Marks": 1, "Chemistry_Marks": 1,
                             "English_Marks": 1, "ComputerScience_Marks": 1},
        })
        self.assertIn("Unsupported subject combination", err)

    def test_missing_required_core_mark(self):
        err = self.normalize_error({
            "class10Percentage": 85, "stream": "Commerce",
            "electives": ["Statistics"],
            "subjectMarks": {"Accountancy_Marks": 80, "English_Marks": 90},
        })
        self.assertIn("Business Studies", err)

    def test_missing_required_elective_mark(self):
        err = self.normalize_error({
            "class10Percentage": 85, "stream": "Commerce",
            "electives": ["Statistics"],
            "subjectMarks": {"Accountancy_Marks": 80, "BusinessStudies_Marks": 82,
                             "English_Marks": 90},
        })
        self.assertIn("Statistics", err)

    def test_marks_out_of_range(self):
        err = self.normalize_error({
            "class10Percentage": 85, "stream": "Commerce",
            "electives": ["Statistics"],
            "subjectMarks": {"Accountancy_Marks": 150, "BusinessStudies_Marks": 82,
                             "English_Marks": 90, "Statistics_Marks": 85},
        })
        self.assertIn("0 and 100", err)


class TestPredictEndpoint(unittest.TestCase):
    """Full /predict API regression via the Flask test client."""

    @classmethod
    def setUpClass(cls):
        cls.client = app_module.app.test_client()
        cls.answers = _valid_answers()
        cls.academic = {
            "class10Percentage": 85,
            "class12Percentage": 88,
            "stream": "Commerce",
            "electives": ["Statistics", "Computer Science"],
            "subjectMarks": {
                "Accountancy_Marks": 80, "BusinessStudies_Marks": 82,
                "English_Marks": 90, "Statistics_Marks": 85,
                "ComputerScience_Marks": 84,
            },
        }

    def test_predict_new_payload(self):
        resp = self.client.post("/predict", json={
            "academic": self.academic, "answers": self.answers,
        })
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        body = resp.get_json()
        for key in ["prediction", "top_domains", "recommended_courses",
                    "prediction_explanation"]:
            self.assertIn(key, body)
        self.assertIn("domain", body["prediction"])
        self.assertIn("confidence", body["prediction"])

    def test_predict_commerce_economics_only_no_economics_marks(self):
        """Economics is optional for the new UI — must NOT 400 without it."""
        academic = {
            "class10Percentage": 85, "stream": "Commerce",
            "electives": ["Economics"],
            "subjectMarks": {
                "Accountancy_Marks": 80, "BusinessStudies_Marks": 82,
                "English_Marks": 90,
            },
        }
        resp = self.client.post("/predict", json={
            "academic": academic, "answers": self.answers,
        })
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))

    def test_predict_legacy_flat_payload(self):
        academic = {
            "Class10_Percentage": 85, "Class12_Percentage": 88,
            "Class12_Stream": "Commerce", "Subject_Combination": "Commerce_Statistics",
            "Accountancy_Marks": 80, "Economics_Marks": 78,
            "BusinessStudies_Marks": 82, "English_Marks": 90,
            "Statistics_Marks": 85,
        }
        resp = self.client.post("/predict", json={
            "academic": academic, "answers": self.answers,
        })
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))

    def test_predict_legacy_camelcase(self):
        academic = {
            "class10Percentage": 85, "class12Percentage": 88,
            "stream": "Science", "subjectCombination": "PCMB",
            "subjectMarks": {
                "Physics_Marks": 85, "Chemistry_Marks": 80, "English_Marks": 90,
                "Maths_Marks": 88, "Biology_Marks": 84,
            },
        }
        resp = self.client.post("/predict", json={
            "academic": academic, "answers": self.answers,
        })
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))

    def test_legacy_and_new_predictions_identical(self):
        """Equivalent legacy/new payloads must yield byte-identical responses."""
        legacy = {
            "class10Percentage": 85, "class12Percentage": 88,
            "stream": "Commerce", "subjectCombination": "Commerce_CS",
            "subjectMarks": {
                "Accountancy_Marks": 80, "BusinessStudies_Marks": 82,
                "Economics_Marks": 78, "English_Marks": 90,
                "ComputerScience_Marks": 85,
            },
        }
        new = {
            "class10Percentage": 85, "class12Percentage": 88,
            "stream": "Commerce", "electives": ["Economics", "Computer Science"],
            "subjectMarks": {
                "Accountancy_Marks": 80, "BusinessStudies_Marks": 82,
                "Economics_Marks": 78, "English_Marks": 90,
                "ComputerScience_Marks": 85,
            },
        }
        r1 = self.client.post("/predict", json={"academic": legacy, "answers": self.answers})
        r2 = self.client.post("/predict", json={"academic": new, "answers": self.answers})
        self.assertEqual(r1.status_code, 200, r1.get_data(as_text=True))
        self.assertEqual(r1.get_data(), r2.get_data())

    def test_predict_error_400s(self):
        bad_academics = [
            {"stream": "Commerce"},                          # no combination info
            {"stream": "Commerce", "electives": []},         # 0 electives
            {"stream": "Science",
             "electives": ["Mathematics", "Biology", "Statistics"]},  # 3
            {"stream": "Commerce", "electives": ["Statistics", "Statistics"]},  # dup
            {"stream": "Commerce", "electives": ["Astrology"]},   # unknown
            {"stream": "Arts", "electives": ["History"]},    # unsupported stream
        ]
        for academic in bad_academics:
            resp = self.client.post("/predict", json={
                "academic": academic, "answers": self.answers,
            })
            self.assertEqual(resp.status_code, 400, academic)
            self.assertIn("error", resp.get_json())

    def test_predict_missing_fields_400(self):
        resp = self.client.post("/predict", json={"academic": self.academic})
        self.assertEqual(resp.status_code, 400)
        resp = self.client.post("/predict", data="not json", content_type="application/json")
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
