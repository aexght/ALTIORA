# Recommendation Engine — Career Guidance System

## Overview

The Recommendation Engine transforms the Random Forest model's 10-class domain probabilities into the Top 5 most suitable course recommendations. It is a lightweight, deterministic, rule-based system — no additional ML model, no eligibility rules, no manual weight assignments.

---

## 1. How Course Popularity is Computed

**Source:** `student_career_with_domains.xlsx` (86,000 rows, 113 unique courses across 10 domains).

**Formula (per domain):**

raw_count = count of students who chose course C in domain D

max_count = maximum raw_count across all courses in domain D

popularity(C, D) = raw_count(C, D) / max_count(D)

**Result:** Each of the 113 courses gets a popularity score between 0 and 1 within its domain. The most popular course in each domain always scores 1.0; all others are relative fractions.

**Example (Technology & Computing):**

| Course | Raw Count | Popularity |
|---|---|---|
| BCA | 1173 | 1.0000 |
| B.Tech CSE | 1126 | 0.9599 |
| B.Tech IT | 1121 | 0.9557 |
| B.Tech Cybersecurity | 1103 | 0.9403 |
| AI & ML | 953 | 0.8124 |

---

## 2. Two-Stage Ranking Strategy

### Stage 1 — Representative Course Selection

Within each Career Domain, only courses whose normalized popularity is `>= 90%` of the domain's maximum popularity are selected as **representative courses**.

**Why 90%?** Courses with popularity ≥ 0.90 are educationally equivalent in terms of student demand. The difference between BCA (1.00) and B.Tech CSE (0.96) is not meaningful — both are high-demand Technology courses. The threshold prevents tiny popularity differences from dominating recommendations.

**Effect across domains:**

| Domain | Total Courses | Representative Courses |
|---|---|---|
| Agriculture Environment & Food | 10 | 10 (all) |
| Business & Management | 11 | 1 (BBA) |
| Commerce & Finance | 17 | 1 (B.Com) |
| Design Media & Creative | 4 | 4 (all) |
| Engineering | 15 | 1 (B.Tech Mechanical) |
| Law & Legal Studies | 3 | 3 (all) |
| Life Sciences & Biotechnology | 9 | 1 (B.Sc Biotech) |
| Medical & Health Sciences | 23 | 1 (MBBS) |
| Physical & Mathematical Sciences | 5 | 3 |
| Technology & Computing | 16 | 4 |

Domains with uniformly distributed demand (Agriculture, Design, Law) keep all their courses. Domains with a dominant single course (Commerce → B.Com, Medical → MBBS) naturally consolidate, preventing less representative courses from appearing as top recommendations.

### Stage 2 — Scoring and Ranking

After selecting representative courses:

Course Score = Domain Probability × Normalized Course Popularity

The formula is identical to the original. The only change is the candidate pool — only representative courses compete, ensuring that minor popularity differences within a domain do not artificially elevate or suppress courses.

### Why Two-Stage is Superior to Raw Popularity Ranking

**Before (raw popularity):**

- Student with Commerce 57% + Design 11% would get: B.Com (57.0), B.Sc Economics (47.1), B.Com Accounting (45.8), Actuarial Science (18.3), B.Sc Finance (18.1)
- All 5 recommendations come from Commerce — Design at 11% is buried by Commerce's mid-popularity courses

**After (representative filtering):**

- Same student gets: B.Com (57.0), B.Des Fashion (11.0), B.Des Product Design (10.8), BJMC (10.6), B.Des UX (10.6)
- Commerce's secondary courses (Economics at 0.83, Accounting at 0.80) are filtered out since they are not representative
- Design courses now surface because the student genuinely has Design affinity
- The student gets educationally diverse recommendations that reflect their actual profile

---

## 3. Why No Additional ML Model is Required

1. **The Random Forest already outputs calibrated probabilities.** Adding a second ML model would introduce unnecessary complexity, latency, and maintenance burden.

2. **Course recommendation is a ranking problem, not a prediction problem.** The goal is to sort known items (courses) by relevance — a weighted score formula with representative filtering is the standard approach in production systems.

3. **The data supports a purely statistical approach.** With 86,000 rows and 113 courses, the popularity counts are statistically stable. The minimum support per course is ~600 students, which gives reliable popularity estimates.

4. **Deterministic systems are easier to debug, test, and explain.** There is no black-box behavior. Every recommended course can be traced back to its domain probability, popularity score, and representative status.

---

## 4. Explanation Templates

Every recommended course includes a deterministic `reason` field with two template sentences:

1. `"High {domain} domain probability"` — Always present. Indicates the RF model assigned meaningful probability to this domain.

2. One of:
   - `"One of the most common {domain} courses in the historical dataset"` — For courses with popularity == 1.0 (the most popular course in the domain)
   - `"Representative course within {domain} domain"` — For courses with popularity >= 0.90 but not the maximum

No LLMs, no SHAP, no manual weights. The explanation is fully deterministic and reproducible.

---

## 5. Modularity and Future Extension

The engine is intentionally decoupled from the prediction pipeline:

- **`recommend.py`** is an independent module that only depends on `pandas` and the dataset file.
- It exposes a clean API: `recommend_courses(domain_probabilities)` → `List[Dict]`
- Integration with Flask requires only:
  ```python
  from recommend import recommend_from_prediction
  result = predict_domains(student_data)
  courses = recommend_from_prediction(result)
  ```

**Future extensions:**
- **College recommendations:** A separate `college_popularity_index` can be built from a `college_domain_dataset` and blended using the same probability × popularity formula.
- **Filters:** Pre/post filters (e.g., "only show 4-year degrees", "exclude colleges without hostel") can be applied to the scored list without modifying the scoring logic.
- **A/B testing:** The scoring formula or representative threshold can be tuned independently from the ML model.
- **Personalization:** If user feedback data is collected, popularity can be replaced with a collaborative filtering score using the same interface.

---

## 6. File Structure

```
recommend.py                      # Main recommendation module
  get_popularity_index()          # Builds/lazily loads the course popularity index
  get_top_courses_by_domain()     # Debug helper: top N courses in a domain
  recommend_courses()             # Core: probabilities dict → ranked course list
  recommend_from_prediction()     # Integration helper: prediction_result → ranked course list

reports/
  recommendation_engine_documentation.md   # This file
```

---

## 7. API Reference

### `recommend_courses(domain_probabilities, top_n=5)`

**Input:** `dict` mapping domain name → probability percentage (0–100).

**Output:** `list` of up to `top_n` dicts:
```json
[
  {
    "course": "BCA",
    "domain": "Technology & Computing",
    "score": 35.00,
    "reason": [
      "High Technology & Computing domain probability",
      "One of the most common Technology & Computing courses in the historical dataset"
    ]
  },
  ...
]
```

### `recommend_from_prediction(prediction_result, top_n=5)`

**Input:** The dict returned by `predict_domains()` (contains `Career_Readiness_Ranking`).

**Output:** Same format as `recommend_courses()`.

---

## 8. Configuration

The representative threshold is defined as a module-level constant in `recommend.py`:

```python
_REPRESENTATIVE_THRESHOLD = 0.90
```

This can be adjusted between 0.0 (include all courses) and 1.0 (only the single most popular course per domain) without changing any other logic.

---

## 9. Dependencies

- `pandas` (read dataset, groupby operations)
- `student_career_with_domains.xlsx` (popularity source, ~2.5 MB)

The engine is independent of `scikit-learn`, `joblib`, and the model files.
