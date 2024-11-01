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

    def get_conversation_text(self, sep="\n") -> str:
        """Converts the recording transcript to a single string in a form:
        agent: Hello how can I help you\n
        client: Hi, I would like to...

        all the conversation entries are separated by `sep`
        """
        assert self.transcript is not None
        assert self.speaker_mapping is not None
        return sep.join(
            f"{self.speaker_mapping[entry.speaker]}: {entry.text}"
            for entry in self.transcript.entries
        )


class Recording(RecordingBase):
    id: PyObjectId = Field(alias="_id")


class LoadRecordingsResponse(BaseModel):
    num_inserted: int


class RecordingsResponse(BaseModel):
    recordings: list[Recording]
