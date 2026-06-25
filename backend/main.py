from fastapi import FastAPI
from .models import *
from .schemas import *
from .db import init_db
from contextlib import asynccontextmanager
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