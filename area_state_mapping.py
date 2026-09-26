"""
Area to State mapping for college master dataset.
Maps city names (Area field) to Indian states.
"""

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
    "Kattankulathur": "Karnataka",  # Actually Tamil Nadu? Need to check
    
    # Maharashtra
    "Mumbai": "Maharashtra",
    "Pune": "Maharashtra",
    "Nagpur": "Maharashtra",
    "Surat": "Maharashtra",
    "Ahmedabad": "Maharashtra",
    "Gandhinagar": "Maharashtra",
    
    # Tamil Nadu
    "Chennai": "Tamil Nadu",
    "Coimbatore": "Tamil Nadu",
    "Tiruchirappalli": "Tamil Nadu",
    "Vellore": "Tamil Nadu",
    "Kozhikode": "Tamil Nadu",
    "Ooty": "Tamil Nadu",
    "Kottayam": "Tamil Nadu",
    "Thrissur": "Tamil Nadu",
    
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
    "Kozhikode": "Kerala",
    "Kottayam": "Kerala",
    "Thrissur": "Kerala",
    "Ooty": "Kerala",  # Actually Tamil Nadu
    
    # Gujarat
    "Ahmedabad": "Gujarat",
    "Gandhinagar": "Gujarat",
    "Anand": "Gujarat",
    "Surat": "Gujarat",
    
    # West Bengal
    "Kolkata": "West Bengal",
    
    # Punjab
    "Chandigarh": "Punjab",
    
    # Rajasthan
    "Jaipur": "Rajasthan",
    
    # Madhya Pradesh
    "Bhopal": "Madhya Pradesh",
    "Indore": "Madhya Pradesh",
    
    # Bihar
    "Patna": "Bihar",
    
    # Odisha
    "Bhubaneswar": "Odisha",
    
    # Haryana
    "Gurugram": "Haryana",
    
    # Punjab/Haryana/Chandigarh
    "Chandigarh": "Chandigarh",
    
    # Uttarakhand
    "Pantnagar": "Uttarakhand",
    
    # Rajasthan
    "Kota": "Rajasthan",
    
    # Jammu & Kashmir
    "Srinagar": "Jammu and Kashmir",
    
    # Himachal Pradesh
    "Shimla": "Himachal Pradesh",
    
    # Jharkhand
    "Ranchi": "Jharkhand",
    
    # Chhattisgarh
    "Raipur": "Chhattisgarh",
    
    # Assam
    "Guwahati": "Assam",
    
    # Punjab
    "Ludhiana": "Punjab",
    "Amritsar": "Punjab",
    
    # Goa
    "Panaji": "Goa",
}

# Additional: Some areas need correction - Kattankulathur is in Tamil Nadu (Chennai area)
# Ooty is in Tamil Nadu (Nilgiris district)
# Amritapuri is in Kerala (Kollam district)

# State to list of districts mapping (for potential future use)
# We can use the districts.json for this

def get_state_for_area(area: str) -> str:
    """Get the state for a given area/city."""
    return AREA_TO_STATE.get(area, "")


def get_district_for_area(area: str) -> str:
    """Get the district for a given area/city (uses area as district proxy)."""
    # In many cases, the city name IS the district name or is within that district
    # For now, we'll use the area as a proxy for district
    return area


def is_same_state(area: str, student_state: str) -> bool:
    """Check if an area belongs to the student's state."""
    area_state = get_state_for_area(area)
    return area_state and area_state.lower() == student_state.lower()


def is_same_district(area: str, student_district: str) -> bool:
    """Check if an area matches the student's district."""
    # Use area as proxy for district
    if not student_district:
        return False
    return area.lower() == student_district.lower()


if __name__ == "__main__":
    # Test
    test_areas = ["Bengaluru", "Mangaluru", "Surathkal", "New Delhi", "Mumbai", "Hyderabad", "Chennai"]
    for area in test_areas:
        state = get_state_for_area(area)
        print(f"{area} -> {state}")