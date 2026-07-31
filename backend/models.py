from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DECIMAL, Boolean, CheckConstraint, Column, text
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, Relationship

from backend.schemas import (
    AsistenciaBase,
    CompraBase,
    Detalle_VentaBase,
    FacturaBase,
    FacturaEnum,
    MedicamentoBase,
    ProveedorBase,
    RolEnum,
    SucursalBase,
    Tabla_InventarioBase,
    TicketBase,
    TicketEnum,
    UsuarioBase,
)


class Sucursal(SucursalBase, table=True):
    __table_args__ = (
        CheckConstraint('num_sucursal > 0', name="chk_num_sucursal_mayorcero"),
        CheckConstraint("telefono ~ '^[0-9]{10}$'", name="chk_telefono_sucursal"),
    )
    idSucursal: int | None = Field(default=None, primary_key=True)
    num_sucursal: int = Field(unique=True, gt=0)
    estaActivo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text("true")))
    empleados: list["Usuario"] = Relationship(back_populates="sucursal_obj")
    lista_pedidos: list["Compra"] = Relationship(back_populates="sucursal_obj")
    lista_inventarios: list["Tabla_Inventario"] = Relationship(back_populates="sucursal_obj")

class Usuario(UsuarioBase, table=True):
    __table_args__ = (
        CheckConstraint("rol IN ('CAJERO', 'ADMIN')", name="chk_rol_usuario"),
    )
    idUsuario: int | None = Field(default=None, primary_key=True)
    alias: str = Field(unique=True, nullable=False, max_length=25)
    passwd: str = Field(nullable=False, max_length=100)
    estaActivo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text("true")) )
    rol: RolEnum = Field(default=RolEnum.CAJERO, sa_column=Column(SAEnum(RolEnum), nullable=False, 
                                                                  server_default=text("'CAJERO'")) )
    idSucursal: int = Field(foreign_key="sucursal.idSucursal")
    sucursal_obj: Sucursal | None = Relationship(back_populates="empleados")
    lista_asistencias: list["Asistencia"] = Relationship(back_populates="usuario_obj")

class Asistencia(AsistenciaBase, table=True):
    idAsistencia: int | None = Field(default=None, primary_key=True)
    horaLlegada: datetime = Field(nullable=False)
    idUsuario: int = Field(foreign_key="usuario.idUsuario")
    usuario_obj:Optional["Usuario"] = Relationship(back_populates="lista_asistencias")

class Proveedor(ProveedorBase, table=True):
    __table_args__=(
        CheckConstraint("telefono ~ '^[0-9]{10}$'", name="chk_telefono_proveedor"),
    )
    idProveedor: int | None = Field(default=None, primary_key=True)
    estaActivo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text("true")))
    lista_surtidos: list["Compra"] = Relationship(back_populates="proveedor_obj")

class Compra(CompraBase, table=True):
    __table_args__=(
        CheckConstraint("monto > 0", name="chk_monto"),
    )
    idCompra: int | None = Field(default=None, primary_key=True)
    monto: Decimal = Field(sa_column=Column(DECIMAL(10,2), nullable=False))
    idProveedor: int = Field(foreign_key="proveedor.idProveedor") 
    idSucursal: int = Field(foreign_key="sucursal.idSucursal")
    sucursal_obj: Sucursal | None = Relationship(back_populates="lista_pedidos")
    proveedor_obj:Proveedor | None = Relationship(back_populates="lista_surtidos")
    lista_inventarios_surtidos: list["Tabla_Inventario"] = Relationship(back_populates="compra_obj")

class Medicamento(MedicamentoBase, table=True):
    idMedicamento: int | None = Field(default=None, primary_key=True)
    estaActivo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text("true")) )
    lista_lotes_inventario:list["Tabla_Inventario"]=Relationship(back_populates="medicamento_obj")

class Tabla_Inventario(Tabla_InventarioBase, table=True):
    __table_args__=(
        CheckConstraint('precio_venta > 0', name="chk_inv_precio_venta"),
        CheckConstraint('costo_individual > 0', name="chk_inv_costo"),
        CheckConstraint("cantidad >= 0", name="chk_inv_cantidad"),
    )
    idInventario: int | None = Field(default=None, primary_key=True)
    precio_venta: Decimal = Field(sa_column=Column(DECIMAL(10,2), nullable=False))
    costo_individual: Decimal = Field(sa_column=Column(DECIMAL(10,2), nullable=False))
    idSucursal: int = Field(foreign_key="sucursal.idSucursal")
    idCompra: int = Field(foreign_key="compra.idCompra") 
    idMedicamento: int = Field(foreign_key="medicamento.idMedicamento")
    sucursal_obj:Sucursal | None = Relationship(back_populates="lista_inventarios")
    compra_obj: Compra | None = Relationship(back_populates="lista_inventarios_surtidos")
    medicamento_obj: Medicamento | None = Relationship(back_populates="lista_lotes_inventario")
    apariciones_detalles: list["Detalle_Venta"] = Relationship(back_populates="tabla_inventario_obj")

class Ticket(TicketBase, table=True):
    __table_args__=(
        CheckConstraint("estatus IN ('ACTIVO', 'CANCELADO')", name="chk_estatus_ticket"),
    )
    idTicket: int | None = Field(default=None, primary_key=True)
    total: Decimal = Field(default=0, sa_column=Column(DECIMAL(10,2), nullable=False, server_default=text("0")) )
    fecha: date = Field(default_factory=date.today, nullable=False)
    estatus: TicketEnum = Field(max_length=10, sa_column=Column(SAEnum(TicketEnum), nullable=False, 
                                                                server_default=text("'ACTIVO'")))
    idSucursal: int = Field(foreign_key="sucursal.idSucursal")
    lista_detalles_venta: list["Detalle_Venta"] = Relationship(back_populates="ticket_obj") 
    lista_facturas: list["Factura"] = Relationship(back_populates="ticket_obj") 

class Detalle_Venta(Detalle_VentaBase, table=True):
    __table_args__=(
        CheckConstraint('precio_final > 0 ',name="chk_det_precio_final"),
        CheckConstraint("cantidad > 0",name="chk_det_cantidad"),
    )
    idDetalleVenta: int | None = Field(default=None, primary_key=True)
    precio_final: Decimal = Field(sa_column=Column(DECIMAL(10,2), nullable=False), gt=0)
    idInventario: int = Field(foreign_key="tabla_inventario.idInventario")
    idTicket: int = Field(foreign_key="ticket.idTicket")
    ticket_obj:Ticket | None = Relationship(back_populates="lista_detalles_venta")
    tabla_inventario_obj:Tabla_Inventario | None = Relationship(back_populates="apariciones_detalles")

class Factura(FacturaBase, table=True):
    __table_args__=(
        CheckConstraint("LENGTH(rfc) = 13", name="chk_rfc"),
        CheckConstraint("estatus IN ('ACTIVA', 'CANCELADA')", name="chk_estatus_factura"),
    )
    idFactura: int | None = Field(default=None, primary_key=True)
    estatus: FacturaEnum = Field(
        max_length=10,
        sa_column=Column(SAEnum(FacturaEnum), nullable=False, server_default=text("'ACTIVA'"))
    )
    idTicket: int = Field(foreign_key="ticket.idTicket", unique=True)
    ticket_obj: Ticket | None = Relationship(back_populates="lista_facturas")