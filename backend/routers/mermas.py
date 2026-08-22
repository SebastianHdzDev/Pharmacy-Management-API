from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.auth import get_current_active_user
from backend.db import get_session
from backend.models import Merma, Tabla_Inventario, Usuario
from backend.schemas import MermaCreate, MermaRead, RolEnum

router = APIRouter(dependencies=[Depends(get_current_active_user)])

@router.get("", response_model=List[MermaRead])
async def obtener_mermas(
    sucursal_id: int | None = None,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_active_user)
) -> List[MermaRead]:
    statement = select(Merma)
    # Verificar rol
    if current_user.rol == RolEnum.CAJERO:
        statement = statement.where(Merma.idSucursal == current_user.idSucursal)
    elif (current_user.rol == RolEnum.ADMIN):
        if sucursal_id is not None:
            statement = statement.where(Merma.idSucursal == sucursal_id)
    resultados = session.exec(statement)
    return resultados.all()


@router.post("", response_model=MermaRead)
def crear_merma(
    req: MermaCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_active_user)
) -> MermaRead:
    statement = (
        select(Tabla_Inventario).where(Tabla_Inventario == req.idInventario).
        with_for_update()
    )
    inventario = session.exec(statement).first()
    if not inventario:
        raise HTTPException(status_code=404, detail="Inventario NO encontrado")
    if inventario.idSucursal != current_user.idSucursal:
        raise HTTPException(status_code=403, detail="No se pueden crear mermas de otras sucursales")
    if inventario.cantidad < req.cantidad:
        raise HTTPException(status_code=400, detail="""No es posible declarar merma con cantidad mayor 
                                                    a la del inventario indicado""")
    #Actualizar inventario 
    inventario.cantidad -= req.cantidad
    session.add(inventario)

    merma = Merma(
        cantidad = req.cantidad,
        motivo = req.motivo,
        descripcion = req.descripcion,
        idInventario = req.idInventario,
        idUsuario = current_user.idUsuario,
        idSucursal = current_user.idSucursal
    )

    session.add(merma)
    session.commit()
    session.refresh(merma)
    return merma
