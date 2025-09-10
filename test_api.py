import requests
import json

# Test creating a topic
def test_create_topic():
    url = "http://127.0.0.1:8000/topics"
    data = {"name": "arrays"}
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=data)
    print(f"Create topic status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()

# Test listing topics
def test_list_topics():
    url = "http://127.0.0.1:8000/topics"
    response = requests.get(url)
    print(f"List topics status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()

# Test generating quiz
def test_generate_quiz(topic_id):
    url = f"http://127.0.0.1:8000/topics/{topic_id}/generate-quiz"
    data = {"difficulty": "easy"}
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=data)
    print(f"Generate quiz status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()

if __name__ == "__main__":
    print("Testing API endpoints...")
    
    # Create a topic
    topic_result = test_create_topic()
    print()
    
    # List topics
    topics = test_list_topics()
    print()
    
    # Generate quiz for the topic
    if topic_result and 'id' in topic_result:
        quiz_result = test_generate_quiz(topic_result['id'])
        print()
    
    print("API tests completed!")
