from celery import Celery  # type: ignore[import-untyped]

from webapp.configs.globals import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery_app = Celery(
    "webapp",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=[
        "webapp.task_exec.tasks.asr",
        "webapp.task_exec.tasks.summarize",
        "webapp.task_exec.tasks.classify_speakers",
        "webapp.task_exec.tasks.ner",
    ],
)

# Optional configuration for Celery
celery_app.conf.update(
    result_expires=3600,
)
