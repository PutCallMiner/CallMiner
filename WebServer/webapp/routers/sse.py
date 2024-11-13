from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from webapp.configs.globals import logger
from webapp.crud.common import get_rec_db, get_tasks_db
from webapp.crud.recordings import get_recording_by_id
from webapp.errors import RecordingNotFoundError

router = APIRouter(prefix="/sse", tags=["SSE"])


@router.get("/{recording_id}")
async def websocket_endpoint(
    recording_id: str,
    recording_db: Annotated[AsyncIOMotorDatabase, Depends(get_rec_db)],
    tasks_db: Annotated[Redis, Depends(get_tasks_db)],
):
    recording = await get_recording_by_id(recording_db, recording_id)
    if recording is None:
        raise RecordingNotFoundError(recording_id)

    async def event_generator():
        if recording.summary:
            yield f"data: <div id='summary'>{recording.summary}</div>\n\n"
        else:
            yield "data: <div id='summary'>Summary not found, please run the analysis first.</div>\n\n"

        pubsub = tasks_db.pubsub()
        channel_name = recording_id + "_summary"
        await pubsub.subscribe(channel_name)

        try:
            async for message in pubsub.listen():
                logger.info(f"Received message: {message}")
                if message["type"] == "message":
                    task = message["channel"].decode("utf-8").split("_")[1]
                    if task == "summary":
                        data = message["data"].decode("utf-8")
                        yield f"data: <div id='summary'>{data}</div>\n\n"
        except Exception:
            logger.warning("SSE closed unexpectedly")
        finally:
            logger.info("Closing SSE connection")
            await pubsub.unsubscribe(channel_name)
            await pubsub.close()

    return StreamingResponse(event_generator(), media_type="text/event-stream")
