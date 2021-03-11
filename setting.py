import os

BOT_TOKEN = '1291846106:AAEoo_HoGHFEGzBMvwf16quTyMvk-OirAzU'
HEROKU_APP_NAME = 'kn19homework'

# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{BOT_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = 5000