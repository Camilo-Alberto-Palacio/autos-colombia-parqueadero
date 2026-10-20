"""
Compilador de Documento Técnico Formal a PDF (Normas APA 7.ª Edición)
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
  <title>Informe Técnico Formal - Parqueadero Autos Colombia 24/7 (Iteración 1)</title>
  <style>
    @page {
      size: letter;
      margin: 25.4mm 25.4mm 25.4mm 25.4mm; /* Márgenes APA 2.54 cm (1 pulgada) */
    }
    body {
      font-family: 'Segoe UI', 'Times New Roman', serif;
      color: #0f172a;
      line-height: 1.65;
      font-size: 11pt;
      margin: 0;
      padding: 0;
    }
    .page-break {
      page-break-before: always;
    }
    .cover-page {
      height: 88vh;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      text-align: center;
      padding: 20px 10px;
    }
    .cover-title {
      font-size: 22pt;
      font-weight: 800;
      color: #0f172a;
      margin-bottom: 10px;
    }
    .cover-sub {
      font-size: 13.5pt;
      color: #1d4ed8;
      font-weight: 700;
      margin-bottom: 20px;
    }
    .cover-box {
      border: 1.5px solid #cbd5e1;
      background-color: #f8fafc;
      padding: 22px;
      border-radius: 10px;
      margin: 30px auto;
      max-width: 520px;
      text-align: left;
    }
    .cover-box table td {
      padding: 6px 10px;
      font-size: 10.5pt;
      vertical-align: top;
    }
    h1 {
      color: #0f172a;
      font-size: 15pt;
      border-bottom: 2px solid #1d4ed8;
      padding-bottom: 5px;
      margin-top: 24px;
    }
    h2 {
      color: #1e3a8a;
      font-size: 12.5pt;
      margin-top: 18px;
    }
    h3 {
      color: #334155;
      font-size: 11pt;
      margin-top: 14px;
    }
    table.data-table {
      width: 100%;
      border-collapse: collapse;
      margin: 14px 0;
      font-size: 9.5pt;
    }
    table.data-table th, table.data-table td {
      border: 1px solid #cbd5e1;
      padding: 7px 9px;
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
      padding: 9px 13px;
      margin: 8px 0;
      font-family: Consolas, monospace;
      font-size: 9pt;
    }
    .diagram-container {
      text-align: center;
      margin: 18px 0;
      page-break-inside: avoid;
    }
    .diagram-container img {
      max-width: 94%;
      max-height: 410px;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
    }
    .diagram-caption {
      font-size: 9pt;
      color: #475569;
      margin-top: 5px;
      font-style: italic;
    }
    .apa-ref {
      padding-left: 36px;
      text-indent: -36px;
      margin-bottom: 10px;
      font-size: 10pt;
    }
    ul, ol {
      padding-left: 22px;
    }
    li {
      margin-bottom: 4px;
    }
  </style>
</head>
<body>

  <!-- PORTADA FORMAL BAJO NORMAS APA -->
  <div class="cover-page">
    <div>
      <div style="font-size: 12pt; font-weight: bold; color: #334155; text-transform: uppercase; letter-spacing: 1.5px;">
        Facultad de Ingeniería · Programa de Ingeniería de Software
      </div>
      <div style="font-size: 10.5pt; color: #64748b; margin-top: 4px;">
        Semillero y Proyecto de Desarrollo de Software
      </div>
    </div>

    <div>
      <div class="cover-title">SISTEMA DE INFORMACIÓN PARQUEADERO AUTOS COLOMBIA 24/7</div>
      <div class="cover-sub">ITERACIÓN 1: GESTIÓN EXCLUSIVA DE ENTRADA Y SALIDA DE VEHÍCULOS</div>

      <div class="cover-box">
        <table style="width: 100%;">
          <tr>
            <td style="width: 38%;"><strong>Asignatura:</strong></td>
            <td>Ingeniería de Software / Desarrollo de Software</td>
          </tr>
          <tr>
            <td><strong>Docente Evaluador:</strong></td>
            <td>Prof. Reinaldo Rojas</td>
          </tr>
          <tr>
            <td><strong>Autor(es):</strong></td>
            <td>
              • Camilo Palacios<br>
              <span style="color:#64748b; font-size:9pt;">(Conformación permitida: 1 a 3 integrantes)</span>
            </td>
          </tr>
          <tr>
            <td><strong>Reglas Clave:</strong></td>
            <td>80 Celdas (70 Carros / 10 Motos) · Mensualidad Exclusiva ($250k / $100k) · Asignación Aleatoria · Operación 24/7</td>
          </tr>
          <tr>
            <td><strong>Fecha de Entrega:</strong></td>
            <td>Octubre de 2026</td>
          </tr>
        </table>
      </div>
    </div>

    <div style="font-size: 10pt; color: #475569;">
      Colombia · 2026
    </div>
  </div>

  <div class="page-break"></div>

  <!-- 1. INTRODUCCIÓN -->
  <h1>1. INTRODUCCIÓN</h1>
  <p>
    El presente informe técnico consolida la especificación de requerimientos funcionales y no funcionales, las reglas de negocio, las historias de usuario, el modelado arquitectónico y UML en StarUML, y el diseño de base de datos (MER, MR y Modelo Físico SQL) para la <strong>Iteración 1</strong> del sistema de información del parqueadero <strong>Autos Colombia 24/7</strong>.
  </p>
  <p>
    Atendiendo las directrices establecidas por el docente Reinaldo Rojas, esta primera entrega se enfoca de forma estricta y exclusiva en el <strong>módulo operativo de entrada y salida de vehículos</strong>. El sistema garantiza la validación automatizada de la vigencia de mensualidades sin periodo de gracia, la asignación dinámica/aleatoria de celdas según el tipo de automotor, el registro de atributos de seguridad y novedades físicas, y la sincronización en tiempo real para múltiples operarios concurrentes en modalidad 24/7.
  </p>

  <!-- 2. ALCANCE Y VISIÓN DE ITERACIONES -->
  <h1>2. ALCANCE DE LA ITERACIÓN 1 E ITERACIONES FUTURAS</h1>
  <div class="rule-box">
    <strong>Alcance Implementado en la Iteración 1:</strong><br>
    • <strong>Módulo de Entrada:</strong> Registro por placa, verificación automática de mensualidad vigente, despliegue de atributos del vehículo (placa, tipo, marca, modelo, color), control de capacidad por tipo, asignación dinámica de celda libre y registro de observaciones/novedades físicas.<br>
    • <strong>Módulo de Salida:</strong> Egreso ágil por placa o soporte de ingreso (#ID) con liberación inmediata de la celda.<br>
    • <strong>Control en Tiempo Real:</strong> Consulta continua de vehículos estacionados, celdas ocupadas y mapa interactivo de las 80 celdas.
  </div>
  <p>
    <strong>Exclusiones y Planificación de Iteraciones Futuras:</strong> Aunque se contemplan dentro del diseño arquitectónico general, se excluyen de la codificación de la Iteración 1:
  </p>
  <ul>
    <li><strong>Iteración 2:</strong> Gestión integral de usuarios (clientes y datos personales) y administración de celdas/vehículos.</li>
    <li><strong>Iteración 3:</strong> Gestión de pagos (recaudo en efectivo y pasarela virtual) y reportes financieros.</li>
  </ul>

  <!-- 3. REGLAS DE NEGOCIO -->
  <h1>3. REGLAS DE NEGOCIO DEL SISTEMA</h1>
  <ul>
    <li><strong>Modalidad de Servicio:</strong> Opera únicamente por <strong>mensualidad</strong> (no maneja cobros por horas ni días).</li>
    <li><strong>Capacidad y Distribución de Celdas:</strong> Dispone de un total estricto de <strong>80 celdas</strong>: <strong>10 celdas para motos</strong> (<code>M-01</code> a <code>M-10</code>) y <strong>70 celdas para carros/camionetas</strong> (<code>C-01</code> a <code>C-70</code>).</li>
    <li><strong>Celdas Dinámicas:</strong> No existen celdas fijas asignadas a un cliente; el sistema asigna aleatoriamente cualquier celda libre correspondiente al tipo de vehículo.</li>
    <li><strong>Cobro por Vehículo:</strong> La mensualidad se cobra de manera independiente por cada vehículo registrado, no por cliente ni por celda.</li>
    <li><strong>Tarifas Definidas:</strong> <strong>$250.000 COP</strong> para carros/camionetas y <strong>$100.000 COP</strong> para motos.</li>
    <li><strong>Vigencia del Pago (Sin Periodo de Gracia):</strong> La mensualidad cubre un mes a partir de la fecha exacta de pago (ej. del 13 de un mes al 13 del siguiente). Si el pago está vencido, se deniega el ingreso de inmediato y no existe periodo de gracia.</li>
    <li><strong>Horario de Operación:</strong> El parqueadero y el sistema funcionan <strong>24/7</strong>.</li>
  </ul>

  <div class="page-break"></div>

  <!-- 4. REQUERIMIENTOS FUNCIONALES Y NO FUNCIONALES -->
  <h1>4. REQUERIMIENTOS FUNCIONALES Y NO FUNCIONALES</h1>
  
  <h2>4.1 Requerimientos Funcionales (Iteración 1)</h2>
  <table class="data-table">
    <thead>
      <tr>
        <th style="width: 11%;">Código</th>
        <th style="width: 29%;">Requerimiento Funcional</th>
        <th style="width: 60%;">Descripción Operativa</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>RF-01</strong></td>
        <td>Registro de Ingreso de Vehículo</td>
        <td>Permitir al operario registrar la entrada digitando la placa del vehículo.</td>
      </tr>
      <tr>
        <td><strong>RF-02</strong></td>
        <td>Validación de Mensualidad</td>
        <td>Verificar automáticamente por la placa que el vehículo esté registrado en el sistema y al día en su pago antes de permitir el ingreso.</td>
      </tr>
      <tr>
        <td><strong>RF-03</strong></td>
        <td>Asignación Dinámica de Celda</td>
        <td>Asignar aleatoriamente una celda disponible en tiempo real según el tipo de vehículo (moto o carro).</td>
      </tr>
      <tr>
        <td><strong>RF-04</strong></td>
        <td>Registro de Atributos del Vehículo</td>
        <td>Consultar y mostrar al operario la placa, tipo de vehículo (carro/moto), marca, modelo y color para verificación visual y de seguridad.</td>
      </tr>
      <tr>
        <td><strong>RF-05</strong></td>
        <td>Control de Capacidad</td>
        <td>Bloquear el ingreso e informar al operario cuando la capacidad de celdas para el tipo de vehículo correspondiente esté completa (10 motos o 70 carros).</td>
      </tr>
      <tr>
        <td><strong>RF-06</strong></td>
        <td>Registro de Salida de Vehículo</td>
        <td>Registrar el egreso del vehículo mediante la placa o soporte de ingreso (#ID), liberando la celda inmediatamente para que quede disponible.</td>
      </tr>
      <tr>
        <td><strong>RF-07</strong></td>
        <td>Consultas y Control en Tiempo Real</td>
        <td>Permitir consultar el número de vehículos parqueados, celdas ocupadas y disponibilidad de celdas por tipo en cualquier momento.</td>
      </tr>
      <tr>
        <td><strong>RF-08</strong></td>
        <td>Registro de Novedades Físicas</td>
        <td>Permitir registrar observaciones o novedades sobre el estado físico del vehículo (ej. rayones o daños previos) al ingresar o salir.</td>
      </tr>
    </tbody>
  </table>

  <h2>4.2 Requerimientos No Funcionales (RNF)</h2>
  <table class="data-table">
    <thead>
      <tr>
        <th style="width: 11%;">Código</th>
        <th style="width: 29%;">Atributo de Calidad</th>
        <th style="width: 60%;">Especificación Técnica Implementada</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>RNF-01</strong></td>
        <td>Concurrencia y Sincronización</td>
        <td>Soporta el trabajo simultáneo de varios operarios en diferentes accesos (Puerta 1 Norte y Puerta 2 Sur) mediante servidor multi-hilo, modo WAL y transacciones atómicas <code>BEGIN IMMEDIATE</code> sin asignar jamás la misma celda a dos vehículos.</td>
      </tr>
      <tr>
        <td><strong>RNF-02</strong></td>
        <td>Usabilidad</td>
        <td>Interfaz intuitiva y ágil (sistema <em>Cobalt Bay OS</em>) que completa el ingreso o salida en 1 clic.</td>
      </tr>
      <tr>
        <td><strong>RNF-03</strong></td>
        <td>Disponibilidad</td>
        <td>Operación continua <strong>24/7</strong> con sincronización automática cada 4 segundos.</td>
      </tr>
      <tr>
        <td><strong>RNF-04</strong></td>
        <td>Seguridad y Validación de Datos</td>
        <td>Control de acceso por roles (Operario / Administrador), llaves foráneas activas y prevención de sobrecupo o doble ingreso.</td>
      </tr>
    </tbody>
  </table>

  <div class="page-break"></div>

  <!-- 5. HISTORIAS DE USUARIO -->
  <h1>5. HISTORIAS DE USUARIO Y CRITERIOS DE ACEPTACIÓN</h1>
  
  <p><strong>HU-01: Registro de Ingreso y Asignación Dinámica de Celda</strong><br>
  <em>Como</em> Operario de Cabina, <em>quiero</em> digitar la placa del vehículo al ingresar <em>para</em> validar su mensualidad y que el sistema le asigne aleatoriamente una celda libre de su tipo.</p>
  <div class="gherkin-box">
    <strong>Dado</strong> que el vehículo 'ABC-123' (Carro) está registrado, al día en su pago y hay celdas de carro libres,<br>
    <strong>Cuando</strong> el operario digita la placa y presiona "¡Abrir Barrera y Asignar Celda!",<br>
    <strong>Entonces</strong> el sistema asigna aleatoriamente una celda libre (ej. C-24), cambia su estado a OCUPADA y registra la entrada.
  </div>

  <p><strong>HU-02: Denegación de Ingreso por Mensualidad Vencida (Cero Periodo de Gracia)</strong><br>
  <em>Como</em> Operario de Cabina, <em>quiero</em> que el sistema verifique la fecha exacta de vencimiento de la mensualidad <em>para</em> denegar el acceso si está vencida.</p>
  <div class="gherkin-box">
    <strong>Dado</strong> que la mensualidad del vehículo 'XYZ-999' venció antes de la fecha actual,<br>
    <strong>Cuando</strong> el operario consulta la placa,<br>
    <strong>Entonces</strong> el sistema muestra alerta roja "MENSUALIDAD VENCIDA - ACCESO DENEGADO" y bloquea la apertura de barrera.
  </div>

  <p><strong>HU-03: Verificación de Atributos y Registro de Novedades Físicas</strong><br>
  <em>Como</em> Operario de Cabina, <em>quiero</em> ver placa, tipo, marca, modelo y color, y registrar observaciones físicas <em>para</em> dejar constancia de rayones o daños previos.</p>
  <div class="gherkin-box">
    <strong>Dado</strong> que el vehículo 'MOT-808' ingresa con un rayón previo en el carenaje,<br>
    <strong>Cuando</strong> el operario registra la novedad y autoriza el ingreso,<br>
    <strong>Entonces</strong> el sistema muestra todos los atributos de seguridad y guarda la novedad asociada al soporte de acceso.
  </div>

  <p><strong>HU-04: Bloqueo por Capacidad Completa según Tipo de Vehículo</strong><br>
  <em>Como</em> Administrador, <em>quiero</em> que el sistema bloquee la entrada cuando se llenen las 10 celdas de moto o las 70 de carro <em>para</em> evitar sobrecupos.</p>
  <div class="gherkin-box">
    <strong>Dado</strong> que las 10 celdas de moto se encuentran OCUPADAS,<br>
    <strong>Cuando</strong> una moto al día intenta ingresar,<br>
    <strong>Entonces</strong> el sistema bloquea el ingreso e informa "Capacidad máxima alcanzada para MOTOs".
  </div>

  <p><strong>HU-05: Registro de Salida y Liberación Inmediata de Celda</strong><br>
  <em>Como</em> Operario de Cabina, <em>quiero</em> dar salida por placa o soporte de ingreso <em>para</em> liberar la celda al instante.</p>
  <div class="gherkin-box">
    <strong>Dado</strong> que el vehículo 'ABC-123' ocupa la celda C-24,<br>
    <strong>Cuando</strong> el operario acciona "Dar Salida",<br>
    <strong>Entonces</strong> el sistema registra la hora de salida y libera inmediatamente la celda C-24 a estado DISPONIBLE.
  </div>

  <div class="page-break"></div>

  <!-- 6. ARQUITECTURA Y MODELADO UML -->
  <h1>6. ARQUITECTURA DEL SISTEMA Y DIAGRAMAS UML (STARUML)</h1>

  <div class="diagram-container">
    <h3>6.1 Arquitectura del Sistema: Diagrama de Componentes e Interfaces</h3>
    <img src="diagramas/6_diagrama_arquitectura_componentes.png" alt="Arquitectura de Componentes">
    <div class="diagram-caption">Figura 1. Diagrama de componentes e interfaces de comunicación (REST JSON, Servicio de Dominio y Persistencia Concurrente).</div>
  </div>

  <div class="diagram-container">
    <h3>6.2 Diagrama de Paquetes</h3>
    <img src="diagramas/1_diagrama_paquetes.png" alt="Diagrama de Paquetes">
    <div class="diagram-caption">Figura 2. Organización modular en paquetes por capas (Presentación, Controladores, Dominio y Persistencia).</div>
  </div>

  <div class="page-break"></div>

  <div class="diagram-container">
    <h3>6.3 Diagrama de Casos de Uso</h3>
    <img src="diagramas/2_diagrama_casos_de_uso.png" alt="Casos de Uso">
    <div class="diagram-caption">Figura 3. Diagrama de casos de uso para la Iteración 1 (Entrada, Salida, Validación y Mapa en Tiempo Real).</div>
  </div>

  <div class="diagram-container">
    <h3>6.4 Diagrama de Clases</h3>
    <img src="diagramas/3_diagrama_de_clases.png" alt="Diagrama de Clases">
    <div class="diagram-caption">Figura 4. Diagrama de clases del dominio con atributos, operaciones, enumeraciones y multiplicidades.</div>
  </div>

  <div class="page-break"></div>

  <div class="diagram-container">
    <h3>6.5 Diagrama de Secuencia: Ingreso de Vehículo</h3>
    <img src="diagramas/4_diagrama_secuencia_entrada.png" alt="Secuencia de Entrada">
    <div class="diagram-caption">Figura 5. Secuencia de validación de mensualidad, verificación de cupo y sorteo aleatorio de celda.</div>
  </div>

  <div class="diagram-container">
    <h3>6.6 Diagrama de Secuencia: Salida de Vehículo</h3>
    <img src="diagramas/5_diagrama_secuencia_salida.png" alt="Secuencia de Salida">
    <div class="diagram-caption">Figura 6. Secuencia de egreso y liberación inmediata de la celda ocupada.</div>
  </div>

  <div class="page-break"></div>

  <!-- 7. DISEÑO DE BASE DE DATOS -->
  <h1>7. DISEÑO DE BASE DE DATOS (MER, MR Y MODELO FÍSICO)</h1>
  <p>
    El diseño de datos garantiza la trazabilidad histórica de accesos, el cobro independiente por vehículo y el control estricto de las 80 celdas reglamentarias:
  </p>

  <div class="diagram-container">
    <h3>7.1 Modelo Entidad-Relación (MER) y Modelo Relacional (MR)</h3>
    <img src="diagramas/7_diagrama_entidad_relacion_mer.png" alt="Diagrama MER y Relacional">
    <div class="diagram-caption">Figura 7. Esquema Entidad-Relación y Modelo Relacional en 3FN con llaves primarias (PK) y foráneas (FK).</div>
  </div>

  <p>
    <strong>Modelo Físico Ejecutable:</strong> El script SQL completo se entrega en el archivo <code>database_schema.sql</code>, el cual construye las tablas (<code>propietario</code>, <code>vehiculo</code>, <code>mensualidad</code>, <code>celda</code> y <code>registro_acceso</code>), los índices de alto rendimiento y pobla las 10 celdas de moto (<code>M-01</code> a <code>M-10</code>) y 70 celdas de carro (<code>C-01</code> a <code>C-70</code>).
  </p>

  <!-- 8. CONCLUSIONES Y REFERENCIAS APA -->
  <h1>8. CONCLUSIONES</h1>
  <ol>
    <li><strong>Cumplimiento Riguroso del Alcance (Iteración 1):</strong> La aplicación resuelve de manera íntegra el control de entrada y salida de vehículos por mensualidad, respetando la exclusión de los módulos de usuarios y pagos reservados para las iteraciones 2 y 3.</li>
    <li><strong>Integridad en Reglas de Negocio y Aforo:</strong> El motor de reglas valida automáticamente la placa, la vigencia mensual exacta sin periodo de gracia ($250.000 carro / $100.000 moto) y asigna de forma aleatoria las celdas disponibles evitando sobrecupos.</li>
    <li><strong>Arquitectura Concurrente 24/7:</strong> El uso de transacciones atómicas en modo WAL y servidor multi-hilo permite que varios operarios en diferentes puertas trabajen simultáneamente en tiempo real sin colisiones en la asignación de celdas.</li>
  </ol>

  <h1>9. REFERENCIAS BIBLIOGRÁFICAS (NORMAS APA 7.ª EDICIÓN)</h1>
  <div class="apa-ref">
    Booch, G., Rumbaugh, J., &amp; Jacobson, I. (2006). <em>El lenguaje unificado de modelado: Guía del usuario</em> (2.ª ed.). Addison-Wesley.
  </div>
  <div class="apa-ref">
    Elmasri, R., &amp; Navathe, S. B. (2017). <em>Fundamentos de sistemas de bases de datos</em> (7.ª ed.). Pearson Educación.
  </div>
  <div class="apa-ref">
    Pressman, R. S., &amp; Maxim, B. R. (2021). <em>Ingeniería del software: Un enfoque práctico</em> (9.ª ed.). McGraw-Hill.
  </div>
  <div class="apa-ref">
    Sommerville, I. (2016). <em>Ingeniería de software</em> (10.ª ed.). Pearson Educación.
  </div>

</body>
</html>
"""

def compilar():
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[OK] Archivo HTML imprimible actualizado: {HTML_PATH}")

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
        print(f"[EXITO] PDF Oficial compilado con 7 diagramas y Normas APA: {PDF_PATH} ({size} bytes)")
    except Exception as e:
        print(f"[ERROR] No se pudo generar PDF con Edge: {e}")

if __name__ == "__main__":
    compilar()
