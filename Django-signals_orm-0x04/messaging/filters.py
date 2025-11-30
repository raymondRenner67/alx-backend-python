import django_filters
from django.utils import timezone
from datetime import timedelta
from .models import Message, User, Conversation


class MessageFilter(django_filters.FilterSet):
    """
    Filter class for Message model to support:
    - Filtering by sender (user)
    - Filtering by conversation
    - Filtering by messages within a time range
    - Search by message content
    """
    sender = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name='sender',
        help_text='Filter messages by sender user'
    )
    
    conversation = django_filters.ModelChoiceFilter(
        queryset=Conversation.objects.all(),
        field_name='conversation',
        help_text='Filter messages by conversation'
    )
    
    # Time range filters
    sent_after = django_filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='gte',
        help_text='Filter messages sent after this timestamp'
    )
    
    sent_before = django_filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='lte',
        help_text='Filter messages sent before this timestamp'
    )
    
    # Quick time range filter (last N days)
    days_back = django_filters.NumberFilter(
        method='filter_days_back',
        help_text='Filter messages from the last N days'
    )
    
    # Search in message body
    message_body = django_filters.CharFilter(
        field_name='message_body',
        lookup_expr='icontains',
        help_text='Search in message content'
    )

    class Meta:
        model = Message
        fields = ['sender', 'conversation', 'sent_after', 'sent_before', 'message_body']

    def filter_days_back(self, queryset, name, value):
        """
        Filter messages from the last N days.
        """
        if value:
            cutoff_date = timezone.now() - timedelta(days=int(value))
            return queryset.filter(sent_at__gte=cutoff_date)
        return queryset
