# Plan: diseño y tareas

> Propuesto por el agente a partir de `SPEC.md` y aprobado por el autor.

## 1. Arquitectura

Una API JSON con FastAPI y una página HTML + CSS + JavaScript (sin frameworks) que la consume.
La misma aplicación sirve la API y la página, así que basta con un comando para arrancarla.

```
Navegador (static/index.html + app.js)
        │  JSON
        ▼
api.py         rutas de la API; traduce errores a códigos HTTP
        │
        ▼
repositorio.py único módulo con SQL (consultas parametrizadas)
        │
        ▼
db.py          conexión SQLite y creación de la tabla
```

| Archivo | Responsabilidad |
|---|---|
| `app/modelos.py` | Estados permitidos y modelos Pydantic: normalización y validación de los datos |
| `app/db.py` | Conexión SQLite por petición y creación de la tabla |
| `app/repositorio.py` | Crear, listar, obtener y cambiar el estado de órdenes |
| `app/api.py` | Rutas de la API |
| `app/main.py` | Crea la aplicación y sirve la página |
| `app/static/` | `index.html`, `app.js`, `estilos.css` |

La validación la hace Pydantic en `modelos.py` antes de llegar al repositorio. No hay capa de
servicio: para tres operaciones no aporta nada (RNF-05).

## 2. Modelo de datos

```sql
CREATE TABLE IF NOT EXISTS ordenes (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_cliente   TEXT NOT NULL,
    descripcion_bici TEXT NOT NULL,
    problema         TEXT NOT NULL,
    estado           TEXT NOT NULL
                     CHECK (estado IN ('Pendiente', 'En reparación', 'Terminada'))
);
```

- `AUTOINCREMENT` garantiza que los id no se reutilizan, así que ordenar por id equivale a ordenar
  por antigüedad (RF-02 CA3).
- El `CHECK` es una segunda barrera; la validación principal está en `modelos.py` (RN-05).
- La ruta de la base de datos se configura con `TALLER_DB_PATH` (por defecto `taller.db`, ignorado
  por git). Los tests usan una base de datos temporal (RNF-02).

## 3. API

| Método | Ruta | Qué hace | Respuestas |
|---|---|---|---|
| `GET` | `/` | Página de la aplicación | `200` |
| `GET` | `/api/ordenes` | Lista las órdenes, más recientes primero | `200` |
| `POST` | `/api/ordenes` | Crea una orden | `201` · `422` datos no válidos (indica el campo) |
| `PATCH` | `/api/ordenes/{id}/estado` | Cambia el estado. Cuerpo: `{"estado": "Terminada"}` | `200` (también si es el mismo estado, sin cambios) · `404` no existe · `422` estado o id no válidos |

FastAPI genera además la documentación interactiva de la API en `/docs`.

## 4. Decisiones de diseño

| # | Decisión | Motivo |
|---|---|---|
| D-1 | `sqlite3` de la librería estándar, sin ORM | Una sola tabla: el SQL es corto y visible, y hay una dependencia menos |
| D-2 | Validación con Pydantic en `modelos.py` | FastAPI la aplica automáticamente y devuelve 422 indicando el campo |
| D-3 | Ruta de la base de datos por variable de entorno | Los tests usan una base de datos temporal sin tocar la real |
| D-4 | `PATCH` para cambiar el estado | Modifica solo una parte de la orden |
| D-5 | Ningún recurso externo (ni fuentes ni CDN) | Funciona sin internet y no envía peticiones a terceros |
| D-6 | Estados guardados con su texto exacto (`En reparación`) | Coinciden con `SPEC.md`; no hace falta traducir entre código e interfaz |

Dependencias nuevas: `fastapi` y `uvicorn`; para los tests, el cliente HTTP que requiera el
`TestClient` de FastAPI.

## 5. Tareas

Cada tarea sigue la Definición de Hecho de `CLAUDE.md` y termina en un commit `feat(T-0X): …`.

### T-01 · Estados y validación de una orden
- **Requisitos:** RF-01 CA3, RN-02, RN-03, RN-05, RN-07
- **Archivos:** `pyproject.toml`, `uv.lock`, `app/modelos.py`, `tests/test_modelos.py`
- **Hecho cuando:**
  1. `cli-0001` con espacios se normaliza a `CLI-0001`.
  2. Se rechazan códigos que no cumplen `CLI-0000`, como `Juan Pérez`, `600123456` o `CLI-123`.
  3. Bici (3–120) y problema (3–500): se aceptan los límites exactos y se rechazan el valor anterior al mínimo, el posterior al máximo, el vacío y el formado solo por espacios.
  4. Al crear una orden no se puede enviar el estado ni otros campos.
  5. Solo los tres estados exactos son válidos; `Entregada` o `pendiente` no lo son.

### T-02 · Base de datos y repositorio
- **Requisitos:** RF-01 CA1 y CA4, RF-02 CA3, RF-04, RN-01, RN-02, RN-06, RNF-02, RNF-04
- **Archivos:** `app/db.py`, `app/repositorio.py`, `tests/conftest.py`, `tests/test_repositorio.py`
- **Hecho cuando:**
  1. Una orden creada tiene un id nuevo y estado `Pendiente`.
  2. Dos órdenes reciben id distintos.
  3. El listado devuelve las órdenes de la más reciente a la más antigua, cada una una vez.
  4. Cambiar el estado modifica solo esa orden; una orden inexistente no modifica nada.
  5. Tras cerrar y reabrir la base de datos, las órdenes y sus estados siguen ahí.
  6. Un dato con texto malicioso (`' OR '1'='1`) se guarda como texto y no altera la consulta.

### T-03 · API: crear y listar
- **Requisitos:** RF-01 CA1, CA3 y CA4, RF-02 CA1 y CA3, RNF-02
- **Archivos:** `pyproject.toml`, `uv.lock`, `app/api.py`, `app/main.py`, `tests/test_api.py`
- **Hecho cuando:**
  1. `POST /api/ordenes` válido responde 201 con la orden en `Pendiente`.
  2. Datos no válidos responden 422, indican el campo y no guardan nada.
  3. `GET /api/ordenes` devuelve las órdenes, de la más reciente a la más antigua.
  4. Los tests usan una base de datos temporal y la real no se crea ni se modifica.

### T-04 · API: cambiar el estado
- **Requisitos:** RF-03 CA1 a CA4, RN-04, RN-06
- **Archivos:** `app/api.py`, `tests/test_api.py`
- **Hecho cuando:**
  1. Se puede pasar de cualquier estado a cualquier otro; la respuesta y el listado lo reflejan.
  2. Elegir el estado actual responde 200 sin modificar la orden.
  3. Un estado no válido responde 422 y la orden no cambia.
  4. Una orden inexistente responde 404 con un mensaje claro; un id no numérico, 422.

### T-05 · Interfaz web
- **Requisitos:** RF-01 CA2, RF-02 CA1 y CA2, RF-03 CA1 y CA2, RNF-01, RNF-04, RNF-08
- **Archivos:** `app/main.py`, `app/static/index.html`, `app/static/app.js`, `app/static/estilos.css`, `tests/test_api.py`
- **Hecho cuando:**
  1. `GET /` sirve la página (test automático).
  2. Crear una orden muestra "Orden #N creada" y aparece en el listado.
  3. Un error de validación se muestra junto al campo, en español, y conserva lo escrito.
  4. Sin órdenes, muestra "No hay reparaciones registradas".
  5. Cada orden tiene un selector de estado; cambiarlo muestra un mensaje, y elegir el mismo, "Sin cambios".
  6. El formulario avisa de que no se escriban datos personales.
  7. Un texto como `<script>` se muestra como texto y no se ejecuta.
  8. Cada estado se distingue visualmente y no solo por el color; se usa bien en el móvil.
  9. Los puntos 2 a 8 se comprueban a mano en el navegador.

## 6. Fases siguientes (referencia)

- **Fase 4, verificación:** `uv run pytest` y prueba manual: crear dos órdenes, provocar un error de validación, cambiar estados, recargar la página y reiniciar el servidor.
- **Fase 5, revisión:** sesión nueva con este prompt:
  > Actúa solo como revisor. No modifiques archivos. Revisa el proyecto frente a `SPEC.md`: errores funcionales, validaciones incompletas, SQL inseguro, persistencia, código innecesario, usabilidad, riesgos con datos personales e instrucciones del README. Clasifica cada hallazgo por gravedad, con archivo, evidencia y solución propuesta. Distingue defectos confirmados de posibles mejoras.
