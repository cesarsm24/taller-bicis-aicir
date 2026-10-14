import os
import sqlite3
from pathlib import Path

ESQUEMA = """
CREATE TABLE IF NOT EXISTS ordenes (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_cliente   TEXT NOT NULL,
    descripcion_bici TEXT NOT NULL,
    problema         TEXT NOT NULL,
    estado           TEXT NOT NULL
                     CHECK (estado IN ('Pendiente', 'En reparación', 'Terminada'))
)
"""


def ruta_configurada() -> str:
    return os.environ.get("TALLER_DB_PATH", "taller.db")


def conectar(ruta: str | Path | None = None) -> sqlite3.Connection:
    # check_same_thread=False: FastAPI puede abrir la conexión y usarla en hilos distintos
    # dentro de una misma petición. Cada petición tiene su propia conexión; no se comparte.
    conexion = sqlite3.connect(ruta or ruta_configurada(), check_same_thread=False)
    conexion.row_factory = sqlite3.Row
    conexion.execute(ESQUEMA)
    return conexion
