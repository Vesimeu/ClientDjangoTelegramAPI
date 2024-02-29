# myshop/mainshop/views.py
import json
import os
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CommandHandler, Updater
import asyncio
from myshop import settings

TELEGRAM_CHAT_ID = '708969494'

markup = InlineKeyboardMarkup([
    [InlineKeyboardButton('Принять заказ', callback_data='accept'),
     InlineKeyboardButton('Отменить заказ', callback_data='decline')]
])

BOT_TOKEN = '7020363948:AAF7oznvRaebiBkGI9Se7tF622_gKt7dbqI'

@csrf_exempt
async def send_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nickname = data['nickname']
            order_description = data['order_description']
            price = data["price"]
            message = f"Заказ от @{nickname}:\n{order_description}\nЦена: {price}"
            print(BOT_TOKEN)
            updater = Updater(BOT_TOKEN)
            updater.bot.send_message(TELEGRAM_CHAT_ID, message, reply_markup=markup)
            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            print(f"Ошибка: {e}")
            return JsonResponse({'status': 'error'}, status=500)
    return JsonResponse({'status': 'error'}, status=400)


def order_page(request):
    # Ваша логика для обработки заказа
    try:
        return render(request, 'order.html')
    except Exception as e:
        print(f"Ошибка: {e}")
        return JsonResponse({'status': 'error'}, status=500)
