# myshop/mainshop/management/commands/telegram_bot_client.py

import uuid
import json
import requests
from django.core.management.base import BaseCommand
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, Updater
from telegram.utils.request import Request
from myshop import settings
from mainshop import models

Order = models.Order
User = models.User


class TelegramBot:
    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.updater = self._create_updater()

    def _create_updater(self):
        request = Request(connect_timeout=15)
        bot = Bot(request=request, token=self.bot_token)
        return Updater(bot=bot, use_context=True)

    def start(self):
        self.updater.start_polling()
        self.updater.idle()

    def generate_token(self, user_id):
        return uuid.uuid4().hex

    def send_data_to_server(self, user_id, token, chat_id):
        url = 'http://127.0.0.1:8000/telegram_auth/'
        params = {'token': token}
        print("Request data:", params)
        response = requests.get(url, params=params)
        print("Response status code:", response.status_code)

        if response.status_code == 200:
            # Сохраняем токен в базе данных только если пользователь существует
            user = User.objects.filter(telegram_id=user_id).first()
            if user:
                print("Сохранил токен в базу данных")
                user.token = token
                user.save()
                print("Данные успешно отправлены на сервер Django")
            else:
                print("Ошибка: пользователь не найден в базе данных")
                self.send_auth_link_message(chat_id, token)  # Отправить ссылку на авторизацию
        else:
            print("Ошибка при отправке данных на сервер Django:", response.text)
            self.send_auth_link_message(chat_id, token)  # Отправить ссылку на авторизацию


    def send_auth_link_message(self, chat_id, token):
        auth_link = f'http://127.0.0.1:8000/telegram_auth/?token={token}'
        keyboard = [[InlineKeyboardButton("Авторизация", url=auth_link)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.updater.bot.send_message(chat_id=chat_id, text=f"Для авторизации перейдите по ссылке ниже:", reply_markup=reply_markup)

    def handle_go_to_site(self, update: Update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Вы перешли на сайт.")
        user_id = update.effective_user.id
        token = self.generate_token(user_id)
        print(token, user_id)

        # Сохраняем токен в базе данных
        user = User.objects.filter(telegram_id=user_id).first()
        if user:
            user.token = token
            user.save()
            print("Токен успешно сохранен в базе данных")
        else:
            print("Ошибка: пользователь не найден в базе данных")

        # Отправляем данные на сервер Django для авторизации
        self.send_data_to_server(user_id, token, update.effective_chat.id)
        self.send_auth_link_message(update.effective_chat.id, token)


class Command(BaseCommand):
    help = 'Starts the telegram bot for customers.'

    def handle(self, *args, **options):
        bot_token = settings.TOKEN_BOT_CLIENT
        telegram_bot = TelegramBot(bot_token)
        dp = telegram_bot.updater.dispatcher

        # Обработчик команды /start
        def start(update: Update, context):
            user_id = update.effective_user.id
            user = User.objects.filter(telegram_id=user_id).first()

            if user:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Вы уже зарегистрированы.")
            else:
                keyboard = [[InlineKeyboardButton("Регистрация", callback_data='registration')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="Привет! Для регистрации нажмите на кнопку ниже.",
                                         reply_markup=reply_markup)

        # Обработчик команды /auth
        def auth(update: Update, context):
            user_id = update.effective_user.id
            user = User.objects.filter(telegram_id=user_id).first()

            if user:
                token = telegram_bot.generate_token(user_id)
                telegram_bot.send_auth_link_message(update.effective_chat.id, token)
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Вы еще не зарегистрированы.")

        # Обработчик команды /reg
        def reg(update: Update, context):
            user_id = update.effective_user.id
            user = User.objects.filter(telegram_id=user_id).first()

            if user:
                auth(update, context)  # Перенаправляем на авторизацию, если пользователь уже зарегистрирован
            else:
                handle_registration(update, context)  # Регистрируем, если пользователь не зарегистрирован

        def handle_registration(update: Update, context):
            user_id = update.effective_user.id
            user = User.objects.filter(telegram_id=user_id).first()

            if user:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Вы уже зарегистрированы.")
            else:
                token = telegram_bot.generate_token(user_id)
                telegram_bot.send_data_to_server(user_id, token)
                telegram_bot.send_auth_link_message(update.effective_chat.id, token)

        dp.add_handler(CommandHandler('start', start))
        dp.add_handler(CommandHandler('auth', auth))
        dp.add_handler(CommandHandler('reg', reg))
        dp.add_handler(CallbackQueryHandler(handle_registration, pattern='registration'))
        dp.add_handler(CommandHandler('go_to_site', telegram_bot.handle_go_to_site))

        telegram_bot.start()
