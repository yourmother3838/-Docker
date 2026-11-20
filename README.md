# Books API

FastAPI + PostgreSQL + Redis + Celery + GraphQL (Strawberry).

## Переменные окружения

См. `.env.example`. По умолчанию используются локальные адреса (`localhost`).

| Переменная | Назначение |
| --- | --- |
| `DATABASE_URL` | подключение к PostgreSQL |
| `CELERY_BROKER_URL` | брокер Celery (Redis) |
| `CELERY_RESULT_BACKEND` | хранилище результатов Celery (Redis) |

## Локальный запуск

```
pip install -r requirements-dev.txt
docker run -d --name pg -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=app postgres:16
docker run -d --name redis -p 6379:6379 redis:7
celery -A tasks.celery_app worker --loglevel=info --pool=solo
uvicorn main:app --reload
```

Таблицы создаются и заполняются начальными данными при старте приложения.

## Тесты

```
pytest
```

Тесты используют SQLite в памяти, а Celery и Redis подменяются, поэтому PostgreSQL и Redis для них не нужны.

## Эндпоинты

- `GET /docs` — Swagger UI
- `GET /health` — проверка приложения и подключения к БД
- `GET /books`, `GET /books/{id}`, `POST /books` — REST по книгам (PostgreSQL)
- `POST /graphql` — GraphQL (`{ books { id title author year price } }`)
- `POST /send-email`, `GET /tasks/{task_id}` — фоновая задача через Celery

## Примеры

```
curl localhost:8000/health
curl localhost:8000/books
curl -X POST localhost:8000/books -H "Content-Type: application/json" -d '{"title":"Foundation","author":"Isaac Asimov","year":1951,"price":9.9}'
curl -X POST localhost:8000/send-email -H "Content-Type: application/json" -d '{"to":"a@b.com","subject":"Hi"}'
curl localhost:8000/tasks/<task_id>
```

## Публичный адрес

Будет добавлен после деплоя.
