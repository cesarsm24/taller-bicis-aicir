import sqlite3
from collections.abc import Iterator
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app import repositorio
from app.db import conectar
from app.modelos import Orden, OrdenNueva

router = APIRouter(prefix="/api/ordenes", tags=["órdenes"])


def obtener_conexion() -> Iterator[sqlite3.Connection]:
    conexion = conectar()
    try:
        yield conexion
    finally:
        conexion.close()


Conexion = Annotated[sqlite3.Connection, Depends(obtener_conexion)]


@router.get("")
def listar_ordenes(conexion: Conexion) -> list[Orden]:
    return repositorio.listar(conexion)


@router.post("", status_code=status.HTTP_201_CREATED)
def crear_orden(datos: OrdenNueva, conexion: Conexion) -> Orden:
    return repositorio.crear(conexion, datos)
