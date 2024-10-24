from abc import ABC, abstractmethod

from motor.motor_asyncio import AsyncIOMotorDatabase

from webapp.models.analysis import AnalyzeParams

TIMEOUT = 300  # TODO: pass this as parameter


class RecordingTask(ABC):
    @abstractmethod
    async def is_result_in_db(
        self, db: AsyncIOMotorDatabase, recording_id: str
    ) -> bool:
        pass

    @abstractmethod
    async def run(
        self, db: AsyncIOMotorDatabase, recording_id: str, params: AnalyzeParams
    ) -> None:
        pass
