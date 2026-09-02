import os
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import Session, select

from backend.context import current_user_id
from backend.models import RolEnum, TokenBloqueado, Usuario

from .db import get_session

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    alias: str | None = None
    sucursal: int | None = None
    id_sub: int | None = None
    rol: str | None = None
    jti: str | None = None


#verifies if the password matches the hashed password stored
def verify_pwd(plain_pwd: str, hashed_pwd: str) -> bool:
    return pwd_context.verify(plain_pwd, hashed_pwd) #if matches or not


#hashes the plain password
def get_pwd_hash(password: str) -> str:
    return pwd_context.hash(password) 


#create the access token (generates a dict)
def create_access_token(data: dict, expires_delta:timedelta | None=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    token_id = uuid.uuid4().hex
    to_encode.update({"exp": expire, "jti": token_id}) #k,v to update
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token:str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        alias: str = payload.get("sub")
        if alias is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudieron verificar tus credenciales",
                headers={"WWW-Authenticate":"Bearer"})
        return TokenData(
            alias=alias,
            sucursal=payload.get("sucursal"),
            id_sub=payload.get("id_sub"),
            rol=payload.get("rol"),
            jti=payload.get("jti")
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudieron verificar tus credenciales",
                headers={"WWW-Authenticate":"Bearer"})


def get_current_user(token:str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    token_data = verify_token(token)
    # Buscar en db mediante el jti
    token_bloqueado = db.get(TokenBloqueado, token_data.jti)
    if token_bloqueado:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión cerrada (Token invalidado)",
            headers={"WWW-Authenticate": "Bearer"})
    # Si no esta bloqueado, conseguir usuario
    statement = select(Usuario).where(Usuario.alias==token_data.alias)
    user = db.exec(statement).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no existe",
                headers={"WWW-Authenticate":"Bearer"})
    current_user_id.set(user.idUsuario)
    return user


async def get_current_active_user(current_user: Usuario = Depends(get_current_user)):
    if not current_user.estaActivo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario Inactivo",
                headers={"WWW-Authenticate":"Bearer"})
    return current_user


def verify_admin(current_user: Usuario = Depends(get_current_user)):
    if current_user.rol != RolEnum.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo administradores pueden realizar esta operacion.")
    return current_user
