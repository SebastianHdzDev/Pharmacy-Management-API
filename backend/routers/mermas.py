
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlmodel import Session, select

from backend.auth import get_current_active_user
from backend.db import get_session
from backend.dependencies import paginacion_comun
from backend.models import Merma, Tabla_Inventario, Usuario
from backend.schemas import MermaCreate, MermaRead, PaginacionMermas, RolEnum

router = APIRouter(dependencies=[Depends(get_current_active_user)])

@router.get("", response_model=PaginacionMermas)
async def obtener_mermas(
    paginacion: dict = Depends(paginacion_comun),
    sucursal_id: int | None = None,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_active_user)
) -> PaginacionMermas:
    statement = select(Merma)
    # Verificar rol
    if current_user.rol == RolEnum.CAJERO:
        statement = statement.where(Merma.idSucursal == current_user.idSucursal)
    elif (current_user.rol == RolEnum.ADMIN):
        if sucursal_id is not None:
            statement = statement.where(Merma.idSucursal == sucursal_id)

    count_statement = statement.with_only_columns(func.count())
    total_records = session.exec(count_statement).one()

    statement = statement.offset(paginacion["skip"]).limit(paginacion["limit"])
    resultados = session.exec(statement).all()
    return {"total": total_records, "items": resultados}


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
