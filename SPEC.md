# Especificación: gestión de reparaciones del taller

## 1. Problema

Un taller de bicicletas necesita una herramienta sencilla para registrar las bicicletas que recibe y consultar el estado de sus reparaciones. El objetivo es sustituir un seguimiento informal por un registro centralizado que permita conocer qué reparaciones existen y en qué situación se encuentran.

La herramienta está destinada al personal del taller que registra las bicicletas y actualiza su estado. En este prototipo no se implementará un sistema de usuarios ni de permisos.

La solución debe permitir:
- Crear órdenes de reparación con la información necesaria.
- Consultar las órdenes registradas.
- Cambiar el estado de una reparación entre `Pendiente`, `En reparación` y `Terminada`.

El desarrollo debe ser sencillo, comprensible, verificable y adecuado a un límite de tres horas. Se utilizarán exclusivamente datos ficticios y la aplicación se ejecutará en local.

## 2. Datos de una orden

| Campo | Descripción | Obligatorio | Formato / límites | Lo genera |
|-------|-------------|-------------|-------------------|-----------|
| `id` | Identificador único de la orden de reparación. | Sí | Entero positivo, único y autoincremental. No puede modificarse desde el formulario. | Sistema / base de datos |
| `codigo_cliente` | Código ficticio que identifica al cliente asociado a la reparación. | Sí | `CLI-` seguido de 4 dígitos (por ejemplo, `CLI-0001`). Se eliminan los espacios exteriores y se guarda en mayúsculas, de modo que `cli-0001` se acepta como `CLI-0001`. | Usuario |
| `descripcion_bici` | Descripción breve de la bicicleta, como tipo, marca o características relevantes. | Sí | Texto de 3 a 120 caracteres tras eliminar espacios exteriores. | Usuario |
| `problema` | Descripción del problema comunicado para la reparación. | Sí | Texto de 3 a 500 caracteres tras eliminar espacios exteriores. | Usuario |
| `estado` | Estado actual de la reparación. | Sí | Uno de estos valores exactos: `Pendiente`, `En reparación` o `Terminada`. | Sistema al crear; usuario al actualizar |

Los límites de longitud y el formato del código son decisiones de diseño del prototipo, no requisitos expresos del enunciado. Todos los campos se validan en el servidor antes de guardar los datos. Los campos obligatorios no pueden contener únicamente espacios en blanco.

## 3. Requisitos funcionales

### RF-01 — Crear una orden de reparación

La aplicación debe permitir registrar una nueva orden mediante un formulario.

- **Criterio de aceptación 1:** Dado un formulario con todos los campos obligatorios válidos, cuando el usuario lo envía, entonces el sistema crea y guarda una orden con un identificador único y el estado inicial `Pendiente`.
- **Criterio de aceptación 2:** Dado que se crea una orden correctamente, cuando termina la operación, entonces la aplicación muestra un mensaje de confirmación con el identificador de la orden y la nueva orden aparece en el listado.
- **Criterio de aceptación 3:** Dado un formulario con un campo vacío, formado solo por espacios, más corto o más largo que su límite, o con un código de cliente que no cumple el formato `CLI-0000`, cuando el usuario lo envía, entonces el sistema no guarda ninguna orden, responde con el código HTTP 422 y muestra un mensaje que indica qué campo es incorrecto y por qué.
- **Criterio de aceptación 4:** Dado que ya existen órdenes registradas, cuando se crea otra orden, entonces recibe un identificador diferente de los anteriores.

### RF-02 — Consultar las órdenes existentes

La aplicación debe mostrar las órdenes registradas y permitir consultar los datos principales de cada una.

- **Criterio de aceptación 1:** Dado que existen órdenes guardadas, cuando el usuario accede al listado, entonces aparecen sus identificadores, códigos de cliente, descripciones, problemas comunicados y estados actuales.
- **Criterio de aceptación 2:** Dado que todavía no existen órdenes, cuando el usuario accede al listado, entonces se muestra un mensaje indicando que no hay reparaciones registradas.
- **Criterio de aceptación 3:** Dado que existen varias órdenes, cuando se muestra el listado, entonces cada orden aparece una sola vez, ordenadas de la más reciente a la más antigua (identificador descendente).

### RF-03 — Cambiar el estado de una reparación

La aplicación debe permitir modificar el estado de una orden existente utilizando los tres estados definidos.

- **Criterio de aceptación 1:** Dada una orden existente, cuando el usuario elige un estado permitido distinto del actual y envía el cambio, entonces el nuevo estado se guarda, aparece actualizado en el listado y se muestra un mensaje de confirmación.
- **Criterio de aceptación 2:** Dada una orden existente, cuando el usuario elige el mismo estado que ya tiene, entonces la operación se acepta sin modificar la orden y se informa de que no ha habido cambios.
- **Criterio de aceptación 3:** Dado un identificador que no corresponde a ninguna orden, cuando se intenta cambiar su estado, entonces no se modifica ninguna orden y la aplicación responde con el código HTTP 404 y un mensaje que indica que la orden no existe. Si el identificador no es un número entero, responde con el código HTTP 422.
- **Criterio de aceptación 4:** Dado un valor de estado distinto de los tres permitidos, cuando se envía una petición para actualizar una orden, entonces el servidor la rechaza con el código HTTP 422, muestra un mensaje de error y conserva el estado anterior.

### RF-04 — Conservar las órdenes registradas

La aplicación debe almacenar las órdenes de manera persistente.

- **Criterio de aceptación 1:** Dada una orden creada correctamente, cuando se detiene y se vuelve a iniciar la aplicación, entonces la orden sigue disponible en el listado.
- **Criterio de aceptación 2:** Dado un cambio de estado guardado correctamente, cuando se reinicia la aplicación, entonces el estado actualizado se conserva.

## 4. Reglas de negocio

**RN-01 — Identificador único.** Cada orden debe tener un identificador generado por el sistema. El usuario no puede elegirlo ni modificarlo.

**RN-02 — Estado inicial.** Toda orden nueva empieza en `Pendiente`. El usuario no selecciona el estado inicial durante la creación.

**RN-03 — Estados permitidos.** Los únicos estados válidos son:
- `Pendiente`
- `En reparación`
- `Terminada`

**RN-04 — Cambios de estado.** Se permite cambiar una orden desde cualquiera de los tres estados a cualquiera de los tres, sin imponer un flujo obligatorio. Esta decisión interpreta el enunciado como una selección libre entre los estados permitidos. Elegir el estado actual no es un error: no produce cambios.

**RN-05 — Validación en el servidor.** Ningún dato recibido del navegador se considerará válido por el mero hecho de proceder de un formulario. El servidor comprobará los campos obligatorios, los límites de longitud, el formato del código de cliente y los estados permitidos.

**RN-06 — Integridad de las órdenes.** Una actualización de estado solo puede modificar la orden identificada. Si la orden no existe o el nuevo estado no es válido, la operación debe rechazarse sin alterar datos.

**RN-07 — Código de cliente ficticio.** El código de cliente identifica de forma ficticia al cliente asociado a una reparación. Su formato cerrado (`CLI-0000`) impide escribir en ese campo nombres, teléfonos o correos. No se almacenarán datos personales reales.

## 5. Requisitos no funcionales

**RNF-01 — Privacidad.** Todos los datos utilizados durante el desarrollo y las demostraciones serán inventados. No se incorporarán datos personales reales ni credenciales. El formulario recordará que no deben escribirse datos personales en los campos de texto libre, ya que en ellos no puede impedirse por validación. El README explicará cómo se relacionarían en una futura versión las reparaciones con los datos de contacto de los clientes y qué restricciones de acceso serían necesarias.

**RNF-02 — Persistencia local.** Se utilizará SQLite para conservar los datos en un archivo local. La base de datos de la aplicación será independiente de la utilizada por las pruebas automatizadas.

**RNF-03 — Restricción tecnológica.** Por decisión del autor, se utilizarán Python, FastAPI, SQLite, HTML, CSS y JavaScript sin frameworks. La arquitectura y la organización del código se detallan en `PLAN.md`.

**RNF-04 — Seguridad básica.** Las consultas SQL se parametrizarán. Las entradas se validarán en el servidor y la interfaz insertará los datos en la página como texto (`textContent`, nunca `innerHTML`), de modo que ningún dato pueda ejecutarse como código. No se almacenarán secretos en el repositorio.

**RNF-05 — Mantenibilidad.** El código debe ser legible, utilizar nombres descriptivos, evitar duplicaciones innecesarias y mantener las dependencias al mínimo. No se introducirán abstracciones que no aporten una ventaja clara al alcance del proyecto.

**RNF-06 — Verificación.** Se utilizará pytest para comprobar cada criterio de aceptación, incluidos los casos de error. Las pruebas deben poder ejecutarse con un comando documentado y no deben depender de datos reales ni contaminar la base de datos de desarrollo.

**RNF-07 — Ejecución y documentación.** La aplicación se ejecutará en local. El README incluirá los requisitos, la instalación, el comando de inicio, las pruebas, el funcionamiento, las decisiones técnicas, las limitaciones y el uso de IA.

**RNF-08 — Usabilidad.** La interfaz debe presentar un formulario comprensible, un listado legible, el estado de cada reparación y mensajes claros de éxito o error. Debe ser posible completar las operaciones principales sin conocimientos técnicos. Se comprobará mediante una prueba manual documentada.

**RNF-09 — Límite de dedicación.** El desarrollo debe ajustarse a un máximo de tres horas. Se priorizarán los requisitos funcionales, la validación, las pruebas esenciales y una entrega reproducible frente a las mejoras cosméticas.

## 6. Fuera de alcance

Quedan fuera del prototipo los siguientes elementos:

- Autenticación, gestión de cuentas, roles y permisos de usuarios.
- Almacenamiento de nombres, teléfonos, direcciones de correo u otros datos personales reales.
- Gestión completa de fichas de clientes.
- Facturación, presupuestos, pagos, inventario y proveedores de piezas.
- Notificaciones por correo electrónico, SMS u otros canales.
- Subida de fotografías o documentos.
- Búsqueda, filtros, paginación y exportación de informes.
- Edición de los datos de una orden (código de cliente, bicicleta y problema); solo se puede cambiar su estado.
- Eliminación de órdenes e historial de cambios.
- Despliegue público, servicios en la nube, APIs externas o infraestructura de producción.

Estos elementos no son necesarios para demostrar los flujos solicitados y aumentarían el tiempo y la complejidad sin aportar valor proporcional al caso práctico.

## 7. Supuestos y decisiones

**SD-01 — Aplicación web local.** Se interpreta que una pequeña aplicación web que funciona en local satisface el requisito de una herramienta sencilla. No se requiere publicación en internet.

**SD-02 — Persistencia.** Aunque el enunciado permite mantener los datos en memoria o guardarlos localmente, se elige SQLite para que las órdenes sobrevivan al reinicio y demostrar una persistencia sencilla.

**SD-03 — Identificador.** El identificador será un entero autoincremental generado por SQLite. No se necesita que sea un código público personalizado. Al ser creciente, también sirve para ordenar el listado sin guardar fechas.

**SD-04 — Código de cliente.** El sistema no tendrá una entidad de cliente independiente en esta versión. Se guardará únicamente el código ficticio asociado a la orden. Se usa el formato cerrado `CLI-0000` porque un texto libre no permitiría garantizar que el campo no contenga datos personales.

**SD-05 — Límites de campos.** Los límites de 3 a 120 y de 3 a 500 caracteres se adoptan como decisiones prácticas del prototipo: el mínimo evita descripciones sin contenido útil. Se podrán ajustar si se obtiene nueva información, sin cambiar los requisitos esenciales.

**SD-06 — Transiciones de estado.** Cualquier estado puede cambiarse a cualquiera de los tres estados válidos. No se impone que una reparación pase obligatoriamente por todos ellos. Elegir el estado actual se trata como una operación sin cambios, no como un error.

**SD-07 — Tratamiento de errores.** Los errores previsibles se comunicarán con mensajes comprensibles que indiquen qué ha fallado y, en los formularios, qué campo corregir. No se mostrarán trazas técnicas al usuario. Se usarán los códigos HTTP 422 (datos no válidos, respuesta estándar de FastAPI) y 404 (orden inexistente).

**SD-08 — Privacidad y permisos.** La ausencia de autenticación se acepta exclusivamente porque el ejercicio es un prototipo local con datos ficticios. Antes de utilizarlo con datos reales o en un entorno compartido sería necesario diseñar controles de acceso y medidas de protección adecuadas.

**SD-09 — Uso de IA.** Claude Code podrá utilizarse para planificar, implementar, preparar pruebas y revisar el código. La persona responsable revisará los cambios, ejecutará las comprobaciones y documentará qué herramientas utilizó y qué resultados verificó.

**SD-10 — Criterio de finalización.** El proyecto se considerará terminado cuando los requisitos RF-01 a RF-04 estén implementados, las pruebas esenciales se hayan ejecutado, la aplicación funcione localmente y las instrucciones de ejecución y las decisiones principales estén documentadas.

Si algún requisito no queda terminado dentro del límite de tiempo, se documentará expresamente en el README junto con la forma prevista de completarlo.
