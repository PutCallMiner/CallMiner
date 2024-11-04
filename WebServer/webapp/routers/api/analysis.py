from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Body

from webapp.crud.common import get_rec_db_context
from webapp.crud.redis_manage import update_task_status
from webapp.models.analysis import RunAnalysisResponse
from webapp.models.task_status import TaskStatus
from webapp.task_exec.common import TaskType
from webapp.task_exec.processing import RecordingProcessor, RerunMode
from webapp.task_exec.tasks.base import AnalyzeParams

router = APIRouter(prefix="/api/analysis", tags=["API"])


async def background_analyze(
    recording_id: str,
    required_tasks: list[TaskType],
    analyze_params: AnalyzeParams,
    force_rerun: RerunMode,
    task_timeout: float | None = None,
):
    """Runs the required analysis components (and their dependencies if needed)"""
    try:
        async with get_rec_db_context() as db:
            processor = RecordingProcessor(db, recording_id)
            await processor.run_with_dependencies(
                required_tasks, analyze_params, force_rerun, task_timeout
            )
    except Exception:
        await update_task_status(recording_id, TaskStatus.FAILED)
        raise

    # TODO: Run conformity check
    # Step 4. Update task status
    await update_task_status(recording_id, TaskStatus.FINISHED)


@router.post("/")
async def run_recording_analysis(
    recording_id: Annotated[str, Body(...)],
    analyze_params: Annotated[AnalyzeParams, Body(...)],
    required_tasks: list[TaskType],
    background_tasks: BackgroundTasks,
    force_rerun: Annotated[RerunMode, Body(...)] = "none",
    task_timeout: Annotated[
        float | None, Body(...)
    ] = 600,  # NOTE: fastapi doesn't allow the default in Body() for some reason
) -> RunAnalysisResponse:
    await update_task_status(recording_id, TaskStatus.IN_PROGRESS)

    background_tasks.add_task(
        background_analyze,
        recording_id,
        required_tasks,
        analyze_params,
        force_rerun,
        task_timeout,
    )

    return RunAnalysisResponse()
