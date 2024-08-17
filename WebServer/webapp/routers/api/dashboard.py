from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api", tags=["API"])


@router.get("/")
def root(request: Request) -> JSONResponse:
    return JSONResponse(content={"message": "Hello, World!"}, status_code=200)
