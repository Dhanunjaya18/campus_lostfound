from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from items import views as item_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('register/', item_views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Items
    path('', item_views.home, name='home'),
    path('dashboard/', item_views.dashboard, name='dashboard'),
    path('post/', item_views.post_item, name='post_item'),
    path('item/<int:pk>/', item_views.item_detail, name='item_detail'),
    path('item/<int:pk>/edit/', item_views.edit_item, name='edit_item'),
    path('item/<int:pk>/delete/', item_views.delete_item, name='delete_item'),
    path('item/<int:pk>/return/', item_views.mark_returned, name='mark_returned'),
    path('search/', item_views.search_items, name='search'),

    # Messaging / Real-time Chat
    path('inbox/', include('messaging.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
