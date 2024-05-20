import requests

bot_token = '7020363948:AAF7oznvRaebiBkGI9Se7tF622_gKt7dbqI'
webhook_url = 'YOUR_WEBHOOK_URL'
allowed_updates = ["message", "callback_query"]

url = f'https://api.telegram.org/bot{bot_token}/setWebhook'
data = {
    'allowed_updates': allowed_updates
}

response = requests.post(url, json=data)
print(response.json())