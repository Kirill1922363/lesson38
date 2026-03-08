from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite:///./animals.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

class Base(DeclarativeBase):
    pass

class Animal(Base):
    __tablename__ = "animals"

    id=Column(Integer, primary_key=True, index=True)
    name=Column(String,  nullable=False)
    age=Column(Integer, nullable=False)
    adopted=Column(Boolean, default=False)
    health_status=Column(String,  nullable=False, server_default="healthy")