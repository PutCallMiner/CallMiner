import asyncio

from motor.motor_asyncio import AsyncIOMotorDatabase

from webapp.configs.globals import logger
from webapp.models.analysis import AnalyzeParams
from webapp.task_exec.common import TaskType, get_task_by_type
from webapp.task_exec.scheduling import Scheduler


class RecordingProcessor:
    def __init__(self, db: AsyncIOMotorDatabase, recording_id: str):
        self.db = db
        self.recording_id = recording_id

    async def _is_component_in_db(self, task_t: TaskType) -> bool:
        task = get_task_by_type(task_t)()
        return await task.is_result_in_db(self.db, self.recording_id)

    async def execute_task(
        self,
        task_t: TaskType,
        analyze_params: AnalyzeParams,
        task_timeout: float | None = None,
    ) -> None:
        task = get_task_by_type(task_t)()
        logger.info(f"[id: {self.recording_id}] Running '{task_t}' task.")
        await task.run(self.db, self.recording_id, analyze_params, task_timeout)

    async def run_with_dependencies(
        self,
        required_components: list[TaskType],
        analyze_params: AnalyzeParams,
        force_rerun: bool,
        task_timeout: float | None = None,
    ) -> None:
        schedule = Scheduler.get_execution_schedule(set(required_components))
        for step in schedule:
            coroutines = []
            for task_t in step:
                result_in_db = await get_task_by_type(task_t)().is_result_in_db(
                    self.db, self.recording_id
                )
                if force_rerun or not result_in_db:
                    coroutines.append(
                        self.execute_task(task_t, analyze_params, task_timeout)
                    )
            await asyncio.gather(*coroutines)
