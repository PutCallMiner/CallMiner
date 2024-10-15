from pydantic import BaseModel


class TranscriptEntry(BaseModel):
    speaker: int
    start_time: int
    end_time: int
    text: str


class Transcript(BaseModel):
    entries: list[TranscriptEntry]

    def get_text_with_speakers(self, special=False) -> str:
        l = ""
        r = ":"
        if special:
            l, r = "<|", "|>"

        return "\n".join(
            [f"{l}Speaker {entry.speaker}{r} {entry.text}" for entry in self.entries]
        )

    def get_n_entries_text_with_speakers(self, n: int) -> str:
        n_entries = self.entries[:n]
        return "\n".join(
            [f"Speaker {entry.speaker}: {entry.text}" for entry in n_entries]
        )
