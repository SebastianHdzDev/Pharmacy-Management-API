from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlmodel import Session, select

from backend.auth import get_current_active_user, get_pwd_hash, verify_admin
from backend.db import get_session
from backend.models import Asistencia, Sucursal, Usuario
from backend.schemas import AsistenciaRead, UsuarioCreate, UsuarioRead, UsuarioUpdate

router = APIRouter(dependencies=[Depends(get_current_active_user)])

@router.post("", response_model=UsuarioRead)
async def crear_usuario(
    info_usuario: UsuarioCreate,
    current_user: Usuario = Depends(verify_admin),
    session: Session = Depends(get_session)
)-> UsuarioRead:
    sucursal = session.get(Sucursal, info_usuario.idSucursal)
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL INDICADA, NO ENCONTRADA")
    usuario = session.exec(select(Usuario).where(Usuario.alias==info_usuario.alias))
    if usuario.first():
        raise HTTPException(status_code=400, detail="USUARIO YA CREADO (YA EXISTE UNO CON ESE ALIAS)")
    hashed_passwd = get_pwd_hash(info_usuario.passwd)
    usuario = Usuario.model_validate(info_usuario)
    usuario.passwd = hashed_passwd
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@router.get("", response_model=list[UsuarioRead])
async def obtener_usuarios(
    current_user: Usuario = Depends(verify_admin),
    session: Session=Depends(get_session)
) -> list[UsuarioRead]:
    statement = select(Usuario).where(Usuario.estaActivo)
    resultados = session.exec(statement)
    usuarios = resultados.all()
    return usuarios


@router.patch("/{usuario_id}", response_model=UsuarioRead)
async def actualizar_usuario(
    usuario_id: Annotated[int, Path(title="ID del usuario")],
    usuario_input: UsuarioUpdate, 
    current_user: Usuario = Depends(verify_admin),
    session : Session = Depends(get_session)
) -> UsuarioRead:
    usuario = session.get(Usuario, usuario_id)
    if not usuario: 
        raise HTTPException(status_code=404, detail="USUARIO NO ENCONTRADO")
    #generar diccionario con los datos enviados *(corregidos), solo considerando los que no son nulos
    datos = usuario_input.model_dump(exclude_unset=True) 
    #actualizar el registro con el diccionario
    usuario.sqlmodel_update(datos) 
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@router.get("/{usuario_id}/asistencias", response_model=list[AsistenciaRead])
async def obtener_asistencias_usuario(
    usuario_id: Annotated[int, Path(title="ID del usuario")],
    session: Session = Depends(get_session)
) -> list[AsistenciaRead]:
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="USUARIO NO ENCONTRADO")
    return session.exec(select(Asistencia).where(Asistencia.idUsuario==usuario_id)).all()


@router.delete("/{usuario_id}")
async def eliminar_usuario(
    usuario_id: int,
    current_user: Usuario = Depends(verify_admin),
    session: Session = Depends(get_session)
):
    statement = select(Usuario).where(Usuario.idUsuario == usuario_id)
    usuario = session.exec(statement).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if usuario.idUsuario == current_user.idUsuario:
        raise HTTPException(status_code=400, detail="¡NO PUEDES DARTE DE BAJA A TI MISMO!")
    if not usuario.estaActivo:
        raise HTTPException(status_code=400, detail="El usuario ya fue dado de baja")
    usuario.estaActivo = False
    session.add(usuario)
    session.commit()
