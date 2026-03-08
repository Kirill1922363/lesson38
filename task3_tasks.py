import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import DeclarativeBase, Session


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


DATABASE_URL = "sqlite:///./tasks.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "tasks"

    id=Column(Integer, primary_key=True, index=True)
    title=Column(String,  nullable=False)
    description=Column(String,  nullable=True)
    done=Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)


def _seed():
    db = Session(engine)
    if db.query(Task).count() == 0:
        db.add_all([
            Task(title="Купити продукти",    description="Молоко, хліб, яйця"),
            Task(title="Зробити домашнє",    description="Математика та фізика"),
            Task(title="Зателефонувати лікарю", description=None, done=True),
        ])
        db.commit()
    db.close()

_seed()


class TaskCreate(BaseModel):
    title:str
    description:str | None = None
    done:bool = False


class TaskResponse(BaseModel):

    id:int
    title:str
    description:str | None
    done:bool

    model_config = {"from_attributes": True}

app = FastAPI(title="Tasks API — Завдання 3")


TASK_ID_MAX = 1000



@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):

    if task_id > TASK_ID_MAX:
        logger.error(
            "422 | task_id=%d перевищує допустиму межу %d",
            task_id, TASK_ID_MAX,
        )
        raise HTTPException(
            status_code=422,
            detail=(
                f"task_id={task_id} виходить за межі допустимих значень. "
                f"Максимальне допустиме значення: {TASK_ID_MAX}."
            ),
        )

    db = Session(engine)
    task = db.get(Task, task_id)
    db.close()

    if task is None:
        logger.warning("404 | Задачу з task_id=%d не знайдено в БД", task_id)
        raise HTTPException(
            status_code=404,
            detail=f"Задачу з id={task_id} не знайдено",
        )

    logger.info("200 | Отримано задачу id=%d title='%s'", task.id, task.title)
    return task


@app.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(payload: TaskCreate):
    db = Session(engine)
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    logger.info("Створено задачу id=%d title='%s'", task.id, task.title)
    return task



@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks():
    db = Session(engine)
    tasks = db.query(Task).all()
    db.close()
    return tasks

if __name__ == "__main__":
    from fastapi.testclient import TestClient

    client = TestClient(app)

    print("\n══ Тест 1: існуюча задача (очікується 200) ══")
    r = client.get("/tasks/1")
    print(f"  status={r.status_code}  body={r.json()}")
    assert r.status_code == 200

    print("\n══ Тест 2: задача не існує (очікується 404) ══")
    r = client.get("/tasks/999")
    print(f"  status={r.status_code}  body={r.json()}")
    assert r.status_code == 404
    assert "не знайдено" in r.json()["detail"]

    print("\n══ Тест 3: id > 1000 (очікується 422) ══")
    r = client.get("/tasks/1001")
    print(f"  status={r.status_code}  body={r.json()}")
    assert r.status_code == 422
    assert "межі" in r.json()["detail"]

    print("\n✅ Всі тести пройшли успішно!")


