import os
import time
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV

from preprocessing import load_data, preprocess, split_data

TUNED_MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "career_model_tuned.pkl")
ORIGINAL_MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "career_model.pkl")

RANDOM_STATE = 42


def tune():
    print("=" * 60)
    print("PHASE 1: HYPERPARAMETER OPTIMIZATION")
    print("=" * 60)

    print("\nLoading data...")
    df = load_data()

    print("Preprocessing...")
    X, y, encoders = preprocess(df, fit_encoders=True)

    print("Splitting data...")
    X_train, X_test, y_train, y_test = split_data(X, y)
    print(f"  Train: {X_train.shape}, Test: {X_test.shape}")

    param_dist = {
        "n_estimators": [100, 200, 300, 400, 500],
        "max_depth": [10, 15, 20, 25, 30, None],
        "min_samples_split": [2, 5, 10],
        "min_samples_leaf": [1, 2, 4],
        "max_features": ["sqrt", "log2", None],
        "bootstrap": [True, False],
    }

    base_rf = RandomForestClassifier(
        random_state=RANDOM_STATE,
        n_jobs=1,
        class_weight="balanced",
        verbose=0,
    )

    search = RandomizedSearchCV(
        estimator=base_rf,
        param_distributions=param_dist,
        n_iter=15,
        cv=5,
        scoring="accuracy",
        n_jobs=-1,
        random_state=RANDOM_STATE,
        verbose=1,
    )

    print("\nStarting RandomizedSearchCV with 15 iterations, 5-fold CV...")
    print("  This may take significant time depending on system resources.")
    start = time.time()
    search.fit(X_train, y_train)
    elapsed = time.time() - start
    print(f"\nSearch completed in {elapsed / 60:.1f} minutes.")

    print("\n--- Best Parameters ---")
    for param, value in search.best_params_.items():
        print(f"  {param}: {value}")
    print(f"\nBest Cross-Validation Score: {search.best_score_:.4f}")

    print("\nTraining final model with best parameters on full training set...")
    best_rf = RandomForestClassifier(
        **search.best_params_,
        random_state=RANDOM_STATE,
        n_jobs=1,
        class_weight="balanced",
    )
    best_rf.fit(X_train, y_train)

    print(f"Saving tuned model to {TUNED_MODEL_PATH}...")
    joblib.dump(best_rf, TUNED_MODEL_PATH)

    test_accuracy = best_rf.score(X_test, y_test)
    print(f"\nTuned model test accuracy: {test_accuracy:.4f}")

    # Also save the best params separately for the report
    info = {
        "best_params": search.best_params_,
        "best_cv_score": float(search.best_score_),
        "test_accuracy": float(test_accuracy),
        "search_time_minutes": round(elapsed / 60, 1),
    }
    info_path = os.path.join(os.path.dirname(__file__), "artifacts", "tuning_results.json")
    import json
    with open(info_path, "w") as f:
        json.dump(info, f, indent=2)
    print(f"Tuning results saved to {info_path}")

    return best_rf, X_test, y_test, encoders, search.best_params_, search.best_score_


if __name__ == "__main__":
    tune()
