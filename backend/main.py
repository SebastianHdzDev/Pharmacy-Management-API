from contextlib import asynccontextmanager

from fastapi import FastAPI

import backend.audit  # noqa: F401

from .db import init_db
from .routers import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan, title="Sistema de Farmacia")

app.include_router(router, prefix="/api/v1")

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok"}