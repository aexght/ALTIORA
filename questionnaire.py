import os
import json
import random

_BASE = os.path.dirname(__file__)
_QUESTIONS_PATH = os.path.join(_BASE, "questions.json")

_TRAITS = [
    "Logical_Score", "Analytical_Score", "Technical_Interest",
    "Business_Interest", "Creativity_Score", "Communication_Score",
    "Leadership_Score", "Research_Interest",
]

_SUPPORTED_TRAITS = set(_TRAITS)

# Assessment domains/categories used across the question bank (the `type`
# field of every question). The selection engine strata by these domains.
QUESTION_DOMAINS = ("Scenario", "Preference", "Behaviour", "Aptitude")

# Assessment lengths the frontend can administer.
SUPPORTED_ASSESSMENT_LENGTHS = (10, 20, 30, 40)

# Client-side anti-repetition history cap (recently used question IDs).
RECENT_HISTORY_CAP = 60


def load_questions():
    with open(_QUESTIONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_questions_by_domain(questions=None):
    """Group questions by their assessment domain (`type` field)."""
    if questions is None:
        questions = load_questions()
    domains = {d: [] for d in QUESTION_DOMAINS}
    for q in questions:
        domains.setdefault(q["type"], []).append(q)
    return domains


def select_assessment(length, exclude=None, rng=None):
    """Select `length` questions via stratified random sampling.

    - `length` must be in SUPPORTED_ASSESSMENT_LENGTHS.
    - Questions are sampled per domain so every assessment is approximately
      balanced across the 4 domains (e.g. 40 -> 10/10/10/10, 10 -> 2/2/3/3).
    - `exclude` is a preference (recently used question IDs): fresh questions
      are preferred within each domain; if a domain does not have enough fresh
      questions the selection safely falls back to recently-used questions, so
      questions are never permanently eliminated.
    - The returned order is randomised once; the caller keeps it fixed for the
      duration of one assessment.

    `rng` is only used by tests to make sampling deterministic.
    """
    if length not in SUPPORTED_ASSESSMENT_LENGTHS:
        raise ValueError(
            "length must be one of {} (got {}).".format(
                SUPPORTED_ASSESSMENT_LENGTHS, length
            )
        )

    rng = rng if rng is not None else random
    exclude = set(exclude or ())
    exclude = {int(i) for i in exclude}

    by_domain = get_questions_by_domain()

    total_available = sum(len(pool) for pool in by_domain.values())
    if total_available < length:
        raise ValueError(
            "Not enough questions in the bank to build a "
            "{}-question assessment ({} available).".format(length, total_available)
        )

    quotas = _quota_plan(length, by_domain, rng)

    selected = []
    selected_ids = set()
    for domain in QUESTION_DOMAINS:
        pool = by_domain[domain]
        fresh = [q for q in pool if q["id"] not in exclude]
        need = quotas[domain]
        if len(fresh) >= need:
            chosen = rng.sample(fresh, need)
        else:
            chosen = fresh
            used_ids = {q["id"] for q in chosen}
            fallback = [q for q in pool if q["id"] not in used_ids]
            chosen = chosen + rng.sample(fallback, need - len(chosen))
        for q in chosen:
            selected.append(q)
            selected_ids.add(q["id"])

    rng.shuffle(selected)
    return selected


def _quota_plan(length, by_domain, rng):
    """Compute per-domain selection quotas.

    Ideal quotas are `length // 4` per domain with the remainder distributed
    to a randomly ordered subset of domains. Each quota is clamped to the
    domain's pool size, and any deficit is redistributed to domains with spare
    capacity. With the expanded bank (~34-35 questions per domain) the clamps
    never bind and quotas match the balanced target (e.g. 40 -> 10/10/10/10).
    """
    base, rem = divmod(length, len(QUESTION_DOMAINS))
    quotas = {d: base for d in QUESTION_DOMAINS}
    for d in rng.sample(QUESTION_DOMAINS, rem):
        quotas[d] += 1

    for d in QUESTION_DOMAINS:
        quotas[d] = min(quotas[d], len(by_domain[d]))

    deficit = length - sum(quotas.values())
    while deficit > 0:
        candidates = [
            d for d in QUESTION_DOMAINS if quotas[d] < len(by_domain[d])
        ]
        if not candidates:
            raise ValueError(
                "Bank cannot satisfy a balanced {}-question assessment.".format(length)
            )
        quotas[rng.choice(candidates)] += 1
        deficit -= 1

    return quotas


def _build_trait_maxima(questions):
    maxima = {t: 0 for t in _TRAITS}
    for q in questions:
        for opt in q["options"]:
            for t, v in opt["contributes"].items():
                if v > maxima[t]:
                    maxima[t] = v
    return maxima


def validate_answers(answers):
    questions = load_questions()
    q_map = {q["id"]: q for q in questions}
    errors = []

    if not isinstance(answers, dict):
        return ["Answers must be a dict mapping question_id to option_id."]

    answered_ids = set()
    for q_id_str, opt_id in answers.items():
        try:
            q_id = int(q_id_str)
        except (ValueError, TypeError):
            errors.append("question_id '{}' is not a valid integer.".format(q_id_str))
            continue

        if q_id not in q_map:
            errors.append("question_id {} does not exist.".format(q_id))
            continue

        if q_id in answered_ids:
            errors.append("Duplicate response for question_id {}.".format(q_id))
            continue
        answered_ids.add(q_id)

        question = q_map[q_id]
        valid_ids = [o["id"] for o in question["options"]]
        if opt_id not in valid_ids:
            valid_str = ", ".join(str(v) for v in valid_ids)
            errors.append(
                "question_id {}: invalid option_id '{}'. "
                "Valid options for this question: {}.".format(q_id, opt_id, valid_str)
            )

    # Cardinality of the active question set. The frontend administers exactly
    # N questions (N in {10, 20, 30, 40}) chosen by select_assessment, which may
    # be ANY set of N distinct valid ids from the master bank (no longer a
    # sequential prefix). Structural errors above already invalidate the
    # payload; only check cardinality once the submitted id set is well-formed.
    if not errors:
        submitted_ids = sorted(answered_ids)
        n = len(submitted_ids)
        if n == 0:
            errors.append("No answers provided for the assessment.")
        elif n not in SUPPORTED_ASSESSMENT_LENGTHS:
            errors.append(
                "Answers must cover exactly 10, 20, 30, or 40 questions "
                "(got {}).".format(n)
            )

    return errors


def compute_scores(answers):
    errors = validate_answers(answers)
    if errors:
        return {"errors": errors}

    questions = load_questions()
    q_map = {q["id"]: q for q in questions}

    trait_raw = {t: 0 for t in _TRAITS}
    answered_questions = []
    for q_id_str, opt_id in answers.items():
        q_id = int(q_id_str)
        question = q_map[q_id]
        answered_questions.append(question)
        matching = [o for o in question["options"] if o["id"] == opt_id]
        if not matching:
            continue
        option = matching[0]
        for t, v in option["contributes"].items():
            if t in trait_raw:
                trait_raw[t] += v

    # Normalize against the theoretical maximum represented by the submitted
    # questions only. A subset assessment (10/20/30 questions) therefore spans
    # the full 0-100 range instead of being deflated by unseen questions,
    # while a 40-question submission keeps the original all-question baseline.
    scores = {}
    for trait in _TRAITS:
        max_t = sum(
            max(o["contributes"].get(trait, 0) for o in q["options"])
            for q in answered_questions
        )
        if max_t == 0:
            scores[trait] = 0
        else:
            normalized = round((trait_raw[trait] / max_t) * 100)
            scores[trait] = normalized

    return scores


def merge_features(academic_data, questionnaire_scores):
    from preprocessing import FEATURE_COLS

    merged = {}
    for col in FEATURE_COLS:
        if col in ["Class12_Stream", "Subject_Combination"]:
            merged[col] = academic_data.get(col, "")
        elif col in [
            "Physics_Marks", "Chemistry_Marks", "Mathematics_Marks",
            "Biology_Marks", "Computer_Science_Marks", "Statistics_Marks",
            "Accountancy_Marks", "Economics_Marks", "Business_Studies_Marks",
            "English_Marks", "Class10_Percentage", "Class12_Percentage",
        ]:
            merged[col] = float(academic_data.get(col, 0))
        elif col in _SUPPORTED_TRAITS:
            merged[col] = float(questionnaire_scores.get(col, 0))
        else:
            merged[col] = float(academic_data.get(col, 0))

    return merged


def main():
    print("=" * 60)
    print("QUESTIONNAIRE SCORING ENGINE TEST")
    print("=" * 60)

    questions = load_questions()
    print("\nLoaded {} questions".format(len(questions)))

    # Demo uses a fixed 40-question stratified assessment.
    sample_questions = select_assessment(40)
    sample_answers = {str(q["id"]): q["options"][0]["id"] for q in sample_questions}

    print("\nSample: All answers = first option")
    scores = compute_scores(sample_answers)
    print(json.dumps(scores, indent=2))

    print("\nSample: All answers = last option (max contribution)")
    sample_answers_max = {str(q["id"]): q["options"][-1]["id"] for q in sample_questions}
    scores_max = compute_scores(sample_answers_max)
    print(json.dumps(scores_max, indent=2))

    print("\nValidation tests:")
    print("  Missing answers:   {}".format(validate_answers({"1": "A"})))
    print("  Invalid q_id:      {}".format(validate_answers({"abc": "A"})))
    print("  Non-existent q:    {}".format(validate_answers({"99": "A"})))
    answers_dup = dict(sample_answers)
    answers_dup["01"] = "A"
    print("  Duplicate:         {}".format(len(validate_answers(answers_dup)) > 0))
    print("  Invalid option:    {}".format(validate_answers({"1": "Z"})))
    print("  Valid 40:          {}".format(len(validate_answers(sample_answers)) == 0))

    academic_data = {
        "Class12_Stream": "Science",
        "Subject_Combination": "PCM",
        "Physics_Marks": 85, "Chemistry_Marks": 78, "Mathematics_Marks": 92,
        "Biology_Marks": 0, "Computer_Science_Marks": 0, "Statistics_Marks": 0,
        "Accountancy_Marks": 0, "Economics_Marks": 0, "Business_Studies_Marks": 0,
        "English_Marks": 80, "Class10_Percentage": 88.5, "Class12_Percentage": 82.0,
    }

    merged = merge_features(academic_data, scores)
    print("\nMerged features ({}):".format(len(merged)))
    from preprocessing import FEATURE_COLS
    for col in FEATURE_COLS:
        print("  {:30s} = {}".format(col, merged.get(col, "MISSING")))


if __name__ == "__main__":
    import json
    main()
