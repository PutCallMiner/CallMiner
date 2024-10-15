import requests

from webapp.celery_app import celery_app
from webapp.configs.globals import MLFLOW_SUMMARIZER_URL
from webapp.errors import SummarizerError
from webapp.models.transcript import Transcript
from webapp.tasks.utils import task_to_async


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
    result = await task_to_async(timeout)(summarize_task)(args=[text])
    summary = result["predictions"][0]
    return summary
