from datetime import date, timedelta
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlmodel import Session, func, select

from backend.auth import get_current_active_user, verify_admin
from backend.db import get_session
from backend.dependencies import paginacion_comun
from backend.models import Asistencia, Compra, Sucursal, Tabla_Inventario, Ticket, Usuario
from backend.schemas import (
    PaginacionAsistencias,
    PaginacionCompras,
    PaginacionInventarios,
    PaginacionSucursales,
    PaginacionUsuarios,
    SucursalCreate,
    SucursalRead,
    SucursalUpdate,
    TicketRead,
    UsuarioRead,
)

router = APIRouter(dependencies=[Depends(get_current_active_user)])

@router.get("", response_model=PaginacionSucursales)
async def obtener_sucursales(
    paginacion: dict = Depends(paginacion_comun),
    current_user: Usuario = Depends(verify_admin),
    session: Session=Depends(get_session)
) -> PaginacionSucursales:
    statement = select(Sucursal).where(Sucursal.estaActivo)

    count_statement = statement.with_only_columns(func.count())
    total_records = session.exec(count_statement).one()

    statement = statement.offset(paginacion["skip"]).limit(paginacion["limit"])

    resultados = session.exec(statement)
    sucursales = resultados.all()
    return {"total": total_records, "items": sucursales}


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
    if not sucursal.estaActivo:
        raise HTTPException(status_code=400, detail="LA SUCURSAL YA FUE DADA DE BAJA")
    sucursal.estaActivo = False
    session.add(sucursal)
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


@router.get("/{sucursal_id}/usuarios", response_model=PaginacionUsuarios)
async def obtener_usuarios_sucursal(
    sucursal_id: Annotated[int, Path(title="ID de la sucursal")],
    paginacion: dict = Depends(paginacion_comun),
    current_user: Usuario = Depends(verify_admin),
    session: Session=Depends(get_session)
) -> PaginacionUsuarios:
    sucursal = session.get(Sucursal, sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL INDICADA, NO ENCONTRADA")
    statement = select(Usuario).where(Usuario.idSucursal==sucursal_id) 

    count_statement = statement.with_only_columns(func.count())
    total_records = session.exec(count_statement).one()

    statement = statement.offset(paginacion["skip"]).limit(paginacion["limit"])
    results = session.exec(statement).all()
    
    return {"total": total_records, "items": results}


@router.get("/{sucursal_id}/asistencias", response_model=PaginacionAsistencias)
async def obtener_asistencias_sucursal(
    sucursal_id: Annotated[int, Path(title="ID de la sucursal")],
    paginacion: dict = Depends(paginacion_comun), 
    current_user: Usuario = Depends(get_current_active_user),
    session : Session = Depends(get_session)
) -> PaginacionAsistencias:
    if current_user.rol=="CAJERO" and sucursal_id != current_user.idSucursal:
        raise HTTPException(status_code=403, detail="El cajero actual no puede consultar informacion de otra sucursal")
    sucursal = session.get(Sucursal, sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL INDICADA, NO ENCONTRADA")
    statement = select(Asistencia).join(Usuario).join(Sucursal).where(Usuario.idSucursal==sucursal_id)

    count_statement = statement.with_only_columns(func.count())
    total_records = session.exec(count_statement).one()

    statement = statement.offset(paginacion["skip"]).limit(paginacion["limit"])
    resultados = session.exec(statement).all()
    return {"total": total_records, "items": resultados}


@router.get("/{sucursal_id}/compras", response_model=PaginacionCompras)
async def obtener_compras_sucursal(
    sucursal_id:Annotated[int, Path(title="ID de la sucursal")],
    paginacion: dict = Depends(paginacion_comun),
    current_user: Usuario = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> PaginacionCompras:
    if current_user.rol=="CAJERO" and sucursal_id != current_user.idSucursal:
        raise HTTPException(status_code=403, detail="El cajero actual no puede consultar informacion de otra sucursal")
    sucursal = session.get(Sucursal, sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL INDICADA, NO ENCONTRADA")
    statement = select(Compra).where(Compra.idSucursal==sucursal_id)

    count_statement = statement.with_only_columns(func.count())
    total_records = session.exec(count_statement).one()

    statement = statement.offset(paginacion["skip"]).limit(paginacion["limit"])
    compras = session.exec(statement).all()
    return {"total": total_records, "items": compras}


@router.get("/{sucursal_id}/inventarios", response_model=PaginacionInventarios)
async def obtener_inventarios_sucursal(
    sucursal_id : Annotated[int, Path(title="ID de la sucursal")],
    paginacion: dict = Depends(paginacion_comun),
    current_user: Usuario = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> PaginacionInventarios:
    if current_user.rol=="CAJERO" and sucursal_id != current_user.idSucursal:
        raise HTTPException(status_code=403, detail="El cajero actual no puede consultar informacion de otra sucursal")
    sucursal = session.get(Sucursal, sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL INDICADA, NO ENCONTRADA")
    statement = select(Tabla_Inventario).where(Tabla_Inventario.idSucursal==sucursal_id)

    count_statement = statement.with_only_columns(func.count())
    total_records = session.exec(count_statement).one()

    statement = statement.offset(paginacion["skip"]).limit(paginacion["limit"])
    inventarios = session.exec(statement).all()
    return {"total": total_records, "items": inventarios}


@router.get("/{sucursal_id}/tickets", response_model=List[TicketRead])
async def obtener_tickets_sucursal(
    sucursal_id: Annotated[int, Path(title="ID de la sucursal")],
    paginacion: dict = Depends(paginacion_comun),
    current_user: Usuario = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> List[TicketRead]:
    if current_user.rol=="CAJERO" and sucursal_id != current_user.idSucursal:
        raise HTTPException(status_code=403, detail="El cajero actual no puede consultar informacion de otra sucursal")
    sucursal = session.get(Sucursal, sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL NO ENCONTRADA")
    statement = select(Ticket).where(Ticket.idSucursal==sucursal_id)

    count_statement = statement.with_only_columns(func.count())
    total_records = session.exec(count_statement).one()

    statement = statement.offset(paginacion["skip"]).limit(paginacion["limit"])
    tickets = session.exec(statement).all()
    return {"total": total_records, "items": tickets}


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
        Ticket.metodo_pago,
        func.count(Ticket.idTicket), #contar
        func.sum(Ticket.total)
    ).where(
        Ticket.idSucursal == sucursal_id, 
        Ticket.fecha == fecha, 
        Ticket.estatus == 'ACTIVO'
    ).group_by(Ticket.metodo_pago)

    # obtener lista de tuplas (cantidad, suma)
    resultados = session.exec(statement).all()

    total = 0.0
    total_efectivo = 0.0
    total_tarjeta = 0.0
    total_tickets = 0

    # mapear columnas select a tuplas
    for metodo, cantidad, suma in resultados:
        # obtener monto y conteo de acuerdo al metodo de pago
        # Aplicar or por si devuelve None
        monto = suma or 0.0
        cantidad = cantidad or 0

        # sumar ese subtotal al total
        total += monto
        total_tickets += cantidad

        if metodo == "EFECTIVO":
            total_efectivo = monto
        elif metodo == "TARJETA":
            total_tarjeta = monto
            
    return {
        "fecha": fecha,
        "cantidad_de_tickets": total_tickets,
        "desglose": {
            "efectivo": total_efectivo,
            "tarjeta": total_tarjeta
        },
        "corte_caja": total}


@router.get("/{sucursal_id}/inventarios/", response_model=PaginacionInventarios)
async def obtener_inventario_por_filtro(
    sucursal_id: Annotated[int, Path(title="ID de la sucursal")],
    filtro: Optional[str] = Query(None, description="Opciones válidas: 'stock_bajo', 'por_caducar'"),
    paginacion: dict = Depends(paginacion_comun),
    session: Session = Depends(get_session)
) -> PaginacionInventarios:
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
    count_statement = statement.with_only_columns(func.count())
    total_records = session.exec(count_statement).one()

    statement = statement.offset(paginacion["skip"]).limit(paginacion["limit"])
    resultados = session.exec(statement).all()
    return {"total": total_records, "items": resultados}
