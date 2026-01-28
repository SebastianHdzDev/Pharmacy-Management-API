from fastapi import APIRouter, HTTPException, Path, Depends
from sqlmodel import Session, select
from typing import Annotated, List

from backend.db import get_session
from backend.models import Compra, Sucursal
from backend.schemas import * 

router = APIRouter()

@router.get("/compras", response_model=List[CompraRead])
async def obtener_compras(session:Session=Depends(get_session))->List[CompraRead]:
    statement = select(Compra)
    compras = session.exec(statement)
    return compras.all()


@router.post("/compras", response_model=CompraRead)
async def crear_compra(
    info_compra : CompraCreate,
    session : Session = Depends(get_session)
) -> CompraRead:
    sucursal = session.get(Sucursal, info_compra.idSucursal)
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL INDICADA, NO ENCONTRADA")
    compra = Compra.model_validate(info_compra)
    session.add(compra)
    session.commit()
    session.refresh(compra)
    return compra


@router.patch("/compras/{compra_id}", response_model=CompraRead)
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


@router.delete("/compras/{compra_id}")
async def eliminar_compra(
    compra_id: Annotated[int, Path(title="ID de la compra")],
    session : Session = Depends(get_session)
): 
    compra = session.get(Compra, compra_id)
    if not compra: 
        raise HTTPException(status_code=404, detail="COMPRA NO ENCONTRADA")
    session.delete(compra)
    session.commit()