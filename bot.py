import logging
import csv
from aiogram import Bot, Dispatcher, executor, types

TOKEN = '1291846106:AAEoo_HoGHFEGzBMvwf16quTyMvk-OirAzU'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
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

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)