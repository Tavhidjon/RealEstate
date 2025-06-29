#!/usr/bin/env python
"""
Test script to verify registration and login functionality.
Run this script from the command line to test the API endpoints.
"""
import requests
import json
import sys

BASE_URL = 'http://localhost:8000/api/'

def register_user():
    """Test registering a new user"""
    url = f"{BASE_URL}auth/register/"
    data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "ComplexPass123!",
        "password2": "ComplexPass123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    print(f"Attempting to register user at {url}")
    response = requests.post(url, json=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("✅ Registration successful!")
        return True
    else:
        print("❌ Registration failed!")
        return False

def login_user():
    """Test logging in with the registered user"""
    url = f"{BASE_URL}auth/login/"
    data = {
        "email": "testuser@example.com",
        "password": "ComplexPass123!"
    }
    
    print(f"Attempting to login at {url}")
    response = requests.post(url, json=data)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Login successful!")
        token_data = response.json()
        print(f"Access Token: {token_data.get('access')[:20]}...")
        print(f"Refresh Token: {token_data.get('refresh')[:20]}...")
        return token_data
    else:
        print("❌ Login failed!")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return None

if __name__ == "__main__":
    print("=== API Authentication Test ===")
    
    if len(sys.argv) > 1 and sys.argv[1] == "register":
        register_user()
    elif len(sys.argv) > 1 and sys.argv[1] == "login":
        login_user()
    else:
        print("Testing registration and login...")
        if register_user():
            print("\n")
            login_user()
