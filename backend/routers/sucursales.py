from datetime import date, timedelta
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlmodel import Session, func, select

from backend.auth import get_current_active_user, verify_admin
from backend.db import get_session
from backend.models import Asistencia, Compra, Sucursal, Tabla_Inventario, Ticket, Usuario
from backend.schemas import (
    AsistenciaRead,
    CompraRead,
    SucursalCreate,
    SucursalRead,
    SucursalUpdate,
    Tabla_InventarioRead,
    TicketRead,
    UsuarioRead,
)

router = APIRouter(dependencies=[Depends(get_current_active_user)])

@router.get("", response_model=List[Sucursal])
async def obtener_sucursales(
    current_user: Usuario = Depends(verify_admin),
    session: Session=Depends(get_session)
) -> List[Sucursal]:
    statement = select(Sucursal)
    resultados = session.exec(statement)
    sucursales = resultados.all()
    return sucursales


@router.get("/{sucursal_id}", response_model=Sucursal)
async def obtener_sucursal(
    sucursal_id: Annotated[int, Path(title="ID de la sucursal")],
    session: Session = Depends(get_session) #ejecución implicita de with Session(engine)
) -> Sucursal:
    sucursal = session.get(Sucursal, sucursal_id) #Tabla, parametro{id}
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL NO ENCONTRADA")
    return sucursal #retornar si se encontro 


@router.post("", response_model=SucursalRead)
async def crear_sucursal(
    info_sucursal: SucursalCreate,
    current_user: Usuario = Depends(verify_admin),
    session: Session=Depends(get_session)
) -> SucursalRead:    
    sucursal = Sucursal.model_validate(info_sucursal) #valida todo el objeto

    session.add(sucursal) #añade solo en memoria (no en la bd)
    
    session.commit() #commit a tabla en la bd, usa el engine para almacenar en la bd
    session.refresh(sucursal) #refresh datos
    return sucursal


@router.patch("/{sucursal_id}", response_model=SucursalRead)
async def actualizar_sucursal(
    sucursal_id: Annotated[int, Path(title="ID de la sucursal")],
    sucursal_info: SucursalUpdate,
    current_user: Usuario = Depends(verify_admin),
    session: Session = Depends(get_session)
) -> SucursalRead:
    sucursal = session.get(Sucursal, sucursal_id) #Tabla, parametro{id}
    if sucursal is None:
        raise HTTPException(status_code=404, detail="SUCURSAL NO ENCONTRADA")
    datos = sucursal_info.model_dump(exclude_unset=True)
    sucursal.sqlmodel_update(datos)
    session.add(sucursal)
    session.commit()
    session.refresh(sucursal)
    return sucursal


@router.delete("/{sucursal_id}")
async def eliminar_sucursal(
    sucursal_id: Annotated[int, Path(title="ID de la sucursal")],
    current_user: Usuario = Depends(verify_admin),
    session: Session = Depends(get_session)
):
    sucursal = session.get(Sucursal, sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL NO ENCONTRADA")
    session.delete(sucursal)
    session.commit()


@router.get("/{sucursal_id}/usuarios/{usuario_id}", response_model=UsuarioRead)
async def obtener_usuario_sucursal(
    usuario_id: Annotated[int, Path(title="ID del usuario")],
    sucursal_id: Annotated[int, Path(title="ID de la sucursal")],
    session: Session=Depends(get_session)
):
    sucursal = session.get(Sucursal, sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL INDICADA NO ENCONTRADA")
    statement = select(Usuario).where(Usuario.idSucursal==sucursal_id).where(Usuario.idUsuario==usuario_id)
    usuarios = session.exec(statement)
    usuario = usuarios.first()
    if not usuario:
        raise HTTPException(status_code=404, detail="USUARIO NO ENCONTRADO")
    return usuario


@router.get("/{sucursal_id}/usuarios", response_model=List[UsuarioRead])
async def obtener_usuarios_sucursal(
    sucursal_id: Annotated[int, Path(title="ID de la sucursal")],
    current_user: Usuario = Depends(verify_admin),
    session: Session=Depends(get_session)
) -> List[UsuarioRead]:
    sucursal = session.get(Sucursal, sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL INDICADA, NO ENCONTRADA")
    statement = select(Usuario).where(Usuario.idSucursal==sucursal_id) 
    results = session.exec(statement)
    usuarios = results.all()
    return usuarios


@router.get("/{sucursal_id}/asistencias", response_model=List[AsistenciaRead])
async def obtener_asistencias_sucursal(
    sucursal_id: Annotated[int, Path(title="ID de la sucursal")],
    current_user: Usuario = Depends(get_current_active_user),
    session : Session = Depends(get_session)
) -> List[AsistenciaRead]:
    if current_user.rol=="CAJERO" and sucursal_id != current_user.idSucursal:
        raise HTTPException(status_code=403, detail="El cajero actual no puede consultar informacion de otra sucursal")
    sucursal = session.get(Sucursal, sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL INDICADA, NO ENCONTRADA")
    statement = select(Asistencia).join(Usuario).join(Sucursal).where(Usuario.idSucursal==sucursal_id)
    resultados = session.exec(statement)
    return resultados.all()


@router.get("/{sucursal_id}/compras", response_model=List[CompraRead])
async def obtener_compras_sucursal(
    sucursal_id:Annotated[int, Path(title="ID de la sucursal")],
    current_user: Usuario = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> List[CompraRead]:
    if current_user.rol=="CAJERO" and sucursal_id != current_user.idSucursal:
        raise HTTPException(status_code=403, detail="El cajero actual no puede consultar informacion de otra sucursal")
    sucursal = session.get(Sucursal, sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL INDICADA, NO ENCONTRADA")
    statement = select(Compra).where(Compra.idSucursal==sucursal_id)
    compras = session.exec(statement)
    return compras.all()


@router.get("/{sucursal_id}/inventarios", response_model=List[Tabla_InventarioRead])
async def obtener_inventarios_sucursal(
    sucursal_id : Annotated[int, Path(title="ID de la sucursal")],
    current_user: Usuario = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> List[Tabla_InventarioRead]:
    if current_user.rol=="CAJERO" and sucursal_id != current_user.idSucursal:
        raise HTTPException(status_code=403, detail="El cajero actual no puede consultar informacion de otra sucursal")
    sucursal = session.get(Sucursal, sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL INDICADA, NO ENCONTRADA")
    statement = select(Tabla_Inventario).where(Tabla_Inventario.idSucursal==sucursal_id)
    inventarios = session.exec(statement)
    return inventarios.all()


@router.get("/{sucursal_id}/tickets", response_model=List[TicketRead])
async def obtener_tickets_sucursal(
    sucursal_id: Annotated[int, Path(title="ID de la sucursal")],
    current_user: Usuario = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> List[TicketRead]:
    if current_user.rol=="CAJERO" and sucursal_id != current_user.idSucursal:
        raise HTTPException(status_code=403, detail="El cajero actual no puede consultar informacion de otra sucursal")
    sucursal = session.get(Sucursal, sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL NO ENCONTRADA")
    statement = select(Ticket).where(Ticket.idSucursal==sucursal_id)
    tickets = session.exec(statement)
    return tickets.all()


@router.get('/{sucursal_id}/corte-caja')
async def obtener_corte_caja(
    sucursal_id: Annotated[int, Path(title="ID de la sucursal")],
    fecha: date,
    current_user: Usuario = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    if current_user.rol=="CAJERO" and sucursal_id != current_user.idSucursal:
        raise HTTPException(status_code=403, detail="El cajero actual no puede consultar informacion de otra sucursal")

    sucursal = session.get(Sucursal, sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL NO ENCONTRADA")
    
    # Conseguir tickets de la sucursal, con la fecha de hoy y activos
    statement = select(
        func.count(Ticket.idTicket), #contar
        func.sum(Ticket.total)
    ).where(
        Ticket.idSucursal == sucursal_id, 
        Ticket.fecha == fecha, 
        Ticket.estatus == 'ACTIVO'
    )
    # obtener tupla (cantidad, suma)
    resultados = session.exec(statement).fetchone()

    # Aplicar or por si devuelve None
    # resultados[0] = count 
    cantidad_tickets = resultados[0] or 0

    # resultados[1] = sum
    corte_caja = resultados[1] or 0.0

    return {
        "fecha": fecha,
        "cantidad_de_tickets": cantidad_tickets,
        "corte_caja": corte_caja}


@router.get("/{sucursal_id}/inventarios/", response_model=List[Tabla_Inventario])
async def obtener_inventario_por_filtro(
    sucursal_id: Annotated[int, Path(title="ID de la sucursal")],
    filtro: Optional[str] = Query(None, description="Opciones válidas: 'stock_bajo', 'por_caducar'"),
    session: Session = Depends(get_session)
) -> List[Tabla_Inventario]:
    statement = select(Tabla_Inventario).where(Tabla_Inventario.idSucursal == sucursal_id)

    if filtro == "stock_bajo":
        statement = statement.where(Tabla_Inventario.cantidad <= 10)
    elif filtro== "por_caducar":
        # Proximos a 3 meses
        limite_caducidad = date.today() + timedelta(days=90)
        statement = statement.where(Tabla_Inventario.fechaCaducidad <= limite_caducidad)

        # Agregar solo las que todavia no han expirado
        statement = statement.where(Tabla_Inventario.fechaCaducidad >= date.today())
    elif filtro is not None:
        # Cualquier otra cosa ingresada en el filtro genera una excepcion
        raise HTTPException(status_code=400, detail="Filtro no válido")
    return session.exec(statement).all()
