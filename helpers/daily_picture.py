import os
import requests
import datetime
from sqlalchemy import create_engine
from sqlalchemy.sql import select
from sqlalchemy.orm import Session
from dotenv import load_dotenv, dotenv_values 
from helpers import picture_helper

from models import Picture, User

engine = create_engine("sqlite:///bot.db", echo=True)

load_dotenv() 
 
TOKEN = os.getenv("BOT_TOKEN")
NASA_TOKEN = os.getenv("NASA_API_KEY")

def send_photo():
    picture_name = datetime.date.today().strftime('%Y-%m-%d')

    session = Session(engine)

    today_picture = select(Picture).where(Picture.created_at==datetime.date.today())
    result_today_picture = session.scalars(today_picture).first()

    if result_today_picture is None:
        data = picture_helper.download_picture(NASA_TOKEN)

        if data is not None:
            if picture_helper.save_picture(data['url']):
                session.add(Picture(title=data['title'], description=data['explanation'], link=data['url']))
                session.commit()

                input_file = f"src/img/{data['date']}.jpg"
                picture_content = f"{data['title']}\n"
            else:
                pass
        else:
            pass
    else:
        if os.path.isfile(f"src/img/{picture_name}.jpg") is False:
            save_today_picture_request = requests.get(result_today_picture.link)
            today_picture_file = open(f"src/img/{picture_name}.jpg", "wb")
            today_picture_file.write(save_today_picture_request.content)
            today_picture_file.close()
        
        input_file = f"src/img/{picture_name}.jpg"
        
        picture_content = f"{result_today_picture.title}\n"
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    user = select(User)
    result_user = session.scalars(user).all()
    for user in result_user:
        params = {
            'chat_id': user.chat_id,
            'caption': picture_content,
        }
        
        with open(os.path.abspath(input_file), 'rb') as photo:
            response = requests.post(url=url, data=params, files={'photo': photo})

        if response.status_code == 200:
            print("Photo sent successfully!")
        else:
            print(f"Failed to send photo: {response.status_code}, {response.text}")
    session.close()

# if __name__ == '__main__':
#     send_photo()
