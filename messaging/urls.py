from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('start/<int:item_pk>/', views.start_or_open_chat, name='start_chat'),
    path('chat/<int:conversation_id>/', views.chat_room, name='chat_room'),
]
