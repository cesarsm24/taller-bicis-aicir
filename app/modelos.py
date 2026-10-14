from enum import StrEnum
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

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


class OrdenNueva(BaseModel):
    """Datos que envía el usuario para crear una orden. El estado no se elige (RN-02)."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    codigo_cliente: CodigoCliente
    descripcion_bici: str = Field(min_length=3, max_length=120)
    problema: str = Field(min_length=3, max_length=500)


class CambioEstado(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estado: Estado


class Orden(BaseModel):
    id: int
    codigo_cliente: str
    descripcion_bici: str
    problema: str
    estado: Estado
