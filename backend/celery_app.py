from celery import Celery;
from core.config import settings
celery_app = Celery(
    "workflow_service",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_track_started=True,
    worker_prefetch_multiplier=1,  # safer for long-running tasks
)
celery_app.autodiscover_tasks(["app.tasks"], force=True)