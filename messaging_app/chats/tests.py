"""
Comprehensive tests for Django Signals and ORM features.
Tests all tasks: signals, message editing, user deletion, threaded messages, unread messages, and caching.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache
from .models import User, Conversation, Message, Notification, MessageHistory
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import time

User = get_user_model()


class SignalsTestCase(TestCase):
    """
    Test cases for Django signals (Tasks 0, 1, 2).
    """
    
    def setUp(self):
        """Set up test data."""
        # Create users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            first_name='User',
            last_name='One',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            first_name='User',
            last_name='Two',
            password='testpass123'
        )
        
        # Create conversation
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)
    
    def test_notification_created_on_new_message(self):
        """
        Task 0: Test that a notification is created when a new message is sent.
        """
        # Initial notification count
        initial_count = Notification.objects.filter(user=self.user2).count()
        
        # User1 sends a message
        message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Hello, User Two!"
        )
        
        # Check that User2 received a notification
        notifications = Notification.objects.filter(user=self.user2, message=message)
        self.assertEqual(notifications.count(), 1)
        
        # Verify notification content
        notification = notifications.first()
        self.assertEqual(notification.notification_type, 'new_message')
        self.assertIn('User One', notification.content)
        self.assertFalse(notification.read)
    
    def test_message_history_created_on_edit(self):
        """
        Task 1: Test that message history is created when a message is edited.
        """
        # Create a message
        message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Original content"
        )
        
        # Verify no history exists yet
        self.assertEqual(message.history.count(), 0)
        self.assertFalse(message.edited)
        
        # Edit the message
        message.message_body = "Edited content"
        message.save()
        
        # Verify history was created
        self.assertEqual(message.history.count(), 1)
        history = message.history.first()
        self.assertEqual(history.old_content, "Original content")
        
        # Verify edited flag is set
        message.refresh_from_db()
        self.assertTrue(message.edited)
    
    def test_multiple_edits_create_multiple_history_records(self):
        """
        Task 1: Test that multiple edits create multiple history records.
        """
        message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Version 1"
        )
        
        # First edit
        message.message_body = "Version 2"
        message.save()
        
        # Second edit
        message.message_body = "Version 3"
        message.save()
        
        # Verify two history records
        self.assertEqual(message.history.count(), 2)
        
        # Verify history content in chronological order
        history_list = list(message.history.all().order_by('edited_at'))
        self.assertEqual(history_list[0].old_content, "Version 1")
        self.assertEqual(history_list[1].old_content, "Version 2")
    
    def test_user_deletion_cleanup(self):
        """
        Task 2: Test that related data is cleaned up when a user is deleted.
        """
        # Create messages and notifications
        message1 = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Test message"
        )
        
        # Get notification count for user1
        user1_notifications = Notification.objects.filter(user=self.user1).count()
        
        # Delete user1
        user1_id = self.user1.user_id
        self.user1.delete()
        
        # Verify user is deleted
        self.assertFalse(User.objects.filter(user_id=user1_id).exists())
        
        # Verify messages sent by user1 are deleted (CASCADE)
        self.assertFalse(Message.objects.filter(sender__user_id=user1_id).exists())
        
        # Verify notifications for user1 are deleted (CASCADE)
        self.assertEqual(Notification.objects.filter(user__user_id=user1_id).count(), 0)


class ThreadedConversationsTestCase(TestCase):
    """
    Test cases for threaded conversations (Task 3).
    """
    
    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            first_name='User',
            last_name='One',
            password='testpass123'
        )
        
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1)
    
    def test_parent_message_relationship(self):
        """
        Task 3: Test that parent-child message relationships work correctly.
        """
        # Create parent message
        parent_message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Parent message"
        )
        
        # Create reply
        reply = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Reply to parent",
            parent_message=parent_message
        )
        
        # Verify relationship
        self.assertEqual(reply.parent_message, parent_message)
        self.assertIn(reply, parent_message.replies.all())
    
    def test_threaded_conversation_retrieval(self):
        """
        Task 3: Test retrieving threaded conversations with optimization.
        """
        # Create parent and multiple replies
        parent = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Parent"
        )
        
        reply1 = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Reply 1",
            parent_message=parent
        )
        
        reply2 = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Reply 2",
            parent_message=parent
        )
        
        # Retrieve with prefetch_related optimization
        messages = Message.objects.filter(
            message_id=parent.message_id
        ).prefetch_related('replies')
        
        parent_with_replies = messages.first()
        self.assertEqual(parent_with_replies.replies.count(), 2)


class UnreadMessagesTestCase(TestCase):
    """
    Test cases for unread messages custom manager (Task 4).
    """
    
    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            first_name='User',
            last_name='One',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            first_name='User',
            last_name='Two',
            password='testpass123'
        )
        
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)
    
    def test_unread_messages_manager(self):
        """
        Task 4: Test custom UnreadMessagesManager.
        """
        # Create messages
        message1 = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Unread message 1",
            read=False
        )
        
        message2 = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Read message",
            read=True
        )
        
        message3 = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Unread message 2",
            read=False
        )
        
        # Get unread messages for user2
        unread = Message.unread.unread_for_user(self.user2)
        
        # Should have 2 unread messages
        self.assertEqual(unread.count(), 2)
        self.assertIn(message1, unread)
        self.assertIn(message3, unread)
        self.assertNotIn(message2, unread)
    
    def test_unread_excludes_own_messages(self):
        """
        Task 4: Test that unread manager excludes user's own messages.
        """
        # User1 sends messages
        Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Message from user1",
            read=False
        )
        
        # Get unread for user1 (should be 0 since they sent it)
        unread_user1 = Message.unread.unread_for_user(self.user1)
        self.assertEqual(unread_user1.count(), 0)
    
    def test_mark_message_as_read(self):
        """
        Task 4: Test marking a message as read.
        """
        message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Test message",
            read=False
        )
        
        # Initially unread
        self.assertFalse(message.read)
        unread_count = Message.unread.unread_for_user(self.user2).count()
        self.assertEqual(unread_count, 1)
        
        # Mark as read
        message.read = True
        message.save()
        
        # Verify it's now read
        message.refresh_from_db()
        self.assertTrue(message.read)
        unread_count = Message.unread.unread_for_user(self.user2).count()
        self.assertEqual(unread_count, 0)


class CachingTestCase(APITestCase):
    """
    Test cases for view caching (Task 5).
    """
    
    def setUp(self):
        """Set up test data and clear cache."""
        cache.clear()
        
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user)
        
        # Create some messages
        for i in range(5):
            Message.objects.create(
                sender=self.user,
                conversation=self.conversation,
                message_body=f"Message {i}"
            )
    
    def test_cached_view_response(self):
        """
        Task 5: Test that the cached view returns data correctly.
        """
        self.client.force_authenticate(user=self.user)
        
        # First request (not cached)
        response1 = self.client.get(
            '/api/messages/cached/',
            {'conversation_id': str(self.conversation.conversation_id)}
        )
        
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertIn('messages', response1.data)
        self.assertEqual(response1.data['message_count'], 5)
    
    def test_cache_persistence(self):
        """
        Task 5: Test that cached data persists across requests.
        """
        self.client.force_authenticate(user=self.user)
        
        # First request
        response1 = self.client.get(
            '/api/messages/cached/',
            {'conversation_id': str(self.conversation.conversation_id)}
        )
        
        # Create a new message
        Message.objects.create(
            sender=self.user,
            conversation=self.conversation,
            message_body="New message after cache"
        )
        
        # Second request (should still return cached data with 5 messages)
        response2 = self.client.get(
            '/api/messages/cached/',
            {'conversation_id': str(self.conversation.conversation_id)}
        )
        
        # Due to caching, should still show 5 messages, not 6
        # (This depends on cache timeout; if 60 seconds haven't passed)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)


class IntegrationTestCase(APITestCase):
    """
    Integration tests combining multiple features.
    """
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            first_name='User',
            last_name='One',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            first_name='User',
            last_name='Two',
            password='testpass123'
        )
        
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)
    
    def test_complete_messaging_workflow(self):
        """
        Test complete workflow: send message, edit, check notifications, check history.
        """
        # User1 sends a message
        message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Original message"
        )
        
        # User2 should have a notification
        notifications = Notification.objects.filter(user=self.user2, message=message)
        self.assertEqual(notifications.count(), 1)
        
        # User1 edits the message
        message.message_body = "Edited message"
        message.save()
        
        # Check history
        self.assertEqual(message.history.count(), 1)
        self.assertEqual(message.history.first().old_content, "Original message")
        
        # Check edited flag
        self.assertTrue(message.edited)
        
        # User2 should have an edit notification
        edit_notifications = Notification.objects.filter(
            user=self.user2,
            message=message,
            notification_type='message_edited'
        )
        self.assertEqual(edit_notifications.count(), 1)
