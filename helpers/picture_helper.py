import requests
import datetime

"""
Загрузка картинки с сервера NASA
"""
def download_picture(token, date=datetime.datetime.now()):
    try:
        request = requests.get("https://api.nasa.gov/planetary/apod", {'api_key': token, 'date': date})
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
