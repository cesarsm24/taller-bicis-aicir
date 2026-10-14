from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app import api

app = FastAPI(
    title="Taller de bicicletas",
    description="Prototipo de gestión de órdenes de reparación. Solo datos ficticios.",
    version="0.1.0",
)

app.include_router(api.router)

# Se monta al final para que las rutas /api tengan prioridad.
app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="interfaz")
