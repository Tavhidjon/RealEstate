# JWT Admin Authentication Test Script
# This script demonstrates how to authenticate as an admin using JWT

import requests
import json
import sys

# Configuration
BASE_URL = 'http://127.0.0.1:8000'
LOGIN_URL = f'{BASE_URL}/auth/login/'
ADMIN_PANEL_URL = f'{BASE_URL}/admin/panel/'
AUTH_HELP_URL = f'{BASE_URL}/auth/help/'

# Check command line arguments
if len(sys.argv) < 3:
    print("Usage: python test_jwt_admin_auth.py <admin_email> <admin_password>")
    print("Example: python test_jwt_admin_auth.py admin@example.com password123")
    sys.exit(1)

# Admin credentials from command line
admin_email = sys.argv[1]
admin_password = sys.argv[2]

print("\n=== JWT Admin Authentication Test ===")

# Step 1: Show auth help instructions
print("\n1. Getting auth help instructions...")
try:
    help_response = requests.get(AUTH_HELP_URL)
    print(f"Status Code: {help_response.status_code}")
    print(json.dumps(help_response.json(), indent=2))
except Exception as e:
    print(f"Error getting auth help: {str(e)}")

# Step 2: Login to get tokens
print("\n2. Logging in as admin to get tokens...")
try:
    login_response = requests.post(LOGIN_URL, data={
        'email': admin_email,
        'password': admin_password
    })
    print(f"Status Code: {login_response.status_code}")
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        print("Login successful!")
        
        # Extract tokens
        if 'access' in login_data and 'refresh' in login_data:
            access_token = login_data['access']
            refresh_token = login_data['refresh']
            print(f"Access token: {access_token[:20]}...")
            print(f"Refresh token: {refresh_token[:20]}...")
        else:
            print("Error: Tokens not found in login response")
            sys.exit(1)
    else:
        print("Login failed:")
        print(json.dumps(login_response.json(), indent=2))
        sys.exit(1)
except Exception as e:
    print(f"Error during login: {str(e)}")
    sys.exit(1)

# Step 3: Access admin panel with token
print("\n3. Accessing admin panel with access token...")
try:
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    admin_response = requests.get(ADMIN_PANEL_URL, headers=headers)
    print(f"Status Code: {admin_response.status_code}")
    
    if admin_response.status_code == 200:
        print("Admin panel access successful!")
        print(json.dumps(admin_response.json(), indent=2))
    else:
        print("Admin panel access failed:")
        print(json.dumps(admin_response.json(), indent=2))
except Exception as e:
    print(f"Error accessing admin panel: {str(e)}")

print("\nTest completed!")
