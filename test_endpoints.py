from app import app

with app.test_client() as client:
    # Test health endpoint
    resp = client.get('/health')
    print('/health:', resp.status_code, resp.get_json())
    
    # Test root
    resp = client.get('/')
    print('/', resp.status_code, resp.get_json())
    
    # Test questions
    resp = client.get('/questions')
    data = resp.get_json()
    print('/questions:', resp.status_code, len(data), 'questions')
    
    # Test assessment endpoints
    for length in [10, 20, 30, 40]:
        resp = client.get('/assessment?length=' + str(length))
        data = resp.get_json()
        print('/assessment?length=' + str(length) + ':', resp.status_code, data.get('length', 'N/A'), 'questions')
    
    # Test invalid assessment length
    resp = client.get('/assessment?length=5')
    print('/assessment?length=5:', resp.status_code, resp.get_json())
    
    # Test invalid exclude
    resp = client.get('/assessment?length=10&exclude=abc')
    print('/assessment?length=10&exclude=abc:', resp.status_code, resp.get_json())
    
    # Test predict endpoint with minimal valid payload
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
        "answers": {str(i): "A" for i in range(1, 11)},
        "preferences": {}
    }
    resp = client.post('/predict', json=payload)
    print('/predict (10q, Science):', resp.status_code)
    if resp.status_code == 200:
        data = resp.get_json()
        print('  Predicted domain:', data.get('prediction', {}).get('domain'))
        print('  Confidence:', data.get('prediction', {}).get('confidence'))
        print('  Courses:', len(data.get('recommended_courses', [])))
        print('  Colleges:', len(data.get('recommended_colleges', [])))
    else:
        print('  Error:', resp.get_json())