import requests
from celery.exceptions import TimeoutError  # type: ignore[import-untyped]

from webapp.celery_app import celery_app
from webapp.configs.globals import MLFLOW_NER_URL
from webapp.errors import NERError, TaskTimeoutError
from webapp.models.transcript import Transcript


@celery_app.task
def ner_task(text: str) -> str:
    resp = requests.post(
        f"{MLFLOW_NER_URL}/invocations",
        json={"instances": [text]},
    )
    if not resp.ok:
        raise NERError(resp.content.decode())
    return resp.json()


async def run_ner_task(transcript: Transcript, timeout: float) -> str:
    text = transcript.get_text_with_speakers()
    ner_result = ner_task.apply_async(args=[text])
    try:
        ner = ner_result.get(timeout=timeout)["predictions"][0]
    except TimeoutError as _:
        raise TaskTimeoutError(ner_task.name, ner_result.id)
    return ner
