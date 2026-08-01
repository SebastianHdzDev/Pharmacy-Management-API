from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from backend.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
    Token,
    create_access_token,
    get_current_active_user,
    oauth2_scheme,
    verify_pwd,
)
from backend.db import get_session
from backend.models import TokenBloqueado, Usuario
from backend.schemas import UsuarioRead

router = APIRouter()

@router.get("/perfil", response_model=UsuarioRead)
async def obtener_perfil(current_user:Usuario = Depends(get_current_active_user)):
    return current_user


@router.post("/token", response_model=Token)
def login_para_obtener_token_acceso(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    statement = select(Usuario).where(Usuario.alias==form_data.username)
    usuario = session.exec(statement).first()
    if not usuario or not verify_pwd(form_data.password, usuario.passwd):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Informacion Erronea (alias o contraseña incorrecta)",
                headers={"WWW-Authenticate":"Bearer"})
    if not usuario.estaActivo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario Inactivo",
                headers={"WWW-Authenticate":"Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub":usuario.alias, 
              "sucursal":usuario.idSucursal,
              "id_sub":usuario.idUsuario,
              "rol":usuario.rol}, 
              expires_delta=access_token_expires
    )
    return {"access_token":access_token, "token_type":"bearer"}


@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme), 
    session: Session = Depends(get_session)
):
    try:
        # Decode it just to find out when it was supposed to expire
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_timestamp = payload.get("exp")
        id_user = payload.get("id_sub")
        jti = payload.get("jti")
        fecha_expiracion = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        
        # Save it to the Blacklist
        token_bloqueado = TokenBloqueado(jti=jti, fecha_expiracion=fecha_expiracion, id_usuario=id_user)
        session.add(token_bloqueado)
        session.commit()
        
        return {"message": "Sesión cerrada exitosamente"}
        
    except jwt.ExpiredSignatureError:
        # If it's already expired, we don't care, they are logged out anyway
        return {"message": "Sesión cerrada"}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")