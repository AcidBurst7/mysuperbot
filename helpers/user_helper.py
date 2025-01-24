from sqlalchemy import create_engine
from sqlalchemy.sql import select
from sqlalchemy.orm import Session

from models import User

def get_user(engine, username, chat_id):
    session = Session(engine)
    user = select(User).where(User.username==username).where(User.chat_id==chat_id)
    result_user = session.scalars(user).first()
    if result_user is None:
        session.add(User(username=username, chat_id=chat_id))
        session.commit()
    session.close()
    