# myshop/admin.py
from django.contrib import admin
from .models import Order,User

admin.site.register(Order)
admin.site.register(User)
