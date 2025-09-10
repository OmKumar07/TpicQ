import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_gemini_api():
    api_key = os.getenv("GEMINI_API_KEY")
    # Updated API URL for the current Gemini API
    api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    
    print(f"API Key: {api_key[:10]}..." if api_key else "No API key")
    print(f"API URL: {api_url}")
    
    # Simple test prompt
    prompt = """Create a simple quiz about Python programming with 2 questions. 
    Return only valid JSON with this structure:
    {
        "title": "Quiz: Python",
        "difficulty": "easy",
        "questions": [
            {
                "q": "What is Python?",
                "options": ["A language", "A snake", "A tool", "A framework"],
                "answer_index": 0
            }
        ]
    }"""
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    try:
        print("Making API call...")
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Response received successfully!")
            
            if "candidates" in result:
                text_content = result["candidates"][0]["content"]["parts"][0]["text"]
                print(f"Raw response: {text_content}")
                
                # Try to parse JSON
                try:
                    quiz_data = json.loads(text_content)
                    print("✅ Successfully parsed JSON!")
                    print(f"Quiz title: {quiz_data.get('title', 'N/A')}")
                    print(f"Number of questions: {len(quiz_data.get('questions', []))}")
                    return True
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing failed: {e}")
                    return False
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_gemini_api()
