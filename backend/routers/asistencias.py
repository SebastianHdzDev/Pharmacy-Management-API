from fastapi import APIRouter, HTTPException, Path, Depends
from sqlmodel import Session, select
from typing import Annotated, List
from backend.db import get_session
from backend.models import Usuario, Asistencia
from backend.schemas import * 
from backend.auth import get_current_active_user

router = APIRouter(dependencies=[Depends(get_current_active_user)])

@router.post("", response_model=Asistencia)
async def registrar_asistencia(
    info_asistencia: AsistenciaCreate,
    current_user: Usuario = Depends(get_current_active_user),
    session: Session=Depends(get_session)
) -> Asistencia:
    usuario = session.get(Usuario, info_asistencia.idUsuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="NO SE ENCONTRO EL USUARIO CON EL ID INDICADO")
    asistencia = Asistencia.model_validate(info_asistencia)
    session.add(asistencia)
    session.commit()
    session.refresh(asistencia)
    return asistencia


@router.get("", response_model=List[Asistencia])
async def obtener_asistencias(session: Session=Depends(get_session)) -> List[Asistencia]:
    statement = select(Asistencia)
    resultados = session.exec(statement)
    asistencias = resultados.all()
    return asistencias


@router.patch("/{asistencia_id}", response_model=AsistenciaRead)
async def actualizar_asistencia(
    asistencia_id: Annotated[int, Path(title="ID de la asistencia")],
    asistencia_info: AsistenciaUpdate,
    session: Session = Depends(get_session)
) -> AsistenciaRead:
    asistencia = session.get(Asistencia, asistencia_id)
    if not asistencia:
        raise HTTPException(status_code=404, detail="ASISTENCIA NO ENCONTRADA")
    datos = asistencia_info.model_dump(exclude_unset=True)
    asistencia.sqlmodel_update(datos)
    session.add(asistencia)
    session.commit()
    session.refresh(asistencia)
    return asistencia


@router.delete("/{asistencia_id}")
async def eliminar_asistencia(
    asistencia_id: Annotated[int, Path(title="ID de la asistencia")],
    session: Session = Depends(get_session)
):
    asistencia = session.get(Asistencia, asistencia_id)
    if not asistencia:
        raise HTTPException(status_code=404, detail="ASISTENCIA NO ENCONTRADA")
    session.delete(asistencia)
    session.commit()