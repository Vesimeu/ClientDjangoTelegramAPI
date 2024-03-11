# myshop/models.py
from django.db import models

class Order(models.Model):
    nickname = models.CharField(max_length=100)
    description = models.TextField() #Описание товара
    price = models.DecimalField(max_digits=10, decimal_places=2)
    accepted = models.BooleanField(default=False) # Статус заказа принятия заказа
    status_orders = models.BooleanField(default=False) # Статус выполнения заказа
    id_client = models.BigIntegerField(null=True, blank=True) #telegram id заказчика
    id_executor = models.BigIntegerField(null=True, blank=True) #telegram id исполнителя
    created_at = models.DateTimeField(auto_now_add=True)
class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=100)
    orders = models.ManyToManyField(Order, related_name='users')