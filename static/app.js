/**
 * Lógica Cliente e Interactividad - Autos Colombia 24/7
 * Iteración 1: Entrada, Salida, Novedades y 80 Celdas Dinámicas
 * Docente: Reinaldo Rojas
 */

let estadoParqueadero = {
  capacidad_total: 80,
  total_ocupadas: 0,
  total_libres: 80,
  carros: { total: 70, ocupadas: 0, libres: 70 },
  motos: { total: 10, ocupadas: 0, libres: 10 },
  vehiculos_adentro: [],
  celdas: [],
  abonados: [],
  historial: []
};

let vehiculoConsultado = null;
let filtroMapaActual = 'TODOS';

// ====================================================================
// 1. INICIALIZACIÓN Y EVENT LISTENERS
// ====================================================================
document.addEventListener("DOMContentLoaded", () => {
  iniciarReloj();
  cargarEstadoParqueadero();
  consultarPlaca(); // Cargar la placa inicial por defecto (ABC-123)

  // Polling automático cada 4 segundos para sincronización en tiempo real entre múltiples operarios
  setInterval(cargarEstadoParqueadero, 4000);
});

function iniciarReloj() {
  const el = document.getElementById("reloj-vivo");
  function actualizar() {
    const ahora = new Date();
    const opciones = { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' };
    el.innerText = ahora.toLocaleTimeString('es-CO', opciones) + " · 24/7 Activo";
  }
  actualizar();
  setInterval(actualizar, 1000);
}

function setNovedad(texto) {
  const input = document.getElementById("input-observaciones-ingreso");
  if (input) input.value = texto;
}

function getPuertaActiva() {
  const sel = document.getElementById("select-puerta-operario");
  return sel ? sel.value : "Puerta 1 - Norte";
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
}

// ====================================================================
// 2. COMUNICACIÓN CON LA API REST
// ====================================================================

async function cargarEstadoParqueadero() {
  try {
    const res = await fetch("/api/resumen");
    if (!res.ok) throw new Error("Error consultando estado");
    estadoParqueadero = await res.json();
    renderizarTodo();
  } catch (err) {
    console.error("Error al cargar estado del parqueadero:", err);
  }
}

function renderizarTodo() {
  actualizarMetricas();
  renderizarVehiculosAdentro();
  renderizarGrillaCeldas();
  renderizarAbonados();
  renderizarHistorial();
}

function actualizarMetricas() {
  const { total_ocupadas, total_libres, carros, motos } = estadoParqueadero;
  
  document.getElementById("side-badge-libres").innerText = `● ${total_libres} Libres`;
  document.getElementById("side-ocupadas-total").innerText = `${total_ocupadas} Ocupadas`;
  const porcentaje = ((total_ocupadas / 80) * 100).toFixed(0);
  document.getElementById("side-progress-bar").style.width = `${porcentaje}%`;

  document.getElementById("card-carros-libres").innerText = `${carros.libres} Libres`;
  document.getElementById("card-motos-libres").innerText = `${motos.libres} Libres`;

  document.getElementById("metric-libres-mapa").innerHTML = `${total_libres} <span class="text-sm font-semibold text-emerald-100">disponibles</span>`;
  document.getElementById("metric-sub-libres").innerText = `${carros.libres} Carros · ${motos.libres} Motos`;

  document.getElementById("metric-ocupadas-mapa").innerHTML = `${total_ocupadas} <span class="text-sm font-semibold text-rose-100">en uso</span>`;
  document.getElementById("metric-sub-ocupadas").innerText = `${carros.ocupadas} Carros · ${motos.ocupadas} Motos`;

  document.getElementById("contador-adentro-badge").innerText = estadoParqueadero.vehiculos_adentro.length;
  document.getElementById("lbl-total-vehiculos-adentro").innerText = `Mostrando ${estadoParqueadero.vehiculos_adentro.length} vehículos`;
}

// ====================================================================
// 3. CONSULTA Y VERIFICACIÓN DE VEHÍCULO (ENTRADA)
// ====================================================================

function onPlacaInput() {
  const input = document.getElementById("input-placa");
  let val = input.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
  if (val.length > 3) {
    val = val.slice(0, 3) + '-' + val.slice(3, 6);
  }
  input.value = val;
}

function cargarPlacaTest(placa) {
  document.getElementById("input-placa").value = placa;
  document.getElementById("input-observaciones-ingreso").value = "";
  consultarPlaca();
}

async function consultarPlaca() {
  const placa = document.getElementById("input-placa").value.trim();
  const feedback = document.getElementById("feedback-entrada");
  feedback.classList.add("hidden");

  if (!placa) return;

  try {
    const res = await fetch(`/api/vehiculo?placa=${encodeURIComponent(placa)}`);
    if (res.ok) {
      vehiculoConsultado = await res.json();
      mostrarFichaVehiculo(vehiculoConsultado);
    } else {
      vehiculoConsultado = null;
      mostrarVehiculoNoEncontrado(placa);
    }
  } catch (e) {
    console.error("Error al consultar placa:", e);
  }
}

function mostrarFichaVehiculo(v) {
  const esCarro = v.tipo_vehiculo === 'CARRO';
  document.getElementById("ficha-icono").innerText = esCarro ? '🚗' : '🏍️';
  document.getElementById("ficha-modelo").innerText = `${v.marca} ${v.modelo}`;
  document.getElementById("ficha-detalles").innerText = `Marca: ${v.marca} · Modelo: ${v.modelo} · Color: ${v.color}`;
  document.getElementById("ficha-conductor").innerText = `${v.propietario_nombre} (Tel: ${v.propietario_telefono})`;
  document.getElementById("ficha-tag-tipo").innerText = v.tipo_vehiculo;

  const alerta = document.getElementById("alerta-mensualidad");
  const alertaIcono = document.getElementById("alerta-icono");
  const alertaTitulo = document.getElementById("alerta-titulo");
  const alertaSubtitulo = document.getElementById("alerta-subtitulo");
  const alertaBadge = document.getElementById("alerta-badge");
  const btnIngreso = document.getElementById("btn-autorizar-entrada");
  const btnSalidaDirecta = document.getElementById("btn-salida-directa");

  const m = v.mensualidad;

  if (v.esta_adentro) {
    alerta.className = "mt-3 p-3 rounded-xl bg-amber-500 text-white flex items-center justify-between shadow-sm";
    alertaIcono.innerText = "🅿️";
    alertaTitulo.innerText = `ESTACIONADO ACTUALMENTE EN CELDA ${v.registro_actual.celda_codigo}`;
    alertaSubtitulo.innerText = `Soporte #${v.registro_actual.id} · Ingresó: ${v.registro_actual.fecha_ingreso}`;
    alertaBadge.innerText = "Adentro";
    alertaBadge.className = "text-[10px] font-black uppercase px-2 py-0.5 rounded bg-white text-amber-800";

    btnIngreso.disabled = true;
    btnIngreso.className = "w-full bg-slate-200 text-slate-400 font-black py-3 px-6 rounded-2xl text-sm flex items-center justify-center gap-2 cursor-not-allowed shadow-none";
    btnSalidaDirecta.classList.remove("hidden");
    btnSalidaDirecta.classList.add("flex");
    return;
  }

  btnSalidaDirecta.classList.add("hidden");
  btnSalidaDirecta.classList.remove("flex");

  if (m && m.al_dia) {
    alerta.className = "mt-3 p-3 rounded-xl bg-emerald-500 text-white flex items-center justify-between shadow-sm";
    alertaIcono.innerText = "✓";
    alertaTitulo.innerText = "MENSUALIDAD VIGENTE - AL DÍA";
    alertaSubtitulo.innerText = `Pago: ${m.fecha_pago} · Vence: ${m.fecha_vencimiento} (${m.dias_restantes} días restantes)`;
    alertaBadge.innerText = "Autorizado";
    alertaBadge.className = "text-[10px] font-black uppercase px-2 py-0.5 rounded bg-white text-emerald-800";

    btnIngreso.disabled = false;
    btnIngreso.className = "w-full bg-emerald-600 hover:bg-emerald-500 text-white font-black py-3.5 px-6 rounded-2xl text-base flex items-center justify-center gap-3 shadow-lg shadow-emerald-600/25 transition-all transform active:scale-98 cursor-pointer";
  } else {
    const fVenc = m ? m.fecha_vencimiento : "Sin pago";
    alerta.className = "mt-3 p-3 rounded-xl bg-rose-600 text-white flex items-center justify-between shadow-sm";
    alertaIcono.innerText = "⛔";
    alertaTitulo.innerText = "MENSUALIDAD VENCIDA - ACCESO DENEGADO";
    alertaSubtitulo.innerText = `Venció el ${fVenc}. Sin periodo de gracia: debe renovar suscripción.`;
    alertaBadge.innerText = "En Mora";
    alertaBadge.className = "text-[10px] font-black uppercase px-2 py-0.5 rounded bg-white text-rose-800";

    btnIngreso.disabled = true;
    btnIngreso.className = "w-full bg-slate-300 text-slate-500 font-black py-3.5 px-6 rounded-2xl text-base flex items-center justify-center gap-3 cursor-not-allowed shadow-none";
  }
}

function mostrarVehiculoNoEncontrado(placa) {
  document.getElementById("ficha-icono").innerText = '❓';
  document.getElementById("ficha-modelo").innerText = `Placa no registrada: ${placa}`;
  document.getElementById("ficha-detalles").innerText = "Solo se permite el ingreso a vehículos con mensualidad registrada";
  document.getElementById("ficha-conductor").innerText = "No figura en el padrón de abonados";
  document.getElementById("ficha-tag-tipo").innerText = "NO REGISTRADO";

  const alerta = document.getElementById("alerta-mensualidad");
  alerta.className = "mt-3 p-3 rounded-xl bg-slate-700 text-white flex items-center justify-between shadow-sm";
  document.getElementById("alerta-icono").innerText = "✕";
  document.getElementById("alerta-titulo").innerText = "VEHÍCULO NO REGISTRADO";
  document.getElementById("alerta-subtitulo").innerText = "El parqueadero opera exclusivamente por mensualidad";
  const badge = document.getElementById("alerta-badge");
  badge.innerText = "Sin Acceso";
  badge.className = "text-[10px] font-black uppercase px-2 py-0.5 rounded bg-white text-slate-900";

  const btnIngreso = document.getElementById("btn-autorizar-entrada");
  btnIngreso.disabled = true;
  btnIngreso.className = "w-full bg-slate-300 text-slate-500 font-black py-3.5 px-6 rounded-2xl text-base flex items-center justify-center gap-3 cursor-not-allowed shadow-none";

  const btnSalidaDirecta = document.getElementById("btn-salida-directa");
  btnSalidaDirecta.classList.add("hidden");
  btnSalidaDirecta.classList.remove("flex");
}

// ====================================================================
// 4. EJECUTAR INGRESO (APERTURA DE BARRERA Y ASIGNACIÓN ALEATORIA)
// ====================================================================

async function ejecutarIngreso() {
  const placa = document.getElementById("input-placa").value.trim();
  const obs = document.getElementById("input-observaciones-ingreso").value.trim();
  const puerta = getPuertaActiva();
  const feedback = document.getElementById("feedback-entrada");

  if (!placa) return;

  try {
    const res = await fetch("/api/ingreso", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ placa: placa, observaciones: obs, puerta: puerta })
    });
    const data = await res.json();

    feedback.classList.remove("hidden");
    if (data.success) {
      feedback.className = "text-center text-xs font-bold text-emerald-800 mt-2 p-3 bg-emerald-50 border border-emerald-300 rounded-xl shadow-sm";
      feedback.innerHTML = `
        🎉 <strong>¡BARRERA ABIERTA! (Soporte #${data.registro_id})</strong><br/>
        📍 <strong>Celda Asignada Dinámicamente: <span class="text-sm font-mono-plate underline">${data.celda_asignada}</span></strong> (${data.zona})<br/>
        <span class="text-[11px] text-emerald-700">${data.observaciones}</span>
      `;
      document.getElementById("input-observaciones-ingreso").value = "";
      await cargarEstadoParqueadero();
      consultarPlaca();
    } else {
      feedback.className = "text-center text-xs font-bold text-rose-700 mt-2 p-2.5 bg-rose-50 border border-rose-200 rounded-xl";
      feedback.innerHTML = `⛔ <strong>ACCESO DENEGADO:</strong> ${data.mensaje}`;
    }
  } catch (err) {
    console.error("Error al ejecutar ingreso:", err);
  }
}

async function ejecutarSalidaDesdePanel() {
  const placa = document.getElementById("input-placa").value.trim();
  const obs = document.getElementById("input-observaciones-ingreso").value.trim();
  if (!placa) return;
  await ejecutarSalida(placa, obs);
}

// ====================================================================
// 5. VEHÍCULOS ADENTRO Y SALIDA RÁPIDA
// ====================================================================

function renderizarVehiculosAdentro() {
  const cont = document.getElementById("lista-vehiculos-adentro");
  const filtro = (document.getElementById("input-filtro-adentro").value || "").toLowerCase();
  const vehiculos = estadoParqueadero.vehiculos_adentro || [];

  const filtrados = vehiculos.filter(v => {
    const idStr = `#${v.registro_id}`;
    return v.vehiculo_placa.toLowerCase().includes(filtro) ||
           idStr.includes(filtro) ||
           v.marca.toLowerCase().includes(filtro) ||
           v.modelo.toLowerCase().includes(filtro) ||
           v.celda_codigo.toLowerCase().includes(filtro) ||
           v.conductor.toLowerCase().includes(filtro);
  });

  if (filtrados.length === 0) {
    cont.innerHTML = `
      <div class="text-center py-10 bg-slate-50 rounded-xl border border-dashed border-slate-200 text-slate-400">
        <div class="text-3xl mb-1">🅿️</div>
        <div class="font-bold text-xs">No hay vehículos estacionados que coincidan</div>
        <div class="text-[11px]">Los vehículos que ingresen aparecerán aquí con su soporte, celda y estado físico.</div>
      </div>
    `;
    return;
  }

  cont.innerHTML = filtrados.map(v => {
    const esCarro = v.tipo_vehiculo === 'CARRO';
    return `
      <div class="bg-slate-50 hover:bg-white border border-slate-200 hover:border-blue-400 rounded-xl p-3.5 flex items-center justify-between transition-all shadow-sm group">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg ${esCarro ? 'bg-blue-100 text-blue-700' : 'bg-emerald-100 text-emerald-700'} flex items-center justify-center text-xl font-bold">
            ${esCarro ? '🚗' : '🏍️'}
          </div>
          <div>
            <div class="flex items-center gap-2 flex-wrap">
              <span class="text-[10px] font-black bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded font-mono-plate">#${v.registro_id}</span>
              <span class="font-mono-plate font-black text-slate-900 text-sm bg-white px-2 py-0.5 rounded border border-slate-200">${v.vehiculo_placa}</span>
              <span class="text-xs font-bold text-slate-800">${v.marca} ${v.modelo} (${v.color})</span>
            </div>
            <div class="text-[11px] text-slate-500 mt-0.5">
              <span>👤 ${v.conductor}</span> · 
              <span class="text-blue-700 font-extrabold">Celda: ${v.celda_codigo}</span> · 
              <span>⏱️ ${v.tiempo_transcurrido}</span>
            </div>
            <div class="text-[10px] text-slate-500 italic mt-0.5">
              📋 ${v.observaciones || 'Sin novedades físicas'}
            </div>
          </div>
        </div>

        <button 
          class="bg-rose-600 hover:bg-rose-500 text-white font-bold px-3.5 py-2 rounded-xl text-xs flex items-center gap-1 shadow-sm transition-all transform active:scale-95 flex-shrink-0"
          onclick="ejecutarSalida('${v.vehiculo_placa}')"
        >
          <span>Dar Salida</span>
          <span>→</span>
        </button>
      </div>
    `;
  }).join('');
}

function filtrarVehiculosAdentro() {
  renderizarVehiculosAdentro();
}

async function ejecutarSalida(placa, obsOpcional = "") {
  const puerta = getPuertaActiva();
  try {
    const res = await fetch("/api/salida", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ placa: placa, observaciones: obsOpcional, puerta: puerta })
    });
    const data = await res.json();

    if (data.success) {
      const feedback = document.getElementById("feedback-entrada");
      feedback.classList.remove("hidden");
      feedback.className = "text-center text-xs font-bold text-blue-800 mt-2 p-3 bg-blue-50 border border-blue-200 rounded-xl shadow-sm";
      feedback.innerHTML = `
        ✓ <strong>SALIDA REGISTRADA (${data.placa})</strong> · Soporte #${data.registro_id}<br/>
        🔓 <strong>Celda ${data.celda_liberada} LIBERADA INMEDIATAMENTE</strong> · Permanencia: ${data.tiempo_permanencia}
      `;
      await cargarEstadoParqueadero();
      consultarPlaca();
    } else {
      alert(`Error al registrar salida: ${data.mensaje}`);
    }
  } catch (err) {
    console.error("Error al registrar salida:", err);
  }
}

// ====================================================================
// 6. MAPA VISUAL DE LAS 80 CELDAS
// ====================================================================

function renderizarGrillaCeldas() {
  const cont = document.getElementById("grilla-celdas");
  const celdas = estadoParqueadero.celdas || [];

  const filtradas = celdas.filter(c => {
    if (filtroMapaActual === 'CARRO') return c.tipo_permitido === 'CARRO';
    if (filtroMapaActual === 'MOTO') return c.tipo_permitido === 'MOTO';
    if (filtroMapaActual === 'DISPONIBLE') return c.estado === 'DISPONIBLE';
    if (filtroMapaActual === 'OCUPADA') return c.estado === 'OCUPADA';
    return true;
  });

  cont.innerHTML = filtradas.map(c => {
    const ocupada = c.estado === 'OCUPADA';
    const esMoto = c.tipo_permitido === 'MOTO';
    const bgClass = ocupada 
      ? 'bg-rose-50 border-rose-300 text-rose-900 hover:border-rose-500' 
      : 'bg-emerald-50 border-emerald-300 text-emerald-900 hover:border-emerald-500';
    
    return `
      <div 
        class="border-2 rounded-xl p-2 text-center cursor-pointer transition-all hover:scale-105 shadow-sm ${bgClass}"
        onclick="seleccionarCelda('${c.codigo}')"
      >
        <div class="text-[10px] font-extrabold uppercase text-slate-500 flex justify-between items-center">
          <span>${esMoto ? '🏍️' : '🚗'}</span>
          <span class="w-2 h-2 rounded-full ${ocupada ? 'bg-rose-500' : 'bg-emerald-500'}"></span>
        </div>
        <div class="font-mono-plate font-black text-sm my-1">${c.codigo}</div>
        <div class="text-[9px] font-bold truncate">
          ${ocupada ? (c.vehiculo_placa || 'Ocupada') : 'Libre'}
        </div>
      </div>
    `;
  }).join('');
}

function filtrarMapa(tipo) {
  filtroMapaActual = tipo;
  renderizarGrillaCeldas();
}

function seleccionarCelda(codigo) {
  const celda = estadoParqueadero.celdas.find(c => c.codigo === codigo);
  if (!celda) return;

  const ocupada = celda.estado === 'OCUPADA';
  document.getElementById("detalle-celda-codigo").innerText = celda.codigo;
  document.getElementById("detalle-celda-tipo").innerText = `${celda.tipo_permitido} · ${celda.zona}`;
  document.getElementById("detalle-celda-piso").innerText = `Piso ${celda.piso}`;

  const badge = document.getElementById("detalle-celda-badge");
  badge.innerText = ocupada ? "Ocupada" : "Disponible";
  badge.className = ocupada 
    ? "px-2 py-0.5 rounded text-xs font-black bg-rose-100 text-rose-800" 
    : "px-2 py-0.5 rounded text-xs font-black bg-emerald-100 text-emerald-800";

  document.getElementById("detalle-celda-placa").innerText = ocupada ? celda.vehiculo_placa : "Ninguna (Libre)";
  document.getElementById("detalle-celda-vehiculo").innerText = ocupada ? `${celda.marca || ''} ${celda.modelo || ''} (${celda.color || ''})` : "-";
  document.getElementById("detalle-celda-conductor").innerText = ocupada ? (celda.conductor || 'Abonado') : "-";
  document.getElementById("detalle-celda-obs").innerText = ocupada ? (celda.observaciones || 'Sin novedades') : "-";

  const btnContainer = document.getElementById("detalle-celda-acciones");
  if (ocupada) {
    btnContainer.innerHTML = `
      <button class="w-full bg-rose-600 hover:bg-rose-700 text-white font-bold py-2.5 rounded-xl text-xs transition" onclick="ejecutarSalida('${celda.vehiculo_placa}')">
        Dar Salida Inmediata a ${celda.vehiculo_placa}
      </button>
    `;
  } else {
    btnContainer.innerHTML = `
      <button class="w-full bg-blue-700 hover:bg-blue-800 text-white font-bold py-2.5 rounded-xl text-xs transition" onclick="cambiarVista('view-control')">
        Ir a Registrar Entrada
      </button>
    `;
  }
}

// ====================================================================
// 7. PADRÓN DE ABONADOS Y HISTORIAL DE AUDITORÍA
// ====================================================================

function renderizarAbonados() {
  const tbody = document.getElementById("tabla-abonados-body");
  if (!tbody) return;
  const abonados = estadoParqueadero.abonados || [];

  tbody.innerHTML = abonados.map(a => {
    const esCarro = a.tipo_vehiculo === 'CARRO';
    const tarifa = a.valor_pagado ? `$${Number(a.valor_pagado).toLocaleString('es-CO')} COP` : (esCarro ? '$250.000 COP' : '$100.000 COP');
    const placaFmt = a.placa.length === 6 ? `${a.placa.slice(0,3)}-${a.placa.slice(3)}` : a.placa;

    return `
      <tr class="hover:bg-slate-50">
        <td class="py-3 px-4 font-mono-plate font-black text-slate-900">${placaFmt}</td>
        <td class="py-3 px-4">
          <span class="${esCarro ? 'bg-blue-100 text-blue-800' : 'bg-emerald-100 text-emerald-800'} px-2 py-0.5 rounded text-[10px] font-bold">
            ${a.tipo_vehiculo}
          </span>
        </td>
        <td class="py-3 px-4 font-bold text-slate-900">${a.marca} ${a.modelo}</td>
        <td class="py-3 px-4 text-slate-600">${a.color}</td>
        <td class="py-3 px-4 text-slate-700">${a.propietario}</td>
        <td class="py-3 px-4 text-slate-600 text-[11px]">
          Pago: ${a.fecha_pago || '-'}<br/>
          <strong class="${a.al_dia ? 'text-emerald-700' : 'text-rose-600'}">Corte: ${a.fecha_vencimiento || '-'}</strong>
        </td>
        <td class="py-3 px-4 font-bold text-slate-900">${tarifa}</td>
        <td class="py-3 px-4">
          ${a.al_dia 
            ? `<span class="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full text-[10px] font-black">● Al Día (+${a.dias_restantes}d)</span>`
            : `<span class="bg-rose-100 text-rose-800 px-2 py-0.5 rounded-full text-[10px] font-black">⛔ VENCIDA (${a.dias_restantes}d)</span>`
          }
        </td>
        <td class="py-3 px-4 text-right">
          <button class="bg-blue-50 text-blue-700 hover:bg-blue-100 font-bold px-2.5 py-1 rounded-md text-[11px]" onclick="cargarPlacaTest('${placaFmt}'); cambiarVista('view-control');">
            Probar en Cabina
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

function renderizarHistorial() {
  const tbody = document.getElementById("tabla-historial-body");
  const hist = estadoParqueadero.historial || [];

  if (hist.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" class="text-center py-6 text-slate-400">Sin movimientos registrados aún en este turno.</td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = hist.map(h => {
    const adentro = h.estado === 'ADENTRO';
    return `
      <tr class="hover:bg-slate-50">
        <td class="py-3 px-4 font-mono-plate font-bold text-slate-500">#${h.id}</td>
        <td class="py-3 px-4">
          <span class="font-mono-plate font-black text-slate-900">${h.vehiculo_placa}</span>
          <span class="text-[11px] text-slate-500 block">${h.marca} ${h.modelo} (${h.color})</span>
        </td>
        <td class="py-3 px-4"><span class="bg-blue-50 text-blue-700 px-2 py-0.5 rounded text-[10px] font-bold">${h.tipo_vehiculo}</span></td>
        <td class="py-3 px-4 font-mono-plate font-black text-blue-700">${h.celda_codigo}</td>
        <td class="py-3 px-4 text-slate-700">${h.fecha_ingreso}</td>
        <td class="py-3 px-4 text-slate-700">${h.fecha_salida || 'Estacionado actualmente'}</td>
        <td class="py-3 px-4 text-slate-600 text-[11px] max-w-xs">${h.observaciones || 'Sin novedades'}</td>
        <td class="py-3 px-4">
          <span class="px-2 py-0.5 rounded-full text-[10px] font-black ${adentro ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'}">
            ● ${adentro ? 'Adentro' : 'Finalizado'}
          </span>
        </td>
      </tr>
    `;
  }).join('');
}

// ====================================================================
// 8. MODAL DE NUEVO ABONADO DE PRUEBA
// ====================================================================

function abrirModalNuevoAbonado() {
  document.getElementById("modal-nuevo-abonado").classList.remove("hidden");
}

function cerrarModalNuevoAbonado() {
  document.getElementById("modal-nuevo-abonado").classList.add("hidden");
}

async function guardarNuevoAbonado() {
  const placa = document.getElementById("modal-input-placa").value.trim();
  const tipo = document.getElementById("modal-select-tipo").value;
  const estadoPago = document.getElementById("modal-select-estado").value;
  const marca = document.getElementById("modal-input-marca").value.trim() || "Genérica";
  const modelo = document.getElementById("modal-input-modelo").value.trim() || "2024";
  const color = document.getElementById("modal-input-color").value.trim() || "Gris";
  const conductor = document.getElementById("modal-input-conductor").value.trim() || "Cliente Abonado";

  if (!placa) {
    alert("Por favor ingresa la placa del vehículo.");
    return;
  }

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
        estado_pago: estadoPago
      })
    });
    const data = await res.json();
    if (data.success) {
      cerrarModalNuevoAbonado();
      await cargarEstadoParqueadero();
      cargarPlacaTest(placa);
      cambiarVista('view-control');
    } else {
      alert("Error al registrar: " + (data.error || data.mensaje));
    }
  } catch (err) {
    console.error("Error al registrar abonado:", err);
  }
}

function abrirModalReglas() {
  document.getElementById("modal-reglas").classList.remove("hidden");
}

function cerrarModalReglas() {
  document.getElementById("modal-reglas").classList.add("hidden");
}
