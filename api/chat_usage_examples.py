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
#     "description": "Leading real estate developer",
#     "has_chat": false,
#     "chat_id": null,
#     "unread_count": 0
#   },
#   {
#     "id": 2,
#     "name": "City Developments",
#     "description": "Urban property specialists",
#     "has_chat": true,
#     "chat_id": 3,
#     "unread_count": 2
#   },
#   ...
# ]

# 2. User starts a new chat with a company (NEW ENDPOINT)
# POST /api/chats/start/1/
# Request body (optional initial message):
# {
#   "content": "Hello! I'm interested in your properties."
# }
# Response:
# {
#   "id": 5,
#   "user": 3,
#   "company": 1,
#   "company_name": "Acme Properties",
#   "created_at": "2025-07-11T14:30:00Z",
#   "updated_at": "2025-07-11T14:30:00Z",
#   "is_active": true,
#   "last_message": {
#     "content": "Hello! I'm interested in your properties.",
#     "timestamp": "2025-07-11T14:30:00Z",
#     "sender_type": "user"
#   },
#   "unread_count": 0,
#   "initial_message": {
#     "id": 10,
#     "chat": 5,
#     "sender_type": "user",
#     "content": "Hello! I'm interested in your properties.",
#     "timestamp": "2025-07-11T14:30:00Z",
#     "is_read": false
#   }
# }

# 3. User sends a message in the chat
# POST /api/chats/5/send_message/
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
# GET /api/chats/5/messages/
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

# 2. Company rep replies to a user's message (ENHANCED RESPONSE)
# POST /api/company-chats/5/reply/
# Request body:
# {
#   "content": "Thank you for your interest! Which property are you referring to?"
# }
# Response:
# {
#   "message": {
#     "id": 11,
#     "chat": 5,
#     "sender_type": "company",
#     "content": "Thank you for your interest! Which property are you referring to?",
#     "timestamp": "2025-07-11T14:35:00Z",
#     "is_read": false
#   },
#   "chat": {
#     "id": 5,
#     "user": 3,
#     "user_email": "john@example.com",
#     "user_name": "John Smith",
#     "created_at": "2025-07-11T14:30:00Z",
#     "updated_at": "2025-07-11T14:35:00Z",
#     "is_active": true,
#     "last_message": {
#       "content": "Thank you for your interest! Which property are you referring to?",
#       "timestamp": "2025-07-11T14:35:00Z",
#       "sender_type": "company"
#     },
#     "unread_count": 0
#   }
# }

# 3. Company rep marks all user messages as read
# GET /api/company-chats/5/mark_as_read/
# Response:
# {
#   "success": true,
#   "messages_marked_read": 1
# }

# --------
# Flutter Code Examples
# --------

'''
// Example 1: Starting a chat with a company
Future<void> startChat(int companyId, {String? initialMessage}) async {
  final url = Uri.parse('$baseUrl/api/chats/start/$companyId/');
  
  Map<String, dynamic> body = {};
  if (initialMessage != null && initialMessage.isNotEmpty) {
    body['content'] = initialMessage;
  }
  
  final response = await http.post(
    url,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $accessToken',
    },
    body: jsonEncode(body),
  );
  
  if (response.statusCode == 200 || response.statusCode == 201) {
    // Chat successfully started
    final chatData = jsonDecode(response.body);
    // Handle the chatData...
    print('Chat started with ID: ${chatData['id']}');
    
    // If there was an initial message
    if (chatData.containsKey('initial_message')) {
      print('Initial message sent: ${chatData['initial_message']['content']}');
    }
  } else {
    // Handle error
    print('Failed to start chat: ${response.body}');
  }
}

// Example 2: Sending a user message in a chat
Future<void> sendMessage(int chatId, String content) async {
  final url = Uri.parse('$baseUrl/api/chats/$chatId/send_message/');
  
  final response = await http.post(
    url,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $accessToken',
    },
    body: jsonEncode({
      'content': content,
    }),
  );
  
  if (response.statusCode == 201) {
    // Message successfully sent
    final messageData = jsonDecode(response.body);
    print('Message sent with ID: ${messageData['id']}');
  } else {
    // Handle error
    print('Failed to send message: ${response.body}');
  }
}

// Example 3: Sending a company reply
Future<void> sendCompanyReply(int chatId, String content) async {
  final url = Uri.parse('$baseUrl/api/company-chats/$chatId/reply/');
  
  final response = await http.post(
    url,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $accessToken',
    },
    body: jsonEncode({
      'content': content,
    }),
  );
  
  if (response.statusCode == 201) {
    // Reply successfully sent
    final responseData = jsonDecode(response.body);
    print('Reply sent with ID: ${responseData['message']['id']}');
    print('Updated chat: ${responseData['chat']['id']}');
    print('Unread count: ${responseData['chat']['unread_count']}');
  } else {
    // Handle error
    print('Failed to send reply: ${response.body}');
  }
}

// Example 4: WebSocket connection for real-time messaging
void connectToWebSocket() {
  final wsUrl = Uri.parse('ws://$baseUrl/ws/chat/?token=$accessToken');
  final channel = WebSocketChannel.connect(wsUrl);
  
  // Listen for incoming messages
  channel.stream.listen((message) {
    final data = jsonDecode(message);
    
    switch (data['type']) {
      case 'chat.message':
        print('New message received: ${data['message']['content']}');
        // Handle new message (update UI, etc.)
        break;
      case 'chat.read.updated':
        print('Messages marked as read in chat: ${data['chat_id']}');
        // Update read status in UI
        break;
      case 'error':
        print('Error: ${data['content']}');
        break;
    }
  }, 
  onError: (error) {
    print('WebSocket error: $error');
    // Attempt to reconnect
  },
  onDone: () {
    print('WebSocket connection closed');
    // Attempt to reconnect
  });
  
  // Send a message
  void sendWebSocketMessage(int chatId, String content) {
    channel.sink.add(jsonEncode({
      'type': 'chat.message',
      'chat_id': chatId,
      'content': content
    }));
  }
  
  // Mark messages as read
  void markMessagesAsRead(int chatId, String senderType) {
    channel.sink.add(jsonEncode({
      'type': 'chat.read',
      'chat_id': chatId,
      'sender_type': senderType
    }));
  }
  
  // Close the WebSocket when done
  void closeWebSocket() {
    channel.sink.close();
  }
}
'''
