"""
Course name mapping from recommendation system courses to college master dataset courses.

The master dataset (college_master_dataset.xlsx) has 45 broad course categories.
The recommendation system (student_career_with_domains.xlsx) has 113 specific course variants.

This module provides a mapping from recommendation course names -> master dataset course columns.
Only exact 'Yes' values in the master dataset count as course availability.
"""

# Maps recommendation system course names -> master dataset course column names
RECOMMENDATION_TO_MASTER_COURSE = {
    # Direct matches (exact name in master dataset)
    "B.Tech Computer Science Engineering": "B.Tech Computer Science Engineering",
    "B.Tech Electronics and Communication Engineering": "B.Tech Electronics and Communication Engineering",
    "B.Tech Mechanical Engineering": "B.Tech Mechanical Engineering",
    "B.Tech Civil Engineering": "B.Tech Civil Engineering",
    "B.Tech Electrical Engineering": "B.Tech Electrical Engineering",
    "B.Tech Chemical Engineering": "B.Tech Chemical Engineering",
    "B.Tech Aerospace Engineering": "B.Tech Aerospace Engineering",
    "B.Tech Agricultural Engineering": "B.Tech Agricultural Engineering",
    "B.Tech Artificial Intelligence and Machine Learning": "B.Tech Artificial Intelligence and Machine Learning",
    "B.Tech Data Science": "B.Tech Data Science",
    "B.Tech Information Technology": "B.Tech Information Technology",
    "B.Tech Information and Communication Technology": "B.Tech Information and Communication Technology",
    "B.Tech Computer Science and Design": "B.Tech Computer Science and Design",
    "BCA": "BCA",
    "BBA": "BBA",
    "BBA LLB": "BBA LLB",
    "BA LLB": "BA LLB",
    "MBBS": "MBBS",
    "B.Pharm": "B.Pharm",
    "Pharm.D": "Pharm.D",
    "B.Sc Nursing": "B.Sc Nursing",
    "B.Sc Biotechnology": "B.Sc Biotechnology",
    "B.Sc Chemistry": "B.Sc Chemistry",
    "B.Sc Physics": "B.Sc Physics",
    "B.Sc Mathematics": "B.Sc Mathematics",
    "B.Sc Microbiology": "B.Sc Microbiology",
    "B.Sc Agriculture": "B.Sc Agriculture",
    "B.Sc Food Technology": "B.Sc Food Technology",
    "B.Sc Forestry": "B.Sc Forestry",
    "B.Sc Horticulture": "B.Sc Horticulture",
    "BBA LLB": "BBA LLB",
    "Integrated M.Sc / BS-MS": "Integrated M.Sc / BS-MS",
    "BA LLB": "BA LLB",
    "BA English": "BA English",
    "BA Kannada": "BA Kannada",
    "BA Hindi": "BA Hindi",
    "BA Economics": "BA Economics",
    "BA History": "BA History",
    "BA Political Science": "BA Political Science",
    "BA Sociology": "BA Sociology",
    "BA Psychology": "BA Psychology",
    "BA Geography": "BA Geography",
    "BA Journalism and Mass Communication": "BA Journalism and Mass Communication",
    "BSW": "BSW",
    "B.Com": "B.Com",
    "B.Des": "B.Des",

    # Variants mapping to master dataset courses
    # B.Com variants
    "B.Com (Hons.)": "B.Com",
    "B.Com Accounting and Finance": "B.Com",
    "B.Com Banking and Insurance": "B.Com",
    "B.Com Business Analytics": "B.Com",
    "B.Com Financial Technology": "B.Com",
    "B.Com International Business": "B.Com",
    "B.Com LLB": "B.Com",
    "B.Com Taxation": "B.Com",
    "Bachelor of Accounting and Finance": "B.Com",
    "Bachelor of Financial Markets": "B.Com",
    "CA (Foundation Route)": "B.Com",
    "CMA (Foundation Route)": "B.Com",
    "Company Secretary (CSEET Route)": "B.Com",
    "Bachelor of Event Management": "BBA",
    "Bachelor of Hotel Management": "BBA",
    "Bachelor of Tourism and Travel Management": "BBA",

    # B.Des variants
    "B.Des Fashion Communication": "B.Des",
    "B.Des Product Design": "B.Des",
    "B.Des UX and Interaction Design": "B.Des",

    # B.Sc variants
    "B.Sc Actuarial Science": "B.Sc Mathematics",
    "B.Sc Astronomy and Astrophysics": "B.Sc Physics",
    "B.Sc Biochemistry": "B.Sc Biotechnology",
    "B.Sc Bioinformatics": "B.Sc Biotechnology",
    "B.Sc Biomedical Science": "B.Sc Biotechnology",
    "B.Sc Cardiac Care Technology": "B.Sc Nursing",
    "B.Sc Computer Science": "BCA",
    "B.Sc Data Science": "B.Tech Data Science",
    "B.Sc Dialysis Technology": "B.Sc Nursing",
    "B.Sc Economics": "BA Economics",
    "B.Sc Electronics": "B.Tech Electronics and Communication Engineering",
    "B.Sc Emergency Medical Technology": "B.Sc Nursing",
    "B.Sc Environmental Science": "B.Sc Biotechnology",
    "B.Sc Finance": "B.Com",
    "B.Sc Fisheries Science": "B.Sc Agriculture",
    "B.Sc Forensic Science": "B.Sc Biotechnology",
    "B.Sc Genetics": "B.Sc Biotechnology",
    "B.Sc Geology": "B.Sc Chemistry",
    "B.Sc Healthcare Management": "BBA",
    "B.Sc Nutrition and Dietetics": "B.Sc Nursing",
    "B.Sc Operation Theatre Technology": "B.Sc Nursing",
    "B.Sc Optometry": "B.Sc Nursing",
    "B.Sc Psychology": "BA Psychology",
    "B.Sc Public Health": "B.Sc Nursing",
    "B.Sc Radiology and Imaging Technology": "B.Sc Nursing",
    "B.Sc Statistics": "B.Sc Mathematics",
    "B.Sc Computer Science": "BCA",
    "B.Sc Artificial Intelligence": "B.Tech Artificial Intelligence and Machine Learning",
    "B.Sc Computational Biology": "B.Sc Biotechnology",

    # B.Tech variants
    "B.Tech Automobile Engineering": "B.Tech Mechanical Engineering",
    "B.Tech Biomedical Engineering": "B.Tech Biotechnology",
    "B.Tech Biotechnology": "B.Tech Biotechnology",
    "B.Tech Cloud Computing": "B.Tech Computer Science Engineering",
    "B.Tech Computer Science and Business Systems": "B.Tech Computer Science Engineering",
    "B.Tech Cybersecurity": "B.Tech Computer Science Engineering",
    "B.Tech Electrical and Electronics Engineering": "B.Tech Electrical Engineering",
    "B.Tech Electronics and VLSI Design": "B.Tech Electronics and Communication Engineering",
    "B.Tech Environmental Engineering": "B.Tech Civil Engineering",
    "B.Tech Food Technology": "B.Sc Food Technology",
    "B.Tech Industrial and Production Engineering": "B.Tech Mechanical Engineering",
    "B.Tech Internet of Things": "B.Tech Information Technology",
    "B.Tech Materials Engineering": "B.Tech Chemical Engineering",
    "B.Tech Mechatronics": "B.Tech Mechanical Engineering",
    "B.Tech Robotics and Automation": "B.Tech Mechanical Engineering",

    # BBA variants
    "BBA Aviation Management": "BBA",
    "BBA Business Analytics": "BBA",
    "BBA Digital Marketing": "BBA",
    "BBA Entrepreneurship": "BBA",
    "BBA Financial Technology": "BBA",
    "BBA Logistics and Supply Chain Management": "BBA",

    # BCA variants
    "BCA Artificial Intelligence": "BCA",
    "BCA Cloud Computing": "BCA",
    "BCA Cybersecurity": "BCA",
    "BCA Data Science and Analytics": "BCA",

    # Medical variants
    "BAMS": "MBBS",
    "BASLP (Audiology and Speech-Language Pathology)": "B.Sc Nursing",
    "BDS": "MBBS",
    "BHMS": "MBBS",
    "BUMS": "MBBS",
    "BOT (Occupational Therapy)": "B.Sc Nursing",
    "BPT (Physiotherapy)": "B.Sc Nursing",
    "D.Pharm": "B.Pharm",
    "General Nursing and Midwifery (GNM)": "B.Sc Nursing",

    # Other bachelor's
    "Bachelor of Event Management": "BBA",
    "Bachelor of Financial Markets": "B.Com",
    "Bachelor of Hotel Management": "BBA",
    "Bachelor of Journalism and Mass Communication": "BA Journalism and Mass Communication",
    "Bachelor of Tourism and Travel Management": "BBA",
    "BMS": "BBA",

    # Professional courses (map to closest)
    "D.Pharm": "B.Pharm",
}

# Master dataset course columns (for reference/validation)
MASTER_DATASET_COURSES = [
    "B.Com", "B.Des", "B.Pharm", "B.Sc Agriculture", "B.Sc Biotechnology",
    "B.Sc Chemistry", "B.Sc Food Technology", "B.Sc Forestry", "B.Sc Horticulture",
    "B.Sc Mathematics", "B.Sc Microbiology", "B.Sc Nursing", "B.Sc Physics",
    "B.Tech Aerospace Engineering", "B.Tech Agricultural Engineering",
    "B.Tech Artificial Intelligence and Machine Learning", "B.Tech Chemical Engineering",
    "B.Tech Civil Engineering", "B.Tech Computer Science Engineering",
    "B.Tech Computer Science and Design", "B.Tech Data Science",
    "B.Tech Electrical Engineering", "B.Tech Electronics and Communication Engineering",
    "B.Tech Information Technology", "B.Tech Information and Communication Technology",
    "B.Tech Mechanical Engineering", "BA LLB", "BBA", "BBA LLB", "BCA",
    "Integrated M.Sc / BS-MS", "MBBS", "Pharm.D", "BA English", "BA Kannada",
    "BA Hindi", "BA Economics", "BA History", "BA Political Science",
    "BA Sociology", "BA Psychology", "BA Geography", "BA Journalism and Mass Communication",
    "BSW"
]

# Domain -> master course mapping (for filtering by predicted domain)
DOMAIN_TO_MASTER_COURSES = {
    "Technology & Computing": [
        "B.Tech Computer Science Engineering", "B.Tech Artificial Intelligence and Machine Learning",
        "B.Tech Data Science", "B.Tech Information Technology",
        "B.Tech Computer Science and Design", "B.Tech Electronics and Communication Engineering",
        "B.Tech Information and Communication Technology", "BCA",
        "Integrated M.Sc / BS-MS"
    ],
    "Engineering": [
        "B.Tech Aerospace Engineering", "B.Tech Agricultural Engineering",
        "B.Tech Chemical Engineering", "B.Tech Civil Engineering",
        "B.Tech Electrical Engineering", "B.Tech Mechanical Engineering",
        "B.Tech Electronics and Communication Engineering",
        "B.Tech Information Technology"
    ],
    "Medical & Health Sciences": [
        "MBBS", "B.Pharm", "Pharm.D", "B.Sc Nursing",
    ],
    "Commerce & Finance": [
        "B.Com", "BBA", "BCA",
    ],
    "Business & Management": [
        "BBA", "BBA LLB",
    ],
    "Life Sciences & Biotechnology": [
        "B.Sc Biotechnology", "B.Sc Microbiology", "B.Sc Food Technology", "B.Sc Agriculture",
        "B.Sc Forestry", "B.Sc Horticulture",
    ],
    "Physical & Mathematical Sciences": [
        "B.Sc Mathematics", "B.Sc Physics", "B.Sc Chemistry",
        "Integrated M.Sc / BS-MS",
    ],
    "Design Media & Creative": [
        "B.Des", "BA Journalism and Mass Communication",
    ],
    "Law & Legal Studies": [
        "BA LLB", "BBA LLB",
    ],
    "Agriculture Environment & Food": [
        "B.Sc Agriculture", "B.Sc Forestry", "B.Sc Horticulture",
        "B.Sc Food Technology", "B.Tech Agricultural Engineering",
    ],
    "Arts Humanities & Social Sciences": [
        "BA English", "BA Kannada", "BA Hindi", "BA Economics", "BA History",
        "BA Political Science", "BA Sociology", "BA Psychology", "BA Geography",
        "BA Journalism and Mass Communication", "BSW",
    ],
}

def map_recommendation_to_master(course_name: str) -> str | None:
    """
    Map a recommendation system course name to master dataset course column.
    Returns the master dataset course column name, or None if no mapping exists.
    """
    return RECOMMENDATION_TO_MASTER_COURSE.get(course_name)


def get_master_courses_for_domain(domain: str) -> list:
    """Get master dataset course columns that belong to a predicted domain."""
    return DOMAIN_TO_MASTER_COURSES.get(domain, [])


def is_course_available_in_master(course_name: str) -> bool:
    """Check if a course name maps to a master dataset column."""
    return course_name in RECOMMENDATION_TO_MASTER_COURSE or course_name in MASTER_DATASET_COURSES