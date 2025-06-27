from fastapi import FastAPI

from .database.db import initialize_db
from .routes.review import router as ReviewRouter

app = FastAPI()


@app.on_event("startup")  # type: ignore
async def start_database() -> None:
    initialize_db()


@app.get("/", tags=["Root"])  # type: ignore
async def read_root() -> dict:
    return {"message": "welcome"}


app.include_router(ReviewRouter, tags=["Review"], prefix="/review")
