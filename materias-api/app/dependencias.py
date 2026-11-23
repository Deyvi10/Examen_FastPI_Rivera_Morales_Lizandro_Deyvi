"""Dependencia reutilizable: busca el plan y resuelve el 404.

"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status

from app.datos import PLANES


def obtener_plan(
    codigo: str = Path(
        description="Código del plan (3 letras mayúsculas + 3 dígitos). Acepta minúsculas."
    ),
) -> dict:
    codigo_normalizado = codigo.upper()
    for plan in PLANES:
        if plan["codigo"] == codigo_normalizado:
            return plan
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No existe el plan con código {codigo_normalizado}",
    )



PlanExistente = Annotated[dict, Depends(obtener_plan)]
