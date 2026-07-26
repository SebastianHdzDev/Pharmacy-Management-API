from asistencias import router as asistencias_router
from compras import router as compras_router
from detalles_venta import router as detalles_venta_router
from facturas import router as facturas_router
from fastapi import APIRouter
from inventarios import router as inventarios_router
from medicamentos import router as medicamentos_router
from proveedores import router as proveedores_router
from sucursales import router as sucursales_router
from tickets import router as tickets_router
from usuarios import router as usuarios_router
from ventas import router as ventas_router

from auth import router as auth_router

router = APIRouter()

router.include_router(auth_router, tags=["Autenticacion"])

router.include_router(sucursales_router, prefix="/sucursales", tags=["Sucursales"])

router.include_router(usuarios_router, prefix="/usuarios", tags=["Usuarios"])

router.include_router(asistencias_router, prefix="/asistencias", tags=["Asistencias"])

router.include_router(medicamentos_router, prefix="/medicamentos", tags=["Medicamentos"])

router.include_router(proveedores_router, prefix="/proveedores", tags=["Proveedores"])

router.include_router(compras_router, prefix="/compras", tags=["Compras"])

router.include_router(inventarios_router, prefix="/inventarios", tags=["Inventarios"])

router.include_router(detalles_venta_router, prefix="/detalles-venta", tags=["Detalles de Venta"])

router.include_router(tickets_router, prefix="/tickets", tags=["Tickets"])

router.include_router(facturas_router, prefix="/facturas", tags=["Facturas"])

router.include_router(ventas_router, prefix="/ventas", tags=["Ventas"])
