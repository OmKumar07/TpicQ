import os
import requests
from typing import Dict, Any
import json

def mock_quiz(topic: str, difficulty: str) -> Dict[str, Any]:
    """Generate a mock quiz for fallback scenarios"""
    question_count = {"easy": 3, "medium": 5, "hard": 7}.get(difficulty, 3)
    
    questions = []
    for i in range(question_count):
        questions.append({
            "q": f"Sample {difficulty} question {i+1} about {topic}",
            "options": [
                f"Option A about {topic}",
                f"Option B about {topic}",
                f"Option C about {topic}",
                f"Option D about {topic}"
            ],
            "answer_index": i % 4  # Vary the correct answer
        })
    
    return {
        "title": f"Quiz: {topic}",
        "difficulty": difficulty,
        "questions": questions
    }

def generate_quiz(topic: str, difficulty: str) -> Dict[str, Any]:
    """
    Generate a quiz using the Gemini API or fallback to mock data.
    
    Args:
        topic: The topic for the quiz
        difficulty: easy, medium, or hard
    
    Returns:
        Dictionary containing quiz data
    """
    api_key = os.getenv("GEMINI_API_KEY")
    # Try the updated Gemini API endpoint
    api_url = os.getenv("GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent")
    
    # If no API key is provided, return mock data
    if not api_key:
        print(f"⚠️ Warning: GEMINI_API_KEY not found, using mock quiz for {topic}")
        return mock_quiz(topic, difficulty)
    
    print(f"🤖 Calling Gemini API for {topic} ({difficulty}) - API Key: {api_key[:10]}...")
    
    try:
        # Prepare the prompt for Gemini
        prompt = f"""Create a {difficulty} level quiz about {topic}. 
        Generate a JSON response with the following structure:
        {{
            "title": "Quiz: {topic}",
            "difficulty": "{difficulty}",
            "questions": [
                {{
                    "q": "Question text here",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "answer_index": 0
                }}
            ]
        }}
        
        Rules:
        - For easy level: 3-4 questions
        - For medium level: 5-6 questions  
        - For hard level: 7-8 questions
        - Make questions appropriate for the difficulty level
        - Ensure answer_index corresponds to the correct option (0-3)
        - Focus on key concepts and practical application
        
        Return only valid JSON, no additional text."""

        # Prepare request payload for Gemini API
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add API key as URL parameter (alternative method)
        api_url_with_key = f"{api_url}?key={api_key}"
        
        # Make the API call
        print(f"📡 Making API call to: {api_url}")
        response = requests.post(api_url_with_key, json=payload, headers=headers, timeout=10)
        
        print(f"📊 API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Gemini API call successful!")
            
            # Extract text from Gemini response
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    text_content = candidate["content"]["parts"][0]["text"]
                    print(f"📝 Raw Gemini response: {text_content[:200]}...")
                    
                    # Clean the response - remove markdown code blocks if present
                    cleaned_text = text_content.strip()
                    if cleaned_text.startswith("```json"):
                        cleaned_text = cleaned_text[7:]  # Remove ```json
                    if cleaned_text.startswith("```"):
                        cleaned_text = cleaned_text[3:]  # Remove ```
                    if cleaned_text.endswith("```"):
                        cleaned_text = cleaned_text[:-3]  # Remove trailing ```
                    cleaned_text = cleaned_text.strip()
                    
                    print(f"🧹 Cleaned response: {cleaned_text[:100]}...")
                    
                    # Try to parse the JSON response
                    try:
                        quiz_data = json.loads(cleaned_text)
                        
                        # Validate the structure
                        if "questions" in quiz_data and isinstance(quiz_data["questions"], list):
                            print(f"🎯 Successfully generated {len(quiz_data['questions'])} questions!")
                            return quiz_data
                        else:
                            print(f"⚠️ Warning: Invalid quiz structure from Gemini API, using mock quiz")
                            return mock_quiz(topic, difficulty)
                    except json.JSONDecodeError as e:
                        print(f"⚠️ Warning: Could not parse JSON from Gemini API ({e}), using mock quiz")
                        return mock_quiz(topic, difficulty)
        else:
            print(f"❌ Gemini API call failed (status {response.status_code}): {response.text}")
            return mock_quiz(topic, difficulty)
        
    except requests.RequestException as e:
        print(f"⚠️ Warning: Network error calling Gemini API: {e}")
        print(f"🔄 Falling back to mock quiz for {topic}")
        return mock_quiz(topic, difficulty)
    except Exception as e:
        print(f"⚠️ Warning: Unexpected error with Gemini API: {e}")
        print(f"🔄 Falling back to mock quiz for {topic}")
        return mock_quiz(topic, difficulty)
