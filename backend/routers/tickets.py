from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlmodel import Session, select

from backend.auth import get_current_active_user
from backend.db import get_session
from backend.models import Detalle_Venta, Factura, Ticket, Usuario
from backend.schemas import Detalle_VentaRead, FacturaRead, TicketRead

router = APIRouter(dependencies=[Depends(get_current_active_user)])

@router.get("", response_model=List[TicketRead])
async def obtener_tickets(session:Session = Depends(get_session))->List[TicketRead]:
    statement = select(Ticket)
    tickets = session.exec(statement)
    return tickets.all()


@router.get("/{ticket_id}/detalles-venta", response_model=List[Detalle_VentaRead])
async def obtener_detalles_venta_ticket(
    ticket_id: Annotated[int, Path(title="ID del ticket")],
    current_user: Usuario = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> List[Detalle_VentaRead]:
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="TICKET NO ENCONTRADO")
    statement = select(Detalle_Venta).where(Detalle_Venta.idTicket==ticket_id)
    detalles = session.exec(statement)
    return detalles.all()


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
