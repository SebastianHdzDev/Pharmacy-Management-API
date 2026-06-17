from fastapi import APIRouter, HTTPException, Path, Depends
from sqlmodel import Session, select, or_  
from typing import Annotated, List
from backend.db import get_session
from backend.models import Medicamento
from backend.schemas import * 
from backend.auth import get_current_active_user

router = APIRouter(dependencies=[Depends(get_current_active_user)])

@router.post("/medicamentos", response_model=MedicamentoRead)
async def crear_medicamento(
    info_medicamento : MedicamentoCreate,
    session : Session = Depends(get_session)
) -> MedicamentoRead:
    medicamento = Medicamento.model_validate(info_medicamento)
    session.add(medicamento)
    session.commit()
    session.refresh(medicamento)
    return medicamento


@router.get("/medicamentos", response_model=List[MedicamentoRead])
async def obtener_medicamentos(
    session : Session = Depends(get_session)
) -> List[MedicamentoRead]:
    statement = select(Medicamento)
    resultados = session.exec(statement)
    return resultados.all()


@router.get("/medicamentos/{medicamento_id}", response_model=MedicamentoRead)
async def obtener_medicamentos(
    medicamento_id : Annotated[int, Path(title="ID del medicamento")],
    session : Session = Depends(get_session)
) -> MedicamentoRead:
    medicamento = session.get(Medicamento, medicamento_id)
    if not medicamento:
        raise HTTPException(status_code=404, detail="MEDICAMENTO NO ENCONTRADO")
    return medicamento

@router.patch("/medicamentos/{medicamento_id}", response_model=MedicamentoRead)
async def actualizar_medicamento(
    medicamento_id : Annotated[int, Path(title="ID del medicamento")],
    medicamento_info : MedicamentoUpdate,
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


@router.delete("/medicamentos/{medicamento_id}", response_model=MedicamentoRead)
async def eliminar_medicamento(
    medicamento_id : Annotated[int, Path(title="ID del medicamento")],
    session: Session = Depends(get_session)
) -> MedicamentoRead:
    medicamento = session.get(Medicamento, medicamento_id)
    if not medicamento:
        raise HTTPException(status_code=404, detail="MEDICAMENTO NO ENCONTRADO")
    session.delete(medicamento)
    session.commit()


@router.get("/", response_model=List[MedicamentoRead])
async def buscar_medicamentos(
    nombre: Optional[str],
    dosis: Optional[str],
    viaAdministracion: Optional[str],
    laboratorio: Optional[str],
    tipoMedicamento: Optional[str],
    usoTerapeutico: Optional[str],
    requiereReceta: Optional[bool],
    session: Session = Depends(get_session)
) -> List[MedicamentoRead]:
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