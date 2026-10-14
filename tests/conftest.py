import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest

from app.db import conectar


@pytest.fixture
def ruta_bd(tmp_path: Path) -> Path:
    return tmp_path / "test.db"


@pytest.fixture
def conexion(ruta_bd: Path) -> Iterator[sqlite3.Connection]:
    conexion = conectar(ruta_bd)
    yield conexion
    conexion.close()
