import asyncio
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from webapp.configs.globals import AZURE_SAS_TOKEN, logger
from webapp.crud.common import get_rec_db, get_tasks_db
from webapp.crud.recordings import (
    get_recording_by_id,
    update_with_ner,
    update_with_speaker_mapping,
    update_with_summary,
    update_with_transcript,
)
from webapp.crud.redis_manage import set_key_value
from webapp.errors import RecordingNotFoundError
from webapp.models.analysis import ASRParams, RunAnalysisResponse
from webapp.models.record import Recording
from webapp.models.task_status import TaskStatus
from webapp.tasks.asr import run_asr_task
from webapp.tasks.classify_speakers import run_classify_speaker_task
from webapp.tasks.ner import run_ner_task
from webapp.tasks.summarize import run_summarize_task
from webapp.utils.azure import download_azure_blob

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

    # get database connection
    db_gen = get_rec_db()
    db = await anext(db_gen)  # noqa: F821

    logger.info(
        f"[id: {recording.id}] Downloading audio file '{recording.recording_url}'."
    )
    audio_bytes = await download_azure_blob(recording.recording_url, AZURE_SAS_TOKEN)

    # Step 1. Run ASR
    logger.info(f"[id: {recording.id}] Running ASR celery task.")
    transcript = await run_asr_task(audio_bytes, asr_params, timeout=stage_timeout)
    logger.info(f"[id: {recording.id}] Writing audio transcript to database.")
    await update_with_transcript(db, recording.id, transcript)

    # Step 2. Run tasks for recording analysis
    logger.info(
        f"[id: {recording.id}] Running Speaker Classifier and Summarizer celery tasks concurrently."
    )

    speaker_classifier_task = run_classify_speaker_task(
        transcript, timeout=stage_timeout
    )
    summarizer_task = run_summarize_task(transcript, timeout=stage_timeout)
    ner_task = run_ner_task(transcript, timeout=stage_timeout)
    # TODO: Run conformity check
    speaker_classifier_mapping, summary, ner = await asyncio.gather(
        speaker_classifier_task, summarizer_task, ner_task
    )

    # Step 3. Write results into db
    logger.info(f"[id: {recording.id}] Writing speaker classifier mapping to database.")
    await update_with_speaker_mapping(db, recording.id, speaker_classifier_mapping)

    logger.info(f"[id: {recording.id}] Writing summary to database.")
    await update_with_summary(db, recording.id, summary)

    logger.info(f"[id: {recording.id}] Writing ner to database.")
    await update_with_ner(db, recording.id, ner)

    # TODO: Run conformity check
    # Step 4. Update task status
    logger.info(f"[id: {recording.id}] Updating task status to: {TaskStatus.FINISHED}")
    await set_key_value(tasks_db, recording.id, TaskStatus.FINISHED)


@router.post("/")
async def run_recording_analysis(
    recording_id: Annotated[str, Body(...)],
    asr_params: Annotated[ASRParams, Body(...)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_rec_db)],
    background_tasks: BackgroundTasks,
    stage_timeout: Annotated[
        float, Body(...)
    ] = 600,  # NOTE: fastapi doesn't allow the default in Body() for some reason
) -> RunAnalysisResponse:
    recording = await get_recording_by_id(db, recording_id)
    if recording is None:
        raise RecordingNotFoundError(recording_id)

    background_tasks.add_task(
        background_analyze,
        recording=recording,
        asr_params=asr_params,
        stage_timeout=stage_timeout,
    )

    return RunAnalysisResponse()
