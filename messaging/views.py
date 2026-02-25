import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Conversation, Message


@login_required
def inbox(request):
    conversations = Conversation.objects.filter(
        Q(participant1=request.user) | Q(participant2=request.user)
    ).select_related('item', 'participant1', 'participant2').order_by('-updated_at')

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
    from items.models import Item
    item = get_object_or_404(Item, pk=item_pk)

    if item.posted_by == request.user:
        messages.warning(request, "You can't chat with yourself.")
        return redirect('item_detail', pk=item_pk)

    user1, user2 = request.user, item.posted_by
    conversation = Conversation.objects.filter(item=item).filter(
        Q(participant1=user1, participant2=user2) |
        Q(participant1=user2, participant2=user1)
    ).first()

    if not conversation:
        conversation = Conversation.objects.create(
            item=item, participant1=user1, participant2=user2,
        )

    return redirect('chat_room', conversation_id=conversation.id)


@login_required
def chat_room(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)

    if request.user not in [conversation.participant1, conversation.participant2]:
        messages.error(request, 'You do not have access to this conversation.')
        return redirect('inbox')

    other_user = conversation.get_other_user(request.user)
    chat_messages = conversation.messages.select_related('sender').all()

    # Mark messages as read on open
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    return render(request, 'messaging/chat_room.html', {
        'conversation': conversation,
        'other_user': other_user,
        'chat_messages': chat_messages,
        'item': conversation.item,
    })


@login_required
@require_http_methods(["GET", "POST"])
def poll_messages(request, conversation_id):
    """
    GET  → Fetch new messages since ?after=<id>  (polling fallback for offline recipient)
    POST → Save a message via HTTP               (fallback send when WebSocket is down)
    """
    conversation = get_object_or_404(Conversation, id=conversation_id)

    if request.user not in [conversation.participant1, conversation.participant2]:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    # ── POST: save message when WebSocket is unavailable ──────────────────
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            content = body.get('message', '').strip()
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'error': 'Invalid request'}, status=400)

        if not content:
            return JsonResponse({'error': 'Empty message'}, status=400)

        msg = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content,
        )
        conversation.save()  # bump updated_at

        return JsonResponse({
            'message': {
                'id': msg.id,
                'message': msg.content,
                'sender_id': msg.sender.id,
                'sender_username': msg.sender.username,
                'timestamp': msg.timestamp.strftime('%H:%M'),
                'is_own': True,
            }
        })

    # ── GET: return new messages since last seen id ────────────────────────
    after_id = int(request.GET.get('after', 0))
    msgs = conversation.messages.filter(id__gt=after_id).select_related('sender').order_by('timestamp')

    # Mark fetched messages as read
    msgs.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    return JsonResponse({
        'messages': [{
            'id': m.id,
            'message': m.content,
            'sender_id': m.sender.id,
            'sender_username': m.sender.username,
            'timestamp': m.timestamp.strftime('%H:%M'),
            'is_own': m.sender == request.user,
        } for m in msgs]
    })
