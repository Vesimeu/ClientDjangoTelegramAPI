# myshop/mainshop/views.py
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from . import models# Импорт модели Order из вашего приложения
from myshop import settings
from telegram import Bot

Order = models.Order
User = models.User

TELEGRAM_CHAT_ID = '708969494'


@csrf_exempt
def send_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nickname = data['nickname']
            order_description = data['order_description']
            price = data["price"]
            telegram_id = data["id_client"]

            # Проверяем, существует ли пользователь с указанным Telegram ID
            user = User.objects.filter(telegram_id=telegram_id).first()

            # Если пользователь не существует, возвращаем ошибку
            if not user:
                return JsonResponse({'status': 'error', 'message': 'Для создания заказа необходимо авторизоваться'}, status=401)

            # Создаем заказ и сохраняем его в базе данных
            order = Order.objects.create(
                nickname=nickname,
                description=order_description,
                price=price,
                id_client=telegram_id
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

def telegram_auth(request):
    if request.method == 'GET':
        return render(request, 'telegram_auth.html')
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            telegram_id = data['id']

            user = User.objects.filter(telegram_id=telegram_id).first()

            if user:
                login(request, user)
                return redirect('order_page')
            else:
                user = User.objects.create(telegram_id=telegram_id)
                login(request, user)
                return redirect('order_page')
        except Exception as e:
            print(f"Ошибка: {e}")
            return JsonResponse({'status': 'error', 'message': 'Произошла ошибка'})
    return JsonResponse({'status': 'error', 'message': 'Неверный запрос'})

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
