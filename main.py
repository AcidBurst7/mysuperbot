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
import helpers.daily_picture as daily_picture

engine = create_engine("sqlite:///bot.db", echo=True)

load_dotenv() 
 
TOKEN = os.getenv("BOT_TOKEN")
NASA_TOKEN = os.getenv("NASA_API_KEY")

dp = Dispatcher()
# schedule = AsyncIOScheduler()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}!\n Скорее запускай команду /today_picture чтобы загрузить картинку дня.")

@dp.message(Command("today_picture"))
async def today_picture(message: Message):
    session = Session(engine)

    user = select(User).where(User.username==message.from_user.username).where(User.chat_id==message.chat.id)
    result_user = session.scalars(user).first()
    if result_user is None:
        session.add(User(username=message.from_user.username, chat_id=message.chat.id))
        session.commit()

    today_picture = select(Picture).where(Picture.created_at==datetime.date.today())
    result_today_picture = session.scalars(today_picture).first()

    if result_today_picture is None:
        data = picture_helper.download_picture(NASA_TOKEN)

        if data is not None:
            if picture_helper.save_picture(data['url']):
                session.add(Picture(title=data['title'], description=data['explanation'], link=data['url']))
                session.commit()

                input_file = FSInputFile(f"src/img/{data['date']}.jpg")
                picture_content = f"{data['title']}\n"
            else:
                await message.answer(f"На сегодня хранилище с картинками недоступно. Попробуте через час или позже.")
        else:
            await message.answer(f"На сегодня хранилище с картинками недоступно. Попробуте через час или позже.")
    else:
        picture_name = datetime.date.today().strftime('%Y-%m-%d')

        if os.path.isfile(f"src/img/{picture_name}.jpg") is False:
            if picture_helper.save_picture(result_today_picture.link) is False:
                await message.answer(f"На сегодня хранилище с картинками недоступно. Попробуте через час или позже.")
        
        input_file = FSInputFile(f"src/img/{picture_name}.jpg")
        
        picture_content = f"{result_today_picture.title}\n"

    session.close()

    await message.answer_photo(input_file, picture_content)


@dp.message(Command("calendar"))
async def today_picture(message: Message):
    await message.answer(
        "Здесь вы можете выбрать дату в промежутке от 1 января 2024 года и до сегодняшней даты. Выберите нужное из календарика ниже.",
        reply_markup=await SimpleCalendar().start_calendar()
    )


@dp.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackData):
    calendar = SimpleCalendar(show_alerts=True)
    date_year = int(datetime.datetime.now().strftime("%Y"))
    date_month = int(datetime.datetime.now().strftime("%m"))
    date_day = int(datetime.datetime.now().strftime("%d"))
    calendar.set_dates_range(datetime.datetime(2024, 1, 1), datetime.datetime(date_year, date_month, date_day))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(f'Подгружаем картинку на дату {date.strftime("%d.%m.%Y")}...')
        print(callback_query)
        session = Session(engine)

        user = select(User).where(User.username==callback_query.from_user.username).where(User.chat_id==callback_query.message.chat.id)
        result_user = session.scalars(user).first()
        if result_user is None:
            session.add(User(username=callback_query.message.from_user.username, chat_id=callback_query.message.chat.id))
            session.commit()

        today_picture = select(Picture).where(Picture.created_at==date.strftime("%Y-%m-%d"))
        result_today_picture = session.scalars(today_picture).first()

        if result_today_picture is None:
            data = picture_helper.download_picture(NASA_TOKEN, date.strftime("%Y-%m-%d"))

            if data is not None:
                if picture_helper.save_picture(data['url'], date.strftime("%Y-%m-%d")):
                    session.add(Picture(title=data['title'], description=data['explanation'], link=data['url']))
                    session.commit()

                    input_file = FSInputFile(f"src/img/{data['date']}.jpg")
                    picture_content = f"{data['title']}\n"
                else:
                    await callback_query.message.answer(f"На сегодня хранилище с картинками недоступно. Попробуте через час или позже.")
            else:
                await callback_query.message.answer(f"На сегодня хранилище с картинками недоступно. Попробуте через час или позже.")
        else:
            picture_name = date.strftime("%Y-%m-%d")

            if os.path.isfile(f"src/img/{picture_name}.jpg") is False:
                if picture_helper.save_picture(result_today_picture.link) is False:
                    await callback_query.message.answer(f"На сегодня хранилище с картинками недоступно. Попробуте через час или позже.")
            
            input_file = FSInputFile(f"src/img/{picture_name}.jpg")
            
            picture_content = f"{result_today_picture.title}\n"

        session.close()

        await callback_query.message.answer_photo(input_file, picture_content)


async def main() -> None:
    # schedule.add_job(daily_picture.send_photo, 'cron', hour=8, minute=0, id='my_job_id')
    # schedule.remove_job('my_job_id')
    # schedule.start()

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
