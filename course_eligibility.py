"""
course_eligibility.py -- Stream-based course eligibility layer.

The single source of truth for "which stream may study which course" is the
dataset `College Datasets/course_eligibility.csv` (Required_Stream column),
joined to concrete courses through `College Datasets/college_course_mapping.csv`
(Eligibility_ID column).

This module is the ONLY place eligibility rules live. No other file may
scatter stream/engineering/medical if-else checks.

Resolution order for a course:
  1. By Eligibility_ID  (exact, from college_course_mapping)
  2. By exact course-name match inside course_eligibility.csv
  3. By domain unanimity (when every row in the course's domain declares the
     same required-stream set, the course inherits it)
  4. Centralized degree-family fallback (only for course names the dataset
     cannot resolve; never overrides CSV data)
  5. Permissive default (unknown course -> open to all streams, with warning)

Pipeline position:
    Student Academic Details (stream)
    -> Predicted Domain
    -> Courses In Domain
    -> filter_eligible_courses(stream, domain, courses)   <-- this module
    -> Recommended Courses (eligible only)
    -> College Recommendation Engine (recommendation_engine.py)
"""

import csv
import os
import re
import logging

logger = logging.getLogger(__name__)

_BASE = os.path.dirname(os.path.abspath(__file__))
_ELIGIBILITY_CSV = os.path.join(_BASE, "College Datasets", "course_eligibility.csv")
_COURSE_MAPPING_CSV = os.path.join(_BASE, "College Datasets", "college_course_mapping.csv")

# Streams the system understands. The trained prediction model currently
# supports Science and Commerce; Arts is supported here for future-proofing.
ALL_STREAMS = ("Science", "Commerce", "Arts")

# ---------------------------------------------------------------------------
# Normalization of the dataset's free-text Required_Stream cells.
# This parses the CSV's values into concrete stream sets. It is a parsing
# rule, NOT a duplicate course->stream mapping (the CSV stays authoritative).
# ---------------------------------------------------------------------------
_ANY_STREAM_MARKERS = ("any stream",)
_STREAM_TOKENS = (
    ("science", "Science"),
    ("commerce", "Commerce"),
    ("arts", "Arts"),
)

# ---------------------------------------------------------------------------
# Degree-family fallback (step 4 above). First matching prefix wins.
# Only reached when the dataset cannot resolve the course name. Prefixes are
# matched against the normalized name (lowercased, non-alphanumerics removed).
# ---------------------------------------------------------------------------
_FALLBACK_PREFIX_RULES = (
    # Engineering / architecture -> Science only.
    ("barch", frozenset(("Science",))),
    ("btech", frozenset(("Science",))),
    ("be", frozenset(("Science",))),
    # Medical / health -> Science only.
    ("mbbs", frozenset(("Science",))),
    ("bds", frozenset(("Science",))),
    ("bpharm", frozenset(("Science",))),
    ("pharmd", frozenset(("Science",))),
    ("bams", frozenset(("Science",))),
    ("bhms", frozenset(("Science",))),
    ("bums", frozenset(("Science",))),
    ("nursing", frozenset(("Science",))),
    ("alliedhealth", frozenset(("Science",))),
    # Science degrees -> Science only.
    ("bsc", frozenset(("Science",))),
    ("msc", frozenset(("Science",))),
    ("bsms", frozenset(("Science",))),
    # Open degrees (Commerce / Management / Arts families) -> any stream.
    ("bca", frozenset(("Science", "Commerce", "Arts"))),
    ("bcom", frozenset(("Science", "Commerce", "Arts"))),
    ("bba", frozenset(("Science", "Commerce", "Arts"))),
    ("bbm", frozenset(("Science", "Commerce", "Arts"))),
    ("bms", frozenset(("Science", "Commerce", "Arts"))),
    ("bdes", frozenset(("Science", "Commerce", "Arts"))),
    ("ba", frozenset(("Science", "Commerce", "Arts"))),
    ("llb", frozenset(("Science", "Commerce", "Arts"))),
    ("journalism", frozenset(("Science", "Commerce", "Arts"))),
    ("masscommunication", frozenset(("Science", "Commerce", "Arts"))),
    ("hotelmanagement", frozenset(("Science", "Commerce", "Arts"))),
    ("tourism", frozenset(("Science", "Commerce", "Arts"))),
)

_ALL_STREAMS_SET = frozenset(ALL_STREAMS)

# ---------------------------------------------------------------------------
# Dataset loading (cached)
# ---------------------------------------------------------------------------
_cache = None


def _read_csv(path):
    if not os.path.exists(path):
        logger.warning("course_eligibility: dataset missing: %s", path)
        return []
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as fh:
            return list(csv.DictReader(fh))
    except (OSError, csv.Error) as exc:
        logger.warning("course_eligibility: failed to read %s: %s", path, exc)
        return []


def _norm_key(value):
    """Lowercase and strip non-alphanumeric characters for matching."""
    if value is None:
        return ""
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def _build_eligibility_data():
    data = {}
    data["eligibility_rows"] = _read_csv(_ELIGIBILITY_CSV)
    data["mapping_rows"] = _read_csv(_COURSE_MAPPING_CSV)

    data["eligibility_by_id"] = {
        r.get("Eligibility_ID"): r for r in data["eligibility_rows"] if r.get("Eligibility_ID")
    }
    data["eligibility_by_name"] = {
        _norm_key(r.get("Course_Name")): r for r in data["eligibility_rows"] if r.get("Course_Name")
    }

    # Concrete course name -> Eligibility_ID (from the college mapping).
    data["mapping_name_to_id"] = {}
    for r in data["mapping_rows"]:
        name = _norm_key(r.get("Course_Name"))
        eid = r.get("Eligibility_ID")
        if name and eid and name not in data["mapping_name_to_id"]:
            data["mapping_name_to_id"][name] = eid

    # Domain -> rows (for the domain-unanimity step).
    domain_rows = {}
    for r in data["eligibility_rows"]:
        domain = _norm_key(r.get("Career_Domain"))
        if domain:
            domain_rows.setdefault(domain, []).append(r)
    data["domain_rows"] = domain_rows

    return data


def get_eligibility_data():
    """Return the cached eligibility bundle, loading it once on first call."""
    global _cache
    if _cache is None:
        _cache = _build_eligibility_data()
    return _cache


# ---------------------------------------------------------------------------
# Required_Stream cell -> allowed streams
# ---------------------------------------------------------------------------
_required_text_cache = {}


def _streams_from_required_text(text):
    """Parse a Required_Stream cell into a frozenset of allowed streams."""
    if text in _required_text_cache:
        return _required_text_cache[text]

    t = (text or "").strip().lower()
    if not t:
        streams = _ALL_STREAMS_SET  # no constraint recorded -> open
    elif any(marker in t for marker in _ANY_STREAM_MARKERS):
        streams = _ALL_STREAMS_SET
    else:
        matched = frozenset(label for token, label in _STREAM_TOKENS if token in t)
        if not matched:
            logger.warning(
                "course_eligibility: unrecognized Required_Stream cell %r; "
                "treating as open to all streams", text,
            )
            streams = _ALL_STREAMS_SET
        else:
            streams = matched

    _required_text_cache[text] = streams
    return streams


def _fallback_streams_for_name(name):
    """Degree-family fallback (step 4). Returns None when no rule matches."""
    key = _norm_key(name)
    if not key:
        return None
    for prefix, streams in _FALLBACK_PREFIX_RULES:
        if key.startswith(prefix):
            return streams
    return None


def required_streams_for_course(course_name, domain=None, eligibility_id=None):
    """Return the frozenset of streams admitted to the given course.

    Resolution order (see module docstring): Eligibility_ID -> exact name in
    course_eligibility.csv -> domain unanimity -> degree-family fallback ->
    permissive default.
    """
    data = get_eligibility_data()

    if eligibility_id:
        row = data["eligibility_by_id"].get(eligibility_id)
        if row:
            return _streams_from_required_text(row.get("Required_Stream"))

    name = _norm_key(course_name)
    if name:
        # Exact name in course_eligibility.csv.
        row = data["eligibility_by_name"].get(name)
        if row:
            return _streams_from_required_text(row.get("Required_Stream"))

        # Concrete course name -> Eligibility_ID via the college mapping.
        eid = data["mapping_name_to_id"].get(name)
        if eid:
            row = data["eligibility_by_id"].get(eid)
            if row:
                return _streams_from_required_text(row.get("Required_Stream"))

        # Domain unanimity.
        dom_key = _norm_key(domain)
        if dom_key:
            rows = data["domain_rows"].get(dom_key, [])
            if rows:
                stream_sets = {
                    _streams_from_required_text(r.get("Required_Stream"))
                    for r in rows
                }
                if len(stream_sets) == 1:
                    return next(iter(stream_sets))

        # Degree-family fallback for unresolvable names.
        fallback = _fallback_streams_for_name(course_name)
        if fallback is not None:
            return fallback

    logger.warning(
        "course_eligibility: unknown course %r (domain=%r); defaulting to "
        "open eligibility", course_name, domain,
    )
    return _ALL_STREAMS_SET


def course_allows_stream(stream, course_name=None, domain=None, eligibility_id=None):
    """True when `stream` may pursue the given course.

    When no stream is given, or the course cannot be resolved at all, the
    course is treated as eligible (never block on unknowns).
    """
    if not stream:
        return True
    stream = str(stream).strip()
    if stream not in ALL_STREAMS:
        return True  # unknown stream -> cannot determine -> keep
    allowed = required_streams_for_course(
        course_name, domain=domain, eligibility_id=eligibility_id
    )
    return stream in allowed


def filter_eligible_courses(stream, predicted_domain, candidate_courses):
    """Filter candidate courses down to those the student's stream may study.

    Args:
        stream (str): The student's Class 12 stream (Science/Commerce/Arts).
        predicted_domain (str): The predicted career domain (used as a
            fallback when a candidate entry has no domain of its own).
        candidate_courses (list): Course entries from the prediction step.
            Entries may be dicts with a "course" key (and optional "domain")
            or plain course-name strings.

    Returns:
        list: The eligible subset, preserving order. When the stream is
        unrecognized this returns the input unchanged (cannot determine
        eligibility).
    """
    stream = (stream or "").strip()
    if not candidate_courses:
        return list(candidate_courses or [])

    if stream not in ALL_STREAMS:
        logger.warning(
            "filter_eligible_courses: unknown stream %r; skipping eligibility "
            "filter", stream,
        )
        return list(candidate_courses)

    eligible = []
    for item in candidate_courses:
        if isinstance(item, dict):
            name = item.get("course")
            dom = item.get("domain") or predicted_domain
        else:
            name = item
            dom = predicted_domain
        if course_allows_stream(stream, course_name=name, domain=dom):
            eligible.append(item)

    logger.info(
        "course_eligibility: stream=%s domain=%s kept %d/%d course(s)",
        stream, predicted_domain, len(eligible), len(candidate_courses),
    )
    return eligible
