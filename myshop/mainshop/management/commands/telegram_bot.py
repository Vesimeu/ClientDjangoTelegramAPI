# myshop/management/commands/telegram_bot.py
from django.core.management.base import BaseCommand
from telegram import Bot, Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, CallbackContext
from telegram.utils.request import Request
from django.utils import timezone
from myshop import settings  # Импорт настроек
from mainshop import models
Order = models.Order
class Command(BaseCommand):
    help = 'Starts the telegram bot for orders.'

    def handle(self, *args, **options):
        # Создаем объект запроса с использованием прокси
        request = Request(connect_timeout=15)

        # Создаем объект бота с использованием запроса и токена
        bot = Bot(request=request, token=settings.TOKEN_ADMIN)
        print(bot)

        # Обработчик команды /start
        def start(update: Update, context: CallbackContext):
            update.message.reply_text("Добро пожаловать! Этот бот поможет вам сделать заказ через наш сайт.")

        # Обработчик команды /accept
        def accept_order(update: Update, context: CallbackContext):
            if context.args:
                order_id = context.args[0]  # Предположим, что аргументом передается ID заказа
                order = Order.objects.get(id=order_id)
                # Здесь вы можете обновить статус заказа в базе данных, например:
                order.status = 'accepted'
                order.save()
                update.message.reply_text(f"Заказ #{order_id} принят.")
            else:
                update.message.reply_text("Вы не указали ID заказа.")

        # Обработчик команды /decline
        def decline_order(update: Update, context: CallbackContext):
            order_id = context.args[0]  # Предположим, что аргументом передается ID заказа
            order = Order.objects.get(id=order_id)
            # Здесь вы можете обновить статус заказа в базе данных, например:
            order.status = 'declined'
            order.save()
            update.message.reply_text(f"Заказ #{order_id} отклонен.")

        def order_list(update: Update, context: CallbackContext):
            orders = Order.objects.all()  # Получаем все заказы из базы данных
            if orders:
                message = "Список заказов:\n"
                for order in orders:
                    message += f"Заказ #{order.id} от @{order.nickname}:\n{order.description}\nЦена: {order.price}\n\n"
            else:
                message = "Список заказов пуст."
            update.message.reply_text(message)

        # Создаем обработчики команд
        start_handler = CommandHandler('start', start)
        accept_handler = CommandHandler('accept', accept_order)
        decline_handler = CommandHandler('decline', decline_order)
        order_list_handler = CommandHandler('order_list', order_list)

        # Создаем и регистрируем диспетчер для обработки команд
        updater = Updater(bot=bot, use_context=True)
        dp = updater.dispatcher
        dp.add_handler(start_handler)
        dp.add_handler(accept_handler)
        dp.add_handler(decline_handler)
        dp.add_handler(order_list_handler)

        # Запускаем бота
        updater.start_polling()
        updater.idle()
