# Taller de bicicletas: órdenes de reparación

Prototipo local para registrar las bicicletas que recibe un taller y consultar el estado de cada
reparación. Caso práctico del proceso de selección PRET/TR3S60 de aicir.

Permite:
- **Crear** una orden de reparación (código ficticio de cliente, bicicleta y problema).
- **Consultar** las órdenes, de la más reciente a la más antigua.
- **Cambiar el estado** de una orden entre `Pendiente`, `En reparación` y `Terminada`.

Todos los datos son inventados. No hay usuarios ni se publica en internet.

## Requisitos

- [uv](https://docs.astral.sh/uv/), el gestor de proyectos de Python. Instala por sí solo la
  versión de Python necesaria (3.12 o superior).

## Instalación y ejecución

```bash
uv sync
uv run uvicorn app.main:app
```

Después, abrir http://localhost:8000.

- La documentación interactiva de la API está en http://localhost:8000/docs.
- Las órdenes se guardan en `taller.db` (SQLite) en la carpeta del proyecto y se conservan al
  reiniciar. Se puede usar otro archivo con la variable `TALLER_DB_PATH`.

## Pruebas

```bash
uv run pytest
uv run ruff check . && uv run ruff format --check .
```

Los tests usan una base de datos temporal: nunca tocan `taller.db`.

## Estructura

```
app/
├── modelos.py      estados y validación de los datos (Pydantic)
├── db.py           conexión SQLite y creación de la tabla
├── repositorio.py  único módulo con SQL (consultas parametrizadas)
├── api.py          rutas de la API REST
├── main.py         crea la aplicación y sirve la página
└── static/         página web: index.html, app.js, estilos.css
tests/              tests automáticos (pytest)
SPEC.md             especificación: requisitos, reglas y decisiones
PLAN.md             diseño y tareas
AI_LOG.md           registro del uso de IA por fase
docs/tiempo.md      tiempo empleado por fase
```

## Decisiones principales

El detalle está en [SPEC.md](SPEC.md) (qué se construye y por qué) y [PLAN.md](PLAN.md) (cómo).

| Decisión | Motivo |
|---|---|
| Código de cliente con formato cerrado `CLI-0000` | Un texto libre permitiría escribir nombres o teléfonos en ese campo |
| Cambio de estado libre entre los tres estados | El enunciado pide cambiar "entre" estados sin imponer un flujo; elegir el estado actual no es un error |
| SQLite en un archivo local | Las órdenes deben sobrevivir al reinicio sin instalar un servidor de base de datos |
| FastAPI + Pydantic | La validación se declara en los modelos y se aplica siempre en el servidor |
| Página HTML + JS sin frameworks ni recursos externos | Basta para una página, funciona sin internet y no contacta con terceros |
| Datos insertados en la página con `textContent` | Ningún texto escrito por un usuario puede ejecutarse como código |
| Errores: `422` datos no válidos, `404` orden inexistente | Comportamiento estándar de FastAPI; nunca se muestran trazas técnicas |

## Comprobaciones realizadas

- **84 tests automáticos**, que cubren cada criterio de aceptación de `SPEC.md`, incluidos los casos de error:
  - `test_modelos.py` (42): formato del código, límites de longitud, campos vacíos o invisibles y estados permitidos.
  - `test_repositorio.py` (11): creación, orden del listado, cambio de estado, persistencia al reabrir e intentos de inyección SQL.
  - `test_api.py` (31): respuestas 201/200/404/422, todas las transiciones de estado y la página web.
- **Fallos introducidos a propósito** en cada tarea (por ejemplo, quitar un `WHERE` o invertir el orden del listado) para confirmar que algún test los detecta.
- **Prueba manual en el navegador**: crear órdenes, provocar errores de validación, cambiar estados, recargar, **reiniciar el servidor** y comprobar que los datos siguen ahí, y usarla en pantalla de móvil.
- **Revisión independiente** en una sesión nueva sin contexto del desarrollo: 6 hallazgos, 4 corregidos con tests, 1 documentado como limitación y 1 resuelto con este README.

## Clientes y privacidad

En una versión futura, crearía una tabla `clientes` con un identificador único y los datos de contacto necesarios. Cada orden de reparación tendría un campo `cliente_id` como clave foránea para relacionarla con su cliente, evitando duplicar sus datos personales.

Aplicaría el principio de mínimo privilegio: el personal de recepción o administración podría consultar los datos de contacto para gestionar citas y avisar de que una reparación está terminada; los mecánicos accederían a la información técnica necesaria para realizar las reparaciones, sin acceder a los datos de contacto si no los necesitan. El acceso estaría protegido mediante autenticación y permisos según las responsabilidades de cada persona.

## Uso de IA

He usado **Claude Code** (modelo Claude Opus 5.5) como agente de desarrollo, dentro de un proceso por fases con un punto de control mío al final de cada una. El detalle por fase está en [AI_LOG.md](AI_LOG.md).

- **Para qué:** preparar la configuración del proyecto, revisar la especificación que redacté y ajustarla a petición mía, proponer el plan, implementar el código y los tests, revisar el proyecto en una sesión independiente y redactar la parte técnica de este README.
- **Qué decidí yo:** las reglas de la especificación, el stack (FastAPI en lugar de la primera propuesta con Flask), qué hallazgos de la revisión corregir y la aprobación de cada fase y cada tarea.
- **Cómo comprobé los resultados:** cada tarea tenía criterios de aceptación y no se daba por terminada sin pasar los tests y ruff, y sin introducir fallos a propósito para confirmar que los tests los detectaban. Ejecuté los tests y probé la aplicación en el navegador, incluido reiniciar el servidor. Al final, una sesión nueva sin contexto revisó el proyecto.
- **Precauciones con los datos:** en el código, los tests y las conversaciones con la IA solo se han usado datos inventados. Con datos reales no los compartiría con un asistente externo sin anonimizarlos ni sin un acuerdo de tratamiento de datos con el proveedor.

## Limitaciones y qué mejoraría

- **Estado desactualizado con dos pestañas abiertas.** El mensaje «Sin cambios» se calcula con el estado que muestra la pantalla, que puede estar desactualizado. Haría que la API indicara si hubo cambio real.
- **Sin autenticación ni roles.** Es aceptable solo porque es un prototipo local con datos ficticios; no debe usarse con datos reales. Sería lo primero antes de añadir datos de contacto.
- **Sin edición, borrado ni historial.** Añadiría un historial de cambios de estado (quién y cuándo) antes que el borrado, para no perder trazabilidad.
- **Sin fechas.** Guardaría la fecha de entrada y la de entrega prevista para ordenar y priorizar el trabajo.
- **Sin búsqueda ni filtros.** Filtrar por estado y por cliente será necesario cuando haya muchas órdenes.
- **Mensaje de error genérico** cuando el texto contiene caracteres invisibles: el servidor lo rechaza, pero la página muestra el mensaje de longitud.

## Tiempo empleado

**1 h 55 min en total**, dentro del límite de 3 horas. Desglose por fase en [docs/tiempo.md](docs/tiempo.md).
