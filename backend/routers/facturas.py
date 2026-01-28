from fastapi import APIRouter, HTTPException, Path, Depends
from sqlmodel import Session, select
from typing import Annotated, List

from backend.db import get_session
from backend.models import Factura, Ticket
from backend.schemas import * 

router = APIRouter()

@router.get("/facturas", response_model=List[FacturaRead])
async def obtener_facturas(
    session : Session = Depends(get_session)
)->List[FacturaRead]:
    statement = select(Factura)
    facturas = session.exec(statement)
    return facturas.all()


@router.post("/facturas", response_model=FacturaRead)
async def crear_factura(
    info_factura:FacturaCreate,
    session: Session = Depends(get_session)
) -> FacturaRead:
    ticket = session.get(Ticket, info_factura.idTicket)
    if not ticket:
        raise HTTPException(status_code=404, detail="TICKET INDICADO NO ENCONTRADO")
    factura = Factura.model_validate(info_factura)
    session.add(factura)
    session.commit()
    session.refresh(factura)
    return factura


@router.patch("/facturas/{factura_id}", response_model=FacturaRead)
async def actualizar_factura(
    factura_id : Annotated[int, Path(title="ID de la factura")],
    factura_info : FacturaUpdate,
    session : Session = Depends(get_session)
) -> FacturaRead:
    factura = session.get(Factura, factura_id)
    if not factura:
        raise HTTPException(status_code=404, detail="FACTURA NO ENCONTRADA")
    ticket = session.get(Ticket, factura.idTicket)
    if ticket.estatus=='CANCELADO':
        raise HTTPException(status_code=400, detail="TICKET CANCELADO, NO SE PUEDE CORREGIR INFORMACION")
    datos = factura_info.model_dump(exclude_unset=True)
    factura.sqlmodel_update(datos)
    session.add(factura)
    session.commit()
    session.refresh(factura)
    return factura


@router.delete("/facturas/{factura_id}")
async def actualizar_factura(
    factura_id : Annotated[int, Path(title="ID de la factura")],
    session : Session = Depends(get_session)
):
    factura = session.get(Factura, factura_id)
    if not factura:
        raise HTTPException(status_code=404, detail="FACTURA NO ENCONTRADA")
    session.delete(factura)    
    session.commit()