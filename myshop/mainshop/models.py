from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.hashers import make_password

class Order(models.Model):
    SUBJECT_CHOICES = [
        ('1', 'Математика'),
        ('2', 'Информатика'),
        ('3', 'Начертательная геометрия'),
        ('4', 'УИР'),
    ]

    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('in_progress', 'В процессе'),
        ('completed', 'Завершен'),
    ]

    subject = models.CharField(max_length=50, default='Не указано', choices=SUBJECT_CHOICES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    accepted = models.BooleanField(default=False)
    status_orders = models.CharField(max_length=20, default='pending', choices=STATUS_CHOICES)
    id_client = models.BigIntegerField(default=0)
    id_executor = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class User(AbstractUser):
    telegram_id = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=100)
    orders = models.ManyToManyField(Order, related_name='users', blank=True)

    groups = models.ManyToManyField(Group, verbose_name='groups', related_name='mainshop_user_set', blank=True,
                                    help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.')
    user_permissions = models.ManyToManyField(Permission, verbose_name='user permissions',
                                              related_name='mainshop_user_set', blank=True,
                                              help_text='Specific permissions for this user.')

    # Устанавливаем значение по умолчанию для поля password
    password = models.CharField(max_length=128, default=make_password('admin'), verbose_name='password')

    token = models.CharField(max_length=255, null=True, blank=True)  # Добавляем поле token

    def __str__(self):
        return self.username
class Executor(models.Model):
    telegram_id = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=100)
    active_orders = models.ManyToManyField(Order, related_name='active_executors', blank=True)
    completed_orders = models.IntegerField(default=0)
    information = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.username
