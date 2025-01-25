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
    url_paths = url.split("/")
    image_name = url_paths[len(url_paths)-1]
    image_extension = image_name.split(".")[1]
    
    if picture_name == "":
        picture_name = datetime.date.today().strftime('%Y-%m-%d')

    full_image_name = f"{picture_name}.{image_extension}"
    image_path = f"./src/img/{full_image_name}"
    
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(image_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            
            result = {"status": "success", "image_name": full_image_name}
        else:
            result = {"status": "error", "message": ""}
    except Exception as e:
        result = {"status": "error", "message": e}

    return result

"""
Достаем картинку из базы
"""
def get_picture_from_base(engine, date):
    message = ""
    status = False
    picture_content = ""
    input_file = ""

    session = Session(engine)
    today_picture = select(Picture).where(Picture.picture_date==date.strftime("%Y-%m-%d"))
    result_today_picture = session.scalars(today_picture).first()

    if result_today_picture is None:
        data = download_picture(NASA_TOKEN, date)
        save_image = save_picture(data['url'], date.strftime("%Y-%m-%d"))

        if data is not None and save_image["status"] == "success":
            session.add(Picture(title=data['title'], description=data['explanation'], link=data['url'], picture_date=date))
            session.commit()

            input_file = FSInputFile(f"./src/img/{save_image["image_name"]}")
            picture_content = f"{data['title']}\n"

            status = True
        else:
            message = f"На сегодня хранилище с картинками недоступно. Попробуте через час или позже."
    else:
        picture_name = date.strftime('%Y-%m-%d')

        if os.path.isfile(f"./src/img/{picture_name}") is False:
            if save_picture(result_today_picture.link) is False:
                message = f"На сегодня хранилище с картинками недоступно. Попробуте через час или позже."
        
        input_file = FSInputFile(f"src/img/{picture_name}.jpg")
        
        picture_content = f"{result_today_picture.title}\n"
        status = True

    session.close()

    return {
        "status": status,
        "message": message,
        "picture": {
            "picture_content": picture_content,
            "input_file": input_file
        }
    }
