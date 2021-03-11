import logging
import csv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.executor import start_webhook
from setting import (BOT_TOKEN, HEROKU_APP_NAME, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_PORT, WEBAPP_HOST)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    if message.text == '/start':
        await message.answer('Бот запущен. Доступные комманды:\n/help')
    if message.text == '/help':
        await message.answer('Введите дату в формате дд.мм\nТипа так 03.08')


@dp.message_handler(regexp='^\d\d.\d\d$')
async def send_homework(message: types.Message):
    with open('dz.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=',')
        for line in reader:
            if line['дата'] == message.text:
                await message.answer(line['дата'] + ": " + line['задание'])

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)

def main():
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )