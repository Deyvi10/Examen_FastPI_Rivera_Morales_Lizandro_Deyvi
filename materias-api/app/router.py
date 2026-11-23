"""Rutas del recurso plan de membresia (pregunta 1).
"""

from fastapi import APIRouter, HTTPException, Query, Response, status

from app.datos import PLANES
from app.dependencias import PlanExistente
from app.esquemas import PlanActualizar, PlanCrear, PlanSalida

router = APIRouter(prefix="/membresias", tags=["Planes de membresía"])


# ---------------------------------------------------------------------------
# Rutas literales
# ---------------------------------------------------------------------------


@router.get("/planes", response_model=list[PlanSalida], status_code=status.HTTP_200_OK)
def listar_planes(
    nivel: int | None = Query(default=None, ge=1, le=5, description="Filtra por nivel (1 a 5)"),
    solo_con_entrenador: bool = Query(
        default=False, description="Si es true, devuelve solo planes con entrenador"
    ),
) -> list[dict]:
    planes_filtrados: list[dict] = []
    for plan in PLANES:
        if nivel is not None and plan["nivel"] != nivel:
            continue
        if solo_con_entrenador and not plan["incluye_entrenador"]:
            continue
        planes_filtrados.append(plan)
    return planes_filtrados

@router.post("/planes", response_model=PlanSalida, status_code=status.HTTP_201_CREATED)
def crear_plan(nuevo_plan: PlanCrear) -> dict:
    for plan in PLANES:
        if plan["codigo"] == nuevo_plan.codigo.upper():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El código {nuevo_plan.codigo} ya existe",
            )
    plan_creado = nuevo_plan.model_dump()
    PLANES.append(plan_creado)
    return plan_creado


# Pregunta 2
@router.get("/facturacion-periodo", status_code=status.HTTP_200_OK)
def facturar_periodo(
    meses: int = Query(ge=1, le=24, description="Cantidad de meses que contrata el socio"),
    nivel: int | None = Query(default=None, ge=1, le=5, description="Filtra por nivel"),
) -> dict:
    
    seleccion: list[dict] = []
    for plan in PLANES:
        if nivel is not None and plan["nivel"] != nivel:
            continue
        seleccion.append(plan)

    
    if not seleccion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay planes registrados para el nivel {nivel}",
        )

    
    suma_precios = 0
    con_entrenador = 0
    for plan in seleccion:
        suma_precios += plan["precio_mensual"]
        if plan["incluye_entrenador"]:
            con_entrenador += 1

    facturacion_base = suma_precios * meses

    
    descuento_aplicado = meses >= 12
    facturacion_estimada = facturacion_base * 0.85 if descuento_aplicado else facturacion_base

    
    return {
        "planes": len(seleccion),
        "meses": meses,
        "precio_promedio": round(suma_precios / len(seleccion), 2),
        "facturacion_base": facturacion_base,
        "descuento_aplicado": descuento_aplicado,
        "facturacion_estimada": round(facturacion_estimada, 2),
        "porcentaje_con_entrenador": round(con_entrenador / len(seleccion) * 100, 1),
    }

# Pregunta 3
@router.get("/contrataciones-socio", status_code=status.HTTP_200_OK)
def contrataciones_socio(
    contratados: list[str] | None = Query(
        default=None,
        description="Códigos ya contratados; repite la clave ?contratados=BAS101&contratados=EST202",
    ),
) -> dict:
   
    if not PLANES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay planes registrados",
        )


    codigos_contratados = {codigo.upper() for codigo in contratados} if contratados else set()


    total = 0
    cantidad_contratados = 0
    disponibles: list[str] = []
    ingreso_disponibles = 0
    mas_caro: dict | None = None

    for plan in PLANES:
        total += 1
        if plan["codigo"] in codigos_contratados:
            cantidad_contratados += 1
            continue
        disponibles.append(plan["codigo"])
        ingreso_disponibles += plan["precio_mensual"]
        if mas_caro is None or plan["precio_mensual"] > mas_caro["precio_mensual"]:
            mas_caro = plan

    return {
        "total": total,
        "contratados": cantidad_contratados,
        "disponibles": disponibles,
        "porcentaje_contratacion": round(cantidad_contratados / total * 100, 1),
        "ingreso_potencial_disponibles": ingreso_disponibles,
        
        "plan_disponible_mas_caro": mas_caro["codigo"] if mas_caro is not None else None,
    }

@router.get("/planes/{codigo}", response_model=PlanSalida, status_code=status.HTTP_200_OK)
def ver_plan(plan: PlanExistente) -> dict:

    return plan

@router.patch("/planes/{codigo}", response_model=PlanSalida, status_code=status.HTTP_200_OK)
def actualizar_plan(cambios: PlanActualizar, plan: PlanExistente) -> dict:

    for campo, valor in cambios.model_dump(exclude_unset=True).items():
        plan[campo] = valor
    return plan

@router.delete("/planes/{codigo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_plan(plan: PlanExistente) -> Response:
    PLANES.remove(plan)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
