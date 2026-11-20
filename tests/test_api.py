import tasks
from main import app


class FakeTask:
    id = "fake-task-id"


class FakeResult:
    status = "SUCCESS"
    result = {"status": "sent"}

    def successful(self):
        return True


def test_docs_available(client):
    assert client.get("/docs").status_code == 200


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "database": "ok"}


def test_books_seeded(client):
    r = client.get("/books")
    assert r.status_code == 200
    assert [b["title"] for b in r.json()] == ["Dune", "Neuromancer"]


def test_create_and_get_book(client):
    payload = {"title": "Foundation", "author": "Isaac Asimov", "year": 1951, "price": 9.9}
    created = client.post("/books", json=payload)
    assert created.status_code == 201
    book_id = created.json()["id"]
    fetched = client.get(f"/books/{book_id}")
    assert fetched.status_code == 200
    assert fetched.json()["title"] == "Foundation"


def test_get_missing_book(client):
    assert client.get("/books/9999").status_code == 404


def test_create_book_validation(client):
    assert client.post("/books", json={"title": "x"}).status_code == 422


def test_graphql_books(client):
    r = client.post("/graphql", json={"query": "{ books { id title } }"})
    assert r.status_code == 200
    titles = [b["title"] for b in r.json()["data"]["books"]]
    assert titles == ["Dune", "Neuromancer"]


def test_graphql_book_by_id(client):
    r = client.post("/graphql", json={"query": "{ book(id: 1) { title author } }"})
    assert r.json()["data"]["book"] == {"title": "Dune", "author": "Frank Herbert"}


def test_graphql_book_missing(client):
    r = client.post("/graphql", json={"query": "{ book(id: 999) { title } }"})
    assert r.json()["data"]["book"] is None


def test_send_email_enqueues_task(client, monkeypatch):
    calls = []

    def fake_delay(to, subject):
        calls.append((to, subject))
        return FakeTask()

    monkeypatch.setattr("main.send_email.delay", fake_delay)
    r = client.post("/send-email", json={"to": "a@b.com", "subject": "Hi"})
    assert r.status_code == 200
    assert r.json() == {"task_id": "fake-task-id"}
    assert calls == [("a@b.com", "Hi")]


def test_task_status(client, monkeypatch):
    monkeypatch.setattr("main.AsyncResult", lambda task_id, app=None: FakeResult())
    r = client.get("/tasks/abc")
    assert r.status_code == 200
    assert r.json() == {"task_id": "abc", "status": "SUCCESS", "result": {"status": "sent"}}


def test_send_email_task_result(monkeypatch):
    monkeypatch.setattr(tasks.time, "sleep", lambda s: None)
    assert tasks.send_email("a@b.com", "Hi") == {
        "to": "a@b.com",
        "subject": "Hi",
        "status": "sent",
    }
