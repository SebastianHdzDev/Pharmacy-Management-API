from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import func
from sqlmodel import Session, select

from backend.auth import get_current_active_user, verify_admin
from backend.db import get_session
from backend.dependencies import paginacion_comun
from backend.models import Medicamento, Usuario
from backend.schemas import MedicamentoCreate, MedicamentoRead, MedicamentoUpdate, PaginacionMedicamentos

router = APIRouter(dependencies=[Depends(get_current_active_user)])

@router.post("", response_model=MedicamentoRead)
async def crear_medicamento(
    info_medicamento: MedicamentoCreate,
    current_user: Usuario = Depends(verify_admin),
    session: Session = Depends(get_session)
) -> MedicamentoRead:
    medicamento = Medicamento.model_validate(info_medicamento)
    session.add(medicamento)
    session.commit()
    session.refresh(medicamento)
    return medicamento


@router.get("/", response_model=PaginacionMedicamentos)
async def obtener_medicamentos(
    nombre: str | None,
    dosis: str | None,
    viaAdministracion: str | None,
    laboratorio: str | None,
    tipoMedicamento: str | None,
    usoTerapeutico: str | None,
    requiereReceta: bool | None,
    paginacion: dict = Depends(paginacion_comun),
    current_user: Usuario = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> PaginacionMedicamentos:
    statement = select(Medicamento).where(Medicamento.estaActivo)

    if nombre:
        statement = statement.where(Medicamento.nombre.ilike(f"%{nombre}%"))
    
    if dosis:
        statement = statement.where(Medicamento.dosis.ilike(f"%{dosis}%"))
    
    if viaAdministracion:
        statement = statement.where(Medicamento.viaAdministracion.ilike(f"%{viaAdministracion}%"))

    if laboratorio:
        statement = statement.where(Medicamento.laboratorio.ilike(f"%{laboratorio}%"))

    if tipoMedicamento:
        statement = statement.where(Medicamento.tipoMedicamento.ilike(f"%{tipoMedicamento}%"))

    if usoTerapeutico:
        statement = statement.where(Medicamento.usoTerapeutico.ilike(f"%{usoTerapeutico}%"))

    if requiereReceta is not None:
        statement = statement.where(Medicamento.requiereReceta == requiereReceta)

    count_statement = statement.with_only_columns(func.count())
    total_records = session.exec(count_statement).one()

    # ejecuta la consulta con todos los where indicados y dependiendo de parametros
    statement = statement.offset(paginacion["skip"]).limit(paginacion["limit"])
    resultados = session.exec(statement).all()
    
    return {"total": total_records, "items": resultados}


@router.get("/{medicamento_id}", response_model=MedicamentoRead)
async def obtener_medicamento_por_id(
    medicamento_id: Annotated[int, Path(title="ID del medicamento")],
    current_user: Usuario = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> MedicamentoRead:
    medicamento = session.get(Medicamento, medicamento_id)
    if not medicamento:
        raise HTTPException(status_code=404, detail="MEDICAMENTO NO ENCONTRADO")
    return medicamento


@router.patch("/{medicamento_id}", response_model=MedicamentoRead)
async def actualizar_medicamento(
    medicamento_id: Annotated[int, Path(title="ID del medicamento")],
    medicamento_info: MedicamentoUpdate,
    current_user: Usuario = Depends(verify_admin),
    session: Session = Depends(get_session)
) -> MedicamentoRead:
    medicamento = session.get(Medicamento, medicamento_id)
    if not medicamento:
        raise HTTPException(status_code=404, detail="MEDICAMENTO NO ENCONTRADO")
    datos = medicamento_info.model_dump(exclude_unset=True)
    medicamento.sqlmodel_update(datos)
    session.add(medicamento)
    session.commit()
    session.refresh(medicamento)
    return medicamento


@router.delete("/{medicamento_id}", response_model=MedicamentoRead)
async def eliminar_medicamento(
    medicamento_id: Annotated[int, Path(title="ID del medicamento")],
    current_user: Usuario = Depends(verify_admin),
    session: Session = Depends(get_session)
) -> MedicamentoRead:
    medicamento = session.get(Medicamento, medicamento_id)
    if not medicamento:
        raise HTTPException(status_code=404, detail="MEDICAMENTO NO ENCONTRADO")
    if not medicamento.estaActivo:
        raise HTTPException(status_code=400, detail="EL MEDICAMENTO YA FUE DADO DE BAJA")
    medicamento.estaActivo = False
    session.add(medicamento)
    session.commit()



