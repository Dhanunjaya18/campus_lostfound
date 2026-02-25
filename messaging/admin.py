from django.contrib import admin
from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'item', 'participant1', 'participant2', 'created_at', 'updated_at']
    search_fields = ['item__title', 'participant1__username', 'participant2__username']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'conversation', 'content_preview', 'timestamp', 'is_read']
    list_filter = ['is_read']
    search_fields = ['sender__username', 'content']

    def content_preview(self, obj):
        return obj.content[:50]
    content_preview.short_description = 'Message'
