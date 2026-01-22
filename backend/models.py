from sqlmodel import Field, Relationship
from typing import Optional, List
from sqlalchemy import CheckConstraint, Column, DECIMAL, text, Boolean, Enum as SAEnum
from datetime import date, datetime
from decimal import Decimal
from schemas import *

class Sucursal(SucursalBase, table=True):
    __table_args__ = (
        CheckConstraint('num_sucursal > 0', name="chk_num_sucursal_mayorcero"),
        CheckConstraint("telefono ~ '^[0-9]{10}$'", name="chk_telefono_sucursal"),
    )
    idSucursal: Optional[int] = Field(default=None, primary_key=True)
    num_sucursal: int = Field(unique=True, gt=0)
    empleados: List["Usuario"] = Relationship(back_populates="sucursal_obj")
    lista_pedidos: List["Compra"] = Relationship(back_populates="sucursal_obj")
    lista_inventarios:List["Tabla_Inventario"]=Relationship(back_populates="sucursal_obj")

class Usuario(UsuarioBase, table=True):
    __table_args__ = (
        CheckConstraint("rol IN ('CAJERO', 'ADMIN')", name="chk_rol_usuario"),
    )
    idUsuario: Optional[int] = Field(default=None, primary_key=True)
    alias: str = Field(unique=True, nullable=False, max_length=25)
    passwd: str = Field(nullable=False, max_length=100)
    estaActivo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text("true")) )
    rol: RolEnum = Field(default=RolEnum.CAJERO, sa_column=Column(SAEnum(RolEnum), nullable=False, server_default=text("'CAJERO'")) )
    idSucursal: int = Field(foreign_key="sucursal.idSucursal")
    sucursal_obj: Optional[Sucursal] = Relationship(back_populates="empleados")
    lista_asistencias: List["Asistencia"] = Relationship(back_populates="usuario_obj")

class Asistencia(AsistenciaBase, table=True):
    idAsistencia: Optional[int] = Field(default=None, primary_key=True)
    horaLlegada: datetime = Field(nullable=False)
    idUsuario: int = Field(foreign_key="usuario.idUsuario")
    usuario_obj:Optional["Usuario"] = Relationship(back_populates="lista_asistencias")

class Proveedor(ProveedorBase, table=True):
    __table_args__=(
        CheckConstraint("telefono ~ '^[0-9]{10}$'", name="chk_telefono_proveedor"),
    )
    idProveedor: Optional[int] = Field(default=None, primary_key=True)
    lista_surtidos:List["Compra"]=Relationship(back_populates="proveedor_obj")

class Compra(CompraBase, table=True):
    __table_args__=(
        CheckConstraint("monto > 0", name="chk_monto"),
    )
    idCompra: Optional[int] = Field(default=None, primary_key=True)
    monto: Decimal = Field(sa_column=Column(DECIMAL(10,2), nullable=False))
    idProveedor: int = Field(foreign_key="proveedor.idProveedor") 
    idSucursal: int = Field(foreign_key="sucursal.idSucursal")
    sucursal_obj: Optional[Sucursal] = Relationship(back_populates="lista_pedidos")
    proveedor_obj:Optional[Proveedor] = Relationship(back_populates="lista_surtidos")
    lista_inventarios_surtidos: List["Tabla_Inventario"] = Relationship(back_populates="compra_obj")

class Medicamento(MedicamentoBase, table=True):
    idMedicamento: Optional[int] = Field(default=None, primary_key=True)
    lista_lotes_inventario:List["Tabla_Inventario"]=Relationship(back_populates="medicamento_obj")

class Tabla_Inventario(Tabla_InventarioBase, table=True):
    __table_args__=(
        CheckConstraint('precio_venta > 0', name="chk_inv_precio_venta"),
        CheckConstraint('costo_individual > 0', name="chk_inv_costo"),
        CheckConstraint("cantidad >= 0", name="chk_inv_cantidad"),
    )
    idInventario: Optional[int] = Field(default=None, primary_key=True)
    precio_venta: Decimal = Field(sa_column=Column(DECIMAL(10,2), nullable=False))
    costo_individual: Decimal = Field(sa_column=Column(DECIMAL(10,2), nullable=False))
    idSucursal: int = Field(foreign_key="sucursal.idSucursal")
    idCompra: int = Field(foreign_key="compra.idCompra") 
    idMedicamento: int = Field(foreign_key="medicamento.idMedicamento")
    sucursal_obj:Optional[Sucursal] = Relationship(back_populates="lista_inventarios")
    compra_obj: Optional[Compra] = Relationship(back_populates="lista_inventarios_surtidos")
    medicamento_obj: Optional[Medicamento] = Relationship(back_populates="lista_lotes_inventario")
    apariciones_detalles: List["Detalle_Venta"] = Relationship(back_populates="tabla_inventario_obj")

class Ticket(TicketBase, table=True):
    __table_args__=(
        CheckConstraint("estatus IN ('ACTIVO', 'CANCELADO')", name="chk_estatus_ticket"),
    )
    idTicket: Optional[int] = Field(default=None, primary_key=True)
    total: Decimal = Field(default=0, sa_column=Column(DECIMAL(10,2), nullable=False, server_default=text("0")) )
    fecha: date = Field(default_factory=date.today, nullable=False)
    estatus: TicketEnum = Field(max_length=10, sa_column=Column(SAEnum(TicketEnum), nullable=False, server_default=text("'ACTIVO'")))
    idSucursal: int = Field(foreign_key="sucursal.idSucursal")
    lista_detalles_venta: List["Detalle_Venta"] = Relationship(back_populates="ticket_obj") 
    lista_facturas: List["Factura"] = Relationship(back_populates="ticket_obj") 

class Detalle_Venta(Detalle_VentaBase, table=True):
    __table_args__=(
        CheckConstraint('precio_final > 0 ',name="chk_det_precio_final"),
        CheckConstraint("cantidad > 0",name="chk_det_cantidad"),
    )
    idDetalleVenta: Optional[int] = Field(default=None, primary_key=True)
    precio_final: Decimal = Field(sa_column=Column(DECIMAL(10,2), nullable=False), gt=0)
    idInventario: int = Field(foreign_key="tabla_inventario.idInventario")
    idTicket: int = Field(foreign_key="ticket.idTicket")
    ticket_obj:Optional[Ticket] = Relationship(back_populates="lista_detalles_venta")
    tabla_inventario_obj:Optional[Tabla_Inventario] = Relationship(back_populates="apariciones_detalles")

class Factura(FacturaBase, table=True): 
    __table_args__=(
        CheckConstraint("LENGTH(rfc) = 13",name="chk_rfc"),
    )
    idFactura: Optional[int] = Field(default=None, primary_key=True)
    idTicket: int = Field(foreign_key="ticket.idTicket")
    ticket_obj:Optional[Ticket] = Relationship(back_populates="lista_facturas")