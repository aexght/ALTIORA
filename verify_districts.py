import json

# Load frontend district.json
with open('frontend/src/data/districts.json', 'r') as f:
    frontend = json.load(f)

# Verify the key states that are used in the old hardcoded list
old_states = ['Maharashtra', 'Karnataka', 'Delhi', 'Tamil Nadu', 'Uttar Pradesh', 'Gujarat', 'West Bengal', 'Telangana', 'Kerala']

for state in old_states:
    entry = next((e for e in frontend if e['state'] == state), None)
    if entry:
        print(state + ': ' + str(len(entry['districts'])) + ' districts - ' + str(entry['districts'][:5]) + '...')
    else:
        print(state + ': NOT FOUND')

# Check new states in the new list
new_states = ['Andaman and Nicobar', 'Chandigarh', 'Dadra and Nagar Haveli and Daman and Diu', 'Ladakh', 'Lakshadweep', 'Puducherry', 'Jammu and Kashmir', 'National Capital Territory of Delhi']
for state in new_states:
    entry = next((e for e in frontend if e['state'] == state), None)
    if entry:
        print(state + ': ' + str(len(entry['districts'])) + ' districts - ' + str(entry['districts']))
    else:
        print(state + ': NOT FOUND')

# Total counts
total_states = len(frontend)
total_districts = sum(len(e['districts']) for e in frontend)
print('Total states: ' + str(total_states))
print('Total districts: ' + str(total_districts))