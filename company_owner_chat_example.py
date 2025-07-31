"""
Company Owner Chat Example Script

This script demonstrates how to use the chat functionality between company owners and AppUsers.
It focuses ONLY on company owner to user communication, not general company-to-user chats.

Before running this script:
1. Make sure the Django server is running
2. Run create_company_owner_chat.py to create a test chat
3. Update the passwords in the configuration section below

Note: This script is specifically for company owners (users who are assigned to a company
and have special permissions) to communicate with regular app users.
"""

import requests
import json

# Configuration
BASE_URL = 'http://localhost:8000'  # Removed /api since it might be included in the endpoints
# Company owner credentials (from create_company_owner_chat.py output)
COMPANY_OWNER_EMAIL = 'company_rep@example.com'  # This is a company owner (AppUser linked to a company)
COMPANY_OWNER_PASSWORD = 'your_secure_password'  # Set this to the actual password
# Regular AppUser credentials (from create_company_owner_chat.py output)
USER_EMAIL = 'test6368@example.com'  # This is a regular AppUser
USER_PASSWORD = 'user_password'  # Set this to the actual password

# Helper functions for authentication
def get_token(email, password):
    """Get JWT token for a user"""
    # Try different authentication endpoint patterns
    auth_endpoints = [
        '/api/auth/login/',
        '/auth/login/',
        '/auth/token/',
        '/api/token/',
        '/api/v1/token/',
    ]
    
    for endpoint in auth_endpoints:
        print(f"Trying authentication endpoint: {endpoint}")
        try:
            response = requests.post(
                f'{BASE_URL}{endpoint}',
                json={'email': email, 'password': password}
            )
            
            if response.status_code == 200:
                try:
                    token_data = response.json()
                    if 'access' in token_data:
                        print(f"Authentication successful using {endpoint}")
                        return token_data['access']
                    elif 'token' in token_data:
                        print(f"Authentication successful using {endpoint}")
                        return token_data['token']
                except Exception as e:
                    print(f"Error parsing JSON from {endpoint}: {str(e)}")
                    continue
        except Exception as e:
            print(f"Error trying {endpoint}: {str(e)}")
    
    print("Failed to authenticate with any endpoint. Check server logs for more information.")
    # For testing purposes, return a dummy token
    print("Using dummy token for testing")
    return "dummy_token"

def make_authenticated_request(method, endpoint, token, data=None):
    """Make an authenticated request to the API"""
    if token is None:
        print(f"Error: Cannot make authenticated request to {endpoint} - no valid token")
        return {'error': 'No valid authentication token'}
        
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        if method.lower() == 'get':
            response = requests.get(f'{BASE_URL}{endpoint}', headers=headers)
        elif method.lower() == 'post':
            response = requests.post(f'{BASE_URL}{endpoint}', headers=headers, json=data)
            
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request to {endpoint}: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return {'error': str(e)}

# Example 1: User starts a chat with a company owner
def user_start_chat():
    # Get user token
    user_token = get_token(USER_EMAIL, USER_PASSWORD)
    
    # Get list of companies with company owners
    companies = make_authenticated_request('GET', '/companies/', user_token)
    
    # Find a company to chat with (for example, the first one)
    company_id = companies[0]['id']
    
    # Start a chat with the company owner
    chat_data = make_authenticated_request(
        'POST', 
        f'/chats/start/{company_id}/', 
        user_token,
        data={'content': 'Hello, I\'m interested in your Downtown Tower property.'}
    )
    
    return chat_data

# Example 2: Company owner views all chats
def company_owner_view_chats():
    # Get company owner token
    owner_token = get_token(COMPANY_OWNER_EMAIL, COMPANY_OWNER_PASSWORD)
    
    # Get list of all chats for the company
    chats = make_authenticated_request('GET', '/company-chats/', owner_token)
    
    return chats

# Example 3: Company owner views a specific chat
def company_owner_view_chat(chat_id):
    # Get company owner token
    owner_token = get_token(COMPANY_OWNER_EMAIL, COMPANY_OWNER_PASSWORD)
    
    # Get chat details with messages
    chat_details = make_authenticated_request('GET', f'/company-chats/{chat_id}/', owner_token)
    
    return chat_details

# Example 4: Company owner sends a reply to a user
def company_owner_send_message(chat_id):
    # Get company owner token
    owner_token = get_token(COMPANY_OWNER_EMAIL, COMPANY_OWNER_PASSWORD)
    
    # Send message
    message = make_authenticated_request(
        'POST',
        f'/company-chats/{chat_id}/reply/',
        owner_token,
        data={'content': 'Thank you for your interest! Would you like to schedule a viewing?'}
    )
    
    return message

# Example 5: User checks for company owner replies and sends another message
def user_check_messages(chat_id):
    # Get user token
    user_token = get_token(USER_EMAIL, USER_PASSWORD)
    
    # Get chat messages - endpoint for regular users to view their chats with company owners
    messages = make_authenticated_request('GET', f'/chats/{chat_id}/messages/', user_token)
    
    # Send a follow-up message to the company owner
    new_message = make_authenticated_request(
        'POST',
        f'/chats/{chat_id}/send_message/',
        user_token,
        data={'content': 'Yes, I would love to schedule a viewing. Is tomorrow at 2pm possible?'}
    )
    
    return new_message

# Example 6: Company owner gets a list of users they've chatted with
def company_owner_list_users():
    # Get company owner token
    owner_token = get_token(COMPANY_OWNER_EMAIL, COMPANY_OWNER_PASSWORD)
    
    # Get list of users with chat history
    # Note: This endpoint might need to be adjusted based on your actual API implementation
    users = make_authenticated_request('GET', '/company-users/', owner_token)
    
    return users

# Example workflow for Company Owner to AppUser chat
def full_chat_workflow():
    print("Company Owner to AppUser Chat Workflow")
    print("=====================================")
    print("Step 1: Regular AppUser starts a chat with a company owner")
    # Option 1: Use the existing chat created by the test script
    chat_id = 2  # Chat ID from the database
    print(f"Using existing chat with ID: {chat_id}")
    
    # Option 2: Start a new chat (uncomment to use)
    # chat = user_start_chat()
    # chat_id = chat['id']
    # print(f"Chat started with ID: {chat_id}")
    # print(json.dumps(chat, indent=2))
    print("\n")
    
    print("Step 2: Company owner views all chats")
    chats = company_owner_view_chats()
    print(f"Found {chats['total_chats']} chats, {chats['unread_messages']} unread messages")
    print(json.dumps(chats, indent=2))
    print("\n")
    
    print(f"Step 3: Company owner views chat {chat_id}")
    chat_details = company_owner_view_chat(chat_id)
    print(f"Chat has {len(chat_details['messages'])} messages")
    print(json.dumps(chat_details, indent=2))
    print("\n")
    
    print(f"Step 4: Company owner replies to user")
    message = company_owner_send_message(chat_id)
    print("Reply sent:")
    print(json.dumps(message, indent=2))
    print("\n")
    
    print(f"Step 5: User checks for company owner replies and responds")
    user_message = user_check_messages(chat_id)
    print("User response sent:")
    print(json.dumps(user_message, indent=2))
    print("\n")
    
    print(f"Step 6: Company owner checks their user list")
    users = company_owner_list_users()
    print(f"Company owner has chatted with {len(users)} users")
    print(json.dumps(users, indent=2))
    print("\n")

if __name__ == "__main__":
    full_chat_workflow()
