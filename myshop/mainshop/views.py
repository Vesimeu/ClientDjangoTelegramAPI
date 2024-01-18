from django.shortcuts import render

def order_page(request):
    # Ваша логика для обработки заказа
    return render(request, 'order.html')