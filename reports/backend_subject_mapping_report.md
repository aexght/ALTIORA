# Backend Subject Mapping Report

## Date
2026-08-01

## Scope
Architecture improvement to the ML backend ONLY so it supports a dynamic academic form (stream + electives → ML subject combination) without breaking the already-trained model, existing API endpoints, or the previous integration tests.

No model changes, no retraining, no feature-order changes, no encoder/scaler changes.

---

## 1. Current Supported Combinations

Extracted from `encoders/saved_encoders.pkl` and `student_career_with_domains.xlsx` (86,000 rows). **The trained model supports exactly 11 subject combinations:**

| Stream | Combination | Elective subjects (beyond core) | Rows |
|---|---|---|---|
| Science | `PCM` | Mathematics | 14,072 |
| Science | `PCB` | Biology | 14,978 |
| Science | `PCMB` | Mathematics, Biology | 17,414 |
| Science | `PCMC` | Mathematics, Computer Science | 10,288 |
| Science | `PCMS` | Mathematics, Statistics | 7,189 |
| Commerce | `Commerce` | (none) | 5,052 |
| Commerce | `Commerce_CS` | Computer Science | 4,190 |
| Commerce | `Commerce_Statistics` | Statistics | 2,088 |
| Commerce | `Commerce_CS_Statistics` | Computer Science, Statistics | 1,474 |
| Commerce | `Commerce_Maths` | Mathematics | 5,774 |
| Commerce | `Commerce_Maths_CS` | Mathematics, Computer Science | 3,481 |

### Streams supported by the model
- `Science` — **5** combinations (core: Physics, Chemistry, English)
- `Commerce` — **6** combinations (core: Accountancy, Economics, Business Studies, English)

### Streams NOT supported by the model
- **`Arts` / `Humanities`** — the encoder has NO Arts stream. Any Arts request is rejected with a 400 error. Supporting it requires retraining.

### Core-subject discovery
Core subjects were identified empirically: their marks are populated in **100% of rows** for that stream.

- **Science core:** Physics, Chemistry, English
- **Commerce core:** Accountancy, Economics, Business Studies, English

> Note: The user's example "Commerce + Economics + Statistics" resolves to `Commerce_Statistics` because **Economics is a core Commerce subject** in the training data (100% populated across all 6 Commerce combinations). Economics does not appear in any combination name and cannot be a distinguishing elective.

### Recognised-but-unsupported elective subjects
`Informatics Practices`, `Information Technology`, `Physical Education`, `Fine Arts`, `Psychology`, `Home Science`, `Sociology`, `Political Science`, `History`, `Geography`, `Philosophy`, `Sanskrit`, `Hindi`.

These are recognised so the backend returns a clear error instead of guessing. Supporting them requires retraining.

---

## 2. New Mapper Architecture

### New file: `subject_combination_mapper.py`

Single source of truth for translating `stream + electives → ML combination`. The frontend never builds ML strings.

### Design (clean lookup table, not an if/else ladder)

```python
# Elective-subject set -> trained combination label (frozenset keys)
_ELECTIVE_TO_COMBO = {
    "Science": {
        frozenset({"Mathematics"}): "PCM",
        frozenset({"Biology"}): "PCB",
        frozenset({"Mathematics", "Biology"}): "PCMB",
        frozenset({"Mathematics", "Computer Science"}): "PCMC",
        frozenset({"Mathematics", "Statistics"}): "PCMS",
    },
    "Commerce": {
        frozenset(): "Commerce",
        frozenset({"Computer Science"}): "Commerce_CS",
        frozenset({"Statistics"}): "Commerce_Statistics",
        frozenset({"Computer Science", "Statistics"}): "Commerce_CS_Statistics",
        frozenset({"Mathematics"}): "Commerce_Maths",
        frozenset({"Mathematics", "Computer Science"}): "Commerce_Maths_CS",
    },
}
```

`frozenset` keys make ordering irrelevant and duplicates harmless.

### Key functions
- `resolve_combination(stream, electives) -> (combination, errors)` — dynamic form path
- `resolve_explicit_label(label) -> (combination, errors)` — backward-compat path
- `validate_stream(stream)` / `validate_electives(stream, electives)`
- `get_core_subjects(stream)` / `get_elective_options(stream)`
- `supported_combinations()` — exact trained list

### Core-subject handling
If the frontend sends core subjects in `electives` (e.g. a "select all subjects you studied" checkbox UI), they are validated as known and then **dropped** — core subjects never change the combination. Only non-core electives distinguish combinations.

---

## 3. Compatibility Notes

### Backward compatibility (TASK 6)
Priority order in `app.py::_normalize_academic`:
1. **Explicit `subjectCombination`** (if supplied) → used directly
2. **Otherwise `stream` + `electives`** → built via the mapper

All previously working payload formats still work:
- Old flat snake_case: `Class10_Percentage`, `Class12_Stream`, `Subject_Combination`
- CamelCase: `class10Percentage`, `class12Percentage`, `stream`, `subjectCombination`
- Nested `subjectMarks`
- Legacy labels: `Commerce with Maths` → `Commerce_Maths`, `Commerce without Maths` → `Commerce`

### Behaviour change (deliberate)
- Legacy `Humanities` / `Arts` is now **rejected with 400** instead of silently encoding to `-1`. This aligns with "never silently map to something else". Supporting Arts requires retraining.

---

## 4. Future Expansion Strategy

1. **Retrain the model** with the new combination label(s) added to the training data.
2. **Add entries to `_ELECTIVE_TO_COMBO`** in `subject_combination_mapper.py`.
3. **Update `SUPPORTED_STREAMS`, `TRAINED_SUBJECT_COMBINATIONS`, `SCIENCE/COMMERCE_ELECTIVE_OPTIONS`** as needed.
4. **Add any new mark columns** to `preprocessing.SUBJECT_MARKS_COLS` and retrain (also updates `_ALL_MARK_KEYS` in `app.py`).
5. No frontend changes needed — it continues sending `stream + electives`.

Because the mapping is a lookup table, adding a supported combination is a data change, not a code restructure.

---

## 5. Validation Rules

| Rule | Behaviour |
|---|---|
| Unsupported stream (e.g. Arts) | 400: `Unsupported stream 'Arts'. Trained model supports only: Science, Commerce.` |
| Impossible elective combination (no trained label) | 400: `Unsupported subject combination for trained model: ...` |
| Unsupported subject (e.g. Informatics Practices) | 400 with clear list of valid subjects |
| Unknown elective name | 400: `Unknown elective subject '...'` |
| Duplicate electives | 400: `Duplicate elective subject '...'` |
| More than 2 electives | 400: `Maximum of 2 electives supported ...` |
| Missing core subject marks | 400: `Missing or invalid marks for core subject 'Physics' ...` |
| Marks outside 0–100 | 400: `Invalid value for '...'. Marks must be numeric between 0 and 100.` |
| Missing required fields (Class10%, Stream) | 400 |
| No combination info at all | 400: explain to send `subjectCombination` OR `stream + electives` |
| Invalid JSON / missing academic / answers | 400 |
| Unknown endpoint | 404 |

All errors are returned as `{ "error": "..." }` JSON with status 400.

---

## 6. Files Modified

| File | Change |
|---|---|
| `subject_combination_mapper.py` | **New.** Lookup table, validation, legacy labels, core/elective definitions. |
| `app.py` | Imported mapper; `_normalize_academic` now resolves combination via explicit label OR `stream+electives`; core-subject & 0–100 mark validation; removed old inline `_SUBJECT_COMBO_MAP`; added `/health` alias; updated Swagger for `electives`. |
| `reports/backend_subject_mapping_report.md` | This report. |

## Files Created
- `subject_combination_mapper.py`

## Files NOT Modified (frozen)
- `predict.py`, `recommend.py`, `questionnaire.py`, `preprocessing.py`, `config.py`, `questions.json`, all `models/`, `encoders/`, `artifacts/`, and all frontend files.

---

## 7. Verification Results

### Smoke test (React proxy → Flask backend)
| Endpoint | Result |
|---|---|
| `GET http://localhost:5000/health` | 200 `{status: running, ...}` |
| `GET /api/questions` | 200 — 40 questions, `contributes` schema |
| `POST /api/predict` (dynamic: stream+electives) | 200 — valid prediction JSON |

### Integration regression (9 backward-compat tests) — ALL PASS
Old flat format, camelCase + legacy label, missing academic (400), invalid qid (400), invalid option (400), Commerce w/o Maths, mixed camel/snake, response structure, old flat Commerce_CS_Statistics.

### New dynamic-form tests — ALL PASS
- Commerce + Statistics + CS → `Commerce_CS_Statistics` → 200
- Commerce + Economics + Statistics → `Commerce_Statistics` (Economics dropped as core) → 200
- Commerce + Mathematics + CS → `Commerce_Maths_CS` → 200
- Science + Mathematics + Statistics → `PCMS` → 200
- Science + Mathematics + CS → `PCMC` → 200
- Science PCM with all-subjects selection → `PCM` → 200
- Unsupported/duplicate/impossible/Arts/invalid-mark/missing-core-mark → all 400

### 22-feature verification
All 22 features (2 categorical + 10 marks + 2 percentages + 8 traits) still reach the model in `FEATURE_COLS` order via `merge_features` → `predict_domains`.

---

## 8. Important: What Requires Retraining

The following are **NOT supported** and are reported honestly (not faked):
- **Arts / Humanities stream** (no Arts classes in encoder)
- **Informatics Practices** as an elective (no mark column)
- **Commerce + Mathematics + Statistics** (no `Commerce_Maths_Statistics` label)
- **Science + Computer Science alone** (no `PC_CS` / `PCS` label)
- **Science + Statistics alone** (no `PC_S` / `PCS` label)
- Any combination beyond 2 electives

Supporting these requires retraining the Random Forest with new combination labels.

---

**Result:** The backend now accepts the natural `{stream, electives, subjectMarks, class10Percentage, class12Percentage}` payload, resolves the ML combination internally, preserves every existing endpoint and payload format, validates strictly with informative errors, and is production-ready for the dynamic React academic form.
