# Registro de uso de IA

| Fase | Qué hizo la IA | Qué decidí / comprobé yo |
|------|----------------|--------------------------|
| 0. Preparación | En modo plan propuso la preparación del proyecto y, tras mi aprobación, creó la carpeta, el repositorio y la estructura. Redactó un `CLAUDE.md` con las reglas de trabajo del agente, instaló el entorno y creó plantillas vacías. | Revisé dichas normas y establecí criterios de validación para dar por terminada una tarea. |
| 1. Especificación | Me hizo preguntas sobre el enunciado para detectar huecos y ambigüedades. Revisó la especificación que redacté, señaló huecos e inconsistencias y, a petición mía, ajustó `SPEC.md`. | Redacté la especificación y decidí las reglas principales. Descarté una inconsistencia que señaló por ser errónea y aprobé la versión final. |
| 2. Plan | Propuso el plan: arquitectura, modelo de datos, API, decisiones de diseño y tareas con sus criterios de validación. | Revisé el plan, elegí FastAPI con rutas y nombres en español y lo aprobé. |
| 3. Implementación | Implementó las cinco tareas del plan con TDD: escribió los tests y el código, y comprobó cada tarea con los tests, ruff y fallos introducidos a propósito. Probó la interfaz en el navegador y corrigió problemas de visualización en pantallas medianas y en el móvil. | Validé cada tarea antes de su commit, ejecutando los tests y probando la aplicación. |
| 4. Verificación | Preparó la lista de pruebas manuales. | Ejecuté los tests automáticos (74 pasan) y realicé las 10 pruebas manuales, incluido reiniciar el servidor para comprobar la persistencia. Todas correctas. |
