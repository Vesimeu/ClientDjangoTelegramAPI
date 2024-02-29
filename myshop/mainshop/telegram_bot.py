# myshop/mainshop/telegram_bot.py
import os
import asyncio
from aiogram import Bot, Dispatcher, executor, types

# Читаем токен из файла
token_file_path = os.path.join(os.path.dirname(__file__), 'telegram_auth_token.txt')
with open(token_file_path, 'r') as file:
    TELEGRAM_TOKEN = file.readline().strip()

# Создаем объект бота для обработки заказов
bot_orders = Bot(token=TELEGRAM_TOKEN)
dispatcher_orders = Dispatcher(bot_orders)

# Обработчики команд для обработки заказов
@dispatcher_orders.message_handler(commands=['start'])
async def handle_start(message: types.Message):
    await message.answer("Добро пожаловать! Этот бот поможет вам сделать заказ через наш сайт.")

# Другие обработчики команд и сообщений для заказов

# Запускаем бота
async def start_bot_orders():
    try:
        await dispatcher_orders.start_polling()
    except Exception as e:
        print(f"Error starting bot orders: {e}")
