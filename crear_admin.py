import os
from dotenv import load_dotenv
from sqlmodel import Session, select

from backend.db import engine 
from backend.models import Usuario, Sucursal
from backend.auth import get_pwd_hash

load_dotenv()

def crear_super_usuario(): 
    alias = os.getenv("SUPERADMIN_ALIAS")
    passwd = os.getenv("SUPERADMIN_PASSWD")

    if not alias or not passwd:
        print("Error: Configura SUPERADMIN_ALIAS y SUPERADMIN_PASSWD en el .env")
        return

    with Session(engine) as session:
        matriz = session.exec(select(Sucursal).where(Sucursal.direccion=="Oficina Central - SISTEMA")).first()

        if not matriz:
            print("Generando sucursal matriz...")
            matriz = Sucursal(
                direccion="Oficina Central - SISTEMA", 
                telefono="5555555555", 
                num_sucursal=10000
            )
            session.add(matriz)
            session.commit()
            session.refresh(matriz)
            print(f"Oficina central creada con ID: {matriz.idSucursal}")
        
        admin_existente = session.exec(select(Usuario).where(Usuario.alias == alias)).first()

        if admin_existente:
            print("Administrador ya existente")
        else:
            print("Generando usuario Superadmin...")
            hashed_pass = get_pwd_hash(passwd)
            admin = Usuario(
                alias=alias,
                estaActivo=True,
                rol='ADMIN',
                passwd=hashed_pass, 
                idSucursal=matriz.idSucursal 
            )
            session.add(admin)
            session.commit() 
            print("Superadmin creado con exito!")

if __name__=="__main__":
    crear_super_usuario()