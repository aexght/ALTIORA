"""
Automated quality gates for the ALTIORA question bank (questions.json).

These gates are intentionally strict so that authoring the expanded bank
(~120-150 questions) can never silently introduce:
  * schema violations
  * duplicate or near-duplicate questions
  * invalid domains / option ids / trait names / contribution values
  * trait-coverage or domain-balance regressions

For the current (pre-expansion) 40-question bank the count gate permits
exactly 40; once expansion begins the bank must be in [120, 150] and the
domain/trait balance gates tighten automatically. Running a half-expanded
bank (e.g. 90 questions) must fail.

Runs with the standard library:
    python -m unittest tests/test_question_bank.py
"""

import os
import re
import sys
import unittest
from collections import Counter

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO)

from questionnaire import QUESTION_DOMAINS, _TRAITS  # noqa: E402

EXPANDED_MIN = 120
EXPANDED_MAX = 150

STOPWORDS = {
    "about", "after", "again", "against", "also", "because", "been",
    "before", "being", "between", "could", "does", "doing", "down", "each",
    "first", "from", "have", "having", "into", "just", "like", "more",
    "most", "much", "must", "only", "other", "over", "same", "some", "such",
    "than", "that", "their", "them", "then", "there", "these", "they",
    "this", "those", "through", "under", "very", "what", "when", "where",
    "which", "while", "with", "would", "your", "our", "their", "has", "had",
    "will", "should", "shall", "can", "may", "might", "during", "below",
    "both", "but", "not", "nor", "for", "off", "out", "so", "up", "by",
    "at", "of", "in", "it", "is", "are", "was", "were", "the", "and", "a",
    "an", "as", "do",
}

NEAR_DUPLICATE_JACCARD_THRESHOLD = 0.75


def _load_bank():
    with open(os.path.join(_REPO, "questions.json"), encoding="utf-8") as f:
        import json
        return json.load(f)


def _significant_tokens(text):
    return {
        w for w in re.findall(r"[a-zA-Z]{4,}", text.lower())
        if w not in STOPWORDS
    }


def _jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


class TestBankSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = _load_bank()

    def test_schema_conformity(self):
        for q in self.bank:
            self.assertIsInstance(q.get("id"), int, q.get("question"))
            self.assertIsInstance(q.get("type"), str, q.get("question"))
            self.assertIsInstance(q.get("question"), str, q.get("question"))
            self.assertGreaterEqual(len(q["question"].strip()), 10)
            options = q.get("options")
            self.assertIsInstance(options, list, q["question"])
            self.assertGreaterEqual(len(options), 2)
            for opt in options:
                self.assertIsInstance(opt.get("id"), str, q["question"])
                self.assertIsInstance(opt.get("text"), str, q["question"])
                self.assertGreaterEqual(len(opt["text"].strip()), 2)
                self.assertIsInstance(opt.get("contributes"), dict, q["question"])

    def test_unique_ids(self):
        ids = [q["id"] for q in self.bank]
        self.assertEqual(len(ids), len(set(ids)), "duplicate question ids")

    def test_valid_domains(self):
        for q in self.bank:
            self.assertIn(q["type"], QUESTION_DOMAINS,
                          "invalid domain '{}' (id {})".format(q["type"], q["id"]))

    def test_unique_question_text(self):
        texts = [q["question"].strip().lower() for q in self.bank]
        self.assertEqual(len(texts), len(set(texts)), "duplicate question text")

    def test_near_duplicate_detection(self):
        tokens = [_significant_tokens(q["question"]) for q in self.bank]
        for i in range(len(self.bank)):
            for j in range(i + 1, len(self.bank)):
                sim = _jaccard(tokens[i], tokens[j])
                self.assertLess(
                    sim, NEAR_DUPLICATE_JACCARD_THRESHOLD,
                    "near-duplicate questions (ids {} and {}): Jaccard {:.2f}".format(
                        self.bank[i]["id"], self.bank[j]["id"], sim)
                )

    def test_option_id_format(self):
        for q in self.bank:
            ids = [o["id"] for o in q["options"]]
            self.assertEqual(len(ids), len(set(ids)),
                             "duplicate option ids in question {}".format(q["id"]))
            for oid in ids:
                self.assertRegex(oid, r"^[A-Z]$",
                                 "option id '{}' must be a single uppercase letter".format(oid))

    def test_option_count_between_4_and_5(self):
        for q in self.bank:
            self.assertIn(len(q["options"]), (4, 5),
                          "question {} must have 4 or 5 options".format(q["id"]))

    def test_valid_trait_names(self):
        for q in self.bank:
            for o in q["options"]:
                for trait in o["contributes"]:
                    self.assertIn(trait, _TRAITS,
                                  "question {} uses unknown trait '{}'".format(q["id"], trait))

    def test_valid_contribution_values(self):
        for q in self.bank:
            for o in q["options"]:
                for trait, value in o["contributes"].items():
                    self.assertIsInstance(value, int, q["id"])
                    self.assertGreaterEqual(value, 1, q["id"])
                    self.assertLessEqual(value, 5, q["id"])

    def test_all_domains_present(self):
        types = {q["type"] for q in self.bank}
        for d in QUESTION_DOMAINS:
            self.assertIn(d, types, "domain '{}' has no questions".format(d))


class TestBankBalance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = _load_bank()
        cls.total = len(cls.bank)

    def test_bank_size_within_target_range(self):
        # Exactly 40 is the current pre-expansion bank; anything else must be
        # a fully expanded 120-150 bank (a half-expanded bank fails).
        if self.total != 40:
            self.assertGreaterEqual(self.total, EXPANDED_MIN,
                                    "bank expansion must reach at least {} questions".format(EXPANDED_MIN))
            self.assertLessEqual(self.total, EXPANDED_MAX)

    def test_domain_balance(self):
        counts = Counter(q["type"] for q in self.bank)
        if self.total == 40:
            for d in QUESTION_DOMAINS:
                self.assertGreaterEqual(counts.get(d, 0), 1)
        else:
            for d in QUESTION_DOMAINS:
                self.assertGreaterEqual(counts[d], 30,
                                        "domain '{}' under-represented ({})".format(d, counts[d]))
                self.assertLessEqual(counts[d], 38,
                                     "domain '{}' over-represented ({})".format(d, counts[d]))
            self.assertLessEqual(max(counts.values()) - min(counts.values()), 4,
                                 "domains must be approximately balanced")

    def test_bankwide_trait_coverage(self):
        # Each trait must appear in at least ~1/3 of the questions so that no
        # trait is starved across the whole bank.
        min_questions = max(1, self.total // 3)
        for trait in _TRAITS:
            covered = sum(
                1 for q in self.bank
                if any(trait in o["contributes"] for o in q["options"])
            )
            self.assertGreaterEqual(
                covered, min_questions,
                "trait '{}' appears in only {} of {} questions".format(
                    trait, covered, self.total)
            )

    def test_domain_trait_coverage(self):
        # Prevent the "beautiful domain pie, starved ML features" failure mode:
        # every domain must measure a broad set of traits. The current bank's
        # Aptitude domain omits Technical_Interest, so the pre-expansion floor
        # is 6 distinct traits; an expanded bank must cover all 8 everywhere.
        floor = 8 if self.total >= EXPANDED_MIN else 6
        for d in QUESTION_DOMAINS:
            covered = {
                trait
                for q in self.bank if q["type"] == d
                for o in q["options"]
                for trait in o["contributes"]
            }
            self.assertGreaterEqual(
                len(covered), floor,
                "domain '{}' only measures {} of {} traits: {}".format(
                    d, len(covered), len(_TRAITS), sorted(covered))
            )


if __name__ == "__main__":
    unittest.main()
