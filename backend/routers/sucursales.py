from fastapi import APIRouter, HTTPException, Path, Depends
from sqlmodel import Session, select
from typing import Annotated, List
from ..db import get_session
from ..models import Sucursal, Usuario, Asistencia, Compra, Ticket, Tabla_Inventario
from ..schemas import *

router = APIRouter()

@router.get("/sucursales", response_model=List[Sucursal])
async def obtener_sucursales(session:Session=Depends(get_session))->List[Sucursal]:
    statement = select(Sucursal)
    resultados = session.exec(statement)
    sucursales = resultados.all()
    return sucursales


@router.get("/sucursales/{sucursal_id}", response_model=Sucursal)
async def obtener_sucursal(
    sucursal_id: Annotated[int, Path(title="ID de la sucursal")],
    session: Session = Depends(get_session) #ejecución implicita de with Session(engine)
) -> Sucursal:
    sucursal = session.get(Sucursal, sucursal_id) #Tabla, parametro{id}
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL NO ENCONTRADA")
    return sucursal #retornar si se encontro 


@router.post("/sucursales", response_model=SucursalRead)
async def crear_sucursal(
    info_sucursal: SucursalCreate,
    session: Session=Depends(get_session)
) -> SucursalRead:    
    sucursal = Sucursal.model_validate(info_sucursal) #valida todo el objeto

    session.add(sucursal) #añade solo en memoria (no en la bd)
    
    session.commit() #commit a tabla en la bd, usa el engine para almacenar en la bd
    session.refresh(sucursal) #refresh datos
    return sucursal


@router.patch("/sucursales/{sucursal_id}", response_model=SucursalRead)
async def actualizar_sucursal(
    sucursal_id: Annotated[int, Path(title="ID de la sucursal")],
    sucursal_info : SucursalUpdate,
    session : Session = Depends(get_session)
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


@router.delete("/sucursales/{sucursal_id}")
async def eliminar_sucursal(
    sucursal_id:Annotated[int, Path(title="ID de la sucursal")],
    session: Session = Depends(get_session)
):
    sucursal = session.get(Sucursal, sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL NO ENCONTRADA")
    session.delete(sucursal)
    session.commit()


@router.get("/sucursales/{sucursal_id}/usuarios/{usuario_id}", response_model=UsuarioRead)
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


@router.get("/sucursales/{sucursal_id}/usuarios", response_model=List[UsuarioRead])
async def obtener_usuarios_sucursal(
    sucursal_id: Annotated[int, Path(title="ID de la sucursal")],
    session: Session=Depends(get_session)
) -> List[UsuarioRead]: 
    sucursal = session.get(Sucursal, sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL INDICADA, NO ENCONTRADA")
    statement = select(Usuario).where(Usuario.idSucursal==sucursal_id) 
    results = session.exec(statement)
    usuarios = results.all()
    return usuarios


@router.get("/sucursales/{sucursal_id}/asistencias/", response_model=List[AsistenciaRead])
async def obtener_asistencias_sucursal(
    sucursal_id: Annotated[int, Path(title="ID de la sucursal")],
    session : Session = Depends(get_session)
) -> List[AsistenciaRead]:
    sucursal = session.get(Sucursal, sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL INDICADA, NO ENCONTRADA")
    statement = select(Asistencia).join(Usuario).join(Sucursal).where(Usuario.idSucursal==sucursal_id)
    resultados = session.exec(statement)
    return resultados.all()


@router.get("/sucursales/{sucursal_id}/compras", response_model=List[CompraRead])
async def obtener_compras_sucursal(
    sucursal_id:Annotated[int, Path(title="ID de la sucursal")],
    session: Session = Depends(get_session)
) -> List[CompraRead]:
    sucursal = session.get(Sucursal, sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL INDICADA, NO ENCONTRADA")
    statement = select(Compra).where(Compra.idSucursal==sucursal_id)
    compras = session.exec(statement)
    return compras.all()


@router.get("/sucursales/{sucursal_id}/inventarios", response_model=List[Tabla_InventarioRead])
async def obtener_inventarios_sucursal(
    sucursal_id : Annotated[int, Path(title="ID de la sucursal")],
    session: Session = Depends(get_session)
) -> List[Tabla_InventarioRead]:
    sucursal = session.get(Sucursal, sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL INDICADA, NO ENCONTRADA")
    statement = select(Tabla_Inventario).where(Tabla_Inventario.idSucursal==sucursal_id)
    inventarios = session.exec(statement)
    return inventarios.all()


@router.get("/sucursales/{sucursal_id}/tickets", response_model=List[TicketRead])
async def obtener_tickets_sucursal(
    sucursal_id : Annotated[int, Path(title="ID de la sucursal")],
    session : Session = Depends(get_session)
) -> List[TicketRead]:
    sucursal = session.get(Sucursal, sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL NO ENCONTRADA")
    statement = select(Ticket).where(Ticket.idSucursal==sucursal_id)
    tickets = session.exec(statement)
    return tickets.all()