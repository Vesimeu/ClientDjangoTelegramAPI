import json
from urllib.request import Request
from telegram.error import TimedOut
from timeout_decorator import timeout
from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from telegram import Bot
import os
import telebot
import asyncio
from asgiref.sync import sync_to_async



token_file_path = os.path.join(os.path.dirname(__file__), 'token.txt')
# Читаем токен из файла
with open(token_file_path, 'r') as file:
    TELEGRAM_TOKEN = file.readline().strip().split('=')[1]

TELEGRAM_CHAT_ID = '708969494'


bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode=None)

# @csrf_exempt
# def send_order_notification(request):
#     if request.method == 'POST':
#         message = "Поступил новый заказ!"
#         bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
#         return JsonResponse({'status': 'success'}, status=200)
#     else:
#         return JsonResponse({'status': 'bad request'}, status=400)

# Эта функция будет вызываться для отправки сообщения в Telegram
# Функция для отправки сообщения в Telegram
# async def send_telegram_message(chat_id, text):
#     try:
#         await bot.send_message(chat_id=chat_id, text=text)
#     except TimedOut as e:
#         print(f"Ошибка отправки уведомления: {e}")

@csrf_exempt
def send_order(request):
    if request.method == 'POST':
        try:
            order_description = json.loads(request.body)['order_description']
            bot.send_message(TELEGRAM_CHAT_ID, f"Поступил новый заказ:\n{order_description}")
            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            print(f"Ошибка: {e}")
            return JsonResponse({'status': 'error'}, status=500)
    return JsonResponse({'status': 'error'}, status=400)

def order_page(request):
    # Ваша логика для обработки заказа
    try:
        return render(request, 'order.html')
    except:
        print("что-то пошло не так")