
# myshop/urls.py

from django.contrib import admin
from django.urls import include, path
from mainshop.views import order_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('order/', include('mainshop.urls')),
    path('', order_page, name='home'),  # обрабатывает корневой URL
]
