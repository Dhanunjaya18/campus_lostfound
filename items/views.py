from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q
from .models import Item, Category
from .forms import RegisterForm, ItemForm


def home(request):
    items = Item.objects.select_related('category', 'posted_by').all()

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        items = items.filter(status=status_filter)

    # Filter by category
    category_filter = request.GET.get('category', '')
    if category_filter:
        items = items.filter(category__id=category_filter)

    categories = Category.objects.all()
    context = {
        'items': items[:20],
        'categories': categories,
        'status_filter': status_filter,
        'category_filter': category_filter,
    }
    return render(request, 'home.html', context)


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account has been created.')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard(request):
    user_items = Item.objects.filter(posted_by=request.user)
    total_posts = user_items.count()
    returned_count = user_items.filter(status='Returned').count()
    lost_count = user_items.filter(status='Lost').count()
    found_count = user_items.filter(status='Found').count()
    context = {
        'user_items': user_items,
        'total_posts': total_posts,
        'returned_count': returned_count,
        'lost_count': lost_count,
        'found_count': found_count,
    }
    return render(request, 'dashboard.html', context)


@login_required
def post_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.posted_by = request.user
            item.save()
            messages.success(request, 'Item posted successfully!')
            return redirect('item_detail', pk=item.pk)
    else:
        form = ItemForm()
    return render(request, 'items/post_item.html', {'form': form, 'title': 'Post Item'})


def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, 'items/item_detail.html', {'item': item})


@login_required
def edit_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if item.posted_by != request.user:
        messages.error(request, 'You can only edit your own posts.')
        return redirect('item_detail', pk=pk)

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated successfully!')
            return redirect('item_detail', pk=pk)
    else:
        form = ItemForm(instance=item)
    return render(request, 'items/post_item.html', {'form': form, 'title': 'Edit Item', 'item': item})


@login_required
def delete_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if item.posted_by != request.user:
        messages.error(request, 'You can only delete your own posts.')
        return redirect('item_detail', pk=pk)

    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item deleted.')
        return redirect('dashboard')
    return render(request, 'items/confirm_delete.html', {'item': item})


@login_required
def mark_returned(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if item.posted_by != request.user:
        messages.error(request, 'Only the owner can mark an item as returned.')
        return redirect('item_detail', pk=pk)

    item.status = 'Returned'
    item.save()
    messages.success(request, f'"{item.title}" has been marked as Returned!')
    return redirect('item_detail', pk=pk)


def search_items(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')

    items = Item.objects.select_related('category', 'posted_by').all()

    if query:
        items = items.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if status_filter:
        items = items.filter(status=status_filter)
    if category_filter:
        items = items.filter(category__id=category_filter)

    categories = Category.objects.all()
    context = {
        'items': items,
        'query': query,
        'categories': categories,
        'status_filter': status_filter,
        'category_filter': category_filter,
    }
    return render(request, 'items/search_results.html', context)
