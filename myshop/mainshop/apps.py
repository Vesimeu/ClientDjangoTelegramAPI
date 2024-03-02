from django.apps import AppConfig
import threading
import asyncio
from .telegram_bot_auth import start_bot_auth, dispatcher_auth

class MainshopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mainshop'

    # def ready(self):
    #     # Подключаемся к модулю с ботами и вызываем задачи для их запуска
    #     from .tasks import start_telegram_bot_orders, start_telegram_bot_auth
    #
    #     # Запускаем задачу для запуска бота для обработки заказов
    #     start_telegram_bot_orders(repeat=60)  # Повторять каждые 60 секунд
    #
    #     # Запускаем задачу для запуска бота для авторизации и регистрации
    #     start_telegram_bot_auth(repeat=60)  # Повторять каждые 60 секунд