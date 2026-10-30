/**
 * Lógica Cliente e Interactividad - Autos Colombia 24/7
 * Iteración 1 & 2: Control de Acceso, Gestión de Usuarios (RBAC) y Gestión de Celdas
 * Asignatura: Ingeniería de Software - PREICA2602B020053
 * Docente: Reinaldo Rojas | Grupo: 25
 */

let estadoParqueadero = {
  capacidad_total: 80,
  total_ocupadas: 0,
  total_libres: 80,
  total_mantenimiento: 0,
  carros: { total: 70, ocupadas: 0, libres: 70, mantenimiento: 0 },
  motos: { total: 10, ocupadas: 0, libres: 10, mantenimiento: 0 },
  vehiculos_adentro: [],
  celdas: [],
  abonados: [],
  usuarios: []
};

let usuarioActivo = {
  id: 2,
  username: "adriana_op",
  nombre: "Adriana Andrea Agudelo Agudelo",
  rol: "OPERARIO"
};

let vehiculoConsultado = null;
let filtroMapaActual = 'TODOS';
let celdaSeleccionadaActual = null;

// ====================================================================
// 1. INICIALIZACIÓN Y EVENT LISTENERS
// ====================================================================
document.addEventListener("DOMContentLoaded", () => {
  iniciarReloj();
  cargarEstadoParqueadero();
  consultarPlaca(); // Cargar la placa de prueba inicial (ABC-123)

  // Polling automático cada 4 segundos para sincronización en tiempo real
  setInterval(cargarEstadoParqueadero, 4000);
});

function iniciarReloj() {
  const el = document.getElementById("reloj-vivo");
  function actualizar() {
    const ahora = new Date();
    const opciones = { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' };
    el.innerText = ahora.toLocaleTimeString('es-CO', opciones) + " • 24/7 Activo";
  }
  actualizar();
  setInterval(actualizar, 1000);
}

function cambiarUsuarioSesion() {
  const sel = document.getElementById("select-usuario-sesion");
  const val = parseInt(sel.value);
  const badge = document.getElementById("badge-rol-activo");
  const footerTag = document.getElementById("footer-user-tag");

  if (val === 1) {
    usuarioActivo = { id: 1, username: "admin", nombre: "Camilo Alberto Palacios Turriago", rol: "ADMIN" };
    badge.className = "bg-purple-600 text-white px-1.5 py-0.2 rounded text-[10px] font-black uppercase";
    badge.innerText = "ADMIN";
    footerTag.innerText = "Administrador: Camilo Palacios";
  } else if (val === 2) {
    usuarioActivo = { id: 2, username: "adriana_op", nombre: "Adriana Andrea Agudelo Agudelo", rol: "OPERARIO" };
    badge.className = "bg-blue-600 text-white px-1.5 py-0.2 rounded text-[10px] font-black uppercase";
    badge.innerText = "OPERARIO";
    footerTag.innerText = "Operador: Adriana Agudelo";
  } else if (val === 3) {
    usuarioActivo = { id: 3, username: "daniel_op", nombre: "Juan Daniel Pulgarin García", rol: "OPERARIO" };
    badge.className = "bg-blue-600 text-white px-1.5 py-0.2 rounded text-[10px] font-black uppercase";
    badge.innerText = "OPERARIO";
    footerTag.innerText = "Operador: Juan Daniel Pulgarin";
  } else if (val === 4) {
    usuarioActivo = { id: 4, username: "auditor", nombre: "Auditor de Calidad y Seguridad", rol: "AUDITOR" };
    badge.className = "bg-emerald-600 text-white px-1.5 py-0.2 rounded text-[10px] font-black uppercase";
    badge.innerText = "AUDITOR";
    footerTag.innerText = "Auditor: Seguridad y Calidad";
  }
}

function getPuertaActiva() {
  const sel = document.getElementById("select-puerta-operario");
  return sel ? sel.value : "Puerta 1 - Norte (Operario 1)";
}

function cambiarVista(vistaId) {
  document.querySelectorAll(".view-container").forEach(el => el.classList.remove("active"));
  const target = document.getElementById(vistaId);
  if (target) target.classList.add("active");

  document.querySelectorAll(".nav-tab").forEach(tab => {
    if (tab.getAttribute("data-target") === vistaId) {
      tab.classList.add("bg-blue-600", "text-white");
      tab.classList.remove("text-slate-300", "hover:bg-slate-800");
    } else {
      tab.classList.remove("bg-blue-600", "text-white");
      tab.classList.add("text-slate-300", "hover:bg-slate-800");
    }
  });

  document.querySelectorAll(".sidebar-link").forEach(btn => {
    btn.classList.remove("bg-blue-700", "text-white", "shadow-sm");
    btn.classList.add("text-slate-600");
  });
  const activeSide = document.getElementById(`side-link-${vistaId.replace('view-', '')}`);
  if (activeSide) {
    activeSide.classList.add("bg-blue-700", "text-white", "shadow-sm");
    activeSide.classList.remove("text-slate-600");
  }

  if (vistaId === 'view-celdas-crud') cargarTablaCeldasCrud();
  if (vistaId === 'view-usuarios') cargarTablaUsuarios();
  if (vistaId === 'view-auditoria') cargarAuditoria();
}

function formatearInputPlaca(input) {
  let v = input.value.replace(/[^a-zA-Z0-9]/g, '').toUpperCase();
  if (v.length > 3) {
    input.value = v.slice(0, 3) + '-' + v.slice(3, 6);
  } else {
    input.value = v;
  }
}

function probarPlaca(placa) {
  document.getElementById("input-placa").value = placa;
  consultarPlaca();
}

// ====================================================================
// 2. CONSUMO DE API Y ACTUALIZACIÓN EN TIEMPO REAL
// ====================================================================
async function cargarEstadoParqueadero() {
  try {
    const res = await fetch("/api/resumen");
    if (!res.ok) return;
    const data = await res.json();
    estadoParqueadero = data;

    actualizarMetricasSidebar(data);
    actualizarListaAdentro(data.vehiculos_adentro);
    renderizarMapaCeldas(data.celdas);
    renderizarTablaAbonados(data.abonados);
  } catch (err) {
    console.error("Error sincronizando estado:", err);
  }
}

function actualizarMetricasSidebar(data) {
  const libres = data.total_libres;
  const ocupadas = data.total_ocupadas;
  const maint = data.total_mantenimiento || 0;

  document.getElementById("side-badge-libres").innerText = `• ${libres} Libres`;
  document.getElementById("side-ocupadas-total").innerText = `${ocupadas} Ocupadas`;
  document.getElementById("side-mantenimiento-total").innerText = `${maint} Celdas`;

  const pct = Math.round((ocupadas / 80) * 100);
  document.getElementById("side-progress-bar").style.width = `${pct}%`;

  document.getElementById("top-carros-libres").innerText = `${data.carros.libres} Libres`;
  document.getElementById("top-motos-libres").innerText = `${data.motos.libres} Libres`;
  document.getElementById("contador-adentro-badge").innerText = data.total_adentro;

  // Actualizar stats de la vista CRUD celdas si están en el DOM
  const elDisp = document.getElementById("stat-crud-disponibles");
  if (elDisp) elDisp.innerText = `${libres} Libres`;
  const elOcup = document.getElementById("stat-crud-ocupadas");
  if (elOcup) elOcup.innerText = `${ocupadas} Ocupadas`;
  const elMaint = document.getElementById("stat-crud-mantenimiento");
  if (elMaint) elMaint.innerText = `${maint} Bloqueadas`;
}

// ====================================================================
// 3. CONSULTA DE VEHÍCULO Y CONTROL DE ENTRADA / SALIDA
// ====================================================================
async function consultarPlaca() {
  const placa = document.getElementById("input-placa").value.trim();
  const contenedor = document.getElementById("contenedor-ficha-vehiculo");
  const btn = document.getElementById("btn-autorizar-ingreso");

  if (!placa) {
    contenedor.innerHTML = `<div class="bg-amber-50 border border-amber-200 text-amber-800 p-3 rounded-xl text-xs font-semibold">Por favor digite una placa para verificar.</div>`;
    return;
  }

  contenedor.innerHTML = `<div class="text-center py-4 text-xs text-slate-500">Consultando base de datos de contratos...</div>`;

  try {
    const res = await fetch(`/api/vehiculo?placa=${encodeURIComponent(placa)}`);
    if (res.status === 404) {
      vehiculoConsultado = null;
      contenedor.innerHTML = `
        <div class="bg-rose-50 border-2 border-rose-300 rounded-xl p-4 text-xs space-y-2">
          <div class="flex items-center gap-2 text-rose-800 font-extrabold text-sm">
            <span class="w-3 h-3 rounded-full bg-rose-600"></span>
            VEHÍCULO NO REGISTRADO (ACCESO DENEGADO)
          </div>
          <p class="text-rose-700">La placa <strong>${placa.toUpperCase()}</strong> no posee ningún contrato en Autos Colombia.</p>
          <p class="text-[11px] text-slate-600">Este parqueadero opera estrictamente por modalidad de mensualidad anticipada.</p>
        </div>
      `;
      btn.disabled = true;
      btn.className = "w-full bg-slate-300 text-slate-500 font-extrabold py-3 px-4 rounded-xl text-sm cursor-not-allowed";
      return;
    }

    const data = await res.json();
    vehiculoConsultado = data;
    renderizarFichaVehiculo(data);
  } catch (err) {
    contenedor.innerHTML = `<div class="bg-rose-50 p-3 rounded-xl text-xs text-rose-700">Error al consultar vehículo: ${err}</div>`;
  }
}

function renderizarFichaVehiculo(v) {
  const contenedor = document.getElementById("contenedor-ficha-vehiculo");
  const btn = document.getElementById("btn-autorizar-ingreso");
  const m = v.mensualidad;

  let badgeMensualidad = "";
  let autorizable = false;

  if (v.esta_adentro) {
    badgeMensualidad = `
      <div class="bg-amber-100 text-amber-900 border border-amber-300 px-3 py-1.5 rounded-lg text-xs font-bold flex items-center justify-between">
        <span>ESTADO: YA ESTÁ ADENTRO EN CELDA <strong>${v.registro_actual.celda_codigo}</strong></span>
        <button onclick="ejecutarSalidaDirecta('${v.placa}')" class="bg-amber-700 hover:bg-amber-800 text-white px-2.5 py-1 rounded text-[10px] font-black">
          DAR SALIDA AHORA
        </button>
      </div>
    `;
    autorizable = false;
  } else if (!m) {
    badgeMensualidad = `<div class="bg-rose-100 text-rose-900 border border-rose-300 px-3 py-1.5 rounded-lg text-xs font-bold">SIN REGISTRO DE MENSUALIDAD</div>`;
  } else if (m.al_dia) {
    badgeMensualidad = `
      <div class="bg-emerald-100 text-emerald-900 border border-emerald-300 px-3 py-2 rounded-xl text-xs font-bold flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-emerald-600"></span>
          <span>MENSUALIDAD AL DÍA (${m.dias_restantes} días de vigencia)</span>
        </div>
        <span class="text-[11px] text-emerald-800 font-extrabold">Vence: ${m.fecha_vencimiento}</span>
      </div>
    `;
    autorizable = true;
  } else {
    badgeMensualidad = `
      <div class="bg-rose-100 text-rose-900 border-2 border-rose-400 px-3 py-2 rounded-xl text-xs font-bold space-y-1">
        <div class="flex items-center gap-2 text-rose-800 font-extrabold">
          <span class="w-3 h-3 rounded-full bg-rose-600"></span>
          <span>ACCESO DENEGADO: MENSUALIDAD VENCIDA</span>
        </div>
        <div class="text-[11px] text-rose-700">Venció el: <strong>${m.fecha_vencimiento}</strong> (Mora: ${Math.abs(m.dias_restantes)} días). Sin periodo de gracia.</div>
      </div>
    `;
    autorizable = false;
  }

  contenedor.innerHTML = `
    <div class="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="font-mono-plate text-lg font-black bg-white px-2.5 py-0.5 rounded-lg border border-slate-300 text-slate-900">${formatearPlacaVisual(v.placa)}</span>
          <span class="text-xs font-extrabold px-2 py-0.5 rounded ${v.tipo_vehiculo === 'CARRO' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}">
            ${v.tipo_vehiculo}
          </span>
        </div>
        <span class="text-xs font-bold text-slate-700">${v.marca} ${v.modelo} • ${v.color}</span>
      </div>
      <div class="text-xs text-slate-600 flex justify-between border-t border-slate-200/80 pt-2">
        <span>Propietario: <strong>${v.propietario_nombre}</strong></span>
        <span>Tel: ${v.propietario_telefono}</span>
      </div>
      ${badgeMensualidad}
    </div>
  `;

  if (autorizable) {
    btn.disabled = false;
    btn.className = "w-full bg-blue-600 hover:bg-blue-700 text-white font-extrabold py-3 px-4 rounded-xl text-sm transition-all shadow-md flex items-center justify-center gap-2 cursor-pointer";
  } else {
    btn.disabled = true;
    btn.className = "w-full bg-slate-300 text-slate-500 font-extrabold py-3 px-4 rounded-xl text-sm cursor-not-allowed";
  }
}

async function ejecutarIngreso() {
  if (!vehiculoConsultado) return;
  const placa = vehiculoConsultado.placa;
  const obs = document.getElementById("input-observaciones-ingreso").value;
  const puerta = getPuertaActiva();

  try {
    const res = await fetch("/api/ingreso", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        placa: placa,
        observaciones: obs,
        puerta: puerta,
        usuario_id: usuarioActivo.id
      })
    });
    const data = await res.json();
    if (data.success) {
      alert(`✅ INGRESO AUTORIZADO\n\nVehículo: ${formatearPlacaVisual(placa)}\nCelda Asignada: ${data.celda_asignada} (${data.zona})\nOperador: ${usuarioActivo.nombre}\n\n¡Barrera abierta!`);
      document.getElementById("input-observaciones-ingreso").value = "";
      consultarPlaca();
      cargarEstadoParqueadero();
    } else {
      alert(`❌ INGRESO DENEGADO\n\n${data.mensaje}\n${data.detalle || ""}`);
    }
  } catch (err) {
    alert("Error de red al procesar ingreso: " + err);
  }
}

async function ejecutarSalidaDirecta(placa) {
  const puerta = getPuertaActiva();
  const obs = prompt(`Registrar salida de ${formatearPlacaVisual(placa)} por ${puerta}.\nObservación física de salida (opcional):`, "Sin novedades físicas a la salida");
  if (obs === null) return;

  try {
    const res = await fetch("/api/salida", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        placa: placa,
        observaciones_salida: obs,
        puerta: puerta,
        usuario_id: usuarioActivo.id
      })
    });
    const data = await res.json();
    if (data.success) {
      alert(`🏁 SALIDA REGISTRADA CON ÉXITO\n\nVehículo: ${data.placa}\nCelda Liberada: ${data.celda_liberada}\nTiempo Permanencia: ${data.tiempo_permanencia}\nOperador: ${usuarioActivo.nombre}\n\n¡Barrera de salida abierta!`);
      consultarPlaca();
      cargarEstadoParqueadero();
    } else {
      alert("Error en salida: " + data.mensaje);
    }
  } catch (err) {
    alert("Error procesando salida: " + err);
  }
}

function actualizarListaAdentro(lista) {
  const cont = document.getElementById("lista-vehiculos-adentro");
  if (!lista || lista.length === 0) {
    cont.innerHTML = `<div class="text-center py-8 text-xs text-slate-400">No hay vehículos estacionados en este momento.</div>`;
    return;
  }

  cont.innerHTML = lista.map(v => `
    <div class="bg-slate-50 hover:bg-white border border-slate-200 rounded-xl p-3 text-xs space-y-2 transition-all">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="font-mono-plate font-extrabold text-slate-900 bg-white px-2 py-0.5 rounded border border-slate-300">${formatearPlacaVisual(v.vehiculo_placa)}</span>
          <span class="font-bold text-[10px] px-1.5 py-0.5 rounded ${v.tipo_vehiculo === 'CARRO' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}">${v.tipo_vehiculo}</span>
        </div>
        <span class="font-black bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-lg text-xs">Celda: ${v.celda_codigo}</span>
      </div>
      <div class="text-[11px] text-slate-600 flex justify-between">
        <span>${v.marca} ${v.modelo} (${v.color})</span>
        <span class="text-slate-500">Ingreso: ${v.fecha_ingreso.slice(11, 16)}</span>
      </div>
      <div class="text-[10px] text-slate-500 italic truncate">${v.observaciones || "Sin novedades"}</div>
      <div class="flex justify-end gap-1.5 pt-1 border-t border-slate-200/60">
        <button onclick="abrirModalReubicarConPlaca('${v.vehiculo_placa}')" class="bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-bold px-2 py-1 rounded text-[10px]">
          Reubicar
        </button>
        <button onclick="ejecutarSalidaDirecta('${v.vehiculo_placa}')" class="bg-rose-600 hover:bg-rose-700 text-white font-bold px-2.5 py-1 rounded text-[10px]">
          Dar Salida
        </button>
      </div>
    </div>
  `).join("");
}

// ====================================================================
// 4. MAPA VISUAL DE 80 CELDAS
// ====================================================================
function filtrarMapa(filtro) {
  filtroMapaActual = filtro;
  document.querySelectorAll(".filtro-btn").forEach(b => {
    if (b.getAttribute("data-filtro") === filtro) {
      b.className = "filtro-btn px-2.5 py-1 rounded-lg bg-blue-600 text-white font-bold";
    } else {
      b.className = "filtro-btn px-2.5 py-1 rounded-lg text-slate-600 hover:bg-slate-100 font-bold";
    }
  });
  renderizarMapaCeldas(estadoParqueadero.celdas);
}

function renderizarMapaCeldas(celdas) {
  const grid = document.getElementById("grid-celdas");
  if (!grid || !celdas) return;

  let filtradas = celdas;
  if (filtroMapaActual !== 'TODOS') {
    filtradas = celdas.filter(c => c.tipo_permitido === filtroMapaActual);
  }

  grid.innerHTML = filtradas.map(c => {
    let bg = "bg-emerald-500 hover:bg-emerald-600 text-white";
    let sub = "LIBRE";
    if (c.estado === 'OCUPADA') {
      bg = "bg-rose-500 hover:bg-rose-600 text-white shadow-sm";
      sub = c.vehiculo_placa ? formatearPlacaVisual(c.vehiculo_placa) : "OCUP";
    } else if (c.estado === 'MANTENIMIENTO') {
      bg = "bg-amber-500 hover:bg-amber-600 text-white";
      sub = "MANT";
    } else if (c.estado === 'INACTIVA') {
      bg = "bg-slate-400 hover:bg-slate-500 text-white";
      sub = "INAC";
    }

    return `
      <div onclick="seleccionarCelda('${c.codigo}')" class="${bg} p-2 rounded-xl text-center cursor-pointer transition-all flex flex-col justify-between h-14">
        <span class="font-black text-xs">${c.codigo}</span>
        <span class="text-[9px] font-bold tracking-tight uppercase">${sub}</span>
      </div>
    `;
  }).join("");
}

function seleccionarCelda(codigo) {
  const celda = estadoParqueadero.celdas.find(c => c.codigo === codigo);
  if (!celda) return;
  celdaSeleccionadaActual = celda;

  const det = document.getElementById("detalle-celda-seleccionada");
  det.innerHTML = `
    <div class="space-y-4 text-left">
      <div class="flex items-center justify-between border-b pb-2">
        <span class="text-base font-black font-mono-plate text-slate-900">${celda.codigo}</span>
        <span class="text-xs font-bold px-2 py-0.5 rounded ${celda.estado === 'DISPONIBLE' ? 'bg-emerald-100 text-emerald-800' : celda.estado === 'OCUPADA' ? 'bg-rose-100 text-rose-800' : 'bg-amber-100 text-amber-800'}">${celda.estado}</span>
      </div>
      <div class="text-xs space-y-1 text-slate-600">
        <div>Tipo Autorizado: <strong>${celda.tipo_permitido}</strong></div>
        <div>Ubicación: <strong>${celda.zona}</strong> (Piso ${celda.piso})</div>
        ${celda.motivo_bloqueo ? `<div class="text-amber-800 bg-amber-50 p-2 rounded border border-amber-200">Motivo Bloqueo: ${celda.motivo_bloqueo}</div>` : ''}
      </div>
      ${celda.estado === 'OCUPADA' ? `
        <div class="bg-slate-100 p-3 rounded-xl text-xs space-y-1">
          <div class="font-bold text-slate-800">Vehículo Ocupante:</div>
          <div>Placa: <strong class="font-mono-plate">${formatearPlacaVisual(celda.vehiculo_placa)}</strong></div>
          <div>Modelo: ${celda.marca || ''} ${celda.modelo || ''}</div>
          <div>Conductor: ${celda.conductor || 'N/A'}</div>
          <button onclick="ejecutarSalidaDirecta('${celda.vehiculo_placa}')" class="w-full mt-2 bg-rose-600 hover:bg-rose-700 text-white font-bold py-1.5 rounded-lg text-xs">Dar Salida</button>
        </div>
      ` : `
        <div class="pt-2">
          <button onclick="abrirModalEstadoCelda('${celda.codigo}', '${celda.estado}')" class="w-full bg-amber-600 hover:bg-amber-700 text-white font-bold py-2 rounded-xl text-xs">
            Gestionar Estado / Mantenimiento
          </button>
        </div>
      `}
    </div>
  `;
}

// ====================================================================
// 5. GESTIÓN Y MANTENIMIENTO DE CELDAS (CRUD)
// ====================================================================
async function cargarTablaCeldasCrud() {
  const estFiltro = document.getElementById("filtro-crud-estado") ? document.getElementById("filtro-crud-estado").value : "";
  const tipoFiltro = document.getElementById("filtro-crud-tipo") ? document.getElementById("filtro-crud-tipo").value : "";

  try {
    let url = "/api/celdas?";
    if (estFiltro) url += `estado=${estFiltro}&`;
    if (tipoFiltro) url += `tipo=${tipoFiltro}&`;

    const res = await fetch(url);
    const data = await res.json();
    const tbody = document.getElementById("tbody-celdas-crud");

    tbody.innerHTML = data.celdas.map(c => `
      <tr class="hover:bg-slate-50 transition-colors">
        <td class="py-2.5 px-4 font-black font-mono-plate text-slate-900">${c.codigo}</td>
        <td class="py-2.5 px-4">
          <span class="px-2 py-0.5 rounded text-[10px] font-black ${c.tipo_permitido === 'CARRO' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}">${c.tipo_permitido}</span>
        </td>
        <td class="py-2.5 px-4 text-slate-600">${c.zona} (Piso ${c.piso})</td>
        <td class="py-2.5 px-4">
          <span class="px-2 py-0.5 rounded text-[10px] font-black ${c.estado === 'DISPONIBLE' ? 'bg-emerald-100 text-emerald-800' : c.estado === 'OCUPADA' ? 'bg-rose-100 text-rose-800' : 'bg-amber-100 text-amber-800'}">${c.estado}</span>
        </td>
        <td class="py-2.5 px-4 text-slate-700">
          ${c.ocupante_placa ? `<span class="font-mono-plate font-bold bg-slate-100 px-1.5 py-0.5 rounded">${formatearPlacaVisual(c.ocupante_placa)}</span> (${c.ocupante_conductor || ''})` : '<span class="text-slate-400">--</span>'}
        </td>
        <td class="py-2.5 px-4 text-slate-500 italic max-w-xs truncate">${c.motivo_bloqueo || '--'}</td>
        <td class="py-2.5 px-4 text-center">
          ${c.estado === 'OCUPADA' ? `
            <button onclick="abrirModalReubicarConPlaca('${c.ocupante_placa}')" class="bg-indigo-100 text-indigo-700 hover:bg-indigo-200 font-bold px-2 py-1 rounded text-[10px]">Reubicar</button>
          ` : `
            <button onclick="abrirModalEstadoCelda('${c.codigo}', '${c.estado}')" class="bg-amber-100 text-amber-800 hover:bg-amber-200 font-bold px-2 py-1 rounded text-[10px]">Cambiar Estado</button>
          `}
        </td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Error cargando tabla de celdas:", err);
  }
}

function abrirModalEstadoCelda(codigo, estadoActual) {
  document.getElementById("modal-celda-codigo").value = codigo;
  document.getElementById("modal-celda-nuevo-estado").value = estadoActual === 'MANTENIMIENTO' ? 'DISPONIBLE' : 'MANTENIMIENTO';
  document.getElementById("modal-celda-motivo").value = "";
  document.getElementById("modal-estado-celda").classList.remove("hidden");
}

async function guardarEstadoCelda() {
  const codigo = document.getElementById("modal-celda-codigo").value;
  const nuevo_estado = document.getElementById("modal-celda-nuevo-estado").value;
  const motivo = document.getElementById("modal-celda-motivo").value;

  try {
    const res = await fetch("/api/celdas/estado", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        codigo: codigo,
        nuevo_estado: nuevo_estado,
        motivo: motivo,
        usuario_id: usuarioActivo.id
      })
    });
    const data = await res.json();
    if (data.success) {
      alert(data.mensaje);
      cerrarModal("modal-estado-celda");
      cargarEstadoParqueadero();
      cargarTablaCeldasCrud();
    } else {
      alert("Error: " + data.mensaje);
    }
  } catch (err) {
    alert("Error de red: " + err);
  }
}

// ====================================================================
// 6. REUBICACIÓN VEHICULAR (ITERACIÓN 2)
// ====================================================================
function abrirModalReubicar() {
  poblarSelectReubicarVehiculos();
  document.getElementById("modal-reubicar-vehiculo").classList.remove("hidden");
}

function abrirModalReubicarConPlaca(placa) {
  abrirModalReubicar();
  const sel = document.getElementById("modal-reubicar-placa");
  sel.value = placa;
  actualizarCeldasLibresParaReubicacion();
}

function poblarSelectReubicarVehiculos() {
  const sel = document.getElementById("modal-reubicar-placa");
  const adentro = estadoParqueadero.vehiculos_adentro || [];
  if (adentro.length === 0) {
    sel.innerHTML = `<option value="">No hay vehículos adentro para reubicar</option>`;
    return;
  }
  sel.innerHTML = adentro.map(v => `
    <option value="${v.vehiculo_placa}">
      ${formatearPlacaVisual(v.vehiculo_placa)} (${v.tipo_vehiculo}) - Celda Actual: ${v.celda_codigo}
    </option>
  `).join("");
  actualizarCeldasLibresParaReubicacion();
}

function actualizarCeldasLibresParaReubicacion() {
  const selPlaca = document.getElementById("modal-reubicar-placa").value;
  const selNueva = document.getElementById("modal-reubicar-nueva-celda");
  const adentro = estadoParqueadero.vehiculos_adentro.find(v => v.vehiculo_placa === selPlaca);

  if (!adentro) {
    selNueva.innerHTML = `<option value="">Seleccione primero un vehículo</option>`;
    return;
  }

  const libres = estadoParqueadero.celdas.filter(c => c.tipo_permitido === adentro.tipo_vehiculo && c.estado === 'DISPONIBLE');
  if (libres.length === 0) {
    selNueva.innerHTML = `<option value="">No hay celdas libres disponibles para ${adentro.tipo_vehiculo}s</option>`;
    return;
  }

  selNueva.innerHTML = libres.map(c => `
    <option value="${c.codigo}">Celda ${c.codigo} (${c.zona} - Piso ${c.piso})</option>
  `).join("");
}

async function ejecutarReubicacion() {
  const placa = document.getElementById("modal-reubicar-placa").value;
  const nueva_celda = document.getElementById("modal-reubicar-nueva-celda").value;
  const motivo = document.getElementById("modal-reubicar-motivo").value;
  const marcar_maint = document.getElementById("modal-reubicar-marcar-maint").checked;

  if (!placa || !nueva_celda) {
    alert("Debe seleccionar un vehículo y la nueva celda.");
    return;
  }

  try {
    const res = await fetch("/api/celdas/reubicar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        placa: placa,
        nueva_celda: nueva_celda,
        motivo: motivo,
        marcar_anterior_mantenimiento: marcar_maint,
        usuario_id: usuarioActivo.id
      })
    });
    const data = await res.json();
    if (data.success) {
      alert(`🔄 REUBICACIÓN EXITOSA\n\n${data.mensaje}`);
      cerrarModal("modal-reubicar-vehiculo");
      cargarEstadoParqueadero();
      cargarTablaCeldasCrud();
    } else {
      alert("Error en reubicación: " + data.mensaje);
    }
  } catch (err) {
    alert("Error de conexión: " + err);
  }
}

// ====================================================================
// 7. GESTIÓN DE USUARIOS Y ROLES (RBAC - ITERACIÓN 2)
// ====================================================================
async function cargarTablaUsuarios() {
  try {
    const res = await fetch("/api/usuarios");
    const data = await res.json();
    const tbody = document.getElementById("tbody-usuarios");

    tbody.innerHTML = data.usuarios.map(u => `
      <tr class="hover:bg-slate-50 transition-colors">
        <td class="py-2.5 px-4 font-bold text-slate-500">#${u.id}</td>
        <td class="py-2.5 px-4 font-mono-plate font-black text-slate-900">${u.username}</td>
        <td class="py-2.5 px-4 font-bold text-slate-800">${u.nombre_completo}</td>
        <td class="py-2.5 px-4 text-slate-600">${u.email}</td>
        <td class="py-2.5 px-4">
          <span class="px-2 py-0.5 rounded text-[10px] font-black ${u.rol === 'ADMIN' ? 'bg-purple-100 text-purple-800' : u.rol === 'OPERARIO' ? 'bg-blue-100 text-blue-800' : 'bg-emerald-100 text-emerald-800'}">${u.rol}</span>
        </td>
        <td class="py-2.5 px-4 text-slate-600">${u.cargo || 'Operador'}</td>
        <td class="py-2.5 px-4">
          <span class="px-2 py-0.5 rounded text-[10px] font-black ${u.activo ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}">${u.activo ? 'ACTIVO' : 'INACTIVO'}</span>
        </td>
        <td class="py-2.5 px-4 text-slate-500 text-[11px]">${u.ultimo_login || 'Sin inicios'}</td>
        <td class="py-2.5 px-4 text-center">
          <button onclick="alternarActivoUsuario(${u.id}, ${u.activo ? 0 : 1})" class="text-[10px] font-bold px-2 py-1 rounded ${u.activo ? 'bg-rose-50 text-rose-700 hover:bg-rose-100' : 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100'}">
            ${u.activo ? 'Suspender' : 'Activar'}
          </button>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Error cargando usuarios:", err);
  }
}

function abrirModalNuevoUsuario() {
  document.getElementById("modal-user-username").value = "";
  document.getElementById("modal-user-password").value = "";
  document.getElementById("modal-user-nombre").value = "";
  document.getElementById("modal-user-email").value = "";
  document.getElementById("modal-nuevo-usuario").classList.remove("hidden");
}

async function guardarNuevoUsuario() {
  const username = document.getElementById("modal-user-username").value;
  const password = document.getElementById("modal-user-password").value;
  const nombre = document.getElementById("modal-user-nombre").value;
  const email = document.getElementById("modal-user-email").value;
  const rol = document.getElementById("modal-user-rol").value;
  const cargo = document.getElementById("modal-user-cargo").value;

  try {
    const res = await fetch("/api/usuarios", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: username,
        password: password,
        nombre_completo: nombre,
        email: email,
        rol: rol,
        cargo: cargo,
        admin_id: usuarioActivo.id
      })
    });
    const data = await res.json();
    if (data.success) {
      alert(data.mensaje);
      cerrarModal("modal-nuevo-usuario");
      cargarTablaUsuarios();
    } else {
      alert("Error: " + data.mensaje);
    }
  } catch (err) {
    alert("Error de red: " + err);
  }
}

async function alternarActivoUsuario(id, nuevoEstado) {
  if (!confirm(`¿Confirma el cambio de estado de la cuenta #${id}?`)) return;
  try {
    const res = await fetch("/api/usuarios/actualizar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: id,
        activo: nuevoEstado,
        admin_id: usuarioActivo.id
      })
    });
    const data = await res.json();
    if (data.success) {
      alert(data.mensaje);
      cargarTablaUsuarios();
    } else {
      alert("Error: " + data.mensaje);
    }
  } catch (err) {
    alert("Error: " + err);
  }
}

// ====================================================================
// 8. AUDITORÍA Y TRAZABILIDAD (BITÁCORA 24/7)
// ====================================================================
async function cargarAuditoria() {
  try {
    const res = await fetch("/api/auditoria?limite=50");
    const data = await res.json();
    const tbody = document.getElementById("tbody-auditoria");

    tbody.innerHTML = data.auditoria.map(a => `
      <tr class="hover:bg-slate-50 transition-colors">
        <td class="py-2.5 px-4 font-mono-plate text-slate-500">${a.fecha}</td>
        <td class="py-2.5 px-4 font-bold text-slate-800">${a.nombre_completo || a.username || 'Sistema'}</td>
        <td class="py-2.5 px-4">
          <span class="px-2 py-0.5 rounded text-[10px] font-black bg-slate-100 text-slate-800">${a.modulo}</span>
        </td>
        <td class="py-2.5 px-4 font-black text-xs text-blue-700">${a.accion}</td>
        <td class="py-2.5 px-4 text-slate-600">${a.detalle}</td>
        <td class="py-2.5 px-4 text-slate-400 text-[11px]">${a.ip_terminal || 'Terminal'}</td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Error cargando auditoría:", err);
  }
}

// ====================================================================
// 9. ABONADOS Y MODALES AUXILIARES
// ====================================================================
function renderizarTablaAbonados(abonados) {
  const tbody = document.getElementById("tbody-abonados");
  if (!tbody || !abonados) return;

  tbody.innerHTML = abonados.map(a => `
    <tr class="hover:bg-slate-50 transition-colors">
      <td class="py-2.5 px-4 font-mono-plate font-black text-slate-900">${formatearPlacaVisual(a.placa)}</td>
      <td class="py-2.5 px-4">
        <span class="font-bold text-slate-800">${a.marca} ${a.modelo}</span>
        <div class="text-[10px] text-slate-500">${a.tipo_vehiculo} • ${a.color}</div>
      </td>
      <td class="py-2.5 px-4">
        <div class="font-bold text-slate-800">${a.nombre_completo}</div>
        <div class="text-[10px] text-slate-500">Tel: ${a.telefono || 'N/A'} • CC: ${a.documento}</div>
      </td>
      <td class="py-2.5 px-4 font-extrabold text-slate-700">$${Number(a.valor_pagado || 0).toLocaleString()} COP</td>
      <td class="py-2.5 px-4 text-slate-600">
        <div>Vence: ${a.fecha_vencimiento || '--'}</div>
        <div class="text-[10px] ${a.al_dia ? 'text-emerald-600' : 'text-rose-600 font-bold'}">${a.al_dia ? `${a.dias_restantes} días vigentes` : `Vencida (${Math.abs(a.dias_restantes)} días)`}</div>
      </td>
      <td class="py-2.5 px-4">
        <span class="px-2 py-0.5 rounded text-[10px] font-black ${a.al_dia ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}">${a.al_dia ? 'AL DÍA' : 'VENCIDA'}</span>
      </td>
      <td class="py-2.5 px-4 text-center">
        <button onclick="probarPlaca('${formatearPlacaVisual(a.placa)}'); cambiarVista('view-control')" class="bg-blue-50 text-blue-700 hover:bg-blue-100 px-2.5 py-1 rounded text-[10px] font-bold">
          Probar en Cabina
        </button>
      </td>
    </tr>
  `).join("");
}

function abrirModalNuevoAbonado() {
  document.getElementById("modal-ab-placa").value = "";
  document.getElementById("modal-ab-marca").value = "";
  document.getElementById("modal-ab-modelo").value = "";
  document.getElementById("modal-ab-color").value = "";
  document.getElementById("modal-ab-conductor").value = "";
  document.getElementById("modal-ab-documento").value = "";
  document.getElementById("modal-ab-telefono").value = "";
  document.getElementById("modal-nuevo-abonado").classList.remove("hidden");
}

async function guardarNuevoAbonado() {
  const placa = document.getElementById("modal-ab-placa").value;
  const tipo = document.getElementById("modal-ab-tipo").value;
  const marca = document.getElementById("modal-ab-marca").value;
  const modelo = document.getElementById("modal-ab-modelo").value;
  const color = document.getElementById("modal-ab-color").value;
  const conductor = document.getElementById("modal-ab-conductor").value;
  const documento = document.getElementById("modal-ab-documento").value;
  const telefono = document.getElementById("modal-ab-telefono").value;
  const estado_pago = document.getElementById("modal-ab-estado-pago").value;

  try {
    const res = await fetch("/api/abonado", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        placa: placa,
        tipo_vehiculo: tipo,
        marca: marca,
        modelo: modelo,
        color: color,
        conductor: conductor,
        documento: documento,
        telefono: telefono,
        estado_pago: estado_pago,
        usuario_id: usuarioActivo.id
      })
    });
    const data = await res.json();
    if (data.success) {
      alert("Abonado registrado exitosamente.");
      cerrarModal("modal-nuevo-abonado");
      cargarEstadoParqueadero();
    } else {
      alert("Error: " + (data.error || data.mensaje));
    }
  } catch (err) {
    alert("Error de conexión: " + err);
  }
}

function cerrarModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add("hidden");
}

function formatearPlacaVisual(p) {
  if (!p) return "";
  let c = p.replace(/[^a-zA-Z0-9]/g, '').toUpperCase();
  if (c.length === 6) return c.slice(0, 3) + '-' + c.slice(3);
  return c;
}
