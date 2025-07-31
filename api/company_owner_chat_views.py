from rest_framework import generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Q
from django.utils import timezone

from .models import Chat, Message, Company, AppUser
from .chat_serializers import ChatSerializer, MessageSerializer, CompanyChatSerializer
from .permissions import IsOwnerOrAdmin

class CompanyOwnerChatListView(generics.ListAPIView):
    """
    List all chats for the company owner's company.
    Only accessible by users who have a company associated with their account.
    """
    serializer_class = CompanyChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Check if user is a company owner
        if not hasattr(user, 'company') or not user.company:
            return Chat.objects.none()
        
        # Return all chats for the user's company
        return Chat.objects.filter(company=user.company).order_by('-updated_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Add additional statistics
        total_chats = queryset.count()
        active_chats = queryset.filter(is_active=True).count()
        unread_messages = Message.objects.filter(
            chat__in=queryset,
            sender_type='user',
            is_read=False
        ).count()
        
        return Response({
            'chats': serializer.data,
            'total_chats': total_chats,
            'active_chats': active_chats,
            'unread_messages': unread_messages
        })

class CompanyOwnerChatDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific chat for the company owner.
    """
    serializer_class = CompanyChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Check if user is a company owner
        if not hasattr(user, 'company') or not user.company:
            return Chat.objects.none()
        
        # Return the chat only if it belongs to the user's company
        return Chat.objects.filter(company=user.company)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Get messages for this chat
        messages = Message.objects.filter(chat=instance).order_by('timestamp')
        message_serializer = MessageSerializer(messages, many=True)
        
        # Mark messages from user as read
        unread_count = messages.filter(sender_type='user', is_read=False).update(is_read=True)
        
        return Response({
            'chat': serializer.data,
            'messages': message_serializer.data,
            'messages_marked_read': unread_count
        })

class CompanyOwnerSendMessageView(APIView):
    """
    Send a message from the company owner to a user.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, chat_id):
        user = request.user
        
        # Check if user is a company owner
        if not hasattr(user, 'company') or not user.company:
            return Response({'error': 'Only company owners can use this endpoint'},
                          status=status.HTTP_403_FORBIDDEN)
        
        # Check if chat exists and belongs to the company
        try:
            chat = Chat.objects.get(id=chat_id, company=user.company)
        except Chat.DoesNotExist:
            return Response({'error': 'Chat not found or does not belong to your company'},
                          status=status.HTTP_404_NOT_FOUND)
        
        # Check for message content
        content = request.data.get('content')
        if not content:
            return Response({'error': 'Message content is required'},
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Create the message
        message = Message.objects.create(
            chat=chat,
            sender_type='company',  # Message from company
            content=content,
            is_read=False
        )
        
        # Update the chat's timestamp
        chat.updated_at = timezone.now()
        chat.save()
        
        # Return the message data
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CompanyOwnerGetUserListView(generics.ListAPIView):
    """
    Get a list of all users who have chats with the company owner's company.
    This helps company owners see which users they've been in contact with.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Check if user is a company owner
        if not hasattr(user, 'company') or not user.company:
            return AppUser.objects.none()
        
        # Get users who have chats with this company
        user_ids = Chat.objects.filter(company=user.company).values_list('user', flat=True)
        return AppUser.objects.filter(id__in=user_ids)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        users_with_chats = []
        for user in queryset:
            # Get the chat for this user with the company
            chat = Chat.objects.get(user=user, company=request.user.company)
            
            # Get unread message count
            unread_count = Message.objects.filter(
                chat=chat, 
                sender_type='user',
                is_read=False
            ).count()
            
            # Get last message
            last_message = Message.objects.filter(chat=chat).order_by('-timestamp').first()
            
            users_with_chats.append({
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': f"{user.first_name} {user.last_name}".strip(),
                'chat_id': chat.id,
                'last_active': chat.updated_at,
                'unread_messages': unread_count,
                'last_message': {
                    'content': last_message.content[:50] + '...' if last_message and len(last_message.content) > 50 else 
                              (last_message.content if last_message else None),
                    'timestamp': last_message.timestamp if last_message else None,
                    'sender_type': last_message.sender_type if last_message else None
                } if last_message else None
            })
        
        # Sort by last active time
        users_with_chats.sort(key=lambda x: x['last_active'], reverse=True)
        
        return Response(users_with_chats)
