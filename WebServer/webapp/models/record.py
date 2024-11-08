from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, Field

from webapp.models.conformity import ConformityResults
from webapp.models.ner import NER
from webapp.models.transcript import Transcript

PyObjectId = Annotated[str, BeforeValidator(str)]


class RecordingBase(BaseModel):
    recording_url: str
    transcript: Transcript | None
    summary: str | None
    speaker_mapping: dict[str, Literal["agent", "client"]] | None
    duration: int | None
    ner: NER | None
    conformity_results: ConformityResults | None

    def get_agent_speaker_id(self) -> int:
        assert self.speaker_mapping is not None, "Speaker mapping is None"
        for key, value in self.speaker_mapping.items():
            if value == "agent":
                return int(key.strip()[-1])
        return 0


class Recording(RecordingBase):
    id: PyObjectId = Field(alias="_id")


class LoadRecordingsResponse(BaseModel):
    num_inserted: int


class RecordingsResponse(BaseModel):
    recordings: list[Recording]
