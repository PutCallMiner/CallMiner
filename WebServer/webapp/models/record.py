from pydantic import Field, BaseModel

from webapp.models.transcript import TranscriptEntry


class Recording(BaseModel):
    id: str | None = Field(serialization_alias="_id", default=None)
    recording_url: str
    transcript: list[TranscriptEntry] | None
    summary: str | None


class LoadRecordingsResponse(BaseModel):
    num_inserted: int


class RecordingsResponse(BaseModel):
    recordings: list[Recording]
