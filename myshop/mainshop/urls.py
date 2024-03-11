from .views import order_page
from django.urls import path
from .views import send_order
from . import views
from django.conf.urls import include
urlpatterns = [
    path('', order_page, name='order_page'),
    path('send_order/', send_order, name='send_order'),
    path('telegram_auth/', views.telegram_auth, name='telegram_auth'),
]