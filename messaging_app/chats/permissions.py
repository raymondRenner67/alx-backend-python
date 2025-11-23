from rest_framework import permissions


class IsParticipantOrSender(permissions.BasePermission):
    """
    Object-level permission to only allow conversation participants to access the
    conversation, and message senders or conversation participants to access messages.
    Admin users are allowed full access.
    """

    def has_permission(self, request, view):
        # Require authentication for all actions (global default already enforces this)
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Allow staff/admin full access
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Conversation: user must be in participants
        from .models import Conversation, Message

        if isinstance(obj, Conversation):
            return request.user in obj.participants.all()

        # Message: allow if user is sender or a participant in the conversation
        if isinstance(obj, Message):
            if obj.sender == request.user:
                return True
            return request.user in obj.conversation.participants.all()

        # Default deny
        return False
