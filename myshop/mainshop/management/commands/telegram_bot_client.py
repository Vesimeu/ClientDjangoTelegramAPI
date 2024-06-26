import uuid
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.types.web_app_info import WebAppInfo
import json
# from ... import views
from django.http import HttpResponse
from channels.db import database_sync_to_async
from django.core.management import BaseCommand
from asgiref.sync import sync_to_async
import urllib3
urllib3.disable_warnings() # disable ssl warning

main_url = '127.0.0.1:8000'
from myshop import settings
from mainshop.models import User, Order, Executor



class Command(BaseCommand):
    help = 'Это телеграмм бот для пользователей. Сделать клиент получает уведомление о его заказе. Может авторизоваться и зарегестрироваться на сайт..'

    def handle(self, *args, **options):
        bot_token = settings.TOKEN_BOT_CLIENT
        telegram_bot = TelegramBot(bot_token)
        telegram_bot.start_bot()

class TelegramBot:
    def __init__(self, bot_token):
        self.bot = Bot(token=bot_token)
        self.dp = Dispatcher(self.bot)
        self.dp.middleware.setup(LoggingMiddleware())

        # Регистрация обработчиков команд
        self.dp.register_message_handler(self.start, commands=['start'])
        self.dp.register_message_handler(self.auth, commands=['auth'])
        self.dp.register_message_handler(self.reg, commands=['reg'])
        self.dp.register_message_handler(self.my_orders, commands=['my_orders'])
        self.dp.register_message_handler(self.my_orders, text=['Список заказов'])
        self.dp.register_callback_query_handler(self.handle_callback, lambda c: True)
        self.dp.register_message_handler(self.handle_go_to_site, commands=['go_to_site'])

    async def handle_callback(self, query: types.CallbackQuery):
        data = query.data
        if data.startswith('accept_order_'):
            order_id = data.split('_')[-1]
            await self.handle_accept_order(query.message, order_id)
        elif data.startswith('reject_order_'):
            order_id = data.split('_')[-1]
            await self.handle_reject_order(query.message, order_id)
        elif data == 'registration':
            await self.handle_registration(query.message)
        await query.answer()  # Обязательно отвечайте на callback, чтобы убрать "крутящийся" индикатор в Telegram

    async def handle_accept_order(self, message: types.Message, order_id):
        order = await self.get_order(order_id)
        await self.accept_order(order)
        await message.answer("Вы успешно приняли заказ!")

    async def handle_reject_order(self, message: types.Message, order_id):
        order = await self.get_order(order_id)
        await self.decline_order(order)
        await message.answer("Вы отклонили заказ.")

    async def my_orders(self, message: types.Message):
        user_id = message.from_user.id
        user = await sync_to_async(User.objects.filter)(telegram_id=user_id)
        user = await sync_to_async(lambda queryset: queryset.first())(user)

        if user:
            orders = await sync_to_async(Order.objects.filter)(id_client=user_id)
            orders = await sync_to_async(list)(orders)  # Преобразуем QuerySet в список
            if orders:
                for order in orders:
                    # Собираем текст заказа с дополнительной информацией
                    order_text = (
                        f"Заказ ID: {order.id}\n"
                        f"Предмет: {order.subject}\n"
                        f"Описание: {order.description}\n"
                        f"Цена: {order.price}\n"
                    )
                    if order.accepted:
                        executor_info = await self.get_executor_info(order.id_executor)
                        if executor_info:
                            order_text += (
                                f"Фрилансер: @{executor_info['username']}\n"
                                f"Информация: {executor_info['information']}\n"
                            )
                    await message.answer(order_text)
            else:
                await message.answer("У вас нет заказов.")
        else:
            await message.answer("Вы не авторизованы. Пожалуйста, зарегистрируйтесь или авторизуйтесь.")
    def main_keyboard(self):
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("Список заказов"))
        return keyboard

    async def start(self, message: types.Message):
        user_id = message.from_user.id
        username = message.from_user.username
        user = await sync_to_async(User.objects.filter)(telegram_id=user_id)
        user = await sync_to_async(lambda queryset: queryset.first())(user)

        if user:
            await message.answer(f"Добро пожаловать обратно {username}!",
                                 reply_markup=self.main_keyboard())
            await self.auth(message)
        else:
            keyboard = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton("Регистрация", callback_data='registration')
            keyboard.add(button)
            await message.answer("Привет! Для регистрации нажмите на кнопку ниже.", reply_markup=keyboard)

    async def auth(self, message: types.Message):
        user_id = message.from_user.id
        user = await sync_to_async(User.objects.filter)(telegram_id=user_id)
        user = await sync_to_async(lambda queryset: queryset.first())(user)

        if user:
            # token = self.generate_token(user_id)
            await self.handle_go_to_site(message)
        else:
            await message.answer("Вы еще не зарегистрированы.")

    async def reg(self, message: types.Message):
        user_id = message.from_user.id
        user = await sync_to_async(User.objects.filter)(telegram_id=user_id)
        user = await sync_to_async(lambda queryset: queryset.first())(user)

        if user:
            await self.auth(message)  # Перенаправляем на авторизацию, если пользователь уже зарегистрирован
        else:
            await self.handle_registration(message)  # Регистрируем, если пользователь не зарегистрирован


    async def handle_registration(self, message: types.Message):
        user_id = message.from_user.id
        username = message.from_user.username  # Получаем username из сообщения

        # Создаем пользователя с telegram_id и username
        user, created = await sync_to_async(User.objects.get_or_create)(
            telegram_id=user_id,
            defaults={'username': username}
        )

        if created:
            # Если пользователь был создан в базе данных, создаем и сохраняем токен
            token = self.generate_token(user_id)
            await sync_to_async(self.save_user_token)(user, token)

            # Отправляем данные на сервер Django
            await self.send_data_to_server(user_id, token, message.chat.id)
            await self.send_auth_link_message(message.chat.id, token)
        else:
            # Если пользователь уже существует, выводим сообщение об ошибке
            await message.answer("Ошибка: пользователь уже зарегистрирован.")


    async def handle_go_to_site(self, message: types.Message):
        await message.answer("Можете переходить на сайт!")
        user_id = message.from_user.id
        token = self.generate_token(user_id)
        user = await sync_to_async(User.objects.filter)(telegram_id=user_id)
        user = await sync_to_async(lambda queryset: queryset.first())(user)

        if user:
            await self.save_user_token(user, token)
            # await message.answer("Ваш токен успешно сохранен в базе данных")
        else:
            await message.answer("Ошибка: пользователь не найден в базе данных")
            await self.reg(message)

        await self.send_data_to_server(user_id, token, message.chat.id)
        await self.send_auth_link_message(message.chat.id, token)


    async def send_auth_link_message(self, chat_id, token):
        auth_link = f'https://{main_url}/telegram_auth/?token={token}'


        # Создаем клавиатуру
        keyboard = types.InlineKeyboardMarkup()

        # Добавляем кнопку "Авторизация"
        website_button = types.InlineKeyboardButton("Авторизация", url=auth_link)
        keyboard.add(website_button)

        # Добавляем кнопку "Open in WebApp"
        webapp_button = types.InlineKeyboardButton("Open in WebApp", web_app=WebAppInfo(url=auth_link))
        keyboard.row(webapp_button)  # Добавляем кнопку в ту же строку, что и кнопка "Авторизация"

        # Отправляем сообщение с клавиатурой
        await self.bot.send_message(chat_id=chat_id, text="Для авторизации перейдите по ссылке ниже:",
                                    reply_markup=keyboard)

    def generate_token(self, user_id):
        return uuid.uuid4().hex

    @database_sync_to_async
    def save_user_token(self, user, token):
        user.token = token
        user.save()

    @database_sync_to_async
    def decline_order(self, order):  # Изменить. Это функция для отмены заказа
        order.accepted = False
        order.save()

    @database_sync_to_async
    def get_executor_info(self, executor_id):
        try:
            executor = Executor.objects.get(telegram_id=executor_id)
            return {
                "username": executor.username,
                "information": executor.information
            }
        except Executor.DoesNotExist:
            return None

    @database_sync_to_async
    def get_all_orders(self, order_id):
        try:
            # Возвращаем все заказы, удовлетворяющие условиям фильтрации
            return Order.objects.filter(id_client=order_id)
        except Order.DoesNotExist:
            return None

    @database_sync_to_async  # Изменить. Это функция для принятия заказа.
    def accept_order(self, order):
        order.status_orders = 'in_progress'
        order.save()

    @database_sync_to_async
    def get_order(self, order_id):
        return Order.objects.get(id=order_id)

    @database_sync_to_async
    def save_user_token(self, user, token):
        user.token = token
        user.save()

    async def send_data_to_server(self, user_id, token, chat_id):
        url = f'https://{main_url}/telegram_auth/'
        params = {'token': token}
        print("Request data:", params)
        response = requests.get(url, params=params , verify=False)
        print("Response status code:", response.status_code)

        if response.status_code == 200:
            user = await sync_to_async(User.objects.filter)(telegram_id=user_id)
            user = await sync_to_async(lambda queryset: queryset.first())(user)
            if user:
                print("Сохранил токен в базу данных")
                await self.save_user_token(user, token)
                print("Данные успешно отправлены на сервер Django")
            else:
                print("Ошибка: пользователь не найден в базе данных")
                await self.send_auth_link_message(chat_id, token)
        else:
            print("Ошибка при отправке данных на сервер Django:", response.text)
            await self.send_auth_link_message(chat_id, token)

    def start_bot(self):
        executor.start_polling(self.dp, skip_updates=False)