from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import func
from sqlmodel import Session, select

from backend.auth import get_current_active_user
from backend.db import get_session
from backend.dependencies import paginacion_comun
from backend.models import Detalle_Venta, Factura, Ticket, Usuario
from backend.schemas import FacturaRead, PaginacionDetallesVenta, PaginacionTickets

router = APIRouter(dependencies=[Depends(get_current_active_user)])

@router.get("", response_model=PaginacionTickets)
async def obtener_tickets(
    paginacion: dict = Depends(paginacion_comun),
    session:Session = Depends(get_session),
    current_user : Usuario = Depends(get_current_active_user)
) -> PaginacionTickets:
    statement = select(Ticket).where(Ticket.idSucursal == current_user.idSucursal)

    count_statement = statement.with_only_columns(func.count())
    total_records = session.exec(count_statement).one()

    statement = statement.offset(paginacion["skip"]).limit(paginacion["limit"])
    tickets = session.exec(statement).all()
    return {"total": total_records, "items": tickets}


@router.get("/{ticket_id}/detalles-venta", response_model=PaginacionDetallesVenta)
async def obtener_detalles_venta_ticket(
    ticket_id: Annotated[int, Path(title="ID del ticket")],
    paginacion: dict = Depends(paginacion_comun),
    current_user: Usuario = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> PaginacionDetallesVenta:
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="TICKET NO ENCONTRADO")
    statement = select(Detalle_Venta).where(Detalle_Venta.idTicket==ticket_id)

    count_statement = statement.with_only_columns(func.count())
    total_records = session.exec(count_statement).one()

    statement = statement.offset(paginacion["skip"]).limit(paginacion["limit"])
    detalles = session.exec(statement).all()
    return {"total": total_records, "items": detalles}


@router.get("/{ticket_id}/facturas", response_model=FacturaRead)
async def obtener_factura_ticket(
    ticket_id : Annotated[int, Path(title="ID del ticket")],
    current_user: Usuario = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> FacturaRead:
    ticket = session.get(Ticket, ticket_id)
    if not ticket: 
        raise HTTPException(status_code=404, detail="TICKET NO ENCONTRADO")
    statement = select(Factura).where(Factura.idTicket==ticket_id)
    factura = session.exec(statement)
    return factura.first()
