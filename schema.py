from typing import Optional

import strawberry
from sqlalchemy import select

import models
from database import SessionLocal


@strawberry.type
class Book:
    id: int
    title: str
    author: str
    year: int
    price: float

    @classmethod
    def from_model(cls, row: models.Book) -> "Book":
        return cls(
            id=row.id,
            title=row.title,
            author=row.author,
            year=row.year,
            price=row.price,
        )


@strawberry.type
class Query:
    @strawberry.field
    def books(self) -> list[Book]:
        with SessionLocal() as db:
            rows = db.scalars(select(models.Book).order_by(models.Book.id)).all()
            return [Book.from_model(r) for r in rows]

    @strawberry.field
    def book(self, id: int) -> Optional[Book]:
        with SessionLocal() as db:
            row = db.get(models.Book, id)
            return Book.from_model(row) if row else None


schema = strawberry.Schema(query=Query)
