import requests
import json

# Test creating a topic and generating a quiz
base_url = "http://127.0.0.1:8000"

# Create a topic
print("Creating topic...")
topic_response = requests.post(f"{base_url}/topics", json={"name": "JavaScript Fundamentals"})
print(f"Topic creation status: {topic_response.status_code}")

if topic_response.status_code == 200:
    topic = topic_response.json()
    topic_id = topic["id"]
    print(f"Topic created with ID: {topic_id}")
elif topic_response.status_code == 400:
    # Topic exists, get all topics and find it
    print("Topic exists, fetching existing topics...")
    topics_response = requests.get(f"{base_url}/topics")
    if topics_response.status_code == 200:
        topics = topics_response.json()
        topic_id = topics[0]["id"] if topics else None
        if topic_id:
            print(f"Using existing topic with ID: {topic_id}")
        else:
            print("No topics found")
            exit()
else:
    print(f"Unexpected error: {topic_response.text}")
    exit()

if topic_id:
    
    # Generate a quiz
    print("Generating quiz...")
    quiz_response = requests.post(
        f"{base_url}/topics/{topic_id}/generate-quiz",
        json={"difficulty": "easy"}
    )
    print(f"Quiz generation status: {quiz_response.status_code}")
    
    if quiz_response.status_code == 200:
        quiz = quiz_response.json()
        print(f"Quiz generated successfully!")
        print(f"Title: {quiz['content']['title']}")
        print(f"Questions: {len(quiz['content']['questions'])}")
        print(f"First question: {quiz['content']['questions'][0]['q']}")
    else:
        print(f"Quiz generation failed: {quiz_response.text}")
