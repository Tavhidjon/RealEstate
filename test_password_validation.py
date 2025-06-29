import requests
import json
import time

# Wait for server to start
time.sleep(2)

print("Testing registration with short password...")

# Test registration with a short password that would fail previous validation
test_user_data = {
    "username": "testuser123",
    "email": "testuser123@example.com",
    "password": "123",  # Short password that would normally fail validation
    "password2": "123",
    "first_name": "Test",
    "last_name": "User"
}

# Send registration request
response = requests.post('http://localhost:8000/api/auth/register/', json=test_user_data)
print("Status Code:", response.status_code)
print("Response:", json.dumps(response.json(), indent=4))

# If registration is successful, try to login with the credentials
if response.status_code == 201:
    print("\nTesting login with the new user...")
    login_data = {
        "email": "testuser123@example.com",
        "password": "123"
    }
    
    login_response = requests.post('http://localhost:8000/api/auth/login/', json=login_data)
    print("Login Status Code:", login_response.status_code)
    if login_response.status_code == 200:
        print("Login successful! Token:", login_response.json().get('access', ''))
    else:
        print("Login Response:", json.dumps(login_response.json(), indent=4))
