
# myshop/urls.py

from django.contrib import admin
from django.urls import include, path
from mainshop.views import order_page
from mainshop.views import telegram_auth

urlpatterns = [
    path('admin/', admin.site.urls),
    path('order/', include('mainshop.urls')),
    path('', order_page, name='home'),  # обрабатывает корневой URL
    path('telegram_auth/', telegram_auth, name='telegram_auth'),
]