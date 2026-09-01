from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import func
from sqlmodel import Session, select

from backend.auth import get_current_active_user, verify_admin
from backend.db import get_session
from backend.dependencies import paginacion_comun
from backend.models import Compra, Usuario
from backend.schemas import CompraRead, CompraUpdate, PaginacionCompras

router = APIRouter(dependencies=[Depends(get_current_active_user)])

@router.get("", response_model=PaginacionCompras)
async def obtener_compras(
    paginacion: dict = Depends(paginacion_comun),
    session: Session=Depends(get_session),
    current_user: Usuario = Depends(verify_admin)
)->list[CompraRead]:
    statement = select(Compra).where(Compra.idSucursal == current_user.idSucursal)

    count_statement = statement.with_only_columns(func.count())
    total_records = session.exec(count_statement).one()

    statement = statement.offset(paginacion["skip"]).limit(paginacion["limit"])
    compras = session.exec(statement)
    return {"total": total_records, "items":compras}


@router.patch("/{compra_id}", response_model=CompraRead)
async def actualizar_compra(
    compra_info: CompraUpdate,
    compra_id: Annotated[int, Path(title="ID de la compra")],
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(verify_admin)
) -> CompraRead:
    compra = session.get(Compra, compra_id)
    if not compra:
        raise HTTPException(status_code=404, detail="COMPRA NO ENCONTRADA")
    if compra.idSucursal != current_user.idSucursal:
        raise HTTPException(status_code=403, detail="No se pueden modificar compras/surtidos de otras sucursales")
    datos = compra_info.model_dump(exclude_unset=True)
    compra.sqlmodel_update(datos)
    session.add(compra)
    session.commit()
    session.refresh(compra)
    return compra
