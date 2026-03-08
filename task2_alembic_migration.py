import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import Animal, engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Animals API — Завдання 2")


class AnimalCreate(BaseModel):
    name:str
    age:int
    adopted:bool = False
    health_status:str  = "healthy"


class AnimalResponse(BaseModel):
    id:int
    name:str
    age:int
    adopted:bool
    health_status:str

    model_config = {"from_attributes": True}


@app.post("/animals", response_model=AnimalResponse, status_code=201)
def create_animal(payload: AnimalCreate):
    if payload.age < 0:
        logger.warning("Спроба створити тварину з від'ємним віком: %d", payload.age)
        raise HTTPException(status_code=400, detail="Вік не може бути від'ємним")

    db = Session(engine)
    animal = Animal(**payload.model_dump())
    db.add(animal)
    db.commit()
    db.refresh(animal)
    logger.info("Створено тварину id=%d, health_status='%s'", animal.id, animal.health_status)
    return animal


@app.get("/animals/{animal_id}", response_model=AnimalResponse)
def get_animal(animal_id: int):
    db = Session(engine)
    animal = db.get(Animal, animal_id)
    if animal is None:
        logger.warning("Тварину з id=%d не знайдено", animal_id)
        raise HTTPException(status_code=404, detail=f"Тварину id={animal_id} не знайдено")
    logger.info("Отримано тварину id=%d", animal_id)
    return animal