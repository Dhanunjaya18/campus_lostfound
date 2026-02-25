from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.contrib.auth.models import User
from items.models import Item
from .models import Conversation, Message


@login_required
def inbox(request):
    """Show all conversations for the logged-in user."""
    conversations = Conversation.objects.filter(
        Q(participant1=request.user) | Q(participant2=request.user)
    ).select_related('item', 'participant1', 'participant2').order_by('-updated_at')

    # Annotate unread counts
    conv_list = []
    total_unread = 0
    for conv in conversations:
        unread = conv.unread_count_for(request.user)
        total_unread += unread
        conv_list.append({
            'conv': conv,
            'other_user': conv.get_other_user(request.user),
            'last_message': conv.messages.last(),
            'unread': unread,
        })

    return render(request, 'messaging/inbox.html', {
        'conv_list': conv_list,
        'total_unread': total_unread,
    })


@login_required
def start_or_open_chat(request, item_pk):
    """Start a new conversation or open an existing one."""
    item = get_object_or_404(Item, pk=item_pk)

    if item.posted_by == request.user:
        messages.warning(request, "You can't chat with yourself about your own item.")
        return redirect('item_detail', pk=item_pk)

    # Get or create conversation (always: current user = p1, owner = p2)
    user1 = request.user
    user2 = item.posted_by

    conversation = Conversation.objects.filter(
        item=item
    ).filter(
        Q(participant1=user1, participant2=user2) |
        Q(participant1=user2, participant2=user1)
    ).first()

    if not conversation:
        conversation = Conversation.objects.create(
            item=item,
            participant1=user1,
            participant2=user2,
        )

    return redirect('chat_room', conversation_id=conversation.id)


@login_required
def chat_room(request, conversation_id):
    """The real-time chat room page."""
    conversation = get_object_or_404(Conversation, id=conversation_id)

    # Security: only participants can access
    if request.user not in [conversation.participant1, conversation.participant2]:
        messages.error(request, 'You do not have access to this conversation.')
        return redirect('inbox')

    other_user = conversation.get_other_user(request.user)

    # Load existing messages
    chat_messages = conversation.messages.select_related('sender').all()

    # Mark messages as read
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    return render(request, 'messaging/chat_room.html', {
        'conversation': conversation,
        'other_user': other_user,
        'chat_messages': chat_messages,
        'item': conversation.item,
    })
