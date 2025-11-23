from django.contrib import admin
from .models import User, Conversation, Message


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
    list_display = ['message_id', 'sender', 'conversation', 'sent_at']
    list_filter = ['sent_at', 'conversation']
    search_fields = ['sender__email', 'message_body']
    readonly_fields = ['message_id', 'sent_at']

