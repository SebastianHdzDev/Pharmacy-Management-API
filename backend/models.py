from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from sqlalchemy import CheckConstraint
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

class Sucursal(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint("numSucursal > 0", name="chk_numSucursal_mayorcero"),
        CheckConstraint("telefono ~ '^[0-9]{10}$'", name="chk_telefono_sucursal"),
    )
    idSucursal: Optional[int] = Field(default=None, primary_key=True)
    direccion: str = Field(max_length=150, nullable=False)
    telefono: str = Field(max_length=10, nullable=False)
    numSucursal: int = Field(unique=True, nullable=False)

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

class Asistencia(SQLModel, table=True):
    idAsistencia: Optional[int] = Field(default=None, primary_key=True)
    horaLlegada: datetime = Field(default_factory=datetime.now, nullable=False)
    horaSalida: Optional[datetime] = Field(default=None)
    idUsuario: int

class Proveedor(SQLModel, table=True):
    idProveedor: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    telefono: str 
    correo: str 

class Compra(SQLModel, table=True):
    idCompra: int = Field(primary_key=True)
    monto: float
    fechaCompra: date
    idProveedor: int
    idSucursal: int

class Medicamento(SQLModel, table=True):
    idMedicamento: int = Field(primary_key=True)
    nombre: str
    dosis: str
    viaAdministracion: str
    laboratorio: str
    tipoMedicamento: str
    usoTerapeutico: str
    requiereReceta: bool

class Tabla_Inventario(SQLModel, table=True):
    idInventario: int = Field(primary_key=True)
    lote: str
    fechaCaducidad: date
    precioVenta: float
    cantidad: int
    costoIndividual: float
    idSucursal: int
    idCompra: int
    idMedicamento: int

class Ticket(SQLModel, table=True):
    idTicket: int = Field(primary_key=True)
    total: float
    fecha: date
    estatus: str = 'ACTIVO' | 'CANCELADO'
    cliente: str | None = None
    idSucursal: int

class Detalle_Venta(SQLModel, table=True):
    idDetalleVenta: int = Field(primary_key=True)
    precioFinal=float
    cantidad: int
    idInventario: int
    idTicket: int

class Factura(SQLModel, table=True): 
    idFactura: int = Field(primary_key=True)
    rfc: str
    razonSocial: str
    selloDigital: str
    fechaTimbrado: date
    folioFiscal: str
    usoCFDI: str
    domicilioFiscal: str
    idTicket: int