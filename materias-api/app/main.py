"""Aplicación FastAPI: monta el router con include_router."""

from fastapi import FastAPI

from app.router import router

app = FastAPI(
    title="API Gimnasio — Planes de Membresía",
    version="1.0.0",
    description="Examen FastAPI variante 1: CRUD en memoria, facturación y planes contratados.",
)

app.include_router(router)


@app.get("/")
def raiz() -> dict:
    return {"api": "planes de membresía", "docs": "/docs"}
