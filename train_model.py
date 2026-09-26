import os
import joblib
from sklearn.ensemble import RandomForestClassifier

from preprocessing import load_data, preprocess, split_data

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "career_model.pkl")

RANDOM_STATE = 42
N_ESTIMATORS = 150
MAX_DEPTH = 25
N_JOBS = 2


def train():
    print("Loading data...")
    df = load_data()

    print("Preprocessing...")
    X, y, encoders = preprocess(df, fit_encoders=True)

    print("Splitting data...")
    X_train, X_test, y_train, y_test = split_data(X, y)

    print(f"Training RandomForest with {N_ESTIMATORS} trees...")
    model = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        max_depth=MAX_DEPTH,
        random_state=RANDOM_STATE,
        n_jobs=N_JOBS,
        class_weight="balanced"
    )
    model.fit(X_train, y_train)

    print("Saving model...")
    joblib.dump(model, MODEL_PATH)

    print(f"Model saved to {MODEL_PATH}")
    print(f"Train shape: {X_train.shape}, Test shape: {X_test.shape}")
    print(f"Number of classes: {len(model.classes_)}")

    return model, X_test, y_test, encoders


if __name__ == "__main__":
    train()
