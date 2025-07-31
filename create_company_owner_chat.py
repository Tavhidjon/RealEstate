"""
Test script to create a chat between a company owner and a regular user.
This demonstrates the company owner chat functionality.
"""

import os
import django
import random
from django.utils import timezone

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

# Import models after Django setup
from api.models import AppUser, Company, Chat, Message

def create_company_owner_chat():
    """
    Create a test chat between a company owner and a regular user.
    This script demonstrates how company owners can interact with chats.
    """
    print("Creating test chat for company owner...")
    
    try:
        # Find a company owner (user with a company)
        company_owners = AppUser.objects.filter(company__isnull=False)
        if not company_owners.exists():
            print("No company owners found. Please create a company owner first.")
            return
        
        company_owner = company_owners.first()
        company = company_owner.company
        
        # Find a regular user (user without a company, not a staff)
        regular_users = AppUser.objects.filter(company__isnull=True, is_staff=False)
        if not regular_users.exists():
            print("No regular users found. Please create a regular user first.")
            return
        
        regular_user = random.choice(regular_users)
        
        print(f"Selected company owner: {company_owner.email} (Company: {company.name})")
        print(f"Selected regular user: {regular_user.email}")
        
        # Create or get a chat between the user and company
        chat, created = Chat.objects.get_or_create(
            user=regular_user,
            company=company,
            defaults={'is_active': True}
        )
        
        if created:
            print(f"Created new chat with ID: {chat.id}")
        else:
            print(f"Found existing chat with ID: {chat.id}")
            
        # Create some messages
        messages = [
            # User starts the conversation
            Message(
                chat=chat,
                sender_type='user',
                content="Hello, I'm interested in your property at 123 Main Street. Is it still available?",
                timestamp=timezone.now() - timezone.timedelta(days=1, hours=2),
                is_read=True
            ),
            
            # Company replies
            Message(
                chat=chat,
                sender_type='company',
                content="Hi there! Yes, the property at 123 Main Street is still available. Would you like to schedule a viewing?",
                timestamp=timezone.now() - timezone.timedelta(days=1, hours=1),
                is_read=True
            ),
            
            # User responds
            Message(
                chat=chat,
                sender_type='user',
                content="Great! I'd love to see it. What times do you have available this week?",
                timestamp=timezone.now() - timezone.timedelta(hours=20),
                is_read=True
            ),
            
            # Company responds
            Message(
                chat=chat,
                sender_type='company',
                content="We have slots available on Thursday at 3pm and Friday at 10am. Which would work better for you?",
                timestamp=timezone.now() - timezone.timedelta(hours=19),
                is_read=True
            ),
            
            # User's most recent message - unread
            Message(
                chat=chat,
                sender_type='user',
                content="Friday at 10am works perfectly for me. Can you confirm the address again and let me know if there's parking available nearby?",
                timestamp=timezone.now() - timezone.timedelta(hours=2),
                is_read=False
            ),
        ]
        
        # Save all messages
        for message in messages:
            message.save()
            
        # Update chat timestamp
        chat.updated_at = timezone.now() - timezone.timedelta(hours=2)
        chat.save()
        
        print(f"Created {len(messages)} messages in the chat")
        print("Test chat created successfully!")
        print("\nNow you can test the company owner chat functionality:")
        print("====================================================")
        print(f"1. Log in as the company owner: {company_owner.email}")
        print(f"2. Access the company owner chat endpoints:")
        print(f"   - GET /api/company/chats/ - List all chats for this company")
        print(f"   - GET /api/company/chats/{chat.id}/ - View this specific chat")
        print(f"   - POST /api/company/chats/{chat.id}/send/ - Send a message to {regular_user.email}")
        print(f"      JSON Body: {{\"content\": \"Your message here\"}}")
        print("\nThe most recent message from the user is unread. The company owner should see this as a new message.")
        
    except Exception as e:
        print(f"Error creating company owner chat: {str(e)}")
        
if __name__ == "__main__":
    create_company_owner_chat()
