import os
import numpy as np
import joblib

from preprocessing import (
    load_data, CATEGORICAL_COLS, SUBJECT_MARKS_COLS, NUMERIC_COLS
)

_BASE = os.path.dirname(__file__)

MODEL_PATH = os.path.join(_BASE, "models", "domain_model.pkl")
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = os.path.join(_BASE, "models", "career_model_tuned.pkl")
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = os.path.join(_BASE, "models", "career_model.pkl")

CALIBRATED_PATH = os.path.join(_BASE, "models", "domain_model_calibrated.pkl")
ENCODERS_PATH = os.path.join(_BASE, "encoders", "saved_encoders.pkl")
FEATURE_ORDER = CATEGORICAL_COLS + SUBJECT_MARKS_COLS + NUMERIC_COLS

_CONFIDENCE_THRESHOLDS = [
    (80.0, "Very High"),
    (60.0, "High"),
    (40.0, "Moderate"),
    (20.0, "Low"),
    (0.0, "Very Low"),
]

_ASSESSMENT_TRAIT_LABELS = {
    "Logical_Score": {
        "label": "Logical Reasoning",
        "description": "Your responses indicate a tendency toward structured, step-by-step thinking and systematic problem-solving."
    },
    "Analytical_Score": {
        "label": "Analytical Thinking",
        "description": "Your responses show a consistent preference for examining information, identifying patterns, and comparing options before deciding."
    },
    "Technical_Interest": {
        "label": "Technical Interest",
        "description": "Your responses indicate an inclination toward technical systems, tools, and engineering-oriented challenges."
    },
    "Business_Interest": {
        "label": "Business Interest",
        "description": "Your responses suggest an interest in commerce, organizational thinking, and business decision-making."
    },
    "Creativity_Score": {
        "label": "Creative Thinking",
        "description": "Your responses indicate an interest in generating new ideas, exploring unconventional approaches, and creative expression."
    },
    "Communication_Score": {
        "label": "Communication",
        "description": "Your responses suggest comfort with expressing ideas clearly and working collaboratively with others."
    },
    "Leadership_Score": {
        "label": "Leadership Orientation",
        "description": "Your responses indicate a tendency toward taking initiative, organizing others, and working toward collective goals."
    },
    "Research_Interest": {
        "label": "Research Orientation",
        "description": "Your responses show an inclination toward in-depth inquiry, evidence-based reasoning, and sustained investigation of questions."
    },
}

_ACADEMIC_LABELS = {
    "Mathematics_Marks": "Mathematics",
    "Physics_Marks": "Physics",
    "Chemistry_Marks": "Chemistry",
    "Biology_Marks": "Biology",
    "Computer_Science_Marks": "Computer Science",
    "Accountancy_Marks": "Accountancy",
    "Economics_Marks": "Economics",
    "Business_Studies_Marks": "Business Studies",
    "English_Marks": "English",
    "Class10_Percentage": "Class 10 overall",
    "Class12_Percentage": "Class 12 overall",
}

_ASSESSMENT_TRAITS = list(_ASSESSMENT_TRAIT_LABELS.keys())
_SUBJECT_MARK_KEYS = [
    "Mathematics_Marks", "Physics_Marks", "Chemistry_Marks", "Biology_Marks",
    "Computer_Science_Marks", "Accountancy_Marks", "Economics_Marks",
    "Business_Studies_Marks", "English_Marks",
    "Class10_Percentage", "Class12_Percentage",
]

_TRAIT_STRENGTH_THRESHOLDS = [
    (80, "Strong"),
    (60, "Moderate"),
    (40, "Developing"),
]


def _trait_strength_label(val):
    for threshold, label in _TRAIT_STRENGTH_THRESHOLDS:
        if val >= threshold:
            return label
    return "Low"


def _load_best_model():
    if os.path.exists(CALIBRATED_PATH):
        return joblib.load(CALIBRATED_PATH)
    return joblib.load(MODEL_PATH)


def load_model_and_encoders():
    model = _load_best_model()
    encoders = joblib.load(ENCODERS_PATH)
    return model, encoders


def _get_confidence_label(probability_pct):
    for threshold, label in _CONFIDENCE_THRESHOLDS:
        if probability_pct >= threshold:
            return label
    return "Very Low"


def _generate_structured_explanation(student_features, predicted_domain, model, encoders):
    """
    Build a structured reasoning object derived from actual model feature values.

    Returns a dict with:
      - assessment_profile: list of {trait, label, value, strength, description}
      - academic_evidence: list of {subject, value, strength}
      - primary_evidence: names of top contributing model features
      - reasoning_summary: a deterministic narrative paragraph
      - legacy_explanation: backward-compatible list of strings
    """
    # --- Assessment profile (all 8 traits, from actual questionnaire scores) ---
    assessment_profile = []
    for trait_key in _ASSESSMENT_TRAITS:
        val = student_features.get(trait_key)
        if val is None:
            continue
        try:
            fval = float(val)
        except (ValueError, TypeError):
            continue
        if fval <= 0:
            continue  # skip traits with zero signal (unanswered / not contributed)
        info = _ASSESSMENT_TRAIT_LABELS[trait_key]
        assessment_profile.append({
            "trait": trait_key,
            "label": info["label"],
            "value": round(fval, 1),
            "strength": _trait_strength_label(fval),
            "description": info["description"],
        })
    assessment_profile.sort(key=lambda x: -x["value"])

    # --- Academic evidence (all subject marks with meaningful values) ---
    academic_evidence = []
    for feat_key in _SUBJECT_MARK_KEYS:
        val = student_features.get(feat_key)
        if val is None:
            continue
        try:
            fval = float(val)
        except (ValueError, TypeError):
            continue
        if fval <= 0:
            continue
        label = _ACADEMIC_LABELS.get(feat_key, feat_key)
        strength = "Excellent" if fval >= 80 else ("Strong" if fval >= 65 else ("Good" if fval >= 50 else None))
        if strength is None:
            continue
        academic_evidence.append({
            "subject": feat_key,
            "label": label,
            "value": round(fval, 1),
            "strength": strength,
        })
    academic_evidence.sort(key=lambda x: -x["value"])

    # --- Primary evidence: top contributing features (importance × student value) ---
    tree_importances = np.array([tree.feature_importances_ for tree in model.estimators_])
    domain_fi = tree_importances.mean(axis=0)

    scored = []
    for idx, feat_name in enumerate(FEATURE_ORDER):
        if feat_name in CATEGORICAL_COLS:
            continue
        import_val = domain_fi[idx]
        if import_val < 0.01:
            continue
        raw_val = student_features.get(feat_name)
        if raw_val is None:
            continue
        try:
            fval = float(raw_val)
        except (ValueError, TypeError):
            continue
        contribution = import_val * fval
        scored.append((contribution, feat_name, fval))

    scored.sort(reverse=True)
    primary_evidence = [feat for _, feat, _ in scored[:6]]

    # --- Determine dominant pattern ---
    top_assessment = [x for x in assessment_profile if x["value"] >= 60]
    top_academic = [x for x in academic_evidence if x["value"] >= 70]

    # Characterise assessment pattern
    assessment_summary = ""
    if top_assessment:
        top_labels = [x["label"] for x in top_assessment[:3]]
        if len(top_labels) == 1:
            assessment_summary = "Your assessment responses show a notable signal in {}.".format(top_labels[0])
        elif len(top_labels) == 2:
            assessment_summary = "Your assessment responses show notable signals in {} and {}.".format(*top_labels)
        else:
            assessment_summary = "Your assessment responses show notable signals across {}, {}, and {}.".format(*top_labels[:3])
    else:
        assessment_summary = "Your assessment responses provided a measured profile across multiple dimensions."

    # Characterise academic pattern
    academic_summary = ""
    if top_academic:
        top_subj = [x["label"] for x in top_academic[:3]]
        academic_summary = "Your academic profile shows strong performance in {}.".format(
            ", ".join(top_subj[:-1]) + (" and " if len(top_subj) > 1 else "") + top_subj[-1]
            if len(top_subj) > 1 else top_subj[0]
        )
    else:
        academic_summary = "Your academic performance contributed to the overall profile."

    # --- Build reasoning narrative ---
    reasoning_summary = (
        "ALTIORA recommended {domain} based on the combination of signals in your profile, "
        "not from any single subject or questionnaire answer. "
        "{assessment} {academic} "
        "When these signals are evaluated together by the Random Forest model — which "
        "aggregates patterns across many decision trees — {domain} emerged as the career "
        "direction with the strongest overall alignment with your profile.".format(
            domain=predicted_domain,
            assessment=assessment_summary,
            academic=academic_summary,
        )
    )

    # --- Legacy backward-compatible explanation (flat list) ---
    legacy = []
    for item in academic_evidence[:3]:
        legacy.append("{} {}".format(item["strength"], _ACADEMIC_LABELS.get(item["subject"], item["subject"])))
    for item in top_assessment[:2]:
        legacy.append("{} {}".format(item["strength"], item["label"]))
    if not legacy:
        legacy.append("Consistent academic performance and aptitude profile.")

    return {
        "assessment_profile": assessment_profile,
        "academic_evidence": academic_evidence,
        "primary_evidence": primary_evidence,
        "reasoning_summary": reasoning_summary,
        "assessment_pattern": assessment_summary,
        "academic_pattern": academic_summary,
        "legacy_explanation": legacy,
    }


def predict_domains(student_features: dict):
    model, encoders = load_model_and_encoders()

    raw_vector = []
    for col in FEATURE_ORDER:
        val = student_features.get(col, 0)
        if col in CATEGORICAL_COLS:
            le = encoders[col]
            val_str = str(val)
            if val_str in le.classes_:
                val = le.transform([val_str])[0]
            else:
                val = -1
        elif col in SUBJECT_MARKS_COLS:
            val = float(val) if val is not None else 0.0
        else:
            val = float(val) if val is not None else 0.0
        raw_vector.append(val)

    X_input = np.array([raw_vector])
    probas = model.predict_proba(X_input)[0]
    predicted_class = model.predict(X_input)[0]

    le_target = encoders.get("Career_Domain", encoders.get("Chosen_Course"))
    domain_names = le_target.classes_
    predicted_domain = le_target.inverse_transform([predicted_class])[0]
    predicted_prob = float(probas[predicted_class]) * 100

    sorted_indices = np.argsort(probas)[::-1]

    ranking = []
    top3 = []
    for rank, idx in enumerate(sorted_indices, 1):
        name = domain_names[idx]
        prob_pct = round(float(probas[idx]) * 100, 2)
        entry = {"domain": name, "probability": prob_pct}
        ranking.append(entry)
        if rank <= 3:
            top3.append(entry)

    structured = _generate_structured_explanation(student_features, predicted_domain, model, encoders)
    confidence = _get_confidence_label(predicted_prob)

    return {
        "Predicted_Domain": predicted_domain,
        "Prediction_Probability": round(predicted_prob, 2),
        "Prediction_Confidence": confidence,
        "Career_Readiness_Ranking": ranking,
        "Top_3_Domains": top3,
        "Prediction_Explanation": structured["legacy_explanation"],
        "Structured_Explanation": structured,
    }


def predict_top5(student_features: dict):
    result = predict_domains(student_features)
    return [(d["domain"], d["probability"]) for d in result["Career_Readiness_Ranking"][:5]]


def main():
    df = load_data()
    sample = df.iloc[0].to_dict()

    print("Sample student features:")
    for k, v in sample.items():
        if k not in ["Student_ID", "Satisfaction_Score"]:
            print("  {}: {}".format(k, v))

    result = predict_domains(sample)

    print("\n" + "=" * 55)
    print("PREDICTION OUTPUT")
    print("=" * 55)
    print("\nPredicted Domain: {}".format(result["Predicted_Domain"]))
    print("Probability: {:.2f}%".format(result["Prediction_Probability"]))
    print("Confidence: {}".format(result["Prediction_Confidence"]))

    print("\nCareer Readiness Ranking:")
    print("-" * 55)
    for entry in result["Career_Readiness_Ranking"]:
        print("  {domain:45s} {prob:6.2f}%".format(
            domain=entry["domain"], prob=entry["probability"]))

    print("\nTop 3 Domains:")
    print("-" * 55)
    for rank, entry in enumerate(result["Top_3_Domains"], 1):
        print("  {}. {domain} ({prob:.2f}%)".format(
            rank, domain=entry["domain"], prob=entry["probability"]))

    print("\nPrediction Explanation:")
    print("-" * 55)
    for line in result["Prediction_Explanation"]:
        print("  \u2022 {}".format(line))

    print("\nFull JSON output:")
    import json
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
