from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Body, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase
import httpx

from webapp.configs.globals import AZURE_SAS_TOKEN, logger
from webapp.crud.common import get_db
from webapp.crud.recordings import get_recording_by_id, update_with_transcript
from webapp.errors import BlobDownloadError, RecordingNotFoundError
from webapp.models.analysis import ASRParams
from webapp.models.record import Recording
from webapp.tasks.analysis import run_asr_task


router = APIRouter(prefix="/api/analysis", tags=["API"])


async def background_analyze(
    recording: Recording,
    asr_params: ASRParams,
    stage_timeout: float,
):
    """Runs the whole recording analysis step by step"""
    # get database connection
    db_gen = get_db()
    db = await anext(db_gen)  # noqa

    logger.info(
        f"[id: {recording.id}] Downloading audio file '{recording.recording_url}'."
    )
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{recording.recording_url}?{AZURE_SAS_TOKEN}")
    if resp.status_code != status.HTTP_200_OK:
        raise BlobDownloadError(recording.recording_url)
    audio_bytes = resp.content

    # Step 1. Run ASR
    logger.info(f"[id: {recording.id}] Running ASR celery task.")
    transcript = await run_asr_task(audio_bytes, asr_params, timeout=stage_timeout)
    logger.info(f"[id: {recording.id}] Writing audio transcript to database.")
    await update_with_transcript(db, recording.id, transcript)

    # TODO: Subsequent steps


@router.post("/")
async def run_recording_analysis(
    recording_id: Annotated[str, Body(...)],
    asr_params: Annotated[ASRParams, Body(...)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    background_tasks: BackgroundTasks,
    stage_timeout: Annotated[
        float, Body(...)
    ] = 600,  # NOTE: fastapi doesn't allow the default in Body() for some reason
):
    recording = await get_recording_by_id(db, recording_id)
    if recording is None:
        raise RecordingNotFoundError(recording_id)

    background_tasks.add_task(
        background_analyze,
        recording=recording,
        asr_params=asr_params,
        stage_timeout=stage_timeout,
    )
