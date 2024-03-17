# myshop/mainshop/views.py
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from mainshop import models
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
            subject = data['subject']
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
                subject=subject,
                description=order_description,
                price=price,
                id_client=telegram_id
            )

            # Получаем номер созданного заказа
            order_number = order.id

            message = f"Заказ #{order_number} от @{telegram_id}:\n{order_description}\nТип предмета: {subject}\nЦена: {price}"
            send_message_to_telegram(message)

            return JsonResponse({'status': 'success', 'order_number': order_number}, status=200)
        except Exception as e:
            print(f"Ошибка: {e}")
            return JsonResponse({'status': 'error'}, status=500)
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def telegram_auth(request):
    if request.method == 'GET':
        # Проверяем значение токена в запросе
        token = request.GET.get('token')
        if token:
            user = User.objects.filter(token=token).first()
            if user:
                login(request, user)
                request.session['is_authenticated'] = True
                request.session['telegram_id'] = str(user.telegram_id)
                # Устанавливаем куки и перенаправляем пользователя на страницу заказа
                response = redirect('order_page')
                response.set_cookie('is_authenticated', True)
                response.set_cookie('telegram_id', str(user.telegram_id))
                return response
            else:
                return JsonResponse({'status': 'error', 'message': 'Пользователь не зарегистрирован'}, status=401)
        else:
            # Если токен отсутствует или пустой, отображаем страницу авторизации/регистрации
            return render(request, 'telegram_auth.html')

    elif request.method == 'POST':
        # Обработка POST-запросов
        # Оставьте ваш текущий код обработки POST-запросов без изменений
        pass

def send_message_to_telegram(message):
    try:
        bot = Bot(token=settings.TOKEN_ADMIN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        return True
    except Exception as e:
        print(f"Ошибка при отправке сообщения в Telegram: {e}")
        return False

def profile_view(request):
    # Здесь необходимо получить информацию о пользователе и передать её в шаблон
    user = request.user  # Получаем текущего пользователя
    return render(request, 'profile.html', {'user': user})


def order_page(request):
    try:
        telegram_id = request.COOKIES.get('telegram_id', '0')
        print(request.session.get('is_authenticated'))

        # Проверяем, авторизован ли пользователь
        if request.session.get('is_authenticated') == None:
            # Получаем имя пользователя и передаем его в шаблон
            username = request.user.username
            return render(request, 'order_auth.html', {'username': username})
        else:
            # Если пользователь не авторизован, используем обычный шаблон order.html
            print(request.COOKIES)
            return render(request, 'order.html', {'telegram_id': telegram_id})
    except Exception as e:
        print(f"Ошибка: {e}")
        return JsonResponse({'status': 'error'}, status=500)