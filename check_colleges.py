import pandas as pd
import json

# College master dataset
df = pd.read_csv('College Datasets/college_database.csv')
print('=== COLLEGE DATABASE ===')
print(f'Total colleges: {len(df)}')
print(f'Columns: {list(df.columns)}')
print()

# Missing critical fields
critical_fields = ['College_ID', 'College_Name', 'State', 'District', 'Ownership', 'Course_Offered', 'Fee_Per_Year', 'Hostel_Available', 'Website', 'NAAC_Grade', 'NIRF_Ranking']
for field in critical_fields:
    if field in df.columns:
        missing = df[field].isna().sum()
        print(f'{field}: {missing} missing out of {len(df)}')
    else:
        print(f'{field}: COLUMN NOT FOUND')

print()
# Duplicate College_IDs
dup_ids = df[df.duplicated(subset=['College_ID'], keep=False)] if 'College_ID' in df.columns else pd.DataFrame()
print(f'Duplicate College_IDs: {len(dup_ids)}')

# Duplicate college names
dup_names = df[df.duplicated(subset=['College_Name'], keep=False)] if 'College_Name' in df.columns else pd.DataFrame()
print(f'Duplicate College_Names: {len(dup_names)}')

# Course mapping status
course_map = pd.read_csv('College Datasets/college_course_mapping.csv')
print(f'\nCourse mapping records: {len(course_map)}')
print(f'Course mapping columns: {list(course_map.columns)}')

# Fee availability
fee_db = pd.read_csv('College Datasets/fee_database.csv')
print(f'\nFee database records: {len(fee_db)}')

# Hostel availability
hostel_db = pd.read_csv('College Datasets/hostel_database.csv')
print(f'Hostel database records: {len(hostel_db)}')

# Verification status
if 'Verification_Status' in df.columns:
    print(f'\nVerification status distribution:')
    print(df['Verification_Status'].value_counts())
else:
    print('\nVerification_Status column not found')