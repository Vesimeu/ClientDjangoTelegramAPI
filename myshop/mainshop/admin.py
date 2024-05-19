# myshop/admin.py
from django.contrib import admin
from .models import Order,User,Executor

admin.site.register(Order)
admin.site.register(User)
admin.site.register(Executor)
