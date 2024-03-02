# myshop/mainshop/views.py
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from . import models# Импорт модели Order из вашего приложения
from myshop import settings
from telegram import Bot

Order = models.Order

TELEGRAM_CHAT_ID = '708969494'


@csrf_exempt
def send_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nickname = data['nickname']
            order_description = data['order_description']
            price = data["price"]

            # Создаем заказ и сохраняем его в базе данных
            order = Order.objects.create(
                nickname=nickname,
                description=order_description,
                price=price
            )

            # Получаем номер созданного заказа
            order_number = order.id

            message = f"Заказ #{order_number} от @{nickname}:\n{order_description}\nЦена: {price}"
            send_message_to_telegram(message)  # Отправляем сообщение в Telegram

            return JsonResponse({'status': 'success', 'order_number': order_number}, status=200)
        except Exception as e:
            print(f"Ошибка: {e}")
            return JsonResponse({'status': 'error'}, status=500)
    return JsonResponse({'status': 'error'}, status=400)

def send_message_to_telegram(message):
    try:
        bot = Bot(token=settings.TOKEN_ADMIN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        return True
    except Exception as e:
        print(f"Ошибка при отправке сообщения в Telegram: {e}")
        return False

def order_page(request):
    # Логика для отображения страницы заказа
    try:
        return render(request, 'order.html')
    except Exception as e:
        print(f"Ошибка: {e}")
        return JsonResponse({'status': 'error'}, status=500)
