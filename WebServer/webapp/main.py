from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from webapp.routers.api.add import router as add_api_router
from webapp.routers.api.dashboard import router as dashboard_api_router
from webapp.routers.api.recordings import router as recordings_api_router
from webapp.routers.dashboard import router as dashboard_router
from webapp.routers.recordings import router as recordings_router

app = FastAPI()

# statics
app.mount("/public", StaticFiles(directory="public"), name="public")

# routes
app.include_router(dashboard_router)
app.include_router(recordings_router)

# api routes
app.include_router(dashboard_api_router)
app.include_router(recordings_api_router)
app.include_router(add_api_router)
