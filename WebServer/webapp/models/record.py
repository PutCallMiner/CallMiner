from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field

from webapp.models.transcript import Transcript

PyObjectId = Annotated[str, BeforeValidator(str)]


class RecordingBase(BaseModel):
    recording_url: str
    transcript: Transcript | None
    summary: str | None
    ner: str | None


class Recording(RecordingBase):
    id: PyObjectId = Field(alias="_id")


class LoadRecordingsResponse(BaseModel):
    num_inserted: int


class RecordingsResponse(BaseModel):
    recordings: list[Recording]
