import unicodedata
from enum import StrEnum
from typing import Annotated, Any

from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, Field

# [0-9] y no \d: \d también acepta dígitos de otros alfabetos.
PATRON_CODIGO_CLIENTE = r"^CLI-[0-9]{4}$"


class Estado(StrEnum):
    PENDIENTE = "Pendiente"
    EN_REPARACION = "En reparación"
    TERMINADA = "Terminada"


def _normalizar_codigo(valor: Any) -> Any:
    return valor.strip().upper() if isinstance(valor, str) else valor


CodigoCliente = Annotated[
    str, BeforeValidator(_normalizar_codigo), Field(pattern=PATRON_CODIGO_CLIENTE)
]

SALTOS_PERMITIDOS = {"\n", "\r", "\t"}


def _sin_caracteres_invisibles(valor: str) -> str:
    # Rechaza caracteres de control (Cc) y de formato invisibles (Cf, p. ej. espacio de ancho
    # cero): permitirían un texto que parece vacío pero supera la longitud mínima (RN-05).
    for caracter in valor:
        if caracter not in SALTOS_PERMITIDOS and unicodedata.category(caracter) in ("Cc", "Cf"):
            raise ValueError("no puede contener caracteres invisibles o de control")
    return valor


TextoLibre = Annotated[str, AfterValidator(_sin_caracteres_invisibles)]


class OrdenNueva(BaseModel):
    """Datos que envía el usuario para crear una orden. El estado no se elige (RN-02)."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    codigo_cliente: CodigoCliente
    descripcion_bici: TextoLibre = Field(min_length=3, max_length=120)
    problema: TextoLibre = Field(min_length=3, max_length=500)


class CambioEstado(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estado: Estado


class Orden(BaseModel):
    id: int
    codigo_cliente: str
    descripcion_bici: str
    problema: str
    estado: Estado
