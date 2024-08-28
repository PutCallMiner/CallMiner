from typing import TypeAlias
import pydantic


class TranscriptEntry(pydantic.BaseModel):
    speaker: str
    start_time: int
    end_time: int
    text: str


Transcript: TypeAlias = list[TranscriptEntry]
