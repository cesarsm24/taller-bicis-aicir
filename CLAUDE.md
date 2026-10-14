# taller-bicis-aicir

Prototipo local para gestionar órdenes de reparación de un taller de bicicletas.
Caso práctico con límite de 3 horas: prima lo simple y claro.

## Reglas
1. Solo datos inventados. Nunca nombres, teléfonos, emails ni otros datos personales reales.
2. `SPEC.md` define qué se construye y `PLAN.md` cómo. No implementar nada que no esté ahí;
   si falta algo, proponerlo y esperar aprobación.
3. Trabajar tarea a tarea según `PLAN.md`. Tocar solo los archivos permitidos de la tarea.
4. TDD: test que falla → código mínimo → test que pasa.
5. No avanzar a la siguiente tarea ni fase sin aprobación del autor.
6. No afirmar que algo funciona sin haberlo ejecutado. No modificar un test para que pase
   un código defectuoso.
7. Un commit por tarea: `feat(T-0X): descripción`.

## Definición de Hecho (cada tarea)
- [ ] Solo se han modificado los archivos permitidos (`git status`).
- [ ] No se ha añadido nada fuera de la tarea (`git diff`).
- [ ] Cada criterio "Hecho cuando" tiene al menos un test, incluidos los casos de error.
- [ ] `uv run pytest` y `uv run ruff check .` pasan.
- [ ] Al terminar, informar: archivos tocados, criterio → test, resultado de las comprobaciones.

## Comandos
- Instalar: `uv sync`
- Tests: `uv run pytest`
- Lint: `uv run ruff check . && uv run ruff format --check .`
