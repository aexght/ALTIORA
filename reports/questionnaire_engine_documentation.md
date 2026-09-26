# Questionnaire Scoring Engine — Career Guidance System

## Overview

The Questionnaire Scoring Engine transforms student responses to an aptitude questionnaire into the 8 trait scores required by the Random Forest prediction model. It is a standalone, reusable module with no dependency on the ML pipeline.

---

## 1. Why Questions are Stored in JSON

**Decoupling content from code.** The `questions.json` file contains all question text, options, and scores. This means:

- **A non-developer can edit questions.** A counselor or domain expert can add, remove, or rephrase questions without touching Python code.
- **Multi-language support is trivial.** Each locale gets its own `questions_XX.json` file.
- **A/B testing is straightforward.** Different question variants can be loaded via configuration.
- **No code change = no redeploy.** For minor text fixes, only the JSON file needs to be updated.

---

## 2. Why Scoring is Isolated from ML

The questionnaire module has **no imports** from scikit-learn, joblib, or any prediction code:

- `questionnaire.py` → depends only on `json` and `os`
- `questions.json` → pure content

This isolation provides several benefits:

| Concern | Benefit |
|---|---|
| **Testability** | Scoring logic can be unit-tested without loading a 117 MB model |
| **Reusability** | The same module can score questionnaires for any purpose — not just career prediction |
| **Security** | The questionnaire endpoint never touches the model file on disk |
| **Latency** | Scoring is instant (JSON parse + arithmetic), no model loading required |
| **Maintenance** | If the ML model is replaced (e.g., XGBoost), the questionnaire code doesn't change |

---

## 3. How Normalization Works

Each of the 8 traits has exactly 3 questions. Each question has 4 options with scores:

| Option | Score |
|---|---|
| Strong (best fit) | 5 |
| Moderate-high | 4 |
| Moderate-low | 2 |
| Low (least fit) | 1 |

Note: Some questions use [5, 3, 2, 1] instead of [5, 4, 2, 1] (questions about data analysis, news analysis, scientific curiosity). The scoring engine handles both structures automatically.

**Normalization formula:**

raw_total = sum of selected scores (max = 15, min = 3)

score = round((raw_total / max_possible) × 100)

**Examples:**

| Scenario | Raw | Max | Score |
|---|---|---|---|
| All max (5+5+5) | 15 | 15 | 100 |
| Balanced (4+4+4) | 12 | 15 | 80 |
| All min (1+1+1) | 3 | 15 | 20 |

The result is always an integer in the 0–100 range, matching the feature scale expected by the Random Forest model.

---

## 4. Validation Rules

The `validate_answers()` function checks:

| Check | Error Message |
|---|---|
| Answers is not a dict | `Answers must be a dict mapping question_id to option_id.` |
| Question ID is not an integer | `question_id 'X' is not a valid integer.` |
| Question ID does not exist | `question_id X does not exist.` |
| Duplicate response | `Duplicate response for question_id X.` |
| Option value is not valid for that question | `question_id X: invalid option_id Y. Valid scores: ...` |
| Missing answers | `Missing answers for question_id(s): ...` |

All errors are collected before returning, so the frontend gets a complete validation report in a single request.

---

## 5. API Reference

### `load_questions()`

Returns the full `questions.json` as a Python list of dicts.

### `get_trait_questions(trait)`

Returns all questions belonging to a specific trait (e.g., `"Technical_Interest"`).

### `validate_answers(answers)`

**Input:** `dict` mapping `question_id` (int or string) → `option_id` (int, the score value).

**Output:** `list` of error strings. Empty list = valid.

### `compute_scores(answers)`

**Input:** Same format as `validate_answers`.

**Output on success:** `dict` with 8 trait keys mapped to integer scores (0–100).

**Output on validation failure:** `{"errors": ["...", "..."]}`.

### `merge_features(academic_data, questionnaire_scores)`

**Input:**
- `academic_data`: `dict` with keys matching the 14 academic features (`Class12_Stream`, `Subject_Combination`, 10 subject marks, `Class10_Percentage`, `Class12_Percentage`)
- `questionnaire_scores`: output of `compute_scores()` (the dict, not error-wrapped)

**Output:** `dict` with exactly 22 keys in the exact order expected by `predict_domains()`.

---

## 6. Integration with predict.py

```python
from questionnaire import compute_scores, merge_features
from predict import predict_domains
from recommend import recommend_from_prediction

# Step 1: Student submits answers + academics
answers = {1: 5, 2: 4, ..., 24: 3}
academic = {
    "Class12_Stream": "Science",
    "Subject_Combination": "PCM",
    "Physics_Marks": 90,
    ...
}

# Step 2: Compute questionnaire scores
scores = compute_scores(answers)
if "errors" in scores:
    return {"error": scores["errors"]}

# Step 3: Merge into 22-feature vector
features = merge_features(academic, scores)

# Step 4: Predict + recommend (existing pipeline)
prediction = predict_domains(features)
recommendations = recommend_from_prediction(prediction)
```

---

## 7. File Structure

```
questionnaire.py                  # Scoring engine module
questions.json                    # 24 questions across 8 traits

reports/
  questionnaire_engine_documentation.md   # This file
```

---

## 8. Configuration

- **Questions file path:** `questions.json` in the project root (configurable via `_QUESTIONS_PATH`)
- **Traits:** Defined in `_TRAITS` list in `questionnaire.py` — must match the `NUMERIC_COLS` in `preprocessing.py` (excluding `Class10_Percentage` and `Class12_Percentage`)

---

## 9. Dependencies

- `json` (standard library)
- `os` (standard library)

Zero external dependencies.
