import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async
from mainshop import models
from myshop import settings
from aiogram import Bot, types
import asyncio
# from mainshop.management.commands.telegram_bot_client import Command
from mainshop.management.commands.telegram_bot_client import send_message_to_telegram_client
Order = models.Order
User = models.User
Executor = models.Executor

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

            user = User.objects.filter(telegram_id=telegram_id).first()

            if not user:
                return JsonResponse({'status': 'error', 'message': 'Для создания заказа необходимо авторизоваться'}, status=401)

            order = Order.objects.create(
                subject=subject,
                description=order_description,
                price=price,
                id_client=telegram_id
            )

            order_number = order.id

            message = f"Заказ #{order_number} от @{telegram_id}:\n{order_description}\nТип предмета: {subject}\nЦена: {price}"
            asyncio.run(send_message_to_telegram(message))

            return JsonResponse({'status': 'success', 'order_number': order_number}, status=200)
        except Exception as e:
            print(f"Ошибка: {e}")
            return JsonResponse({'status': 'error'}, status=500)
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def telegram_auth(request):
    if request.method == 'GET':
        token = request.GET.get('token')
        if token:
            user = User.objects.filter(token=token).first()
            if user:
                login(request, user)
                request.session['is_authenticated'] = True
                request.session['telegram_id'] = str(user.telegram_id)
                response = redirect('order_page')
                response.set_cookie('is_authenticated', True)
                response.set_cookie('telegram_id', str(user.telegram_id))
                return response
            else:
                return JsonResponse({'status': 'error', 'message': 'Пользователь не зарегистрирован'}, status=401)
        else:
            return render(request, 'telegram_auth.html')

    elif request.method == 'POST':
        pass


def notify_user(request):
    if request.method == 'GET':
        data = json.loads(request.body)
        order_data = data.get('order')
        order_id = order_data.get('id')
        description = order_data.get('description')
        client_id = order_data.get('id_client')
        executor_id = order_data.get('id_executor')

        user = User.objects.filter(telegram_id=client_id).first()
        if not user:
            return JsonResponse({'status': 'error', 'message': 'Пользователь не найден'}, status=404)
        username = user.username

        executor_name = Executor.objects.filter(telegram_id=executor_id).first()
        if not executor_name:
            return JsonResponse({'status': 'error', 'message': 'Исполнитель не найден'}, status=404)

        message = f"Уважаемый {username}, ваш заказ '{description}' принят пользователем @{executor_name}. \nСпасибо за ваш заказ!"

        try:
            asyncio.run(send_message_to_telegram_client(message, client_id))
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            print(f"Ошибка при отправке уведомления пользователю: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error'}, status=400)

async def send_message_to_telegram(message):
    try:
        bot = Bot(token=settings.TOKEN_ADMIN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        return True
    except Exception as e:
        print(f"Ошибка при отправке сообщения в Telegram: {e}")
        return False

# async def send_message_to_telegram_client(message, chat_id):
#     bot = Bot(token=settings.TOKEN_BOT_CLIENT)
#     keyboard = types.InlineKeyboardMarkup()
#     accept_button = types.InlineKeyboardButton("Принять", callback_data="accept_order")
#     reject_button = types.InlineKeyboardButton("Отклонить", callback_data="reject_order")
#     keyboard.add(accept_button, reject_button)
#
#     try:
#         await bot.send_message(chat_id=chat_id, text=message, reply_markup=keyboard)
#         return True
#     except Exception as e:
#         print(f"Ошибка при отправке сообщения в Telegram: {e}")
#         return False

def profile_view(request):
    telegram_id = request.COOKIES.get('telegram_id')

    if telegram_id:
        try:
            user = User.objects.get(telegram_id=telegram_id)
            orders = Order.objects.filter(id_client=telegram_id)
            return render(request, 'profile.html', {'username': user.username, 'orders': orders})
        except User.DoesNotExist:
            return redirect('telegram_auth')
    else:
        return redirect('telegram_auth')

def delete_order(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
        order.delete()
        return redirect('profile')
    except Order.DoesNotExist:
        return render(request, 'profile.html', {'username': request.user.username, 'orders': Order.objects.filter(user=request.user), 'order_deleted': False})

def order_page(request):
    try:
        telegram_id = request.COOKIES.get('telegram_id', '0')

        if request.COOKIES.get('is_authenticated') is None:
            username = request.user.username
            return render(request, 'order_auth.html', {'username': username})
        else:
            user = User.objects.filter(telegram_id=telegram_id).first()
            if user:
                username = user.username
            else:
                username = "Пользователь" + str(telegram_id)
            return render(request, 'order.html', {'username': username, 'telegram_id': telegram_id})
    except Exception as e:
        print(f"Ошибка: {e}")
        return JsonResponse({'status': 'error'}, status=500)
