from fastapi import APIRouter, HTTPException, Path, Depends
from sqlmodel import Session, select
from typing import Annotated, List
from backend.db import get_session
from backend.models import Proveedor, Compra
from backend.schemas import * 
from backend.auth import get_current_active_user

router = APIRouter(dependencies=[Depends(get_current_active_user)])

@router.get("", response_model=List[ProveedorRead])
async def obtener_proveedores(
    session: Session = Depends(get_session)
) -> List[ProveedorRead]:
    statement = select(Proveedor)
    proveedores = session.exec(statement)
    return proveedores.all()


@router.get("/{proveedor_id}/compras", response_model=List[CompraRead])
async def obtener_compras_proveedores(
    proveedor_id  : Annotated[int, Path(title="ID del proveedor")],
    session : Session = Depends(get_session)
)->List[CompraRead]:
    proveedor = session.get(Proveedor, proveedor_id)
    if not proveedor:
        raise HTTPException(status_code=404, detail="PROVEEDOR NO ENCONTRADO")
    compras = session.exec(select(Compra).where(Compra.idProveedor== proveedor_id))
    return compras.all()


@router.post("", response_model=ProveedorRead)
async def crear_proveedor(
    info_proveedor : ProveedorCreate,
    session : Session = Depends(get_session)
) -> ProveedorRead:
    proveedor = Proveedor.model_validate(info_proveedor)
    session.add(proveedor)
    session.commit()
    session.refresh(proveedor)
    return proveedor


@router.patch("/{proveedor_id}", response_model=ProveedorRead)
async def actualizar_proveedor(
    proveedor_id: Annotated[int, Path(title="ID del proveedor")],
    proveedor_info : ProveedorUpdate,
    session : Session = Depends(get_session)
) -> ProveedorRead:
    proveedor = session.get(Proveedor, proveedor_id)
    if not proveedor:
        raise HTTPException(status_code=404, detail="PROVEEDOR NO ENCONTRADO")
    datos = proveedor.model_dump(exclude_unset=True)
    proveedor.sqlmodel_update(datos)
    session.add(proveedor)
    session.commit()
    session.refresh(proveedor)
    return proveedor


@router.delete("/{proveedor_id}")
async def eliminar_proveedor(
    proveedor_id: Annotated[int, Path(title="ID del proveedor")],
    session : Session = Depends(get_session)
):
    proveedor = session.get(Proveedor, proveedor_id)
    if not proveedor:
        raise HTTPException(status_code=404, detail="PROVEEDOR NO ENCONTRADO")
    session.delete(proveedor)
    session.commit()
