
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.auth import get_current_active_user
from backend.db import get_session
from backend.models import (
    Compra,
    Medicamento,
    Proveedor,
    Sucursal,
    Tabla_Inventario,
    Usuario,
)
from backend.schemas import (
    CompraCreate,
    CompraRead,
    SurtidoRequest,
    Tabla_InventarioCreate,
    Tabla_InventarioRead,
    Tabla_InventarioUpdate,
)

router = APIRouter(dependencies=[Depends(get_current_active_user)])

@router.get("", response_model=list[Tabla_InventarioRead])
async def obtener_inventarios(session : Session=Depends(get_session)) -> list[Tabla_InventarioRead]:
    statement = select(Tabla_Inventario)
    inventarios = session.exec(statement)
    return inventarios.all()


@router.post("", response_model=Tabla_InventarioRead)
async def crear_inventario(
    info_inventario : Tabla_InventarioCreate,
    current_user: Usuario = Depends(get_current_active_user),
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


@router.patch("/{inventario_id}/editar", response_model=Tabla_InventarioRead)
async def editar_inventario_existente(
    payload: Tabla_InventarioUpdate,
    inventario_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> Tabla_InventarioRead:
    statement = select(Tabla_Inventario).where(
        Tabla_Inventario.idInventario == inventario_id
    ).with_for_update()
    inventario = session.exec(statement).first()
    if not inventario:
        raise HTTPException(status_code=404, detail="Inventario no encontrado")
    if inventario.idSucursal != current_user.idSucursal:
        raise HTTPException(status_code=403, detail="No se puede editar inventarios de otra sucursal")
    if payload.costo_individual is not None:
        inventario.costo_individual = payload.costo_individual
        
    if payload.fechaCaducidad is not None:
        inventario.fechaCaducidad = payload.fechaCaducidad
        
    if payload.precio_venta is not None:
        inventario.precio_venta = payload.precio_venta
        
    if payload.lote is not None:
        inventario.lote = payload.lote
    session.add(inventario)
    session.commit()
    session.refresh(inventario)
    return inventario
