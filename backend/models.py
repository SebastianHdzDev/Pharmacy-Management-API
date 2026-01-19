from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from sqlalchemy import CheckConstraint, Column, DECIMAL
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

class Sucursal(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint('num_sucursal > 0', name="chk_num_sucursal_mayorcero"),
        CheckConstraint("telefono ~ '^[0-9]{10}$'", name="chk_telefono_sucursal"),
    )
    idSucursal: Optional[int] = Field(default=None, primary_key=True)
    direccion: str = Field(max_length=150, nullable=False)
    telefono: str = Field(max_length=10, nullable=False)
    num_sucursal: int = Field(unique=True, gt=0, nullable=False)
    empleados: List["Usuario"] = Relationship(back_populates="sucursal_obj")
    lista_pedidos: List["Compra"] = Relationship(back_populates="sucursal_obj")
    lista_inventarios:List["Tabla_Inventario"]=Relationship(back_populates="sucursal_obj")

class RolEnum(str, Enum):
    CAJERO = "CAJERO"
    ADMIN = "ADMIN"

class Usuario(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint("rol IN ('CAJERO', 'ADMIN')", name="chk_rol_usuario"),
    )
    idUsuario: Optional[int] = Field(default=None, primary_key=True)
    alias: str = Field(unique=True, max_length=25, nullable=False)
    passwd: str = Field(max_length=100, nullable=False)
    estaActivo: bool = Field(default=True)
    idSucursal: int = Field(foreign_key="sucursal.idSucursal")
    rol: str = Field(default=RolEnum.CAJERO, max_length=10)
    sucursal_obj: Optional[Sucursal] = Relationship(back_populates="empleados")
    lista_asistencias: List["Asistencia"] = Relationship(back_populates="usuario_obj")

class Asistencia(SQLModel, table=True):
    idAsistencia: Optional[int] = Field(default=None, primary_key=True)
    horaLlegada: datetime = Field(default_factory=datetime.now, nullable=False)
    horaSalida: Optional[datetime] = Field(default=None)
    idUsuario: int = Field(foreign_key="usuario.idUsuario")
    usuario_obj:Optional["Usuario"] = Relationship(back_populates="lista_asistencias")

class Proveedor(SQLModel, table=True):
    __table_args__=(
        CheckConstraint("telefono ~ '^[0-9]{10}$'", name="chk_telefono_proveedor"),
    )
    idProveedor: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100, nullable=False)
    telefono: str = Field(max_length=10, nullable=False)
    correo: str = Field(max_length=50, nullable=False)
    lista_surtidos:List["Compra"]=Relationship(back_populates="proveedor_obj")

class Compra(SQLModel, table=True):
    idCompra: Optional[int] = Field(default=None, primary_key=True)
    monto: Decimal = Field(sa_column=Column(DECIMAL(10,2), nullable=False))
    fechaCompra: date = Field(default_factory=date.today, nullable=False)
    idProveedor: int = Field(foreign_key="proveedor.idProveedor") 
    idSucursal: int = Field(foreign_key="sucursal.idSucursal")
    sucursal_obj: Optional[Sucursal] = Relationship(back_populates="lista_pedidos")
    proveedor_obj:Optional[Proveedor] = Relationship(back_populates="lista_surtidos")
    lista_inventarios_surtidos: List["Tabla_Inventario"] = Relationship(back_populates="compra_obj")

class Medicamento(SQLModel, table=True):
    idMedicamento: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100, nullable=False)
    dosis: str = Field(max_length=10, nullable=False)
    viaAdministracion: str = Field(max_length=25, nullable=False)
    laboratorio: str = Field(max_length=50, nullable=False)
    tipoMedicamento: str = Field(max_length=50, nullable=False)
    usoTerapeutico: str = Field(max_length=255, nullable=False)
    requiereReceta: bool = Field(nullable=False)
    lista_lotes_inventario:List["Tabla_Inventario"]=Relationship(back_populates="medicamento_obj")

class Tabla_Inventario(SQLModel, table=True):
    __table_args__=(
        CheckConstraint('precio_venta > 0', name="chk_inv_precio_venta"),
        CheckConstraint('costo_individual > 0', name="chk_inv_costo"),
        CheckConstraint("cantidad >= 0", name="chk_inv_cantidad"),
    )
    idInventario: Optional[int] = Field(default=None, primary_key=True)
    lote: str = Field(max_length=20, nullable=False)
    fechaCaducidad: date = Field(nullable=False)
    precio_venta: Decimal = Field(sa_column=Column(DECIMAL(10,2), nullable=False))
    cantidad: int = Field(ge=0,nullable=False)
    costo_individual: Decimal = Field(sa_column=Column(DECIMAL(10,2), nullable=False))
    idSucursal: int = Field(foreign_key="sucursal.idSucursal")
    idCompra: int = Field(foreign_key="compra.idCompra") 
    idMedicamento: int = Field(foreign_key="medicamento.idMedicamento")
    sucursal_obj:Optional[Sucursal] = Relationship(back_populates="lista_inventarios")
    compra_obj: Optional[Compra] = Relationship(back_populates="lista_inventarios_surtidos")
    medicamento_obj: Optional[Medicamento] = Relationship(back_populates="lista_lotes_inventario")
    apariciones_detalles: List["Detalle_Venta"] = Relationship(back_populates="tabla_inventario_obj")

class TicketEnum (str, Enum):
    ACTIVO="ACTIVO"
    CANCELADO="CANCELADO"

class Ticket(SQLModel, table=True):
    __table_args__=(
        CheckConstraint("estatus IN ('ACTIVO', 'CANCELADO')", name="chk_estatus_ticket"),
    )
    idTicket: Optional[int] = Field(default=None, primary_key=True)
    total: Decimal = Field(sa_column=Column(DECIMAL(10,2), nullable=False))
    fecha: date = Field(default_factory=date.today, nullable=False)
    estatus: str = Field(default=TicketEnum.ACTIVO, max_length=10)
    cliente: Optional[str] = Field(default=None, max_length=50)
    idSucursal: int = Field(foreign_key="sucursal.idSucursal")
    lista_detalles_venta: List["Detalle_Venta"] = Relationship(back_populates="ticket_obj") 
    lista_facturas: List["Factura"] = Relationship(back_populates="ticket_obj") 

class Detalle_Venta(SQLModel, table=True):
    __table_args__=(
        CheckConstraint('precio_final > 0 ',name="chk_det_precio_final"),
        CheckConstraint("cantidad > 0",name="chk_det_cantidad"),
    )
    idDetalleVenta: Optional[int] = Field(default=None, primary_key=True)
    precio_final: Decimal = Field(sa_column=Column(DECIMAL(10,2), nullable=False), gt=0)
    cantidad: int = Field(gt=0, nullable=False)
    idInventario: int = Field(foreign_key="tabla_inventario.idInventario")
    idTicket: int = Field(foreign_key="ticket.idTicket")
    ticket_obj:Optional[Ticket] = Relationship(back_populates="lista_detalles_venta")
    tabla_inventario_obj:Optional[Tabla_Inventario] = Relationship(back_populates="apariciones_detalles")

class Factura(SQLModel, table=True): 
    __table_args__=(
        CheckConstraint("LENGTH(rfc) = 13",name="chk_rfc"),
    )
    idFactura: Optional[int] = Field(default=None, primary_key=True)
    rfc: str = Field(max_length=13, nullable=False)
    razonSocial: str = Field(max_length=150, nullable=False)
    selloDigital: str = Field(max_length=255, nullable=False)
    fechaTimbrado: date = Field(nullable=False)
    folioFiscal: str = Field(max_length=40, nullable=False)
    usoCFDI: str = Field(max_length=35, nullable=False)
    domicilioFiscal: str = Field(max_length=150, nullable=False)
    idTicket: int = Field(foreign_key="ticket.idTicket")
    ticket_obj:Optional[Ticket] = Relationship(back_populates="lista_facturas")