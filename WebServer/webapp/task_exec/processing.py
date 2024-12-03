import asyncio
from typing import Iterable, Literal

from motor.motor_asyncio import AsyncIOMotorDatabase

from webapp.configs.globals import logger
from webapp.crud import recordings as crud
from webapp.models.analysis import AnalyzeParams
from webapp.task_exec.common import (
    TASK_TYPE_TO_DB_ENTRY,
    Scheduler,
    TaskType,
    get_task_by_type,
)

RerunMode = Literal["none", "selected", "all"]


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
        downstream_tasks = Scheduler.get_downstream_tasks(task_t)
        logger.info(
            f"[id: {self.recording_id}] Deleting downstream task results {downstream_tasks}"
        )
        await crud.delete_analysis_elements(
            self.db,
            self.recording_id,
            (TASK_TYPE_TO_DB_ENTRY[task] for task in downstream_tasks),
        )

    async def run_with_dependencies(
        self,
        required_tasks: Iterable[TaskType],
        analyze_params: AnalyzeParams,
        force_rerun: RerunMode,
        task_timeout: float | None = None,
    ) -> None:
        logger.info(f"[id: {self.recording_id}] Required Tasks: {required_tasks}")
        required = set(required_tasks)
        schedule = Scheduler.get_execution_schedule(required)
        logger.info(f"[id: {self.recording_id}] Schedule constructed: {schedule}")
        for step in schedule:
            coroutines = []
            for task_t in step:
                result_in_db = await get_task_by_type(task_t)().is_result_in_db(
                    self.db, self.recording_id
                )
                if result_in_db:
                    logger.info(
                        f"[id: {self.recording_id}] Result of '{task_t}' already in DB."
                    )

                    if force_rerun == "none":
                        continue

                    if force_rerun == "selected" and task_t not in required:
                        continue

                coroutines.append(
                    self.execute_task(task_t, analyze_params, task_timeout)
                )
            await asyncio.gather(*coroutines)
