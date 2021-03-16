import logging
import asyncio

# datebase
from db import SQLite

# telegram
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.executor import start_webhook
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from setting import BOT_TOKEN
# telegram end

# datetime
from datetime import datetime
from datetime import timedelta
# datetime end

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

db = SQLite('db.db')

@dp.message_handler(commands=['test'])
async def test(message: types.Message):
    db.add_message(message.from_user.id, message.from_user.username, message.from_user.full_name, message.text)

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

@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    if(not db.get_users_status_notifications(message.from_user.id)):
        db.add_subscriber(message.from_user.id)
    else:
        db.update_subscription(message.from_user.id, True)
    await message.answer("Вы успешно подписались на рассылку дз")

@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    if(not db.get_users_status_notifications(message.from_user.id)):
        db.add_subscriber(message.from_user.id, False)
        await message.answer('Вы итак не подписаны')
    else:
        db.update_subscription(message.from_user.id, False)
        await message.answer('Вы успешно отписались от рассылки дз')

# напоминание что нужно сделать дз
async def notification(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        
        users = db.get_status_notifications()

        for i in users:
            if (datetime.now().strftime("%H:%M") == i[2]):
                tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%d.%m")
                await bot.send_message(i[0], f'ДЗ на завтра\n{find_homework(tomorrow_date)}')

# поиск дз по дате
@dp.message_handler(regexp='^\d\d[.]\d\d$')
async def send_homework(message: types.Message):
    await message.answer(find_homework(message.text))

# поиск дз в базе данных
def find_homework(date):
    homework = db.get_homework(date)
    for i in homework:
        return (f'{i[0]}: {i[1]}')

# добавление дз в базу данных
"""class Add_Homework(StatesGroup):
    answer = State()

@dp.message_handler(commands=['add'])
async def cmd_dialog(message: types.Message):
    await Add_Homework.answer.set()
    await message.answer('Дата:')

@dp.message_handler(state=Add_Homework.answer)
async def process_message(message: types.Message, state: FSMContext):
    print(state)"""

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(notification(60))
    executor.start_polling(dp, skip_updates=True)


# сделать поиск дз в отдельную функцию и в отдельном файле