from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User, Conversation, Message
from .serializers import (
    UserSerializer,
    ConversationListSerializer,
    ConversationDetailSerializer,
    MessageSerializer,
)
from .permissions import IsParticipantOfConversation
from django.db.models import Q


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
    permission_classes = [IsParticipantOfConversation]

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
    permission_classes = [IsParticipantOfConversation]
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

