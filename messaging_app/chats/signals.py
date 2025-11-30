"""
Django signals for the messaging application.
Implements automatic notifications and data cleanup.
"""
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory

User = get_user_model()


@receiver(post_save, sender=Message)
def create_notification_on_new_message(sender, instance, created, **kwargs):
    """
    Task 0: Automatically notify users when they receive a new message.
    
    This signal listens for new Message instances and creates notifications
    for all receivers (participants except the sender).
    """
    if created:  # Only for new messages, not updates
        # Get all receivers (conversation participants except sender)
        receivers = instance.conversation.participants.exclude(user_id=instance.sender.user_id)
        
        # Create a notification for each receiver
        for receiver in receivers:
            Notification.objects.create(
                user=receiver,
                message=instance,
                notification_type='new_message',
                content=f"New message from {instance.sender.get_full_name()}: {instance.message_body[:50]}..."
            )


@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Task 1: Log when a user edits a message and save the old content.
    
    This signal uses pre_save to capture the old content before the message
    is updated, storing it in MessageHistory.
    """
    if instance.pk:  # Only for existing messages (updates, not new creations)
        try:
            # Fetch the old version from the database
            old_message = Message.objects.get(pk=instance.pk)
            
            # Check if the message body has changed
            if old_message.message_body != instance.message_body:
                # Save the old content to history
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.message_body,
                    edited_by=instance.sender  # Track who edited it
                )
                
                # Mark the message as edited and track editor
                instance.edited = True
                instance.edited_by = instance.sender
                
                # Optionally create a notification for message edit
                receivers = instance.conversation.participants.exclude(user_id=instance.sender.user_id)
                for receiver in receivers:
                    Notification.objects.create(
                        user=receiver,
                        message=instance,
                        notification_type='message_edited',
                        content=f"{instance.sender.get_full_name()} edited their message"
                    )
        except Message.DoesNotExist:
            # This shouldn't happen, but handle gracefully
            pass


@receiver(post_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    """
    Task 2: Automatically clean up related data when a user deletes their account.
    
    This signal ensures that when a User is deleted, all associated data is cleaned up:
    - Messages sent by the user
    - Notifications for the user
    - Message histories (through messages CASCADE)
    
    While foreign key constraints with CASCADE handle most cleanup automatically,
    this signal provides explicit deletion for completeness and logging.
    """
    # Explicitly delete all messages sent by this user
    # This will CASCADE delete related MessageHistory records
    deleted_messages = Message.objects.filter(sender=instance).delete()
    
    # Explicitly delete all notifications for this user
    deleted_notifications = Notification.objects.filter(user=instance).delete()
    
    # Log the deletion (could be to a file, external service, etc.)
    print(f"User {instance.get_full_name()} ({instance.email}) account deleted")
    print(f"  - Deleted {deleted_messages[0]} message(s)")
    print(f"  - Deleted {deleted_notifications[0]} notification(s)")
    
    # Optionally notify admins
    admin_users = User.objects.filter(role='admin')
    for admin in admin_users:
        Notification.objects.create(
            user=admin,
            notification_type='user_deleted',
            content=f"User {instance.get_full_name()} ({instance.email}) has deleted their account"
        )
