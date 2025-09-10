import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if API key is loaded
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key loaded: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"API Key (first 10 chars): {api_key[:10]}...")
else:
    print("API Key is None or empty")

# Check all environment variables that start with GEMINI
gemini_vars = {k: v for k, v in os.environ.items() if k.startswith("GEMINI")}
print(f"All GEMINI environment variables: {gemini_vars}")
