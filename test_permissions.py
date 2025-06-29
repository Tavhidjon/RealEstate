import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_permissions(token=None):
    """Test the permissions for regular users vs admin users"""
    
    # Headers for authenticated requests
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    # Test endpoints
    endpoints = [
        "/buildings/",
        "/companies/",
        "/floors/",
        "/flats/"
    ]
    
    # Test READ permissions (GET)
    print("\n=== Testing READ permissions (GET) ===")
    for endpoint in endpoints:
        url = f"{BASE_URL}{endpoint}"
        response = requests.get(url, headers=headers)
        print(f"{endpoint}: {response.status_code} - {'Success' if response.status_code == 200 else 'Failed'}")
    
    # Test WRITE permissions (POST)
    print("\n=== Testing WRITE permissions (POST) ===")
    for endpoint in endpoints:
        url = f"{BASE_URL}{endpoint}"
        # Example data for POST request (will likely fail due to validation, but that's OK)
        data = {"name": "Test", "description": "Testing permissions"}
        response = requests.post(url, json=data, headers=headers)
        
        # For admin users, we expect 400 (bad request) since our test data is incomplete
        # For non-admin users, we expect 403 (forbidden) or 401 (unauthorized)
        print(f"{endpoint}: {response.status_code} - " + 
              (f"Success (Admin: validation error)" if response.status_code == 400 else 
               f"Success (Non-admin: permission denied)" if response.status_code in [401, 403] else 
               "Failed (unexpected status)"))


if __name__ == "__main__":
    # Check if token was provided
    if len(sys.argv) > 1:
        token = sys.argv[1]
        print(f"Testing with provided token: {token[:10]}...")
        test_permissions(token)
    else:
        print("No token provided. Testing unauthenticated access.")
        test_permissions()
        
        print("\n\nTo test with a token, run:")
        print("python test_permissions.py <your_jwt_token>")
