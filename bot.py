import logging
import asyncio

# datebase
from db import DataBase

# telegram
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.executor import start_webhook
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from setting import (BOT_TOKEN, HEROKU_APP_NAME,
                        WEBHOOK_URL, WEBHOOK_PATH,
                        WEBAPP_HOST, WEBAPP_PORT, DATABASE_URL)
# telegram end

# datetime
from datetime import datetime
from datetime import timedelta
# datetime end

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

db = DataBase(DATABASE_URL)

@dp.message_handler(commands=['test'])
async def test(message: types.Message):
    print(message.from_user.id)


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

# сделать
@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    if(not db.get_subscription_status(message.from_user.id)):
        db.add_subscriber(message.from_user.id)
    else:
        db.update_subscription(message.from_user.id, True)
    await message.answer("Вы успешно подписались на рассылку дз")

@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    if(not db.get_subscription_status(message.from_user.id)):
        db.add_subscriber(message.from_user.id, False)
        await message.answer('Вы итак не подписаны')
    else:
        db.update_subscription(message.from_user.id, False)
        await message.answer('Вы успешно отписались от рассылки дз')

# напоминание что нужно сделать дз
async def notification(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        
        users = db.get_status(True)
        db.time(628447199, '21:28')

        for i in users:
            if (datetime.now().strftime("%H:%M") == i[0]):
                tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%d.%m")
                await bot.send_message(i[2], f'ДЗ на завтра\n{find_homework(tomorrow_date)}')

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
class Add_Homework(StatesGroup):
    date = State()
    task = State()

@dp.message_handler(commands=['add'])
async def add_homework(message: types.Message):
    if message.from_user.id == 628447199:
        await Add_Homework.date.set()
        await message.answer('Дата:')
    else:
        await message.answer('У вас нет прав для использования этой комманды')

@dp.message_handler(state='*', commands=['cancel'])
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel(message: types.Message, state: FSMContext):
    current_state = state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.answer('Отмена...')

@dp.message_handler(state=Add_Homework.date)
async def add_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['date'] = message.text

    await Add_Homework.next()
    await message.answer('Задание:')

@dp.message_handler(state=Add_Homework.task)
async def add_task(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['task'] = message.text

        db.add_homework(data['date'], data['task'])

        await message.answer('Домашнее задание успешно добавлено в базу данных!')
    
    await state.finish()

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(dp)

async def on_shutdown(dp):
    logging.info(dp)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(notification(60))
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )


# сделать поиск дз в отдельную функцию и в отдельном файле