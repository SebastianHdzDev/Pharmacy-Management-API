from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from backend.db import get_session
from backend.models import Usuario
from backend.schemas import * 
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from backend.auth import get_current_active_user, Token, verify_pwd, verify_token, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

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
