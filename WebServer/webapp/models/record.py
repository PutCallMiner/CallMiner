from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field

from webapp.models.transcript import TranscriptEntry

PyObjectId = Annotated[str, BeforeValidator(str)]


class Recording(BaseModel):
    id: PyObjectId | None = Field(alias="_id", default=None)
    recording_url: str
    transcript: list[TranscriptEntry] | None
    summary: str | None


class LoadRecordingsResponse(BaseModel):
    num_inserted: int


class RecordingsResponse(BaseModel):
    recordings: list[Recording]
