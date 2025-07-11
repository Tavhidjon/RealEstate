"""
Example code showing how to use the Chat API endpoints in a client application.

This is for reference only - it's not part of the Django backend.
"""

# Example flow for a user interacting with the chat system:

# 1. User views the list of companies they can chat with
# GET /api/chat/companies-list/
# Response:
# [
#   {
#     "id": 1,
#     "name": "Acme Properties",
#     "description": "Leading real estate developer"
#   },
#   ...
# ]

# 2. User creates a new chat with a company
#POST /api/chats/
# Request body:
# {
#   "company": 1
# }
# Response:
# {
#   "id": 5,
#   "company": 1,
#   "company_name": "Acme Properties",
#   "created_at": "2025-07-11T14:30:00Z",
#   "updated_at": "2025-07-11T14:30:00Z",
#   "is_active": true,
#   "last_message": null,
#   "unread_count": 0
# }

# 3. User sends a message in the chat
#POST /api/chats/5/send_message/
# Request body:
# {
#   "content": "Hello! I'm interested in your property on Main Street."
# }
# Response:
# {
#   "id": 10,
#   "chat": 5,
#   "sender_type": "user",
#   "content": "Hello! I'm interested in your property on Main Street.",
#   "timestamp": "2025-07-11T14:31:00Z",
#   "is_read": false
# }

# 4. User views messages in the chat
#GET /api/chats/5/messages/
# Response:
# [
#   {
#     "id": 10,
#     "chat": 5,
#     "sender_type": "user",
#     "content": "Hello! I'm interested in your property on Main Street.",
#     "timestamp": "2025-07-11T14:31:00Z",
#     "is_read": false
#   },
#   {
#     "id": 11,
#     "chat": 5,
#     "sender_type": "company",
#     "content": "Thank you for your interest! Which property are you referring to?",
#     "timestamp": "2025-07-11T14:35:00Z",
#     "is_read": true  # Marked as read when user views the messages
#   }
# ]

# 5. User checks for unread messages across all chats
#GET /api/chats/unread_count/
# Response:
# [
#   {
#     "id": 5,
#     "company__name": "Acme Properties",
#     "unread": 1
#   },
#   {
#     "id": 6,
#     "company__name": "City Developments",
#     "unread": 0
#   }
# ]

# --------
# Company side (for company representatives)
# --------

# 1. Company rep views all chats for their company
#GET /api/company-chats/
# Response:
# [
#   {
#     "id": 5,
#     "user": 3,
#     "company": 1,
#     "company_name": "Acme Properties",
#     "created_at": "2025-07-11T14:30:00Z", 
#     "updated_at": "2025-07-11T14:35:00Z",
#     "is_active": true,
#     "last_message": {
#       "content": "Hello! I'm interested in your property on Main Street.",
#       "timestamp": "2025-07-11T14:31:00Z",
#       "sender_type": "user"
#     },
#     "unread_count": 1
#   },
#   ...
# ]

# 2. Company rep replies to a user's message
#POST /api/company-chats/5/reply/
# Request body:
# {
#   "content": "Thank you for your interest! Which property are you referring to?"
# }
# Response:
# {
#   "id": 11,
#   "chat": 5,
#   "sender_type": "company",
#   "content": "Thank you for your interest! Which property are you referring to?",
#   "timestamp": "2025-07-11T14:35:00Z",
#   "is_read": false
# }
