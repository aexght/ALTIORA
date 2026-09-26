"""
subject_combination_mapper.py

Single source of truth for translating a student's stream + elective subjects
into the ML subject combination label expected by the trained encoder.

The trained Random Forest model was fit on EXACTLY 11 Subject_Combination
labels (extracted from encoders/saved_encoders.pkl and the training dataset):

    Science (core: Physics, Chemistry, English):
        PCM        = + Mathematics
        PCB        = + Biology
        PCMB       = + Mathematics, Biology
        PCMC       = + Mathematics, Computer Science
        PCMS       = + Mathematics, Statistics

    Commerce (model core: Accountancy, Economics, Business Studies, English):
        Commerce                    = no electives
        Commerce_CS                 = + Computer Science
        Commerce_Statistics         = + Statistics
        Commerce_CS_Statistics      = + Computer Science, Statistics
        Commerce_Maths              = + Mathematics
        Commerce_Maths_CS           = + Mathematics, Computer Science

    NEW UI contract (current frontend):
        Science core (always required marks): Physics, Chemistry, English
        Science electives (choose 1-2): Mathematics, Biology, Computer Science, Statistics

        Commerce core (always required marks): Accountancy, Business Studies, English
        Commerce electives (choose 1-2): Economics, Statistics, Computer Science

    Economics is an INTERNAL COMPATIBILITY subject for Commerce:
        * the trained model always assumes it is present (100% of Commerce rows),
          so users may choose NOT to select it;
        * it is dropped from combination resolution (it never changes the label);
        * its marks are defaulted to 0 internally when the client omits them,
          satisfying the model without exposing the label or breaking input.

    `Mathematics` is still accepted as a Commerce elective for backward
    compatibility with earlier dynamic clients (maps to Commerce_Maths*).

This module NEVER invents combinations. Anything the trained model does not
understand is rejected. Supporting new combinations requires retraining the
model (reported explicitly instead of faking support).

The frontend must never build these ML strings. It sends human subject names
in the `electives` array; this module owns the translation.
"""

# ---------------------------------------------------------------------------
# Trained-model facts (do NOT extend without retraining)
# ---------------------------------------------------------------------------

SUPPORTED_STREAMS = ("Science", "Commerce")

TRAINED_SUBJECT_COMBINATIONS = frozenset({
    # Science (5)
    "PCM", "PCB", "PCMB", "PCMC", "PCMS",
    # Commerce (6)
    "Commerce", "Commerce_CS", "Commerce_CS_Statistics",
    "Commerce_Maths", "Commerce_Maths_CS", "Commerce_Statistics",
})

MAX_ELECTIVES = 2

# Human subject names (canonical) that the frontend may send as electives.
SCIENCE_ELECTIVE_OPTIONS = ("Mathematics", "Biology", "Computer Science", "Statistics")
# Economics is the current UI elective; Mathematics kept for backward
# compatibility with earlier dynamic clients.
COMMERCE_ELECTIVE_OPTIONS = ("Economics", "Statistics", "Computer Science", "Mathematics")

# Core (fixed) subjects per stream, derived from the training data (their
# marks are populated in 100% of rows for that stream). These are what the
# trained model always expects for the legacy (explicit label) path.
SCIENCE_CORE_SUBJECTS = ("Physics", "Chemistry", "English")
COMMERCE_CORE_SUBJECTS = ("Accountancy", "Economics", "Business Studies", "English")

# UI core subjects — the fixed subjects the new frontend always collects marks
# for. Equals the model core MINUS compatibility subjects.
SCIENCE_UI_CORE_SUBJECTS = ("Physics", "Chemistry", "English")
COMMERCE_UI_CORE_SUBJECTS = ("Accountancy", "Business Studies", "English")

# Internal compatibility subjects: the model assumes they are always present
# even though users may not select them. They never change the combination and
# their marks default to 0 internally when the client does not supply them.
SCIENCE_COMPATIBILITY_SUBJECTS = ()
COMMERCE_COMPATIBILITY_SUBJECTS = ("Economics",)

# Canonical subject -> subjectMarks key expected by the frontend.
SUBJECT_TO_MARK_KEY = {
    "Physics": "Physics_Marks",
    "Chemistry": "Chemistry_Marks",
    "Mathematics": "Mathematics_Marks",
    "Biology": "Biology_Marks",
    "Computer Science": "ComputerScience_Marks",
    "Statistics": "Statistics_Marks",
    "Accountancy": "Accountancy_Marks",
    "Economics": "Economics_Marks",
    "Business Studies": "BusinessStudies_Marks",
    "English": "English_Marks",
}

# Subjects the user may pick that the trained model does NOT have a mark
# column for. Recognised so we can return a clear error instead of guessing.
UNSUPPORTED_SUBJECTS = frozenset({
    "Informatics Practices", "Information Technology", "Physical Education",
    "Fine Arts", "Psychology", "Home Science", "Sociology", "Political Science",
    "History", "Geography", "Philosophy", "Sanskrit", "Hindi",
})

# Elective-subject set -> trained combination label.
# frozenset keys make ordering/duplicates irrelevant.
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

# Elective name aliases so the frontend can send natural variants.
_ELECTIVE_ALIASES = {
    "mathematics": "Mathematics",
    "maths": "Mathematics",
    "math": "Mathematics",
    "computer science": "Computer Science",
    "computer_science": "Computer Science",
    "computers": "Computer Science",
    "computer": "Computer Science",
    "cs": "Computer Science",
    "biology": "Biology",
    "statistics": "Statistics",
    "stats": "Statistics",
    "accounts": "Accountancy",
    "accountancy": "Accountancy",
    "economics": "Economics",
    "english": "English",
    "physics": "Physics",
    "chemistry": "Chemistry",
    "business studies": "Business Studies",
    "business_studies": "Business Studies",
    "informatics practices": None,
    "informatics practice": None,
    "ip": None,
}

# Legacy frontend labels (pre-dynamic-form) -> trained combination label.
LEGACY_LABEL_MAP = {
    "PCM": "PCM",
    "PCB": "PCB",
    "PCMB": "PCMB",
    "PCMC": "PCMC",
    "PCMS": "PCMS",
    "Commerce with Maths": "Commerce_Maths",
    "Commerce without Maths": "Commerce",
    "Commerce": "Commerce",
    "Commerce_CS": "Commerce_CS",
    "Commerce_Statistics": "Commerce_Statistics",
    "Commerce_CS_Statistics": "Commerce_CS_Statistics",
    "Commerce_Maths": "Commerce_Maths",
    "Commerce_Maths_CS": "Commerce_Maths_CS",
}

# Subjects recognised as unsupported under the dynamic form.
_UNSUPPORTED_ALIASES = {
    "informatics practices": "Informatics Practices",
    "informatics practice": "Informatics Practices",
    "information technology": "Information Technology",
    "physical education": "Physical Education",
    "fine arts": "Fine Arts",
    "psychology": "Psychology",
    "home science": "Home Science",
    "sociology": "Sociology",
    "political science": "Political Science",
    "history": "History",
    "geography": "Geography",
    "philosophy": "Philosophy",
    "sanskrit": "Sanskrit",
    "hindi": "Hindi",
}


def _normalize_elective(elective):
    """Return canonical elective name, 'unsupported', or None if unknown."""
    if not isinstance(elective, str):
        return None
    key = elective.strip().lower()
    if key in _ELECTIVE_ALIASES:
        return _ELECTIVE_ALIASES[key] if _ELECTIVE_ALIASES[key] else "unsupported"
    if key in _UNSUPPORTED_ALIASES:
        return "unsupported"
    return None


def validate_stream(stream):
    if not isinstance(stream, str):
        return False
    return stream.strip() == "Science" or stream.strip() == "Commerce"


def get_core_subjects(stream):
    stream = stream.strip()
    if stream == "Science":
        return list(SCIENCE_CORE_SUBJECTS)
    if stream == "Commerce":
        return list(COMMERCE_CORE_SUBJECTS)
    return []


def get_elective_options(stream):
    stream = stream.strip()
    if stream == "Science":
        return list(SCIENCE_ELECTIVE_OPTIONS)
    if stream == "Commerce":
        return list(COMMERCE_ELECTIVE_OPTIONS)
    return []


def get_ui_core_subjects(stream):
    """Core subjects the new frontend always collects marks for."""
    stream = stream.strip()
    if stream == "Science":
        return list(SCIENCE_UI_CORE_SUBJECTS)
    if stream == "Commerce":
        return list(COMMERCE_UI_CORE_SUBJECTS)
    return []


def get_compatibility_subjects(stream):
    """Subjects the model assumes present but users may omit."""
    stream = stream.strip()
    if stream == "Commerce":
        return list(COMMERCE_COMPATIBILITY_SUBJECTS)
    return []


def expected_marks_subjects(stream, electives):
    """
    Dynamically generate the list of subjects for which marks are required
    (no hardcoded combination tables).

    = stream UI core subjects + every selected elective that is NOT an
      internal compatibility subject. Compatibility subjects (e.g. Economics
      for Commerce) are defaulted to 0 internally, so they are never required.

    Example: Commerce + ["Statistics"]
        -> [Accountancy, Business Studies, English, Statistics]
    """
    stream = stream.strip()
    subjects = list(get_ui_core_subjects(stream))
    compat = set(get_compatibility_subjects(stream))
    if not isinstance(electives, (list, tuple)):
        return subjects
    for e in electives:
        canonical = _normalize_elective(e)
        if canonical is None or canonical == "unsupported":
            continue
        if canonical in compat or canonical in subjects:
            continue
        subjects.append(canonical)
    return subjects


def validate_electives(stream, electives):
    """
    Validate the electives array for a stream.

    Rules:
      * stream must be supported;
      * 'electives' must be an array containing exactly 1 or 2 subject names;
      * no duplicates (alias/case-insensitive), including core subjects;
      * every name must be recognised;
      * core/compatibility subjects are validated as known and then DROPPED,
        since they never change the combination.

    Returns (normalized_elective_set, errors).
    normalized_elective_set is None when errors are present.
    """
    errors = []

    if not validate_stream(stream):
        return None, [
            "Unsupported stream '{}'. Trained model supports only: {}.".format(
                stream, ", ".join(SUPPORTED_STREAMS)
            )
        ]

    if not isinstance(electives, (list, tuple)):
        return None, ["'electives' must be an array of subject names."]

    if len(electives) < 1:
        return None, [
            "'electives' must contain between 1 and {} subjects for {} stream.".format(
                MAX_ELECTIVES, stream
            )
        ]

    if len(electives) > MAX_ELECTIVES:
        return None, [
            "Maximum of {} electives supported by the trained model; "
            "received {}.".format(MAX_ELECTIVES, len(electives))
        ]

    elective_options = set(get_elective_options(stream))
    core_subjects = set(get_core_subjects(stream))

    submitted = set()
    seen = set()
    for e in electives:
        canonical = _normalize_elective(e)

        if canonical is None:
            errors.append("Unknown elective subject '{}'.".format(e))
            continue

        if canonical == "unsupported":
            errors.append(
                "Subject '{}' is not supported by the trained model. "
                "For {} stream, valid subjects: {}.".format(
                    e, stream, ", ".join(sorted(elective_options | core_subjects))
                )
            )
            continue

        if canonical in submitted:
            errors.append("Duplicate elective subject '{}'.".format(canonical))
            continue
        submitted.add(canonical)

        if canonical in core_subjects:
            continue

        if canonical not in elective_options:
            errors.append(
                "Subject '{}' is not a valid elective for {} stream. "
                "Valid electives: {}.".format(
                    canonical, stream, ", ".join(sorted(elective_options))
                )
            )
            continue

        seen.add(canonical)

    if errors:
        return None, errors

    return frozenset(seen), []


def resolve_combination_with_electives(stream, electives):
    """
    Translate stream + electives into a trained ML subject combination.

    Returns (combination, normalized_elective_set, errors).
    combination and normalized_elective_set are None when errors are present.
    """
    elective_set, errors = validate_electives(stream, electives)
    if errors:
        return None, None, errors

    stream = stream.strip()
    combo = _ELECTIVE_TO_COMBO.get(stream, {}).get(elective_set)
    if combo is None:
        electives_desc = ", ".join(sorted(elective_set)) if elective_set else "(none)"
        return None, elective_set, [
            "Unsupported subject combination for trained model: {} with electives {}.".format(
                stream, electives_desc
            )
        ]

    return combo, elective_set, []


def resolve_combination(stream, electives):
    """
    Translate stream + electives into a trained ML subject combination.

    Backward-compatible wrapper returning (combination, errors) only.
    """
    combo, _, errors = resolve_combination_with_electives(stream, electives)
    return combo, errors


def resolve_explicit_label(label):
    """
    Backward compatibility for clients that still send `subjectCombination`.

    Accepts legacy frontend labels and direct encoder labels.
    Returns (combination, errors). combination is None when the label is not
    a trained combination.
    """
    if not isinstance(label, str):
        return None, ["'subjectCombination' must be a string."]

    trimmed = label.strip()
    combo = LEGACY_LABEL_MAP.get(trimmed)

    if combo is None and trimmed in TRAINED_SUBJECT_COMBINATIONS:
        combo = trimmed

    if combo is None:
        return None, [
            "Unsupported subject combination for trained model: '{}'. "
            "Trained model supports exactly: {}.".format(
                label, ", ".join(sorted(TRAINED_SUBJECT_COMBINATIONS))
            )
        ]

    return combo, []


def supported_combinations():
    """Return the exact list of combinations the trained model supports."""
    return sorted(TRAINED_SUBJECT_COMBINATIONS)


if __name__ == "__main__":
    print("=" * 60)
    print("SUBJECT COMBINATION MAPPER TEST")
    print("=" * 60)

    print("\nTrained model supports exactly {} subject combinations:".format(
        len(TRAINED_SUBJECT_COMBINATIONS)))
    for c in supported_combinations():
        print("  ", c)

    print("\n--- resolve_combination (stream + electives) ---")
    test_cases = [
        # Science (5)
        ("Science", ["Mathematics"], "PCM"),
        ("Science", ["Biology"], "PCB"),
        ("Science", ["Mathematics", "Biology"], "PCMB"),
        ("Science", ["Mathematics", "Computer Science"], "PCMC"),
        ("Science", ["Mathematics", "Statistics"], "PCMS"),
        # Commerce — current UI (Economics dropped as internal compatibility)
        ("Commerce", ["Economics"], "Commerce"),
        ("Commerce", ["Statistics"], "Commerce_Statistics"),
        ("Commerce", ["Computer Science"], "Commerce_CS"),
        ("Commerce", ["Economics", "Statistics"], "Commerce_Statistics"),
        ("Commerce", ["Economics", "Computer Science"], "Commerce_CS"),
        ("Commerce", ["Statistics", "Computer Science"], "Commerce_CS_Statistics"),
        # Commerce — backward-compatible electives (Mathematics still accepted)
        ("Commerce", ["Mathematics"], "Commerce_Maths"),
        ("Commerce", ["Mathematics", "Computer Science"], "Commerce_Maths_CS"),
    ]
    for stream, electives, expected in test_cases:
        combo, errs = resolve_combination(stream, electives)
        status = "OK" if combo == expected else "FAIL ({} -> {})".format(combo, errs)
        print("  {:10s} {:<32s} -> {}  [{}]".format(stream, str(electives), combo, status))

    print("\n--- expected_marks_subjects (dynamic required marks) ---")
    marks_cases = [
        ("Commerce", ["Statistics"]),
        ("Commerce", ["Economics", "Statistics"]),
        ("Commerce", ["Computer Science"]),
        ("Science", ["Mathematics", "Statistics"]),
        ("Science", ["Biology"]),
    ]
    for stream, electives in marks_cases:
        print("  {:10s} {:<32s} -> {}".format(stream, str(electives), expected_marks_subjects(stream, electives)))

    print("\n--- Unsupported combinations (must error) ---")
    bad_cases = [
        ("Science", ["Mathematics", "Computer Science", "Statistics"]),  # 3 electives
        ("Science", []),                                                  # 0 electives
        ("Commerce", ["Mathematics", "Statistics"]),                      # no trained combo
        ("Science", ["Computer Science"]),                                # PCS not trained
        ("Science", ["Statistics"]),                                      # PC_S not trained
        ("Science", ["Informatics Practices"]),                           # unsupported subject
        ("Arts", ["History"]),                                            # unsupported stream
        ("Commerce", ["Mathematics", "Mathematics"]),                     # duplicate
        ("Commerce", ["Economics", "Economics"]),                         # duplicate (compat/core)
        ("Science", ["UnknownSubject"]),                                  # unknown
    ]
    for stream, electives in bad_cases:
        combo, errs = resolve_combination(stream, electives)
        print("  {:10s} {:<45s} -> ERROR: {}".format(stream, str(electives), errs[0] if errs else "NONE"))

    print("\n--- resolve_explicit_label (backward compat) ---")
    legacy_cases = [
        ("PCM", "PCM"),
        ("Commerce with Maths", "Commerce_Maths"),
        ("Commerce without Maths", "Commerce"),
        ("Commerce_CS", "Commerce_CS"),
        ("Commerce_CS_Statistics", "Commerce_CS_Statistics"),
        ("Humanities", None),
        ("Arts", None),
        ("DoesNotExist", None),
    ]
    for label, expected in legacy_cases:
        combo, errs = resolve_explicit_label(label)
        if expected is None:
            status = "REJECTED" if combo is None else "FAIL"
        else:
            status = "OK" if combo == expected else "FAIL"
        print("  {:<28s} -> {:<18s} [{}]".format(label, str(combo), status))
