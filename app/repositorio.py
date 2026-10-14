import sqlite3

from app.modelos import Estado, Orden, OrdenNueva

# Único módulo con SQL. Todas las consultas son parametrizadas (?): los datos del usuario
# nunca se concatenan en el texto SQL.


def crear(conexion: sqlite3.Connection, datos: OrdenNueva) -> Orden:
    with conexion:
        cursor = conexion.execute(
            "INSERT INTO ordenes (codigo_cliente, descripcion_bici, problema, estado)"
            " VALUES (?, ?, ?, ?)",
            (datos.codigo_cliente, datos.descripcion_bici, datos.problema, Estado.PENDIENTE),
        )
    return Orden(id=cursor.lastrowid, **datos.model_dump(), estado=Estado.PENDIENTE)


def listar(conexion: sqlite3.Connection) -> list[Orden]:
    filas = conexion.execute(
        "SELECT id, codigo_cliente, descripcion_bici, problema, estado"
        " FROM ordenes ORDER BY id DESC"
    ).fetchall()
    return [Orden(**dict(fila)) for fila in filas]


def obtener(conexion: sqlite3.Connection, id_orden: int) -> Orden | None:
    fila = conexion.execute(
        "SELECT id, codigo_cliente, descripcion_bici, problema, estado FROM ordenes WHERE id = ?",
        (id_orden,),
    ).fetchone()
    return Orden(**dict(fila)) if fila else None


def cambiar_estado(conexion: sqlite3.Connection, id_orden: int, estado: Estado) -> Orden | None:
    with conexion:
        conexion.execute("UPDATE ordenes SET estado = ? WHERE id = ?", (estado, id_orden))
    return obtener(conexion, id_orden)
