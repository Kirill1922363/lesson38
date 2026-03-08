import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import DeclarativeBase, Session

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./animals.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


class Base(DeclarativeBase):
    pass


class Animal(Base):
    __tablename__ = "animals"

    id= Column(Integer, primary_key=True, index=True)
    name= Column(String, nullable=False)
    age= Column(Integer, nullable=False)
    adopted = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)


class AnimalCreate(BaseModel):
    name:str
    age:int
    adopted: bool = False


class AnimalResponse(BaseModel):
    id:int
    name:str
    age:int
    adopted: bool

    model_config = {"from_attributes": True}   



app = FastAPI(title="Animals API — Завдання 1")


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


@app.post("/animals", response_model=AnimalResponse, status_code=201)
def create_animal(payload: AnimalCreate):
    if payload.age < 0:
        logger.warning("Спроба створити тварину з від'ємним віком: %d", payload.age)
        raise HTTPException(
            status_code=400,
            detail="Вік не може бути від'ємним",
        )

    db = Session(engine)
    animal = Animal(**payload.model_dump())
    db.add(animal)
    db.commit()
    db.refresh(animal)
    logger.info("Створено тварину id=%d name='%s'", animal.id, animal.name)
    return animal


@app.get("/animals/{animal_id}", response_model=AnimalResponse)
def get_animal(animal_id: int):
    db = Session(engine)
    animal = db.get(Animal, animal_id)

    if animal is None:
        logger.warning("Тварину з id=%d не знайдено", animal_id)
        raise HTTPException(
            status_code=404,
            detail=f"Тварину з id={animal_id} не знайдено",
        )

    logger.info("Отримано тварину id=%d name='%s'", animal.id, animal.name)
    return animal


