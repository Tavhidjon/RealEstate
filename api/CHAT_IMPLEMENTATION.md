# Chat System Implementation Guide

This document explains how the chat system is implemented in the RealEstate project.

## Models

The chat system uses three models:

### 1. `Company` Model
- Represents real estate companies in the system
- Companies can be chatted with by users

### 2. `Chat` Model
- Represents a conversation between a user and a company
- Each chat is unique per user-company pair
- Tracks creation and update timestamps
- Has an active/inactive status

### 3. `Message` Model
- Represents individual messages within a chat
- Contains message content, timestamp, and read status
- Identifies sender type (user or company)

## How to Link Users with Companies

For company representatives to access and respond to chats, the system offers two options:

### Option 1: Direct Company Association (Recommended)
- Users have a `company` field that can link them to the company they represent
- If a user's `company` field is set, they can see all chats for that company

```python
# Example of assigning a user to a company
user = AppUser.objects.get(email='representative@company.com')
company = Company.objects.get(id=1)
user.company = company
user.save()
```

### Option 2: Group-based Access
- Users can be added to groups named with the format `company_{id}`
- Example: Adding a user to the group `company_1` gives them access to Company with ID 1

```python
# Example of using Django's group system
from django.contrib.auth.models import Group
user = AppUser.objects.get(email='representative@company.com')
company_group, _ = Group.objects.get_or_create(name='company_1')
user.groups.add(company_group)
```

## Authentication and Permission Checks

- All chat endpoints require authentication
- Users can only access their own chats
- Company representatives can only access chats for their assigned company

## API Endpoints

### User-Side Endpoints:
- `GET /chat/companies-list/` - View all companies available for chatting
- `POST /chats/` - Create a new chat with a company
- `GET /chats/{id}/messages/` - View all messages in a specific chat
- `POST /chats/{id}/send_message/` - Send a message in a chat
- `GET /chats/unread_count/` - Check unread messages count across all chats

### Company-Side Endpoints:
- `GET /company-chats/` - View all chats for a company
- `POST /company-chats/{id}/reply/` - Reply to a user message
- `GET /company-chats/{id}/mark_as_read/` - Mark all user messages as read

## Message Read Status

- Messages sent by users are marked as read when viewed by the company
- Messages sent by companies are marked as read when viewed by the user

## Extending the Chat System

To add real-time chat functionality, consider implementing WebSockets using Django Channels.

```python
# Simplified example of adding Django Channels
# 1. Install dependencies
# pip install channels

# 2. Update settings.py
INSTALLED_APPS = [
    # ... existing apps
    'channels',
]

ASGI_APPLICATION = 'server.asgi.application'

# 3. Implement consumers and routing
```
