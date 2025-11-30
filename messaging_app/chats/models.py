from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class User(AbstractUser):
    """
    Extended User model with additional fields for the messaging application.
    """
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
    ]

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    first_name = models.CharField(max_length=255, null=False)
    last_name = models.CharField(max_length=255, null=False)
    email = models.EmailField(unique=True, null=False)
    password_hash = models.CharField(max_length=255, null=False, default='')
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, null=False, default='guest')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Conversation(models.Model):
    """
    Model to represent a conversation between multiple users.
    """
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        participant_names = ', '.join([p.get_full_name() for p in self.participants.all()])
        return f"Conversation: {participant_names} ({self.conversation_id})"


class UnreadMessagesManager(models.Manager):
    """
    Custom manager to filter unread messages for a specific user.
    Task 4: Custom ORM Manager for Unread Messages
    """
    def unread_for_user(self, user):
        """
        Retrieve unread messages for a specific user.
        Uses .only() to retrieve only necessary fields for optimization.
        """
        return self.filter(
            conversation__participants=user,
            read=False
        ).exclude(
            sender=user
        ).only(
            'message_id', 'sender', 'conversation', 'message_body', 'sent_at', 'read'
        ).select_related('sender', 'conversation')


class Message(models.Model):
    """
    Model to represent a message within a conversation.
    Enhanced with fields for multiple tasks:
    - Task 0: sender and receiver for notifications
    - Task 1: edited field for tracking message edits
    - Task 3: parent_message for threaded conversations
    - Task 4: read field for unread message filtering
    """
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    message_body = models.TextField(null=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    # Task 1: Track if message has been edited
    edited = models.BooleanField(default=False)
    
    # Task 3: Self-referential foreign key for threaded conversations (replies)
    parent_message = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE, 
        related_name='replies'
    )
    
    # Task 4: Track if message has been read
    read = models.BooleanField(default=False)

    # Default manager
    objects = models.Manager()
    
    # Task 4: Custom manager for unread messages
    unread = UnreadMessagesManager()

    class Meta:
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['conversation']),
            models.Index(fields=['sender']),
            models.Index(fields=['read']),
            models.Index(fields=['parent_message']),
        ]

    def __str__(self):
        return f"Message from {self.sender.get_full_name()}: {self.message_body[:50]}"

    @property
    def receiver(self):
        """
        Get the receiver(s) of the message.
        For Task 0: Used to identify who should receive notifications.
        """
        return self.conversation.participants.exclude(user_id=self.sender.user_id)


class MessageHistory(models.Model):
    """
    Model to store the edit history of messages.
    Task 1: Create a Signal for Logging Message Edits
    """
    history_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-edited_at']
        verbose_name_plural = 'Message Histories'

    def __str__(self):
        return f"History of {self.message.message_id} at {self.edited_at}"


class Notification(models.Model):
    """
    Model to store notifications for users.
    Task 0: Implement Signals for User Notifications
    """
    NOTIFICATION_TYPES = [
        ('new_message', 'New Message'),
        ('message_edited', 'Message Edited'),
        ('user_deleted', 'User Deleted'),
    ]

    notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(
        Message, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        null=True,
        blank=True
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='new_message')
    content = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'read']),
        ]

    def __str__(self):
        return f"Notification for {self.user.get_full_name()}: {self.content[:50]}"

