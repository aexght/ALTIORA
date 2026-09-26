from app import app

with app.test_client() as client:
    # Test predict with different assessment lengths
    for length in [10, 20, 30, 40]:
        payload = {
            "academic": {
                "Class10_Percentage": 85,
                "Class12_Percentage": 80,
                "Class12_Stream": "Science",
                "Subject_Combination": "PCM",
                "Physics_Marks": 90,
                "Chemistry_Marks": 85,
                "Mathematics_Marks": 95,
                "English_Marks": 88,
                "Biology_Marks": 0,
                "Computer_Science_Marks": 0,
                "Statistics_Marks": 0,
                "Accountancy_Marks": 0,
                "Economics_Marks": 0,
                "Business_Studies_Marks": 0
            },
            "answers": {str(i): "A" for i in range(1, length + 1)},
            "preferences": {}
        }
        resp = client.post('/predict', json=payload)
        print('/predict (' + str(length) + 'q, Science):', resp.status_code)
        if resp.status_code == 200:
            data = resp.get_json()
            print('  Domain:', data.get('prediction', {}).get('domain'))
            print('  Confidence:', data.get('prediction', {}).get('confidence'))
            print('  Courses:', len(data.get('recommended_courses', [])))
            print('  Colleges:', len(data.get('recommended_colleges', [])))
        else:
            print('  Error:', resp.get_json())
    
    print()
    
    # Test predict with Commerce stream
    for length in [10, 20, 30, 40]:
        payload = {
            "academic": {
                "Class10_Percentage": 85,
                "Class12_Percentage": 80,
                "Class12_Stream": "Commerce",
                "Subject_Combination": "Commerce",
                "Physics_Marks": 0,
                "Chemistry_Marks": 0,
                "Mathematics_Marks": 0,
                "English_Marks": 88,
                "Biology_Marks": 0,
                "Computer_Science_Marks": 0,
                "Statistics_Marks": 0,
                "Accountancy_Marks": 90,
                "Economics_Marks": 85,
                "Business_Studies_Marks": 92
            },
            "answers": {str(i): "A" for i in range(1, length + 1)},
            "preferences": {}
        }
        resp = client.post('/predict', json=payload)
        print('/predict (' + str(length) + 'q, Commerce):', resp.status_code)
        if resp.status_code == 200:
            data = resp.get_json()
            print('  Domain:', data.get('prediction', {}).get('domain'))
            print('  Confidence:', data.get('prediction', {}).get('confidence'))
            print('  Courses:', len(data.get('recommended_courses', [])))
            print('  Colleges:', len(data.get('recommended_colleges', [])))
        else:
            print('  Error:', resp.get_json())
    
    print()
    
    # Test predict with invalid inputs
    print('Testing invalid inputs:')
    
    # Missing academic
    resp = client.post('/predict', json={"answers": {}})
    print('Missing academic:', resp.status_code, resp.get_json())
    
    # Missing answers
    resp = client.post('/predict', json={"academic": {}})
    print('Missing answers:', resp.status_code, resp.get_json())
    
    # Invalid JSON
    resp = client.post('/predict', data='not json', content_type='application/json')
    print('Invalid JSON:', resp.status_code, resp.get_json())
    
    # Invalid stream
    payload = {
        "academic": {
            "Class10_Percentage": 85,
            "Class12_Percentage": 80,
            "Class12_Stream": "Arts",
        },
        "answers": {str(i): "A" for i in range(1, 11)},
    }
    resp = client.post('/predict', json=payload)
    print('Invalid stream (Arts):', resp.status_code, resp.get_json())
    
    # Invalid marks
    payload = {
        "academic": {
            "Class10_Percentage": 85,
            "Class12_Percentage": 80,
            "Class12_Stream": "Science",
            "Subject_Combination": "PCM",
            "Physics_Marks": 150,  # Invalid
        },
        "answers": {str(i): "A" for i in range(1, 11)},
    }
    resp = client.post('/predict', json=payload)
    print('Invalid marks:', resp.status_code, resp.get_json())