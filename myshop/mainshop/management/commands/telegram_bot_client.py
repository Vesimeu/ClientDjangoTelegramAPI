from django.core.management.base import BaseCommand
from telegram import Bot, Update, InlineKeyboardButton , InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, CallbackQueryHandler
from telegram.utils.request import Request
from myshop import settings  # Импорт настроек
from mainshop import models
Order = models.Order
User = models.User


class Command(BaseCommand):
    help = 'Starts the telegram bot for customers.'

    def handle(self, *args, **options):
        # Создаем объект запроса с использованием прокси
        request = Request(connect_timeout=15)

        # Создаем объект бота с использованием запроса и токена
        bot = Bot(request=request, token=settings.TOKEN_BOT_CLIENT)
        print(bot)

        # Обработчик команды /start
        def start(update: Update, context):
            user_id = update.effective_user.id
            user = User.objects.filter(telegram_id=user_id).first()

            if user:
                # Пользователь уже существует
                context.bot.send_message(chat_id=update.effective_chat.id, text="Добро пожаловать обратно!")
            else:
                # Пользователь не существует
                # Отправляем кнопку регистрации
                keyboard = [[InlineKeyboardButton("Регистрация", callback_data='registration')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Для регистрации нажмите на кнопку ниже.", reply_markup=reply_markup)

        # Обработчик нажатия кнопки регистрации
        def registration_button(update: Update, context):
            user_id = update.effective_user.id
            user = User.objects.filter(telegram_id=user_id).first()

            if user:
                # Пользователь уже существует
                context.bot.send_message(chat_id=update.effective_chat.id, text="Вы уже зарегистрированы.")
            else:
                # Пользователь не существует
                # Создаем нового пользователя
                user = User.objects.create(telegram_id=user_id, name=update.effective_user.first_name)

                # Отправляем сообщение об успешной регистрации
                context.bot.send_message(chat_id=update.effective_chat.id, text="Вы успешно зарегистрированы!")

        # Обработчик сообщений для регистрации пользователя
        def registration(update: Update, context):
            context.bot.send_message(chat_id=update.effective_chat.id, text="Извините, регистрация через сообщения больше не поддерживается. Пожалуйста, используйте кнопку регистрации.")

        # Обработчик всех остальных сообщений
        def message(update: Update, context):
            context.bot.send_message(chat_id=update.effective_chat.id, text="Извините, я не понимаю эту команду.")

        # Обработчик неизвестной команды
        def unknown(update: Update, context):
            context.bot.send_message(chat_id=update.effective_chat.id, text="Извините, я не понимаю эту команду.")

        # Создаем и регистрируем диспетчер для обработки команд
        updater = Updater(bot=bot, use_context=True)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler('start', start))
        dp.add_handler(CallbackQueryHandler(registration_button, pattern='registration'))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, registration))  # Registration through messages is disabled
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message))
        dp.add_handler(CommandHandler('unknown', unknown))

        # Запускаем бота
        updater.start_polling()
        updater.idle()