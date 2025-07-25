# Chat System API Documentation

This document provides an overview of the chat functionality in the RealEstate application, including examples of how to use each endpoint.

## Overview

The chat system allows users to communicate with property companies. Users can:
- View a list of companies they can chat with
- Create new chats with companies
- Send messages to companies
- View their message history
- Check for unread messages

Company representatives can:
- View all chats for their company
- Reply to user messages

## API Endpoints

### User-Side Endpoints

#### 1. View Companies List
Get a list of all companies the user can chat with.

```
GET /chat/companies-list/
```

**Example Response:**
```json
[
  {
    "id": 1,
    "name": "Acme Properties",
    "description": "Leading real estate developer"
  }
]
```

#### 2. Create a New Chat
Start a new chat with a company.

```
POST /chats/
```

**Request Body:**
```json
{
  "company": 1
}
```

**Example Response:**
```json
{
  "id": 1,
  "company": 1,
  "company_name": "Acme Properties",
  "created_at": "2025-07-23T11:30:00Z",
  "updated_at": "2025-07-23T11:30:00Z",
  "is_active": true,
  "last_message": null,
  "unread_count": 0
}
```

#### 3. Send a Message in a Chat
Send a new message in an existing chat.

```
POST /chats/{id}/send_message/
```

**Request Body:**
```json
{
  "content": "Hello! I'm interested in your property."
}
```

**Example Response:**
```json
{
  "id": 1,
  "chat": 1,
  "sender_type": "user",
  "content": "Hello! I'm interested in your property.",
  "timestamp": "2025-07-23T11:44:41.063829Z",
  "is_read": false
}
```

#### 4. View Messages in a Chat
Get all messages in a specific chat.

```
GET /chats/{id}/messages/
```

**Example Response:**
```json
[
  {
    "id": 1,
    "chat": 1,
    "sender_type": "user",
    "content": "Hello! I'm interested in your property.",
    "timestamp": "2025-07-23T11:44:41.063829Z",
    "is_read": false
  },
  {
    "id": 2,
    "chat": 1,
    "sender_type": "company",
    "content": "Thank you for your interest! Which property are you looking at?",
    "timestamp": "2025-07-23T12:00:00Z",
    "is_read": true
  }
]
```

#### 5. Check Unread Messages Count
Get the count of unread messages across all chats.

```
GET /chats/unread_count/



```
**Example Response:**
```json
[
  {
    "id": 1,
    "company__name": "Acme Properties",
    "unread": 1
  },
  {
    "id": 2,
    "company__name": "City Developments",
    "unread": 0
  }
]
```

### Company-Side Endpoints

#### 1. View Company Chats
View all chats for a company (for company representatives).

```
GET /company-chats/
```

**Example Response:**
```json
[
  {
    "id": 1,
    "user": 3,
    "company": 1,
    "company_name": "Acme Properties",
    "created_at": "2025-07-23T11:30:00Z",
    "updated_at": "2025-07-23T11:44:41Z",
    "is_active": true,
    "last_message": {
      "content": "Hello! I'm interested in your property.",
      "timestamp": "2025-07-23T11:44:41Z",
      "sender_type": "user"
    },
    "unread_count": 1
  }
]
```

#### 2. Reply to a User Message
Send a reply from the company to a user.

```
POST /company-chats/{id}/reply/
```

**Request Body:**
```json
{
  "content": "Thank you for your interest! Which property are you looking at?"
}
```

**Example Response:**
```json
{
  "id": 2,
  "chat": 1,
  "sender_type": "company",
  "content": "Thank you for your interest! Which property are you looking at?",
  "timestamp": "2025-07-23T12:00:00Z",
  "is_read": false
}
```

## Testing the API with Swagger UI

You can test all these endpoints using the Swagger UI at:
```
http://127.0.0.1:8000/swagger/
```

Follow these steps to test the complete chat flow:

1. Login as an admin/user
2. View companies list: GET `/chat/companies-list/`
3. Create a new chat: POST `/chats/` with company ID
4. Send a message: POST `/chats/{id}/send_message/` with content
5. View messages: GET `/chats/{id}/messages/`
6. Check unread messages: GET `/chats/unread_count/`
7. Test company-side: GET `/company-chats/`
8. Reply as company: POST `/company-chats/{id}/reply/` with content

## Authentication

All chat endpoints require authentication. You need to be logged in to use these endpoints.

### JWT Token Configuration

The application uses JWT (JSON Web Tokens) for authentication with the following settings:
- Access Token lifetime: 7 days
- Refresh Token lifetime: 30 days

This extended duration means users can remain authenticated for longer periods without needing to log in frequently.

## Models

The chat system uses the following models:

- `Chat`: Represents a conversation between a user and a company
- `Message`: Represents individual messages within a chat

A chat is unique per user-company pair, and messages belong to a specific chat.
