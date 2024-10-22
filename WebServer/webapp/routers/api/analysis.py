from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from webapp.configs.globals import logger
from webapp.crud.common import get_rec_db, get_tasks_db
from webapp.crud.recordings import (
    get_recording_by_id,
)
from webapp.crud.redis_manage import set_key_value
from webapp.errors import RecordingNotFoundError
from webapp.models.analysis import ASRParams, RunAnalysisResponse
from webapp.models.record import Recording
from webapp.models.task_status import TaskStatus
from webapp.tasks.base import AnalyzeParams
from webapp.tasks.common import Component, RecordingProcessor

router = APIRouter(prefix="/api/analysis", tags=["API"])


async def background_analyze(
    recording: Recording,
    asr_params: ASRParams,
    stage_timeout: float,
):
    """Runs the whole recording analysis step by step"""
    # set task status
    tasks_db_gen = get_tasks_db()
    tasks_db = await anext(tasks_db_gen)  # noqa: F821
    await set_key_value(tasks_db, recording.id, TaskStatus.IN_PROGRESS)

    # TODO: Run conformity check
    # Step 4. Update task status
    logger.info(f"[id: {recording.id}] Updating task status to: {TaskStatus.FINISHED}")
    await set_key_value(tasks_db, recording.id, TaskStatus.FINISHED)


@router.post("/")
async def run_recording_analysis(
    recording_id: Annotated[str, Body(...)],
    analyze_params: Annotated[AnalyzeParams, Body(...)],
    required_components: list[Component],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_rec_db)],
    background_tasks: BackgroundTasks,
    stage_timeout: Annotated[
        float, Body(...)
    ] = 600,  # NOTE: fastapi doesn't allow the default in Body() for some reason
) -> RunAnalysisResponse:
    recording = await get_recording_by_id(db, recording_id)
    if recording is None:
        raise RecordingNotFoundError(recording_id)

    processor = RecordingProcessor(db, recording)
    background_tasks.add_task(
        processor.run_with_dependencies, required_components, analyze_params
    )

    return RunAnalysisResponse()
