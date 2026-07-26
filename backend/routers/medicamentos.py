from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlmodel import Session, select

from backend.auth import get_current_active_user, verify_admin
from backend.db import get_session
from backend.models import Medicamento, Usuario
from backend.schemas import MedicamentoCreate, MedicamentoRead, MedicamentoUpdate

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


@router.get("", response_model=list[MedicamentoRead])
async def obtener_medicamentos(
    current_user: Usuario = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> list[MedicamentoRead]:
    statement = select(Medicamento)
    resultados = session.exec(statement)
    return resultados.all()


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
    session.delete(medicamento)
    session.commit()


@router.get("/", response_model=list[MedicamentoRead])
async def buscar_medicamentos(
    nombre: str | None,
    dosis: str | None,
    viaAdministracion: str | None,
    laboratorio: str | None,
    tipoMedicamento: str | None,
    usoTerapeutico: str | None,
    requiereReceta: bool | None,
    current_user: Usuario = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> list[MedicamentoRead]:
    statement = select(Medicamento)

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

    # ejecuta la consulta con todos los where indicados y dependiendo de parametros
    resultados = session.exec(statement)
    
    return resultados.all()
