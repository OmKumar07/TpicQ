import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_simple_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": "Say hello in JSON format like: {\"message\": \"hello\"}"
            }]
        }]
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        print("Testing Gemini API...")
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if "candidates" in result:
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                print(f"✅ Success! Response: {text}")
                return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return False

if __name__ == "__main__":
    test_simple_gemini()
