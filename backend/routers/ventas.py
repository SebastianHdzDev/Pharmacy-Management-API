from backend.models import Tabla_Inventario
from fastapi import APIRouter, HTTPException, Depends, Path
from sqlmodel import Session, select
from typing import Annotated
from backend.db import get_session
from backend.models import Usuario, Detalle_Venta, Ticket
from backend.schemas import * 
from backend.auth import get_current_active_user
from datetime import timedelta, date

router = APIRouter(dependencies=[Depends(get_current_active_user)])

@router.post('', response_model=TicketRead)
async def registrarVenta(
    cart: VentaRequest, 
    current_user: Usuario = Depends(get_current_active_user),
    session: Session=Depends(get_session)
) -> TicketRead:
    # Extraer ID de sucursal del token 
    ticket_info = TicketCreate("ACTIVO", cart.cliente, current_user.idSucursal)
    ticket = Ticket.model_validate(ticket_info)
    session.add(ticket)
    session.flush() # Hacer commit temporal, no definitivo

    total = 0.0

    for detalle in cart.carrito:
        # Evitar condicion de carrera
        statement = select(Tabla_Inventario).where(
            Tabla_Inventario.idInventario == detalle.idInventario
        ).with_for_update() 
    
        inventario = session.exec(statement).first()
        if not inventario:
            raise HTTPException(status_code=404, detail=f"Inventario no encontrado: {detalle.idInventario}")
        # Verificar si el inventario satisface la venta
        if inventario.cantidad < detalle.cantidad:
            raise HTTPException(status_code=400, 
                                detail=f"Stock insuficiente en lote {inventario.lote}. "
                                       f"Disponible: {inventario.cantidad}, Solicitado: {detalle.cantidad}")
        
        # Verificar fecha de caducidad (no vender medicamentos caducados)
        if inventario.fechaCaducidad < date.today():
            raise HTTPException(status_code=400, 
                                detail="No se pueden vender medicamentos caducos."
                                    f"Caducidad inventario {inventario.fechaCaducidad}, Fecha hoy: {datetime.today()}")

        # Actualizar inventario y calcular total
        inventario.cantidad -= detalle.cantidad
        session.add(inventario)
        total += (detalle.precio_final * detalle.cantidad)

        # Crear detalle de venta
        detalle_venta_info = Detalle_Venta(
            cantidad=detalle.cantidad, 
            idInventario=inventario.idInventario, 
            idTicket=ticket.idTicket,
            precio_final=detalle.precio_final
        )
        detalle_venta = Detalle_Venta.model_validate(detalle_venta_info)
        session.add(detalle_venta)
    
    ticket.total = total
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


@router.post('/{ticket_id}/devolucion', response_model=TicketRead)
async def realizar_devolucion(
    ticket_id: Annotated[int, Path(title="ID del ticket")],
    session: Session = Depends(get_session)
) -> TicketRead:
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="TICKET NO ENCONTRADO")
    if ticket.estatus == "CANCELADO":
        raise HTTPException(status_code=400, detail="EL PROCESO YA NO ESTA DISPONIBLE PARA ESTE TICKET")
    
    # Verificar si ticket tiene menos de 24 horas
    diferencia_dias = date.today() - ticket.fecha
    if diferencia_dias > timedelta(days=1):
        raise HTTPException(status_code=400, detail="Solo se aceptan devoluciones dentro de las primeras 24 horas")

    # Conseguir todos los detalles de venta asociados al ticket
    statement = select(Detalle_Venta).where(Detalle_Venta.idTicket==ticket_id)
    resultados = session.exec(statement)
    for row in resultados:
        statement = select(Tabla_Inventario).where(
            Tabla_Inventario.idInventario == row.idInventario
        ).with_for_update()
        inventario = session.exec(statement).first()

        if not inventario:
            raise HTTPException(status_code=404, detail="INVENTARIO NO ENCONTRADO")
        
        # Verificar que la diferencia entre el medicamento y fecha actual sea de 1 mes al menos
        if inventario.fechaCaducidad < date.today() + timedelta(days=30):
            raise HTTPException(
                status_code=400, 
                detail="No se aceptan devoluciones de medicamentos próximos a caducar (menos de 30 días)."
            )

        inventario.cantidad += row.cantidad
        # Actualizar inventario con patch
        session.add(inventario)
        
    # Poner el estado del ticket en CANCELADO
    ticket.estatus = 'CANCELADO'
    session.add(ticket)
    session.commit()
    return ticket
