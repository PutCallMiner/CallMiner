import fastapi
import fastapi.staticfiles
import fastapi.templating

import routers.dashboard
import routers.transcript


app = fastapi.FastAPI()

app.mount("/public", fastapi.staticfiles.StaticFiles(directory="public"), name="public")
app.include_router(routers.dashboard.router)
app.include_router(routers.transcript.router)


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}
