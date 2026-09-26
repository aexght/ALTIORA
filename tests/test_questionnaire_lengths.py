"""
Regression tests for the Assessment Length feature (10/20/30/40 questions).

Contract (post selection-engine):
  * an assessment is a randomized, stratified selection of N questions
    (N in {10, 20, 30, 40}) drawn from the master bank, submitted as ANY set
    of N distinct valid question ids (no longer a sequential prefix)
  * validation: exactly N answers, N in {10,20,30,40}, all ids valid and
    unique; malformed / unknown / duplicate / missing ids rejected
  * scoring normalizes trait scores against the theoretical maximum of the
    SUBMITTED questions, so partial assessments stay on a 0-100 scale instead
    of being deflated by unseen questions
  * a full 40-question submission keeps the legacy normalization behaviour

Runs with the standard library:
    python -m unittest tests/test_questionnaire_lengths.py
"""

import os
import sys
import unittest

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO)

import app as app_module  # noqa: E402
from questionnaire import (  # noqa: E402
    SUPPORTED_ASSESSMENT_LENGTHS,
    _TRAITS,
    compute_scores,
    validate_answers,
)


def _load_questions():
    return app_module._load_questions_json()


def _answers_for_n(n, pick="first"):
    """Answers for n distinct valid questions (deterministic subset).

    pick: "first" -> first option, "last" -> last option, or a trait name ->
    the option with the highest contribution to that trait.
    """
    questions = _load_questions()
    step = len(questions) / float(n)
    chosen = [questions[int(i * step)] for i in range(n)]
    answers = {}
    for q in chosen:
        if pick == "first":
            opt_id = q["options"][0]["id"]
        elif pick == "last":
            opt_id = q["options"][-1]["id"]
        else:
            opt_id = max(
                q["options"], key=lambda o: o["contributes"].get(pick, 0)
            )["id"]
        answers[str(q["id"])] = opt_id
    return answers


def _questions_map():
    return {q["id"]: q for q in _load_questions()}


def _trait_raw(answers, trait):
    q_map = _questions_map()
    total = 0
    for q_id_str, opt_id in answers.items():
        option = next(
            o for o in q_map[int(q_id_str)]["options"] if o["id"] == opt_id
        )
        total += option["contributes"].get(trait, 0)
    return total


def _subset_denominator(question_ids, trait):
    q_map = _questions_map()
    return sum(
        max(o["contributes"].get(trait, 0) for o in q_map[qid]["options"])
        for qid in question_ids
    )


_ACADEMIC_COMMERCE = {
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


class TestValidation(unittest.TestCase):
    def test_any_valid_set_of_n_accepted(self):
        for n in SUPPORTED_ASSESSMENT_LENGTHS:
            answers = _answers_for_n(n)
            self.assertEqual(validate_answers(answers), [],
                             "unexpected errors for {} questions".format(n))
            scores = compute_scores(answers)
            self.assertNotIn("errors", scores)
            self.assertEqual(sorted(scores.keys()), sorted(_TRAITS))

    def test_answers_must_be_dict(self):
        self.assertEqual(len(validate_answers([("1", "A")])), 1)
        self.assertEqual(len(validate_answers("not a dict")), 1)

    def test_unknown_question_id_rejected(self):
        answers = _answers_for_n(10)
        answers["999"] = "A"
        self.assertTrue(validate_answers(answers))

    def test_malformed_question_id_rejected(self):
        answers = _answers_for_n(10)
        answers["abc"] = "A"
        self.assertTrue(validate_answers(answers))

    def test_duplicate_question_id_rejected(self):
        # "1" and "01" both parse to question id 1 -> duplicate response.
        answers = _answers_for_n(10)
        answers["01"] = answers["1"]
        self.assertTrue(validate_answers(answers))

    def test_invalid_option_rejected(self):
        answers = _answers_for_n(10)
        answers["1"] = "NOT_A_VALID_OPTION"
        self.assertTrue(validate_answers(answers))

    def test_unsupported_length_rejected(self):
        # Only counts that can be built from the current 40-question bank.
        # More than 40 answers necessarily reference unknown ids (covered by
        # test_unknown_question_id_rejected).
        for n in (1, 5, 12, 39):
            self.assertTrue(validate_answers(_answers_for_n(n)),
                            "{} answers should be rejected".format(n))

    def test_empty_answers_rejected(self):
        errs = validate_answers({})
        self.assertEqual(len(errs), 1)
        self.assertIn("No answers", errs[0])

    def test_missing_answer_rejected(self):
        # 39 valid answers is not a supported assessment length.
        answers = _answers_for_n(39)
        errs = validate_answers(answers)
        self.assertTrue(errs)
        self.assertIn("10, 20, 30, or 40", errs[0])


class TestScoring(unittest.TestCase):
    def test_full_40_matches_legacy_normalization(self):
        # A 40-question submission submits the whole (current) bank; the
        # submitted-set denominator equals the legacy all-40 denominator.
        answers = _answers_for_n(40, pick="first")
        scores = compute_scores(answers)
        submitted_ids = [int(k) for k in answers]
        for trait in _TRAITS:
            max_t = _subset_denominator(submitted_ids, trait)
            expected = 0 if max_t == 0 else round((_trait_raw(answers, trait) / max_t) * 100)
            self.assertEqual(scores[trait], expected,
                             "trait {} changed for a full 40-question submission".format(trait))

    def test_partial_max_answers_score_100_not_deflated(self):
        # Every trait has a smaller denominator in any 10/20/30-question subset
        # than across all 40, so the legacy all-40 normalization deflated
        # partial assessments. Answering the max-contributing option for every
        # active question in a trait must now score exactly 100.
        for n in (10, 20, 30):
            for trait in _TRAITS:
                answers = _answers_for_n(n, pick=trait)
                scores = compute_scores(answers)
                self.assertEqual(scores[trait], 100,
                                 "{} questions, trait {}: deflated ({} < 100)".format(
                                     n, trait, scores[trait]))

    def test_partial_denominators_are_subset_derived(self):
        n = 10
        trait = "Logical_Score"
        answers = _answers_for_n(n, pick=trait)
        scores = compute_scores(answers)
        subset_max = _subset_denominator([int(k) for k in answers], trait)
        full_max = _subset_denominator([q["id"] for q in _load_questions()], trait)
        self.assertGreater(subset_max, 0)
        self.assertLess(subset_max, full_max)
        expected = round((_trait_raw(answers, trait) / subset_max) * 100)
        self.assertEqual(scores[trait], expected)
        legacy = round((_trait_raw(answers, trait) / full_max) * 100)
        self.assertLess(legacy, scores[trait])


class TestPredictEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app_module.app.test_client()

    def test_predict_200_for_each_assessment_length(self):
        for n in SUPPORTED_ASSESSMENT_LENGTHS:
            resp = self.client.post("/predict", json={
                "academic": _ACADEMIC_COMMERCE,
                "answers": _answers_for_n(n),
            })
            self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))

    def test_predict_schema_unaffected_by_length(self):
        base = self.client.post("/predict", json={
            "academic": _ACADEMIC_COMMERCE,
            "answers": _answers_for_n(40),
        }).get_json()
        short = self.client.post("/predict", json={
            "academic": _ACADEMIC_COMMERCE,
            "answers": _answers_for_n(10),
        }).get_json()
        for key in ["prediction", "top_domains", "recommended_courses",
                    "prediction_explanation", "recommended_colleges"]:
            self.assertIn(key, base)
            self.assertIn(key, short)
        for body in (base, short):
            self.assertIn("domain", body["prediction"])
            self.assertIn("confidence", body["prediction"])

    def test_predict_rejects_invalid_partial_payload(self):
        answers = _answers_for_n(20)
        del answers[str(int(list(answers)[0]))]
        resp = self.client.post("/predict", json={
            "academic": _ACADEMIC_COMMERCE, "answers": answers,
        })
        self.assertEqual(resp.status_code, 400)
        self.assertIn("error", resp.get_json())

    def test_full_40_prediction_is_deterministic_baseline(self):
        a = self.client.post("/predict", json={
            "academic": _ACADEMIC_COMMERCE,
            "answers": _answers_for_n(40),
        }).get_json()
        b = self.client.post("/predict", json={
            "academic": _ACADEMIC_COMMERCE,
            "answers": _answers_for_n(40),
        }).get_json()
        self.assertEqual(a["prediction"], b["prediction"])


if __name__ == "__main__":
    unittest.main()
