import requests
from celery.exceptions import TimeoutError  # type: ignore[import-untyped]

from webapp.celery_app import celery_app
from webapp.configs.globals import MLFLOW_SUMMARIZER_URL
from webapp.errors import SummarizerError, TaskTimeoutError
from webapp.models.transcript import Transcript


@celery_app.task
def summarize_task(text: str) -> str:
    resp = requests.post(
        f"{MLFLOW_SUMMARIZER_URL}/invocations",
        json={"instances": [{"conversation": [text]}]},
    )
    if not resp.ok:
        raise SummarizerError(resp.content.decode())
    return resp.json()


async def run_summarize_task(transcript: Transcript, timeout: float) -> str:
    text = transcript.get_text_with_speakers()
    summarizer_result = summarize_task.apply_async(args=[text])
    try:
        summary = summarizer_result.get(timeout=timeout)["predictions"][0]
    except TimeoutError as _:
        raise TaskTimeoutError(summarize_task.name, summarizer_result.id)
    return summary
