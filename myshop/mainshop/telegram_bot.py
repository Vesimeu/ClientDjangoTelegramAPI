# myshop/mainshop/telegram_bot.py

import os
import telebot

# Читаем токен из файла
token_file_path = os.path.join(os.path.dirname(__file__), 'telegram_auth_token.txt')
# Читаем токен из файла
with open(token_file_path, 'r') as file:
    TELEGRAM_TOKEN = file.readline().strip()

# Создаем объект бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Этот бот поможет тебе авторизоваться на нашем сайте.")

# Другие обработчики сообщений и команд можно добавить по мере необходимости

# Не запускаем бота здесь, запуск будет произведен в файле views.py
