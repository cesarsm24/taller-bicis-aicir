import sqlite3
from pathlib import Path

import pytest

from app import repositorio
from app.db import conectar
from app.modelos import Estado, Orden, OrdenNueva


def crear(
    conexion: sqlite3.Connection, codigo: str = "CLI-0001", bici: str = "Bici urbana"
) -> Orden:
    datos = OrdenNueva(codigo_cliente=codigo, descripcion_bici=bici, problema="Pinchazo trasero")
    return repositorio.crear(conexion, datos)


# Criterio 1: id nuevo y estado Pendiente


def test_crear_orden(conexion: sqlite3.Connection) -> None:
    orden = crear(conexion, codigo="CLI-0042", bici="Bici de paseo azul")
    assert orden == Orden(
        id=1,
        codigo_cliente="CLI-0042",
        descripcion_bici="Bici de paseo azul",
        problema="Pinchazo trasero",
        estado=Estado.PENDIENTE,
    )
    assert repositorio.obtener(conexion, orden.id) == orden


# Criterio 2: ids distintos


def test_ids_distintos(conexion: sqlite3.Connection) -> None:
    ids = [crear(conexion).id for _ in range(3)]
    assert len(set(ids)) == 3


# Criterio 3: listado de la más reciente a la más antigua, cada una una vez


def test_listar_sin_ordenes(conexion: sqlite3.Connection) -> None:
    assert repositorio.listar(conexion) == []


def test_listar_de_la_mas_reciente_a_la_mas_antigua(conexion: sqlite3.Connection) -> None:
    creadas = [crear(conexion, codigo=f"CLI-000{n}") for n in range(1, 4)]
    assert repositorio.listar(conexion) == list(reversed(creadas))


# Criterio 4: cambiar el estado solo afecta a esa orden


def test_cambiar_estado_solo_modifica_esa_orden(conexion: sqlite3.Connection) -> None:
    primera = crear(conexion)
    segunda = crear(conexion)
    actualizada = repositorio.cambiar_estado(conexion, primera.id, Estado.TERMINADA)
    assert actualizada == primera.model_copy(update={"estado": Estado.TERMINADA})
    assert repositorio.obtener(conexion, primera.id) == actualizada
    assert repositorio.obtener(conexion, segunda.id) == segunda


def test_cambiar_estado_de_orden_inexistente_no_modifica_nada(
    conexion: sqlite3.Connection,
) -> None:
    existente = crear(conexion)
    assert repositorio.cambiar_estado(conexion, 999, Estado.TERMINADA) is None
    assert repositorio.listar(conexion) == [existente]


def test_obtener_orden_inexistente(conexion: sqlite3.Connection) -> None:
    assert repositorio.obtener(conexion, 999) is None


# Criterio 5: los datos se conservan al cerrar y reabrir


def test_ordenes_y_estados_se_conservan_al_reabrir(ruta_bd: Path) -> None:
    primera_conexion = conectar(ruta_bd)
    orden = crear(primera_conexion)
    repositorio.cambiar_estado(primera_conexion, orden.id, Estado.EN_REPARACION)
    primera_conexion.close()

    segunda_conexion = conectar(ruta_bd)
    recuperada = repositorio.obtener(segunda_conexion, orden.id)
    segunda_conexion.close()
    assert recuperada is not None
    assert recuperada.estado is Estado.EN_REPARACION


# Criterio 6: el texto malicioso se guarda como texto


@pytest.mark.parametrize("texto", ["' OR '1'='1", "x'); DROP TABLE ordenes; --"])
def test_texto_malicioso_se_guarda_como_texto(conexion: sqlite3.Connection, texto: str) -> None:
    orden = crear(conexion, bici=texto)
    assert repositorio.obtener(conexion, orden.id).descripcion_bici == texto
    assert len(repositorio.listar(conexion)) == 1


# Segunda barrera: la base de datos rechaza estados desconocidos


def test_la_base_de_datos_rechaza_estados_desconocidos(conexion: sqlite3.Connection) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        conexion.execute(
            "INSERT INTO ordenes (codigo_cliente, descripcion_bici, problema, estado)"
            " VALUES ('CLI-0001', 'Bici', 'Pinchazo', 'Entregada')"
        )
