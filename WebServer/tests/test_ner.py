from webapp.models.ner import NER, NEREntry
from webapp.task_exec.tasks import NERTask


def test_parse_ner_output():
    ner_output = (
        "<|agent|> My name is <persName>John</persName> I live in <placeName>"
        "Poznań</placeName> what is your name?\n"
        "<|client|> Hi I am <persName>Eve</persName>\n"
    )

    res = NERTask.parse_ner_output(ner_output)
    assert res == NER(
        entries=[
            [
                NEREntry(entity="persName", start_char=11, end_char=15),
                NEREntry(entity="placeName", start_char=26, end_char=32),
            ],
            [NEREntry(entity="persName", start_char=8, end_char=11)],
        ]
    )
