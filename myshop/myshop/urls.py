
# myshop/urls.py

from django.contrib import admin
from django.urls import include, path
from mainshop.views import order_page
from mainshop.views import telegram_auth
from mainshop.views import profile_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('order/', include('mainshop.urls')),
    path('', order_page, name='home'),  # обрабатывает корневой URL
    path('telegram_auth/', telegram_auth, name='telegram_auth'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('profile/', profile_view, name='profile'),
]