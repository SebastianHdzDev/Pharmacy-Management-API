from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import func
from sqlmodel import Session, select

from backend.auth import get_current_active_user, verify_admin
from backend.db import get_session
from backend.dependencies import paginacion_comun
from backend.models import Asistencia, Usuario
from backend.schemas import AsistenciaCreate, AsistenciaRead, AsistenciaUpdate, PaginacionAsistencias

router = APIRouter(dependencies=[Depends(get_current_active_user)])

@router.post("/check", response_model=Asistencia)
async def registrar_asistencia(
    current_user: Usuario = Depends(get_current_active_user),
    session: Session=Depends(get_session)
) -> Asistencia:
    # Buscar asistencia del dia de hoy WHERE idUsuario = current_user.idUsuario 
    # AND DATE(horaLlegada) = CURRENT_DATE AND horaSalida IS NULL
    statement = (
        select(Asistencia).
        where(Asistencia.idUsuario == current_user.idUsuario).
        where(func.date(Asistencia.horaLlegada.date()) == datetime.now().date()).
        where(Asistencia.horaSalida.is_(None)))
    asistencia = session.exec(statement).first()
    # Crear asistencia si no se encontro, ENTRADA
    if not asistencia:
        registro = AsistenciaCreate(
            horaLlegada = datetime.now(), 
            horaSalida = None, 
            idUsuario = current_user.idUsuario
        )
        asist = Asistencia.model_validate(registro)
        session.add(asist)
        session.commit()
        session.refresh(asist)
        return asist
    # Si ya existe, editar la existente, SALIDA
    else:  
        asistencia.horaSalida = datetime.now()
        session.add(asistencia)
        session.commit()
        session.refresh(asistencia)
        return asistencia


@router.get("", response_model=PaginacionAsistencias)
async def obtener_asistencias(
    session: Session=Depends(get_session),
    paginacion: dict = Depends(paginacion_comun),
    current_user: Usuario = Depends(verify_admin)
) -> PaginacionAsistencias:
    statement = (
        select(Asistencia).join(Usuario).where(Usuario.idSucursal == current_user.idSucursal)
    )
    # Make a statement with only columns, and counting
    count_statement = statement.with_only_columns(func.count())
    total_records = session.exec(count_statement).one() #exec and get


    # Aplply pagination to filtered query
    statement = statement.offset(paginacion["skip"]).limit(paginacion["limit"])

    resultados = session.exec(statement)
    asistencias = resultados.all()
    return {"total": total_records, "items": asistencias}


@router.patch("/{asistencia_id}", response_model=AsistenciaRead)
async def actualizar_asistencia(
    asistencia_id: Annotated[int, Path(title="ID de la asistencia")],
    asistencia_info: AsistenciaUpdate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(verify_admin)
) -> AsistenciaRead:
    asistencia = session.get(Asistencia, asistencia_id)
    if not asistencia:
        raise HTTPException(status_code=404, detail="ASISTENCIA NO ENCONTRADA")
    datos = asistencia_info.model_dump(exclude_unset=True)
    if "horaSalida" in datos and datos["horaSalida"]:
        if "horaLlegada" in datos:
            llegada = datos["horaLlegada"]
        else:
            llegada = asistencia.horaLlegada 
        if datos["horaSalida"] < llegada:
            raise HTTPException(status_code=400, detail="La hora de salida no puede ser menor a la hora de llegada")
    asistencia.sqlmodel_update(datos)
    session.add(asistencia)
    session.commit()
    session.refresh(asistencia)
    return asistencia


@router.delete("/{asistencia_id}")
async def eliminar_asistencia(
    asistencia_id: Annotated[int, Path(title="ID de la asistencia")],
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(verify_admin)
):
    asistencia = session.get(Asistencia, asistencia_id)
    if not asistencia:
        raise HTTPException(status_code=404, detail="ASISTENCIA NO ENCONTRADA")
    
    session.delete(asistencia)
    session.commit()