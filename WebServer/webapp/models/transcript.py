from pydantic import BaseModel


class TranscriptEntry(BaseModel):
    speaker: int
    start_time: int
    end_time: int
    text: str


class Transcript(BaseModel):
    entries: list[TranscriptEntry]

    def get_text_with_speakers(self) -> str:
        speakers_text = []
        for entry in self.entries:
            speakers_text.append(f"Speaker {entry.speaker}: {entry.text}")
        return "\n".join(speakers_text)
