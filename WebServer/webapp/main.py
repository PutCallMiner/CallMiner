from fastapi import FastAPI, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles

from webapp.crud.common import init_db
from webapp.errors import (
    BlobDownloadError,
    RecordingAlreadyExistsError,
    RecordingNotFoundError,
)
from webapp.routers.api.analysis import router as analysis_api_router
from webapp.routers.api.dashboard import router as dashboard_api_router
from webapp.routers.api.recordings import router as recordings_api_router
from webapp.routers.dashboard import router as dashboard_router
from webapp.routers.recordings import router as recordings_router


async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.exception_handler(RecordingAlreadyExistsError)
def recording_exists_handler(request: Request, exc: RecordingAlreadyExistsError):
    raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc))


@app.exception_handler(RecordingNotFoundError)
def recording_not_found_handler(request: Request, exc: RecordingNotFoundError):
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))


@app.exception_handler(BlobDownloadError)
def audio_download_handler(request: Request, exc: BlobDownloadError):
    raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc))


# TODO: handle TaskTimeoutError when method of analysis status tracking is decided
# @app.exception_handler(TaskTimeoutError)
# def task_timout_handler(request: Request, exc: TaskTimeoutError):
#     raise HTTPException(status.HTTP_408_REQUEST_TIMEOUT, detail=str(exc))


# statics
app.mount("/public", StaticFiles(directory="public"), name="public")

# routes
app.include_router(dashboard_router)
app.include_router(recordings_router)

# api routes
app.include_router(dashboard_api_router)
app.include_router(recordings_api_router)
app.include_router(analysis_api_router)
