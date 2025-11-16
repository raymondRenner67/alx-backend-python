from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    class Meta:
        model = User
        fields = [
            'user_id',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'role',
            'created_at',
        ]
        read_only_fields = ['user_id', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.
    Includes nested sender information.
    """
    # include nested sender info and accept sender_id on write
    sender = UserSerializer(read_only=True)
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='sender'
    )
    # ensure message_body is a CharField at serializer level for validation
    message_body = serializers.CharField()

    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'sender_id',
            'conversation',
            'message_body',
            'sent_at',
        ]
        read_only_fields = ['message_id', 'sent_at']


class ConversationListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing conversations.
    Includes basic participant information.
    """
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        source='participants'
    )

    def validate_participant_ids(self, value):
        # require at least two participants for a conversation
        if not value or len(value) < 2:
            raise serializers.ValidationError('A conversation requires at least two participants')
        return value

    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participant_ids',
            'created_at',
        ]
        read_only_fields = ['conversation_id', 'created_at']


class ConversationDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for conversation detail view.
    Includes all messages and detailed participant information.
    """
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        source='participants'
    )
    messages = MessageSerializer(many=True, read_only=True)
    # example extra read-only field provided by a SerializerMethodField
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participant_ids',
            'messages',
            'created_at',
        ]
        read_only_fields = ['conversation_id', 'created_at', 'messages']

    def get_message_count(self, obj):
        return obj.messages.count()
