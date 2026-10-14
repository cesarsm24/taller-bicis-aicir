from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import db
from app.main import app

VALIDA = {
    "codigo_cliente": "CLI-0010",
    "descripcion_bici": "Bici eléctrica blanca",
    "problema": "La batería no carga",
}


@pytest.fixture
def cliente(ruta_bd: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setenv("TALLER_DB_PATH", str(ruta_bd))
    with TestClient(app) as cliente:
        yield cliente


def crear(cliente: TestClient, **cambios: str) -> dict:
    respuesta = cliente.post("/api/ordenes", json={**VALIDA, **cambios})
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


# Criterio 1: crear una orden válida


def test_crear_orden(cliente: TestClient) -> None:
    orden = crear(cliente, codigo_cliente=" cli-0010 ")
    assert orden == {
        "id": 1,
        "codigo_cliente": "CLI-0010",
        "descripcion_bici": "Bici eléctrica blanca",
        "problema": "La batería no carga",
        "estado": "Pendiente",
    }


def test_ids_distintos(cliente: TestClient) -> None:
    assert crear(cliente)["id"] != crear(cliente)["id"]


# Criterio 2: datos no válidos → 422, indica el campo y no guarda nada


@pytest.mark.parametrize(
    ("cambios", "campo"),
    [
        ({"codigo_cliente": "Juan Pérez"}, "codigo_cliente"),
        ({"descripcion_bici": "ab"}, "descripcion_bici"),
        ({"problema": "   "}, "problema"),
        ({"estado": "Terminada"}, "estado"),
    ],
)
def test_crear_con_datos_no_validos(cliente: TestClient, cambios: dict, campo: str) -> None:
    respuesta = cliente.post("/api/ordenes", json={**VALIDA, **cambios})
    assert respuesta.status_code == 422
    assert [error["loc"][-1] for error in respuesta.json()["detail"]] == [campo]
    assert cliente.get("/api/ordenes").json() == []


def test_crear_sin_un_campo(cliente: TestClient) -> None:
    datos = {k: v for k, v in VALIDA.items() if k != "problema"}
    respuesta = cliente.post("/api/ordenes", json=datos)
    assert respuesta.status_code == 422
    assert respuesta.json()["detail"][0]["loc"][-1] == "problema"


# Criterio 3: listar de la más reciente a la más antigua


def test_listar_sin_ordenes(cliente: TestClient) -> None:
    respuesta = cliente.get("/api/ordenes")
    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_listar_de_la_mas_reciente_a_la_mas_antigua(cliente: TestClient) -> None:
    creadas = [crear(cliente, codigo_cliente=f"CLI-000{n}") for n in range(1, 4)]
    assert cliente.get("/api/ordenes").json() == list(reversed(creadas))


# Criterio 4: los tests usan una base de datos temporal


def test_la_api_usa_la_base_de_datos_temporal(cliente: TestClient, ruta_bd: Path) -> None:
    crear(cliente)
    assert Path(db.ruta_configurada()) == ruta_bd
    assert ruta_bd.exists()
