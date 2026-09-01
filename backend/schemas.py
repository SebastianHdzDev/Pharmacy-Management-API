from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


###############   SUCURSAL    ###############
class SucursalBase(SQLModel):
    direccion: str = Field(max_length=150)
    telefono: str = Field(max_length=10)
    num_sucursal: int = Field(gt=0)
    estaActivo: bool = Field(default=True)

class SucursalCreate(SucursalBase):
    pass

class SucursalRead(SucursalBase):
    idSucursal: int

class SucursalUpdate(SQLModel):
    direccion: str | None = None
    telefono: str | None = None
    num_sucursal: int | None = None
    estaActivo: bool | None = None

###############   USUARIO    ###############
class RolEnum(str, Enum):
    CAJERO = "CAJERO"
    ADMIN = "ADMIN"

class UsuarioBase(SQLModel):
    alias: str = Field(max_length=25)
    estaActivo: bool = Field(default=True)
    rol: RolEnum = Field(default=RolEnum.CAJERO, max_length=10)

class UsuarioCreate(UsuarioBase):
    passwd: str = Field(max_length=100)
    idSucursal: int

class UsuarioRead(UsuarioBase):
    idUsuario: int
    idSucursal: int #Retornar sucursal donde trabaja

class UsuarioUpdate(SQLModel):
    alias: str|None = None
    estaActivo: bool|None = None
    rol: RolEnum|None = None
    passwd: str|None = None

###############   ASISTENCIA    ###############
class AsistenciaBase(SQLModel):
    horaLlegada: datetime = Field(default_factory=datetime.now)
    horaSalida: datetime | None = Field(default=None)

class AsistenciaCreate(AsistenciaBase):
    idUsuario: int

class AsistenciaRead(AsistenciaBase):
    idAsistencia : int
    idUsuario: int #Ver que usuario registro la asistencia

class AsistenciaUpdate(SQLModel):
    horaSalida: datetime | None = None
    horaLlegada: datetime | None = None

###############   PROVEEDOR    ###############
class ProveedorBase(SQLModel):
    nombre: str = Field(max_length=100)
    telefono: str = Field(max_length=10)
    correo: str = Field(max_length=50)
    estaActivo: bool = Field(default=True)

class ProveedorCreate(ProveedorBase):
    pass

class ProveedorRead(ProveedorBase):
    idProveedor: int

class ProveedorUpdate(SQLModel):
    nombre: str | None = None
    telefono: str | None = None
    correo: str | None = None
    estaActivo: bool | None = None

###############   COMPRA    ###############
class CompraBase(SQLModel):
    monto: Decimal = Field(gt=0, decimal_places=2)
    fechaCompra: date = Field(default_factory=date.today)

class CompraCreate(CompraBase):
    idProveedor: int
    idSucursal: int 
    idUsuarioRegistro: int

class CompraRead(CompraBase):
    idCompra: int
    idProveedor: int
    idSucursal: int

class CompraUpdate(SQLModel):
    monto: Decimal|None = None
    fechaCompra: date|None = None

###############   MEDICAMENTO    ###############
class MedicamentoBase(SQLModel):
    nombre: str = Field(max_length=100)
    dosis: str = Field(max_length=10)
    viaAdministracion: str = Field(max_length=25)
    laboratorio: str = Field(max_length=50)
    tipoMedicamento: str = Field(max_length=50)
    usoTerapeutico: str = Field(max_length=255)
    requiereReceta: bool
    estaActivo: bool = Field(default = True)

class MedicamentoCreate(MedicamentoBase):
    pass

class MedicamentoRead(MedicamentoBase):
    idMedicamento: int

class MedicamentoUpdate(SQLModel):
    nombre: str|None = None
    dosis: str|None = None
    viaAdministracion: str|None = None
    laboratorio: str|None = None
    tipoMedicamento: str|None = None
    usoTerapeutico: str|None = None
    requiereReceta: bool|None = None
    estaActivo: bool|None = None

###############   TABLA_INVENTARIO    ###############
class Tabla_InventarioBase(SQLModel):
    lote: str = Field(max_length=20)
    fechaCaducidad: date 
    precio_venta: Decimal = Field(gt=0, decimal_places=2)
    cantidad: int = Field(ge=0)
    costo_individual: Decimal = Field(gt=0, decimal_places=2)

class Tabla_InventarioCreate(Tabla_InventarioBase):
    idSucursal: int
    idMedicamento: int
    idCompra: int

class Tabla_InventarioRead(Tabla_InventarioBase):
    idInventario: int
    idSucursal: int
    idMedicamento: int

class Tabla_InventarioUpdate(SQLModel):
    lote: str|None = None
    fechaCaducidad: date|None = None
    precio_venta: Decimal |None = None
    cantidad: int |None = None
    costo_individual: Decimal|None = None

###############   TICKET   ###############
class TicketEnum (str, Enum):
    ACTIVO="ACTIVO"
    CANCELADO="CANCELADO"

class MetodoPagoEnum(str, Enum):
    EFECTIVO = "EFECTIVO"
    TARJETA = "TARJETA"

class TicketBase(SQLModel):
    estatus: TicketEnum = Field(default=TicketEnum.ACTIVO, max_length=10)
    cliente: str | None = Field(default=None, max_length=50)
    metodo_pago: MetodoPagoEnum = Field(default=MetodoPagoEnum.EFECTIVO)

class TicketCreate(TicketBase):
    idSucursal: int #Sucursal que expide el ticket
    idUsuarioVendedor: int

class TicketRead(TicketBase):
    idTicket: int
    idSucursal: int
    total: Decimal
    fecha: date

class TicketUpdate(SQLModel):
    total: Decimal|None = None
    estatus: TicketEnum|None = None
    cliente: str|None = None

###############   DETALLE_VENTA    ###############
class Detalle_VentaBase(SQLModel):
    cantidad: int = Field(gt=0)

class Detalle_VentaCreate(Detalle_VentaBase):
    idInventario: int
    idTicket: int

class Detalle_VentaRead(Detalle_VentaBase):
    idDetalleVenta: int

class Detalle_VentaUpdate(SQLModel):
    cantidad: int|None = None

###############   FACTURA    ###############
class FacturaEnum(str, Enum):
    ACTIVA = "ACTIVA"
    CANCELADA = "CANCELADA"

class FacturaBase(SQLModel):
    rfc: str = Field(max_length=13)
    razonSocial: str = Field(max_length=150)
    selloDigital: str = Field(max_length=255)
    fechaTimbrado: date
    folioFiscal: str = Field(max_length=40)
    usoCFDI: str = Field(max_length=35)
    domicilioFiscal: str = Field(max_length=150)
    estatus: FacturaEnum = Field(default=FacturaEnum.ACTIVA, max_length=10)

class FacturaCreate(FacturaBase):
    idTicket: int

class FacturaRead(FacturaBase):
    idFactura: int
    idTicket: int

class FacturaUpdate(SQLModel):
    rfc: str | None = None
    razonSocial: str | None = None
    selloDigital: str | None = None
    fechaTimbrado: date | None = None
    folioFiscal: str | None = None
    usoCFDI: str | None = None
    domicilioFiscal: str | None = None
    estatus: FacturaEnum | None = None

###############   VENTAS    ###############
# Paquete individual de un medicamento
class ItemCarrito(SQLModel):
    idInventario: int
    cantidad: int
    precio_final: Decimal

# Paquete completo que manda el frontend
class VentaRequest(SQLModel):
    cliente: str | None = None
    carrito: list[ItemCarrito]
    metodo_pago: MetodoPagoEnum

###############   SURTIDOS    ###############
# Usado para crear inventario y referencia a medicamento
class ItemSurtido(BaseModel):
    idMedicamento: int
    lote: str
    fechaCaducidad: date
    precio_venta: Decimal
    cantidad: int
    costo_individual: Decimal

# Usado para tener un 'ticket' de lo que se surtio
class SurtidoRequest(BaseModel):
    idProveedor: int
    montoTotal: Decimal
    productos: list[ItemSurtido]

###############   MERMAS    ###############
class MermaEnum(str, Enum):
    DANIO = "DAÑO"
    CADUCIDAD = "CADUCIDAD"
    ROBO = "ROBO"
    ERROR_CONTEO = "ERROR DE CONTEO"
    OTRO = "OTRO"

class MermaBase(SQLModel):
    cantidad: int
    motivo: MermaEnum = Field(max_length=15)
    descripcion: str | None = Field(max_length=255, default=None)

class MermaRead(MermaBase):
    idMerma: int
    idInventario: int
    idUsuario: int
    idSucursal: int
    fecha: date

class MermaCreate(MermaBase):
    idInventario : int

###############   PAGINACIONES    ###############
class PaginacionMedicamentos(BaseModel):
    total: int
    items: list[MedicamentoRead]

class PaginacionAsistencias(BaseModel):
    total: int
    items: list[AsistenciaRead]

class PaginacionCompras(BaseModel):
    total: int
    items: list[CompraRead]

class PaginacionFacturas(BaseModel):
    total: int
    items: list[FacturaRead]

class PaginacionInventarios(BaseModel):
    total: int
    items: list[Tabla_InventarioRead]

class PaginacionMermas(BaseModel):
    total: int
    items: list[MermaRead]

class PaginacionProveedores(BaseModel):
    total: int
    items: list[ProveedorRead]

class PaginacionSucursales(BaseModel):
    total: int
    items: list[SucursalRead]

class PaginacionTickets(BaseModel):
    total: int
    items: list[TicketRead]

class PaginacionDetallesVenta(BaseModel):
    total: int
    items: list[Detalle_VentaRead]

class PaginacionUsuarios(BaseModel):
    total: int
    items: list[UsuarioRead]

