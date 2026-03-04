from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "aaron2",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "nightly-replenishment": {
            "task": "app.tasks.replenishment.auto_replenish",
            "schedule": crontab(hour=21, minute=0),
        },
    },
)

celery_app.autodiscover_tasks(["app.tasks"])
