from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo



bot = Bot(token="7020363948:AAF7oznvRaebiBkGI9Se7tF622_gKt7dbqI")
dp = Dispatcher(bot)

@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    await message.answer("Let's begin translate",
reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="translate",
web_app=WebAppInfo(url="https://translate.yandex.ru/"))))

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)