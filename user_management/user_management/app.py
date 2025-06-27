from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from user_management.user_management.database.db import initialize_db
from user_management.user_management.routes.google_login import (
    router as GoogleLoginRouter,
)
from user_management.user_management.routes.login import router as LoginRouter
from user_management.user_management.routes.register import router as RegisterRouter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")  # type: ignore
async def start_database() -> None:
    initialize_db()


@app.get("/", tags=["Root"])  # type: ignore
async def read_root() -> dict:
    return {"message": "welcome"}


app.include_router(LoginRouter, tags=["Login"], prefix="/login")
app.include_router(
    RegisterRouter,
    tags=["Register"],
    prefix="/register",
)
app.include_router(GoogleLoginRouter, tags=["GoogleLogin"], prefix="/google_login")
