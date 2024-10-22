from typing import Literal

from pydantic import BaseModel, Field


class ASRParams(BaseModel):
    language: str | None = Field(None, examples=["pl"])
    num_speakers: int | None = Field(None, examples=[2])
    whisper_prompt: str | None = Field(None, examples=[None])


class RunAnalysisResponse(BaseModel):
    analysis_started: Literal[True] = True
