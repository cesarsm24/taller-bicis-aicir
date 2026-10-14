from fastapi import FastAPI

from app import api

app = FastAPI(
    title="Taller de bicicletas",
    description="Prototipo de gestión de órdenes de reparación. Solo datos ficticios.",
    version="0.1.0",
)

app.include_router(api.router)
