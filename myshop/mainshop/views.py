from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Bot
import os
import asyncio


token_file_path = os.path.join(os.path.dirname(__file__), 'token.txt')
# Читаем токен из файла
with open(token_file_path, 'r') as file:
    TELEGRAM_TOKEN = file.readline().strip().split('=')[1]

TELEGRAM_CHAT_ID = '708969494'

bot = Bot(token=TELEGRAM_TOKEN)

# @csrf_exempt
# def send_order_notification(request):
#     if request.method == 'POST':
#         message = "Поступил новый заказ!"
#         bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
#         return JsonResponse({'status': 'success'}, status=200)
#     else:
#         return JsonResponse({'status': 'bad request'}, status=400)

@csrf_exempt
async def send_order(request):
    if request.method == 'POST':
        try:
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Поступил новый заказ!")
            return JsonResponse({'status': 'success'}, status=200)
        except TimedOut as e:
            # Обработка исключения таймаута
            print(f"Ошибка отправки уведомления: {e}")
            return JsonResponse({'status': 'timeout error'}, status=500)
    return JsonResponse({'status': 'error'}, status=400)
def order_page(request):
    # Ваша логика для обработки заказа
    try:
        return render(request, 'order.html')
    except:
        print("что-то пошло не так")