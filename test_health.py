import requests
import sys

try:
    response = requests.get('http://127.0.0.1:8000/health', timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    if response.status_code == 200 and response.json().get('status') == 'ok':
        print("✓ Health endpoint working correctly!")
        sys.exit(0)
    else:
        print("✗ Health endpoint returned unexpected response")
        sys.exit(1)
except Exception as e:
    print(f"✗ Error testing health endpoint: {e}")
    sys.exit(1)
