from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, Field

from webapp.models.ner import NER
from webapp.models.transcript import Transcript

PyObjectId = Annotated[str, BeforeValidator(str)]
SpeakerClass = Literal["agent", "client"]
SpeakerMapping = dict[int, SpeakerClass]


class RecordingBase(BaseModel):
    recording_url: str
    transcript: Transcript | None
    summary: str | None
    speaker_mapping: SpeakerMapping | None
    duration: int | None
    ner: NER | None


class Recording(RecordingBase):
    id: PyObjectId = Field(alias="_id")


class LoadRecordingsResponse(BaseModel):
    num_inserted: int


class RecordingsResponse(BaseModel):
    recordings: list[Recording]
