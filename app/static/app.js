"use strict";

// Los datos se insertan siempre con textContent, nunca con innerHTML,
// para que ningún texto pueda ejecutarse como código en la página (RNF-04).

const ESTADOS = ["Pendiente", "En reparación", "Terminada"];

const MENSAJE_CAMPO = {
  codigo_cliente: "Usa el formato CLI-0000, por ejemplo CLI-0042.",
  descripcion_bici: "Describe la bicicleta con entre 3 y 120 caracteres.",
  problema: "Describe el problema con entre 3 y 500 caracteres.",
};

const $ = (id) => document.getElementById(id);

async function pedir(ruta, opciones = {}) {
  const respuesta = await fetch(ruta, {
    ...opciones,
    headers: { "Content-Type": "application/json" },
  });
  const cuerpo = await respuesta.json().catch(() => null);
  return { ok: respuesta.ok, status: respuesta.status, cuerpo };
}

function mostrarMensaje(texto, tipo = "ok") {
  const mensaje = $("mensaje");
  mensaje.textContent = texto;
  mensaje.dataset.tipo = tipo;
}

function errorDeConexion() {
  mostrarMensaje("No se ha podido contactar con el servidor. Comprueba que está en marcha.", "error");
}

// --- Listado ---

async function cargarOrdenes() {
  let resultado;
  try {
    resultado = await pedir("/api/ordenes");
  } catch {
    errorDeConexion();
    return;
  }
  const ordenes = resultado.cuerpo ?? [];
  $("cuerpo-tabla").replaceChildren(...ordenes.map(filaOrden));
  $("vacio").hidden = ordenes.length > 0;
}

function celda(contenido, etiqueta) {
  const td = document.createElement("td");
  td.dataset.etiqueta = etiqueta;
  if (contenido instanceof Node) td.append(contenido);
  else td.textContent = contenido;
  return td;
}

function etiquetaEstado(estado) {
  const span = document.createElement("span");
  span.className = "estado";
  span.dataset.estado = estado;
  span.textContent = estado;
  return span;
}

function selectorEstado(orden) {
  const formulario = document.createElement("form");
  formulario.className = "cambio";

  const selector = document.createElement("select");
  selector.setAttribute("aria-label", `Nuevo estado de la orden ${orden.id}`);
  for (const estado of ESTADOS) {
    const opcion = new Option(estado, estado, false, estado === orden.estado);
    selector.append(opcion);
  }

  const boton = document.createElement("button");
  boton.type = "submit";
  boton.textContent = "Cambiar";

  formulario.append(selector, boton);
  formulario.addEventListener("submit", (evento) => {
    evento.preventDefault();
    cambiarEstado(orden, selector.value, boton);
  });
  return formulario;
}

function filaOrden(orden) {
  const fila = document.createElement("tr");
  fila.append(
    celda(`#${orden.id}`, "Nº"),
    celda(orden.codigo_cliente, "Cliente"),
    celda(orden.descripcion_bici, "Bicicleta"),
    celda(orden.problema, "Problema"),
    celda(etiquetaEstado(orden.estado), "Estado"),
    celda(selectorEstado(orden), "Cambiar estado"),
  );
  return fila;
}

// --- Cambiar estado ---

async function cambiarEstado(orden, nuevo, boton) {
  boton.disabled = true;
  let resultado;
  try {
    resultado = await pedir(`/api/ordenes/${orden.id}/estado`, {
      method: "PATCH",
      body: JSON.stringify({ estado: nuevo }),
    });
  } catch {
    errorDeConexion();
    boton.disabled = false;
    return;
  }

  if (!resultado.ok) {
    const detalle = typeof resultado.cuerpo?.detail === "string" ? resultado.cuerpo.detail : "";
    mostrarMensaje(detalle || "No se ha podido cambiar el estado.", "error");
  } else if (nuevo === orden.estado) {
    mostrarMensaje(`Sin cambios: la orden #${orden.id} ya estaba en «${nuevo}».`);
  } else {
    mostrarMensaje(`Orden #${orden.id}: estado cambiado a «${nuevo}».`);
  }
  await cargarOrdenes();
}

// --- Crear orden ---

function limpiarErrores(formulario) {
  for (const campo of Object.keys(MENSAJE_CAMPO)) {
    formulario.elements[campo].removeAttribute("aria-invalid");
    $(`error-${campo}`).textContent = "";
  }
}

function marcarErrores(formulario, campos) {
  for (const campo of campos) {
    formulario.elements[campo].setAttribute("aria-invalid", "true");
    $(`error-${campo}`).textContent = MENSAJE_CAMPO[campo];
  }
  formulario.elements[campos[0]].focus();
}

async function crearOrden(evento) {
  evento.preventDefault();
  const formulario = evento.currentTarget;
  const boton = formulario.querySelector("button[type=submit]");
  limpiarErrores(formulario);
  boton.disabled = true;

  let resultado;
  try {
    const datos = Object.fromEntries(new FormData(formulario));
    resultado = await pedir("/api/ordenes", { method: "POST", body: JSON.stringify(datos) });
  } catch {
    errorDeConexion();
    boton.disabled = false;
    return;
  }
  boton.disabled = false;

  if (resultado.ok) {
    formulario.reset();
    mostrarMensaje(`Orden #${resultado.cuerpo.id} creada.`);
    await cargarOrdenes();
    return;
  }

  // 422: el servidor indica qué campos son incorrectos. Se conserva lo escrito.
  const campos = (Array.isArray(resultado.cuerpo?.detail) ? resultado.cuerpo.detail : [])
    .map((error) => error.loc?.at(-1))
    .filter((campo) => campo in MENSAJE_CAMPO);
  if (campos.length) {
    marcarErrores(formulario, [...new Set(campos)]);
  } else {
    mostrarMensaje("No se ha podido crear la orden.", "error");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  $("form-nueva").addEventListener("submit", crearOrden);
  cargarOrdenes();
});
