from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from sqlalchemy.orm import Session

import app.models
from app.config import settings
from app.database import create_database_tables, get_db
from app.routes.tasks import router as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database_tables()
    yield


app = FastAPI(
    title=settings.app_name,
    description="Task Management REST API for a DevOps CI/CD portfolio project.",
    version=settings.app_version,
    lifespan=lifespan,
)

app.include_router(tasks_router)


@app.get("/", tags=["system"])
def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health/live", tags=["health"])
def liveness_check():
    return {"status": "alive"}


@app.get("/health/ready", tags=["health"])
def readiness_check(db: Annotated[Session, Depends(get_db)]):
    db.execute(text("SELECT 1"))

    return {
        "status": "ready",
        "database": "connected",
    }


Instrumentator().instrument(app).expose(app)