from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt 
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from backend.models import Usuario
from passlib.context import CryptContext
from .db import get_session
from sqlmodel import Session, select
import os
from dotenv import load_dotenv
# install fastapi, sqlmodel, pyjwt, "pwdlib[argon2]", passlib

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
    alias: Optional[str] = None
    sucursal: Optional[int] = None
    id_sub: Optional[int] = None
    rol: Optional[str] = None


#verifies if the password matches the hashed password stored
def verify_pwd(plain_pwd: str, hashed_pwd: str) -> bool:
    return pwd_context.verify(plain_pwd, hashed_pwd) #if matches or not


#hashes the plain password
def get_pwd_hash(password: str) -> str:
    return pwd_context.hash(password) 


#create the access token (generates a dict)
def create_access_token(data: dict, expires_delta:Optional[timedelta]=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire}) #k,v to update
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
            rol=payload.get("rol")
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudieron verificar tus credenciales",
                headers={"WWW-Authenticate":"Bearer"})


def get_current_user(token:str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    token_data = verify_token(token)
    statement = select(Usuario).where(Usuario.alias==token_data.alias)
    user = db.exec(statement).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no existe",
                headers={"WWW-Authenticate":"Bearer"})
    return user


async def get_current_active_user(current_user: Usuario = Depends(get_current_user)):
    if not current_user.estaActivo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario Inactivo",
                headers={"WWW-Authenticate":"Bearer"})
    return current_user
