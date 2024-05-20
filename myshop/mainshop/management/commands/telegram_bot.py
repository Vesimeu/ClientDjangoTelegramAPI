import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import requests
from channels.db import database_sync_to_async
from django.core.management import BaseCommand
from myshop import settings
from mainshop.models import Order, Executor

REGISTRATION_PASSWORD = "222333"


class RegistrationStates(StatesGroup):
    waiting_for_password = State()
    waiting_for_information = State()


class Command(BaseCommand):
    help = 'Starts the telegram bot for orders.'

    def handle(self, *args, **options):
        bot_token = settings.TOKEN_ADMIN
        telegram_bot = TelegramBot(bot_token)
        telegram_bot.start_bot()


class TelegramBot:
    def __init__(self, bot_token):
        self.bot = Bot(token=bot_token)
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        self.dp.middleware.setup(LoggingMiddleware())

        # Регистрация обработчиков команд
        self.dp.register_message_handler(self.start, commands=['start'])
        self.dp.register_message_handler(self.help, commands=['help'])
        self.dp.register_message_handler(self.accept_order, commands=['accept'])
        self.dp.register_message_handler(self.decline_order, commands=['decline'])
        self.dp.register_message_handler(self.order_list, commands=['order_list'])
        self.dp.register_message_handler(self.order_list, text=['Список доступных заказов'])
        self.dp.register_message_handler(self.order_active, commands=['order_active'])
        self.dp.register_message_handler(self.order_active, text=['Список активных заказов'])

        # Обработчики состояний
        self.dp.register_message_handler(self.check_password, state=RegistrationStates.waiting_for_password)
        self.dp.register_message_handler(self.get_information, state=RegistrationStates.waiting_for_information)

        # Обработчики инлайн-кнопок
        self.dp.register_callback_query_handler(self.take_order_callback, lambda c: c.data.startswith('take_order_'))

        # Инициализация клиентского бота
        self.client_bot_url = f"https://localhost:8000/notify_user/"

    async def start(self, message: types.Message):
        telegram_id = message.from_user.id
        username = message.from_user.username

        if not await self.is_registered(telegram_id):
            await message.answer("Для доступа к боту вам нужно зарегистрироваться. Пожалуйста, введите пароль:")
            await RegistrationStates.waiting_for_password.set()
        else:
            await message.answer(f"Добро пожаловать, {username}!",
                                 reply_markup=self.main_keyboard())

    async def check_password(self, message: types.Message, state: FSMContext):
        if message.text == REGISTRATION_PASSWORD:
            await message.answer("Пароль принят. Пожалуйста, введите информацию о себе:")
            await RegistrationStates.next()
        else:
            await message.answer("Неверный пароль. Попробуйте еще раз:")

    def main_keyboard(self):
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("Список доступных заказов", callback_data="order_list"))
        keyboard.add(KeyboardButton("Список активных заказов", callback_data="order_active"))
        return keyboard

    async def get_information(self, message: types.Message, state: FSMContext):
        telegram_id = message.from_user.id
        username = message.from_user.username
        information = message.text

        await self.register_executor(telegram_id, username, information)
        await message.answer("Вы успешно зарегистрированы! Теперь вам доступны все команды.",
                             reply_markup=self.main_keyboard())
        await state.finish()

    async def help(self, message: types.Message):
        help_message = "/accept {number} - принять заказ\n/decline {number} - отказать\n/order_list - список заказов."
        await message.answer(help_message)

    async def decline_order(self, message: types.Message):
        if not await self.is_registered(message.from_user.id):
            await message.answer("Вы должны зарегистрироваться, чтобы использовать эту команду.")
            return

        args = message.get_args().split()
        if args:
            order_id = args[0]
            try:
                order = await self.get_order(order_id)
                await self.decline_order_async(order)
                await message.answer(f"Заказ #{order_id} отклонен.")
            except Order.DoesNotExist:
                await message.answer("Заказ с указанным номером не найден.")
        else:
            await message.answer("Вы не указали номер заказа.")

    async def order_list(self, message: types.Message):
        if not await self.is_registered(message.from_user.id):
            await message.answer("Вы должны зарегистрироваться, чтобы использовать эту команду.")
            return

        orders = await self.get_all_orders()
        if orders:
            for order in orders:
                order_text = (f"Заказ #{order.id}:\n"
                              f"Предмет: {order.subject}\n"
                              f"Описание: {order.description}\n"
                              f"Цена: {order.price}\n"
                              f"Статус принятия: {'Принят' if order.accepted else 'Не принят'}\n")
                status_orders_text = ''
                if order.status_orders == 'pending':
                    status_orders_text = 'В ожидании'
                elif order.status_orders == 'in_progress':
                    status_orders_text = 'В процессе'
                elif order.status_orders == 'completed':
                    status_orders_text = 'Завершен'
                order_text += f"Статус заказа: {status_orders_text}\n"
                order_text += f"ID клиента: {order.id_client}\n"
                order_text += f"ID исполнителя: {order.id_executor}\n"
                order_text += f"Дата создания: {order.created_at}\n\n"
                keyboard = InlineKeyboardMarkup()
                keyboard.add(InlineKeyboardButton("Взять", callback_data=f"take_order_{order.id}"))
                await message.answer(order_text, reply_markup=keyboard)
        else:
            await message.answer("Список заказов пуст.")

    async def order_active(self, message: types.Message):
        if not await self.is_registered(message.from_user.id):
            await message.answer("Вы должны зарегистрироваться, чтобы использовать эту команду.")
            return

        telegram_id = message.from_user.id
        active_orders = await self.get_active_orders(telegram_id)
        if active_orders:
            active_order_list_message = "Список активных заказов:\n"
            for order in active_orders:
                active_order_list_message += f"Заказ #{order.id}:\n"
                active_order_list_message += f"Предмет: {order.subject}\n"
                active_order_list_message += f"Описание: {order.description}\n"
                active_order_list_message += f"Цена: {order.price}\n"
                active_order_list_message += f"Дата создания: {order.created_at}\n\n"
            await message.answer(active_order_list_message)
        else:
            await message.answer("У вас нет активных заказов.")

    async def accept_order(self, message: types.Message):
        if not await self.is_registered(message.from_user.id):
            await message.answer("Вы должны зарегистрироваться, чтобы использовать эту команду.")
            return
        print(message)

        args = message.get_args().split()
        if args:
            order_id = args[0]
            try:
                order = await self.get_order(order_id)
                await self.process_order(order)
                await self.add_executor(order, message.chat.id)
                await self.notify_user(order)
                await message.answer(f"Заказ #{order_id} принят.")
            except Order.DoesNotExist:
                await message.answer("Заказ с указанным номером не найден.")
        else:
            await message.answer("Вы не указали номер заказа.")

    async def take_order_callback(self, callback_query: types.CallbackQuery):
        order_id = callback_query.data.split('_')[-1]
        telegram_id = callback_query.from_user.id
        try:
            order = await self.get_order(order_id)
            await self.process_order(order)
            await self.add_executor(order, telegram_id)
            await self.notify_user(order)
            await callback_query.message.edit_text(f"Заказ #{order_id} принят.")
        except Order.DoesNotExist:
            await callback_query.answer("Заказ с указанным номером не найден.", show_alert=True)

    async def notify_user(self, order):
        order_data = {
            "id": order.id,
            "description": order.description,
            "id_client": order.id_client,
            "id_executor": order.id_executor,
        }
        headers = {
            "Referer": "https://127.0.0.1:8000/notify_user/"
        }
        try:
            response = requests.get(self.client_bot_url, json={"order": order_data}, headers=headers, verify=False)
            if response.status_code != 200:
                raise Exception(f"Ошибка при отправке уведомления: {response.text}")
        except Exception as e:
            print(f"Ошибка при отправке уведомления пользователю: {e}")


    @database_sync_to_async
    def get_order(self, order_id):
        return Order.objects.get(id=order_id)

    @database_sync_to_async
    def decline_order_async(self, order):
        order.accepted = False
        order.save()
        # Найдем исполнителя, который принял данный заказ
        executor = Executor.objects.filter(active_orders=order).first()
        if executor:
            # Удалим заказ из списка активных заказов у исполнителя
            executor.active_orders.remove(order)

    @database_sync_to_async
    def process_order(self, order):
        order.accepted = True
        order.save()

    @database_sync_to_async
    def add_executor(self, order, chat_id):
        executor = Executor.objects.get(telegram_id=chat_id)
        order.id_executor = executor.telegram_id
        order.save()
        executor.active_orders.add(order)

    @database_sync_to_async
    def get_all_orders(self):
        return list(Order.objects.filter(accepted=False))

    @database_sync_to_async
    def get_active_orders(self, telegram_id):
        executor = Executor.objects.get(telegram_id=telegram_id)
        return list(executor.active_orders.all())

    @database_sync_to_async
    def is_registered(self, telegram_id):
        return Executor.objects.filter(telegram_id=telegram_id).exists()

    @database_sync_to_async
    def register_executor(self, telegram_id, username, information):
        executor = Executor(telegram_id=telegram_id, username=username, information=information)
        executor.save()

    def start_bot(self):
        executor.start_polling(self.dp, skip_updates=True)


if __name__ == "__main__":
    bot_token = settings.TOKEN_ADMIN
    telegram_bot = TelegramBot(bot_token)
    telegram_bot.start_bot()
