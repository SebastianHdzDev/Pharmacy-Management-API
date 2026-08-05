from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlmodel import Session, select

from backend.auth import get_current_active_user, verify_admin
from backend.db import get_session
from backend.models import Asistencia, Usuario
from backend.schemas import AsistenciaCreate, AsistenciaRead, AsistenciaUpdate

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
    if usuario.idUsuario != current_user.idUsuario:
        raise HTTPException(status_code=403, detail="NO SE PUEDE CREAR ASISTENCIAS DE OTROS USUARIOS")
    asistencia = Asistencia.model_validate(info_asistencia)
    session.add(asistencia)
    session.commit()
    session.refresh(asistencia)
    return asistencia


@router.get("", response_model=list[Asistencia])
async def obtener_asistencias(
    session: Session=Depends(get_session),
    current_user: Usuario = Depends(verify_admin)
) -> list[Asistencia]:
    statement = select(Asistencia).join(Usuario).where(Usuario.idSucursal == current_user.idSucursal)
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
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(verify_admin)
):
    asistencia = session.get(Asistencia, asistencia_id)
    if not asistencia:
        raise HTTPException(status_code=404, detail="ASISTENCIA NO ENCONTRADA")
    
    session.delete(asistencia)
    session.commit()