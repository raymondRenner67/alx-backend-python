from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .models import User, Conversation, Message, Notification, MessageHistory
from .serializers import (
    UserSerializer,
    ConversationListSerializer,
    ConversationDetailSerializer,
    MessageSerializer,
)
from .permissions import IsParticipantOfConversation
from .pagination import MessagePagination
from .filters import MessageFilter
from django.db.models import Q, Prefetch


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for User model.
    Provides read-only access to users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Conversation model.
    Provides endpoints for:
    - List all conversations
    - Create a new conversation
    - Retrieve a specific conversation
    - Update a conversation
    - Delete a conversation
    """
    queryset = Conversation.objects.all()
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        """Limit conversations to those the requesting user participates in (unless staff)."""
        user = self.request.user
        if not user or not user.is_authenticated:
            return Conversation.objects.none()
        if user.is_staff or user.is_superuser:
            return Conversation.objects.all()
        return Conversation.objects.filter(participants=user).distinct()

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        if self.action == 'retrieve':
            return ConversationDetailSerializer
        return ConversationListSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new conversation with specified participants.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """
        Send a message to this conversation.
        Expects: {"sender_id": "<uuid>", "message_body": "text"}
        """
        conversation = self.get_object()
        sender_id = request.data.get('sender_id')
        message_body = request.data.get('message_body')

        if not sender_id or not message_body:
            return Response({'error': 'sender_id and message_body are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sender = User.objects.get(user_id=sender_id)
        except User.DoesNotExist:
            return Response({'error': 'Sender not found'}, status=status.HTTP_404_NOT_FOUND)

        # Ensure sender is a participant (or admin) before creating
        if not (sender in conversation.participants.all() or request.user.is_staff or request.user == sender):
            return Response({'error': 'Sender is not a participant of this conversation'}, status=status.HTTP_403_FORBIDDEN)

        message = Message.objects.create(sender=sender, conversation=conversation, message_body=message_body)
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """
        Add a user to an existing conversation.
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(user_id=user_id)
            if user in conversation.participants.all():
                return Response(
                    {'error': 'User is already a participant'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            conversation.participants.add(user)
            serializer = ConversationDetailSerializer(conversation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        """
        Remove a user from a conversation.
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(user_id=user_id)
            if user not in conversation.participants.all():
                return Response(
                    {'error': 'User is not a participant'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            conversation.participants.remove(user)
            serializer = ConversationDetailSerializer(conversation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Message model.
    Provides endpoints for:
    - List all messages (with optional conversation filtering)
    - Create a new message
    - Retrieve a specific message
    - Update a message
    - Delete a message
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    pagination_class = MessagePagination
    filterset_class = MessageFilter
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['message_body', 'sender__email']
    ordering_fields = ['sent_at']

    def get_queryset(self):
        """
        Filter messages by conversation if conversation_id is provided.
        """
        user = self.request.user
        if not user or not user.is_authenticated:
            return Message.objects.none()

        # base queryset: messages where the user is sender or a participant in the conversation
        queryset = Message.objects.filter(Q(sender=user) | Q(conversation__participants=user)).distinct()

        conversation_id = self.request.query_params.get('conversation_id')
        if conversation_id:
            queryset = queryset.filter(conversation__conversation_id=conversation_id)
        return queryset

    def create(self, request, *args, **kwargs):
        """
        Create a new message in a conversation.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """
        Task 4: Get unread messages for the authenticated user.
        Uses the custom UnreadMessagesManager with .only() optimization.
        """
        user = request.user
        unread_messages = Message.unread.unread_for_user(user)
        
        # Paginate results
        page = self.paginate_queryset(unread_messages)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(unread_messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Task 4: Mark a message as read.
        """
        message = self.get_object()
        message.read = True
        message.save()
        serializer = self.get_serializer(message)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def thread(self, request, pk=None):
        """
        Task 3: Get threaded conversation (message and all its replies).
        Uses prefetch_related and select_related for optimization.
        """
        message = self.get_object()
        
        # Recursively fetch all replies with optimization
        messages_with_replies = Message.objects.filter(
            Q(message_id=message.message_id) | Q(parent_message=message)
        ).select_related(
            'sender', 'conversation', 'parent_message'
        ).prefetch_related(
            'replies', 'history'
        )
        
        serializer = self.get_serializer(messages_with_replies, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """
        Task 1: Get edit history for a message.
        Display the message edit history in the user interface,
        allowing users to view previous versions of their messages.
        """
        message = self.get_object()
        history = message.history.all()
        
        history_data = [{
            'history_id': str(h.history_id),
            'old_content': h.old_content,
            'edited_at': h.edited_at,
            'edited_by': {
                'user_id': str(h.edited_by.user_id) if h.edited_by else None,
                'name': h.edited_by.get_full_name() if h.edited_by else 'Unknown',
                'email': h.edited_by.email if h.edited_by else None
            } if h.edited_by else None
        } for h in history]
        
        return Response({
            'message_id': str(message.message_id),
            'current_content': message.message_body,
            'edited': message.edited,
            'last_edited_by': {
                'user_id': str(message.edited_by.user_id) if message.edited_by else None,
                'name': message.edited_by.get_full_name() if message.edited_by else 'Unknown',
                'email': message.edited_by.email if message.edited_by else None
            } if message.edited_by else None,
            'edit_count': len(history_data),
            'history': history_data
        })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request):
    """
    Task 2: Delete user account and all related data.
    The post_delete signal will handle cleanup of messages, notifications, and history.
    """
    user = request.user
    
    # Store user info for response
    user_email = user.email
    user_name = user.get_full_name()
    
    # Delete the user (signals will handle related data cleanup)
    user.delete()
    
    return Response({
        'message': f'User account for {user_name} ({user_email}) and all related data has been deleted successfully.'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@cache_page(60)  # Task 5: Cache for 60 seconds
def cached_conversation_messages(request):
    """
    Task 5: Cached view that retrieves messages in a conversation.
    Cache timeout is set to 60 seconds.
    """
    conversation_id = request.query_params.get('conversation_id')
    
    if not conversation_id:
        return Response({
            'error': 'conversation_id parameter is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        conversation = Conversation.objects.get(conversation_id=conversation_id)
        
        # Check if user is participant
        if request.user not in conversation.participants.all():
            return Response({
                'error': 'You are not a participant of this conversation'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get messages with optimization
        messages = Message.objects.filter(
            conversation=conversation
        ).select_related(
            'sender', 'conversation'
        ).prefetch_related(
            'replies'
        ).order_by('-sent_at')
        
        serializer = MessageSerializer(messages, many=True)
        
        return Response({
            'conversation_id': conversation_id,
            'message_count': messages.count(),
            'messages': serializer.data,
            'cached': True  # Indicator that this response might be cached
        })
        
    except Conversation.DoesNotExist:
        return Response({
            'error': 'Conversation not found'
        }, status=status.HTTP_404_NOT_FOUND)

