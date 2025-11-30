from django.contrib import admin
from .models import User, Conversation, Message, Notification, MessageHistory


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'first_name', 'last_name', 'email', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['user_id', 'created_at']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['conversation_id', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['conversation_id', 'created_at']
    filter_horizontal = ['participants']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['message_id', 'sender', 'conversation', 'sent_at', 'edited', 'read', 'parent_message']
    list_filter = ['sent_at', 'conversation', 'edited', 'read']
    search_fields = ['sender__email', 'message_body']
    readonly_fields = ['message_id', 'sent_at']
    raw_id_fields = ['sender', 'conversation', 'parent_message']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['notification_id', 'user', 'notification_type', 'message', 'read', 'created_at']
    list_filter = ['notification_type', 'read', 'created_at']
    search_fields = ['user__email', 'content']
    readonly_fields = ['notification_id', 'created_at']
    raw_id_fields = ['user', 'message']


@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ['history_id', 'message', 'edited_at']
    list_filter = ['edited_at']
    search_fields = ['message__message_body', 'old_content']
    readonly_fields = ['history_id', 'edited_at']
    raw_id_fields = ['message']

