from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlmodel import Session

from backend.auth import get_current_active_user
from backend.db import get_session
from backend.models import Detalle_Venta, Tabla_Inventario, Ticket
from backend.schemas import Detalle_VentaCreate, Detalle_VentaRead, Detalle_VentaUpdate

router = APIRouter(dependencies=[Depends(get_current_active_user)])

@router.post("", response_model=Detalle_VentaRead)
async def crear_detalle_venta(
    info_detalle_venta: Detalle_VentaCreate,
    session: Session = Depends(get_session)
)->Detalle_VentaRead:
    ticket = session.get(Ticket, info_detalle_venta.idTicket)
    if not ticket:
        raise HTTPException(status_code=404, detail="TICKET NO ENCONTRADO")
    if ticket.estatus=='CANCELADO':
        raise HTTPException(status_code=400, detail="TICKET CANCELADO, NO SE PUEDEN AGREGAR PRODUCTOS")
    inventario = session.get(Tabla_Inventario, info_detalle_venta.idInventario)
    if not inventario:
        raise HTTPException(status_code=404, detail="EL INVENTARIO NO EXISTE")
    if info_detalle_venta.cantidad > inventario.cantidad:
        raise HTTPException(status_code=400, detail=f"STOCK INSUFICIENTE, SOLO QUEDAN {inventario.cantidad}")
    detalle_venta = Detalle_Venta.model_validate(info_detalle_venta)
    session.add(detalle_venta)
    session.commit()
    session.refresh(detalle_venta)
    return detalle_venta

@router.patch("/{detalle_venta_id}", response_model=Detalle_VentaRead)
async def actualizar_detalle_venta(
    detalle_venta_id: Annotated[int, Path(title="ID del ticket")], 
    detalle_venta_info: Detalle_VentaUpdate,
    session: Session = Depends(get_session)
) -> Detalle_VentaRead:
    detalle_venta = session.get(Detalle_Venta, detalle_venta_id)
    if not detalle_venta:
        raise HTTPException(status_code=400, detail="DETALLE DE VENTA NO ENCONTRADO")
    ticket = session.get(Ticket, detalle_venta.idTicket)
    if not ticket:
        raise HTTPException(status_code=404, detail="TICKET NO ENCONTRADO")
    if ticket.estatus=='CANCELADO':
        raise HTTPException(status_code=400, detail="TICKET CANCELADO, NO SE PUEDE CORREGIR INFORMACION")
    inventario = session.get(Tabla_Inventario, detalle_venta.idInventario)
    if not inventario:
        raise HTTPException(status_code=404, detail="EL INVENTARIO NO EXISTE")
    datos = detalle_venta_info.model_dump(exclude_unset=True)
    detalle_venta.sqlmodel_update(datos)
    session.add(detalle_venta)
    session.commit()
    session.refresh(detalle_venta)
    return detalle_venta


@router.delete("/{detalle_venta_id}")
async def eliminar_detalle_venta(
    detalle_venta_id : Annotated[int, Path(title="ID del detalle de venta")],
    session: Session = Depends(get_session)
):
    detalle = session.get(Detalle_Venta, detalle_venta_id)
    if not detalle: 
        raise HTTPException(status_code=404, detail="EL INVENTARIO NO EXISTE")
    session.delete(detalle)
    session.commit()
