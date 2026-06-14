from fastapi import FastAPI, HTTPException, Path, Query, Depends
from sqlmodel import Session, select
from .models import *
from .schemas import *
from .db import init_db, get_session
from contextlib import asynccontextmanager
from typing import Annotated, List
from .routers import sucursales, usuarios, medicamentos, proveedores, compras, inventarios, tickets, detalles_venta, facturas, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan, title="Sistema de Farmacia")

app.include_router(auth.router, tags=["Autenticacion"])

app.include_router(sucursales.router, tags=["Sucursales"])

app.include_router(usuarios.router, tags=["Usuarios"])

app.include_router(medicamentos.router, tags=["Medicamentos"])

app.include_router(proveedores.router, tags=["Proveedores"])

app.include_router(compras.router, tags=["Compras"])

app.include_router(inventarios.router, tags=["Inventarios"])

app.include_router(tickets.router, tags=["Tickets"])

app.include_router(detalles_venta.router, tags=["Detalles de Venta"])

app.include_router(facturas.router, tags=["Facturas"])