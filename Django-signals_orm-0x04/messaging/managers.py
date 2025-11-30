from django.db import models


class UnreadMessagesManager(models.Manager):
    """Custom manager for filtering unread messages for a specific user."""
    
    def unread_for_user(self, user):
        """
        Returns unread messages for the specified user.
        Optimizes query by only selecting necessary fields.
        
        Args:
            user: The User instance to filter messages for
            
        Returns:
            QuerySet of unread Message instances
        """
        return self.filter(
            read=False,
            conversation__participants__user_id=user.user_id
        ).exclude(
            sender=user
        ).only(
            'message_id',
            'sender_id',
            'conversation_id',
            'message_body',
            'sent_at',
            'read'
        )
