"""
Test script to create a company and chat for testing.
"""

import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

# Import models
from api.models import Company, AppUser, Chat, Message

# Get the admin user
try:
    admin = AppUser.objects.filter(is_superuser=True).first()
    if not admin:
        print("No admin user found. Please create an admin user first.")
        exit(1)
    
    print(f"Found admin user: {admin.username} ({admin.email})")
    
    # Create a test company if it doesn't exist
    company_name = "Test Company"
    company, created = Company.objects.get_or_create(
        name=company_name,
        defaults={'description': 'A company for testing the chat functionality'}
    )
    
    if created:
        print(f"Created new company: {company.name} (ID: {company.id})")
    else:
        print(f"Using existing company: {company.name} (ID: {company.id})")
    
    # Create a chat between admin and company
    chat, created = Chat.objects.get_or_create(
        user=admin,
        company=company,
        defaults={'is_active': True}
    )
    
    if created:
        print(f"Created new chat with ID: {chat.id}")
    else:
        print(f"Using existing chat with ID: {chat.id}")
    
    # Create a test message
    message = Message.objects.create(
        chat=chat,
        sender_type='user',
        content='This is a test message from script.',
        is_read=False
    )
    print(f"Created test message: '{message.content}'")
    
    print("\nTEST INFORMATION:")
    print("=================")
    print(f"Company ID: {company.id}")
    print(f"Chat ID: {chat.id}")
    print(f"User ID: {admin.id}")
    print(f"Message ID: {message.id}")
    print("\nTo send a message, use this endpoint:")
    print(f"POST /api/chats/{chat.id}/send_message/")
    print('With JSON body: {"content": "Your message here"}')
    print("\nTo check messages, use:")
    print(f"GET /api/chats/{chat.id}/messages/")
    
except Exception as e:
    print(f"An error occurred: {str(e)}")
