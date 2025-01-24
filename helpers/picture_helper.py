import requests
import os
import datetime
from sqlalchemy import create_engine
from sqlalchemy.sql import select
from sqlalchemy.orm import Session
from dotenv import load_dotenv 

from sqlalchemy.sql import select
from sqlalchemy.orm import Session

from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery

from models import Picture

load_dotenv()
NASA_TOKEN = os.getenv("NASA_API_KEY")

"""
Загрузка картинки с сервера NASA
"""
def download_picture(token, date):
    try:
        request = requests.get("https://api.nasa.gov/planetary/apod", {'api_key': token, 'date': date.strftime("%Y-%m-%d")})
        result = request.json()
    except Exception:
        result = None
        
    return result

"""
Сохранение картинки на диске
"""
def save_picture(url, picture_name=""):
    if picture_name == "":
        picture_name = datetime.date.today().strftime('%Y-%m-%d')
    
    try:
        save_today_picture_request = requests.get(url)
        today_picture_file = open(f"src/img/{picture_name}.jpg", "wb")
        today_picture_file.write(save_today_picture_request.content)
        today_picture_file.close()
        result = True
    except Exception:
        result = False
    return result

"""
Достаем картинку из базы
"""
def get_picture_from_base(engine, date):
    message = ""
    picture_content = ""
    input_file = ""

    session = Session(engine)
    today_picture = select(Picture).where(Picture.picture_date==date.strftime("%Y-%m-%d"))
    result_today_picture = session.scalars(today_picture).first()

    if result_today_picture is None:
        data = download_picture(NASA_TOKEN, date)

        if data is not None:
            if save_picture(data['url']):
                session.add(Picture(title=data['title'], description=data['explanation'], link=data['url'], picture_date=date))
                session.commit()

                input_file = FSInputFile(f"src/img/{data['date']}.jpg")
                picture_content = f"{data['title']}\n"
            else:
                message = f"На сегодня хранилище с картинками недоступно. Попробуте через час или позже."
        else:
            message = f"На сегодня хранилище с картинками недоступно. Попробуте через час или позже."
    else:
        picture_name = date.strftime('%Y-%m-%d')

        if os.path.isfile(f"src/img/{picture_name}.jpg") is False:
            if save_picture(result_today_picture.link) is False:
                message = f"На сегодня хранилище с картинками недоступно. Попробуте через час или позже."
        
        input_file = FSInputFile(f"src/img/{picture_name}.jpg")
        
        picture_content = f"{result_today_picture.title}\n"

    session.close()

    return {
        "message": message,
        "picture": {
            "picture_content": picture_content,
            "input_file": input_file
        }
    }
