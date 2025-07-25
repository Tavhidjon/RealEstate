from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone

from .models import Chat, Message, Company, AppUser
from .chat_serializers import ChatSerializer, MessageSerializer, CompanyChatSerializer
from .permissions import IsOwnerOrAdmin


class CompanyChatListView(generics.ListAPIView):
    """List all companies for chat functionality"""
    queryset = Company.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Handle Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Company.objects.none()
            
        # Annotate companies with chat info for the current user
        user = self.request.user
        companies = Company.objects.all()
        
        # For each company, we'll annotate with whether there's an active chat
        # and the count of unread messages
        for company in companies:
            try:
                chat = Chat.objects.get(user=user, company=company)
                company.has_chat = True
                company.chat_id = chat.id
                company.unread_count = Message.objects.filter(
                    chat=chat, 
                    is_read=False, 
                    sender_type='company'
                ).count()
            except Chat.DoesNotExist:
                company.has_chat = False
                company.chat_id = None
                company.unread_count = 0
                
        return companies.order_by('name')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        result = []
        
        for company in queryset:
            result.append({
                'id': company.id,
                'name': company.name,
                'description': company.description,
                'has_chat': getattr(company, 'has_chat', False),
                'chat_id': getattr(company, 'chat_id', None),
                'unread_count': getattr(company, 'unread_count', 0)
            })
        
        return Response(result)


class ChatViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user chats with companies"""
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        # Handle Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Chat.objects.none()
            
        # Only return chats that belong to the current user
        return Chat.objects.filter(user=self.request.user).order_by('-updated_at')
    
    def perform_create(self, serializer):
        # Auto-set the user to the current authenticated user
        serializer.save(user=self.request.user)
        
    @action(detail=False, methods=['post'], url_path='start/(?P<company_id>[^/.]+)')
    def start_chat(self, request, company_id=None):
        """Start a new chat with a company or return an existing one"""
        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)
            
        # Get or create a chat with this company
        chat, created = Chat.objects.get_or_create(
            user=request.user,
            company=company,
            defaults={'is_active': True}
        )
        
        # If an initial message is provided, create it
        initial_message = None
        content = request.data.get('content')
        if content:
            initial_message = Message.objects.create(
                chat=chat,
                sender_type='user',
                content=content,
                is_read=False
            )
            
            # Update chat timestamp if a new message was sent
            chat.updated_at = timezone.now()
            chat.save()
        
        # Return the chat and optionally the initial message
        chat_serializer = self.get_serializer(chat)
        response_data = chat_serializer.data
        
        if initial_message:
            message_serializer = MessageSerializer(initial_message)
            response_data['initial_message'] = message_serializer.data
            
        return Response(response_data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages for a specific chat"""
        chat = self.get_object()
        messages = chat.messages.all().order_by('timestamp')
        
        # Mark all unread messages as read when user views them
        if request.user == chat.user:
            unread_messages = messages.filter(is_read=False, sender_type='company')
            unread_messages.update(is_read=True)
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a new message in the chat"""
        chat = self.get_object()
        content = request.data.get('content')
        
        if not content:
            return Response({'error': 'Message content is required'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Create the message
        message = Message.objects.create(
            chat=chat,
            sender_type='user',  # Since this is sent by the app user
            content=content,
            is_read=False
        )
        
        # Update the chat's updated_at timestamp
        chat.updated_at = timezone.now()
        chat.save()
        
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread messages across all chats"""
        # Ensure user is authenticated (should be handled by permission_classes,
        # but adding an extra check for clarity)
        if not request.user.is_authenticated:
            return Response([], status=status.HTTP_401_UNAUTHORIZED)
            
        unread_counts = Chat.objects.filter(user=request.user)\
            .annotate(unread=Count('messages', filter=Q(messages__is_read=False, messages__sender_type='company')))\
            .values('id', 'company__name', 'unread')
        
        return Response(unread_counts)


class CompanyChatViewSet(viewsets.ModelViewSet):
    """ViewSet for company representatives to manage chats"""
    serializer_class = CompanyChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Handle Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Chat.objects.none()
        
        # Check if user has a company_association field or is part of company admin group
        user = self.request.user
        
        # If user is superadmin, they can see all chats for all companies
        if user.is_superuser:
            return Chat.objects.all().order_by('-updated_at')
        
        # Check for company assignment in user profile
        # This would need to be implemented based on how you want to associate users with companies
        # For example, if you add a company field to the AppUser model
        if hasattr(user, 'company') and user.company:
            return Chat.objects.filter(company=user.company).order_by('-updated_at')
        
        # Alternative: check if user is in a group named after a company
        company_groups = user.groups.filter(name__startswith='company_')
        if company_groups.exists():
            # Extract company IDs from group names (e.g., "company_1" → 1)
            company_ids = []
            for group in company_groups:
                try:
                    company_id = int(group.name.replace('company_', ''))
                    company_ids.append(company_id)
                except ValueError:
                    continue
            
            if company_ids:
                return Chat.objects.filter(company__id__in=company_ids).order_by('-updated_at')
        
        # Return empty queryset if user doesn't represent any company
        return Chat.objects.none()
    
    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """Send a reply from the company to the user"""
        chat = self.get_object()
        content = request.data.get('content')
        
        # Validate request data
        if not content:
            return Response({'error': 'Message content is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Check if chat is active
        if not chat.is_active:
            return Response({'error': 'Cannot send message to inactive chat'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Verify authorization (this is an extra check beyond the permission classes)
        user = request.user
        if not (user.is_superuser or 
                (hasattr(user, 'company') and user.company == chat.company) or
                user.groups.filter(name=f'company_{chat.company.id}').exists()):
            return Response({'error': 'You are not authorized to reply on behalf of this company'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        # Create the message
        message = Message.objects.create(
            chat=chat,
            sender_type='company',  # Since this is sent by the company
            content=content,
            is_read=False
        )
        
        # Update the chat's updated_at timestamp
        chat.updated_at = timezone.now()
        chat.save()
        
        # Prepare response with both message and updated chat data
        message_serializer = MessageSerializer(message)
        chat_serializer = CompanyChatSerializer(chat, context={'request': request})
        
        return Response({
            'message': message_serializer.data,
            'chat': chat_serializer.data
        }, status=status.HTTP_201_CREATED)
        
    @action(detail=True, methods=['get'])
    def mark_as_read(self, request, pk=None):
        """Mark all user messages as read by the company"""
        chat = self.get_object()
        unread_count = Message.objects.filter(chat=chat, is_read=False, sender_type='user').update(is_read=True)
        
        return Response({
            'success': True,
            'messages_marked_read': unread_count
        })
