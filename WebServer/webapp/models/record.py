import pydantic

from webapp.models.transcript import TranscriptEntry


class Recording(pydantic.BaseModel):
    id: str | None = pydantic.Field(serialization_alias="_id", default=None)
    recording_url: str
    agent: str | None
    transcript: list[TranscriptEntry] | None
    summary: str | None
    analyzed: bool
