from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlmodel import Session, select

from backend.auth import get_current_active_user
from backend.db import get_session
from backend.models import Compra
from backend.schemas import CompraRead, CompraUpdate

router = APIRouter(dependencies=[Depends(get_current_active_user)])

@router.get("", response_model=list[CompraRead])
async def obtener_compras(session:Session=Depends(get_session))->list[CompraRead]:
    statement = select(Compra)
    compras = session.exec(statement)
    return compras.all()


@router.patch("/{compra_id}", response_model=CompraRead)
async def actualizar_compra(
    compra_info: CompraUpdate,
    compra_id: Annotated[int, Path(title="ID de la compra")],
    session: Session = Depends(get_session)
) -> CompraRead:
    compra = session.get(Compra, compra_id)
    if not compra:
        raise HTTPException(status_code=404, detail="COMPRA NO ENCONTRADA")
    datos = compra_info.model_dump(exclude_unset=True)
    compra.sqlmodel_update(datos)
    session.add(compra)
    session.commit()
    session.refresh(compra)
    return compra
