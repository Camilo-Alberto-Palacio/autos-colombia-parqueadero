"""
Compilador de Documento Técnico a PDF usando Microsoft Edge Headless
Autos Colombia 24/7 - Docente: Reinaldo Rojas
"""

import os
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(BASE_DIR, "documento_imprimible.html")
PDF_PATH = os.path.join(BASE_DIR, "DOCUMENTACION_TECNICA_ITERACION_1.pdf")
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

html_content = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Documentación Técnica - Autos Colombia 24/7</title>
  <style>
    @page {
      size: letter;
      margin: 20mm 18mm 20mm 18mm;
    }
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      color: #1e293b;
      line-height: 1.6;
      font-size: 11pt;
      margin: 0;
      padding: 0;
    }
    .page-break {
      page-break-before: always;
    }
    .cover-page {
      height: 90vh;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      text-align: center;
      padding: 40px 20px;
    }
    .cover-title {
      font-size: 26pt;
      font-weight: 800;
      color: #0f172a;
      margin-bottom: 8px;
    }
    .cover-sub {
      font-size: 15pt;
      color: #1d4ed8;
      font-weight: 600;
      margin-bottom: 25px;
    }
    .cover-box {
      border: 2px solid #e2e8f0;
      background-color: #f8fafc;
      padding: 24px;
      border-radius: 12px;
      margin: 40px auto;
      max-width: 500px;
      text-align: left;
    }
    .cover-box table td {
      padding: 6px 10px;
      font-size: 10.5pt;
    }
    h1 {
      color: #0f172a;
      font-size: 18pt;
      border-bottom: 2px solid #1d4ed8;
      padding-bottom: 6px;
      margin-top: 30px;
    }
    h2 {
      color: #1e3a8a;
      font-size: 14pt;
      margin-top: 22px;
    }
    h3 {
      color: #334155;
      font-size: 12pt;
      margin-top: 16px;
    }
    table.data-table {
      width: 100%;
      border-collapse: collapse;
      margin: 15px 0;
      font-size: 9.5pt;
    }
    table.data-table th, table.data-table td {
      border: 1px solid #cbd5e1;
      padding: 8px 10px;
      text-align: left;
    }
    table.data-table th {
      background-color: #f1f5f9;
      font-weight: 700;
      color: #0f172a;
    }
    table.data-table tr:nth-child(even) {
      background-color: #f8fafc;
    }
    .rule-box {
      background-color: #eff6ff;
      border-left: 4px solid #1d4ed8;
      padding: 10px 14px;
      margin: 10px 0;
      font-size: 10pt;
    }
    .gherkin-box {
      background-color: #f0fdf4;
      border-left: 4px solid #16a34a;
      padding: 10px 14px;
      margin: 8px 0;
      font-family: Consolas, monospace;
      font-size: 9.5pt;
    }
    .diagram-container {
      text-align: center;
      margin: 25px 0;
      page-break-inside: avoid;
    }
    .diagram-container img {
      max-width: 95%;
      max-height: 480px;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .diagram-caption {
      font-size: 9pt;
      color: #64748b;
      margin-top: 6px;
      font-weight: 600;
    }
    ul, ol {
      padding-left: 22px;
    }
    li {
      margin-bottom: 5px;
    }
  </style>
</head>
<body>

  <!-- PORTADA FORMAL -->
  <div class="cover-page">
    <div>
      <div style="font-size: 13pt; font-weight: bold; color: #64748b; text-transform: uppercase; letter-spacing: 2px;">
        Universidad / Facultad de Ingeniería
      </div>
      <div style="font-size: 11pt; color: #94a3b8; margin-top: 4px;">
        Semillero de Desarrollo de Software
      </div>
    </div>

    <div>
      <div class="cover-title">PARQUEADERO AUTOS COLOMBIA 24/7</div>
      <div class="cover-sub">DOCUMENTO TÉCNICO DE ESPECIFICACIÓN Y DISEÑO DE SOFTWARE</div>
      <div style="font-size: 12pt; color: #475569; font-weight: 600;">
        Iteración 1: Módulo Exclusivo de Entrada y Salida de Vehículos
      </div>

      <div class="cover-box">
        <table style="width: 100%;">
          <tr>
            <td><strong>Asignatura:</strong></td>
            <td>Ingeniería de Software / Desarrollo de Software</td>
          </tr>
          <tr>
            <td><strong>Docente:</strong></td>
            <td>Prof. Reinaldo Rojas</td>
          </tr>
          <tr>
            <td><strong>Equipo de Trabajo:</strong></td>
            <td>
              • Camilo Palacios<br>
              • [Compañero 2 - Opcional]<br>
              • [Compañero 3 - Opcional]
            </td>
          </tr>
          <tr>
            <td><strong>Modalidad:</strong></td>
            <td>Exclusiva por Mensualidad (80 Celdas)</td>
          </tr>
          <tr>
            <td><strong>Fecha:</strong></td>
            <td>Octubre de 2026</td>
          </tr>
        </table>
      </div>
    </div>

    <div style="font-size: 10pt; color: #94a3b8;">
      Medellín, Colombia · 2026
    </div>
  </div>

  <div class="page-break"></div>

  <!-- CONTENIDO -->
  <h1>1. INTRODUCCIÓN Y CONTEXTO</h1>
  <p>
    El presente documento técnico formaliza el análisis, modelado e implementación de la primera fase de desarrollo de la plataforma de control del parqueadero <strong>Autos Colombia 24/7</strong>.
  </p>
  <p>
    El parqueadero opera bajo una modalidad especializada dirigida a clientes habituales mediante contrato de <strong>mensualidad exclusiva</strong>, atendiendo de forma ininterrumpida las 24 horas del día durante los 7 días de la semana. El objetivo central de esta primera iteración es dotar a la cabina de control de una herramienta confiable para la validación automática de vigencias, el control de aforo estricto y la asignación dinámica de celdas libres.
  </p>

  <h1>2. ALCANCE DE LA ITERACIÓN 1</h1>
  <div class="rule-box">
    <strong>Alcance Específico de la Entrega:</strong><br>
    • <strong>Módulo de Entrada:</strong> Identificación por placa, validación de estado de cuenta de mensualidad, validación de cupo y asignación aleatoria de celda libre.<br>
    • <strong>Módulo de Salida:</strong> Búsqueda de vehículos en planta, registro de timestamp de salida y liberación inmediata de la celda de parqueo.<br>
    • <strong>Monitoreo de Aforo:</strong> Semáforo y mapa en vivo de 80 celdas (70 carros y 10 motos).
  </div>
  <p>
    <strong>Exclusiones Explícitas:</strong> En estricto cumplimiento de los requerimientos de la Iteración 1, <em>no</em> se incluye la gestión avanzada de perfiles de usuario ni módulos de pasarelas de pago o recaudo en efectivo en sitio, los cuales forman parte de las iteraciones 2 y 3.
  </p>

  <h1>3. REGLAS DE NEGOCIO</h1>
  <ul>
    <li><strong>RN-01 (Modalidad Exclusiva por Mensualidad):</strong> No se trabaja cobro por horas, minutos ni días.</li>
    <li><strong>RN-02 (Aforo y Distribución):</strong> Dispone exactamente de <strong>80 celdas fijas</strong> divididas en 10 celdas para motocicletas (<code>M-01</code> a <code>M-10</code>) y 70 celdas para vehículos/carros (<code>C-01</code> a <code>C-70</code>).</li>
    <li><strong>RN-03 (Asignación Dinámica / Aleatoria):</strong> No existen puestos fijos por cliente. El sistema sortea aleatoriamente una de las celdas disponibles para su categoría.</li>
    <li><strong>RN-04 (Cobro por Vehículo):</strong> La mensualidad se paga por placa: <strong>$250.000 COP</strong> (Carro) y <strong>$100.000 COP</strong> (Moto).</li>
    <li><strong>RN-05 (Vigencia Estricta):</strong> La suscripción cubre 1 mes calendario. Si la fecha de vencimiento es anterior a la fecha actual, el sistema deniega el acceso automáticamente bajo alerta de mora.</li>
    <li><strong>RN-06 (Control de Duplicidad):</strong> Un vehículo que ya se encuentre adentro no puede registrar otro ingreso hasta tanto registre su egreso.</li>
    <li><strong>RN-07 (Trazabilidad):</strong> Despliegue visual de Placa, Tipo, Marca, Modelo, Color y Titular.</li>
    <li><strong>RN-08 (Horario 24/7):</strong> Registro cronológico continuo con reloj y timestamps exactos.</li>
  </ul>

  <div class="page-break"></div>

  <h1>4. REQUERIMIENTOS FUNCIONALES (RF)</h1>
  <table class="data-table">
    <thead>
      <tr>
        <th style="width: 12%;">Código</th>
        <th style="width: 28%;">Requerimiento</th>
        <th style="width: 60%;">Descripción Técnica</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>RF-01</strong></td>
        <td>Búsqueda de Placa</td>
        <td>Búsqueda normalizada por placa en la base de datos de automotores suscritos.</td>
      </tr>
      <tr>
        <td><strong>RF-02</strong></td>
        <td>Validación de Mensualidad</td>
        <td>Verifica si la mensualidad está al día. En caso de vencimiento bloquea la apertura de barrera.</td>
      </tr>
      <tr>
        <td><strong>RF-03</strong></td>
        <td>Control de Aforo</td>
        <td>Comprueba que el aforo disponible para la categoría sea mayor a cero antes de abrir.</td>
      </tr>
      <tr>
        <td><strong>RF-04</strong></td>
        <td>Asignación Aleatoria</td>
        <td>Selecciona dinámicamente una celda disponible del pool correspondiente y la marca OCUPADA.</td>
      </tr>
      <tr>
        <td><strong>RF-05</strong></td>
        <td>Registro de Acceso</td>
        <td>Inserta registro con fecha y hora actual, placa y celda asignada en estado ADENTRO.</td>
      </tr>
      <tr>
        <td><strong>RF-06</strong></td>
        <td>Listado en Planta</td>
        <td>Despliega los vehículos estacionados con tiempo transcurrido en tiempo real.</td>
      </tr>
      <tr>
        <td><strong>RF-07</strong></td>
        <td>Salida y Liberación</td>
        <td>Al registrar la salida, actualiza fecha_salida y devuelve la celda a estado DISPONIBLE.</td>
      </tr>
      <tr>
        <td><strong>RF-08</strong></td>
        <td>Mapa de 80 Celdas</td>
        <td>Grilla interactiva con semáforo verde/rojo para inspeccionar ocupación en vivo.</td>
      </tr>
    </tbody>
  </table>

  <h1>5. HISTORIAS DE USUARIO (FORMATO GHERKIN)</h1>
  
  <p><strong>HU-01: Ingreso Autorizado con Mensualidad Vigente</strong></p>
  <div class="gherkin-box">
    <strong>Dado</strong> que el vehículo 'ABC-123' (Carro) tiene mensualidad activa y hay celdas libres,<br>
    <strong>Cuando</strong> el operador pulsa "¡Abrir Barrera de Entrada!",<br>
    <strong>Entonces</strong> el sistema sortea una celda libre (ej: C-24), cambia su estado a OCUPADA y almacena el ingreso.
  </div>

  <p><strong>HU-02: Bloqueo Automático por Mensualidad Vencida</strong></p>
  <div class="gherkin-box">
    <strong>Dado</strong> que el vehículo 'XYZ-999' tiene su mensualidad vencida,<br>
    <strong>Cuando</strong> se ingresa la placa en la cabina,<br>
    <strong>Entonces</strong> el sistema muestra alerta roja de mora y deshabilita el botón de apertura de barrera.
  </div>

  <p><strong>HU-03: Egreso y Liberación Inmediata de Celda</strong></p>
  <div class="gherkin-box">
    <strong>Dado</strong> que el vehículo 'ABC-123' está adentro ocupando la celda C-24,<br>
    <strong>Cuando</strong> el operador pulsa "Dar Salida",<br>
    <strong>Entonces</strong> el sistema libera la celda C-24 a DISPONIBLE y finaliza el registro de estancia.
  </div>

  <div class="page-break"></div>

  <h1>6. ARQUITECTURA Y MODELADO UML (STARUML)</h1>

  <div class="diagram-container">
    <h3>Diagrama 1: Diagrama de Paquetes y Arquitectura Modular</h3>
    <img src="diagramas/1_diagrama_paquetes.png" alt="Diagrama de Paquetes">
    <div class="diagram-caption">Figura 1. Organización del sistema en 3 capas desacopladas (Presentación, Lógica y Persistencia).</div>
  </div>

  <div class="diagram-container">
    <h3>Diagrama 2: Diagrama de Casos de Uso</h3>
    <img src="diagramas/2_diagrama_casos_de_uso.png" alt="Casos de Uso">
    <div class="diagram-caption">Figura 2. Casos de uso e interacciones con el Operador de Cabina, Cámara LPR y Reloj 24/7.</div>
  </div>

  <div class="page-break"></div>

  <div class="diagram-container">
    <h3>Diagrama 3: Diagrama de Clases del Dominio</h3>
    <img src="diagramas/3_diagrama_de_clases.png" alt="Diagrama de Clases">
    <div class="diagram-caption">Figura 3. Clases de entidad, atributos, métodos, tipos enumerados y relaciones con multiplicidad.</div>
  </div>

  <div class="page-break"></div>

  <div class="diagram-container">
    <h3>Diagrama 4: Diagrama de Secuencia - Proceso de Ingreso</h3>
    <img src="diagramas/4_diagrama_secuencia_entrada.png" alt="Secuencia de Entrada">
    <div class="diagram-caption">Figura 4. Secuencia temporal de validación de mensualidad, cupo y asignación aleatoria.</div>
  </div>

  <div class="diagram-container">
    <h3>Diagrama 5: Diagrama de Secuencia - Proceso de Salida</h3>
    <img src="diagramas/5_diagrama_secuencia_salida.png" alt="Secuencia de Salida">
    <div class="diagram-caption">Figura 5. Secuencia de registro de egreso, cálculo de tiempo y liberación automática de celda.</div>
  </div>

  <div class="page-break"></div>

  <h1>7. DISEÑO DE BASE DE DATOS: MER, MR Y MODELO FÍSICO</h1>
  <p>
    La base de datos fue normalizada en 3FN y diseñada para operar con integridad referencial estricta:
  </p>
  <ul>
    <li><code>propietario (id, documento, nombre_completo, telefono, email)</code></li>
    <li><code>vehiculo (placa, tipo_vehiculo, marca, modelo, color, propietario_id)</code></li>
    <li><code>mensualidad (id, vehiculo_placa, fecha_pago, fecha_vencimiento, valor_pagado, estado)</code></li>
    <li><code>celda (codigo, tipo_permitido, estado, piso, zona)</code> - <strong>80 celdas exactas</strong></li>
    <li><code>registro_acceso (id, vehiculo_placa, celda_codigo, fecha_ingreso, fecha_salida, estado)</code></li>
  </ul>
  <p>
    El script SQL ejecutable completo se encuentra en <code>database_schema.sql</code>, el cual inicializa automáticamente la base de datos SQLite <code>autos_colombia.db</code> con las 10 celdas de moto (<code>M-01</code> a <code>M-10</code>) y 70 celdas de carro (<code>C-01</code> a <code>C-70</code>).
  </p>

</body>
</html>
"""

def compilar():
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[OK] Archivo HTML imprimible generado: {HTML_PATH}")

    # Ejecutar Microsoft Edge Headless para compilar el PDF
    cmd = [
        EDGE_PATH,
        "--headless",
        "--disable-gpu",
        "--allow-file-access-from-files",
        f"--print-to-pdf={PDF_PATH}",
        HTML_PATH
    ]
    try:
        subprocess.run(cmd, check=True)
        size = os.path.getsize(PDF_PATH)
        print(f"[EXITO] PDF Oficial compilado: {PDF_PATH} ({size} bytes)")
    except Exception as e:
        print(f"[ERROR] No se pudo generar PDF con Edge: {e}")

if __name__ == "__main__":
    compilar()
