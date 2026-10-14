import pytest
from pydantic import ValidationError

from app.modelos import CambioEstado, Estado, OrdenNueva

VALIDA = {
    "codigo_cliente": "CLI-0001",
    "descripcion_bici": "Bici de montaña roja",
    "problema": "La cadena se sale al cambiar de marcha",
}

LIMITES = [("descripcion_bici", 3, 120), ("problema", 3, 500)]


def nueva(**cambios: str) -> OrdenNueva:
    return OrdenNueva(**{**VALIDA, **cambios})


def test_orden_valida() -> None:
    orden = nueva()
    assert orden.codigo_cliente == "CLI-0001"
    assert orden.descripcion_bici == "Bici de montaña roja"
    assert orden.problema == "La cadena se sale al cambiar de marcha"


# Criterio 1: normalización del código de cliente


def test_codigo_se_normaliza_a_mayusculas_y_sin_espacios() -> None:
    assert nueva(codigo_cliente="  cli-0001 ").codigo_cliente == "CLI-0001"


# Criterio 2: códigos que no cumplen CLI-0000


@pytest.mark.parametrize(
    "codigo",
    ["Juan Pérez", "600123456", "CLI-123", "CLI-12345", "CLI0001", "XXX-0001", "", "CLI-١٢٣٤"],
)
def test_codigo_invalido(codigo: str) -> None:
    with pytest.raises(ValidationError) as error:
        nueva(codigo_cliente=codigo)
    assert error.value.errors()[0]["loc"] == ("codigo_cliente",)


# Criterio 3: longitudes de bici (3-120) y problema (3-500)


@pytest.mark.parametrize(("campo", "minimo", "maximo"), LIMITES)
def test_limites_exactos_aceptados(campo: str, minimo: int, maximo: int) -> None:
    assert len(getattr(nueva(**{campo: "x" * minimo}), campo)) == minimo
    assert len(getattr(nueva(**{campo: "x" * maximo}), campo)) == maximo


@pytest.mark.parametrize(("campo", "minimo", "maximo"), LIMITES)
def test_fuera_de_limites_rechazado(campo: str, minimo: int, maximo: int) -> None:
    for valor in ("x" * (minimo - 1), "x" * (maximo + 1)):
        with pytest.raises(ValidationError):
            nueva(**{campo: valor})


@pytest.mark.parametrize("campo", ["descripcion_bici", "problema"])
@pytest.mark.parametrize("valor", ["", "     "])
def test_vacio_o_solo_espacios_rechazado(campo: str, valor: str) -> None:
    with pytest.raises(ValidationError):
        nueva(**{campo: valor})


@pytest.mark.parametrize("campo", ["descripcion_bici", "problema"])
def test_espacios_exteriores_se_eliminan_antes_de_medir(campo: str) -> None:
    assert getattr(nueva(**{campo: "  abc  "}), campo) == "abc"
    with pytest.raises(ValidationError):
        nueva(**{campo: "  ab  "})


@pytest.mark.parametrize("campo", list(VALIDA))
def test_campo_obligatorio(campo: str) -> None:
    datos = {k: v for k, v in VALIDA.items() if k != campo}
    with pytest.raises(ValidationError):
        OrdenNueva(**datos)


# Criterio 4: al crear no se puede enviar el estado ni otros campos


@pytest.mark.parametrize("extra", [{"estado": "Terminada"}, {"id": 99}, {"otro": "x"}])
def test_no_se_aceptan_campos_extra_al_crear(extra: dict) -> None:
    with pytest.raises(ValidationError):
        OrdenNueva(**VALIDA, **extra)


# Criterio 5: solo los tres estados exactos


def test_estados_permitidos() -> None:
    assert [e.value for e in Estado] == ["Pendiente", "En reparación", "Terminada"]


@pytest.mark.parametrize("estado", ["Pendiente", "En reparación", "Terminada"])
def test_estado_valido(estado: str) -> None:
    assert CambioEstado(estado=estado).estado == estado


@pytest.mark.parametrize("estado", ["Entregada", "pendiente", "En reparacion", "", "TERMINADA"])
def test_estado_no_valido(estado: str) -> None:
    with pytest.raises(ValidationError):
        CambioEstado(estado=estado)


# Revisión D5: caracteres invisibles o de control en los textos libres


@pytest.mark.parametrize("campo", ["descripcion_bici", "problema"])
@pytest.mark.parametrize("valor", ["​​​", "\x00\x01\x02", "Bici​roja"])
def test_texto_con_caracteres_invisibles_o_de_control_rechazado(campo: str, valor: str) -> None:
    with pytest.raises(ValidationError):
        nueva(**{campo: valor})


def test_el_problema_admite_varias_lineas() -> None:
    assert (
        nueva(problema="Pinchazo.\nTambién frena poco.").problema
        == "Pinchazo.\nTambién frena poco."
    )
