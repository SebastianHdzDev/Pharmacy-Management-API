from fastapi import APIRouter, HTTPException, Path, Depends
from sqlmodel import Session, select
from typing import Annotated, List

from backend.db import get_session
from backend.models import Medicamento
from backend.schemas import * 

router = APIRouter()

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