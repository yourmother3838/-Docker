from contextlib import asynccontextmanager

from celery.result import AsyncResult
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from strawberry.fastapi import GraphQLRouter

import models
from database import Base, SessionLocal, engine, get_db
from schema import schema
from tasks import celery_app, send_email

SEED_BOOKS = [
    {"title": "Dune", "author": "Frank Herbert", "year": 1965, "price": 12.5},
    {"title": "Neuromancer", "author": "William Gibson", "year": 1984, "price": 10.0},
]


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.scalar(select(models.Book.id).limit(1)) is None:
            db.add_all(models.Book(**b) for b in SEED_BOOKS)
            db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(GraphQLRouter(schema), prefix="/graphql")


class EmailIn(BaseModel):
    to: str
    subject: str


class BookIn(BaseModel):
    title: str
    author: str
    year: int
    price: float


class BookOut(BookIn):
    model_config = ConfigDict(from_attributes=True)

    id: int


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}


@app.get("/books", response_model=list[BookOut])
def list_books(db: Session = Depends(get_db)):
    return db.scalars(select(models.Book).order_by(models.Book.id)).all()


@app.get("/books/{book_id}", response_model=BookOut)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(models.Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.post("/books", response_model=BookOut, status_code=201)
def create_book(data: BookIn, db: Session = Depends(get_db)):
    book = models.Book(**data.model_dump())
    db.add(book)
    db.commit()
    return book


@app.post("/send-email")
def send_email_endpoint(data: EmailIn):
    task = send_email.delay(data.to, data.subject)
    return {"task_id": task.id}


@app.get("/tasks/{task_id}")
def task_status(task_id: str):
    res = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": res.status,
        "result": res.result if res.successful() else None,
    }
