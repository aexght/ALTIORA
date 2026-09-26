# Prediction Layer Documentation

## Changes Made

### 1. `predict.py` — Complete Rewrite

The prediction module was updated to support the new career domain (10-class) model
while maintaining backward compatibility.

### 2. Probability Calibration — Evaluated, Not Applied

**Method**: CalibratedClassifierCV (Isotonic & Sigmoid) on a 60/20/20 split.

**Results**:

| Method | Log Loss | Brier (macro) |
|--------|----------|---------------|
| Uncalibrated | 0.9471 | 0.0490 |
| Isotonic | 0.9086 | 0.0478 |
| Sigmoid | 0.9846 | 0.0484 |

**Decision**: Keep uncalibrated model.

Improvement from isotonic calibration is only ~4% in log loss and ~2.4% in Brier score.
Random Forest with 200 trees produces naturally well-calibrated probabilities due to
averaging across many trees. The added complexity of a calibration wrapper is not justified.

### 3. New Output Schema

```json
{
    "Predicted_Domain": "Technology & Computing",
    "Prediction_Probability": 47.49,
    "Prediction_Confidence": "Moderate",
    "Career_Readiness_Ranking": [
        {"domain": "Technology & Computing", "probability": 47.49},
        {"domain": "Engineering", "probability": 41.33},
        ...
    ],
    "Top_3_Domains": [
        {"domain": "Technology & Computing", "probability": 47.49},
        {"domain": "Engineering", "probability": 41.33},
        {"domain": "Agriculture Environment & Food", "probability": 6.52}
    ],
    "Prediction_Explanation": [
        "Excellent Technical interest",
        "Excellent Logical reasoning",
        "Good Communication skills",
        "Strong Research inclination"
    ]
}
```

### 4. Confidence Level Mapping

| Probability | Label |
|------------|-------|
| >= 80% | Very High |
| 60–79% | High |
| 40–59% | Moderate |
| 20–39% | Low |
| < 20% | Very Low |

### 5. Lightweight Explanation

Generated without SHAP/LIME using:
- Per-feature importance × student feature value
- Top 4 contributing features with value thresholds (>=80: Excellent, >=65: Strong, >=50: Good)
- Template-based natural language output

---

## Design Decisions

### Why prediction probabilities are used as readiness scores

1. Probabilities are well-calibrated posterior estimates P(Domain | Features).
2. They naturally sum to 1.0 across all domains, providing a complete picture.
3. No manual weighting or formula derivation is needed.
4. The model captures non-linear interactions that manual formulas cannot.

### Why SHAP/LIME were intentionally omitted

1. SHAP requires storing the full training dataset (86k rows x 22 cols) for background
   distributions, adding ~15MB per model load.
2. SHAP computation per prediction is 10-100x slower than the prediction itself.
3. LIME fits a local surrogate for every prediction, adding non-determinism.
4. For 10 broad domains with only 22 features, the feature importance-based
   explanation is sufficient and trivially reproducible.
5. SHAP/LIME will be added as a future enhancement for course-level recommendations
   (113 classes) where fine-grained explanations add more value.

### Why lightweight deterministic explanations are sufficient

1. The feature set (22 features) is small enough for manual inspection.
2. Domain-level predictions (10 classes) are coarse enough that "which features
   drove this" is easily answered by importance × value.
3. Deterministic explanations produce identical output for identical input,
   which is essential for research reproducibility and user trust.
4. The template-based approach is trivially auditable and cannot produce
   misleading attributions.

---

## Future Integration Architecture

```
                    ┌─────────────────────┐
                    │   predict_top5()    │ ← Backward-compatible entry point
                    └─────────┬───────────┘
                              │
                    ┌─────────▼───────────┐
                    │  predict_domains()  │ ← Main prediction function
                    └─────────┬───────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
    ┌─────────────┐  ┌───────────────┐  ┌───────────┐
    │Course Rec   │  │College Rec    │  │XAI        │
    │Engine       │  │Engine (future)│  │(future)   │
    │(next phase) │  │               │  │SHAP/LIME  │
    └─────────────┘  └───────────────┘  └───────────┘
```

- **Course Recommendation Engine**: Uses `Predicted_Domain` to fetch top-5 courses
  for that domain from the dataset's `Chosen_Course` column.
- **College Recommendation**: Will receive the full probability vector to weight
  college suggestions across multiple domains.
- **Explainable AI**: SHAP/LIME can wrap the existing model without architectural
  changes, consuming the same input and output schema.
