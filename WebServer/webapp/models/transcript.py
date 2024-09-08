from pydantic import BaseModel


class TranscriptEntry(BaseModel):
    speaker: int
    start_time: int
    end_time: int
    text: str


class Transcript(BaseModel):
    entries: list[TranscriptEntry]
