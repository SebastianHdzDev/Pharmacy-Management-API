from fastapi import APIRouter, HTTPException, Path, Depends
from sqlmodel import Session, select
from typing import Annotated, List
from backend.db import get_session
from backend.models import Compra, Sucursal, Medicamento, Tabla_Inventario, Usuario, Proveedor
from backend.schemas import * 
from backend.auth import get_current_active_user

router = APIRouter(dependencies=[Depends(get_current_active_user)])

@router.get("", response_model=List[Tabla_InventarioRead])
async def obtener_inventarios(session : Session=Depends(get_session)) -> List[Tabla_InventarioRead]:
    statement = select(Tabla_Inventario)
    inventarios = session.exec(statement)
    return inventarios.all()


@router.post("", response_model=Tabla_InventarioRead)
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


@router.patch("/{inventario_id}", response_model=Tabla_InventarioRead)
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


@router.delete("/{inventario_id}")
async def eliminar_inventario(
    inventario_id : Annotated[int, Path(title="ID del inventario")],
    session: Session = Depends(get_session)
):
    inventario = session.get(Tabla_Inventario, inventario_id)
    if not inventario:
        raise HTTPException(status_code=404, detail="INVENTARIO NO ENCONTRADO")
    session.delete(inventario)
    session.commit()


@router.post("/surtidos", response_model=CompraRead)
async def surtir_inventarios(
    payload: SurtidoRequest,
    current_user: Usuario = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> CompraRead:
    
    sucursal = session.get(Sucursal, current_user.idSucursal)
    if not sucursal:
        raise HTTPException(status_code=404, detail="SUCURSAL INDICADA, NO ENCONTRADA")
    
    proveedor = session.get(Proveedor, payload.idProveedor)
    if not proveedor:
        raise HTTPException(status_code=404, detail="PROVEEDOR NO ENCONTRADO")
    
    # Generar la compra temporalmente a la cual asociar los inventarios
    compra_info = CompraCreate(
        monto=payload.montoTotal, 
        idProveedor=payload.idProveedor,
        idSucursal=current_user.idSucursal
    )

    compra = Compra.model_validate(compra_info)
    session.add(compra)
    session.flush()

    # Explorar la lista de productos y crear inventarios
    for item in payload.productos:
        medicamento = session.get(Medicamento, item.idMedicamento)
        if not medicamento:
            raise HTTPException(status_code=404, detail=f"MEDICAMENTO ID {item.idMedicamento} NO ENCONTRADO")
        
        # Generar el inventario con el la informacion de cada producto o medicamento
        inventario_info = Tabla_InventarioCreate(
            lote=item.lote,
            fechaCaducidad=item.fechaCaducidad,
            precio_venta=item.precio_venta,
            cantidad=item.cantidad,
            costo_individual=item.costo_individual,
            idSucursal=current_user.idSucursal,
            idMedicamento=item.idMedicamento,
            idCompra=compra.idCompra # <--- Asociar todos los inventarios a la misma compra
        )

        inventario = Tabla_Inventario.model_validate(inventario_info)
        
        # Almacenar en DB temporalmente
        session.add(inventario)
    
    # Una vez finalizados almacenar definitivamente
    session.commit()
    session.refresh(compra)
    return compra
