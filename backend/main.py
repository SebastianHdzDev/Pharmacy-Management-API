from fastapi import FastAPI, HTTPException, Path, Query, Depends
from sqlmodel import Session
from models import *
from db import init_db, get_session
from contextlib import asynccontextmanager
from typing import Annotated

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"mensaje": "Sistema de Farmacia Activo"}


@app.get("/sucursales/{sucursal_id}")
async def sucursal(
    sucursal_id: Annotated[int, Path(title="ID de la sucursal")],
    session: Session = Depends(get_session) #ejecución implicita de with Session(engine)
) -> Sucursal:
    sucursal = session.get(Sucursal, sucursal_id) #Tabla, parametro{id}
    if sucursal is None:
        raise HTTPException(status_code=404, detail="SUCURSAL NO ENCONTRADA ")
    return sucursal #retornar si se encontro 

@app.post("/sucursales")
async def crear_sucursal(
    info_sucursal: Sucursal,
    session: Session=Depends(get_session)
) -> Sucursal:
    sucursal = Sucursal.model_validate(info_sucursal) #valida todo el objeto

    session.add(sucursal) #añade solo en memoria (no en la bd)

    session.commit() #commit a tabla en la bd, usa el engine para almacenar en la bd
    session.refresh(sucursal) #refresh datos
    return sucursal
#EL objeto session usa el engine, pero se usa para las operaciones con la bd
#Por cada peticion se crea una nueva sesion y cuando se termina, se debe
#cerrar la sesion 

