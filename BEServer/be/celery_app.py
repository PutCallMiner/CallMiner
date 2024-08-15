from celery import Celery

from be.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND


celery_app = Celery(
    "be",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["be.tasks"]
)

# Optional configuration for Celery
celery_app.conf.update(
    result_expires=3600,
)

if __name__ == "__main__":
    celery_app.start()