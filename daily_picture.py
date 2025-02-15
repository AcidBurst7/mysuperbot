#!/usr/bin/python

import os
import requests
import datetime
from sqlalchemy import create_engine
from sqlalchemy.sql import select
from sqlalchemy.orm import Session
from dotenv import load_dotenv, dotenv_values 
from helpers import picture_helper
import daily_picture

from models import Picture, User

engine = create_engine("sqlite:///bot.db", echo=True)

load_dotenv() 
 
TOKEN = os.getenv("BOT_TOKEN")
NASA_TOKEN = os.getenv("NASA_API_KEY")

def send_photo():
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    session = Session(engine)

    picture = picture_helper.get_picture_from_base(engine, datetime.date.today())
    
    user = select(User)
    result_user = session.scalars(user).all()
    for user in result_user:
        params = {
            'chat_id': user.chat_id,
            'caption': picture["media"]["title"],
        }
        
        with open(os.path.abspath(picture["media"]["path"]), 'rb') as photo:
            response = requests.post(url=url, data=params, files={'photo': photo})

        if response.status_code == 200:
            print("Photo sent successfully!")
        else:
            print(f"Failed to send photo: {response.status_code}, {response.text}")
    session.close()

if __name__ == '__main__':
    send_photo()
