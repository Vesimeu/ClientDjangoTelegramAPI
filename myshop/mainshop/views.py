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




token_file_path = os.path.join(os.path.dirname(__file__), 'token.txt')
# Читаем токен из файла
with open(token_file_path, 'r') as file:
    TELEGRAM_TOKEN = file.readline().strip().split('=')[1]

TELEGRAM_CHAT_ID = '708969494'


bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode=None)

@csrf_exempt
def send_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nickname = data['nickname']
            order_description = data['order_description']
            price = data["price"]
            message = f"Заказ от @{nickname}:\n{order_description} \nЦена: {price}"
            bot.send_message(TELEGRAM_CHAT_ID, message)
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