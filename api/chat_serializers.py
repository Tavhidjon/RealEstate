from rest_framework import serializers
from .models import Chat, Message, Company

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender_type', 'content', 'timestamp', 'is_read']
        read_only_fields = ['id', 'timestamp', 'is_read']


class ChatSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.name')
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Chat
        fields = ['id', 'user', 'company', 'company_name', 'created_at', 
                  'updated_at', 'is_active', 'last_message', 'unread_count']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'company_name']
    
    def get_last_message(self, obj):
        """Get the most recent message in the chat"""
        last_message = obj.messages.order_by('-timestamp').first()
        if last_message:
            return {
                'content': last_message.content[:50] + '...' if len(last_message.content) > 50 else last_message.content,
                'timestamp': last_message.timestamp,
                'sender_type': last_message.sender_type
            }
        return None
    
    def get_unread_count(self, obj):
        """Get the count of unread messages for the user"""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated and request.user == obj.user:
            return obj.messages.filter(is_read=False, sender_type='company').count()
        return 0


class CompanyChatSerializer(serializers.ModelSerializer):
    """Serializer for company-side view of chats"""
    user_email = serializers.ReadOnlyField(source='user.email')
    user_name = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Chat
        fields = ['id', 'user', 'user_email', 'user_name', 'created_at', 
                  'updated_at', 'is_active', 'last_message', 'unread_count']
        read_only_fields = ['id', 'user', 'user_email', 'user_name', 'created_at', 'updated_at']
    
    def get_user_name(self, obj):
        if obj.user.first_name or obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return obj.user.username
    
    def get_last_message(self, obj):
        """Get the most recent message in the chat"""
        last_message = obj.messages.order_by('-timestamp').first()
        if last_message:
            return {
                'content': last_message.content[:50] + '...' if len(last_message.content) > 50 else last_message.content,
                'timestamp': last_message.timestamp,
                'sender_type': last_message.sender_type
            }
        return None
    
    def get_unread_count(self, obj):
        """Get the count of unread messages for the company"""
        return obj.messages.filter(is_read=False, sender_type='user').count()
