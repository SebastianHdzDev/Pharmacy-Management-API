from fastapi import APIRouter, HTTPException, Path, Depends
from sqlmodel import Session, select
from typing import Annotated, List
from backend.db import get_session
from backend.models import Compra, Sucursal, Medicamento, Tabla_Inventario
from backend.schemas import * 
from backend.auth import get_current_active_user

router = APIRouter(dependencies=[Depends(get_current_active_user)])

@router.get("/inventarios", response_model=List[Tabla_InventarioRead])
async def obtener_inventarios(session : Session=Depends(get_session)) -> List[Tabla_InventarioRead]:
    statement = select(Tabla_Inventario)
    inventarios = session.exec(statement)
    return inventarios.all()


@router.post("/inventarios", response_model=Tabla_InventarioRead)
async def crear_inventario(
    info_inventario : Tabla_InventarioCreate,
    session : Session = Depends(get_session)
)->Tabla_InventarioRead:
    # Sucursal, Compra, Medicamento 
    sucursal = session.get(Sucursal, info_inventario.idSucursal)
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL INDICADA, NO ENCONTRADA")
    medicamento = session.get(Medicamento, info_inventario.idMedicamento)
    if not medicamento:
        raise HTTPException(status_code=404, detail="MEDICAMENTO INDICADO, NO ENCONTRADO")
    compra = session.get(Compra, info_inventario.idCompra)
    if not compra:
        raise HTTPException(status_code=404, detail="COMPRA INDICADA, NO ENCONTRADA")
    inventario = Tabla_Inventario.model_validate(info_inventario)
    session.add(inventario)
    session.commit()
    session.refresh(inventario)
    return inventario


@router.patch("/inventarios/{inventario_id}", response_model=Tabla_InventarioRead)
async def actualizar_inventario(
    inventario_id : Annotated[int, Path(title="ID del inventario")],
    inventario_info : Tabla_InventarioUpdate,
    session : Session = Depends(get_session)
) -> Tabla_InventarioRead:
    inventario = session.get(Tabla_Inventario, inventario_id)
    if not inventario:
        raise HTTPException(status_code=404, detail="INVENTARIO NO ENCONTRADO")
    datos = inventario_info.model_dump(exclude_unset=True)
    inventario.sqlmodel_update(datos)
    session.add(inventario)
    session.commit()
    session.refresh(inventario)
    return inventario


@router.delete("/inventarios/{inventario_id}")
async def eliminar_inventario(
    inventario_id : Annotated[int, Path(title="ID del inventario")],
    session: Session = Depends(get_session)
):
    inventario = session.get(Tabla_Inventario, inventario_id)
    if not inventario:
        raise HTTPException(status_code=404, detail="INVENTARIO NO ENCONTRADO")
    session.delete(inventario)
    session.commit()