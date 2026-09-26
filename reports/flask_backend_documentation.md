# Flask Backend — Career Guidance System

## 1. Overall Architecture

```
                    ┌─────────────────────────────┐
  React Frontend    │      Flask Backend          │
  ─────────────     │      ────────────           │
                    │                             │
  GET /             │  ┌───────────────────────┐  │
  GET /questions    │  │     app.py            │  │
  POST /predict     │  │  (orchestration only) │  │
       │            │  └───────┬───────────────┘  │
       │            │          │                   │
       │            │    ┌─────┴──────┐            │
       │            │    │  config.py │            │
       │            │    └────────────┘            │
       │            │                              │
       │            │  ┌──────────────┐            │
       │            │  │questionnaire │            │
       ├────────────┼──┤ .py          │            │
       │            │  └──────┬───────┘            │
       │            │         │ compute_scores()   │
       │            │         │ merge_features()   │
       │            │         ▼                    │
       │            │  ┌──────────────┐            │
       │            │  │  predict.py  │            │
       ├────────────┼──┤              │            │
       │            │  └──────┬───────┘            │
       │            │         │ predict_domains()  │
       │            │         ▼                    │
       │            │  ┌──────────────┐            │
       │            │  │ recommend.py │            │
       │            │  │              │            │
       │            │  └──────────────┘            │
       │            │         │ recommend_from_    │
       │            │         │ prediction()       │
       │            │         ▼                    │
       │            │  ┌──────────────┐            │
       │  JSON      │  │   JSON       │            │
       │◄───────────┼──┤   Response   │            │
       │            │  └──────────────┘            │
       ▼            └─────────────────────────────┘
```

## 2. File Structure

```
career-guidance/
  app.py                        # Flask application (API layer only)
  config.py                     # Configuration settings
  requirements.txt              # Python dependencies
  questionnaire.py              # Scoring engine (no changes)
  predict.py                    # ML prediction (no changes)
  recommend.py                  # Recommendation engine (no changes)
  preprocessing.py              # Data preprocessing (no changes)
  questions.json                # Questionnaire data (no changes)
  student_career_with_domains.xlsx  # Dataset (no changes)
  models/
    domain_model.pkl
  encoders/
    saved_encoders.pkl
  artifacts/
    feature_columns.pkl
  reports/
    flask_backend_documentation.md
```

## 3. Request Lifecycle

A single `POST /predict` request follows this exact pipeline:

```
1. HTTP POST /predict
   │
2. Flask receives JSON body
   │
3. Validate request structure
   │  - Check 'academic' and 'answers' exist
   │  - Check all required academic fields present
   │  - Validate questionnaire answers
   │
4. questionnaire.compute_scores(answers)
   │  - Converts answer scores → 0-100 trait scores
   │
5. questionnaire.merge_features(academic, scores)
   │  - Combines academic marks + trait scores → 22-feature dict
   │
6. predict.predict_domains(features)
   │  - Loads model + encoders (lazy, cached)
   │  - Encodes categorical values
   │  - Runs Random Forest prediction
   │  - Returns domain probabilities, ranking, explanation
   │
7. recommend.recommend_from_prediction(pred)
   │  - Two-stage course scoring
   │  - Returns top 5 courses with reasons
   │
8. Flask assembles final JSON response
   │
9. HTTP 200 JSON response returned
```

## 4. Endpoint Descriptions

### `GET /`

**Purpose:** Health check / liveness probe.

**Response:**
```json
{
  "status": "running",
  "service": "Career Guidance Recommendation API",
  "version": "1.0"
}
```

**curl:**
```bash
curl http://localhost:5000/
```

---

### `GET /questions`

**Purpose:** Load the complete questionnaire dynamically. Used by the React frontend to render all questions.

**Response:** Array of question objects. Each contains:
- `id` — unique question number
- `section` — trait category grouping
- `trait` — internal trait name (maps to model features)
- `question` — question text
- `options` — array of `{text, score}` pairs

**curl:**
```bash
curl http://localhost:5000/questions
```

---

### `POST /predict`

**Purpose:** Main prediction endpoint. Accepts academic details and questionnaire answers, returns career prediction and course recommendations.

**Request body:**
```json
{
  "academic": {
    "Class10_Percentage": 88.5,
    "Class12_Stream": "Science",
    "Subject_Combination": "PCM",
    "Physics_Marks": 85,
    "Chemistry_Marks": 78,
    "Maths_Marks": 92,
    "Biology_Marks": 0,
    "ComputerScience_Marks": 0,
    "English_Marks": 80,
    "BusinessStudies_Marks": 0,
    "Economics_Marks": 0,
    "Accountancy_Marks": 0
  },
  "answers": {
    "1": 5,
    "2": 4,
    "3": 2
  }
}
```

**Field name mapping** (backend handles abbreviation):
| API Field | Internal Field |
|---|---|
| `Maths_Marks` | `Mathematics_Marks` |
| `ComputerScience_Marks` | `Computer_Science_Marks` |
| `BusinessStudies_Marks` | `Business_Studies_Marks` |
| All others | Same as API field |

**Response:**
```json
{
  "prediction": {
    "domain": "Technology & Computing",
    "probability": 47.49,
    "confidence": "Moderate"
  },
  "top_domains": [
    {"domain": "Technology & Computing", "probability": 47.49},
    {"domain": "Engineering", "probability": 34.0},
    {"domain": "Physical & Mathematical Sciences", "probability": 18.0}
  ],
  "recommended_courses": [
    {
      "course": "BCA",
      "domain": "Technology & Computing",
      "score": 38.5,
      "reason": [
        "High Technology & Computing domain probability",
        "One of the most common Technology & Computing courses in the historical dataset"
      ]
    }
  ],
  "prediction_explanation": [
    "Excellent Mathematics marks",
    "Strong Physics marks",
    "Strong Computer Science marks"
  ]
}
```

**curl:**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "academic": {
      "Class10_Percentage": 88.5,
      "Class12_Stream": "Science",
      "Subject_Combination": "PCM",
      "Physics_Marks": 85,
      "Chemistry_Marks": 78,
      "Maths_Marks": 92,
      "Biology_Marks": 0,
      "ComputerScience_Marks": 88,
      "English_Marks": 80,
      "BusinessStudies_Marks": 0,
      "Economics_Marks": 0,
      "Accountancy_Marks": 0
    },
    "answers": {
      "1": 5, "2": 5, "3": 4, "4": 4, "5": 3, "6": 5,
      "7": 5, "8": 4, "9": 5, "10": 2, "11": 2, "12": 2,
      "13": 2, "14": 2, "15": 2, "16": 4, "17": 4, "18": 4,
      "19": 4, "20": 4, "21": 4, "22": 5, "23": 5, "24": 5
    }
  }'
```

## 5. Error Handling

| HTTP Code | Scenario | Example Response |
|---|---|---|
| 400 | Missing required academic field | `{"error": "Missing required academic field: Maths_Marks"}` |
| 400 | Invalid answers type | `{"error": "'answers' must be a JSON object."}` |
| 400 | Missing answers or academic | `{"error": "Request must contain 'academic' and 'answers' fields."}` |
| 400 | Invalid JSON body | `{"error": "Invalid JSON in request body."}` |
| 400 | Questionnaire validation errors | `{"error": ["Missing answers for question_id(s): 12.", "..."]}` |
| 404 | Unknown endpoint | `{"error": "Endpoint not found."}` |
| 500 | Server error | `{"error": "Internal server error."}` |

All errors return JSON. The server never crashes or returns HTML.

## 6. Integration with React

**Step 1: Fetch questions**
```javascript
const response = await fetch("http://localhost:5000/questions");
const questions = await response.json();
// Render each question with its options
```

**Step 2: Collect answers**
```javascript
const answers = {};
questions.forEach(q => {
  answers[q.id] = selectedScore; // score value from chosen option
});
```

**Step 3: Submit prediction request**
```javascript
const payload = {
  academic: {
    Class10_Percentage: 88.5,
    Class12_Stream: "Science",
    Subject_Combination: "PCM",
    Physics_Marks: 85,
    Chemistry_Marks: 78,
    Maths_Marks: 92,
    Biology_Marks: 0,
    ComputerScience_Marks: 88,
    English_Marks: 80,
    BusinessStudies_Marks: 0,
    Economics_Marks: 0,
    Accountancy_Marks: 0,
  },
  answers,
};

const response = await fetch("http://localhost:5000/predict", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload),
});

const result = await response.json();
// result.prediction.domain — primary prediction
// result.top_domains — all 10 domains ranked
// result.recommended_courses — top 5 courses
// result.prediction_explanation — reasons
```

## 7. Swagger / OpenAPI

The API is self-documenting via Swagger UI:

- **URL:** `http://localhost:5000/apidocs/`
- **Format:** OpenAPI 2.0 (Swagger)
- **Library:** flasgger

Each endpoint includes a schema definition for request/response bodies, making it possible to test APIs directly from the browser during development.

## 8. Configuration

All settings are in `config.py`:

| Setting | Description |
|---|---|
| `MODEL_PATH` | Path to trained Random Forest model |
| `ENCODER_PATH` | Path to LabelEncoder pickle |
| `QUESTIONS_JSON` | Path to questions JSON file |
| `FEATURE_COLUMNS_PATH` | Path to feature columns order |
| `DEBUG` | Flask debug mode |
| `SECRET_KEY` | Flask session secret |
| `COLLEGE_JSON` | Reserved for future college data |

## 9. Running

```bash
pip install -r requirements.txt

python app.py
# Starts on http://0.0.0.0:5000
# Swagger UI: http://localhost:5000/apidocs/
```
