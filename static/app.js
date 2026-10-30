/**
 * Controlador Frontend SPA - Autos Colombia 24/7 (Cobalt Bay OS)
 * Iteraciones 1 y 2 Unificadas:
 *  - Control de Entrada, Salida y Novedades 24/7
 *  - Autenticación SHA-256 y Control de Acceso Basado en Roles (RBAC)
 *  - Gestión CRUD de Usuarios y Roles (ADMIN / OPERARIO / AUDITOR)
 *  - Gestión CRUD, Mantenimiento y Reubicación Transaccional de 80 Celdas
 *  - Gestión CRUD de Clientes Abonados y Auditoría Inmutable
 * Asignatura: Ingeniería de Software - PREICA2602B020053 | Grupo 25
 */

// Estado reactivo global del cliente SPA
const estadoApp = {
  sesion: {
    id: 1,
    username: "admin",
    nombre_completo: "Camilo Alberto Palacios Turriago",
    rol: "ADMIN",
    cargo: "Administrador General",
    permisos: [
      "OPERACION_ACCESO",
      "MANTENIMIENTO_CELDAS",
      "CRUD_CELDAS",
      "GESTION_USUARIOS",
      "GESTION_ABONADOS",
      "CONSULTA_AUDITORIA",
    ],
  },
  resumen: null,
  celdasCrud: [],
  usuarios: [],
  abonados: [],
  filtroMapa: "TODOS",
  celdaSeleccionada: null,
  vehiculoConsultado: null,
};

// ============================================================================
// UTILIDADES DE INTERFAZ, FORMATO Y NOTIFICACIONES FLOTANTES (SIN ALERT/PROMPT)
// ============================================================================

function escaparHtml(valor) {
  if (valor === null || valor === undefined) return "";
  return String(valor)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatearPlacaVisual(placa) {
  if (!placa) return "";
  const limpia = String(placa).replace(/[-\s]/g, "").toUpperCase();
  if (limpia.length === 6) {
    return `${limpia.slice(0, 3)}-${limpia.slice(3)}`;
  }
  return limpia;
}

function formatearInputPlaca(input) {
  let limpia = input.value.replace(/[^a-zA-Z0-9]/g, "").toUpperCase();
  if (limpia.length > 6) limpia = limpia.slice(0, 6);
  if (limpia.length > 3) {
    input.value = `${limpia.slice(0, 3)}-${limpia.slice(3)}`;
  } else {
    input.value = limpia;
  }
}

function formatearMonedaCOP(valor) {
  const num = Number(valor || 0);
  return "$" + num.toLocaleString("es-CO", { maximumFractionDigits: 0 });
}

function obtenerTerminalActiva() {
  const sel = document.getElementById("select-puerta-operario");
  return sel ? sel.value : "Puerta 1 - Norte";
}

function tienePermiso(permiso) {
  return Array.isArray(estadoApp.sesion.permisos) && estadoApp.sesion.permisos.includes(permiso);
}

function mostrarNotificacion(titulo, detalle = "", tipo = "exito") {
  const cont = document.getElementById("toast-container");
  if (!cont) return;

  const estilos = {
    exito: "bg-emerald-950/95 border-emerald-500 text-emerald-50",
    error: "bg-rose-950/95 border-rose-500 text-rose-50",
    alerta: "bg-amber-950/95 border-amber-500 text-amber-50",
    info: "bg-slate-900/95 border-blue-500 text-blue-50",
  };
  const etiquetas = {
    exito: "OK",
    error: "ERROR",
    alerta: "AVISO",
    info: "INFO",
  };

  const toast = document.createElement("div");
  toast.className = `pointer-events-auto border-l-4 rounded-xl px-4 py-3 shadow-xl transition-all duration-300 flex items-start justify-between gap-3 ${estilos[tipo] || estilos.info}`;
  toast.innerHTML = `
    <div class="space-y-0.5">
      <div class="flex items-center gap-2">
        <span class="text-[10px] font-black uppercase px-1.5 py-0.5 rounded bg-white/15">${etiquetas[tipo] || "INFO"}</span>
        <span class="text-xs font-extrabold">${escaparHtml(titulo)}</span>
      </div>
      ${detalle ? `<p class="text-[11px] opacity-90 leading-snug">${escaparHtml(detalle)}</p>` : ""}
    </div>
    <button onclick="this.parentElement.remove()" class="text-xs font-bold opacity-70 hover:opacity-100">&times;</button>
  `;
  cont.appendChild(toast);

  setTimeout(() => {
    if (toast.parentElement) toast.remove();
  }, 4800);
}

function abrirModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove("hidden");
}

function cerrarModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add("hidden");
}

async function apiGet(ruta) {
  const resp = await fetch(ruta, { headers: { Accept: "application/json" } });
  const data = await resp.json();
  return { ok: resp.ok, status: resp.status, data };
}

async function apiPost(ruta, payload) {
  const resp = await fetch(ruta, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await resp.json();
  return { ok: resp.ok, status: resp.status, data };
}

// ============================================================================
// NAVEGACIÓN DE VISTAS Y SINCRONIZACIÓN DE PRIVILEGIOS RBAC
// ============================================================================

function cambiarVista(vistaId) {
  document.querySelectorAll(".view-container").forEach((sec) => {
    sec.classList.toggle("active", sec.id === vistaId);
  });

  document.querySelectorAll(".nav-tab").forEach((btn) => {
    const activo = btn.getAttribute("data-target") === vistaId;
    btn.className = activo
      ? "nav-tab px-2.5 py-1 rounded-md text-xs font-bold transition-all bg-blue-600 text-white shadow-sm"
      : "nav-tab px-2.5 py-1 rounded-md text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800 transition-all";
  });

  const mapaSide = {
    "view-control": "side-link-control",
    "view-mapa": "side-link-mapa",
    "view-celdas-crud": "side-link-celdas-crud",
    "view-usuarios": "side-link-usuarios",
    "view-abonados": "side-link-abonados",
    "view-auditoria": "side-link-auditoria",
  };
  document.querySelectorAll(".sidebar-link").forEach((btn) => {
    const activo = btn.id === mapaSide[vistaId];
    btn.className = activo
      ? "sidebar-link flex items-center gap-2.5 px-3 py-2 rounded-xl text-left transition-all bg-blue-700 text-white shadow-sm"
      : "sidebar-link flex items-center gap-2.5 px-3 py-2 rounded-xl text-left transition-all text-slate-600 hover:bg-slate-100";
  });

  if (vistaId === "view-celdas-crud") {
    cargarTablaCeldasCrud();
    cargarHistorialCeldas();
  } else if (vistaId === "view-usuarios") {
    cargarTablaUsuarios();
  } else if (vistaId === "view-abonados") {
    cargarAbonadosServidor();
  } else if (vistaId === "view-auditoria") {
    cargarAuditoria();
  } else if (vistaId === "view-mapa") {
    renderizarMapaCeldas();
  }
}

function aplicarPermisosRBAC() {
  const rol = estadoApp.sesion.rol;
  const esAdmin = tienePermiso("GESTION_USUARIOS") && tienePermiso("CRUD_CELDAS");
  const puedeOperar = tienePermiso("OPERACION_ACCESO");

  const lblUser = document.getElementById("header-user-name");
  const badgeRol = document.getElementById("badge-rol-activo");
  const statusBar = document.getElementById("rbac-status-bar");
  const statusText = document.getElementById("rbac-status-text");
  const footerUser = document.getElementById("footer-user-tag");

  if (lblUser) lblUser.textContent = estadoApp.sesion.nombre_completo;
  if (footerUser) footerUser.textContent = `${rol}: ${estadoApp.sesion.nombre_completo}`;

  if (badgeRol) {
    badgeRol.textContent = rol;
    if (rol === "ADMIN") {
      badgeRol.className = "bg-purple-600 text-white px-1.5 py-0.5 rounded text-[10px] font-black uppercase";
    } else if (rol === "OPERARIO") {
      badgeRol.className = "bg-blue-600 text-white px-1.5 py-0.5 rounded text-[10px] font-black uppercase";
    } else {
      badgeRol.className = "bg-emerald-600 text-white px-1.5 py-0.5 rounded text-[10px] font-black uppercase";
    }
  }

  if (statusBar && statusText) {
    if (rol === "ADMIN") {
      statusBar.className = "bg-purple-950/90 text-purple-100 px-5 py-1.5 text-[11px] flex items-center justify-between border-b border-purple-800/50 flex-shrink-0";
      statusText.innerHTML = `Rol activo: <strong>ADMIN (${escaparHtml(estadoApp.sesion.username)})</strong> — Control total habilitado (Acceso 24/7, CRUD Usuarios y Roles, CRUD Estructural de 80 Celdas, Mantenimiento, Reubicación y Auditoría).`;
    } else if (rol === "OPERARIO") {
      statusBar.className = "bg-blue-950/90 text-blue-100 px-5 py-1.5 text-[11px] flex items-center justify-between border-b border-blue-800/50 flex-shrink-0";
      statusText.innerHTML = `Rol activo: <strong>OPERARIO (${escaparHtml(estadoApp.sesion.username)})</strong> — Operación de Cabina 24/7, Mantenimiento/Reubicación de Celdas y Padrón de Abonados activos. <em>CRUD de Usuarios y alta/baja estructural de Celdas restringidos (HTTP 403).</em>`;
    } else {
      statusBar.className = "bg-emerald-950/90 text-emerald-100 px-5 py-1.5 text-[11px] flex items-center justify-between border-b border-emerald-800/50 flex-shrink-0";
      statusText.innerHTML = `Rol activo: <strong>AUDITOR (${escaparHtml(estadoApp.sesion.username)})</strong> — Modo Supervisión de Solo Lectura. Todas las operaciones de escritura están protegidas por RBAC (HTTP 403).`;
    }
  }

  document.querySelectorAll(".rbac-admin-only").forEach((el) => {
    el.disabled = !esAdmin;
    el.classList.toggle("opacity-40", !esAdmin);
    el.classList.toggle("cursor-not-allowed", !esAdmin);
    el.title = esAdmin ? "" : "Restringido por RBAC: Requiere rol ADMIN";
  });

  document.querySelectorAll(".rbac-operacion").forEach((el) => {
    el.disabled = !puedeOperar;
    el.classList.toggle("opacity-40", !puedeOperar);
    el.classList.toggle("cursor-not-allowed", !puedeOperar);
    el.title = puedeOperar ? "" : "Restringido por RBAC: Rol AUDITOR es de solo lectura";
  });
}

// ============================================================================
// AUTENTICACIÓN SHA-256 Y SESIÓN DE USUARIO (ITERACIÓN 2)
// ============================================================================

function abrirModalLogin() {
  const errBox = document.getElementById("login-error-box");
  if (errBox) errBox.classList.add("hidden");
  abrirModal("modal-login");
}

function autocompletarLogin(username, password) {
  document.getElementById("login-username").value = username;
  document.getElementById("login-password").value = password;
  const errBox = document.getElementById("login-error-box");
  if (errBox) errBox.classList.add("hidden");
}

async function ejecutarLogin() {
  const username = document.getElementById("login-username").value.trim();
  const password = document.getElementById("login-password").value;
  const errBox = document.getElementById("login-error-box");

  const { ok, data } = await apiPost("/api/auth/login", {
    username,
    password,
    terminal: obtenerTerminalActiva(),
  });

  if (!ok || !data.success) {
    if (errBox) {
      errBox.textContent = data.mensaje || "Credenciales inválidas.";
      errBox.classList.remove("hidden");
    }
    mostrarNotificacion("Autenticación Rechazada", data.mensaje || "Error de credenciales", "error");
    return;
  }

  estadoApp.sesion = data.usuario;
  cerrarModal("modal-login");
  aplicarPermisosRBAC();
  await cargarResumenGeneral();
  cargarTablaCeldasCrud();
  cargarTablaUsuarios();
  mostrarNotificacion("Sesión Iniciada (SHA-256)", data.mensaje, "exito");
}

// ============================================================================
// CARGA DE MÉTRICAS Y RESUMEN OPERATIVO EN TIEMPO REAL
// ============================================================================

async function cargarResumenGeneral() {
  const { ok, data } = await apiGet("/api/resumen");
  if (!ok) return;

  estadoApp.resumen = data;
  estadoApp.abonados = data.abonados || [];

  const totalCap = data.capacidad_total || 80;
  const ocupadas = data.total_ocupadas || 0;
  const libres = data.total_libres || 0;
  const mant = data.total_mantenimiento || 0;
  const pct = totalCap > 0 ? Math.round((ocupadas / totalCap) * 100) : 0;

  document.getElementById("side-badge-libres").textContent = `• ${libres} Libres`;
  document.getElementById("side-capacidad-total").textContent = `${totalCap} Celdas`;
  document.getElementById("side-ocupadas-total").textContent = `${ocupadas} Ocupadas`;
  document.getElementById("side-progress-bar").style.width = `${pct}%`;
  document.getElementById("side-mantenimiento-total").textContent = `${mant} Celdas`;

  document.getElementById("top-carros-libres").textContent = `${data.carros.libres} Libres`;
  document.getElementById("top-carros-total").textContent = `/ ${data.carros.total}`;
  document.getElementById("top-motos-libres").textContent = `${data.motos.libres} Libres`;
  document.getElementById("top-motos-total").textContent = `/ ${data.motos.total}`;

  document.getElementById("stat-crud-total").textContent = String(totalCap);
  document.getElementById("stat-crud-sub").textContent = `${data.carros.total} Carros / ${data.motos.total} Motos`;
  document.getElementById("stat-crud-disponibles").textContent = String(libres);
  document.getElementById("stat-crud-ocupadas").textContent = String(ocupadas);
  document.getElementById("stat-crud-mantenimiento").textContent = String(mant);

  renderizarVehiculosAdentro(data.vehiculos_adentro || []);
  renderizarMapaCeldas();
  renderizarTablaAbonados(estadoApp.abonados);
}

// ============================================================================
// VISTA 1: CONTROL DE ENTRADA, SALIDA Y NOVEDADES (ITERACIÓN 1 + 2)
// ============================================================================

function probarPlaca(placa) {
  const input = document.getElementById("input-placa");
  input.value = placa;
  consultarPlaca();
}

async function consultarPlaca() {
  const placa = document.getElementById("input-placa").value.trim();
  const cont = document.getElementById("contenedor-ficha-vehiculo");
  const btn = document.getElementById("btn-autorizar-ingreso");

  if (!placa) {
    mostrarNotificacion("Placa requerida", "Digite una placa para verificar su estado de mensualidad.", "alerta");
    return;
  }

  const { ok, status, data } = await apiGet(`/api/vehiculo?placa=${encodeURIComponent(placa)}`);
  if (!ok || status === 404) {
    estadoApp.vehiculoConsultado = null;
    cont.innerHTML = `
      <div class="bg-rose-50 border border-rose-200 rounded-xl p-4 text-xs text-rose-900 space-y-1">
        <div class="font-extrabold text-rose-800">VEHÍCULO NO REGISTRADO EN EL PADRÓN (${escaparHtml(formatearPlacaVisual(placa))})</div>
        <p>Autos Colombia opera exclusivamente por mensualidad. Registre primero al cliente en la pestaña <strong>5. Abonados</strong>.</p>
      </div>
    `;
    btn.disabled = true;
    btn.classList.add("opacity-40", "cursor-not-allowed");
    return;
  }

  estadoApp.vehiculoConsultado = data;
  const m = data.mensualidad;
  const alDia = m && m.al_dia;
  const adentro = data.esta_adentro;

  let badgeEstado = "";
  if (!data.activo) {
    badgeEstado = `<span class="bg-slate-200 text-slate-800 px-2.5 py-0.5 rounded-full text-[11px] font-black">VEHÍCULO INACTIVO</span>`;
  } else if (adentro) {
    badgeEstado = `<span class="bg-indigo-100 text-indigo-800 px-2.5 py-0.5 rounded-full text-[11px] font-black">YA ESTÁ ADENTRO (${escaparHtml(data.registro_actual.celda_codigo)})</span>`;
  } else if (alDia) {
    badgeEstado = `<span class="bg-emerald-100 text-emerald-800 px-2.5 py-0.5 rounded-full text-[11px] font-black">MENSUALIDAD VIGENTE (${m.dias_restantes} días)</span>`;
  } else {
    badgeEstado = `<span class="bg-rose-100 text-rose-800 px-2.5 py-0.5 rounded-full text-[11px] font-black">EN MORA • ACCESO BLOQUEADO</span>`;
  }

  const colorCaja = alDia && !adentro ? "bg-emerald-50/60 border-emerald-200" : adentro ? "bg-indigo-50/60 border-indigo-200" : "bg-rose-50/70 border-rose-200";

  cont.innerHTML = `
    <div class="${colorCaja} border rounded-xl p-4 space-y-2.5 text-xs">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <div class="flex items-center gap-2">
          <span class="bg-slate-900 text-amber-300 font-mono-plate font-extrabold px-2.5 py-1 rounded-lg text-sm border border-amber-400/40">${escaparHtml(formatearPlacaVisual(data.placa))}</span>
          <span class="font-extrabold text-slate-900">${escaparHtml(data.marca)} ${escaparHtml(data.modelo)} (${escaparHtml(data.color)})</span>
          <span class="text-[10px] font-black px-2 py-0.5 rounded bg-white border border-slate-200">${escaparHtml(data.tipo_vehiculo)}</span>
        </div>
        ${badgeEstado}
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] text-slate-700 pt-1 border-t border-slate-200/70">
        <div><strong>Titular:</strong> ${escaparHtml(data.propietario_nombre)} (CC ${escaparHtml(data.propietario_doc)})</div>
        <div><strong>Contacto:</strong> ${escaparHtml(data.propietario_telefono)}</div>
        <div><strong>Vencimiento Mensualidad:</strong> ${m ? escaparHtml(m.fecha_vencimiento) : "Sin contrato"}</div>
        <div><strong>Tarifa Plana:</strong> ${m ? formatearMonedaCOP(m.valor_pagado) : "N/A"}</div>
      </div>
    </div>
  `;

  const habilitarBoton = alDia && !adentro && tienePermiso("OPERACION_ACCESO");
  btn.disabled = !habilitarBoton;
  btn.classList.toggle("opacity-40", !habilitarBoton);
  btn.classList.toggle("cursor-not-allowed", !habilitarBoton);
}

async function ejecutarIngreso() {
  if (!tienePermiso("OPERACION_ACCESO")) {
    mostrarNotificacion("Acceso Denegado (RBAC)", "Su rol actual no tiene permisos para abrir barreras.", "error");
    return;
  }

  const placa = document.getElementById("input-placa").value.trim();
  const observaciones = document.getElementById("input-observaciones-ingreso").value.trim();
  const puerta = obtenerTerminalActiva();

  const { ok, data } = await apiPost("/api/ingreso", {
    placa,
    observaciones,
    puerta,
    usuario_id: estadoApp.sesion.id,
  });

  if (!ok || !data.success) {
    mostrarNotificacion("Ingreso Denegado", data.mensaje || "No fue posible autorizar el ingreso.", "error");
    await consultarPlaca();
    return;
  }

  document.getElementById("input-observaciones-ingreso").value = "";
  mostrarNotificacion(
    `Celda Asignada: ${data.celda_asignada} (${data.zona})`,
    `${data.mensaje} Ubicación: Piso ${data.piso}.`,
    "exito"
  );
  await cargarResumenGeneral();
  await consultarPlaca();
}

function renderizarVehiculosAdentro(lista) {
  const badge = document.getElementById("contador-adentro-badge");
  const cont = document.getElementById("lista-vehiculos-adentro");
  if (badge) badge.textContent = String(lista.length);
  if (!cont) return;

  if (lista.length === 0) {
    cont.innerHTML = `
      <div class="text-center py-10 bg-slate-50 rounded-xl border border-dashed border-slate-200 text-xs text-slate-500">
        No hay vehículos estacionados dentro del parqueadero en este instante.<br/>
        <span class="text-[11px] text-slate-400">Las 80 celdas reglamentarias están listas para operación.</span>
      </div>
    `;
    return;
  }

  const puedeOperar = tienePermiso("OPERACION_ACCESO");
  const disClass = puedeOperar ? "" : "opacity-40 cursor-not-allowed";

  cont.innerHTML = lista
    .map(
      (v) => `
      <div class="bg-slate-50 hover:bg-slate-100/80 border border-slate-200 rounded-xl p-3.5 space-y-2 transition-colors">
        <div class="flex items-center justify-between gap-2">
          <div class="flex items-center gap-2">
            <span class="bg-slate-900 text-amber-300 font-mono-plate font-extrabold px-2 py-0.5 rounded text-xs">${escaparHtml(formatearPlacaVisual(v.vehiculo_placa))}</span>
            <span class="bg-rose-100 text-rose-800 font-mono-plate font-black px-2 py-0.5 rounded text-xs">Celda ${escaparHtml(v.celda_codigo)}</span>
            <span class="text-[10px] font-bold text-slate-500">${escaparHtml(v.tipo_vehiculo)}</span>
          </div>
          <span class="text-[10px] font-semibold text-slate-500">${escaparHtml(v.fecha_ingreso)}</span>
        </div>
        <div class="text-[11px] text-slate-700">
          <strong>${escaparHtml(v.marca)} ${escaparHtml(v.modelo)}</strong> (${escaparHtml(v.color)}) • Titular: ${escaparHtml(v.conductor)}
        </div>
        ${v.observaciones ? `<div class="text-[10px] text-slate-500 bg-white border border-slate-200/80 rounded-lg px-2.5 py-1">${escaparHtml(v.observaciones)}</div>` : ""}
        <div class="flex flex-wrap items-center justify-end gap-1.5 pt-1">
          <button ${puedeOperar ? "" : "disabled"} onclick="abrirModalNovedad('${escaparHtml(v.vehiculo_placa)}', '${escaparHtml(v.celda_codigo)}')" class="${disClass} bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-200 font-bold px-2.5 py-1 rounded-lg text-[11px]">
            + Novedad
          </button>
          <button ${puedeOperar ? "" : "disabled"} onclick="abrirModalReubicarConPlaca('${escaparHtml(v.vehiculo_placa)}')" class="${disClass} bg-indigo-50 hover:bg-indigo-100 text-indigo-800 border border-indigo-200 font-bold px-2.5 py-1 rounded-lg text-[11px]">
            Reubicar Celda
          </button>
          <button ${puedeOperar ? "" : "disabled"} onclick="abrirModalSalida('${escaparHtml(v.vehiculo_placa)}', '${escaparHtml(v.celda_codigo)}')" class="${disClass} bg-rose-600 hover:bg-rose-700 text-white font-bold px-3 py-1 rounded-lg text-[11px] shadow-sm">
            Dar Salida
          </button>
        </div>
      </div>
    `
    )
    .join("");
}

function abrirModalSalida(placa, celda) {
  document.getElementById("modal-salida-titulo").textContent = "Confirmar Salida y Liberación de Celda";
  document.getElementById("modal-salida-placa").value = placa;
  document.getElementById("modal-salida-accion").value = "SALIDA";
  document.getElementById("modal-salida-sub").innerHTML = `Se cerrará el ciclo de acceso del vehículo <strong class="font-mono-plate">${escaparHtml(formatearPlacaVisual(placa))}</strong> y la celda <strong>${escaparHtml(celda)}</strong> pasará inmediatamente a estado <strong>DISPONIBLE</strong>.`;
  document.getElementById("modal-salida-obs").value = "Sin novedades físicas a la salida";
  const btn = document.getElementById("btn-confirmar-salida-modal");
  btn.textContent = "Liberar Celda y Abrir Barrera";
  btn.className = "px-4 py-2 rounded-xl text-xs font-bold bg-rose-600 hover:bg-rose-700 text-white";
  abrirModal("modal-salida");
}

function abrirModalNovedad(placa, celda) {
  document.getElementById("modal-salida-titulo").textContent = "Registrar Novedad Física / Seguridad (HU-03)";
  document.getElementById("modal-salida-placa").value = placa;
  document.getElementById("modal-salida-accion").value = "NOVEDAD";
  document.getElementById("modal-salida-sub").innerHTML = `Agregue un reporte de seguridad sobre el vehículo <strong class="font-mono-plate">${escaparHtml(formatearPlacaVisual(placa))}</strong> estacionado en la celda <strong>${escaparHtml(celda)}</strong>.`;
  document.getElementById("modal-salida-obs").value = "";
  document.getElementById("modal-salida-obs").placeholder = "Ej: Luces estacionarias encendidas, espejo plegado...";
  const btn = document.getElementById("btn-confirmar-salida-modal");
  btn.textContent = "Guardar Novedad en Bitácora";
  btn.className = "px-4 py-2 rounded-xl text-xs font-bold bg-amber-600 hover:bg-amber-700 text-white";
  abrirModal("modal-salida");
}

async function confirmarAccionSalidaNovedad() {
  const placa = document.getElementById("modal-salida-placa").value;
  const accion = document.getElementById("modal-salida-accion").value;
  const obs = document.getElementById("modal-salida-obs").value.trim();

  if (accion === "NOVEDAD") {
    const { ok, data } = await apiPost("/api/novedad", {
      placa,
      novedad: obs,
      usuario_id: estadoApp.sesion.id,
    });
    if (!ok || !data.success) {
      mostrarNotificacion("No se pudo guardar novedad", data.mensaje || "Error", "error");
      return;
    }
    cerrarModal("modal-salida");
    mostrarNotificacion("Novedad Registrada", data.mensaje, "exito");
    await cargarResumenGeneral();
  } else {
    const { ok, data } = await apiPost("/api/salida", {
      placa,
      observaciones_salida: obs,
      puerta: obtenerTerminalActiva(),
      usuario_id: estadoApp.sesion.id,
    });
    if (!ok || !data.success) {
      mostrarNotificacion("Error al dar salida", data.mensaje || "Error", "error");
      return;
    }
    cerrarModal("modal-salida");
    mostrarNotificacion(
      `Celda ${data.celda_liberada} Liberada`,
      `${data.mensaje} Permanencia total: ${data.tiempo_permanencia}.`,
      "exito"
    );
    await cargarResumenGeneral();
    if (estadoApp.vehiculoConsultado && estadoApp.vehiculoConsultado.placa === placa) {
      await consultarPlaca();
    }
  }
}

// ============================================================================
// VISTA 2: MAPA INTERACTIVO DE 80 CELDAS
// ============================================================================

function filtrarMapa(filtro) {
  estadoApp.filtroMapa = filtro;
  document.querySelectorAll(".filtro-btn").forEach((b) => {
    const activo = b.getAttribute("data-filtro") === filtro;
    b.className = activo
      ? "filtro-btn px-2.5 py-1 rounded-lg bg-blue-600 text-white"
      : "filtro-btn px-2.5 py-1 rounded-lg text-slate-600 hover:bg-slate-100";
  });
  renderizarMapaCeldas();
}

function renderizarMapaCeldas() {
  const grid = document.getElementById("grid-celdas");
  if (!grid || !estadoApp.resumen) return;

  const celdas = (estadoApp.resumen.celdas || []).filter((c) => {
    if (estadoApp.filtroMapa === "CARRO") return c.tipo_permitido === "CARRO";
    if (estadoApp.filtroMapa === "MOTO") return c.tipo_permitido === "MOTO";
    if (estadoApp.filtroMapa === "MANTENIMIENTO") return c.estado === "MANTENIMIENTO" || c.estado === "INACTIVA";
    return true;
  });

  grid.innerHTML = celdas
    .map((c) => {
      let estilo = "bg-emerald-50 border-emerald-300 text-emerald-900 hover:bg-emerald-100";
      let sub = c.tipo_permitido === "MOTO" ? "MOTO" : "LIBRE";
      if (c.estado === "OCUPADA") {
        estilo = "bg-rose-50 border-rose-400 text-rose-900 hover:bg-rose-100 shadow-sm";
        sub = formatearPlacaVisual(c.vehiculo_placa || "OCUP");
      } else if (c.estado === "MANTENIMIENTO") {
        estilo = "bg-amber-50 border-amber-400 text-amber-900 hover:bg-amber-100";
        sub = "MANT.";
      } else if (c.estado === "INACTIVA") {
        estilo = "bg-slate-200 border-slate-400 text-slate-700 hover:bg-slate-300";
        sub = "INACT.";
      }
      const anillo = estadoApp.celdaSeleccionada === c.codigo ? "ring-2 ring-blue-600 scale-[1.03]" : "";
      return `
        <button onclick="seleccionarCelda('${escaparHtml(c.codigo)}')" class="border rounded-xl p-2 text-center transition-all ${estilo} ${anillo}">
          <div class="font-mono-plate font-extrabold text-[11px]">${escaparHtml(c.codigo)}</div>
          <div class="text-[9px] font-bold truncate mt-0.5">${escaparHtml(sub)}</div>
        </button>
      `;
    })
    .join("");

  if (estadoApp.celdaSeleccionada) {
    mostrarDetalleCeldaSeleccionada(estadoApp.celdaSeleccionada);
  }
}

function seleccionarCelda(codigo) {
  estadoApp.celdaSeleccionada = codigo;
  renderizarMapaCeldas();
  mostrarDetalleCeldaSeleccionada(codigo);
}

function mostrarDetalleCeldaSeleccionada(codigo) {
  const panel = document.getElementById("detalle-celda-seleccionada");
  if (!panel || !estadoApp.resumen) return;

  const c = (estadoApp.resumen.celdas || []).find((x) => x.codigo === codigo);
  if (!c) return;

  const puedeMant = tienePermiso("MANTENIMIENTO_CELDAS");
  const esAdmin = tienePermiso("CRUD_CELDAS");

  const badgeColor =
    c.estado === "DISPONIBLE"
      ? "bg-emerald-100 text-emerald-800"
      : c.estado === "OCUPADA"
      ? "bg-rose-100 text-rose-800"
      : c.estado === "MANTENIMIENTO"
      ? "bg-amber-100 text-amber-800"
      : "bg-slate-200 text-slate-800";

  panel.innerHTML = `
    <div class="text-left space-y-3 p-1">
      <div class="flex items-center justify-between border-b border-slate-200 pb-2.5">
        <div>
          <span class="font-mono-plate font-black text-lg text-slate-900">${escaparHtml(c.codigo)}</span>
          <span class="ml-1.5 text-[10px] font-bold px-2 py-0.5 rounded bg-white border border-slate-200">${escaparHtml(c.tipo_permitido)}</span>
        </div>
        <span class="px-2.5 py-0.5 rounded-full text-[10px] font-black ${badgeColor}">${escaparHtml(c.estado)}</span>
      </div>

      <div class="space-y-1 text-xs text-slate-700">
        <div><strong>Ubicación Física:</strong> ${escaparHtml(c.zona)} • Piso ${c.piso}</div>
        ${
          c.estado === "OCUPADA"
            ? `
          <div class="bg-rose-50 border border-rose-200 rounded-xl p-3 mt-2 space-y-1">
            <div class="font-extrabold text-rose-900">Ocupante Actual: ${escaparHtml(formatearPlacaVisual(c.vehiculo_placa))}</div>
            <div class="text-[11px] text-rose-800">${escaparHtml(c.marca || "")} ${escaparHtml(c.modelo || "")} (${escaparHtml(c.color || "")})</div>
            <div class="text-[11px] text-rose-700">Titular: ${escaparHtml(c.conductor || "")}</div>
          </div>
        `
            : ""
        }
        ${
          c.motivo_bloqueo
            ? `<div class="bg-amber-50 border border-amber-200 rounded-xl p-2.5 text-[11px] text-amber-900"><strong>Motivo técnico:</strong> ${escaparHtml(c.motivo_bloqueo)}</div>`
            : ""
        }
      </div>

      <div class="flex flex-wrap gap-2 pt-2 border-t border-slate-200">
        ${
          c.estado === "OCUPADA"
            ? `
            <button ${puedeMant ? "" : "disabled"} onclick="abrirModalReubicarConPlaca('${escaparHtml(c.vehiculo_placa)}')" class="${puedeMant ? "" : "opacity-40 cursor-not-allowed"} flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-3 rounded-xl text-xs">
              Reubicar Vehículo
            </button>
            <button ${puedeMant ? "" : "disabled"} onclick="abrirModalSalida('${escaparHtml(c.vehiculo_placa)}', '${escaparHtml(c.codigo)}')" class="${puedeMant ? "" : "opacity-40 cursor-not-allowed"} flex-1 bg-rose-600 hover:bg-rose-700 text-white font-bold py-2 px-3 rounded-xl text-xs">
              Dar Salida
            </button>
          `
            : `
            <button ${puedeMant ? "" : "disabled"} onclick="abrirModalEstadoCelda('${escaparHtml(c.codigo)}', '${escaparHtml(c.estado)}', '${escaparHtml(c.motivo_bloqueo || "")}')" class="${puedeMant ? "" : "opacity-40 cursor-not-allowed"} flex-1 bg-amber-600 hover:bg-amber-700 text-white font-bold py-2 px-3 rounded-xl text-xs">
              Estado / Mant.
            </button>
            <button ${esAdmin ? "" : "disabled"} onclick="abrirModalEditarCelda('${escaparHtml(c.codigo)}')" class="${esAdmin ? "" : "opacity-40 cursor-not-allowed"} bg-slate-800 hover:bg-slate-900 text-white font-bold py-2 px-3 rounded-xl text-xs">
              Editar CRUD
            </button>
          `
        }
      </div>
    </div>
  `;
}

// ============================================================================
// VISTA 3: GESTIÓN CRUD, MANTENIMIENTO Y REUBICACIÓN DE CELDAS (ITERACIÓN 2)
// ============================================================================

async function cargarTablaCeldasCrud() {
  const q = (document.getElementById("filtro-crud-busqueda")?.value || "").trim();
  const estado = document.getElementById("filtro-crud-estado")?.value || "";
  const tipo = document.getElementById("filtro-crud-tipo")?.value || "";

  const params = new URLSearchParams();
  if (q) params.set("q", q);
  if (estado) params.set("estado", estado);
  if (tipo) params.set("tipo", tipo);

  const { ok, data } = await apiGet(`/api/celdas?${params.toString()}`);
  if (!ok) return;

  estadoApp.celdasCrud = data.celdas || [];
  const lbl = document.getElementById("contador-celdas-filtradas");
  if (lbl) lbl.textContent = `${estadoApp.celdasCrud.length} registros`;

  const tbody = document.getElementById("tbody-celdas-crud");
  if (!tbody) return;

  const esAdmin = tienePermiso("CRUD_CELDAS");
  const puedeMant = tienePermiso("MANTENIMIENTO_CELDAS");

  tbody.innerHTML = estadoApp.celdasCrud
    .map((c) => {
      const badgeEst =
        c.estado === "DISPONIBLE"
          ? "bg-emerald-100 text-emerald-800"
          : c.estado === "OCUPADA"
          ? "bg-rose-100 text-rose-800"
          : c.estado === "MANTENIMIENTO"
          ? "bg-amber-100 text-amber-800"
          : "bg-slate-200 text-slate-700";

      const badgeTipo =
        c.tipo_permitido === "CARRO"
          ? "bg-blue-50 text-blue-700 border border-blue-200"
          : "bg-purple-50 text-purple-700 border border-purple-200";

      const ocupanteHtml = c.ocupante_placa
        ? `<span class="font-mono-plate font-bold text-rose-700">${escaparHtml(formatearPlacaVisual(c.ocupante_placa))}</span> <span class="text-[11px] text-slate-500">(${escaparHtml(c.ocupante_conductor || "")})</span>`
        : `<span class="text-slate-400">Libre</span>`;

      return `
        <tr class="hover:bg-slate-50">
          <td class="py-2.5 px-4 font-mono-plate font-extrabold text-slate-900">${escaparHtml(c.codigo)}</td>
          <td class="py-2.5 px-4"><span class="px-2 py-0.5 rounded text-[10px] font-black ${badgeTipo}">${escaparHtml(c.tipo_permitido)}</span></td>
          <td class="py-2.5 px-4 font-semibold text-slate-700">${escaparHtml(c.zona)} • Piso ${c.piso}</td>
          <td class="py-2.5 px-4"><span class="px-2 py-0.5 rounded-full text-[10px] font-black ${badgeEst}">${escaparHtml(c.estado)}</span></td>
          <td class="py-2.5 px-4">${ocupanteHtml}</td>
          <td class="py-2.5 px-4 text-slate-500 max-w-xs truncate">${escaparHtml(c.motivo_bloqueo || "Operación normal 24/7")}</td>
          <td class="py-2.5 px-4 text-center">
            <div class="flex items-center justify-center gap-1.5">
              ${
                c.estado === "OCUPADA"
                  ? `<button ${puedeMant ? "" : "disabled"} onclick="abrirModalReubicarConPlaca('${escaparHtml(c.ocupante_placa)}')" class="${puedeMant ? "" : "opacity-40 cursor-not-allowed"} bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 font-bold px-2 py-1 rounded text-[11px]">Reubicar</button>`
                  : `<button ${puedeMant ? "" : "disabled"} onclick="abrirModalEstadoCelda('${escaparHtml(c.codigo)}', '${escaparHtml(c.estado)}', '${escaparHtml(c.motivo_bloqueo || "")}')" class="${puedeMant ? "" : "opacity-40 cursor-not-allowed"} bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-200 font-bold px-2 py-1 rounded text-[11px]">Estado</button>`
              }
              <button ${esAdmin ? "" : "disabled"} onclick="abrirModalEditarCelda('${escaparHtml(c.codigo)}')" class="${esAdmin ? "" : "opacity-40 cursor-not-allowed"} bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold px-2 py-1 rounded text-[11px]">Editar</button>
              <button ${esAdmin && c.estado !== "OCUPADA" ? "" : "disabled"} onclick="eliminarCeldaCrud('${escaparHtml(c.codigo)}')" class="${esAdmin && c.estado !== "OCUPADA" ? "" : "opacity-40 cursor-not-allowed"} bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 font-bold px-2 py-1 rounded text-[11px]">Eliminar</button>
            </div>
          </td>
        </tr>
      `;
    })
    .join("");
}

function abrirModalCrearCelda() {
  if (!tienePermiso("CRUD_CELDAS")) {
    mostrarNotificacion("Acceso Denegado (RBAC)", "Solo el rol ADMIN puede registrar nuevas celdas físicas.", "error");
    return;
  }
  document.getElementById("modal-celda-crud-titulo").textContent = "Registrar Nueva Celda Física (CRUD)";
  document.getElementById("modal-celda-modo").value = "CREAR";
  const inputCod = document.getElementById("modal-crud-celda-codigo");
  inputCod.value = "C-71";
  inputCod.readOnly = false;
  inputCod.classList.remove("bg-slate-200");
  document.getElementById("modal-crud-celda-tipo").value = "CARRO";
  document.getElementById("modal-crud-celda-zona").value = "PISO 2 - ZONA EXPANSIÓN";
  document.getElementById("modal-crud-celda-piso").value = "2";
  document.getElementById("modal-crud-celda-estado").value = "DISPONIBLE";
  document.getElementById("modal-crud-celda-motivo").value = "";
  abrirModal("modal-celda-crud");
}

function abrirModalEditarCelda(codigo) {
  if (!tienePermiso("CRUD_CELDAS")) {
    mostrarNotificacion("Acceso Denegado (RBAC)", "Solo el rol ADMIN puede modificar parámetros estructurales de celdas.", "error");
    return;
  }
  const c =
    estadoApp.celdasCrud.find((x) => x.codigo === codigo) ||
    (estadoApp.resumen?.celdas || []).find((x) => x.codigo === codigo);
  if (!c) return;

  document.getElementById("modal-celda-crud-titulo").textContent = `Editar Parámetros de Celda ${c.codigo}`;
  document.getElementById("modal-celda-modo").value = "EDITAR";
  const inputCod = document.getElementById("modal-crud-celda-codigo");
  inputCod.value = c.codigo;
  inputCod.readOnly = true;
  inputCod.classList.add("bg-slate-200");
  document.getElementById("modal-crud-celda-tipo").value = c.tipo_permitido;
  document.getElementById("modal-crud-celda-zona").value = c.zona;
  document.getElementById("modal-crud-celda-piso").value = String(c.piso);
  document.getElementById("modal-crud-celda-estado").value = c.estado === "OCUPADA" ? "DISPONIBLE" : c.estado;
  document.getElementById("modal-crud-celda-motivo").value = c.motivo_bloqueo || "";
  abrirModal("modal-celda-crud");
}

async function guardarCeldaCrud() {
  const modo = document.getElementById("modal-celda-modo").value;
  const payload = {
    codigo: document.getElementById("modal-crud-celda-codigo").value.trim().toUpperCase(),
    tipo_permitido: document.getElementById("modal-crud-celda-tipo").value,
    zona: document.getElementById("modal-crud-celda-zona").value.trim().toUpperCase(),
    piso: Number(document.getElementById("modal-crud-celda-piso").value),
    estado: document.getElementById("modal-crud-celda-estado").value,
    motivo_bloqueo: document.getElementById("modal-crud-celda-motivo").value.trim(),
    usuario_id: estadoApp.sesion.id,
  };

  const ruta = modo === "CREAR" ? "/api/celdas" : "/api/celdas/actualizar";
  const { ok, data } = await apiPost(ruta, payload);
  if (!ok || !data.success) {
    mostrarNotificacion("Operación CRUD Rechazada", data.mensaje || "Error en validación de celda", "error");
    return;
  }

  cerrarModal("modal-celda-crud");
  mostrarNotificacion("Inventario de Celdas Actualizado", data.mensaje, "exito");
  await cargarResumenGeneral();
  await cargarTablaCeldasCrud();
  await cargarHistorialCeldas();
}

async function eliminarCeldaCrud(codigo) {
  const { ok, data } = await apiPost("/api/celdas/eliminar", {
    codigo,
    usuario_id: estadoApp.sesion.id,
  });
  if (!ok || !data.success) {
    mostrarNotificacion("No se puede eliminar la celda", data.mensaje || "Restricción de integridad", "alerta");
    return;
  }
  mostrarNotificacion("Celda Eliminada", data.mensaje, "exito");
  await cargarResumenGeneral();
  await cargarTablaCeldasCrud();
  await cargarHistorialCeldas();
}

function abrirModalEstadoCelda(codigo, estadoActual, motivoActual = "") {
  if (!tienePermiso("MANTENIMIENTO_CELDAS")) {
    mostrarNotificacion("Acceso Denegado (RBAC)", "Su rol no posee permisos de mantenimiento de celdas.", "error");
    return;
  }
  document.getElementById("modal-celda-codigo").value = codigo;
  document.getElementById("modal-celda-nuevo-estado").value =
    estadoActual === "DISPONIBLE" ? "MANTENIMIENTO" : "DISPONIBLE";
  document.getElementById("modal-celda-motivo").value = motivoActual || "";
  abrirModal("modal-estado-celda");
}

async function guardarEstadoCelda() {
  const codigo = document.getElementById("modal-celda-codigo").value;
  const nuevo_estado = document.getElementById("modal-celda-nuevo-estado").value;
  const motivo = document.getElementById("modal-celda-motivo").value.trim();

  const { ok, data } = await apiPost("/api/celdas/estado", {
    codigo,
    nuevo_estado,
    motivo,
    usuario_id: estadoApp.sesion.id,
  });

  if (!ok || !data.success) {
    mostrarNotificacion("Conflicto en Celda", data.mensaje || "No se pudo cambiar el estado", "error");
    return;
  }

  cerrarModal("modal-estado-celda");
  mostrarNotificacion("Estado Operativo Actualizado", data.mensaje, "exito");
  await cargarResumenGeneral();
  await cargarTablaCeldasCrud();
  await cargarHistorialCeldas();
}

function abrirModalReubicar() {
  const adentro = estadoApp.resumen?.vehiculos_adentro || [];
  if (adentro.length === 0) {
    mostrarNotificacion("Sin vehículos adentro", "No hay vehículos estacionados para reubicar en este momento.", "alerta");
    return;
  }
  abrirModalReubicarConPlaca(adentro[0].vehiculo_placa);
}

function abrirModalReubicarConPlaca(placaSeleccionada) {
  if (!tienePermiso("MANTENIMIENTO_CELDAS")) {
    mostrarNotificacion("Acceso Denegado (RBAC)", "Su rol no posee permisos para reubicar vehículos.", "error");
    return;
  }
  const adentro = estadoApp.resumen?.vehiculos_adentro || [];
  if (adentro.length === 0) {
    mostrarNotificacion("Sin vehículos estacionados", "Ingrese primero un vehículo para probar la reubicación.", "alerta");
    return;
  }

  const selPlaca = document.getElementById("modal-reubicar-placa");
  selPlaca.innerHTML = adentro
    .map(
      (v) =>
        `<option value="${escaparHtml(v.vehiculo_placa)}" data-tipo="${escaparHtml(v.tipo_vehiculo)}" ${
          v.vehiculo_placa === placaSeleccionada ? "selected" : ""
        }>${escaparHtml(formatearPlacaVisual(v.vehiculo_placa))} — Celda actual ${escaparHtml(v.celda_codigo)} (${escaparHtml(v.tipo_vehiculo)})</option>`
    )
    .join("");

  document.getElementById("modal-reubicar-motivo").value = "Mantenimiento correctivo / filtración en celda origen";
  document.getElementById("modal-reubicar-marcar-maint").checked = true;
  actualizarCeldasLibresParaReubicacion();
  abrirModal("modal-reubicar-vehiculo");
}

function actualizarCeldasLibresParaReubicacion() {
  const selPlaca = document.getElementById("modal-reubicar-placa");
  const opt = selPlaca.options[selPlaca.selectedIndex];
  const tipoReq = opt ? opt.getAttribute("data-tipo") : "CARRO";

  const libresCompatibles = (estadoApp.resumen?.celdas || []).filter(
    (c) => c.estado === "DISPONIBLE" && c.tipo_permitido === tipoReq
  );

  const selDestino = document.getElementById("modal-reubicar-nueva-celda");
  selDestino.innerHTML = libresCompatibles
    .map(
      (c) =>
        `<option value="${escaparHtml(c.codigo)}">${escaparHtml(c.codigo)} — ${escaparHtml(c.zona)} (Piso ${c.piso})</option>`
    )
    .join("");
}

async function ejecutarReubicacion() {
  const placa = document.getElementById("modal-reubicar-placa").value;
  const nueva_celda = document.getElementById("modal-reubicar-nueva-celda").value;
  const motivo = document.getElementById("modal-reubicar-motivo").value.trim();
  const marcar_anterior_mantenimiento = document.getElementById("modal-reubicar-marcar-maint").checked;

  const { ok, data } = await apiPost("/api/celdas/reubicar", {
    placa,
    nueva_celda,
    motivo,
    marcar_anterior_mantenimiento,
    usuario_id: estadoApp.sesion.id,
  });

  if (!ok || !data.success) {
    mostrarNotificacion("Error en Reubicación", data.mensaje || "Transacción rechazada", "error");
    return;
  }

  cerrarModal("modal-reubicar-vehiculo");
  mostrarNotificacion("Reubicación Atómica Exitosa", data.mensaje, "exito");
  await cargarResumenGeneral();
  await cargarTablaCeldasCrud();
  await cargarHistorialCeldas();
}

async function cargarHistorialCeldas() {
  const { ok, data } = await apiGet("/api/historial_celdas?limite=40");
  if (!ok) return;
  const tbody = document.getElementById("tbody-historial-celdas");
  if (!tbody) return;

  const items = data.historial || [];
  if (items.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="py-4 px-4 text-center text-slate-400">Sin cambios técnicos registrados aún en el historial de celdas.</td></tr>`;
    return;
  }

  tbody.innerHTML = items
    .map(
      (h) => `
      <tr class="hover:bg-slate-50">
        <td class="py-2 px-4 text-slate-500 font-mono-plate text-[11px]">${escaparHtml(h.fecha_cambio)}</td>
        <td class="py-2 px-4 font-mono-plate font-extrabold text-slate-900">${escaparHtml(h.celda_codigo)}</td>
        <td class="py-2 px-4 font-bold text-slate-700">${escaparHtml(h.estado_anterior)} &rarr; <span class="text-blue-700">${escaparHtml(h.estado_nuevo)}</span></td>
        <td class="py-2 px-4 text-slate-600">${escaparHtml(h.motivo || "")}</td>
        <td class="py-2 px-4 text-slate-700 font-semibold">${escaparHtml(h.username || "sistema")} (${escaparHtml(h.rol || "ADMIN")})</td>
      </tr>
    `
    )
    .join("");
}

// ============================================================================
// VISTA 4: GESTIÓN CRUD DE USUARIOS, ROLES Y PERMISOS RBAC (ITERACIÓN 2)
// ============================================================================

async function cargarTablaUsuarios() {
  const q = (document.getElementById("filtro-user-q")?.value || "").trim();
  const rol = document.getElementById("filtro-user-rol")?.value || "";

  const params = new URLSearchParams();
  if (q) params.set("q", q);
  if (rol) params.set("rol", rol);

  const { ok, data } = await apiGet(`/api/usuarios?${params.toString()}`);
  if (!ok) return;

  estadoApp.usuarios = data.usuarios || [];
  const lbl = document.getElementById("contador-usuarios");
  if (lbl) lbl.textContent = `${estadoApp.usuarios.length} cuentas registradas`;

  const tbody = document.getElementById("tbody-usuarios");
  if (!tbody) return;

  const esAdmin = tienePermiso("GESTION_USUARIOS");

  tbody.innerHTML = estadoApp.usuarios
    .map((u) => {
      const badgeRol =
        u.rol === "ADMIN"
          ? "bg-purple-100 text-purple-800 border border-purple-200"
          : u.rol === "OPERARIO"
          ? "bg-blue-100 text-blue-800 border border-blue-200"
          : "bg-emerald-100 text-emerald-800 border border-emerald-200";

      const badgeActivo = u.activo
        ? `<span class="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full text-[10px] font-black">ACTIVO</span>`
        : `<span class="bg-rose-100 text-rose-800 px-2 py-0.5 rounded-full text-[10px] font-black">SUSPENDIDO</span>`;

      return `
        <tr class="hover:bg-slate-50">
          <td class="py-2.5 px-2.5 font-bold text-slate-500">#${u.id}</td>
          <td class="py-2.5 px-2.5 font-mono-plate font-extrabold text-slate-900">${escaparHtml(u.username)}</td>
          <td class="py-2.5 px-3 font-bold text-slate-800">${escaparHtml(u.nombre_completo)}</td>
          <td class="py-2.5 px-3 text-slate-600">${escaparHtml(u.email)}</td>
          <td class="py-2.5 px-2.5"><span class="px-2 py-0.5 rounded text-[10px] font-black ${badgeRol}">${escaparHtml(u.rol)}</span></td>
          <td class="py-2.5 px-2.5 text-slate-600">${escaparHtml(u.cargo || "")}</td>
          <td class="py-2.5 px-2.5">${badgeActivo}</td>
          <td class="py-2.5 px-2.5 text-[11px] text-slate-500 whitespace-nowrap">${escaparHtml(u.ultimo_login || "Sin ingreso")}</td>
          <td class="py-2.5 px-3 text-center whitespace-nowrap">
            <div class="flex items-center justify-center gap-1">
              <button ${esAdmin ? "" : "disabled"} onclick="abrirModalEditarUsuario(${u.id})" class="${esAdmin ? "" : "opacity-40 cursor-not-allowed"} bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold px-2 py-1 rounded text-[11px]">Editar</button>
              <button ${esAdmin ? "" : "disabled"} onclick="abrirModalClave(${u.id}, '${escaparHtml(u.username)}')" class="${esAdmin ? "" : "opacity-40 cursor-not-allowed"} bg-purple-50 hover:bg-purple-100 text-purple-800 border border-purple-200 font-bold px-2 py-1 rounded text-[11px]">Clave</button>
              <button ${esAdmin ? "" : "disabled"} onclick="alternarActivoUsuario(${u.id}, ${u.activo ? 0 : 1})" class="${esAdmin ? "" : "opacity-40 cursor-not-allowed"} bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-200 font-bold px-2 py-1 rounded text-[11px]">${u.activo ? "Suspender" : "Activar"}</button>
              <button ${esAdmin ? "" : "disabled"} onclick="eliminarUsuario(${u.id})" class="${esAdmin ? "" : "opacity-40 cursor-not-allowed"} bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 font-bold px-2 py-1 rounded text-[11px]">Baja</button>
            </div>
          </td>
        </tr>
      `;
    })
    .join("");
}

function abrirModalUsuario() {
  if (!tienePermiso("GESTION_USUARIOS")) {
    mostrarNotificacion("Acceso Denegado (RBAC)", "Solo el rol ADMIN puede gestionar cuentas de usuario.", "error");
    return;
  }
  document.getElementById("modal-usuario-titulo").textContent = "Registrar Nuevo Usuario del Sistema";
  document.getElementById("modal-user-id").value = "";
  const inUser = document.getElementById("modal-user-username");
  inUser.value = "";
  inUser.readOnly = false;
  inUser.classList.remove("bg-slate-200");
  document.getElementById("contenedor-user-password").classList.remove("hidden");
  document.getElementById("modal-user-password").value = "";
  document.getElementById("modal-user-nombre").value = "";
  document.getElementById("modal-user-email").value = "";
  document.getElementById("modal-user-rol").value = "OPERARIO";
  document.getElementById("modal-user-cargo").value = "Operador de Turno 24/7";
  abrirModal("modal-usuario");
}

function abrirModalEditarUsuario(id) {
  if (!tienePermiso("GESTION_USUARIOS")) {
    mostrarNotificacion("Acceso Denegado (RBAC)", "Solo el rol ADMIN puede editar cuentas.", "error");
    return;
  }
  const u = estadoApp.usuarios.find((x) => x.id === id);
  if (!u) return;

  document.getElementById("modal-usuario-titulo").textContent = `Editar Perfil y Rol RBAC — ${u.username}`;
  document.getElementById("modal-user-id").value = String(u.id);
  const inUser = document.getElementById("modal-user-username");
  inUser.value = u.username;
  inUser.readOnly = true;
  inUser.classList.add("bg-slate-200");
  document.getElementById("contenedor-user-password").classList.add("hidden");
  document.getElementById("modal-user-nombre").value = u.nombre_completo;
  document.getElementById("modal-user-email").value = u.email;
  document.getElementById("modal-user-rol").value = u.rol;
  document.getElementById("modal-user-cargo").value = u.cargo || "";
  abrirModal("modal-usuario");
}

async function guardarUsuario() {
  const idRaw = document.getElementById("modal-user-id").value;
  const payload = {
    username: document.getElementById("modal-user-username").value.trim(),
    password: document.getElementById("modal-user-password").value,
    nombre_completo: document.getElementById("modal-user-nombre").value.trim(),
    email: document.getElementById("modal-user-email").value.trim(),
    rol: document.getElementById("modal-user-rol").value,
    cargo: document.getElementById("modal-user-cargo").value.trim(),
    admin_id: estadoApp.sesion.id,
  };

  let resp;
  if (!idRaw) {
    resp = await apiPost("/api/usuarios", payload);
  } else {
    payload.user_id = Number(idRaw);
    resp = await apiPost("/api/usuarios/actualizar", payload);
  }

  if (!resp.ok || !resp.data.success) {
    mostrarNotificacion("Validación de Usuario", resp.data.mensaje || "Error al guardar usuario", "error");
    return;
  }

  cerrarModal("modal-usuario");
  mostrarNotificacion("Gestión de Usuarios", resp.data.mensaje, "exito");
  await cargarTablaUsuarios();
}

function abrirModalClave(userId, username) {
  if (!tienePermiso("GESTION_USUARIOS")) {
    mostrarNotificacion("Acceso Denegado (RBAC)", "Solo ADMIN puede restablecer contraseñas.", "error");
    return;
  }
  document.getElementById("modal-clave-userid").value = String(userId);
  document.getElementById("modal-clave-username").textContent = username;
  document.getElementById("modal-clave-input").value = "";
  abrirModal("modal-clave");
}

async function ejecutarCambioClave() {
  const user_id = Number(document.getElementById("modal-clave-userid").value);
  const nueva_password = document.getElementById("modal-clave-input").value;

  const { ok, data } = await apiPost("/api/usuarios/clave", {
    user_id,
    nueva_password,
    admin_id: estadoApp.sesion.id,
  });

  if (!ok || !data.success) {
    mostrarNotificacion("Error al cambiar clave", data.mensaje || "Contraseña inválida", "error");
    return;
  }

  cerrarModal("modal-clave");
  mostrarNotificacion("Hash SHA-256 Actualizado", data.mensaje, "exito");
}

async function alternarActivoUsuario(userId, nuevoEstado) {
  const u = estadoApp.usuarios.find((x) => x.id === userId);
  if (!u) return;

  const { ok, data } = await apiPost("/api/usuarios/actualizar", {
    user_id: userId,
    activo: nuevoEstado,
    rol: u.rol,
    nombre_completo: u.nombre_completo,
    email: u.email,
    cargo: u.cargo,
    admin_id: estadoApp.sesion.id,
  });

  if (!ok || !data.success) {
    mostrarNotificacion("Acción Bloqueada", data.mensaje || "No se pudo cambiar el estado", "alerta");
    return;
  }
  mostrarNotificacion("Estado de Cuenta Actualizado", data.mensaje, "exito");
  await cargarTablaUsuarios();
}

async function eliminarUsuario(userId) {
  const { ok, data } = await apiPost("/api/usuarios/eliminar", {
    user_id: userId,
    admin_id: estadoApp.sesion.id,
  });
  if (!ok || !data.success) {
    mostrarNotificacion("Protección de Seguridad", data.mensaje || "No se pudo dar de baja", "alerta");
    return;
  }
  mostrarNotificacion("Baja de Usuario Procesada", data.mensaje, "exito");
  await cargarTablaUsuarios();
}

// ============================================================================
// VISTA 5: PADRÓN CRUD DE CLIENTES ABONADOS Y VEHÍCULOS (ITERACIÓN 2)
// ============================================================================

async function cargarAbonadosServidor() {
  const { ok, data } = await apiGet("/api/abonados");
  if (!ok) return;
  estadoApp.abonados = data.abonados || [];
  filtrarAbonadosLocal();
}

function filtrarAbonadosLocal() {
  const q = (document.getElementById("filtro-abonados-q")?.value || "").trim().toLowerCase();
  const filtrados = estadoApp.abonados.filter((a) => {
    if (!q) return true;
    return (
      String(a.placa).toLowerCase().includes(q) ||
      String(a.nombre_completo).toLowerCase().includes(q) ||
      String(a.documento).toLowerCase().includes(q) ||
      String(a.marca).toLowerCase().includes(q)
    );
  });
  renderizarTablaAbonados(filtrados);
}

function renderizarTablaAbonados(lista) {
  const lbl = document.getElementById("contador-abonados");
  if (lbl) lbl.textContent = `${lista.length} abonados`;
  const tbody = document.getElementById("tbody-abonados");
  if (!tbody) return;

  const puedeEditar = tienePermiso("GESTION_ABONADOS");

  tbody.innerHTML = lista
    .map((a) => {
      const badgeVigencia = a.al_dia
        ? `<span class="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full text-[10px] font-black">ACTIVA (${a.dias_restantes}d)</span>`
        : `<span class="bg-rose-100 text-rose-800 px-2 py-0.5 rounded-full text-[10px] font-black">VENCIDA / MORA</span>`;

      return `
        <tr class="hover:bg-slate-50">
          <td class="py-3 px-4 font-mono-plate font-extrabold text-slate-900">${escaparHtml(formatearPlacaVisual(a.placa))}</td>
          <td class="py-3 px-4">
            <div class="font-bold text-slate-800">${escaparHtml(a.marca)} ${escaparHtml(a.modelo)}</div>
            <div class="text-[11px] text-slate-500">${escaparHtml(a.tipo_vehiculo)} • Color ${escaparHtml(a.color)}</div>
          </td>
          <td class="py-3 px-4">
            <div class="font-bold text-slate-800">${escaparHtml(a.nombre_completo)}</div>
            <div class="text-[11px] text-slate-500">CC ${escaparHtml(a.documento)} • Tel ${escaparHtml(a.telefono)}</div>
          </td>
          <td class="py-3 px-4 font-extrabold text-slate-800">${formatearMonedaCOP(a.valor_pagado || (a.tipo_vehiculo === "CARRO" ? 250000 : 100000))}</td>
          <td class="py-3 px-4 text-slate-600 font-mono-plate text-[11px]">${escaparHtml(a.fecha_vencimiento || "Sin contrato")}</td>
          <td class="py-3 px-4">${badgeVigencia}</td>
          <td class="py-3 px-4 text-center">
            <button ${puedeEditar ? "" : "disabled"} onclick="abrirModalEditarAbonado('${escaparHtml(a.placa)}')" class="${puedeEditar ? "" : "opacity-40 cursor-not-allowed"} bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 font-bold px-2.5 py-1 rounded-lg text-[11px]">
              Editar Datos
            </button>
          </td>
        </tr>
      `;
    })
    .join("");
}

function abrirModalNuevoAbonado() {
  if (!tienePermiso("GESTION_ABONADOS")) {
    mostrarNotificacion("Acceso Denegado (RBAC)", "Su rol no posee privilegios para modificar el padrón de abonados.", "error");
    return;
  }
  document.getElementById("modal-abonado-titulo").textContent = "Registrar Cliente Abonado y Vehículo";
  document.getElementById("modal-ab-modo").value = "CREAR";
  const inPlaca = document.getElementById("modal-ab-placa");
  inPlaca.value = "";
  inPlaca.readOnly = false;
  inPlaca.classList.remove("bg-slate-200");
  document.getElementById("modal-ab-tipo").value = "CARRO";
  document.getElementById("modal-ab-marca").value = "";
  document.getElementById("modal-ab-modelo").value = "";
  document.getElementById("modal-ab-color").value = "";
  document.getElementById("modal-ab-conductor").value = "";
  document.getElementById("modal-ab-documento").value = "";
  document.getElementById("modal-ab-telefono").value = "";
  document.getElementById("contenedor-ab-estado-pago").classList.remove("hidden");
  document.getElementById("modal-ab-estado-pago").value = "ACTIVA";
  abrirModal("modal-nuevo-abonado");
}

function abrirModalEditarAbonado(placa) {
  if (!tienePermiso("GESTION_ABONADOS")) {
    mostrarNotificacion("Acceso Denegado (RBAC)", "Rol sin permisos de edición de abonados.", "error");
    return;
  }
  const a = estadoApp.abonados.find((x) => x.placa === placa);
  if (!a) return;

  document.getElementById("modal-abonado-titulo").textContent = `Actualizar Titular / Vehículo — ${formatearPlacaVisual(a.placa)}`;
  document.getElementById("modal-ab-modo").value = "EDITAR";
  const inPlaca = document.getElementById("modal-ab-placa");
  inPlaca.value = formatearPlacaVisual(a.placa);
  inPlaca.readOnly = true;
  inPlaca.classList.add("bg-slate-200");
  document.getElementById("modal-ab-tipo").value = a.tipo_vehiculo;
  document.getElementById("modal-ab-marca").value = a.marca;
  document.getElementById("modal-ab-modelo").value = a.modelo;
  document.getElementById("modal-ab-color").value = a.color;
  document.getElementById("modal-ab-conductor").value = a.nombre_completo;
  document.getElementById("modal-ab-documento").value = a.documento;
  document.getElementById("modal-ab-telefono").value = a.telefono;
  document.getElementById("contenedor-ab-estado-pago").classList.add("hidden");
  abrirModal("modal-nuevo-abonado");
}

async function guardarAbonado() {
  const modo = document.getElementById("modal-ab-modo").value;
  const payload = {
    placa: document.getElementById("modal-ab-placa").value.trim(),
    tipo_vehiculo: document.getElementById("modal-ab-tipo").value,
    marca: document.getElementById("modal-ab-marca").value.trim(),
    modelo: document.getElementById("modal-ab-modelo").value.trim(),
    color: document.getElementById("modal-ab-color").value.trim(),
    conductor: document.getElementById("modal-ab-conductor").value.trim(),
    documento: document.getElementById("modal-ab-documento").value.trim(),
    telefono: document.getElementById("modal-ab-telefono").value.trim(),
    estado_pago: document.getElementById("modal-ab-estado-pago").value,
    usuario_id: estadoApp.sesion.id,
  };

  const ruta = modo === "CREAR" ? "/api/abonado" : "/api/abonado/actualizar";
  const { ok, data } = await apiPost(ruta, payload);
  if (!ok || !data.success) {
    mostrarNotificacion("Error en Padrón de Abonados", data.mensaje || "Revise los campos", "error");
    return;
  }

  cerrarModal("modal-nuevo-abonado");
  mostrarNotificacion("Padrón de Abonados Actualizado", data.mensaje, "exito");
  await cargarResumenGeneral();
}

// ============================================================================
// VISTA 6: BITÁCORA CENTRAL INMUTABLE DE AUDITORÍA 24/7
// ============================================================================

async function cargarAuditoria() {
  const mod = document.getElementById("filtro-auditoria-modulo")?.value || "";
  const ruta = mod ? `/api/auditoria?limite=80&modulo=${encodeURIComponent(mod)}` : "/api/auditoria?limite=80";
  const { ok, data } = await apiGet(ruta);
  if (!ok) return;

  const tbody = document.getElementById("tbody-auditoria");
  if (!tbody) return;

  const items = data.auditoria || [];
  if (items.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="py-8 text-center text-slate-400">No existen eventos registrados para el filtro seleccionado.</td></tr>`;
    return;
  }

  tbody.innerHTML = items
    .map((a) => {
      const colMod =
        a.modulo === "SEGURIDAD"
          ? "bg-purple-100 text-purple-800"
          : a.modulo === "USUARIOS"
          ? "bg-indigo-100 text-indigo-800"
          : a.modulo === "CELDAS"
          ? "bg-amber-100 text-amber-800"
          : a.modulo === "ABONADOS"
          ? "bg-blue-100 text-blue-800"
          : "bg-emerald-100 text-emerald-800";

      return `
        <tr class="hover:bg-slate-50">
          <td class="py-2.5 px-4 font-bold text-slate-400">#${a.id}</td>
          <td class="py-2.5 px-4 font-mono-plate text-[11px] text-slate-600">${escaparHtml(a.fecha)}</td>
          <td class="py-2.5 px-4 font-bold text-slate-800">${escaparHtml(a.username || "sistema")} <span class="text-[10px] text-slate-500">(${escaparHtml(a.rol || "N/A")})</span></td>
          <td class="py-2.5 px-4"><span class="px-2 py-0.5 rounded text-[10px] font-black ${colMod}">${escaparHtml(a.modulo)}</span></td>
          <td class="py-2.5 px-4 font-mono-plate font-bold text-[11px] text-slate-800">${escaparHtml(a.accion)}</td>
          <td class="py-2.5 px-4 text-slate-600">${escaparHtml(a.detalle)}</td>
          <td class="py-2.5 px-4 text-[11px] text-slate-500">${escaparHtml(a.ip_terminal || "Cabina")}</td>
        </tr>
      `;
    })
    .join("");
}

// ============================================================================
// RELOJ EN VIVO Y ARRANQUE AUTOMÁTICO (CON SOPORTE DE VISTAS PARA MOCKUPS)
// ============================================================================

function iniciarReloj24x7() {
  const actualizar = () => {
    const el = document.getElementById("reloj-vivo");
    if (!el) return;
    const ahora = new Date();
    el.textContent = ahora.toLocaleString("es-CO", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };
  actualizar();
  const esMockup = new URLSearchParams(window.location.search).has("mockup");
  if (!esMockup) {
    setInterval(actualizar, 1000);
  }
}

async function aplicarModoMockupSiExiste() {
  const params = new URLSearchParams(window.location.search);
  const mockup = params.get("mockup");
  if (!mockup) return;

  const styleFreeze = document.createElement("style");
  styleFreeze.textContent =
    "*, *::before, *::after { animation: none !important; transition: none !important; } .view-container.active { opacity: 1 !important; transform: none !important; }";
  document.head.appendChild(styleFreeze);

  if (mockup === "login") {
    await consultarPlaca();
    abrirModalLogin();
  } else if (mockup === "usuarios") {
    cambiarVista("view-usuarios");
    await cargarTablaUsuarios();
  } else if (mockup === "celdas") {
    cambiarVista("view-celdas-crud");
    await cargarTablaCeldasCrud();
    await cargarHistorialCeldas();
  } else if (mockup === "mapa") {
    cambiarVista("view-mapa");
    const ocupada = (estadoApp.resumen?.celdas || []).find((c) => c.estado === "OCUPADA");
    seleccionarCelda(ocupada ? ocupada.codigo : "C-01");
  } else if (mockup === "reubicar") {
    cambiarVista("view-mapa");
    const ocupada = (estadoApp.resumen?.celdas || []).find((c) => c.estado === "OCUPADA");
    if (ocupada) {
      seleccionarCelda(ocupada.codigo);
      abrirModalReubicarConPlaca(ocupada.vehiculo_placa);
    }
  } else if (mockup === "abonados") {
    cambiarVista("view-abonados");
    await cargarAbonadosServidor();
  } else if (mockup === "auditoria") {
    cambiarVista("view-auditoria");
    await cargarAuditoria();
  }
  await new Promise((r) => setTimeout(r, 150));
}

document.addEventListener("DOMContentLoaded", async () => {
  iniciarReloj24x7();
  aplicarPermisosRBAC();
  await cargarResumenGeneral();
  const esMockup = new URLSearchParams(window.location.search).has("mockup");
  if (!esMockup) {
    await consultarPlaca();
  }
  await aplicarModoMockupSiExiste();
});
