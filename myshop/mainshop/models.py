# myshop/models.py
from django.db import models

class Order(models.Model):
    nickname = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
