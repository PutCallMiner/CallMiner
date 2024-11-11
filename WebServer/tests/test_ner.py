from webapp.models.ner import NER, NEREntry
from webapp.task_exec.tasks import NERTask


def test_parse_ner_output():
    text = "agent: Ja Tomek\nclient: Ja z Poznania"
    ents = [
        {"start": 10, "end": 15, "label": "persName"},
        {"start": 29, "end": 37, "label": "placeName"},
    ]

    res = NERTask.parse_ner_output(text, ents)
    assert res == NER(
        entries=[
            [NEREntry(entity="persName", start_char=3, end_char=8)],
            [NEREntry(entity="placeName", start_char=5, end_char=13)],
        ]
    )
