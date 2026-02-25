from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Per-conversation real-time chat
    re_path(r'ws/chat/(?P<conversation_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    # Per-user persistent notification socket (open on every page)
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]
