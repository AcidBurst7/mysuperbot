import asyncio
import logging
import sys
import os
import datetime
from sqlalchemy import create_engine
from sqlalchemy.sql import select
from sqlalchemy.orm import Session
from dotenv import load_dotenv 

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.command import Command
from aiogram.utils.markdown import hbold
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, DialogCalendar, DialogCalendarCallback, \
    get_user_locale


from models import Picture, User
import helpers.picture_helper as picture_helper
import daily_picture as daily_picture
import helpers.user_helper as user_helper

engine = create_engine("sqlite:///bot.db", echo=True)

load_dotenv() 
 
TOKEN = os.getenv("BOT_TOKEN")
NASA_TOKEN = os.getenv("NASA_API_KEY")

dp = Dispatcher()
schedule = AsyncIOScheduler(timezone="Europe/Moscow")

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}!\n Скорее запускай команду /today_picture чтобы загрузить картинку дня или с помощью команды /calendar получить картинку за интересующую дату.")

@dp.message(Command("today_picture"))
async def today_picture(message: Message):
    date_today = datetime.date.today()

    user_helper.get_user(engine, message.from_user, message.chat.id)
    await picture_helper.send_answer(engine, message, date_today)

@dp.message(Command("calendar"))
async def calendar_picture(message: Message):
    await message.answer(
        "Здесь вы можете выбрать дату в промежутке от 1 января 1995 года и до сегодняшней даты. Выберите нужное из календарика ниже.",
        reply_markup=await SimpleCalendar().start_calendar()
    )

@dp.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackData):
    calendar = SimpleCalendar(show_alerts=True)
    
    date_today = datetime.datetime.now()
    year = int(date_today.strftime("%Y"))
    month = int(date_today.strftime("%m"))
    day = int(date_today.strftime("%d"))

    calendar.set_dates_range(datetime.datetime(1995, 1, 1), datetime.datetime(year, month, day))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(f'Подгружаем картинку на дату {date.strftime("%d.%m.%Y")}...')
        user_helper.get_user(engine, callback_query.from_user, callback_query.message.chat.id)
        await picture_helper.send_answer(engine, callback_query.message, date)

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    schedule.add_job(daily_picture.send_photo, 'cron', day_of_week='0-6', hour='8', minute='0', id='send_photo_job')
    schedule.start()
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
