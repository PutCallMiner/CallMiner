import base64
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Body, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase
import httpx
from pydantic import TypeAdapter

from webapp.configs.globals import AZURE_SAS_TOKEN
from webapp.crud.common import get_db
from webapp.crud.recordings import get_recording_by_id, update_with_transcript
from webapp.errors import BlobDownloadError, RecordingNotFoundError
from webapp.models.analysis import ASRParams
from webapp.models.record import Recording
from webapp.models.transcript import Transcript
from webapp.tasks.analysis import asr_task


router = APIRouter(prefix="/api/analysis", tags=["API"])


async def background_analyze(
    recording: Recording,
    asr_params: ASRParams,
    stage_timeout: float,
):
    # get database connection
    db_gen = get_db()
    db = await anext(db_gen)

    # download audio
    # service_client = BlobServiceClient.from_connection_string(
    #     AZURE_STORAGE_CONNECTION_STRING
    # )
    # blob_downloader = AzureBlobDownloader(service_client)
    # audio_bytes = blob_downloader.download_blob_from_url(recording.recording_url)

    # download audio
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{recording.recording_url}?{AZURE_SAS_TOKEN}")
    if resp.status_code != status.HTTP_200_OK:
        raise BlobDownloadError(recording.recording_url)
    audio_bytes = resp.content

    asr_result = asr_task.apply_async(
        args=[base64.b64encode(audio_bytes).decode(), asr_params.model_dump()]
    )
    transcript_raw = asr_result.get(timeout=stage_timeout)
    transcript: Transcript = TypeAdapter(Transcript).validate_python(transcript_raw)
    print(f"{transcript = }", flush=True)
    await update_with_transcript(db, recording.id, transcript)


@router.post("/")
async def run_recording_analysis(
    recording_id: Annotated[str, Body(...)],
    asr_params: Annotated[ASRParams, Body(...)],
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    stage_timeout: Annotated[float, Body(...)] = 600,
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
    # print(f"{type(audio_bytes) = }", flush=True)

    # start celery task
    # result = asr_worker.apply_async(args=[audio_bytes, asr_params])
    # try:
    #     transcript: Transcript = result.get(timeout=stage_timeout)
    #     update_result = await update_with_transcript(db, recording_id, transcript)
    #     return JSONResponse(
    #         content={"modified_count": update_result.modified_count}, status_code=200
    #     )
    # except TimeoutError:
    #     return JSONResponse(
    #         content={
    #             "task_id": result.id,
    #             "status": "Task still running, timeout exceeded",
    #         },
    #         status_code=500,
    #     )
