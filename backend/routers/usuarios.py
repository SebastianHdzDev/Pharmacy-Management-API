from fastapi import APIRouter, HTTPException, Path, Depends
from sqlmodel import Session, select
from typing import Annotated, List
from backend.db import get_session
from backend.models import Sucursal, Usuario, Asistencia
from backend.schemas import * 
from backend.auth import *

router = APIRouter(dependencies=[Depends(get_current_active_user)])

@router.post("/usuarios", response_model=UsuarioRead)
async def crear_usuario(
        info_usuario: UsuarioCreate,
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


@router.get("/usuarios", response_model=List[UsuarioRead])
async def obtener_usuarios(session: Session=Depends(get_session)) -> List[UsuarioRead]: 
    statement = select(Usuario)
    resultados = session.exec(statement)
    usuarios = resultados.all()
    return usuarios


@router.patch("/usuarios/{usuario_id}", response_model=UsuarioRead)
async def actualizar_usuario(
    usuario_id : Annotated[int, Path(title="ID del usuario")],
    usuario_input : UsuarioUpdate, 
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

@router.get("/usuarios/{usuario_id}/asistencias", response_model=List[AsistenciaRead])
async def obtener_asistencias_usuario(
    usuario_id: Annotated[int, Path(title="ID del usuario")],
    session : Session = Depends(get_session)
) -> List[AsistenciaRead]:
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="USUARIO NO ENCONTRADO")
    return session.exec(select(Asistencia).where(Asistencia.idUsuario==usuario_id)).all()


@router.delete("/usuarios/{usuario_id}")
async def eliminar_usuario(
    usuario_id: int,
    current_user: Usuario = Depends(get_current_active_user), 
    session: Session = Depends(get_session)
):
    statement = select(Usuario).where(Usuario.idUsuario==usuario_id)
    usuario = session.exec(statement).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if usuario.id == current_user.idUsuario:
        raise HTTPException(status_code=404, detail="¡NO PUEDES ELIMINARTE A TI MISMO!")
    session.delete(usuario)
    session.commit()
