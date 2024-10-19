from pydantic import BaseModel


class NEREntry(BaseModel):
    entity: str
    start_char: int
    end_char: int


class NER(BaseModel):
    entries: list[list[NEREntry]]
