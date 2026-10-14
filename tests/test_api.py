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


# --- T-04: cambiar el estado ---

ESTADOS = ["Pendiente", "En reparación", "Terminada"]


def cambiar(cliente: TestClient, id_orden: int | str, estado: str):
    return cliente.patch(f"/api/ordenes/{id_orden}/estado", json={"estado": estado})


# Criterio 1: de cualquier estado a cualquier otro


@pytest.mark.parametrize(("desde", "hacia"), [(d, h) for d in ESTADOS for h in ESTADOS if d != h])
def test_cambiar_de_cualquier_estado_a_cualquier_otro(
    cliente: TestClient, desde: str, hacia: str
) -> None:
    orden = crear(cliente)
    if desde != "Pendiente":
        cambiar(cliente, orden["id"], desde)
    respuesta = cambiar(cliente, orden["id"], hacia)
    assert respuesta.status_code == 200
    assert respuesta.json() == {**orden, "estado": hacia}
    assert cliente.get("/api/ordenes").json() == [{**orden, "estado": hacia}]


def test_cambiar_estado_no_afecta_a_otras_ordenes(cliente: TestClient) -> None:
    primera = crear(cliente)
    segunda = crear(cliente)
    cambiar(cliente, primera["id"], "Terminada")
    assert cliente.get("/api/ordenes").json() == [segunda, {**primera, "estado": "Terminada"}]


# Criterio 2: elegir el estado actual responde 200 sin modificar la orden


@pytest.mark.parametrize("estado", ESTADOS)
def test_cambiar_al_mismo_estado_no_modifica_la_orden(cliente: TestClient, estado: str) -> None:
    orden = crear(cliente)
    if estado != "Pendiente":
        orden = cambiar(cliente, orden["id"], estado).json()
    respuesta = cambiar(cliente, orden["id"], estado)
    assert respuesta.status_code == 200
    assert respuesta.json() == orden
    assert cliente.get("/api/ordenes").json() == [orden]


# Criterio 3: un estado no válido responde 422 y la orden no cambia


@pytest.mark.parametrize(
    "cuerpo",
    [
        {"estado": "Entregada"},
        {"estado": "pendiente"},
        {"estado": ""},
        {},
        {"estado": "Terminada", "x": 1},
    ],
)
def test_estado_no_valido(cliente: TestClient, cuerpo: dict) -> None:
    orden = crear(cliente)
    respuesta = cliente.patch(f"/api/ordenes/{orden['id']}/estado", json=cuerpo)
    assert respuesta.status_code == 422
    assert cliente.get("/api/ordenes").json() == [orden]


# Criterio 4: orden inexistente → 404 con mensaje; id no numérico → 422


def test_cambiar_estado_de_orden_inexistente(cliente: TestClient) -> None:
    orden = crear(cliente)
    respuesta = cambiar(cliente, 999, "Terminada")
    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "No existe ninguna orden con id 999."}
    assert cliente.get("/api/ordenes").json() == [orden]


def test_cambiar_estado_con_id_no_numerico(cliente: TestClient) -> None:
    assert cambiar(cliente, "abc", "Terminada").status_code == 422
