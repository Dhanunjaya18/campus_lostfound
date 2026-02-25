from django import template
from django.db.models import Q
from messaging.models import Conversation

register = template.Library()

@register.simple_tag
def unread_count(user):
    if not user.is_authenticated:
        return 0
    convs = Conversation.objects.filter(
        Q(participant1=user) | Q(participant2=user)
    )
    total = 0
    for conv in convs:
        total += conv.unread_count_for(user)
    return total
