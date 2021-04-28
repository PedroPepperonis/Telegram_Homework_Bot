# -*- coding: utf8 -*-

import logging
import asyncio
import re
from datetime import datetime
from datetime import timedelta

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageTextIsEmpty
from aiogram.utils.executor import start_webhook

from config.config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT, DATABASE_URL, TIMER
from database.db import DataBase

logging.basicConfig(level=logging.INFO)
bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

db = DataBase(DATABASE_URL)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Бот запущен. Для более подробной информации /help')


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.answer('Короче, я отправляю дз.\n'
                         '/today - дз на сегодня\n'
                         '/tomorrow - дз на завтра\n'
                         '/week - дз на неделю вперед\n'
                         '/subscribe - подписаться на уведомления о дз\n'
                         '/unsubscribe - отписаться от уведомлений\n'
                         '/time - выбрать время когда будут приходить уведомления\n'
                         '/n - узнать время когда мне приходят уведомления\n'
                         'Также можно ввести дату вручную типа так 20.03')


# дз на сегодня
@dp.message_handler(commands=['today'])
async def today(message: types.Message):
    today_date = datetime.now().strftime("%d.%m")
    try:
        await message.answer(find_homework(today_date))
    except MessageTextIsEmpty:
        await message.answer('К сожалению дз пока нет')


# дз на завтра
@dp.message_handler(commands=['tomorrow'])
async def tomorrow(message: types.Message):
    tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%d.%m")
    try:
        await message.answer(find_homework(tomorrow_date))
    except MessageTextIsEmpty:
        await message.answer('К сожалению дз пока нет')


# дз на неделю
@dp.message_handler(commands=['week'])
async def week(message: types.Message):
    for i in range(1, 8):
        date = (datetime.now() + timedelta(days=i)).strftime("%d.%m")
        try:
            await message.answer(find_homework(date))
        except MessageTextIsEmpty as error:
            print(f'{error}: на этот день домашнего задания нет')


# поиск дз по дате
@dp.message_handler(regexp='^\d\d[.]\d\d$')
async def send_homework(message: types.Message):
    try:
        await message.answer(find_homework(message.text))
    except MessageTextIsEmpty:
        await message.answer('К сожалению дз пока нет')


# подписка и отписка от уведомлений
@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    if message.chat.type == 'group':
        if not db.get_subscription_status(message.chat.id):
            db.add_subscriber(message.chat.id)
        else:
            db.update_subscription(message.chat.id, True)
            db.time(message.chat.id, '15:00')
        await message.answer('Уведомления включены')

    if message.chat.type == 'private':
        if not db.get_subscription_status(message.from_user.id):
            db.add_subscriber(message.from_user.id)
        else:
            db.update_subscription(message.from_user.id, True)
        await message.answer("Вы успешно подписались на рассылку дз")


@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    if message.chat.type == 'group':
        db.update_subscription(message.chat.id, False)
        await message.answer('Уведомления отключены')

    if message.chat.type == 'private':
        if not db.get_subscription_status(message.from_user.id):
            db.add_subscriber(message.from_user.id, False)
            await message.answer('Вы итак не подписаны')
        else:
            db.update_subscription(message.from_user.id, False)
            await message.answer('Вы успешно отписались от рассылки дз')


# узнать время когда приходят уведомления
@dp.message_handler(commands=['n'])
async def notification_time(message: types.Message):
    time = db.get_notification_time(message.from_user.id)
    for i in time:
        if i['status']:
            await message.answer('Вы получаете уведомления ежедневно в ' + i['time'])
        else:
            await message.answer('В данный момент вы не получаете уведомления о дз\nЧтобы подписаться /subscribe')


# напоминание что нужно сделать дз
async def notification(wait_for):
    while True:
        await asyncio.sleep(wait_for)

        users = db.get_status(True)

        for i in users:
            if datetime.now().strftime("%H:%M") == i['time']:
                tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%d.%m")
                await bot.send_message(i['user_id'], f'ДЗ на завтра\n{find_homework(tomorrow_date)}')


# поиск дз в базе данных
def find_homework(date):
    homework = db.get_homework(date)
    for i in homework:
        return f"{i['date']}\n{i['task']}"


class AddHomework(StatesGroup):
    date = State()
    task = State()


@dp.message_handler(commands=['add'])
async def add_homework(message: types.Message):
    if message.from_user.id == 628447199:
        await AddHomework.date.set()
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


@dp.message_handler(state=AddHomework.date)
async def add_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['date'] = message.text

    await AddHomework.next()
    await message.answer('Задание:')


@dp.message_handler(state=AddHomework.task)
async def add_task(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['task'] = message.text

        db.add_homework(data['date'], data['task'])

        await message.answer('Домашнее задание успешно добавлено в базу данных!')

    await state.finish()


# обновление дз
class UpdateHomework(StatesGroup):
    date = State()
    task = State()


@dp.message_handler(commands=['update'])
async def get_date(message: types.Message):
    if message.from_user.id == 628447199:
        await UpdateHomework.date.set()
        await message.answer('Дата:')
    else:
        await message.answer('У вас нет доступа к этой команде')


@dp.message_handler(state=UpdateHomework.date)
async def set_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['date'] = message.text

    await UpdateHomework.next()
    await message.answer('Задание:')


@dp.message_handler(state=UpdateHomework.task)
async def update_task(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['task'] = message.text

        db.update_homework(data['date'], data['task'])

        await message.answer('Домашнее задание успешно обновлено!')

    await state.finish()


# выбор времени когда будут приходить уведомления
class SetTime(StatesGroup):
    time = State()


@dp.message_handler(commands=['time'])
async def get_time(message: types.Message):
    await SetTime.time.set()
    await message.answer(
        'В какое время вы хотите получать напоминания о дз?\n'
        'Время в формате чч:мм\n'
        f'Типа так {datetime.now().strftime("%H:%M")}'
    )


@dp.message_handler(state=SetTime.time)
async def edit_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['time'] = re.search(r'^\d\d[:]\d\d$', message.text)
        if data['time']:
            db.time(message.from_user.id, data['time'].group(0))
            await message.answer('Теперь вы будете получать уведомления ежедневно в ' + data['time'].group(0))
        else:
            await message.answer('Вы неправильно ввели время\nПопробуйте еще раз /time')

    await state.finish()


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(dp)


async def on_shutdown(dp):
    logging.info(dp)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(notification(int(TIMER)))
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
