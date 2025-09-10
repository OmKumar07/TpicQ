import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"Testing with API key: {api_key[:10]}...")

# Try the simplest possible request
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    response = requests.get(url, timeout=10)
    print(f"List models status: {response.status_code}")
    if response.status_code == 200:
        models = response.json()
        print("Available models:")
        for model in models.get('models', [])[:5]:  # Show first 5
            print(f"  - {model['name']}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")
