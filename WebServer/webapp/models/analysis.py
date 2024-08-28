from pydantic import BaseModel, Field


class ASRParams(BaseModel):
    num_speakers: int | None = Field(None)
    beam_size: int | None = Field(None)
