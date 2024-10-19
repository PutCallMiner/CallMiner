import re

import requests
from celery.exceptions import TimeoutError  # type: ignore[import-untyped]

from webapp.celery_app import celery_app
from webapp.configs.globals import MLFLOW_NER_URL
from webapp.errors import NERError, TaskTimeoutError
from webapp.models.ner import NER, NEREntry
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


def parse_ner_output(text: str) -> NER:
    """Takes output from NER model in the following form: <|Speaker x|> Text <entity>text</entity>\n...
    Converts it into list of lists of NER Entries to match the transcript, each entry in the outer
    list matches entry in transcript and each entry in the inner lists is an entity with addresses of
    characters relative to the current transcript entry
    """
    ner = NER(entries=[])
    components = re.finditer(r"<\|Speaker (?P<speaker>\d+)\|> (?P<text>.+)", text)
    for component in components:
        ner_entries = []
        tags_chars = 0
        matches = re.finditer(
            r"<(?P<entity>[a-zA-Z]+)>.*?</(?P=entity)>", component.group("text")
        )
        for match in matches:
            entity = match.group("entity")
            start_char = match.span()[0] - tags_chars
            tags_chars = tags_chars + 5 + 2 * len(entity)
            end_char = match.span()[1] - tags_chars
            ner_entries.append(
                NEREntry(
                    entity=entity,
                    start_char=start_char,
                    end_char=end_char,
                )
            )
        ner.entries.append(ner_entries)
    return ner


async def run_ner_task(transcript: Transcript, timeout: float) -> NER:
    text = transcript.get_text_with_speakers(special=True)
    ner_result = ner_task.apply_async(args=[text])
    res = ner_result.get(timeout=timeout)["predictions"][0]
    return parse_ner_output(res)
