import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from channels.db import database_sync_to_async
from django.core.management import BaseCommand

from myshop import settings
from mainshop.models import Order

class Command(BaseCommand):
    help = 'Starts the telegram bot for orders.'

    def handle(self, *args, **options):
        bot_token = settings.TOKEN_ADMIN
        telegram_bot = TelegramBot(bot_token)
        telegram_bot.start_bot()

class TelegramBot:
    def __init__(self, bot_token):
        self.bot = Bot(token=bot_token)
        self.dp = Dispatcher(self.bot)
        self.dp.middleware.setup(LoggingMiddleware())

        # Регистрация обработчиков команд
        self.dp.register_message_handler(self.start, commands=['start'])
        self.dp.register_message_handler(self.help, commands=['help'])
        self.dp.register_message_handler(self.accept_order, commands=['accept'])
        self.dp.register_message_handler(self.decline_order, commands=['decline'])
        self.dp.register_message_handler(self.order_list, commands=['order_list'])

    async def start(self, message: types.Message):
        await message.answer("Добро пожаловать! Этот бот поможет вам сделать заказ через наш сайт.")

    async def help(self, message: types.Message):
        help_message = "/accept {number} - принять заказ\n/decline {number} - отказать\n/order_list - список заказов."
        await message.answer(help_message)

    async def accept_order(self, message: types.Message):
        args = message.get_args().split()
        if args:
            order_id = args[0]
            try:
                order = await self.get_order(order_id)
                await self.process_order(order)
                await message.answer(f"Заказ #{order_id} принят.")
            except Order.DoesNotExist:
                await message.answer("Заказ с указанным номером не найден.")
        else:
            await message.answer("Вы не указали номер заказа.")

    @database_sync_to_async
    def get_order(self, order_id):
        return Order.objects.get(id=order_id)

    @database_sync_to_async
    def process_order(self, order):
        order.accepted = True
        order.save()

    async def decline_order(self, message: types.Message):
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

    @database_sync_to_async
    def decline_order_async(self, order):
        order.accepted = False
        order.save()

    @database_sync_to_async
    def get_all_orders(self):
        return list(Order.objects.all())

    async def order_list(self, message: types.Message): #Тут упал бот
        orders = await self.get_all_orders()
        print(orders)
        if orders:
            order_list_message = "Список заказов:\n"
            for order in orders:
                order_list_message += f"Заказ #{order.id}:\n"
                order_list_message += f"Предмет: {order.subject}\n"
                order_list_message += f"Описание: {order.description}\n"
                order_list_message += f"Цена: {order.price}\n"
                order_list_message += f"Статус принятия: {'Принят' if order.accepted else 'Не принят'}\n"
                order_list_message += f"Статус заказа: {'Активен' if order.status_orders else 'Не активен'}\n"
                order_list_message += f"ID клиента: {order.id_client}\n"
                order_list_message += f"ID исполнителя: {order.id_executor}\n"
                order_list_message += f"Дата создания: {order.created_at}\n\n"
            await message.answer(order_list_message)
        else:
            await message.answer("Список заказов пуст.")

    def start_bot(self):
        executor.start_polling(self.dp, skip_updates=True)
