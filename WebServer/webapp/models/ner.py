from pydantic import BaseModel


class NEREntry(BaseModel):
    entity: str
    start_char: int
    end_char: int
    lemmas: list[str]


class NER(BaseModel):
    entries: list[list[NEREntry]]
