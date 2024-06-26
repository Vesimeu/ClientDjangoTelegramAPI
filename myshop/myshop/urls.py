
# myshop/urls.py

from django.contrib import admin
from django.urls import include, path
from mainshop.views import order_page
from mainshop.views import telegram_auth,notify_user
from mainshop.views import profile_view , delete_order
from django.contrib.auth import views as auth_views
# from mainshop.management.commands.telegram_bot_client import TelegramBot as Bot




urlpatterns = [
    path('admin/', admin.site.urls),
    path('order/', include('mainshop.urls')),
    path('', order_page, name='home'),  # обрабатывает корневой URL
    path('telegram_auth/', telegram_auth, name='telegram_auth'),
    path('webapp/', telegram_auth, name='telegram_auth'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('profile/', profile_view, name='profile'),
    path('delete_order/<int:order_id>/', delete_order, name='delete_order'),
    path('notify_user/', notify_user, name='notify_user'),  # Новый URL для уведомлений
    # path('notify_user/', Bot.handle_order_notification),
]