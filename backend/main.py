from fastapi import FastAPI, HTTPException, Path, Query, Depends
from models import *
from db import init_db, get_session
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"mensaje": "Sistema de Farmacia Activo"}

