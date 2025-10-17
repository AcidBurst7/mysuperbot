import requests
import os
import datetime
from dotenv import load_dotenv 
from sqlalchemy.sql import select
from sqlalchemy.orm import Session

from aiogram.types import FSInputFile

from database.models import Picture
from logger import logger

load_dotenv()
NASA_TOKEN = os.getenv("NASA_API_KEY")

"""
Загрузка картинки с сервера NASA
"""
def download_media(token, date):
    result = None
    try:
        picture_date = date.strftime("%Y-%m-%d")
        request = requests.get(
            "https://api.nasa.gov/planetary/apod", 
            {
                'api_key': token, 
                'date': picture_date
            }
        )
        if request.status_code == 200:
            result = request.json()
            logger.error(result.json())
        else:
            logger.error(f"Запрос картинки на дату - {picture_date}, код ответа: {request.status_code}")
    except Exception as e:
        logger.critical(f"Бот упал с ошибкой: {e}", exc_info=True)
    return result

"""
Сохранение картинки на диск
"""
def save_media(data, picture_name=""):
    if data["media_type"] == "image":
        if type(data) is list and data["media_type"] == "image":
            url = data["url"]
        elif type(data) is dict:
            url = data.url
        else:
            url = data.link
    
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
                
                result = {"status": True, "image_name": full_image_name}
            else:
                result = {"status": False, "message": "Не удалось загрузить картинку"}
        except Exception as e:
            result = {"status": False, "message": e}
    else:
        result = {"status": False, "message": "Media type is not image"}

    if result.status is False:
        logger.critical(f"Неудачное сохранение картинки на диск. Сообщение: {result.message}", exc_info=True)
    else:
        logger.error(f"Удачное сохранение картинки на диск. Сообщение: {result.message}")
    
    return result

"""
Достаем картинку из базы
"""
def get_picture_from_base(engine, date):
    message = "" 
    media_content = "" 
    media_file = ""
    media_path = ""
    status = False

    session = Session(engine)
    today_media = select(Picture).where(Picture.published_date==date.strftime("%Y-%m-%d"))
    result_today_media = session.scalars(today_media).first()
    if result_today_media is None:
        data = download_media(NASA_TOKEN, date)

        if 'code' not in data:
            if data is not None:
                save_image = save_media(data, date.strftime("%Y-%m-%d"))

                if save_image["status"]:
                    session.add(Picture(title=data['title'], description=data['explanation'], link=data['url'], type=data["media_type"], published_date=date))
                    session.commit()
                
                if data["media_type"] == "video":
                    media_content = f"Сегодня тот самый редкий случай когда вместо картинки - видео!\n{data['title']}\n{data["url"]}"
                elif data["media_type"] == "image":
                    media_content = f"{data['title']}\n"
                    media_path = f"./src/img/{save_image["image_name"]}"
                    media_file = FSInputFile(media_path)

                status = True
            else:
                message = f"На сегодня хранилище с картинками недоступно. Попробуте через час или позже 🌌."
        else:
            if data['code'] == 400:
                message = f"На сегодня картинка пока не доступна. Она пока еще в пути до Земли 🪐🛰️"
            else:
                message = f"На сегодня хранилище с картинками недоступно. Попробуте через час или позже 🌌 ."
    else:
        if result_today_media.type == "image":
            url_paths = result_today_media.link.split("/")
            image_extension = url_paths[len(url_paths)-1].split(".")[1]
            picture_name = date.strftime('%Y-%m-%d')

            full_image_name = f"{picture_name}.{image_extension}"
            media_path = f"./src/img/{full_image_name}"

            if os.path.isfile(media_path) is False:
                if save_media(result_today_media.link) is False:
                    message = f"На сегодня хранилище с картинками недоступно. Попробуте через час или позже."
            media_file = FSInputFile(media_path)
            media_content = f"{result_today_media.title}\n"
        elif result_today_media.type == "video":
            media_content = f"""
                Сегодня тот самый редкий случай когда вместо картинки - видео! 
                🎬 \n{result_today_media.title}\n{result_today_media.link}
            """
            status = True

    session.close()

    return {
        "status": status,
        "message": message,
        "media": {
            "title": media_content,
            "path": media_path,
            "file": media_file
        }
    }


async def send_answer(engine, message, date):
    response = get_picture_from_base(engine, date)

    if response["status"]:
        content = response["media"]["title"]  
    else:
        content = response["message"]

    if response["media"]["file"] == "":
        await message.answer(content)
    else:
        await message.answer_photo(response["media"]["file"], response["media"]["title"])