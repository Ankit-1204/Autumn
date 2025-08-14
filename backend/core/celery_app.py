from celery import Celery;
from core.config import settings
celery_app = Celery(
    "workflow_service",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.autodiscover_tasks(["app.tasks"], force=True)