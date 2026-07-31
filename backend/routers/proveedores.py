from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlmodel import Session, select

from backend.auth import get_current_active_user, verify_admin
from backend.db import get_session
from backend.models import Compra, Proveedor, Usuario
from backend.schemas import CompraRead, ProveedorCreate, ProveedorRead, ProveedorUpdate

router = APIRouter(dependencies=[Depends(get_current_active_user)])

@router.get("", response_model=list[ProveedorRead])
async def obtener_proveedores(
    session: Session = Depends(get_session)
) -> list[ProveedorRead]:
    statement = select(Proveedor).where(Proveedor.estaActivo)
    proveedores = session.exec(statement)
    return proveedores.all()


@router.get("/{proveedor_id}/compras", response_model=list[CompraRead])
async def obtener_compras_proveedores(
    proveedor_id: Annotated[int, Path(title="ID del proveedor")],
    session: Session = Depends(get_session)
)->list[CompraRead]:
    proveedor = session.get(Proveedor, proveedor_id)
    if not proveedor:
        raise HTTPException(status_code=404, detail="PROVEEDOR NO ENCONTRADO")
    compras = session.exec(select(Compra).where(Compra.idProveedor== proveedor_id))
    return compras.all()


@router.post("", response_model=ProveedorRead)
async def crear_proveedor(
    info_proveedor: ProveedorCreate,
    current_user: Usuario = Depends(verify_admin),
    session: Session = Depends(get_session)
) -> ProveedorRead:
    proveedor = Proveedor.model_validate(info_proveedor)
    session.add(proveedor)
    session.commit()
    session.refresh(proveedor)
    return proveedor


@router.patch("/{proveedor_id}", response_model=ProveedorRead)
async def actualizar_proveedor(
    proveedor_id: Annotated[int, Path(title="ID del proveedor")],
    proveedor_info: ProveedorUpdate,
    current_user: Usuario = Depends(verify_admin),
    session: Session = Depends(get_session)
) -> ProveedorRead:
    proveedor = session.get(Proveedor, proveedor_id)
    if not proveedor:
        raise HTTPException(status_code=404, detail="PROVEEDOR NO ENCONTRADO")
    datos = proveedor_info.model_dump(exclude_unset=True)
    proveedor.sqlmodel_update(datos)
    session.add(proveedor)
    session.commit()
    session.refresh(proveedor)
    return proveedor


@router.delete("/{proveedor_id}")
async def eliminar_proveedor(
    proveedor_id: Annotated[int, Path(title="ID del proveedor")],
    current_user: Usuario = Depends(verify_admin),
    session: Session = Depends(get_session)
):
    proveedor = session.get(Proveedor, proveedor_id)
    if not proveedor:
        raise HTTPException(status_code=404, detail="PROVEEDOR NO ENCONTRADO")
    if not proveedor.estaActivo:
        raise HTTPException(status_code=400, detail="EL PROVEEDOR YA FUE DADO DE BAJA")
    proveedor.estaActivo = False
    session.add(proveedor)
    session.commit()
