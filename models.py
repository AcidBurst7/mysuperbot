from sqlalchemy.orm import Session
import datetime
from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, Date, DateTime
from sqlalchemy import String, BigInteger
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

class Base(DeclarativeBase):
    pass

class Picture(Base):
    __tablename__ = "picture"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(30))
    description: Mapped[Optional[str]]
    link: Mapped[Optional[str]]
    picture_date: Mapped[str] = mapped_column(Date, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, default=datetime.date.today, nullable=False)
    
    def __repr__(self) -> str:
        return f"Picture(id={self.id!r}, title={self.title!r}, fullname={self.description!r})"
    

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    chat_id: Mapped[int] = mapped_column(BigInteger())
    created_at: Mapped[str] = mapped_column(Date, default=datetime.date.today, nullable=False)
    

engine = create_engine("sqlite:///bot.db", echo=True)
Base.metadata.create_all(engine)