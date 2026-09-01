from fastapi import Query


def paginacion_comun(
    skip: int = Query(0, ge=0, description="Numero de registros a omitir"),
    limit: int = Query(20, ge=1, le=100, description="Limite de registros a retornar")
) -> dict[str, int]:
    return {"skip": skip, "limit": limit}