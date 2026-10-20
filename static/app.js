/**
 * Lógica Cliente e Interactividad - Autos Colombia 24/7
 * Iteración 1: Entrada, Salida y 80 Celdas Dinámicas
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

  // Polling automático cada 10 segundos para mantener sincronización 24/7
  setInterval(cargarEstadoParqueadero, 10000);
});

// Reloj en tiempo real 24/7
function iniciarReloj() {
  const el = document.getElementById("reloj-vivo");
  function actualizar() {
    const ahora = new Date();
    const opciones = { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' };
    el.innerText = ahora.toLocaleTimeString('es-CO', opciones) + " (Turno Activo)";
  }
  actualizar();
  setInterval(actualizar, 1000);
}

// Navegación entre pestañas
function cambiarVista(vistaId) {
  document.querySelectorAll(".view-container").forEach(el => el.classList.remove("active"));
  const target = document.getElementById(vistaId);
  if (target) target.classList.add("active");

  // Actualizar estilos de tabs superiores
  document.querySelectorAll(".nav-tab").forEach(tab => {
    if (tab.getAttribute("data-target") === vistaId) {
      tab.classList.add("bg-blue-600", "text-white");
      tab.classList.remove("text-slate-300", "hover:bg-slate-800");
    } else {
      tab.classList.remove("bg-blue-600", "text-white");
      tab.classList.add("text-slate-300", "hover:bg-slate-800");
    }
  });

  // Actualizar sidebar links
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
  renderizarHistorial();
}

// Actualizar contadores y barras de progreso
function actualizarMetricas() {
  const { total_ocupadas, total_libres, carros, motos } = estadoParqueadero;
  
  // Sidebar
  document.getElementById("side-badge-libres").innerText = `● ${total_libres} Libres`;
  document.getElementById("side-ocupadas-total").innerText = `${total_ocupadas} Ocupadas`;
  const porcentaje = ((total_ocupadas / 80) * 100).toFixed(0);
  document.getElementById("side-progress-bar").style.width = `${porcentaje}%`;

  // Header Cards en Vista 1
  document.getElementById("card-carros-libres").innerText = `${carros.libres} Libres`;
  document.getElementById("card-motos-libres").innerText = `${motos.libres} Libres`;

  // Cards en Vista 2 (Mapa)
  document.getElementById("metric-libres-mapa").innerHTML = `${total_libres} <span class="text-sm font-semibold text-emerald-100">disponibles</span>`;
  document.getElementById("metric-sub-libres").innerText = `${carros.libres} Carros · ${motos.libres} Motos`;

  document.getElementById("metric-ocupadas-mapa").innerHTML = `${total_ocupadas} <span class="text-sm font-semibold text-rose-100">en uso</span>`;
  document.getElementById("metric-sub-ocupadas").innerText = `${carros.ocupadas} Carros · ${motos.ocupadas} Motos`;

  // Badge contador adentro
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
  document.getElementById("ficha-detalles").innerText = `Color: ${v.color} · ${v.tipo_vehiculo}`;
  document.getElementById("ficha-conductor").innerText = v.propietario_nombre;
  document.getElementById("ficha-tag-tipo").innerText = v.tipo_vehiculo;

  const alerta = document.getElementById("alerta-mensualidad");
  const alertaIcono = document.getElementById("alerta-icono");
  const alertaTitulo = document.getElementById("alerta-titulo");
  const alertaSubtitulo = document.getElementById("alerta-subtitulo");
  const alertaBadge = document.getElementById("alerta-badge");
  const btnIngreso = document.getElementById("btn-autorizar-entrada");

  const m = v.mensualidad;

  if (v.esta_adentro) {
    alerta.className = "mt-3.5 p-3 rounded-xl bg-amber-500 text-white flex items-center justify-between shadow-sm";
    alertaIcono.innerText = "⚠️";
    alertaTitulo.innerText = "VEHÍCULO YA SE ENCUENTRA ADENTRO";
    alertaSubtitulo.innerText = `Estacionado actualmente en la celda ${v.registro_actual.celda_codigo}`;
    alertaBadge.innerText = "En Sitio";
    alertaBadge.className = "text-[10px] font-black uppercase px-2 py-0.5 rounded bg-white text-amber-800";
    btnIngreso.disabled = true;
    btnIngreso.className = "w-full bg-slate-300 text-slate-500 font-black py-4 px-6 rounded-2xl text-lg flex items-center justify-center gap-3 cursor-not-allowed shadow-none";
    return;
  }

  if (m && m.al_dia) {
    // Al Día
    alerta.className = "mt-3.5 p-3 rounded-xl bg-emerald-500 text-white flex items-center justify-between shadow-sm";
    alertaIcono.innerText = "✓";
    alertaTitulo.innerText = "MENSUALIDAD VIGENTE - AL DÍA";
    alertaSubtitulo.innerText = `Cubre hasta ${m.fecha_vencimiento} (${m.dias_restantes} días restantes)`;
    alertaBadge.innerText = "Autorizado";
    alertaBadge.className = "text-[10px] font-black uppercase px-2 py-0.5 rounded bg-white text-emerald-800";

    btnIngreso.disabled = false;
    btnIngreso.className = "w-full bg-emerald-600 hover:bg-emerald-500 text-white font-black py-4 px-6 rounded-2xl text-lg flex items-center justify-center gap-3 shadow-lg shadow-emerald-600/25 transition-all transform active:scale-98 cursor-pointer";
  } else {
    // Vencida
    const fVenc = m ? m.fecha_vencimiento : "Sin pago";
    alerta.className = "mt-3.5 p-3 rounded-xl bg-rose-600 text-white flex items-center justify-between shadow-sm";
    alertaIcono.innerText = "⛔";
    alertaTitulo.innerText = "MENSUALIDAD VENCIDA - ACCESO DENEGADO";
    alertaSubtitulo.innerText = `Fecha de vencimiento: ${fVenc}. Debe renovar la suscripción.`;
    alertaBadge.innerText = "En Mora";
    alertaBadge.className = "text-[10px] font-black uppercase px-2 py-0.5 rounded bg-white text-rose-800";

    btnIngreso.disabled = true;
    btnIngreso.className = "w-full bg-slate-300 text-slate-500 font-black py-4 px-6 rounded-2xl text-lg flex items-center justify-center gap-3 cursor-not-allowed shadow-none";
  }
}

function mostrarVehiculoNoEncontrado(placa) {
  document.getElementById("ficha-icono").innerText = '❓';
  document.getElementById("ficha-modelo").innerText = `Placa no registrada: ${placa}`;
  document.getElementById("ficha-detalles").innerText = "Solo se permite el ingreso a vehículos suscritos";
  document.getElementById("ficha-conductor").innerText = "No registrado en el sistema";
  document.getElementById("ficha-tag-tipo").innerText = "DESCONOCIDO";

  const alerta = document.getElementById("alerta-mensualidad");
  alerta.className = "mt-3.5 p-3 rounded-xl bg-slate-700 text-white flex items-center justify-between shadow-sm";
  document.getElementById("alerta-icono").innerText = "✕";
  document.getElementById("alerta-titulo").innerText = "VEHÍCULO NO REGISTRADO";
  document.getElementById("alerta-subtitulo").innerText = "El parqueadero opera exclusivamente por mensualidad";
  const badge = document.getElementById("alerta-badge");
  badge.innerText = "Sin Acceso";
  badge.className = "text-[10px] font-black uppercase px-2 py-0.5 rounded bg-white text-slate-900";

  const btnIngreso = document.getElementById("btn-autorizar-entrada");
  btnIngreso.disabled = true;
  btnIngreso.className = "w-full bg-slate-300 text-slate-500 font-black py-4 px-6 rounded-2xl text-lg flex items-center justify-center gap-3 cursor-not-allowed shadow-none";
}

// ====================================================================
// 4. EJECUTAR INGRESO (APERTURA DE BARRERA Y ASIGNACIÓN ALEATORIA)
// ====================================================================

async function ejecutarIngreso() {
  const placa = document.getElementById("input-placa").value.trim();
  const feedback = document.getElementById("feedback-entrada");

  if (!placa) return;

  try {
    const res = await fetch("/api/ingreso", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ placa: placa })
    });
    const data = await res.json();

    feedback.classList.remove("hidden");
    if (data.success) {
      feedback.className = "text-center text-xs font-bold text-emerald-700 mt-2 p-2 bg-emerald-50 border border-emerald-200 rounded-xl animate-bounce";
      feedback.innerHTML = `🎉 <strong>¡BARRERA ABIERTA!</strong> ${data.mensaje} <br/>📍 <strong>Celda Asignada Aleatoriamente: ${data.celda_asignada}</strong> (${data.zona})`;
      
      // Refrescar estado y consulta de placa
      await cargarEstadoParqueadero();
      consultarPlaca();
    } else {
      feedback.className = "text-center text-xs font-bold text-rose-700 mt-2 p-2 bg-rose-50 border border-rose-200 rounded-xl";
      feedback.innerHTML = `⛔ <strong>ACCESO DENEGADO:</strong> ${data.mensaje}`;
    }
  } catch (err) {
    console.error("Error al ejecutar ingreso:", err);
  }
}

// ====================================================================
// 5. VEHÍCULOS ADENTRO Y SALIDA RÁPIDA
// ====================================================================

function renderizarVehiculosAdentro() {
  const cont = document.getElementById("lista-vehiculos-adentro");
  const filtro = (document.getElementById("input-filtro-adentro").value || "").toLowerCase();
  const vehiculos = estadoParqueadero.vehiculos_adentro || [];

  const filtrados = vehiculos.filter(v => {
    return v.vehiculo_placa.toLowerCase().includes(filtro) ||
           v.marca.toLowerCase().includes(filtro) ||
           v.modelo.toLowerCase().includes(filtro) ||
           v.celda_codigo.toLowerCase().includes(filtro) ||
           v.conductor.toLowerCase().includes(filtro);
  });

  if (filtrados.length === 0) {
    cont.innerHTML = `
      <div class="text-center py-10 bg-slate-50 rounded-xl border border-dashed border-slate-200 text-slate-400">
        <div class="text-3xl mb-1">🅿️</div>
        <div class="font-bold text-xs">No hay vehículos estacionados actualmente</div>
        <div class="text-[11px]">Los vehículos que ingresen aparecerán aquí para control de salida rápida.</div>
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
            <div class="flex items-center gap-2">
              <span class="font-mono-plate font-black text-slate-900 text-sm bg-white px-2 py-0.5 rounded border border-slate-200">${v.vehiculo_placa}</span>
              <span class="text-xs font-bold text-slate-700">${v.marca} ${v.modelo}</span>
            </div>
            <div class="text-[11px] text-slate-500 mt-0.5">
              <span>👤 ${v.conductor}</span> · 
              <span class="text-blue-700 font-bold">Celda: ${v.celda_codigo}</span> · 
              <span>⏱️ ${v.tiempo_transcurrido}</span>
            </div>
          </div>
        </div>

        <button 
          class="bg-rose-600 hover:bg-rose-500 text-white font-bold px-3.5 py-2 rounded-xl text-xs flex items-center gap-1 shadow-sm transition-all transform active:scale-95"
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

async function ejecutarSalida(placa) {
  try {
    const res = await fetch("/api/salida", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ placa: placa })
    });
    const data = await res.json();

    if (data.success) {
      alert(`✓ SALIDA EXITOSA\nVehículo: ${data.placa}\nCelda Liberada: ${data.celda_liberada}\nTiempo de permanencia: ${data.tiempo_permanencia}`);
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
// 7. HISTORIAL DE AUDITORÍA
// ====================================================================

function renderizarHistorial() {
  const tbody = document.getElementById("tabla-historial-body");
  const hist = estadoParqueadero.historial || [];

  if (hist.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" class="text-center py-6 text-slate-400">Sin movimientos registrados aún en este turno.</td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = hist.map(h => {
    const adentro = h.estado === 'ADENTRO';
    return `
      <tr class="hover:bg-slate-50">
        <td class="py-3 px-4 font-mono-plate font-black text-slate-900">${h.vehiculo_placa}</td>
        <td class="py-3 px-4"><span class="bg-blue-50 text-blue-700 px-2 py-0.5 rounded text-[10px] font-bold">${h.tipo_vehiculo}</span></td>
        <td class="py-3 px-4 font-mono-plate font-bold text-slate-800">${h.celda_codigo}</td>
        <td class="py-3 px-4 text-slate-700">${h.fecha_ingreso}</td>
        <td class="py-3 px-4 text-slate-700">${h.fecha_salida || 'Estacionado actualmente'}</td>
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
      alert("Vehículo registrado exitosamente.");
      cerrarModalNuevoAbonado();
      cargarPlacaTest(placa);
      cambiarVista('view-control');
    } else {
      alert("Error al registrar: " + (data.error || data.mensaje));
    }
  } catch (err) {
    console.error("Error al registrar abonado:", err);
  }
}

// Modal Reglas de Negocio
function abrirModalReglas() {
  document.getElementById("modal-reglas").classList.remove("hidden");
}

function cerrarModalReglas() {
  document.getElementById("modal-reglas").classList.add("hidden");
}
