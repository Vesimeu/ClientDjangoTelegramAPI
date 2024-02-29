from .views import order_page
from django.urls import path
from .views import send_order
from django.conf.urls import include
urlpatterns = [
    path('', order_page, name='order_page'),
    path('send_order/', send_order, name='send_order'),
]