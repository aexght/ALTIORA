import os, time, json, joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV

from preprocessing import load_data, preprocess, split_data

TUNED_MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "career_model_tuned.pkl")
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "artifacts", "tuning_results.json")
RANDOM_STATE = 42

print("=" * 60)
print("PHASE 1: HYPERPARAMETER OPTIMIZATION")
print("=" * 60)

print("\nLoading and preprocessing data...")
df = load_data()
X, y, encoders = preprocess(df, fit_encoders=True)
X_train, X_test, y_train, y_test = split_data(X, y)
print(f"Train: {X_train.shape}, Test: {X_test.shape}")

param_dist = {
    "n_estimators": [100, 200, 300, 400],
    "max_depth": [15, 20, 25, 30, None],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4],
    "max_features": ["sqrt", "log2"],
    "bootstrap": [True, False],
}

base_rf = RandomForestClassifier(
    random_state=RANDOM_STATE,
    n_jobs=-1,
    class_weight="balanced",
)

search = RandomizedSearchCV(
    estimator=base_rf,
    param_distributions=param_dist,
    n_iter=10,
    cv=5,
    scoring="accuracy",
    n_jobs=1,
    random_state=RANDOM_STATE,
    verbose=1,
)

print("\nStarting RandomizedSearchCV (10 iterations, 5-fold CV, sequential)...")
print("  (n_jobs=1 for search to avoid memory issues; RF uses all cores internally)")
start = time.time()
search.fit(X_train, y_train)
elapsed = time.time() - start
print(f"\nSearch completed in {elapsed/60:.1f} minutes.")

print("\n--- BEST PARAMETERS ---")
for p, v in search.best_params_.items():
    print(f"  {p}: {v}")
print(f"\nBest CV Score: {search.best_score_:.4f}")

print("\nRetraining on full training set with best parameters...")
best_rf = RandomForestClassifier(
    **search.best_params_,
    random_state=RANDOM_STATE,
    n_jobs=-1,
    class_weight="balanced",
)
best_rf.fit(X_train, y_train)

print(f"Saving tuned model to {TUNED_MODEL_PATH}...")
joblib.dump(best_rf, TUNED_MODEL_PATH)

train_acc = best_rf.score(X_train, y_train)
test_acc = best_rf.score(X_test, y_test)
print(f"Train accuracy: {train_acc:.4f}")
print(f"Test accuracy:  {test_acc:.4f}")

results = {
    "best_params": {k: v if not isinstance(v, np.integer) else int(v) for k, v in search.best_params_.items()},
    "best_cv_score": float(search.best_score_),
    "train_accuracy": float(train_acc),
    "test_accuracy": float(test_acc),
    "search_time_minutes": round(elapsed / 60, 1),
}
with open(RESULTS_PATH, "w") as f:
    json.dump(results, f, indent=2)
print(f"Results saved to {RESULTS_PATH}")
print("Phase 1 complete.")
