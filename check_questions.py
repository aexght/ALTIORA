import json
from collections import Counter

with open('questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

print('=== QUESTION BANK ANALYSIS ===')
print(f'Total questions: {len(questions)}')
print(f'ID range: {min(q["id"] for q in questions)} - {max(q["id"] for q in questions)}')

# Check duplicates
ids = [q['id'] for q in questions]
texts = [q['question'] for q in questions]
id_dupes = {k: v for k, v in Counter(ids).items() if v > 1}
text_dupes = {k: v for k, v in Counter(texts).items() if v > 1}
print(f'Duplicate IDs: {id_dupes}')
print(f'Duplicate texts: {text_dupes}')

# Type distribution
types = [q.get('type', 'unknown') for q in questions]
type_counts = Counter(types)
print(f'Type distribution: {dict(type_counts)}')

# Trait coverage
all_traits = set()
for q in questions:
    for opt in q.get('options', []):
        for trait in opt.get('contributes', {}).keys():
            all_traits.add(trait)
print(f'Traits covered: {sorted(all_traits)}')
print(f'Number of unique traits: {len(all_traits)}')

# Invalid option IDs
invalid_option_ids = []
for q in questions:
    for opt in q.get('options', []):
        oid = opt.get('id', '')
        if not (len(oid) == 1 and 'A' <= oid <= 'E'):
            invalid_option_ids.append((q['id'], oid))
print(f'Invalid option IDs: {invalid_option_ids}')

# Check contribution values (should be integers)
invalid_contrib = []
for q in questions:
    for opt in q.get('options', []):
        for trait, val in opt.get('contributes', {}).items():
            if not isinstance(val, int):
                invalid_contrib.append((q['id'], opt['id'], trait, val))
print(f'Non-integer contribution values: {invalid_contrib}')

# Check for malformed questions
malformed = []
for q in questions:
    if 'id' not in q or 'question' not in q or 'options' not in q or 'type' not in q:
        malformed.append(q.get('id', 'unknown'))
print(f'Malformed questions (missing fields): {malformed}')

# Check options count
opt_counts = []
for q in questions:
    opt_counts.append(len(q.get('options', [])))
print(f'Options per question: min={min(opt_counts)}, max={max(opt_counts)}, avg={sum(opt_counts)/len(opt_counts):.1f}')