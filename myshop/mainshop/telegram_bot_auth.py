# myshop/mainshop/telegram_bot_auth.py
import os
import asyncio
from aiogram import Bot, Dispatcher, executor, types

# Читаем токен из файла
token_file_path = os.path.join(os.path.dirname(__file__), 'telegram_auth_token_auth.txt')
with open(token_file_path, 'r') as file:
    TELEGRAM_TOKEN_AUTH = file.readline().strip()

# Создаем объект бота для авторизации и регистрации
bot_auth = Bot(token=TELEGRAM_TOKEN_AUTH)
dispatcher_auth = Dispatcher(bot_auth)

# Обработчики команд для авторизации и регистрации
@dispatcher_auth.message_handler(commands=['start'])
async def handle_start_auth(message: types.Message):
    await message.answer("Привет! Этот бот поможет тебе авторизоваться на нашем сайте.")

# Другие обработчики команд и сообщений для авторизации и регистрации

# Запускаем бота для авторизации
async def start_bot_auth():
    try:
        await dispatcher_auth.start_polling()
    except Exception as e:
        print(f"Error starting bot auth: {e}")
