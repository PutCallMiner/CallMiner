from celery import Celery

from webapp.configs.globals import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery_app = Celery(
    "webapp",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["webapp.tasks.analysis"],
)

# Optional configuration for Celery
celery_app.conf.update(
    result_expires=3600,
)
