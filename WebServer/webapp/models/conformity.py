from typing import Self

from pydantic import BaseModel, Field, model_validator


class ConformityResult(BaseModel):
    intent_name: str = Field(..., description="Uniquely identifies the intent")
    passed: bool = Field(
        ..., description="Whether an transcript entry corresponding to intent was found"
    )
    entry_id: int | None = Field(
        None, ge=0, description="ID of entry from transcript which passes the intent"
    )

    @model_validator(mode="after")
    def check_entry_id_passed(self) -> Self:
        if self.passed and self.entry_id is None:
            raise ValueError("'entry_id' cannot be None if 'passed' is True")
        if not self.passed and self.entry_id is not None:
            raise ValueError("'entry_id' must be None if 'passed' is False")
        return self


class ConformityResults(BaseModel):
    results: list[ConformityResult]
