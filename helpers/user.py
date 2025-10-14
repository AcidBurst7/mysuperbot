from sqlalchemy.sql import select
from sqlalchemy.orm import Session

from models import User


"""
Распознавание пользователя
"""
def get_user(engine, user_info, chat_id):
    session = Session(engine)
    user = select(User).where(User.chat_id==chat_id)
    result_user = session.scalars(user).first()
    if result_user is None:
        username = user_info.username if user_info.username is not None else ""
        first_name = user_info.first_name if user_info.first_name is not None else ""
        last_name = user_info.last_name if user_info.last_name is not None else ""
        full_name = user_info.full_name if user_info.full_name is not None else ""
        is_premium = user_info.is_premium if user_info.is_premium is not None else False

        session.add(User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            full_name=full_name,
            is_premium=is_premium,
            chat_id=chat_id))
        session.commit()
    session.close()
    