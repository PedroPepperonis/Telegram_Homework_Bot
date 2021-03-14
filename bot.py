#telegram
import logging
import csv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.executor import start_webhook
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

# datetime
from datetime import datetime
from datetime import timedelta
# datetime end

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


""" сделать кнопки када нибудь
# button
today_button = InlineKeyboardButton('На сегодня', callback_data='/today')
tomorrow_button = InlineKeyboardButton('На завтра', callback_data='/tomorrow')
week_button = InlineKeyboardButton('На неделю', callback_data='/week')
# button end

markup1 = InlineKeyboardMarkup(resize_keyboard=True).add(today_button).add(tomorrow_button).add(week_button)
"""

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Бот запущен. Доступные комманды:\n/help')

@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.answer('Введите дату в формате дд.мм\nТипа так 03.08')

# дз на сегодня
@dp.message_handler(commands=['today'])
async def today(message: types.Message):
    today_date = datetime.now().strftime("%d.%m")
    await message.answer(find_homework(today_date))

# дз на завтра
@dp.message_handler(commands=['tomorrow'])
async def tomorrow(message: types.Message):
    tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%d.%m")
    await message.answer(find_homework(tomorrow_date))

# дз на неделю
@dp.message_handler(commands=['week'])
async def week(message: types.Message):
    i = 1
    while i <= 7:
        week = (datetime.now() + timedelta(days=i)).strftime("%d.%m")
        await message.answer(find_homework(week))
        i += 1


# поиск дз по дате
@dp.message_handler(regexp='^\d\d[.]\d\d$')
async def send_homework(message: types.Message):
    await message.answer(find_homework(message.text))

# поиск дз в файле
def find_homework(date):
    with open('dz.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=',')
        for line in reader:
            if line['дата'] == date:
                return (line['дата'] + ": " + line['задание'])


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


# сделать поиск дз в отдельную функцию и в отдельном файле