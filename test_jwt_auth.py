# JWT Authentication Test Script
# This script demonstrates how to use the JWT authentication endpoints

import requests
import json
import random

# Configuration
BASE_URL = 'http://127.0.0.1:8000'
REGISTER_URL = f'{BASE_URL}/auth/register/'
LOGIN_URL = f'{BASE_URL}/auth/login/'
REFRESH_URL = f'{BASE_URL}/auth/login/refresh/'
PROTECTED_URL = f'{BASE_URL}/example/protected/'
LOGOUT_URL = f'{BASE_URL}/auth/logout/'

# Test user data
import random
random_num = random.randint(1000, 9999)

user_data = {
    'username': f'testuser{random_num}',
    'email': f'test{random_num}@example.com',
    'password': 'TestPassword123!',
    'password2': 'TestPassword123!',
    'first_name': 'Test',
    'last_name': 'User'
}

# Step 1: Register a new user
print("\n1. Registering a new user...")
try:
    register_response = requests.post(REGISTER_URL, data=user_data)
    print(f"Status Code: {register_response.status_code}")
    print(json.dumps(register_response.json(), indent=2))
except Exception as e:
    print(f"Error during registration: {str(e)}")

# Step 2: Login to get tokens
print("\n2. Logging in to get tokens...")
try:
    login_response = requests.post(LOGIN_URL, data={
        'email': user_data['email'],
        'password': user_data['password']
    })
    print(f"Status Code: {login_response.status_code}")
    login_data = login_response.json()
    print(json.dumps(login_data, indent=2))

    # Extract tokens
    if 'access' in login_data and 'refresh' in login_data:
        access_token = login_data['access']
        refresh_token = login_data['refresh']
    else:
        print("Error: Tokens not found in login response")
        exit()
except Exception as e:
    print(f"Error during login: {str(e)}")
    exit()

# Step 3: Access protected endpoint with token
print("\n3. Accessing protected endpoint with access token...")
try:
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    protected_response = requests.get(PROTECTED_URL, headers=headers)
    print(f"Status Code: {protected_response.status_code}")
    print(json.dumps(protected_response.json(), indent=2))
except Exception as e:
    print(f"Error accessing protected endpoint: {str(e)}")

# Step 4: Refresh the access token
print("\n4. Refreshing access token...")
try:
    refresh_response = requests.post(REFRESH_URL, data={
        'refresh': refresh_token
    })
    print(f"Status Code: {refresh_response.status_code}")
    refresh_data = refresh_response.json()
    print(json.dumps(refresh_data, indent=2))

    # Extract new access token
    if 'access' in refresh_data:
        new_access_token = refresh_data['access']
        print("Successfully obtained new access token")
    else:
        print("Error: New access token not found in refresh response")
except Exception as e:
    print(f"Error refreshing token: {str(e)}")

# Step 5: Access protected endpoint with the new access token
print("\n5. Accessing protected endpoint with new access token...")
try:
    headers = {
        'Authorization': f'Bearer {new_access_token}'
    }
    protected_response = requests.get(PROTECTED_URL, headers=headers)
    print(f"Status Code: {protected_response.status_code}")
    print(json.dumps(protected_response.json(), indent=2))
except Exception as e:
    print(f"Error accessing protected endpoint with new token: {str(e)}")

# Step 6: Logout (blacklist the refresh token)
print("\n6. Logging out (blacklisting the refresh token)...")
try:
    headers = {
        'Authorization': f'Bearer {new_access_token}'
    }
    logout_response = requests.post(LOGOUT_URL, headers=headers, data={
        'refresh': refresh_token
    })
    print(f"Status Code: {logout_response.status_code}")
    print(json.dumps(logout_response.json(), indent=2))
except Exception as e:
    print(f"Error during logout: {str(e)}")

# Step 7: Try to refresh token after logout (should fail)
print("\n7. Trying to refresh token after logout (should fail)...")
try:
    refresh_response = requests.post(REFRESH_URL, data={
        'refresh': refresh_token
    })
    print(f"Status Code: {refresh_response.status_code}")
    print(json.dumps(refresh_response.json(), indent=2))
except Exception as e:
    print(f"Error refreshing token after logout (expected): {str(e)}")

print("\nTest completed!")
