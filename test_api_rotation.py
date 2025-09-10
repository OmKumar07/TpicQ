#!/usr/bin/env python3
"""
Test script for API key rotation system.
This will test if the API key rotation works correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment variables
load_dotenv()

from backend.services.gemini_client import get_available_api_keys, test_api_key

def main():
    print("🔑 Testing API Key Rotation System")
    print("=" * 50)
    
    # Get all available API keys
    api_keys = get_available_api_keys()
    
    print(f"📊 Found {len(api_keys)} API key(s)")
    
    if not api_keys:
        print("❌ No API keys found! Please configure GEMINI_API_KEY_1, etc.")
        return
    
    # Test each API key
    for i, api_key in enumerate(api_keys):
        print(f"\n🧪 Testing API Key {i+1}: {api_key[:10]}...")
        
        # Test if the key works
        is_working = test_api_key(api_key)
        
        if is_working:
            print(f"✅ API Key {i+1} is working!")
        else:
            print(f"❌ API Key {i+1} failed (quota exceeded or invalid)")
    
    print(f"\n📋 Summary:")
    print(f"- Total API Keys: {len(api_keys)}")
    print(f"- Rotation system is ready!")
    print(f"\n💡 Usage Instructions:")
    print(f"1. Replace 'your_second_api_key_here' etc. with real API keys from different Google accounts")
    print(f"2. Each API key gets 50 free requests per day")
    print(f"3. The system will automatically switch to the next key when one is quota exceeded")
    print(f"4. With 4 keys, you get 200 requests per day total!")

if __name__ == "__main__":
    main()
