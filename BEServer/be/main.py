from fastapi import FastAPI

from be.routers.persons import router as persons_router


app = FastAPI()

app.include_router(persons_router)


@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}
