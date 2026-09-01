from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import func
from sqlmodel import Session, select

from backend.auth import get_current_active_user, verify_admin
from backend.db import get_session
from backend.dependencies import paginacion_comun
from backend.models import Compra, Proveedor, Usuario
from backend.schemas import (
    PaginacionCompras,
    PaginacionProveedores,
    ProveedorCreate,
    ProveedorRead,
    ProveedorUpdate,
)

router = APIRouter(dependencies=[Depends(get_current_active_user)])

@router.get("", response_model=PaginacionProveedores)
async def obtener_proveedores(
    paginacion: dict = Depends(paginacion_comun),
    session: Session = Depends(get_session)
) -> PaginacionProveedores:
    statement = select(Proveedor).where(Proveedor.estaActivo)

    count_statement = statement.with_only_columns(func.count())
    total_records = session.exec(count_statement).one()

    statement = statement.offset(paginacion["skip"]).limit(paginacion["limit"])
    proveedores = session.exec(statement).all()
    return {"total": total_records, "items": proveedores}


@router.get("/{proveedor_id}/compras", response_model=PaginacionCompras)
async def obtener_compras_proveedores(
    proveedor_id: Annotated[int, Path(title="ID del proveedor")],
    paginacion: dict = Depends(paginacion_comun),
    session: Session = Depends(get_session)
) -> PaginacionCompras:
    proveedor = session.get(Proveedor, proveedor_id)
    if not proveedor:
        raise HTTPException(status_code=404, detail="PROVEEDOR NO ENCONTRADO")
    statement = select(Compra).where(Compra.idProveedor == proveedor_id)

    count_statement = statement.with_only_columns(func.count())
    total_records = session.exec(count_statement).one()

    statement = statement.offset(paginacion["skip"]).limit(paginacion["limit"])
    compras = session.exec(statement).all()
    return {"total": total_records, "items": compras}


@router.post("", response_model=ProveedorRead)
async def crear_proveedor(
    info_proveedor: ProveedorCreate,
    current_user: Usuario = Depends(verify_admin),
    session: Session = Depends(get_session)
) -> ProveedorRead:
    proveedor = Proveedor.model_validate(info_proveedor)
    session.add(proveedor)
    session.commit()
    session.refresh(proveedor)
    return proveedor


@router.patch("/{proveedor_id}", response_model=ProveedorRead)
async def actualizar_proveedor(
    proveedor_id: Annotated[int, Path(title="ID del proveedor")],
    proveedor_info: ProveedorUpdate,
    current_user: Usuario = Depends(verify_admin),
    session: Session = Depends(get_session)
) -> ProveedorRead:
    proveedor = session.get(Proveedor, proveedor_id)
    if not proveedor:
        raise HTTPException(status_code=404, detail="PROVEEDOR NO ENCONTRADO")
    datos = proveedor_info.model_dump(exclude_unset=True)
    proveedor.sqlmodel_update(datos)
    session.add(proveedor)
    session.commit()
    session.refresh(proveedor)
    return proveedor


@router.delete("/{proveedor_id}")
async def eliminar_proveedor(
    proveedor_id: Annotated[int, Path(title="ID del proveedor")],
    current_user: Usuario = Depends(verify_admin),
    session: Session = Depends(get_session)
):
    proveedor = session.get(Proveedor, proveedor_id)
    if not proveedor:
        raise HTTPException(status_code=404, detail="PROVEEDOR NO ENCONTRADO")
    if not proveedor.estaActivo:
        raise HTTPException(status_code=400, detail="EL PROVEEDOR YA FUE DADO DE BAJA")
    proveedor.estaActivo = False
    session.add(proveedor)
    session.commit()
