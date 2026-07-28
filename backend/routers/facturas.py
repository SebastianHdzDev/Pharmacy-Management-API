from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from backend.auth import get_current_active_user
from backend.db import get_session
from backend.models import Factura, Ticket, Usuario
from backend.schemas import FacturaCreate, FacturaRead, FacturaUpdate

router = APIRouter(dependencies=[Depends(get_current_active_user)])

@router.get("", response_model=list[FacturaRead])
async def obtener_facturas(
    session : Session = Depends(get_session)
)->list[FacturaRead]:
    statement = select(Factura)
    facturas = session.exec(statement)
    return facturas.all()


@router.post("", response_model=FacturaRead)
async def crear_factura(
    info_factura:FacturaCreate,
    current_user: Usuario = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> FacturaRead:
    ticket = session.get(Ticket, info_factura.idTicket)
    if not ticket:
        raise HTTPException(status_code=404, detail="TICKET INDICADO NO ENCONTRADO")
    factura = Factura.model_validate(info_factura)
    session.add(factura)
    try:
        session.commit()
        session.refresh(factura)
        return factura
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Este ticket ya ha sido facturado."
        )  


@router.patch("/{factura_id}", response_model=FacturaRead)
async def actualizar_factura(
    factura_id : Annotated[int, Path(title="ID de la factura")],
    factura_info : FacturaUpdate,
    current_user: Usuario = Depends(get_current_active_user),
    session : Session = Depends(get_session)
) -> FacturaRead:
    factura = session.get(Factura, factura_id)
    if not factura:
        raise HTTPException(status_code=404, detail="FACTURA NO ENCONTRADA")
    ticket = session.get(Ticket, factura.idTicket)
    if ticket.idSucursal != current_user.idSucursal:
        raise HTTPException(status_code=403, detail="El cajero no puede modificar facturas de otra sucursal")
    if ticket.estatus=='CANCELADO':
        raise HTTPException(status_code=400, detail="TICKET CANCELADO, NO SE PUEDE CORREGIR INFORMACION")
    datos = factura_info.model_dump(exclude_unset=True)
    factura.sqlmodel_update(datos)
    session.add(factura)
    session.commit()
    session.refresh(factura)
    return factura


@router.delete("/{factura_id}")
async def eliminar_factura(
    factura_id : Annotated[int, Path(title="ID de la factura")],
    session : Session = Depends(get_session)
):
    factura = session.get(Factura, factura_id)
    if not factura:
        raise HTTPException(status_code=404, detail="FACTURA NO ENCONTRADA")
    session.delete(factura)    
    session.commit()