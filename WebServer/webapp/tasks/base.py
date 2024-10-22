from abc import ABC, abstractmethod

from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from webapp.models.analysis import ASRParams

TIMEOUT = 300  # TODO: pass this as parameter


class AnalyzeParams(BaseModel):
    asr: ASRParams


class DatabaseTask(ABC):
    @abstractmethod
    async def run(
        self, db: AsyncIOMotorDatabase, recording_id: str, params: AnalyzeParams
    ) -> None:
        pass
