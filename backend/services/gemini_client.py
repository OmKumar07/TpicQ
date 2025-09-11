import os
import requests
from typing import Dict, Any, List, Optional
import json
import random
import time

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
        raise Exception("No Gemini API keys configured. Please add valid API keys to environment variables.")
    
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
            
            # Check error type
            error_str = str(e).lower()
            
            # For quota errors (429), try next key immediately
            if "429" in str(e) or "quota" in error_str:
                print(f"🔄 Key {i+1} quota exceeded, trying next key...")
                continue
            
            # For API disabled errors (403), try next key immediately
            if "403" in str(e) or "permission" in error_str or "disabled" in error_str:
                print(f"🔄 Key {i+1} API disabled, trying next key...")
                continue
            
            # For overloaded errors (503), wait a bit before trying next key
            if "503" in str(e) or "overloaded" in error_str or "unavailable" in error_str:
                print(f"⏳ API overloaded, waiting 2 seconds before next key...")
                time.sleep(2)
                continue
            
            # For other errors, also try the next key
            continue
    
    # If all keys failed, raise the last error instead of using fallback
    print(f"❌ All {len(api_keys)} API keys failed")
    
    # Create a more descriptive error message based on the last error
    if last_error:
        error_str = str(last_error).lower()
        if "503" in str(last_error) or "overloaded" in error_str:
            raise Exception("All Gemini API services are currently overloaded. Please try again in a few minutes.")
        elif "403" in str(last_error) or "permission" in error_str or "disabled" in error_str:
            raise Exception("Gemini API access is restricted. Please check your API key permissions.")
        elif "429" in str(last_error) or "quota" in error_str:
            raise Exception("All API keys have exceeded their quota limits. Please try again tomorrow or add more API keys.")
        else:
            raise Exception(f"All API keys failed: {last_error}")
    else:
        raise Exception("All API keys failed with unknown errors.")

def call_gemini_api(api_key: str, topic: str, difficulty: str, max_retries: int = 3) -> Dict[str, Any]:
    """
    Make the actual API call to Gemini with a specific API key.
    Includes retry logic for transient failures.
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
    
    for attempt in range(max_retries):
        try:
            # Calculate timeout based on attempt
            timeout = 30 + (attempt * 15)  # 30s, 45s, 60s
            
            print(f"📡 Making API call to: {api_url} (attempt {attempt + 1}/{max_retries})")
            response = requests.post(api_url_with_key, json=payload, headers=headers, timeout=timeout)
            
            print(f"📊 API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Gemini API call successful!")
                
                # Extract text from Gemini response
                if "candidates" in result and len(result["candidates"]) > 0:
                    candidate = result["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        text_content = candidate["content"]["parts"][0]["text"]
                        print(f"📝 Raw Gemini response received")
                        
                        # Clean the response - remove markdown code blocks if present
                        cleaned_text = text_content.strip()
                        if cleaned_text.startswith("```json"):
                            cleaned_text = cleaned_text[7:]  # Remove ```json
                        if cleaned_text.startswith("```"):
                            cleaned_text = cleaned_text[3:]  # Remove ```
                        if cleaned_text.endswith("```"):
                            cleaned_text = cleaned_text[:-3]  # Remove trailing ```
                        cleaned_text = cleaned_text.strip()
                        
                        # Try to parse the JSON response
                        try:
                            quiz_data = json.loads(cleaned_text)
                            
                            # Validate the structure
                            if "questions" in quiz_data and isinstance(quiz_data["questions"], list):
                                print(f"🎯 Successfully generated {len(quiz_data['questions'])} questions!")
                                
                                # Randomize the answer positions to prevent predictability
                                quiz_data = randomize_quiz_answers(quiz_data)
                                
                                print(f"🔀 Answer positions randomized!")
                                
                                # Verify answer distribution
                                answer_distribution = {}
                                for q in quiz_data['questions']:
                                    idx = q['answer_index']
                                    answer_distribution[idx] = answer_distribution.get(idx, 0) + 1
                                print(f"📊 Answer distribution: {answer_distribution}")
                                
                                return quiz_data
                            else:
                                raise Exception("Invalid quiz structure from Gemini API")
                        except json.JSONDecodeError as e:
                            raise Exception(f"Failed to parse JSON from Gemini API: {e}")
                    else:
                        raise Exception("Unexpected Gemini response structure")
                else:
                    raise Exception("No candidates in Gemini response")
            
            elif response.status_code == 503:
                # Service unavailable - retry with exponential backoff
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    print(f"⏳ API overloaded (503), retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"❌ API still overloaded after {max_retries} attempts")
                    raise Exception(f"Gemini API overloaded after {max_retries} retries")
            
            elif response.status_code == 429:
                # Rate limit - don't retry this key
                print(f"❌ Rate limit exceeded (429) for this API key")
                raise Exception("Gemini API rate limit exceeded")
            
            elif response.status_code == 403:
                # Forbidden - API disabled
                print(f"❌ API access forbidden (403) - API may be disabled")
                raise Exception("Gemini API access forbidden - check API key and permissions")
            
            else:
                print(f"❌ Gemini API call failed (status {response.status_code})")
                print(f"🔍 Response text: {response.text}")
                
                # For other errors, retry once more
                if attempt < max_retries - 1:
                    print(f"🔄 Retrying API call in 3 seconds...")
                    time.sleep(3)
                    continue
                else:
                    raise Exception(f"Gemini API call failed with status {response.status_code}")
        
        except requests.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"⚠️ Network error: {e}, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            else:
                print(f"⚠️ Network error calling Gemini API: {e}")
                raise Exception(f"Network error calling Gemini API: {e}")
        except Exception as e:
            print(f"⚠️ Error with Gemini API: {e}")
            raise
