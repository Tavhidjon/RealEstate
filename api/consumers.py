from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from .models import AppUser, Chat, Message


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        Validates the token and sets up channel groups.
        """
        # Get the user token from the query string
        self.token = self.scope["query_string"].decode("utf-8").split("=")[-1]
        self.user = await self.get_user_from_token(self.token)
        
        # If no user (invalid token), close connection
        if not self.user or isinstance(self.user, AnonymousUser):
            await self.close(code=4001)  # 4001: Authentication failed
            return
            
        # If a user is found, accept the connection
        await self.accept()
        
        # Add user to their personal channel group
        await self.channel_layer.group_add(
            f"user_{self.user.id}",
            self.channel_name
        )
        
        # If user is associated with a company, add to company channel group
        if hasattr(self.user, 'company') and self.user.company:
            await self.channel_layer.group_add(
                f"company_{self.user.company.id}",
                self.channel_name
            )
            
        # Check if the user is in any company groups (for representatives)
        company_groups = await database_sync_to_async(self.get_user_company_groups)(self.user)
        for company_id in company_groups:
            await self.channel_layer.group_add(
                f"company_{company_id}",
                self.channel_name
            )

    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        Remove user from channel groups.
        """
        if hasattr(self, 'user') and self.user and not isinstance(self.user, AnonymousUser):
            # Remove from user group
            await self.channel_layer.group_discard(
                f"user_{self.user.id}",
                self.channel_name
            )
            
            # Remove from company group if applicable
            if hasattr(self.user, 'company') and self.user.company:
                await self.channel_layer.group_discard(
                    f"company_{self.user.company.id}",
                    self.channel_name
                )
                
            # Remove from company groups from user's group memberships
            company_groups = await database_sync_to_async(self.get_user_company_groups)(self.user)
            for company_id in company_groups:
                await self.channel_layer.group_discard(
                    f"company_{company_id}",
                    self.channel_name
                )

    async def receive_json(self, content):
        """
        Called when a message is received from the client.
        """
        message_type = content.get('type')
        
        if message_type == 'chat.message':
            # Handle new message
            await self.handle_new_message(content)
        elif message_type == 'chat.read':
            # Handle marking messages as read
            await self.handle_read_messages(content)
        else:
            # Unknown message type
            await self.send_json({
                'type': 'error',
                'content': f"Unknown message type: {message_type}"
            })

    async def handle_new_message(self, content):
        """Handle a new message from client"""
        chat_id = content.get('chat_id')
        message_content = content.get('content')
        
        if not chat_id or not message_content:
            await self.send_json({
                'type': 'error',
                'content': "Missing chat_id or message content"
            })
            return
            
        # Determine sender type (user or company)
        sender_type = 'user'  # Default
        if (hasattr(self.user, 'company') and self.user.company) or \
           await database_sync_to_async(self.get_user_company_groups)(self.user):
            # Check if user has permission to send as company for this chat
            chat = await self.get_chat(chat_id)
            if chat and (self.user.is_superuser or 
                       (hasattr(self.user, 'company') and self.user.company == chat.company) or
                       self.user.groups.filter(name=f'company_{chat.company.id}').exists()):
                sender_type = 'company'
                
        # Create the message in database
        message = await self.create_message(
            chat_id=chat_id,
            sender_type=sender_type,
            content=message_content
        )
        
        if not message:
            await self.send_json({
                'type': 'error',
                'content': "Failed to create message"
            })
            return
            
        # Get serialized message data
        message_data = await self.get_message_data(message)
        
        # Broadcast message to appropriate groups
        chat = await self.get_chat(chat_id)
        if chat:
            # Send to user's channel
            await self.channel_layer.group_send(
                f"user_{chat.user.id}",
                {
                    "type": "chat.message",
                    "message": message_data
                }
            )
            
            # Send to company's channel
            await self.channel_layer.group_send(
                f"company_{chat.company.id}",
                {
                    "type": "chat.message",
                    "message": message_data
                }
            )

    async def handle_read_messages(self, content):
        """Mark messages as read"""
        chat_id = content.get('chat_id')
        sender_type = content.get('sender_type')
        
        if not chat_id or not sender_type:
            await self.send_json({
                'type': 'error',
                'content': "Missing chat_id or sender_type"
            })
            return
            
        # Mark messages as read
        updated_count = await self.mark_messages_as_read(chat_id, sender_type)
        
        # Acknowledge the operation
        await self.send_json({
            'type': 'chat.read.confirmed',
            'chat_id': chat_id,
            'updated_count': updated_count
        })
        
        # Notify other clients about read status change
        chat = await self.get_chat(chat_id)
        if chat:
            notification = {
                "type": "chat.read.updated",
                "chat_id": chat_id,
                "updated_by": self.user.id,
                "sender_type": sender_type
            }
            
            # Send to user's channel
            await self.channel_layer.group_send(
                f"user_{chat.user.id}",
                notification
            )
            
            # Send to company's channel
            await self.channel_layer.group_send(
                f"company_{chat.company.id}",
                notification
            )

    async def chat_message(self, event):
        """
        Called when a message is broadcast to a group this consumer is in.
        Forward the message to the client.
        """
        await self.send_json(event)

    async def chat_read_updated(self, event):
        """
        Called when read status is updated and broadcast to a group.
        Forward the notification to the client.
        """
        await self.send_json(event)
        
    @database_sync_to_async
    def get_user_from_token(self, token_str):
        """Validate JWT token and return user"""
        if not token_str:
            return AnonymousUser()
            
        try:
            # Validate the token
            token = AccessToken(token_str)
            user_id = token.payload.get('user_id')
            
            # Get the user from the ID in token payload
            if user_id:
                return AppUser.objects.get(id=user_id)
                
        except (TokenError, AppUser.DoesNotExist):
            pass
            
        return AnonymousUser()
        
    def get_user_company_groups(self, user):
        """Return company IDs from user group memberships"""
        company_ids = []
        for group in user.groups.filter(name__startswith='company_'):
            try:
                company_id = int(group.name.replace('company_', ''))
                company_ids.append(company_id)
            except ValueError:
                continue
                
        return company_ids

    @database_sync_to_async
    def get_chat(self, chat_id):
        """Get chat by ID"""
        try:
            return Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return None
    
    @database_sync_to_async
    def create_message(self, chat_id, sender_type, content):
        """Create a new message in the database"""
        try:
            chat = Chat.objects.get(id=chat_id)
            
            # Only proceed if chat is active
            if not chat.is_active:
                return None
                
            # Create message
            message = Message.objects.create(
                chat=chat,
                sender_type=sender_type,
                content=content,
                is_read=False
            )
            
            # Update chat's updated_at timestamp
            chat.updated_at = timezone.now()
            chat.save()
            
            return message
            
        except Chat.DoesNotExist:
            return None
    
    @database_sync_to_async
    def get_message_data(self, message):
        """Convert message object to dictionary for JSON response"""
        return {
            'id': message.id,
            'chat_id': message.chat_id,
            'sender_type': message.sender_type,
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'is_read': message.is_read
        }
    
    @database_sync_to_async
    def mark_messages_as_read(self, chat_id, sender_type):
        """Mark messages of the specified sender_type in the chat as read"""
        try:
            chat = Chat.objects.get(id=chat_id)
            
            # Filter messages by sender_type and update
            unread_messages = Message.objects.filter(
                chat=chat,
                sender_type=sender_type,
                is_read=False
            )
            
            count = unread_messages.count()
            unread_messages.update(is_read=True)
            
            return count
            
        except Chat.DoesNotExist:
            return 0
