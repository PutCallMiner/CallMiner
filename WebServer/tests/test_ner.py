from webapp.task_exec.tasks import NERTask


def test_parse_ner_output():
    text = "agent: Ja Tomek\nclient: Ja z Poznania"
    ents = [
        {"start": 10, "end": 15, "label": "persName"},
        {"start": 29, "end": 37, "label": "placeName"},
    ]

    res = NERTask.fix_locations(text, ents)
    assert res == [
        [{"start": 1, "end": 3, "label": "persName"}],
        [{"start": 5, "end": 13, "label": "placeName"}],
    ]
