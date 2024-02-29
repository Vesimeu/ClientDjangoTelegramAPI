# myshop/tasks.py
from background_task import background

from .telegram_bot import start_bot_orders, dispatcher_orders
from .telegram_bot_auth import start_bot_auth, dispatcher_auth

@background(schedule=1)
def start_telegram_bot_orders():
    start_bot_orders()

@background(schedule=1)
def start_telegram_bot_auth():
    start_bot_auth()
