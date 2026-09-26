import os
import joblib
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

from preprocessing import load_data, preprocess, split_data, get_feature_names

_BASE = os.path.dirname(__file__)
MODEL_PATH = os.path.join(_BASE, "models", "career_model_tuned.pkl")
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = os.path.join(_BASE, "models", "career_model.pkl")


def evaluate():
    print("Loading data...")
    df = load_data()

    print("Preprocessing...")
    X, y, encoders = preprocess(df, fit_encoders=False)

    print("Splitting data...")
    X_train, X_test, y_train, y_test = split_data(X, y)

    print("Loading model...")
    model = joblib.load(MODEL_PATH)

    print("\n--- Evaluation on Test Set ---")
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")

    print("\n--- Classification Report ---")
    target_names = encoders["Chosen_Course"].classes_
    print(classification_report(y_test, y_pred, target_names=target_names, zero_division=0))

    print("\n--- Confusion Matrix (first 15 classes) ---")
    cm = confusion_matrix(y_test, y_pred)
    print(f"Confusion matrix shape: {cm.shape}")
    print(cm[:15, :15])

    print("\n--- Feature Importance ---")
    feature_names = get_feature_names()
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]

    print(f"{'Feature':30s} {'Importance':>10s}")
    print("-" * 42)
    for i in indices:
        print(f"{feature_names[i]:30s} {importances[i]:>10.4f}")

    return model, X_test, y_test


if __name__ == "__main__":
    evaluate()
