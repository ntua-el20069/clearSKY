from credits.database.db import initialize_db
from credits.routes.credits import router as CreditsRouter
from fastapi import FastAPI

app = FastAPI()


@app.on_event("startup")  # type: ignore
async def start_database() -> None:
    initialize_db()


@app.get("/", tags=["Root"])  # type: ignore
async def read_root() -> dict:
    return {"message": "welcome"}


app.include_router(CreditsRouter, tags=["Credits"], prefix="/credits")
