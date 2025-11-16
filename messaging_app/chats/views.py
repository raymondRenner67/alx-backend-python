from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User, Conversation, Message
from .serializers import (
    UserSerializer,
    ConversationListSerializer,
    ConversationDetailSerializer,
    MessageSerializer,
)


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

    def get_queryset(self):
        """
        Filter messages by conversation if conversation_id is provided.
        """
        queryset = Message.objects.all()
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

