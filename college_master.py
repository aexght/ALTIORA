"""
College Master Dataset Integration.

Loads the authoritative college_master_dataset.xlsx and provides a clean API
for finding colleges by course and student location.

Dataset structure:
- College_Name: name of the college
- Area: city/area location
- 45 course columns with "Yes"/"No" values

Merges metadata from the legacy college_database.csv for fields like
Ownership, NAAC_Grade, NIRF_Rank, Hostel_Available, etc.

This module replaces the legacy CSV-based college recommendation system.
"""

import os
import re
from typing import Optional
import pandas as pd


_BASE = os.path.dirname(os.path.abspath(__file__))
_MASTER_DATASET_PATH = os.path.join(_BASE, "College Datasets", "college_master_dataset.xlsx")
_LEGACY_COLLEGE_DB_PATH = os.path.join(_BASE, "College Datasets", "college_database.csv")

# Area to State mapping (from area_state_mapping.py)
AREA_TO_STATE = {
    # Karnataka
    "Bengaluru": "Karnataka",
    "Mysuru": "Karnataka",
    "Mangaluru": "Karnataka",
    "Surathkal": "Karnataka",
    "Dharwad": "Karnataka",
    "Belagavi": "Karnataka",
    "Hubballi": "Karnataka",
    "Tumakuru": "Karnataka",
    "Kalaburagi": "Karnataka",
    "Nitte": "Karnataka",
    "Kattankulathur": "Tamil Nadu",  # Actually in Tamil Nadu near Chennai
    
    # Maharashtra
    "Mumbai": "Maharashtra",
    "Pune": "Maharashtra",
    "Nagpur": "Maharashtra",
    "Surat": "Gujarat",  # Surat is in Gujarat
    "Ahmedabad": "Gujarat",
    "Gandhinagar": "Gujarat",
    "Anand": "Gujarat",
    
    # Tamil Nadu
    "Chennai": "Tamil Nadu",
    "Coimbatore": "Tamil Nadu",
    "Tiruchirappalli": "Tamil Nadu",
    "Vellore": "Tamil Nadu",
    "Kozhikode": "Kerala",  # Kozhikode is in Kerala
    "Ooty": "Tamil Nadu",
    "Kottayam": "Kerala",
    "Thrissur": "Kerala",
    "Amritapuri": "Kerala",
    
    # Delhi
    "New Delhi": "Delhi",
    
    # Uttar Pradesh
    "Lucknow": "Uttar Pradesh",
    "Kanpur": "Uttar Pradesh",
    "Varanasi": "Uttar Pradesh",
    "Prayagraj": "Uttar Pradesh",
    
    # Telangana
    "Hyderabad": "Telangana",
    "Warangal": "Telangana",
    "Kandi": "Telangana",
    
    # Andhra Pradesh
    "Visakhapatnam": "Andhra Pradesh",
    "Guntur": "Andhra Pradesh",
    "Tadepalligudem": "Andhra Pradesh",
    
    # Kerala
    "Kochi": "Kerala",
    "Thiruvananthapuram": "Kerala",
    "Kottayam": "Kerala",
    
    # West Bengal
    "Kolkata": "West Bengal",
    
    # Punjab
    "Chandigarh": "Chandigarh",
    
    # Uttarakhand
    "Pantnagar": "Uttarakhand",
}

# In-memory cache
_master_df = None
_course_columns = None
_legacy_college_db = None


def _load_legacy_college_db():
    """Load and cache the legacy college database for metadata."""
    global _legacy_college_db
    if _legacy_college_db is None:
        if os.path.exists(_LEGACY_COLLEGE_DB_PATH):
            _legacy_college_db = pd.read_csv(_LEGACY_COLLEGE_DB_PATH)
        else:
            _legacy_college_db = pd.DataFrame()
    return _legacy_college_db


def _load_master_dataset():
    """Load and cache the master dataset, merged with legacy metadata."""
    global _master_df, _course_columns
    if _master_df is None:
        _master_df = pd.read_excel(_MASTER_DATASET_PATH)
        
        # Merge with legacy college database metadata
        legacy_df = _load_legacy_college_db()
        if not legacy_df.empty:
            # Merge on College_Name
            metadata_cols = ["College_ID", "State", "District", "City", "College_Type", 
                           "Ownership", "Affiliated_University", "NAAC_Grade", "NIRF_Rank",
                           "AICTE_Approved", "Hostel_Available", "Official_Website", 
                           "Admission_URL", "Notes", "Source"]
            available_cols = [c for c in metadata_cols if c in legacy_df.columns]
            if available_cols:
                _master_df = _master_df.merge(
                    legacy_df[["College_Name"] + available_cols],
                    on="College_Name",
                    how="left"
                )
        
        # Course columns are all except College_Name and Area
        _course_columns = [c for c in _master_df.columns if c not in ["College_Name", "Area"]]
    return _master_df


def get_all_course_columns() -> list:
    """Get list of all course column names in the master dataset."""
    _load_master_dataset()
    return _course_columns.copy()


def _normalize_token(value) -> str:
    """Normalize string for comparison."""
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value).strip().lower())


def _is_yes(value) -> bool:
    """Check if a dataset cell value means 'Yes'."""
    if value is None:
        return False
    norm = _normalize_token(value)
    return norm == "yes"


def _get_area_state(area: str) -> str:
    """Get the state for a given area/city."""
    return AREA_TO_STATE.get(area, "")


def find_colleges_for_course(
    course_name: str,
    student_state: str = "",
    student_district: str = "",
    top_n: int = 5
) -> list:
    """
    Find colleges offering a specific course, ranked by location relevance.

    Location ranking:
    1. Same district (Area matches district)
    2. Same state (Area's state matches student's state)
    3. Other locations

    Args:
        course_name: Master dataset course column name
        student_state: Student's state (from StudentDetailsPage)
        student_district: Student's district (from StudentDetailsPage)
        top_n: Maximum number of colleges to return

    Returns:
        List of college dicts with: college_name, area, course, location_match, location_label
    """
    df = _load_master_dataset()

    if course_name not in df.columns:
        return []

    # Filter colleges that offer this course (exact "Yes")
    mask = df[course_name].apply(_is_yes)
    eligible = df[mask].copy()

    if eligible.empty:
        return []

    # Normalize location fields
    student_state_norm = _normalize_token(student_state)
    student_district_norm = _normalize_token(student_district)

    def location_rank(row):
        area = _normalize_token(row.get("Area", ""))
        area_state = _normalize_token(_get_area_state(row.get("Area", "")))
        
        # Same district: area name matches district (or district name appears in area)
        if student_district_norm and student_district_norm in area:
            return 0
        # Same state: area's state matches student's state
        if student_state_norm and area_state and student_state_norm == area_state:
            return 1
        return 2

    eligible["location_rank"] = eligible.apply(location_rank, axis=1)

    # Sort by location rank, then by college name for consistency
    eligible = eligible.sort_values(["location_rank", "College_Name"])

    results = []
    for _, row in eligible.head(top_n).iterrows():
        rank = row["location_rank"]
        area = row["Area"]
        if rank == 0:
            location_match = "district"
            location_label = f"Near {area}"
        elif rank == 1:
            location_match = "state"
            location_label = f"Within {student_state}"
        else:
            location_match = "other"
            location_label = "Other options"

        results.append({
            "college_name": row["College_Name"],
            "area": area,
            "course": course_name,
            "location_match": location_match,
            "location_label": location_label,
        })

    return results


def find_colleges_for_multiple_courses(
    course_names: list,
    student_state: str = "",
    student_district: str = "",
    per_course_limit: int = 3,
    total_limit: int = 10
) -> list:
    """
    Find colleges for multiple recommended courses.

    Args:
        course_names: List of master dataset course column names
        student_state: Student's state
        student_district: Student's district
        per_course_limit: Max colleges per course
        total_limit: Total max colleges across all courses

    Returns:
        List of college dicts, deduplicated by college name
    """
    seen = set()
    all_results = []

    for course in course_names:
        colleges = find_colleges_for_course(
            course, student_state, student_district, top_n=per_course_limit
        )
        for c in colleges:
            key = c["college_name"]
            if key not in seen:
                seen.add(key)
                all_results.append(c)

        if len(all_results) >= total_limit:
            break

    return all_results[:total_limit]


def get_college_courses(college_name: str) -> list:
    """Get all courses offered by a specific college (Yes values)."""
    df = _load_master_dataset()
    row = df[df["College_Name"] == college_name]
    if row.empty:
        return []
    row = row.iloc[0]
    courses = [c for c in _course_columns if _is_yes(row[c])]
    return courses


# For backward compatibility with existing recommendation engine
def get_colleges_by_domain_and_location(
    domain: str,
    student_state: str = "",
    student_district: str = "",
    top_n: int = 10
) -> list:
    """
    Get colleges for a predicted domain using the master dataset.

    Maps domain to relevant master courses, then finds colleges.
    """
    from course_mapping import get_master_courses_for_domain

    master_courses = get_master_courses_for_domain(domain)
    if not master_courses:
        return []

    return find_colleges_for_multiple_courses(
        master_courses, student_state, student_district,
        per_course_limit=3, total_limit=top_n
    )


if __name__ == "__main__":
    # Quick test
    print("Course columns:", get_all_course_columns())
    print()

    # Test: B.Tech Computer Science Engineering in Karnataka
    result = find_colleges_for_course(
        "B.Tech Computer Science Engineering",
        student_state="Karnataka",
        student_district="Dakshina Kannada",
        top_n=5
    )
    print("B.Tech CSE colleges in Karnataka/Dakshina Kannada:")
    for r in result:
        print(f"  {r['college_name']} | {r['area']} | {r['location_match']} | {r['location_label']}")
    
    print()
    
    # Test: B.Tech CSE in Maharashtra
    result = find_colleges_for_course(
        "B.Tech Computer Science Engineering",
        student_state="Maharashtra",
        student_district="Mumbai",
        top_n=5
    )
    print("B.Tech CSE colleges in Maharashtra/Mumbai:")
    for r in result:
        print(f"  {r['college_name']} | {r['area']} | {r['location_match']} | {r['location_label']}")