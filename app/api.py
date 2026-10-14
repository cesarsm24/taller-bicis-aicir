import sqlite3
from collections.abc import Iterator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app import repositorio
from app.db import conectar
from app.modelos import CambioEstado, Orden, OrdenNueva

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


@router.patch("/{id_orden}/estado")
def cambiar_estado(id_orden: int, cambio: CambioEstado, conexion: Conexion) -> Orden:
    # Se permite cualquier estado, incluido el actual (RN-04): en ese caso no cambia nada.
    orden = repositorio.cambiar_estado(conexion, id_orden, cambio.estado)
    if orden is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe ninguna orden con id {id_orden}.",
        )
    return orden
