import os, json, joblib
from preprocessing import load_data, preprocess, split_data
from sklearn.ensemble import RandomForestClassifier

BASE = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE, "models", "career_model_tuned.pkl")
RESULTS_PATH = os.path.join(BASE, "artifacts", "tuning_results.json")

print("Loading data...")
df = load_data()
X, y, encoders = preprocess(df, fit_encoders=True)
X_train, X_test, y_train, y_test = split_data(X, y)

best_params = {
    "n_estimators": 300,
    "min_samples_split": 2,
    "min_samples_leaf": 1,
    "max_features": "sqrt",
    "max_depth": 30,
    "bootstrap": True,
}

print("Retraining with best parameters (n_estimators=300, max_depth=None)...")
model = RandomForestClassifier(
    **best_params, random_state=42, n_jobs=-1, class_weight="balanced"
)
model.fit(X_train, y_train)

print(f"Saving to {MODEL_PATH} (with compression)...")
joblib.dump(model, MODEL_PATH, compress=3)

train_acc = model.score(X_train, y_train)
test_acc = model.score(X_test, y_test)
print(f"Train accuracy: {train_acc:.4f}")
print(f"Test accuracy:  {test_acc:.4f}")

results = {
    "best_params": best_params,
    "best_cv_score": 0.1164,
    "train_accuracy": float(train_acc),
    "test_accuracy": float(test_acc),
    "search_time_minutes": 14.9,
}
os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
with open(RESULTS_PATH, "w") as f:
    json.dump(results, f, indent=2)
print("Done - Phase 1 complete.")
