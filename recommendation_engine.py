"""
recommendation_engine.py — College recommendation engine.

Turns a successful career prediction + student preferences into ranked
college recommendations.

This module is intentionally isolated from app.py. All recommendation logic
lives here; app.py only calls `recommend_colleges_from_prediction()`.

Dataset (loaded ONCE and cached in memory):
  * college_master_dataset.xlsx     – authoritative college/course/location matrix
    Columns: College_Name, Area, 45 course columns (Yes/No)

Join key from prediction -> colleges:  predicted Career_Domain ==
mapped master dataset courses (via course_mapping.py).

Scoring: each dimension is normalized to 0-100, then combined with the
weights below (they sum to 1.0). This keeps the scores tunable by changing
weights without rewriting logic.

Missing-data policy (project-wide): never output "Unknown" to the client.
Such values are surfaced as "Not Verified"; nothing is fabricated, and
colleges with unverified records are never removed — only slightly penalized.
"""

import os
import re
import logging

from course_eligibility import course_allows_stream

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Scoring weights (sum to 1.0)
# ---------------------------------------------------------------------------
WEIGHT_COURSE_MATCH = 0.40
WEIGHT_LOCATION_MATCH = 0.20
WEIGHT_BUDGET_MATCH = 0.15
WEIGHT_OWNERSHIP_MATCH = 0.10
WEIGHT_HOSTEL_MATCH = 0.05
WEIGHT_TRAVEL_PREFERENCE = 0.05
WEIGHT_COLLEGE_TYPE = 0.05

WEIGHTS = {
    "course_match": WEIGHT_COURSE_MATCH,
    "location_match": WEIGHT_LOCATION_MATCH,
    "budget_match": WEIGHT_BUDGET_MATCH,
    "ownership_match": WEIGHT_OWNERSHIP_MATCH,
    "hostel_match": WEIGHT_HOSTEL_MATCH,
    "travel_preference": WEIGHT_TRAVEL_PREFERENCE,
    "college_type": WEIGHT_COLLEGE_TYPE,
}

DEFAULT_TOP_N = 5

# Values that indicate missing / unverified data anywhere in the datasets.
_UNVERIFIED_VALUES = {
    "", "unknown", "na", "n/a", "not verified", "not available",
    "none", "null",
}

# ---------------------------------------------------------------------------
# Dataset loading (cached after the first call)
# ---------------------------------------------------------------------------
_BASE = os.path.dirname(os.path.abspath(__file__))

_datasets = None


def _normalize_token(value):
    """Lowercase, strip, and squeeze whitespace for comparisons."""
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value).strip().lower())


def _is_verified(value):
    """True when a value is meaningful (not a missing-data marker)."""
    if value is None:
        return False
    norm = _normalize_token(value)
    return norm not in _UNVERIFIED_VALUES


def _parse_fee(value):
    """Parse a fee string to a float, or None when not numeric/verifiable.

    Handles forms like "120000", "1,20,000", "1.5 Lakh" (rejected -> None).
    """
    if not _is_verified(value):
        return None
    s = str(value).strip().replace(",", "").replace("₹", "").replace("Rs.", "").strip()
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def _parse_rank(value):
    """Parse NIRF rank to an int for ordering; None when not a plain number."""
    if not _is_verified(value):
        return None
    s = str(value).strip()
    try:
        return int(s)
    except (ValueError, TypeError):
        return None


def _load_master_dataset():
    """Load the master dataset using the college_master module."""
    from college_master import _load_master_dataset as load_master
    load_master()  # This populates the cache in college_master module
    from college_master import _master_df, _course_columns, _is_yes, _get_area_state
    return _master_df, _course_columns, _is_yes, _get_area_state


def get_datasets():
    """Return the cached master dataset bundle, loading it once on first call."""
    global _datasets
    if _datasets is None:
        _master_df, _course_columns, _is_yes, _get_area_state = _load_master_dataset()
        # Build indexes similar to old structure for compatibility
        colleges = _master_df.to_dict("records")
        
        # Map master dataset courses to domain
        from course_mapping import DOMAIN_TO_MASTER_COURSES
        
        college_by_id = {}
        mapping_by_college = {}
        colleges_by_domain = {}
        
        for idx, row in enumerate(colleges):
            cid = f"MASTER-{idx}"
            college_by_id[cid] = row
            
            # Get courses offered by this college
            offered = []
            for course in _course_columns:
                if _is_yes(row.get(course)):
                    offered.append({
                        "College_ID": cid,
                        "Course_Name": course,
                        "Career_Domain": None,  # Will be filled from domain mapping
                    })
            mapping_by_college[cid] = offered
            
            # Map to domains
            for domain, courses in DOMAIN_TO_MASTER_COURSES.items():
                if any(_is_yes(row.get(c)) for c in courses):
                    colleges_by_domain.setdefault(domain, set()).add(cid)
        
        _datasets = {
            "master_df": _master_df,
            "course_columns": _course_columns,
            "is_yes": _is_yes,
            "get_area_state": _get_area_state,
            "colleges": colleges,
            "college_by_id": college_by_id,
            "mapping_by_college": mapping_by_college,
            "colleges_by_domain": colleges_by_domain,
        }
    return _datasets


# ---------------------------------------------------------------------------
# Preferences normalization
# ---------------------------------------------------------------------------
def normalize_preferences(preferences):
    """Accept frontend preference keys (camelCase or snake_case) and produce
    a canonical dict with safe defaults for missing values."""
    prefs = preferences if isinstance(preferences, dict) else {}

    def pick(*names):
        for name in names:
            if name in prefs and prefs[name] not in (None, ""):
                return prefs[name]
        return None

    ownership = pick("ownership")
    if ownership is not None:
        ownership = str(ownership).strip()
        if ownership.lower() not in ("government", "private", "both"):
            ownership = "Both"
    else:
        ownership = "Both"

    hostel = pick("hostel")
    if hostel is not None:
        hostel = str(hostel).strip()
        if hostel.lower() not in ("required", "not required", "doesn't matter"):
            hostel = "Doesn't Matter"
    else:
        hostel = "Doesn't Matter"

    college_type = pick("collegeType", "college_type")
    if college_type is not None:
        college_type = str(college_type).strip()
        if college_type.lower() not in ("autonomous", "university", "affiliated", "any"):
            college_type = "Any"
    else:
        college_type = "Any"

    travel = pick("travelPreference", "travel_preference")
    if travel is not None:
        travel = str(travel).strip()
        if travel.lower() not in (
            "nearby", "within district", "within state", "anywhere"
        ):
            travel = "Anywhere"
    else:
        travel = "Anywhere"

    max_fee = pick("maxFee", "max_fee", "budget")
    if max_fee is not None:
        try:
            max_fee = float(str(max_fee).replace(",", "").strip())
        except (ValueError, TypeError):
            max_fee = None
    if max_fee is not None and max_fee <= 0:
        max_fee = None

    placement = pick("placementImportance", "placement_importance")
    try:
        placement = int(float(placement)) if placement is not None else 3
    except (ValueError, TypeError):
        placement = 3

    return {
        "state": (str(pick("state") or "")).strip(),
        "district": (str(pick("district") or "")).strip(),
        "ownership": ownership,
        "hostel": hostel,
        "collegeType": college_type,
        "travelPreference": travel,
        "maxFee": max_fee,
        "placementImportance": placement,
    }


# ---------------------------------------------------------------------------
# College type classification (Autonomous / University / Affiliated)
# ---------------------------------------------------------------------------
def classify_college_type(college):
    """Derive the college type category from the Affiliated_University column.

    The college_database has no explicit Autonomous/University/Affiliated
    field; the institution type is encoded in `Affiliated_University`:
      - any mention of "Autonomous"            -> Autonomous
      - college name itself contains University -> University
      - otherwise                              -> Affiliated
    """
    au = _normalize_token(college.get("Affiliated_University"))
    name = _normalize_token(college.get("College_Name"))

    if "autonomous" in au:
        return "Autonomous"
    if "university" in name or au in (
        "university of delhi", "university of madras", "university of mumbai",
        "anna university", "osmania university", "andhra university",
        "banaras hindu university", "gujarat university",
    ):
        return "University"
    return "Affiliated"


# ---------------------------------------------------------------------------
# Per-dimension scoring (each returns a float in 0-100)
# ---------------------------------------------------------------------------
def score_course_match(offered_rows, recommended_courses):
    """Course Match (0-100).

    A college is only ever scored here after passing the hard domain filter,
    so every scored college already offers the predicted domain. The score
    is boosted when one of its offered course names matches a recommended
    course name (normalized comparison).
    """
    if not offered_rows:
        return 0.0

    offered_names = [_normalize_token(r.get("Course_Name")) for r in offered_rows]
    offered_names = [n for n in offered_names if n]

    if not offered_names:
        return 50.0

    recommended = []
    if recommended_courses:
        for rec in recommended_courses:
            if isinstance(rec, dict) and rec.get("course"):
                recommended.append(_normalize_token(rec.get("course")))
            elif isinstance(rec, str):
                recommended.append(_normalize_token(rec))

    if not recommended:
        return 80.0  # offers the domain; no specific recommended course to match

    for offered in offered_names:
        for rec in recommended:
            if offered == rec or (len(rec) >= 8 and (rec in offered or offered in rec)):
                return 100.0
    return 80.0


def score_location_match(college, prefs):
    """Location Match (0-100). State match is enforced as a hard filter before
    scoring; here we refine by district (district is optional and only ever
    reduces the score, never removes the college)."""
    college_state = _normalize_token(college.get("State"))
    college_district = _normalize_token(college.get("District"))
    pref_state = _normalize_token(prefs["state"])
    pref_district = _normalize_token(prefs["district"])

    if not pref_state:
        return 100.0  # no location constraint

    if college_state != pref_state:
        return 0.0  # should not occur after hard filtering

    if not pref_district:
        return 100.0

    if pref_district == college_district:
        return 100.0
    if pref_district and college_district and (
        pref_district in college_district or college_district in pref_district
    ):
        return 90.0
    return 70.0  # same state, different district -> reduce, keep


def score_budget_match(fee_amount, prefs):
    """Budget Match (0-100).

    - fee known & within budget          -> 100
    - fee known & over budget            -> lower score (kept, not removed)
    - fee not verified                   -> slight penalty (kept)
    - no budget preference               -> neutral 100
    """
    max_fee = prefs.get("maxFee")
    if max_fee is None:
        return 100.0

    if fee_amount is None:
        return 60.0  # Not Verified -> slight penalty, keep

    if fee_amount <= max_fee:
        return 100.0
    return 25.0  # over budget -> lower score, keep


def _hostel_available(college, hostel_row):
    """Best-effort hostel availability from either dataset. Returns
    'Yes' | 'No' | 'Not Verified'."""
    # Convert pandas Series to dict if needed
    if hasattr(college, 'to_dict'):
        college = college.to_dict()
    if hostel_row is not None and hasattr(hostel_row, 'to_dict'):
        hostel_row = hostel_row.to_dict()
    
    for source in (hostel_row, college):
        if source:
            for col in ("Boys_Hostel", "Girls_Hostel", "Hostel_Available"):
                val = source.get(col)
                if _is_verified(val):
                    return "Yes" if _normalize_token(val) in ("yes", "available") else "No"
    return "Not Verified"


def score_hostel_match(college, hostel_row, prefs):
    """Hostel Match (0-100). Never removes a college."""
    pref = prefs["hostel"]
    if pref == "Doesn't Matter":
        return 100.0

    availability = _hostel_available(college, hostel_row)

    if availability == "Yes":
        return 100.0
    if availability == "No":
        # 'Required' heavily penalizes unavailability; 'Not Required' is neutral.
        return 40.0 if pref == "Required" else 100.0
    return 70.0  # Not Verified -> small penalty


def score_ownership_match(college, prefs):
    """Ownership Match (0-100). Respects Government / Private / Both.

    college_database Ownership can be: Government, Private, Deemed,
    Government-Aided. These are mapped onto the binary preference scale.
    """
    pref = prefs["ownership"]
    if pref == "Both":
        return 100.0

    ownership = _normalize_token(college.get("Ownership"))

    if pref == "Government":
        if ownership == "government":
            return 100.0
        if ownership == "government-aided":
            return 90.0
        if ownership == "deemed":
            return 50.0
        return 30.0  # private

    # pref == Private
    if ownership == "private":
        return 100.0
    if ownership == "deemed":
        return 85.0
    if ownership == "government-aided":
        return 60.0
    return 30.0  # government


def score_travel_preference(college, prefs):
    """Travel Preference (0-100). Approximates distance using only state and
    district (never fabricates GPS coordinates)."""
    pref = prefs["travelPreference"]
    if pref == "Anywhere":
        return 100.0

    pref_state = _normalize_token(prefs["state"])
    pref_district = _normalize_token(prefs["district"])
    college_state = _normalize_token(college.get("State"))
    college_district = _normalize_token(college.get("District"))

    same_state = bool(pref_state) and college_state == pref_state
    same_district = bool(pref_district) and (
        pref_district == college_district
        or (pref_district and college_district and (
            pref_district in college_district or college_district in pref_district
        ))
    )

    if pref in ("Nearby", "Within District"):
        if same_district:
            return 100.0
        if same_state:
            return 70.0
        return 40.0

    # Within State
    if same_state:
        return 100.0
    return 40.0


def score_college_type(college, prefs):
    """College Type Match (0-100). Respects Autonomous / University /
    Affiliated / Any."""
    pref = prefs["collegeType"]
    if pref == "Any":
        return 100.0
    if classify_college_type(college) == pref:
        return 100.0
    return 40.0


# ---------------------------------------------------------------------------
# Reason generation (only truthful reasons)
# ---------------------------------------------------------------------------
def _build_reasons(college, offered_rows, recommended_courses, prefs, fee_amount, hostel_available, domain):
    reasons = []

    # Course
    if recommended_courses:
        matched = False
        offered_names = [_normalize_token(r.get("Course_Name")) for r in offered_rows]
        for rec in recommended_courses:
            rec_name = rec.get("course") if isinstance(rec, dict) else rec
            rec_norm = _normalize_token(rec_name)
            for offered, raw in zip(offered_names, [r.get("Course_Name") for r in offered_rows]):
                if offered == rec_norm or (len(rec_norm) >= 8 and (rec_norm in offered or offered in rec_norm)):
                    reasons.append("Offers recommended course: {}".format(raw))
                    matched = True
                    break
            if matched:
                break
    if not any("Offers recommended course" in r for r in reasons):
        reasons.append("Offers courses in the {} domain".format(domain))

    # Location
    pref_state = _normalize_token(prefs["state"])
    college_state = college.get("State")
    college_district = college.get("District")
    if pref_state and _normalize_token(college_state) == pref_state:
        if prefs["district"] and _normalize_token(college_district) == _normalize_token(prefs["district"]):
            reasons.append("Located in {}, {}".format(college_district, college_state))
        else:
            reasons.append("Located in {}".format(college_state))

    # Budget (only claimed when the fee is actually known & within budget)
    if fee_amount is not None and prefs.get("maxFee") is not None and fee_amount <= prefs["maxFee"]:
        reasons.append("Within your budget")

    # Ownership (only when it is an actual match)
    pref_own = prefs["ownership"]
    if pref_own != "Both" and score_ownership_match(college, prefs) >= 90:
        reasons.append("Matches preferred ownership ({})".format(college.get("Ownership")))

    # Hostel
    if prefs["hostel"] == "Required":
        if hostel_available == "Yes":
            reasons.append("Hostel available")
        elif hostel_available == "No":
            reasons.append("Hostel not available")

    # College type
    ctype = classify_college_type(college)
    if prefs["collegeType"] == ctype:
        reasons.append("{} institution".format(ctype))
    if ctype == "Affiliated" and _is_verified(college.get("Affiliated_University")):
        reasons.append("Affiliated to {}".format(college.get("Affiliated_University")))

    # Travel (only when it is an actual match)
    pref_travel = prefs["travelPreference"]
    if pref_travel != "Anywhere":
        pref_state = _normalize_token(prefs["state"])
        pref_district = _normalize_token(prefs["district"])
        college_state = _normalize_token(college.get("State"))
        college_district = _normalize_token(college.get("District"))
        same_state = bool(pref_state) and college_state == pref_state
        same_district = bool(pref_district) and (
            pref_district == college_district
            or (pref_district and college_district and (
                pref_district in college_district or college_district in pref_district
            ))
        )
        if pref_travel in ("Nearby", "Within District") and same_district:
            reasons.append("Within your preferred district")
        elif same_state:
            reasons.append("Within your preferred state")

    # Rank / accreditation (only when verified)
    rank = _parse_rank(college.get("NIRF_Rank"))
    if rank is not None:
        reasons.append("NIRF rank {}".format(rank))
    naac = college.get("NAAC_Grade")
    if _is_verified(naac):
        reasons.append("NAAC accredited: {}".format(naac))

    return reasons


# ---------------------------------------------------------------------------
# Main entry points
# ---------------------------------------------------------------------------
def _verification_status(college, fee_known, hostel_available):
    """Derive an honest verification_status from how many core fields carry
    real values. This is computed from the data, never fabricated."""
    verified_fields = 0
    if _parse_rank(college.get("NIRF_Rank")) is not None:
        verified_fields += 1
    if _is_verified(college.get("NAAC_Grade")):
        verified_fields += 1
    if fee_known:
        verified_fields += 1
    if hostel_available != "Not Verified":
        verified_fields += 1
    if verified_fields >= 4:
        return "Verified"
    if verified_fields >= 2:
        return "Partially Verified"
    return "Not Verified"


def _best_course_name(offered_rows, recommended_courses):
    """Pick the most relevant offered course name for display."""
    if not offered_rows:
        return "Not Verified"
    if recommended_courses:
        for rec in recommended_courses:
            rec_name = rec.get("course") if isinstance(rec, dict) else rec
            rec_norm = _normalize_token(rec_name)
            for row in offered_rows:
                if _normalize_token(row.get("Course_Name")) == rec_norm:
                    return row["Course_Name"]
        for rec in recommended_courses:
            rec_name = rec.get("course") if isinstance(rec, dict) else rec
            rec_norm = _normalize_token(rec_name)
            if not rec_norm:
                continue
            for row in offered_rows:
                offered = _normalize_token(row.get("Course_Name"))
                if len(rec_norm) >= 8 and (rec_norm in offered or offered in rec_norm):
                    return row["Course_Name"]
    return offered_rows[0]["Course_Name"]


def _score_college(cid, domain, recommended_courses, prefs, datasets, offered_rows=None):
    college = datasets["college_by_id"].get(cid)
    if not college:
        return None
    if offered_rows is None:
        offered_rows = datasets["mapping_by_college"].get(cid, [])

    # Fee for the best course of this college in the domain.
    fee_row = None
    for row in offered_rows:
        key = (cid, row.get("Course_Name"))
        if row.get("Career_Domain") == domain and key in datasets["fee_by_key"]:
            fee_row = datasets["fee_by_key"][key]
            break
    if fee_row is None and offered_rows:
        key = (cid, offered_rows[0].get("Course_Name"))
        fee_row = datasets["fee_by_key"].get(key)
    fee_amount = _parse_fee(fee_row.get("Annual_Fee") if fee_row else None)

    hostel_row = datasets["hostel_by_college"].get(cid, {})
    hostel_available = _hostel_available(college, hostel_row)

    # Normalized 0-100 dimension scores.
    course_score = score_course_match(offered_rows, recommended_courses)
    location_score = score_location_match(college, prefs)
    budget_score = score_budget_match(fee_amount, prefs)
    ownership_score = score_ownership_match(college, prefs)
    hostel_score = score_hostel_match(college, hostel_row, prefs)
    travel_score = score_travel_preference(college, prefs)
    college_type_score = score_college_type(college, prefs)

    components = {
        "course_match": course_score,
        "location_match": location_score,
        "budget_match": budget_score,
        "ownership_match": ownership_score,
        "hostel_match": hostel_score,
        "travel_preference": travel_score,
        "college_type": college_type_score,
    }
    total = sum(components[key] * WEIGHTS[key] for key in WEIGHTS)

    return {
        "college": college,
        "components": components,
        "total": total,
        "fee_amount": fee_amount,
        "hostel_available": hostel_available,
        "best_course": _best_course_name(offered_rows, recommended_courses),
    }


def recommend_colleges(
    predicted_domain,
    recommended_courses=None,
    preferences=None,
    top_n=DEFAULT_TOP_N,
    stream=None,
):
    """Rank colleges for a predicted domain against student preferences.

    Uses the authoritative college_master_dataset.xlsx as the data source.
    Finds colleges offering the predicted domain's courses, ranked by location relevance.

    When `stream` is given, filters courses by stream eligibility via course_eligibility.py.
    With `stream=None` the eligibility filter is skipped.

    Args:
        predicted_domain (str): The predicted career domain.
        recommended_courses (list): Recommended course entries from the
            prediction step (each with a "course" key).
        preferences (dict): Student preferences (see normalize_preferences).
        top_n (int): Number of colleges to return.
        stream (str): Student's Class 12 stream (Science/Commerce/Arts).
            Optional; enables the eligibility filter.

    Returns:
        list[dict]: Top colleges sorted by match percentage (descending).
        Each item has: college_name, match_percentage, course, reason[],
        state, district, ownership, naac, nirf, fee, hostel, website,
        image_key, verification_status.
        Empty list on missing data / no matches / no eligible course. Never raises.
    """
    from college_master import (
        find_colleges_for_multiple_courses,
        _load_master_dataset,
        _course_columns,
        _is_yes,
        _get_area_state,
    )
    from course_mapping import (
        map_recommendation_to_master,
        get_master_courses_for_domain as get_courses_for_domain,
    )

    prefs = normalize_preferences(preferences)

    domain = (predicted_domain or "").strip()
    if not domain:
        logger.warning("recommendation_engine: no predicted domain supplied")
        return []

    # Get master dataset courses for this domain
    master_courses = get_courses_for_domain(domain)
    if not master_courses:
        logger.warning(
            "recommendation_engine: no master courses mapped for domain '%s'", domain
        )
        return []

    # Map recommended courses to master dataset courses
    master_recommended_courses = set()
    if recommended_courses:
        for rec in recommended_courses:
            rec_name = rec.get("course") if isinstance(rec, dict) else rec
            master_course = map_recommendation_to_master(rec_name)
            if master_course and master_course in master_courses:
                master_recommended_courses.add(master_course)

    # Student location
    prefs = normalize_preferences(preferences)
    student_state = prefs.get("state", "")
    student_district = prefs.get("district", "")

    # Stream eligibility filter
    stream = (stream or "").strip()
    if stream:
        # Filter master courses by stream eligibility
        filtered_courses = []
        for course in master_courses:
            if course_allows_stream(stream, course_name=course, domain=domain):
                filtered_courses.append(course)
        if not filtered_courses:
            logger.info(
                "recommendation_engine: stream '%s' has no eligible course in "
                "domain '%s'; no colleges considered", stream, domain,
            )
            return []
        master_courses = filtered_courses

    logger.info(
        "recommendation_engine: predicted domain = %s", domain
    )
    logger.info(
        "recommendation_engine: student stream = %s", stream or "unspecified"
    )
    logger.info(
        "recommendation_engine: master courses for domain = %s", master_courses
    )
    logger.info(
        "recommendation_engine: recommended master courses = %s", list(master_recommended_courses)
    )

    # Find colleges using the master dataset
    # Use a simple location-aware search with course match scoring
    _load_master_dataset()

    # Get colleges offering the domain's courses
    df = _load_master_dataset()
    
    # Filter colleges that offer at least one of the domain's master courses
    mask = df[master_courses].apply(lambda row: any(_is_yes(row[c]) for c in master_courses), axis=1)
    eligible_df = df[mask].copy()

    if eligible_df.empty:
        logger.warning(
            "recommendation_engine: no colleges offer domain '%s' courses", domain
        )
        return []

    # Apply state filter if student has state preference
    student_state = prefs.get("state", "")
    student_district = prefs.get("district", "")
    pref_state = _normalize_token(student_state)
    pref_district = _normalize_token(student_district)

    if pref_state:
        def state_match(row):
            area_state = _get_area_state(row.get("Area", ""))
            return _normalize_token(area_state) == pref_state
        
        eligible_df = eligible_df[eligible_df.apply(state_match, axis=1)]
        if eligible_df.empty:
            logger.info(
                "recommendation_engine: no colleges in state '%s' for domain '%s'",
                student_state, domain,
            )
            return []

# Score each college
    scored = []
    for _, row in eligible_df.iterrows():
        # Course match score
        offered_courses = [c for c in master_courses if _is_yes(row.get(c))]
        
        # Course match: 100 if any recommended course matches, 80 if offers domain but no specific match
        course_score = 80.0
        if master_recommended_courses:
            for course in master_recommended_courses:
                if _is_yes(row.get(course)):
                    course_score = 100.0
                    break
        
        # Location match
        area = row.get("Area", "")
        area_state = _get_area_state(area)
        
        if pref_state and area_state and _normalize_token(area_state) == pref_state:
            if pref_district and pref_district.lower() in _normalize_token(area):
                location_score = 100.0
            else:
                location_score = 90.0
        else:
            location_score = 50.0
        
        # Ownership match (using existing scoring function)
        ownership_score = score_ownership_match(row, prefs)
        
        # Hostel match (using existing scoring function)
        hostel_score = score_hostel_match(row, None, prefs)
        
        # Budget match - neutral since no fee data in master dataset
        budget_score = 100.0
        
        # College type match - neutral since no college_type in master dataset
        college_type_score = 100.0
        
        # Travel preference - use location as proxy
        travel_score = score_travel_preference(row, prefs)
        
        # Weighted scoring using all available dimensions
        # Weights that have data: course (0.40), location (0.20), ownership (0.10), hostel (0.05)
        # Weights without data: budget (0.15), college_type (0.05), travel (0.05)
        # Use available weights only, normalize by sum of used weights
        used_weights = WEIGHT_COURSE_MATCH + WEIGHT_LOCATION_MATCH + WEIGHT_OWNERSHIP_MATCH + WEIGHT_HOSTEL_MATCH + WEIGHT_TRAVEL_PREFERENCE
        total = (
            course_score * WEIGHT_COURSE_MATCH +
            location_score * WEIGHT_LOCATION_MATCH +
            ownership_score * WEIGHT_OWNERSHIP_MATCH +
            hostel_score * WEIGHT_HOSTEL_MATCH +
            travel_score * WEIGHT_TRAVEL_PREFERENCE
        )
        
        # Normalize to 100 scale (divide by sum of weights used)
        total_pct = total / used_weights

        # Get the best course name for display
        best_course = None
        if master_recommended_courses:
            for course in master_recommended_courses:
                if _is_yes(row.get(course)):
                    best_course = course
                    break
        if not best_course and offered_courses:
            best_course = offered_courses[0]

        scored.append({
            "college": row.to_dict(),
            "total": total_pct,
            "best_course": best_course,
            "offered_courses": offered_courses,
        })

    if not scored:
        return []

    scored.sort(key=lambda x: x["total"], reverse=True)
    top = scored[:top_n]

    logger.info(
        "recommendation_engine: final top %d college(s)", len(top)
    )
    for rank, item in enumerate(top, 1):
        logger.info(
            "recommendation_engine: #%d %s (score %.2f)",
            rank, item["college"].get("College_Name"), item["total"],
        )

    # Build result in the expected format
    result = []
    for item in top:
        college = item["college"]
        offered_courses = item["offered_courses"]
        
        # Build reasons
        reasons = []
        if master_recommended_courses:
            matched = False
            for course in master_recommended_courses:
                if _is_yes(college.get(course)):
                    reasons.append(f"Offers recommended course: {course}")
                    matched = True
                    break
            if not matched:
                reasons.append(f"Offers courses in the {domain} domain")
        else:
            reasons.append(f"Offers courses in the {domain} domain")

        # Location reason
        area = college.get("Area", "")
        if pref_state and _get_area_state(area) and _normalize_token(_get_area_state(area)) == pref_state:
            if pref_district and pref_district.lower() in _normalize_token(area):
                reasons.append(f"Located in {area}, {student_state}")
            else:
                reasons.append(f"Located in {student_state}")

        # Overall alignment reason
        reasons.append(f"Match: {round(item['total'], 1)}%")

        # Location match for frontend
        if pref_state and _get_area_state(area) and _normalize_token(_get_area_state(area)) == pref_state:
            if pref_district and pref_district.lower() in _normalize_token(area):
                location_match = "district"
                location_label = f"Near {area}"
            else:
                location_match = "state"
                location_label = f"Within {student_state}"
        else:
            location_match = "other"
            location_label = "Other options"

        # Extract metadata from merged dataset
        ownership = college.get("Ownership")
        naac = college.get("NAAC_Grade")
        nirf = college.get("NIRF_Rank")
        fee = "Not Verified"  # Not in master dataset
        hostel = college.get("Hostel_Available")
        website = college.get("Official_Website")

        # Normalize "Unknown" values to "Not Verified"
        for field_name, field_val in [("ownership", ownership), ("naac", naac), ("nirf", nirf), 
                                       ("hostel", hostel), ("website", website)]:
            if field_val and str(field_val).strip().lower() in ("unknown", "not verified", "not available", "na", "n/a", "none", ""):
                if field_name == "ownership":
                    ownership = "Not Verified"
                elif field_name == "naac":
                    naac = "Not Verified"
                elif field_name == "nirf":
                    nirf = "Not Verified"
                elif field_name == "hostel":
                    hostel = "Not Verified"
                elif field_name == "website":
                    website = "Not Verified"

        result.append({
            "college_name": college.get("College_Name") or "Not Verified",
            "match_percentage": round(item["total"], 2),
            "course": item["best_course"] or "Not Verified",
            "reason": reasons,
            "state": _get_area_state(college.get("Area", "")) or college.get("State") or "Not Verified",
            "district": college.get("Area") or college.get("District") or "Not Verified",
            "ownership": ownership if ownership and str(ownership).strip() else "Not Verified",
            "naac": naac if naac and str(naac).strip() else "Not Verified",
            "nirf": nirf if nirf and str(nirf).strip() else "Not Verified",
            "fee": fee,
            "hostel": hostel if hostel and str(hostel).strip() else "Not Verified",
            "website": website if website and str(website).strip() else "Not Verified",
            "image_key": None,
            "verification_status": "Not Verified",
            "location_match": location_match,
            "location_label": location_label,
        })

    return result


def recommend_colleges_from_prediction(prediction_result, recommended_courses=None, preferences=None, top_n=DEFAULT_TOP_N, stream=None):
    """Convenience wrapper: pull the domain out of a predict_domains() result
    and delegate to recommend_colleges().

    `recommended_courses` (optional) is the list returned by
    recommend.recommend_from_prediction() (each entry has a "course" key).
    It is used to boost the course-match score and to pick the displayed
    course name for each college.

    `stream` (optional) enables the stream-eligibility filter: only colleges
    offering a course the student may study are recommended.
    """
    if not isinstance(prediction_result, dict):
        return []
    domain = prediction_result.get("Predicted_Domain")
    return recommend_colleges(domain, recommended_courses, preferences, top_n=top_n, stream=stream)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from predict import predict_domains, load_data

    df = load_data()
    sample = df.iloc[0].to_dict()
    pred = predict_domains(sample)
    print("Predicted domain:", pred["Predicted_Domain"])
    print("Preferences: default (no state/budget/etc.)")
    for c in recommend_colleges_from_prediction(pred, preferences=None):
        print("  {:.2f}% | {} | {}".format(c["match_percentage"], c["college_name"], c["course"]))
