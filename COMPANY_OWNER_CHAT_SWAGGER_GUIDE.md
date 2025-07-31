# Company Owner and AppUser Chat System - Swagger Guide

This guide explains how to use the chat system between company owners (users assigned to a company) and regular app users through the Swagger UI.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Authentication](#authentication)
- [Company Owner Endpoints](#company-owner-endpoints)
- [Regular User Endpoints](#regular-user-endpoints)
- [Example Workflow](#example-workflow)

## Prerequisites

- Django server running (`python manage.py runserver`)
- Access to the Swagger UI (http://localhost:8000/swagger/)
- Company owner account (AppUser linked to a Company)
- Regular user account (AppUser not linked to any Company)

## Authentication

Before using any endpoints, you need to authenticate:

1. Click the "Authorize" button at the top of the Swagger UI
2. Choose "Bearer" authentication
3. Enter your JWT token or login credentials
4. Click "Authorize" and close the dialog

### Getting a Token

```
POST /api/auth/login/
```

Request body:
```json
{
  "email": "your_email@example.com",
  "password": "your_password"
}
```

Response:
```json
{
  "access": "your_jwt_token",
  "refresh": "your_refresh_token"
}
```

## Company Owner Endpoints

### List All Chats

As a company owner, view all chats for your company:

```
GET /company-chats/
```

Response:
```json
[
  {
    "id": 2,
    "user": {
      "id": 9,
      "email": "admin@gmail.com",
      "username": "admin"
    },
    "company": {
      "id": 1,
      "name": "Test Company"
    },
    "created_at": "2025-07-25T11:21:51.062670Z",
    "updated_at": "2025-07-31T18:11:38.648865Z",
    "is_active": true,
    "last_message": {
      "content": "Hello, thank you for your interest in our properties. How can I help you today?",
      "timestamp": "2025-07-31T18:11:38.622136Z",
      "sender_type": "company"
    },
    "unread_count": 2
  }
]
```

### View Specific Chat

Get details of a specific chat with all messages:

```
GET /company-chats/{id}/
```

Response:
```json
{
  "id": 2,
  "user": {
    "id": 9,
    "email": "admin@gmail.com",
    "username": "admin"
  },
  "messages": [
    {
      "id": 8,
      "content": "Hello, I'm interested in your Downtown Tower property.",
      "timestamp": "2025-07-25T11:21:51.062670Z",
      "sender_type": "user",
      "is_read": true
    },
    {
      "id": 13,
      "content": "Hello, thank you for your interest in our properties. How can I help you today?",
      "timestamp": "2025-07-31T18:11:38.622136Z",
      "sender_type": "company",
      "is_read": false
    }
  ],
  "company": {
    "id": 1,
    "name": "Test Company"
  }
}
```

### Send Message Reply

Send a message as a company owner:

```
POST /company-chats/{id}/reply/
```

Request body:
```json
{
  "content": "Thank you for your interest! Would you like to schedule a viewing?"
}
```

Response:
```json
{
  "message": {
    "id": 13,
    "chat": 2,
    "sender_type": "company",
    "content": "Thank you for your interest! Would you like to schedule a viewing?",
    "timestamp": "2025-07-31T18:11:38.622136Z",
    "is_read": false
  },
  "chat": {
    "id": 2,
    "user": 9,
    "user_email": "admin@gmail.com",
    "user_name": "admin",
    "created_at": "2025-07-25T11:21:51.062670Z",
    "updated_at": "2025-07-31T18:11:38.648865Z",
    "is_active": true,
    "last_message": {
      "content": "Hello, thank you for your interest in our properties...",
      "timestamp": "2025-07-31T18:11:38.622136Z",
      "sender_type": "company"
    },
    "unread_count": 2
  }
}
```

### Mark Messages as Read

Mark all user messages in a chat as read:

```
GET /company-chats/{id}/mark_as_read/
```

Response:
```json
{
  "messages_marked": 2
}
```

## Regular User Endpoints

### List All User Chats

As a regular user, view all your chats:

```
GET /chats/
```

### View Chat Messages

View messages in a specific chat:

```
GET /chats/{id}/messages/
```

### Start a Chat with a Company

Start a new chat with a company:

```
POST /chats/start/{company_id}/
```

Request body:
```json
{
  "content": "I'm interested in your Downtown Tower property."
}
```

### Send Message to Company

Send a follow-up message in an existing chat:

```
POST /chats/{id}/send_message/
```

Request body:
```json
{
  "content": "Yes, I would love to schedule a viewing. Is tomorrow at 2pm possible?"
}
```

## Example Workflow

### As a Regular User:

1. Authenticate with your user account
2. Start a chat with a company:
   ```
   POST /chats/start/1/
   ```
   With body:
   ```json
   {
     "content": "Hello, I'm interested in your Downtown Tower property."
   }
   ```
3. Note the returned `chat_id` for future reference

### As a Company Owner:

1. Authenticate with your company owner account
2. List all chats to find the new conversation:
   ```
   GET /company-chats/
   ```
3. View the specific chat:
   ```
   GET /company-chats/2/
   ```
4. Send a reply:
   ```
   POST /company-chats/2/reply/
   ```
   With body:
   ```json
   {
     "content": "Thank you for your interest! Would you like to schedule a viewing?"
   }
   ```
5. Mark messages as read:
   ```
   GET /company-chats/2/mark_as_read/
   ```

### Back as a Regular User:

1. Check for company replies:
   ```
   GET /chats/2/messages/
   ```
2. Send a response:
   ```
   POST /chats/2/send_message/
   ```
   With body:
   ```json
   {
     "content": "Yes, I would love to schedule a viewing. Is tomorrow at 2pm possible?"
   }
   ```

## Notes

- All endpoints require authentication
- Company owners can only access chats related to their company
- Regular users can only access their own chats
- Message timestamps are in UTC
- The `is_read` flag indicates if a message has been read by the recipient
- The `sender_type` can be either "user" or "company"
