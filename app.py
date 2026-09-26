import os
import json
import sys

from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger, swag_from

sys.path.insert(0, os.path.dirname(__file__))

from config import (
    DEBUG, SECRET_KEY, QUESTIONS_JSON, MODEL_PATH,
    ENCODER_PATH, FEATURE_COLUMNS_PATH,
)

from questionnaire import (
    SUPPORTED_ASSESSMENT_LENGTHS,
    compute_scores,
    load_questions,
    merge_features,
    select_assessment,
)
from predict import predict_domains
from recommend import recommend_from_prediction, get_popularity_index
from recommendation_engine import recommend_colleges_from_prediction
from course_eligibility import filter_eligible_courses
from subject_combination_mapper import (
    resolve_combination_with_electives,
    resolve_explicit_label,
    validate_stream,
    get_core_subjects,
    expected_marks_subjects,
    SUBJECT_TO_MARK_KEY,
)

app = Flask(__name__)
app.config["DEBUG"] = DEBUG
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SWAGGER"] = {
    "title": "Career Guidance Recommendation API",
    "version": "1.0",
    "description": "REST API for the Career Guidance Recommendation System. "
                   "Predicts career domains from academic and aptitude data, "
                   "and recommends top courses.",
}

CORS(app)
Swagger(app)

# Preload recommendation popularity index at startup to avoid cold-start
# latency on the first /predict request (reads 8.7 MB Excel file).
try:
    get_popularity_index()
except Exception as e:
    app.logger.warning("Failed to preload popularity index: %s", e)

_ACADEMIC_KEYS = [
    "Class10_Percentage", "Class12_Stream", "Subject_Combination",
    "Physics_Marks", "Chemistry_Marks",
    "Biology_Marks", "English_Marks",
    "Maths_Marks", "ComputerScience_Marks",
    "BusinessStudies_Marks", "Economics_Marks", "Accountancy_Marks",
    "Statistics_Marks", "Class12_Percentage",
]

_REQUIRED_ACADEMIC = [
    "Class10_Percentage", "Class12_Stream",
]

_CAMEL_TO_SNAKE = {
    "class10Percentage": "Class10_Percentage",
    "class12Percentage": "Class12_Percentage",
    "stream": "Class12_Stream",
    "subjectCombination": "Subject_Combination",
}

_SNAKE_FROM_CAMEL = {v: k for k, v in _CAMEL_TO_SNAKE.items()}

# Every mark field the trained model consumes (internal names).
_ALL_MARK_KEYS = [
    "Physics_Marks", "Chemistry_Marks", "Mathematics_Marks",
    "Biology_Marks", "Computer_Science_Marks", "Statistics_Marks",
    "Accountancy_Marks", "Economics_Marks", "Business_Studies_Marks",
    "English_Marks",
]

# Marks that may arrive under a frontend key name (mapped to internal name).
_MARK_KEY_ALIASES = {
    "Maths_Marks": "Mathematics_Marks",
    "ComputerScience_Marks": "Computer_Science_Marks",
    "BusinessStudies_Marks": "Business_Studies_Marks",
}


def _is_valid_marks_value(val):
    if val is None:
        return True
    try:
        fval = float(val)
    except (ValueError, TypeError):
        return False
    return 0 <= fval <= 100


def _resolve_subject_combination(raw, stream):
    """
    Resolve the ML subject combination for a request.

    Priority:
      1. Explicit legacy `subjectCombination` / `Subject_Combination` label.
      2. `stream` + `electives` (new dynamic form).

    Returns (combination, elective_set, errors).
    elective_set is None when the legacy label path was used; otherwise it is
    the validated, normalized set of non-core electives.
    """
    explicit = raw.get("Subject_Combination")
    if explicit is None:
        explicit = raw.get("subjectCombination")

    if explicit is not None and str(explicit).strip() != "":
        combo, errors = resolve_explicit_label(explicit)
        if errors:
            return None, None, errors
        return combo, None, []

    if "electives" in raw:
        electives = raw.get("electives")
        combo, elective_set, errors = resolve_combination_with_electives(stream, electives)
        if errors:
            return None, None, errors
        return combo, elective_set, []

    return None, None, [
        "No subject combination provided. Send either 'subjectCombination' "
        "or 'stream' + 'electives'."
    ]


def _normalize_academic(raw):
    result = {}

    for key in _REQUIRED_ACADEMIC:
        val = raw.get(key)
        if val is None:
            camel_key = _SNAKE_FROM_CAMEL.get(key)
            if camel_key:
                val = raw.get(camel_key)
        if val is None:
            return {"error": "Missing required academic field: {}".format(key)}
        result[key] = val

    for key in ["Class12_Percentage"]:
        val = raw.get(key)
        if val is None:
            camel_key = _SNAKE_FROM_CAMEL.get(key)
            if camel_key:
                val = raw.get(camel_key)
        result[key] = val if val is not None else 0

    mark_values = {}
    if "subjectMarks" in raw and isinstance(raw["subjectMarks"], dict):
        for k, v in raw["subjectMarks"].items():
            internal_key = _MARK_KEY_ALIASES.get(k, k)
            mark_values[internal_key] = v

    for key in _ALL_MARK_KEYS:
        if key in mark_values:
            continue
        val = raw.get(key)
        alias = _MARK_KEY_ALIASES.get(key)
        if val is None and alias is None:
            for fk, ik in _MARK_KEY_ALIASES.items():
                if ik == key:
                    val = raw.get(fk)
                    break
        if val is not None:
            mark_values[key] = val

    for key in _ALL_MARK_KEYS:
        result[key] = mark_values.get(key, 0)

    stream = str(result.get("Class12_Stream", "")).strip()

    if not validate_stream(stream):
        return {
            "error": "Unsupported stream '{}'. Trained model supports only: Science, Commerce.".format(
                stream
            )
        }

    combo, elective_set, combo_errors = _resolve_subject_combination(raw, stream)
    if combo_errors:
        return {"error": combo_errors[0]}

    result["Subject_Combination"] = combo

    # Determine which subjects MUST have valid marks.
    if elective_set is None:
        # Legacy path (explicit subjectCombination): the model core subjects
        # are required, exactly as before.
        required_subjects = get_core_subjects(stream)
    else:
        # Dynamic path: UI core + selected electives. Internal compatibility
        # subjects (Economics for Commerce) are NOT required here — they are
        # defaulted to 0 below when the client does not supply them.
        required_subjects = expected_marks_subjects(stream, raw.get("electives") or [])

    for subject in required_subjects:
        mark_key = SUBJECT_TO_MARK_KEY.get(subject)
        if mark_key is None:
            continue
        internal_key = _MARK_KEY_ALIASES.get(mark_key, mark_key)
        if internal_key not in mark_values:
            return {
                "error": "Missing or invalid marks for required subject '{}' ({}) "
                         "for {} stream.".format(subject, mark_key, stream)
            }
        if not _is_valid_marks_value(mark_values[internal_key]):
            return {
                "error": "Invalid value for '{}'. Marks must be numeric between 0 and 100.".format(
                    internal_key
                )
            }

    for key in _ALL_MARK_KEYS:
        if not _is_valid_marks_value(result[key]):
            return {
                "error": "Invalid value for '{}'. Marks must be numeric between 0 and 100.".format(
                    key
                )
            }

    return result


def _load_questions_json():
    with open(QUESTIONS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


@app.route("/", methods=["GET"])
@app.route("/health", methods=["GET"])
@swag_from({
    "tags": ["Health"],
    "summary": "Health check",
    "description": "Returns service status and version. Also available at /health.",
    "responses": {
        200: {
            "description": "Service is running",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "service": {"type": "string"},
                    "version": {"type": "string"},
                },
            },
        }
    },
})
def health_check():
    return jsonify({
        "status": "running",
        "service": "Career Guidance Recommendation API",
        "version": "1.0",
    })


@app.route("/questions", methods=["GET"])
@swag_from({
    "tags": ["Questions"],
    "summary": "Get all questionnaire questions",
    "description": "Returns the complete questionnaire with all questions "
                   "and scoring options in the redesigned format.",
    "responses": {
        200: {
            "description": "Questionnaire loaded successfully",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "type": {"type": "string"},
                        "question": {"type": "string"},
                        "options": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "text": {"type": "string"},
                                    "contributes": {
                                        "type": "object",
                                        "additionalProperties": {"type": "integer"},
                                    },
                                },
                            },
                        },
                    },
                },
            },
        }
    },
})
def get_questions():
    try:
        questions = _load_questions_json()
        return jsonify(questions)
    except Exception as e:
        return jsonify({"error": "Failed to load questions: {}".format(str(e))}), 500


@app.route("/assessment", methods=["GET"])
@swag_from({
    "tags": ["Questions"],
    "summary": "Get a randomized, domain-balanced question selection",
    "description": "Selects `length` questions via stratified random sampling "
                   "across the 4 assessment domains. `exclude` is an optional "
                   "comma-separated list of recently used question IDs; the "
                   "selection prefers fresh questions and falls back to older "
                   "ones within a domain when necessary. The returned question "
                   "set and order are stable for the duration of one assessment.",
    "parameters": [
        {
            "name": "length",
            "in": "query",
            "type": "integer",
            "required": True,
            "enum": [10, 20, 30, 40],
            "description": "Number of questions to select",
        },
        {
            "name": "exclude",
            "in": "query",
            "type": "string",
            "required": False,
            "description": "Comma-separated question IDs to deprioritize",
        },
    ],
    "responses": {
        200: {
            "description": "Assessment selected successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "length": {"type": "integer"},
                    "questions": {
                        "type": "array",
                        "items": {"type": "object"},
                    },
                },
            },
        },
        400: {
            "description": "Invalid length or exclude list",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                },
            },
        },
    },
})
def get_assessment():
    length_raw = request.args.get("length", "40")
    exclude_raw = request.args.get("exclude", "")

    try:
        length = int(length_raw)
    except (TypeError, ValueError):
        return jsonify({
            "error": "'length' must be an integer in {}.".format(
                list(SUPPORTED_ASSESSMENT_LENGTHS)
            )
        }), 400

    if length not in SUPPORTED_ASSESSMENT_LENGTHS:
        return jsonify({
            "error": "'length' must be one of {}.".format(
                list(SUPPORTED_ASSESSMENT_LENGTHS)
            )
        }), 400

    exclude = []
    for token in exclude_raw.split(","):
        token = token.strip()
        if not token:
            continue
        try:
            exclude.append(int(token))
        except ValueError:
            return jsonify({
                "error": "Invalid exclude id '{}'.".format(token)
            }), 400

    try:
        selected = select_assessment(length, exclude=exclude)
    except Exception as e:
        return jsonify({
            "error": "Failed to build assessment: {}".format(str(e))
        }), 500

    return jsonify({"length": length, "questions": selected})


@app.route("/predict", methods=["POST"])
@swag_from({
    "tags": ["Prediction"],
    "summary": "Predict career domain and get course recommendations",
    "description": "Takes academic details and questionnaire answers, "
                   "runs the ML pipeline, and returns predicted domain, "
                   "top domains, recommended courses, ranked colleges, "
                   "and explanation.",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["academic", "answers"],
                "properties": {
                    "academic": {
                        "type": "object",
                        "description": "Academic details. Dynamic form: send stream + electives + subjectMarks. "
                                       "Backward compatible: send subjectCombination instead of electives.",
                        "properties": {
                            "Class10_Percentage": {"type": "number"},
                            "class10Percentage": {"type": "number"},
                            "Class12_Percentage": {"type": "number"},
                            "class12Percentage": {"type": "number"},
                            "Class12_Stream": {"type": "string", "enum": ["Science", "Commerce"]},
                            "stream": {"type": "string", "enum": ["Science", "Commerce"]},
                            "Subject_Combination": {"type": "string", "description": "Legacy: explicit ML combination (e.g. PCM, Commerce_CS). Takes priority over electives."},
                            "subjectCombination": {"type": "string", "description": "Legacy: explicit combination label."},
                            "electives": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Dynamic form: elective subject names, e.g. [\"Statistics\", \"Computer Science\"]. The backend maps these to the ML combination.",
                            },
                            "subjectMarks": {
                                "type": "object",
                                "description": "Nested marks object (frontend format)",
                                "properties": {
                                    "Physics_Marks": {"type": "number"},
                                    "Chemistry_Marks": {"type": "number"},
                                    "Maths_Marks": {"type": "number"},
                                    "Biology_Marks": {"type": "number"},
                                    "English_Marks": {"type": "number"},
                                    "Accountancy_Marks": {"type": "number"},
                                    "BusinessStudies_Marks": {"type": "number"},
                                    "Economics_Marks": {"type": "number"},
                                    "ComputerScience_Marks": {"type": "number"},
                                    "Statistics_Marks": {"type": "number"},
                                },
                            },
                        },
                    },
                    "answers": {
                        "type": "object",
                        "description": "Questionnaire answers mapping question_id to option_id (e.g. {\"1\": \"A\", \"2\": \"C\", ...})",
                        "additionalProperties": {"type": "string"},
                    },
                    "preferences": {
                        "type": "object",
                        "description": "Optional student preferences for college recommendations. Omit (or send empty) for defaults.",
                        "properties": {
                            "state": {"type": "string", "description": "Preferred state (e.g. Karnataka). Colleges outside it are filtered out."},
                            "district": {"type": "string", "description": "Optional preferred district. Only affects the score."},
                            "ownership": {"type": "string", "enum": ["Government", "Private", "Both"], "default": "Both"},
                            "maxFee": {"type": "number", "description": "Maximum annual fee budget."},
                            "hostel": {"type": "string", "enum": ["Required", "Not Required", "Doesn't Matter"], "default": "Doesn't Matter"},
                            "collegeType": {"type": "string", "enum": ["Autonomous", "University", "Affiliated", "Any"], "default": "Any"},
                            "placementImportance": {"type": "integer", "minimum": 1, "maximum": 5, "default": 3},
                            "travelPreference": {"type": "string", "enum": ["Nearby", "Within District", "Within State", "Anywhere"], "default": "Anywhere"},
                        },
                    },
                },
            },
        }
    ],
    "responses": {
        200: {
            "description": "Prediction completed successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "prediction": {
                        "type": "object",
                        "properties": {
                            "domain": {"type": "string"},
                            "probability": {"type": "number"},
                            "confidence": {"type": "string"},
                        },
                    },
                    "top_domains": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "domain": {"type": "string"},
                                "probability": {"type": "number"},
                            },
                        },
                    },
                    "recommended_courses": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "course": {"type": "string"},
                                "domain": {"type": "string"},
                                "score": {"type": "number"},
                                "reason": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                        },
                    },
                    "prediction_explanation": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "recommended_colleges": {
                        "type": "array",
                        "description": "Top ranked colleges for the predicted domain, matched against the student's preferences.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "college_name": {"type": "string"},
                                "match_percentage": {"type": "number"},
                                "course": {"type": "string"},
                                "reason": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "state": {"type": "string"},
                                "district": {"type": "string"},
                                "ownership": {"type": "string"},
                                "naac": {"type": "string"},
                                "nirf": {"type": "string"},
                                "fee": {"type": "string"},
                                "hostel": {"type": "string"},
                                "website": {"type": "string"},
                                "image_key": {"type": "string", "nullable": True},
                                "verification_status": {"type": "string"},
                            },
                        },
                    },
                },
            },
        },
        400: {
            "description": "Validation error",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                },
            },
        },
    },
})
def predict():
    try:
        data = request.get_json(silent=True)
    except Exception:
        return jsonify({"error": "Invalid JSON in request body."}), 400

    if not data or "academic" not in data or "answers" not in data:
        return jsonify({
            "error": "Request must contain 'academic' and 'answers' fields."
        }), 400

    academic_raw = data["academic"]
    answers = data["answers"]
    preferences = data.get("preferences")

    if not isinstance(academic_raw, dict):
        return jsonify({"error": "'academic' must be a JSON object."}), 400
    if not isinstance(answers, dict):
        return jsonify({"error": "'answers' must be a JSON object."}), 400

    academic = _normalize_academic(academic_raw)
    if isinstance(academic, dict) and "error" in academic:
        return jsonify(academic), 400

    app.logger.debug(
        "Predict: incoming payload = %s",
        json.dumps(academic_raw, sort_keys=True),
    )
    app.logger.debug(
        "Predict: resolved subject combination = %s",
        academic.get("Subject_Combination"),
    )

    scores = compute_scores(answers)
    if isinstance(scores, dict) and "errors" in scores:
        return jsonify({"error": scores["errors"]}), 400

    features = merge_features(academic, scores)
    pred = predict_domains(features)
    stream = str(academic.get("Class12_Stream", "")).strip()
    recs = recommend_from_prediction(pred)
    eligible_recs = filter_eligible_courses(stream, pred["Predicted_Domain"], recs)
    colleges = recommend_colleges_from_prediction(
        pred, recommended_courses=eligible_recs, preferences=preferences, stream=stream
    )

    app.logger.debug(
        "Predict: prediction = %s (confidence %s)",
        pred["Predicted_Domain"],
        pred["Prediction_Confidence"],
    )
    app.logger.debug(
        "Predict: prediction probability = %s",
        pred["Prediction_Probability"],
    )
    app.logger.debug(
        "Predict: %d recommended course(s), %d eligible for stream %s",
        len(recs), len(eligible_recs), stream,
    )
    app.logger.debug(
        "Predict: returned %d recommended college(s)",
        len(colleges),
    )

    structured = pred.get("Structured_Explanation", {})
    result = {
        "prediction": {
            "domain": pred["Predicted_Domain"],
            "probability": pred["Prediction_Probability"],
            "confidence": pred["Prediction_Confidence"],
        },
        "top_domains": pred["Career_Readiness_Ranking"],
        "recommended_courses": eligible_recs,
        "prediction_explanation": pred["Prediction_Explanation"],
        "recommended_colleges": colleges,
        # Structured reasoning — additive, backward-compatible
        "assessment_profile": structured.get("assessment_profile", []),
        "reasoning": {
            "summary": structured.get("reasoning_summary", ""),
            "assessment_pattern": structured.get("assessment_pattern", ""),
            "academic_pattern": structured.get("academic_pattern", ""),
            "primary_evidence": structured.get("primary_evidence", []),
            "academic_evidence": structured.get("academic_evidence", []),
        },
    }

    return jsonify(result)


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found."}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error."}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=DEBUG)
