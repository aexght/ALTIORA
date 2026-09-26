import pandas as pd
import os
import sys
import re

def main():
    base_dir = r"D:\ML-PROJECT-SEM-5\College Datasets"
    files = {
        'college': os.path.join(base_dir, 'college_database.csv'),
        'eligibility': os.path.join(base_dir, 'course_eligibility.csv'),
        'mapping': os.path.join(base_dir, 'college_course_mapping.csv'),
        'hostel': os.path.join(base_dir, 'hostel_database.csv'),
        'fee': os.path.join(base_dir, 'fee_database.csv'),
        'image': os.path.join(base_dir, 'image_download_manifest.csv')
    }
    
    passed = 0
    failed = 0
    
    def report(name, condition, details=""):
        nonlocal passed, failed
        if condition:
            print(f"[PASS] {name}")
            passed += 1
        else:
            print(f"[FAIL] {name} - {details}")
            failed += 1

    # 1. Structural Integrity
    dfs = {}
    for key, path in files.items():
        if os.path.exists(path) and os.path.getsize(path) > 0:
            try:
                dfs[key] = pd.read_csv(path, dtype=str)
                report(f"{key} exists and non-empty", True)
                if len(dfs[key]) == 0:
                    report(f"{key} has rows", False, "File has no rows")
                else:
                    report(f"{key} has rows", True)
                    
            except Exception as e:
                report(f"{key} read error", False, str(e))
        else:
            report(f"{key} exists and non-empty", False, f"File missing or empty: {path}")
            return
            
    # Check Columns (Simplified)
    req_cols = {
        'college': ['College_ID', 'College_Name', 'State', 'Ownership', 'NAAC_Grade', 'NIRF_Rank', 'AICTE_Approved', 'Hostel_Available', 'College_Type', 'Official_Website'],
        'eligibility': ['Eligibility_ID'],
        'mapping': ['College_ID', 'Course_Name', 'Eligibility_ID', 'Mode', 'Degree_Level', 'Career_Domain'],
        'hostel': ['College_ID', 'Boys_Hostel', 'Girls_Hostel'],
        'fee': ['College_ID'],
        'image': ['College_ID']
    }
    
    for key, cols in req_cols.items():
        missing = [c for c in cols if c not in dfs[key].columns]
        report(f"{key} required columns", len(missing) == 0, f"Missing {missing}")
        
    # 2. PK Uniqueness
    report("College PK unique", dfs['college']['College_ID'].is_unique, "Duplicate College_ID found")
    report("Eligibility PK unique", dfs['eligibility']['Eligibility_ID'].is_unique, "Duplicate Eligibility_ID found")
    
    if 'College_ID' in dfs['mapping'].columns and 'Course_Name' in dfs['mapping'].columns:
        mapping_dups = dfs['mapping'][['College_ID', 'Course_Name']].duplicated().any()
        report("Mapping PK unique", not mapping_dups, "Duplicate (College_ID, Course_Name) found")

    # 3. FK Integrity
    if 'College_ID' in dfs['mapping'].columns:
        invalid_mapping_colleges = ~dfs['mapping']['College_ID'].isin(dfs['college']['College_ID'])
        report("Mapping College_ID FK", not invalid_mapping_colleges.any(), f"{invalid_mapping_colleges.sum()} invalid references")
        
    if 'Eligibility_ID' in dfs['mapping'].columns:
        invalid_mapping_elig = ~dfs['mapping']['Eligibility_ID'].isin(dfs['eligibility']['Eligibility_ID'])
        report("Mapping Eligibility_ID FK", not invalid_mapping_elig.any(), f"{invalid_mapping_elig.sum()} invalid references")
        
    for key in ['hostel', 'fee', 'image']:
        if 'College_ID' in dfs[key].columns:
            invalid_fk = ~dfs[key]['College_ID'].isin(dfs['college']['College_ID'])
            report(f"{key} College_ID FK", not invalid_fk.any(), f"{invalid_fk.sum()} invalid references")

    # 4. Vocab Validation
    vocab = {
        'Ownership': ['Government', 'Private', 'Deemed', 'Government-Aided'],
        'NAAC_Grade': ['A++', 'A+', 'A', 'B++', 'B+', 'B', 'C', 'Unknown'],
        'AICTE_Approved': ['Yes', 'No', 'Not Applicable', 'Unknown'],
        'Hostel_Available': ['Yes', 'No', 'Unknown'],
        'College_Type': ['Engineering', 'Medical', 'Commerce', 'Management', 'Law', 'Science', 'Agriculture', 'Pharmacy', 'Design', 'Multi-Disciplinary', 'University']
    }
    for col, allowed in vocab.items():
        if col in dfs['college'].columns:
            invalid = ~dfs['college'][col].isin(allowed)
            report(f"Vocab {col}", not invalid.any(), f"Invalid values: {dfs['college'].loc[invalid, col].unique()}")

    mapping_vocab = {
        'Mode': ['Full-Time', 'Part-Time', 'Distance', 'Unknown'],
        'Degree_Level': ['Undergraduate', 'Undergraduate Professional', 'Integrated', 'Postgraduate'],
        'Career_Domain': ['Agriculture Environment & Food', 'Business & Management', 'Commerce & Finance', 'Design Media & Creative', 'Engineering', 'Law & Legal Studies', 'Life Sciences & Biotechnology', 'Medical & Health Sciences', 'Physical & Mathematical Sciences', 'Technology & Computing']
    }
    for col, allowed in mapping_vocab.items():
        if col in dfs['mapping'].columns:
            invalid = ~dfs['mapping'][col].isin(allowed)
            report(f"Vocab {col}", not invalid.any(), f"Invalid values: {dfs['mapping'].loc[invalid, col].unique()}")
            
    hostel_vocab = {
        'Boys_Hostel': ['Yes', 'No', 'Unknown'],
        'Girls_Hostel': ['Yes', 'No', 'Unknown']
    }
    for col, allowed in hostel_vocab.items():
        if col in dfs['hostel'].columns:
            invalid = ~dfs['hostel'][col].isin(allowed)
            report(f"Vocab {col}", not invalid.any(), f"Invalid values: {dfs['hostel'].loc[invalid, col].unique()}")

    # 5. Domain Coverage
    if 'Career_Domain' in dfs['mapping'].columns:
        domains_present = dfs['mapping']['Career_Domain'].value_counts()
        missing_domains = [d for d in mapping_vocab['Career_Domain'] if d not in domains_present or domains_present[d] < 5]
        report("Domain Coverage", len(missing_domains) == 0, f"Domains with < 5 mappings: {missing_domains}")

    if 'State' in dfs['college'].columns:
        states_present = dfs['college']['State'].nunique()
        report("State Coverage", states_present >= 9, f"Only {states_present} states present")

    # 6. Data Quality
    for col in ['College_ID', 'College_Name', 'State']:
        if col in dfs['college'].columns:
            nulls = dfs['college'][col].isnull() | (dfs['college'][col] == 'NaN') | (dfs['college'][col] == 'nan') | (dfs['college'][col] == 'None') | (dfs['college'][col] == '')
            report(f"No nulls in {col}", not nulls.any(), f"{nulls.sum()} nulls found")

    if 'Official_Website' in dfs['college'].columns:
        invalid_url = ~dfs['college']['Official_Website'].astype(str).str.startswith('http') & (dfs['college']['Official_Website'] != 'Unknown')
        report("Website format", not invalid_url.any(), f"{invalid_url.sum()} invalid websites")

    if 'NIRF_Rank' in dfs['college'].columns:
        def valid_nirf(x):
            x = str(x).strip()
            if x in ['Unranked', 'Unknown']: return True
            if x.isdigit(): return True
            if re.match(r'^Band \d+-\d+$', x): return True
            return False
        invalid_nirf = ~dfs['college']['NIRF_Rank'].apply(valid_nirf)
        report("NIRF_Rank format", not invalid_nirf.any(), f"{invalid_nirf.sum()} invalid NIRF ranks")

    print(f"\nTotal Passed: {passed}")
    print(f"Total Failed: {failed}")
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
