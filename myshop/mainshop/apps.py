from django.apps import AppConfig
import threading
import asyncio

class MainshopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mainshop'

