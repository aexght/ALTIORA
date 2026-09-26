import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import os

DATASET_PATH = os.path.join(os.path.dirname(__file__), "student_career_with_domains.xlsx")
ENCODERS_PATH = os.path.join(os.path.dirname(__file__), "encoders", "saved_encoders.pkl")

IGNORE_COLS = ["Student_ID", "Satisfaction_Score", "Chosen_Course"]
TARGET_COL = "Career_Domain"

CATEGORICAL_COLS = ["Class12_Stream", "Subject_Combination"]

SUBJECT_MARKS_COLS = [
    "Physics_Marks", "Chemistry_Marks", "Mathematics_Marks",
    "Biology_Marks", "Computer_Science_Marks", "Statistics_Marks",
    "Accountancy_Marks", "Economics_Marks", "Business_Studies_Marks",
    "English_Marks"
]

NUMERIC_COLS = [
    "Class10_Percentage", "Class12_Percentage",
    "Logical_Score", "Analytical_Score",
    "Technical_Interest", "Business_Interest",
    "Creativity_Score", "Communication_Score",
    "Leadership_Score", "Research_Interest"
]

FEATURE_COLS = CATEGORICAL_COLS + SUBJECT_MARKS_COLS + NUMERIC_COLS


def load_data(path=DATASET_PATH):
    df = pd.read_excel(path)
    return df


def preprocess(df, fit_encoders=True, encoders=None):
    data = df.drop(columns=IGNORE_COLS, errors="ignore")

    for col in SUBJECT_MARKS_COLS:
        data[col] = data[col].fillna(0)

    if fit_encoders:
        encoders = {}
        for col in CATEGORICAL_COLS:
            le = LabelEncoder()
            data[col] = le.fit_transform(data[col].astype(str))
            encoders[col] = le

        le_target = LabelEncoder()
        data[TARGET_COL] = le_target.fit_transform(data[TARGET_COL].astype(str))
        encoders[TARGET_COL] = le_target

        joblib.dump(encoders, ENCODERS_PATH)
    else:
        if encoders is None:
            encoders = joblib.load(ENCODERS_PATH)
        for col in CATEGORICAL_COLS:
            le = encoders[col]
            data[col] = data[col].astype(str)
            data[col] = data[col].map(lambda v: le.transform([v])[0] if v in le.classes_ else -1)
        le_target = encoders[TARGET_COL]
        data[TARGET_COL] = le_target.transform(data[TARGET_COL].astype(str))

    X = data[FEATURE_COLS].values
    y = data[TARGET_COL].values

    if fit_encoders:
        print("=" * 50)
        print("VALIDATION SUMMARY")
        print("=" * 50)
        print(f"  Dataset loaded: {os.path.basename(DATASET_PATH)}")
        print(f"  Feature count: {len(FEATURE_COLS)}")
        print(f"  Feature names: {FEATURE_COLS}")
        print(f"  Target column: {TARGET_COL}")
        print(f"  Career Domains: {len(encoders[TARGET_COL].classes_)}")
        print(f"  Domain classes: {list(encoders[TARGET_COL].classes_)}")
        print(f"  Encoder keys: {list(encoders.keys())}")
        print(f"  X shape: {X.shape}, y shape: {y.shape}")
        print(f"  Chosen_Course in X: {'Chosen_Course' in str(FEATURE_COLS)}")
        print(f"  Career_Domain is target: {TARGET_COL == 'Career_Domain'}")
        print(f"  Data leakage check: PASS (Chosen_Course excluded)")
        print("=" * 50)

    return X, y, encoders


def split_data(X, y, test_size=0.2, random_state=42):
    return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)


def get_feature_names():
    return FEATURE_COLS
