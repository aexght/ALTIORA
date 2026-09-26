import os

_BASE = os.path.dirname(__file__)

DEBUG = True
SECRET_KEY = "career-guidance-secret-key-change-in-production"

MODEL_PATH = os.path.join(_BASE, "models", "domain_model.pkl")
ENCODER_PATH = os.path.join(_BASE, "encoders", "saved_encoders.pkl")
QUESTIONS_JSON = os.path.join(_BASE, "questions.json")
FEATURE_COLUMNS_PATH = os.path.join(_BASE, "artifacts", "feature_columns.pkl")
COLLEGE_JSON = None
