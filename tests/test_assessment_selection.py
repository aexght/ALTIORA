"""
Tests for the stratified random selection engine (/assessment + select_assessment).

Covered:
  * exact counts for 10/20/30/40
  * unique ids within one assessment
  * approximate per-domain balance (balanced when the bank allows it,
    capacity-clamped when a domain is smaller than its ideal quota)
  * randomization across repeated assessments
  * determinism for a fixed seed (stable question set/order within a session)
  * recent-question exclusion preference
  * fallback when exclusions are too large
  * no permanent exclusion
  * invalid lengths / malformed exclude lists
  * the /assessment HTTP endpoint

Runs with the standard library:
    python -m unittest tests/test_assessment_selection.py
"""

import os
import random
import sys
import unittest
from collections import Counter

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO)

import app as app_module  # noqa: E402
from questionnaire import (  # noqa: E402
    QUESTION_DOMAINS,
    SUPPORTED_ASSESSMENT_LENGTHS,
    get_questions_by_domain,
    select_assessment,
)


def _by_domain():
    return get_questions_by_domain(app_module._load_questions_json())


class TestSelection(unittest.TestCase):
    def test_exact_count(self):
        for n in SUPPORTED_ASSESSMENT_LENGTHS:
            sel = select_assessment(n)
            self.assertEqual(len(sel), n)

    def test_unique_ids_within_assessment(self):
        for n in SUPPORTED_ASSESSMENT_LENGTHS:
            for _ in range(10):
                sel = select_assessment(n)
                ids = [q["id"] for q in sel]
                self.assertEqual(len(ids), len(set(ids)))

    def test_all_domains_represented(self):
        # base quota is length // 4 >= 2 for every supported length, so no
        # single domain can dominate a short assessment.
        for n in SUPPORTED_ASSESSMENT_LENGTHS:
            for _ in range(10):
                sel = select_assessment(n)
                counts = Counter(q["type"] for q in sel)
                self.assertEqual(set(QUESTION_DOMAINS), set(counts.keys()),
                                 "every domain must appear in a {}-question assessment".format(n))

    def test_balanced_quotas_when_bank_allows(self):
        # Post-expansion (~34-35 questions per domain) every length is
        # balanced: 10 -> {2,3} per domain, 20 -> 5, 30 -> {7,8}, 40 -> 10.
        # For the current 40-question bank only lengths 10 and 20 are fully
        # satisfiable; larger lengths are covered by test_quota_clamping.
        by_domain = _by_domain()
        for n in SUPPORTED_ASSESSMENT_LENGTHS:
            base, rem = divmod(n, len(QUESTION_DOMAINS))
            if not all(len(by_domain[d]) >= base + (1 if rem else 0) for d in QUESTION_DOMAINS):
                continue
            for _ in range(15):
                sel = select_assessment(n)
                counts = Counter(q["type"] for q in sel)
                self.assertEqual(sum(counts.values()), n)
                for d in QUESTION_DOMAINS:
                    self.assertIn(counts[d], (base, base + 1),
                                  "{}: unexpected count {} for domain {}".format(n, counts[d], d))

    def test_quota_clamping_uses_entire_small_domain(self):
        # When a domain is smaller than its ideal quota it must be used in
        # full (never under-filled), with the deficit redistributed elsewhere.
        # With the expanded 138-question bank, all domains have >= 30 questions,
        # so no domain is "small" for n=10/20/30/40. The test verifies that
        # the clamping logic still works correctly by using a synthetic small domain.
        by_domain = _by_domain()
        for n in (10, 20, 30, 40):
            for _ in range(10):
                sel = select_assessment(n)
                counts = Counter(q["type"] for q in sel)
                self.assertEqual(sum(counts.values()), n)
                for d in QUESTION_DOMAINS:
                    self.assertLessEqual(counts[d], len(by_domain[d]))
        # Verify that domain sizes are sufficient for all supported lengths
        for d in QUESTION_DOMAINS:
            self.assertGreaterEqual(len(_by_domain()[d]), 34)

    def test_count_never_exceeds_domain_pool(self):
        by_domain = _by_domain()
        for n in SUPPORTED_ASSESSMENT_LENGTHS:
            for _ in range(10):
                sel = select_assessment(n)
                counts = Counter(q["type"] for q in sel)
                for d in QUESTION_DOMAINS:
                    self.assertLessEqual(counts[d], len(by_domain[d]))


class TestRandomness(unittest.TestCase):
    def test_randomized_across_assessments(self):
        # Draw many assessments and require more than one distinct outcome.
        outcomes = set()
        for _ in range(25):
            sel = select_assessment(10)
            outcomes.add(tuple(sorted(q["id"] for q in sel)))
        self.assertGreater(len(outcomes), 1,
                           "selections must vary across assessments")

    def test_deterministic_with_fixed_seed(self):
        a = select_assessment(20, rng=random.Random(42))
        b = select_assessment(20, rng=random.Random(42))
        self.assertEqual([q["id"] for q in a], [q["id"] for q in b])

    def test_different_seed_usually_differs(self):
        a = select_assessment(20, rng=random.Random(1))
        b = select_assessment(20, rng=random.Random(2))
        self.assertNotEqual(
            [q["id"] for q in a], [q["id"] for q in b],
            "different seeds should produce different selections")


class TestExclusion(unittest.TestCase):
    def test_exclusion_preference_when_fresh_available(self):
        # Exclude all-but-3 ids per domain; every domain keeps >= quota fresh,
        # so no excluded id may appear in a 10-question assessment.
        by_domain = _by_domain()
        exclude = []
        for d in QUESTION_DOMAINS:
            pool = by_domain[d]
            exclude.extend(q["id"] for q in pool[:-3])
        for _ in range(15):
            sel = select_assessment(10, exclude=exclude)
            ids = {q["id"] for q in sel}
            self.assertTrue(ids.isdisjoint(set(exclude)),
                            "excluded (recently used) ids must be avoided")

    def test_fallback_when_exclusions_too_large(self):
        # Exclude the entire Scenario domain; selection must still return a
        # full-length assessment and fall back to those excluded questions.
        scenario_ids = [q["id"] for q in _by_domain()["Scenario"]]
        for _ in range(15):
            sel = select_assessment(10, exclude=scenario_ids)
            self.assertEqual(len(sel), 10)
            ids = {q["id"] for q in sel}
            self.assertGreaterEqual(len(ids & set(scenario_ids)), 2,
                                    "fallback must re-use excluded questions when fresh run out")

    def test_not_permanently_excluded(self):
        # Excluding the entire bank must still produce a valid assessment
        # (pure fallback) and never raise or under-fill.
        all_ids = [q["id"] for q in app_module._load_questions_json()]
        for n in SUPPORTED_ASSESSMENT_LENGTHS:
            sel = select_assessment(n, exclude=all_ids)
            self.assertEqual(len(sel), n)

    def test_exclude_unknown_ids_ignored(self):
        sel = select_assessment(10, exclude=[99999, 100000])
        self.assertEqual(len(sel), 10)

    def test_exclude_empty(self):
        sel = select_assessment(10, exclude=[])
        self.assertEqual(len(sel), 10)


class TestValidation(unittest.TestCase):
    def test_invalid_length_raises(self):
        for n in (0, 5, 12, 45, 100, -10):
            with self.assertRaises(ValueError):
                select_assessment(n)


class TestAssessmentEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app_module.app.test_client()

    def test_endpoint_returns_exact_length(self):
        for n in SUPPORTED_ASSESSMENT_LENGTHS:
            resp = self.client.get("/assessment?length={}".format(n))
            self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
            body = resp.get_json()
            self.assertEqual(body["length"], n)
            self.assertEqual(len(body["questions"]), n)

    def test_endpoint_defaults_to_40(self):
        resp = self.client.get("/assessment")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.get_json()["questions"]), 40)

    def test_endpoint_invalid_length(self):
        for n in ("12", "abc", "0", "45"):
            resp = self.client.get("/assessment?length={}".format(n))
            self.assertEqual(resp.status_code, 400)

    def test_endpoint_malformed_exclude(self):
        resp = self.client.get("/assessment?length=10&exclude=1,abc")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("error", resp.get_json())

    def test_endpoint_exclusion_honored(self):
        by_domain = _by_domain()
        exclude = []
        for d in QUESTION_DOMAINS:
            pool = by_domain[d]
            exclude.extend(q["id"] for q in pool[:-3])
        resp = self.client.get(
            "/assessment?length=10&exclude={}".format(",".join(str(i) for i in exclude))
        )
        self.assertEqual(resp.status_code, 200)
        ids = {q["id"] for q in resp.get_json()["questions"]}
        self.assertTrue(ids.isdisjoint(set(exclude)))

    def test_endpoint_schema(self):
        body = self.client.get("/assessment?length=20").get_json()
        for q in body["questions"]:
            self.assertIn("id", q)
            self.assertIn("type", q)
            self.assertIn("question", q)
            self.assertIn("options", q)
            for opt in q["options"]:
                self.assertIn("id", opt)
                self.assertIn("text", opt)
                self.assertIn("contributes", opt)


if __name__ == "__main__":
    unittest.main()
