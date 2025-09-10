import os
import requests
from typing import Dict, Any, List, Optional
import json
import random

def get_available_api_keys() -> List[str]:
    """
    Get all available Gemini API keys from environment variables.
    Returns a list of API keys that are properly configured.
    """
    api_keys = []
    
    # Check for numbered API keys (GEMINI_API_KEY_1, GEMINI_API_KEY_2, etc.)
    for i in range(1, 10):  # Support up to 9 API keys
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if key and key.strip() and key != "your_api_key_here" and not key.endswith("_here"):
            api_keys.append(key.strip())
    
    # Fallback to original GEMINI_API_KEY if no numbered keys found
    if not api_keys:
        fallback_key = os.getenv("GEMINI_API_KEY")
        if fallback_key and fallback_key.strip():
            api_keys.append(fallback_key.strip())
    
    return api_keys

def test_api_key(api_key: str) -> bool:
    """
    Test if an API key is valid and not quota exceeded.
    Returns True if the key is usable, False otherwise.
    """
    test_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    test_payload = {
        "contents": [{
            "parts": [{"text": "Test"}]
        }]
    }
    
    try:
        response = requests.post(
            test_url,
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        # If we get 429 (quota exceeded), this key is not usable
        if response.status_code == 429:
            return False
        
        # If we get 200 or other non-quota errors, the key is potentially usable
        return response.status_code != 429
        
    except Exception:
        return False

def randomize_quiz_answers(quiz_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Randomize the correct answer positions in a quiz to prevent predictability.
    Takes the correct answer (always at index 0 from Gemini) and shuffles options.
    """
    if "questions" not in quiz_data:
        return quiz_data
    
    for question in quiz_data["questions"]:
        if "options" in question and "answer_index" in question:
            # Get the current correct answer
            correct_answer = question["options"][question["answer_index"]]
            
            # Shuffle all options
            options = question["options"].copy()
            random.shuffle(options)
            
            # Find where the correct answer ended up after shuffling
            new_correct_index = options.index(correct_answer)
            
            # Update the question with shuffled options and new correct index
            question["options"] = options
            question["answer_index"] = new_correct_index
    
    return quiz_data

def mock_quiz(topic: str, difficulty: str) -> Dict[str, Any]:
    """Generate a mock quiz for fallback scenarios - NOT USED in production"""
    question_count = 10  # Always generate 10 questions
    
    questions = []
    for i in range(question_count):
        questions.append({
            "q": f"Sample {difficulty} question {i+1} about {topic}",
            "options": [
                f"Correct answer for Q{i+1}",  # Always put correct answer first
                f"Wrong option B{i+1}", 
                f"Wrong option C{i+1}",
                f"Wrong option D{i+1}"
            ],
            "answer_index": 0  # Always 0 initially, will be randomized
        })
    
    quiz_data = {
        "title": f"Quiz: {topic}",
        "difficulty": difficulty,
        "questions": questions
    }
    
    # Apply randomization to ensure unpredictable answer positions
    return randomize_quiz_answers(quiz_data)

def generate_quiz(topic: str, difficulty: str) -> Dict[str, Any]:
    """
    Generate a quiz using the Gemini API with rotating API keys for quota management.
    
    Args:
        topic: The topic for the quiz
        difficulty: easy, medium, or hard
    
    Returns:
        Dictionary containing quiz data
    
    Raises:
        Exception: If all API keys fail or return invalid data
    """
    # Get all available API keys
    api_keys = get_available_api_keys()
    
    if not api_keys:
        print(f"❌ Error: No valid GEMINI_API_KEY found")
        raise Exception("No Gemini API keys configured")
    
    print(f"🔑 Found {len(api_keys)} API key(s) available")
    
    # Try each API key until one works
    last_error = None
    for i, api_key in enumerate(api_keys):
        try:
            print(f"🤖 Trying API key {i+1}/{len(api_keys)} for {topic} ({difficulty}) - Key: {api_key[:10]}...")
            
            result = call_gemini_api(api_key, topic, difficulty)
            if result:
                print(f"✅ Successfully generated quiz using API key {i+1}")
                return result
                
        except Exception as e:
            print(f"❌ API key {i+1} failed: {str(e)}")
            last_error = e
            
            # If this was a quota error, try the next key immediately
            if "429" in str(e) or "quota" in str(e).lower():
                print(f"🔄 Key {i+1} quota exceeded, trying next key...")
                continue
            
            # For other errors, also try the next key
            continue
    
    # If all keys failed, raise the last error
    print(f"❌ All {len(api_keys)} API keys failed")
    raise Exception(f"All API keys failed. Last error: {last_error}")

def call_gemini_api(api_key: str, topic: str, difficulty: str) -> Dict[str, Any]:
    """
    Make the actual API call to Gemini with a specific API key.
    """
    # Try the updated Gemini API endpoint
    api_url = os.getenv("GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent")
    
    # Prepare the prompt for Gemini
    prompt = f"""Create a {difficulty} level quiz about {topic}. 
    Generate a JSON response with the following structure:
    {{
        "title": "Quiz: {topic}",
        "difficulty": "{difficulty}",
        "questions": [
            {{
                "q": "Question text here",
                "options": ["Correct Answer", "Wrong Option 1", "Wrong Option 2", "Wrong Option 3"],
                "answer_index": 0
            }}
        ]
    }}
    
    CRITICAL REQUIREMENTS:
    - Generate exactly 10 questions regardless of difficulty level
    - ALWAYS put the correct answer as the FIRST option (index 0)
    - The system will automatically randomize the answer positions later
    - Keep ALL options SHORT and CONCISE (maximum 6-8 words each)
    - Avoid long, detailed explanations in options - use brief, clear phrases
    - Make sure all options are plausible but clearly distinct
    
    Difficulty guidelines:
    - EASY: Basic concepts, definitions, simple applications
    - MEDIUM: Applied knowledge, problem-solving, analysis  
    - HARD: Complex scenarios, advanced concepts, critical thinking
    
    Question quality rules:
    - Focus on key concepts and practical application of {topic}
    - Make questions specific and educational
    - Ensure all 4 options are plausible but clearly distinct
    - Use varied question types: definitions, applications, comparisons, best practices
    - Options should be concise phrases, not full sentences
    - Structure: [Correct Answer, Wrong 1, Wrong 2, Wrong 3]
    
    Example of good short options:
    - "Machine learning algorithm"
    - "Database system" 
    - "Security protocol"
    - "Web framework"
    
    IMPORTANT: Always place the correct answer as the first option (index 0). 
    The randomization will happen automatically after generation.
    
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
                            print(f"🔍 First question before randomization: {quiz_data['questions'][0]}")
                            
                            # Randomize the answer positions to prevent predictability
                            quiz_data = randomize_quiz_answers(quiz_data)
                            
                            print(f"🔀 Answer positions randomized!")
                            print(f"🔍 First question after randomization: {quiz_data['questions'][0]}")
                            
                            # Verify answer distribution
                            answer_distribution = {}
                            for q in quiz_data['questions']:
                                idx = q['answer_index']
                                answer_distribution[idx] = answer_distribution.get(idx, 0) + 1
                            print(f"📊 Answer distribution: {answer_distribution}")
                            
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
