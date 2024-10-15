from webapp.models.ner import NER, NEREntry
from webapp.tasks.ner import parse_ner_output


def test_parse_ner_output():
    ner_output = (
        "<|Speaker 1|> My name is <persName>John</persName> I live in <placeName>"
        "Poznań</placeName> what is your name?\n"
        "<|Speaker 2|> Hi I am <persName>Eve</persName>\n"
    )

    res = parse_ner_output(ner_output)
    assert res == NER(
        entries=[
            [
                NEREntry(entity="persName", start_char=11, end_char=15),
                NEREntry(entity="placeName", start_char=26, end_char=32),
            ],
            [NEREntry(entity="persName", start_char=8, end_char=11)],
        ]
    )
