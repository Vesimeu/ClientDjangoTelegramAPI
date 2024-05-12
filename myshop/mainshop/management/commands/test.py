import uuid
import requests
import asyncio
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.types import Message, BotCommand
from aiogram.filters import Command
# from aiogram.contrib.middlewares.logging import LoggingMiddleware
# from aiogram.utils import executor
from aiogram.types.web_app_info import WebAppInfo
from django.core.management import BaseCommand
from asgiref.sync import sync_to_async
import logging
#
# from mainshop.models import User


token = "7020363948:AAF7oznvRaebiBkGI9Se7tF622_gKt7dbqI"


router = Router()

@router.message(Command(commands=["start"]))
async def command_start(message: Message):
    user_id = message.from_user.id
    # user = await sync_to_async(User.objects.filter)(telegram_id=user_id)
    # user = await sync_to_async(lambda queryset: queryset.first())(user)
    print(user_id)


async def main():
    bot = Bot(token, parse_mode='HTML')
    dp = Dispatcher()
    dp.include_routers(router)
    # await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())