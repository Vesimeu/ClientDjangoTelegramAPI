# myshop/management/commands/telegram_bot.py
from django.core.management.base import BaseCommand
from telegram import Bot, Update
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from telegram.utils.request import Request
from myshop import settings  # Импорт настроек


class Command(BaseCommand):
    help = 'Starts the telegram bot for orders.'

    def handle(self, *args, **options):
        # Создаем объект запроса с использованием прокси
        request = Request(connect_timeout=15)

        # Создаем объект бота с использованием запроса и токена
        bot = Bot(request=request, token=settings.TOKEN_ADMIN)
        print(bot)

        # Обработчик команды /start
        def start(update: Update, context):
            update.message.reply_text("Добро пожаловать! Этот бот поможет вам сделать заказ через наш сайт.")

        # Создаем обработчик команды /start
        start_handler = CommandHandler('start', start)

        # Создаем обработчик неизвестной команды
        unknown_handler = MessageHandler(Filters.command, unknown)

        # Создаем и регистрируем диспетчер для обработки команд
        updater = Updater(bot=bot, use_context=True)
        dp = updater.dispatcher
        dp.add_handler(start_handler)
        dp.add_handler(unknown_handler)

        # Запускаем бота
        updater.start_polling()
        updater.idle()


def unknown(update: Update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Извините, я не понимаю эту команду.")
