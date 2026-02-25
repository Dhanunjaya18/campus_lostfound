from django.db import models
from django.contrib.auth.models import User
from items.models import Item


class Conversation(models.Model):
    """A unique conversation thread between two users about a specific item."""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='conversations')
    participant1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_p1')
    participant2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_p2')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('item', 'participant1', 'participant2')
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat: {self.participant1} & {self.participant2} about '{self.item.title}'"

    def get_other_user(self, user):
        """Return the other participant in the conversation."""
        if self.participant1 == user:
            return self.participant2
        return self.participant1

    def unread_count_for(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.timestamp:%H:%M}] {self.sender}: {self.content[:40]}"
