from statistics.statistics.database.db import initialize_db
from statistics.statistics.routes.course_stats import router as CourseStats
from statistics.statistics.routes.courses import router as CourseRouter
from statistics.statistics.routes.grades import router as GradeRouter

from fastapi import FastAPI

app = FastAPI()


@app.on_event("startup")  # type: ignore
async def start_database() -> None:
    initialize_db()


@app.get("/", tags=["Root"])  # type: ignore
async def read_root() -> dict:
    return {"message": "welcome"}


app.include_router(GradeRouter, tags=["Grades"], prefix="/grades")
app.include_router(CourseRouter, tags=["Courses"], prefix="/courses")
app.include_router(CourseStats, tags=["CourseStatistics"], prefix="/course_stats")
