from rest_framework import permissions
from .models import Conversation, Message


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Permission class that enforces:
    - Only authenticated users can access the API
    - Only participants of a conversation (or admins) can view/send/update/delete messages
    - Only participants (or admins) can retrieve conversation details
    """

    def has_permission(self, request, view):
        # Require authentication for all actions
        if not (request.user and request.user.is_authenticated):
            return False

        # For message creation, ensure the requesting user is a participant in the target conversation
        if view.__class__.__name__ == 'MessageViewSet' and view.action == 'create':
            conv_id = request.data.get('conversation') or request.data.get('conversation_id')
            if not conv_id:
                return False
            try:
                conv = Conversation.objects.get(conversation_id=conv_id)
            except Conversation.DoesNotExist:
                return False
            # allow if user is participant or admin
            if request.user.is_staff or request.user.is_superuser:
                return True
            return request.user in conv.participants.all()

        # For conversation creation, allow any authenticated user (further validation occurs in serializer)
        if view.__class__.__name__ == 'ConversationViewSet' and view.action == 'create':
            return True

        # Default allow; object-level checks will enforce details
        return True

    def has_object_permission(self, request, view, obj):
        # Admins have full access
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Conversation object: only participants can access
        if isinstance(obj, Conversation):
            return request.user in obj.participants.all()

        # Message object: only sender or any participant in the conversation can access
        if isinstance(obj, Message):
            # Allow read for participants and sender
            if request.method in ('GET', 'HEAD', 'OPTIONS'):
                if obj.sender == request.user:
                    return True
                return request.user in obj.conversation.participants.all()

            # For modifications (PUT, PATCH, DELETE) only allow sender or participants
            if request.method in ('PUT', 'PATCH', 'DELETE'):
                if obj.sender == request.user:
                    return True
                return request.user in obj.conversation.participants.all()

            # Default deny for other methods
            return False

        # Default deny
        return False
