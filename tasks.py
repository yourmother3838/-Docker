import time

from celery import Celery

from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery_app = Celery(
    "app",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)


@celery_app.task(name="send_email")
def send_email(to: str, subject: str) -> dict:
    time.sleep(10)
    return {"to": to, "subject": subject, "status": "sent"}
