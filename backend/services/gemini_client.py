import os
import requests
from typing import Dict, Any
import json

def mock_quiz(topic: str, difficulty: str) -> Dict[str, Any]:
    """Generate a mock quiz for fallback scenarios"""
    question_count = 10  # Always generate 10 questions
    
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
    Generate a quiz using the Gemini API. NO FALLBACK TO MOCK DATA.
    
    Args:
        topic: The topic for the quiz
        difficulty: easy, medium, or hard
    
    Returns:
        Dictionary containing quiz data
    
    Raises:
        Exception: If API call fails or returns invalid data
    """
    api_key = os.getenv("GEMINI_API_KEY")
    # Try the updated Gemini API endpoint
    api_url = os.getenv("GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent")
    
    # If no API key is provided, raise an error
    if not api_key:
        print(f"❌ Error: GEMINI_API_KEY not found")
        raise Exception("Gemini API key not configured")
    
    print(f"🤖 Calling Gemini API for {topic} ({difficulty}) - API Key: {api_key[:10]}...")
    
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
    - Generate exactly 10 questions regardless of difficulty level
    - Difficulty should affect question complexity, not quantity:
      * EASY: Basic concepts, definitions, simple applications
      * MEDIUM: Applied knowledge, problem-solving, analysis
      * HARD: Complex scenarios, advanced concepts, critical thinking
    - Ensure answer_index corresponds to the correct option (0-3)
    - Focus on key concepts and practical application of {topic}
    - Make questions specific, detailed, and educational
    - Vary question types: definitions, applications, comparisons, best practices
    - Ensure all options are plausible but only one is correct
    
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
    
    try:
        # Make the API call
        print(f"📡 Making API call to: {api_url}")
        response = requests.post(api_url_with_key, json=payload, headers=headers, timeout=60)
        
        print(f"📊 API Response Status: {response.status_code}")
        print(f"📄 API Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Gemini API call successful!")
            print(f"🔍 Full API response: {result}")
            
            # Extract text from Gemini response
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    text_content = candidate["content"]["parts"][0]["text"]
                    print(f"📝 Raw Gemini response: {text_content}")
                    
                    # Clean the response - remove markdown code blocks if present
                    cleaned_text = text_content.strip()
                    if cleaned_text.startswith("```json"):
                        cleaned_text = cleaned_text[7:]  # Remove ```json
                    if cleaned_text.startswith("```"):
                        cleaned_text = cleaned_text[3:]  # Remove ```
                    if cleaned_text.endswith("```"):
                        cleaned_text = cleaned_text[:-3]  # Remove trailing ```
                    cleaned_text = cleaned_text.strip()
                    
                    print(f"🧹 Cleaned response: {cleaned_text}")
                    
                    # Try to parse the JSON response
                    try:
                        quiz_data = json.loads(cleaned_text)
                        
                        # Validate the structure
                        if "questions" in quiz_data and isinstance(quiz_data["questions"], list):
                            print(f"🎯 Successfully generated {len(quiz_data['questions'])} questions!")
                            print(f"🔍 First question: {quiz_data['questions'][0]}")
                            return quiz_data
                        else:
                            print(f"⚠️ Warning: Invalid quiz structure from Gemini API")
                            print(f"🔍 Received structure: {quiz_data}")
                            raise Exception("Invalid quiz structure from Gemini API")
                    except json.JSONDecodeError as e:
                        print(f"⚠️ Warning: Could not parse JSON from Gemini API")
                        print(f"🔍 JSON Error: {e}")
                        print(f"🔍 Raw text that failed to parse: {cleaned_text}")
                        raise Exception(f"Failed to parse JSON from Gemini API: {e}")
                else:
                    print(f"⚠️ Warning: Unexpected Gemini response structure")
                    print(f"🔍 Candidate structure: {candidate}")
                    raise Exception("Unexpected Gemini response structure")
            else:
                print(f"⚠️ Warning: No candidates in Gemini response")
                print(f"🔍 Response structure: {result}")
                raise Exception("No candidates in Gemini response")
        else:
            print(f"❌ Gemini API call failed (status {response.status_code})")
            print(f"🔍 Response text: {response.text}")
            raise Exception(f"Gemini API call failed with status {response.status_code}")
        
    except requests.RequestException as e:
        print(f"⚠️ Network error calling Gemini API: {e}")
        raise Exception(f"Network error calling Gemini API: {e}")
    except Exception as e:
        print(f"⚠️ Error with Gemini API: {e}")
        raise
