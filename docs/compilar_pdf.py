"""
Compilador de Documento Técnico Formal a PDF (Normas APA 7.ª Edición)
Autos Colombia 24/7 - Docente: Reinaldo Rojas Lopez
Institución Universitaria Digital de Antioquia (IU Digital)
Versión: Entrega de Corrección Oficial
"""

import os
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(BASE_DIR, "documento_imprimible.html")
PDF_PATH = os.path.join(BASE_DIR, "DOCUMENTACION_TECNICA_ITERACION_1.pdf")
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

html_content = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>SISTEMA DE GESTIÓN DE OPERACIONES: PARQUEADERO AUTOS COLOMBIA 24/7 - ITERACIÓN 1 (CORREGIDO)</title>
  <style>
    @page {
      size: letter;
      margin: 25.4mm 25.4mm 25.4mm 25.4mm; /* Márgenes APA 2.54 cm */
    }
    body {
      font-family: 'Segoe UI', 'Times New Roman', serif;
      color: #0f172a;
      line-height: 1.6;
      font-size: 10.5pt;
      margin: 0;
      padding: 0;
    }
    .page-break {
      page-break-before: always;
    }
    .cover-page {
      min-height: 86vh;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      text-align: center;
      padding: 20px 10px;
    }
    .cover-title {
      font-size: 20pt;
      font-weight: 800;
      color: #0f172a;
      margin-bottom: 8px;
      line-height: 1.3;
    }
    .cover-sub {
      font-size: 13pt;
      color: #1d4ed8;
      font-weight: 700;
      margin-bottom: 15px;
    }
    .badge-correction {
      display: inline-block;
      background-color: #dbeafe;
      color: #1e40af;
      border: 1px solid #93c5fd;
      padding: 4px 14px;
      border-radius: 9999px;
      font-size: 9.5pt;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 12px;
    }
    .cover-box {
      border: 1.5px solid #cbd5e1;
      background-color: #f8fafc;
      padding: 18px 24px;
      border-radius: 10px;
      margin: 20px auto;
      max-width: 540px;
      text-align: left;
    }
    .cover-box table {
      width: 100%;
      border-collapse: collapse;
    }
    .cover-box table td {
      padding: 5px 8px;
      font-size: 10pt;
      vertical-align: top;
    }
    h1 {
      color: #0f172a;
      font-size: 14pt;
      border-bottom: 2px solid #1d4ed8;
      padding-bottom: 4px;
      margin-top: 20px;
      margin-bottom: 12px;
      text-transform: uppercase;
    }
    h2 {
      color: #1e3a8a;
      font-size: 12pt;
      margin-top: 16px;
      margin-bottom: 8px;
    }
    h3 {
      color: #334155;
      font-size: 10.5pt;
      margin-top: 12px;
      margin-bottom: 6px;
    }
    p, li {
      text-align: justify;
      margin-bottom: 8px;
    }
    ul, ol {
      margin-top: 4px;
      margin-bottom: 10px;
      padding-left: 24px;
    }
    .data-table {
      width: 100%;
      border-collapse: collapse;
      margin: 12px 0 16px 0;
      font-size: 9pt;
    }
    .data-table th, .data-table td {
      border: 1px solid #cbd5e1;
      padding: 6px 8px;
      text-align: left;
    }
    .data-table th {
      background-color: #f1f5f9;
      color: #1e293b;
      font-weight: 700;
    }
    .data-table tr:nth-child(even) {
      background-color: #f8fafc;
    }
    .alert-box {
      background-color: #eff6ff;
      border-left: 4px solid #2563eb;
      padding: 10px 14px;
      margin: 12px 0;
      border-radius: 0 6px 6px 0;
      font-size: 9.5pt;
    }
    .gherkin-box {
      background-color: #f8fafc;
      border-left: 4px solid #10b981;
      border-right: 1px solid #e2e8f0;
      border-top: 1px solid #e2e8f0;
      border-bottom: 1px solid #e2e8f0;
      padding: 8px 12px;
      margin: 8px 0 14px 0;
      border-radius: 0 6px 6px 0;
      font-size: 9pt;
      line-height: 1.5;
    }
    .gherkin-exception {
      border-left-color: #ef4444;
      background-color: #fef2f2;
    }
    .diagram-container {
      margin: 14px auto;
      text-align: center;
      page-break-inside: avoid;
    }
    .diagram-container img {
      max-width: 95%;
      height: auto;
      max-height: 480px;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.05);
      background: #ffffff;
      padding: 4px;
    }
    .diagram-caption {
      font-size: 8.5pt;
      color: #64748b;
      margin-top: 6px;
      font-style: italic;
    }
    code {
      font-family: 'JetBrains Mono', Consolas, monospace;
      background-color: #f1f5f9;
      padding: 1px 5px;
      border-radius: 4px;
      font-size: 9pt;
      color: #0f172a;
    }
    .footer-text {
      font-size: 8.5pt;
      color: #64748b;
      text-align: center;
      border-top: 1px solid #e2e8f0;
      padding-top: 8px;
      margin-top: 20px;
    }
  </style>
</head>
<body>

  <!-- PORTADA -->
  <div class="cover-page">
    <div>
      <div class="badge-correction">Documento de Entrega con Correcciones Docentes</div>
      <div class="cover-title">SISTEMA DE GESTIÓN DE OPERACIONES:<br>PARQUEADERO "AUTOS COLOMBIA 24/7"</div>
      <div class="cover-sub">EVIDENCIA DE APRENDIZAJE 1: DISEÑO DEL SISTEMA DE INFORMACIÓN - ITERACIÓN 1</div>
      <p style="text-align: center; color: #475569; font-size: 10.5pt; margin-top: -6px;">
        Módulo Exclusivo de Control de Entrada y Salida, Validación de Mensualidades y Asignación de Celdas
      </p>
    </div>

    <div class="cover-box">
      <table>
        <tr>
          <td style="width: 32%;"><strong>Integrantes:</strong></td>
          <td>
            Adriana Andrea Agudelo Agudelo<br>
            Camilo Alberto Palacios Turriago<br>
            Juan Daniel Pulgarin García
          </td>
        </tr>
        <tr>
          <td><strong>Asignatura:</strong></td>
          <td>Ingeniería de Software / Desarrollo de Software</td>
        </tr>
        <tr>
          <td><strong>Código Curso:</strong></td>
          <td>PREICA2602B020053 - Grupo 25</td>
        </tr>
        <tr>
          <td><strong>Docente:</strong></td>
          <td>Prof. Reinaldo Rojas Lopez</td>
        </tr>
        <tr>
          <td><strong>Institución:</strong></td>
          <td>Institución Universitaria Digital de Antioquia (IU Digital)</td>
        </tr>
        <tr>
          <td><strong>Facultad:</strong></td>
          <td>Facultad de Ingeniería</td>
        </tr>
        <tr>
          <td><strong>Normativa:</strong></td>
          <td>Normas APA 7.ª Edición</td>
        </tr>
        <tr>
          <td><strong>Fecha Entrega:</strong></td>
          <td>Noviembre de 2026 - Medellín, Antioquia</td>
        </tr>
      </table>
    </div>

    <div>
      <p style="text-align: center; font-size: 9pt; color: #64748b; margin: 0;">
        Repositorio GitHub: <code>https://github.com/Camilo-Alberto-Palacio/autos-colombia-parqueadero</code><br>
        Mockups Figma / Stitch: <code>https://stitch.withgoogle.com/projects/3967613353864933368</code>
      </p>
    </div>
  </div>

  <div class="page-break"></div>

  <!-- 1. INTRODUCCIÓN -->
  <h1>1. INTRODUCCIÓN</h1>
  <p>
    El presente informe técnico documenta de manera exhaustiva el proceso de ingeniería de requerimientos, diseño arquitectónico por capas, modelado UML en StarUML, diseño de base de datos relacional (MER, MR y Modelo Físico DDL) y construcción de software correspondientes a la <strong>Iteración 1 (Versión Corregida)</strong> del sistema de información para el parqueadero <strong>Autos Colombia 24/7</strong>.
  </p>
  <p>
    La empresa opera bajo un modelo de negocio especializado en el estacionamiento de vehículos mediante <strong>mensualidad exclusiva</strong>, prestando servicio ininterrumpido las 24 horas del día, los 7 días de la semana (24/7). En esta primera entrega, el alcance se centra de forma estricta y rigurosa en el <strong>módulo operativo de control de entrada y salida de vehículos</strong>, garantizando la validación automática de vigencias de pago mensual sin periodo de gracia, el control transaccional estricto de las 80 celdas físicas disponibles (10 exclusivas para motos y 70 para carros), la asignación dinámica/aleatoria de espacios libres y la sincronización concurrente en tiempo real para múltiples operarios en diferentes accesos (ej. Puerta 1 Norte y Puerta 2 Sur).
  </p>

  <div class="alert-box">
    <strong>Síntesis de Correcciones Incorporadas en esta Entrega:</strong>
    <ul style="margin: 4px 0 0 0; padding-left: 18px;">
      <li><strong>Criterios de Aceptación BDD Completos:</strong> Se integraron escenarios formales para los casos excepcionales de <em>placa inexistente (no registrada)</em>, <em>ingreso duplicado (vehículo ya adentro)</em> y <em>salida sin registro activo (vehículo que no está adentro)</em>, con sus resultados esperados.</li>
      <li><strong>Corrección Semántica UML en Casos de Uso:</strong> Se corrigió la orientación de las relaciones <code>&laquo;extend&raquo;</code> (apuntan rigurosamente desde el caso de uso de extensión hacia el caso base, según la norma OMG UML 2.5) y se eliminaron las relaciones <code>&laquo;include&raquo;</code> dirigidas a actores externos.</li>
      <li><strong>Diagrama de Paquetes UML con Dependencias:</strong> Se estructuró formalmente la arquitectura en paquetes con sus relaciones de dependencia unidireccionales (<code>&laquo;use&raquo;</code> y <code>&laquo;access&raquo;</code>).</li>
      <li><strong>Ajuste y Profundización del RNF-03:</strong> Se detalló técnicamente el mecanismo de control de ocupación implementado en el backend (exclusión mutua <code>threading.Lock</code>, transacciones atómicas SQLite WAL <code>BEGIN IMMEDIATE</code> y validación estricta de cupos).</li>
    </ul>
  </div>

  <!-- 2. ALCANCE Y REGLAS DE NEGOCIO -->
  <h1>2. ALCANCE Y REGLAS DE NEGOCIO DEL SISTEMA</h1>

  <h2>2.1 Alcance de la Iteración 1</h2>
  <ul>
    <li><strong>Gestión de Entrada y Salida:</strong> Registro de ingreso digitando placa, verificación instantánea de contrato mensual vigente, visualización de ficha técnica de seguridad (placa, tipo, marca, modelo, color y titular), asignación aleatoria de celda y registro de salida con liberación en 1 clic.</li>
    <li><strong>Registro de Novedades Físicas:</strong> Campo operativo para asentar rayones, golpes, abolladuras o accesorios dejados al momento de entrar o salir.</li>
    <li><strong>Control de Capacidad en Tiempo Real:</strong> Monitoreo de 80 celdas reglamentarias (70 carros y 10 motos), previniendo sobrecupos y bloqueos concurrentes.</li>
  </ul>

  <h2>2.2 Reglas de Negocio (Business Rules)</h2>
  <ul>
    <li><strong>RN-01 (Mensualidad Exclusiva):</strong> El parqueadero presta servicio únicamente bajo modalidad de mensualidad. No existen tarifas por horas ni fracciones.</li>
    <li><strong>RN-02 (Distribución Reglamentaria de 80 Celdas):</strong> Capacidad física fija de 10 celdas exclusivas para motos (<code>M-01</code> a <code>M-10</code>) y 70 celdas para automóviles/camionetas (<code>C-01</code> a <code>C-70</code>).</li>
    <li><strong>RN-03 (Asignación Dinámica / Aleatoria):</strong> Las celdas no son fijas para ningún abonado; el sistema sortea aleatoriamente una celda libre al ingresar según el tipo de vehículo.</li>
    <li><strong>RN-04 (Cobro por Vehículo):</strong> La mensualidad se liquida individualmente por placa registrada.</li>
    <li><strong>RN-05 (Tarifas Oficiales):</strong> <strong>$250.000 COP</strong> mensuales para carros y <strong>$100.000 COP</strong> mensuales para motos.</li>
    <li><strong>RN-06 (Cero Periodo de Gracia):</strong> La mensualidad vence exactamente al cumplirse un mes calendario desde el pago. Si la fecha actual supera el vencimiento, se bloquea el acceso inmediatamente.</li>
    <li><strong>RN-07 (Control Antiduplicidad):</strong> No se autoriza doble ingreso de un vehículo que ya figure con estado <code>ADENTRO</code>.</li>
  </ul>

  <div class="page-break"></div>

  <!-- 3. REQUERIMIENTOS FUNCIONALES Y NO FUNCIONALES -->
  <h1>3. REQUERIMIENTOS FUNCIONALES Y NO FUNCIONALES</h1>

  <h2>3.1 Requerimientos Funcionales (Iteración 1)</h2>
  <table class="data-table">
    <thead>
      <tr>
        <th style="width: 12%;">Código</th>
        <th style="width: 28%;">Nombre</th>
        <th style="width: 60%;">Descripción Operativa y Criterio de Control</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>RF-01</strong></td>
        <td>Registro de Ingreso</td>
        <td>Permitir al operario registrar la entrada digitando la placa vehicular en la consola de acceso.</td>
      </tr>
      <tr>
        <td><strong>RF-02</strong></td>
        <td>Validación de Mensualidad</td>
        <td>Verificar de forma automática que la placa exista en el padrón de abonados y que su mensualidad esté vigente antes de franquear el acceso.</td>
      </tr>
      <tr>
        <td><strong>RF-03</strong></td>
        <td>Asignación Dinámica de Celda</td>
        <td>Asignar de forma aleatoria una celda disponible de la categoría correspondiente (Carro o Moto) y marcarla como <code>OCUPADA</code>.</td>
      </tr>
      <tr>
        <td><strong>RF-04</strong></td>
        <td>Verificación de Atributos</td>
        <td>Mostrar en pantalla placa, tipo, marca, modelo, color y conductor registrado para comprobación visual contra el automotor físico.</td>
      </tr>
      <tr>
        <td><strong>RF-05</strong></td>
        <td>Control de Capacidad Máxima</td>
        <td>Bloquear el ingreso e informar al operario cuando se completen las 70 celdas de carro o las 10 de moto.</td>
      </tr>
      <tr>
        <td><strong>RF-06</strong></td>
        <td>Registro de Salida</td>
        <td>Registrar el egreso del vehículo, calcular la permanencia exacta y liberar de inmediato la celda a estado <code>DISPONIBLE</code>.</td>
      </tr>
      <tr>
        <td><strong>RF-07</strong></td>
        <td>Monitoreo en Tiempo Real</td>
        <td>Visualizar en vivo el inventario de 80 celdas, vehículos adentro, celdas libres por tipo e historial de accesos.</td>
      </tr>
      <tr>
        <td><strong>RF-08</strong></td>
        <td>Registro de Novedades Físicas</td>
        <td>Permitir registrar observaciones sobre el estado físico del automotor (rayones o golpes) al ingresar o salir.</td>
      </tr>
    </tbody>
  </table>

  <h2>3.2 Requerimientos No Funcionales (RNF)</h2>
  <table class="data-table">
    <thead>
      <tr>
        <th style="width: 12%;">Código</th>
        <th style="width: 25%;">Atributo</th>
        <th style="width: 63%;">Especificación Técnica Implementada</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>RNF-01</strong></td>
        <td>Concurrencia Multi-Operario</td>
        <td>Servidor HTTP multi-hilo (<code>ThreadedHTTPServer</code>), serialización mediante <code>threading.Lock</code> y base de datos SQLite en modo <code>WAL</code>.</td>
      </tr>
      <tr>
        <td><strong>RNF-02</strong></td>
        <td>Rendimiento</td>
        <td>Tiempo de respuesta en consultas de placa, validación de vigencias y asignación aleatoria inferior a 2 segundos (promedio real: &lt; 60 ms).</td>
      </tr>
      <tr>
        <td><strong>RNF-03</strong></td>
        <td>Control de Ocupación en Backend</td>
        <td><strong>[Ajuste Backend]:</strong> Mecanismo centralizado de control de aforo para las 80 celdas físicas (70 carros / 10 motos). Implementa exclusión mutua en memoria (<code>db_lock</code>) y transacciones atómicas SQLite (<code>BEGIN IMMEDIATE</code>) bajo modo WAL. Filtra celdas libres por categoría vehicular, excluyendo celdas ocupadas o en mantenimiento. Si las celdas disponibles para el tipo son cero (0), deniega de inmediato la transacción con código <code>AFORO_COMPLETO</code>, impidiendo cualquier sobrecupo o doble asignación concurrente.</td>
      </tr>
      <tr>
        <td><strong>RNF-04</strong></td>
        <td>Integridad de Datos</td>
        <td>Integridad referencial activa (<code>PRAGMA foreign_keys = ON</code>), modelo relacional normalizado en 3FN y control antiduplicidad estricto.</td>
      </tr>
      <tr>
        <td><strong>RNF-05</strong></td>
        <td>Disponibilidad 24/7</td>
        <td>Operación continua 24/7 con sincronización en tiempo real y UI basada en el sistema <em>Cobalt Bay OS</em>.</td>
      </tr>
    </tbody>
  </table>

  <div class="page-break"></div>

  <!-- 4. HISTORIAS DE USUARIO Y CRITERIOS DE ACEPTACIÓN -->
  <h1>4. HISTORIAS DE USUARIO CON CRITERIOS DE ACEPTACIÓN COMPLETOS</h1>

  <p><strong>HU-01: Registro de Ingreso, Validación y Asignación Dinámica de Celda</strong><br>
  <em>Como</em> Operario de Cabina, <em>quiero</em> digitar la placa de un vehículo que llega a la portería <em>para</em> validar su mensualidad, comprobar sus datos físicos y asignarle aleatoriamente una celda disponible según su categoría.</p>
  <div class="gherkin-box">
    <strong>Criterio 1 (Flujo Exitoso - Ingreso y Asignación):</strong><br>
    <strong>Dado</strong> que el vehículo 'TOY-456' (Carro) está registrado en el padrón de abonados con mensualidad vigente y existen celdas de carro libres,<br>
    <strong>Cuando</strong> el operario digita la placa y acciona "¡Abrir Barrera y Asignar Celda!",<br>
    <strong>Entonces</strong> el backend selecciona aleatoriamente una celda libre (ej. C-24), cambia su estado a OCUPADA, estampa la hora exacta de ingreso, abre la barrera y actualiza el mapa en vivo.
  </div>
  <div class="gherkin-box gherkin-exception">
    <strong>Criterio 2 (Excepción Evaluada - Placa Inexistente / No Registrada):</strong><br>
    <strong>Dado</strong> que llega un vehículo con una placa que no se encuentra en el padrón de abonados (ej. 'ZZZ-000'),<br>
    <strong>Cuando</strong> el operario digita la placa y consulta o intenta registrar el ingreso,<br>
    <strong>Entonces</strong> el sistema bloquea la apertura de barrera, genera el código de error <code>NO_REGISTRADO</code>, proyecta la alerta roja: <em>"El vehículo con placa 'ZZZ-000' NO se encuentra registrado en el padrón de abonados. El parqueadero opera exclusivamente bajo modalidad de mensualidad"</em>, registra la incidencia en la auditoría y no altera ninguna celda.
  </div>
  <div class="gherkin-box gherkin-exception">
    <strong>Criterio 3 (Excepción Evaluada - Control Antiduplicidad / Ya Adentro):</strong><br>
    <strong>Dado</strong> que el vehículo 'TOY-456' ya figura adentro del parqueadero en estado ADENTRO ocupando la celda C-24,<br>
    <strong>Cuando</strong> se intenta registrar nuevamente su entrada por cualquier puerta de acceso,<br>
    <strong>Entonces</strong> el backend bloquea la transacción, emite el código de error <code>YA_ADENTRO</code> con la advertencia: <em>"Control de duplicidad: El vehículo 'TOY-456' ya figura ADENTRO en la celda C-24. No se autoriza doble ingreso sin registro previo de salida"</em>, y mantiene la barrera cerrada.
  </div>

  <p><strong>HU-02: Bloqueo de Acceso por Mensualidad Vencida (Cero Periodo de Gracia)</strong><br>
  <em>Como</em> Operario de Cabina, <em>quiero</em> que el sistema verifique la fecha exacta de corte de la mensualidad <em>para</em> impedir el ingreso de automotores morosos.</p>
  <div class="gherkin-box gherkin-exception">
    <strong>Criterio 1 (Excepción - Mensualidad Expirada):</strong><br>
    <strong>Dado</strong> que el vehículo 'XYZ-999' tiene su mensualidad vencida (fecha de corte previa a la fecha actual),<br>
    <strong>Cuando</strong> el operario digita la placa para ingresar,<br>
    <strong>Entonces</strong> el sistema bloquea la barrera y emite la alerta roja: <em>"Acceso Denegado: La mensualidad del vehículo 'XYZ-999' está VENCIDA. No existe periodo de gracia"</em> con código <code>MENSUALIDAD_VENCIDA</code>.
  </div>

  <p><strong>HU-03: Verificación Visual de Atributos y Registro de Novedades Físicas</strong><br>
  <em>Como</em> Operario de Cabina, <em>quiero</em> ver placa, marca, modelo, color y conductor registrado, y poder asentar observaciones <em>para</em> dejar constancia de rayones o pertenencias.</p>
  <div class="gherkin-box">
    <strong>Criterio 1 (Flujo Exitoso - Con Novedad Física):</strong><br>
    <strong>Dado</strong> que la motocicleta 'MOT-808' ingresa presentando un rayón previo en el carenaje,<br>
    <strong>Cuando</strong> el operario digita la novedad física y confirma el ingreso,<br>
    <strong>Entonces</strong> la observación queda guardada de manera indeleble en el registro de acceso y en la bitácora de auditoría inmutable.
  </div>

  <p><strong>HU-04: Control Estricto de Capacidad Máxima (70 Carros / 10 Motos)</strong><br>
  <em>Como</em> Administrador / Operario, <em>quiero</em> que el sistema bloquee el ingreso al agotarse las celdas de una categoría vehicular <em>para</em> evitar sobrecupos.</p>
  <div class="gherkin-box gherkin-exception">
    <strong>Criterio 1 (Excepción - Capacidad Máxima Alcanzada):</strong><br>
    <strong>Dado</strong> que las 10 celdas de moto se encuentran en estado OCUPADA,<br>
    <strong>Cuando</strong> una motocicleta al día intenta ingresar,<br>
    <strong>Entonces</strong> el sistema deniega el acceso con código <code>AFORO_COMPLETO</code> informando: <em>"Capacidad máxima alcanzada para MOTOs (10/10 celdas ocupadas)"</em> y mantiene la barrera cerrada.
  </div>

  <p><strong>HU-05: Registro de Salida, Liquidación de Estancia y Liberación Inmediata de Celda</strong><br>
  <em>Como</em> Operario de Cabina de Salida, <em>quiero</em> registrar el egreso de un automotor <em>para</em> liberar su celda al instante y calcular el tiempo de permanencia.</p>
  <div class="gherkin-box">
    <strong>Criterio 1 (Flujo Exitoso - Salida y Liberación en 1 Clic):</strong><br>
    <strong>Dado</strong> que el vehículo 'TOY-456' figura ADENTRO ocupando la celda C-24,<br>
    <strong>Cuando</strong> el operario presiona "Dar Salida",<br>
    <strong>Entonces</strong> el sistema registra la fecha/hora de salida, liquida la permanencia exacta, marca el registro como FINALIZADO y cambia la celda C-24 a DISPONIBLE en tiempo real.
  </div>
  <div class="gherkin-box gherkin-exception">
    <strong>Criterio 2 (Excepción Evaluada - Salida de Vehículo sin Registro Activo / No Adentro):</strong><br>
    <strong>Dado</strong> que el automotor 'KTM-505' no se encuentra adentro del parqueadero (su registro está FINALIZADO o nunca ha ingresado),<br>
    <strong>Cuando</strong> un operario intenta forzar el registro de salida para dicha placa,<br>
    <strong>Entonces</strong> el backend rechaza la solicitud con código <code>NO_ADENTRO</code>, proyecta la alerta: <em>"Operación inválida: El vehículo 'KTM-505' no figura actualmente adentro del parqueadero"</em>, mantiene bloqueada la barrera de salida y no altera ninguna celda.
  </div>

  <div class="page-break"></div>

  <!-- 5. MOCKUPS DE FIGMA -->
  <h1>5. MOCKUPS DE LAS HISTORIAS DE USUARIO EN FIGMA</h1>
  <p>
    Los prototipos visuales de alta fidelidad fueron concebidos bajo el sistema de diseño <em>Cobalt Bay OS</em>, accesible públicamente en Google Stitch y Figma:
  </p>

  <div class="diagram-container">
    <h3>Figura 1. Guía de Estilos y Design Tokens en Figma</h3>
    <img src="extracted_pdf_images/page_10_X29.png" alt="Design Tokens Figma">
    <div class="diagram-caption">Especificación de tokens visuales: paleta de colores operativos, estados de celdas, tipografía monoespaciada e iconografía.</div>
  </div>

  <div class="diagram-container">
    <h3>Figura 2. Mockup de Interfaz Principal de Control de Acceso</h3>
    <img src="extracted_pdf_images/page_11_X32.png" alt="Mockup Interfaz Principal">
    <div class="diagram-caption">Consola operativa unificada: validación de placa, ficha de seguridad del vehículo, asignación dinámica y registro de novedades.</div>
  </div>

  <div class="page-break"></div>

  <div class="diagram-container">
    <h3>Figura 3. Mockup del Mapa Interactivo de las 80 Celdas</h3>
    <img src="extracted_pdf_images/page_12_X35.png" alt="Mockup Mapa de Celdas">
    <div class="diagram-caption">Plano visual de distribución física: 70 celdas de carro y 10 de moto con código de color en tiempo real (Disponible, Ocupada, Mantenimiento).</div>
  </div>

  <div class="diagram-container">
    <h3>Figura 4. Mockup del Padrón de Abonados y Mensualidades</h3>
    <img src="extracted_pdf_images/page_13_X38.png" alt="Mockup Abonados">
    <div class="diagram-caption">Control de titulares, placas vinculadas, tarifas individuales ($250k / $100k) y semáforo de vigencia sin periodo de gracia.</div>
  </div>

  <div class="page-break"></div>

  <div class="diagram-container">
    <h3>Figura 5. Mockup de Bitácora de Auditoría y Trazabilidad</h3>
    <img src="extracted_pdf_images/page_14_X41.png" alt="Mockup Auditoría">
    <div class="diagram-caption">Historial inmutable de movimientos, cálculo de tiempo de permanencia, registro de novedades físicas y operario responsable.</div>
  </div>

  <div class="page-break"></div>

  <!-- 6. ARQUITECTURA Y DIAGRAMAS UML STARUML -->
  <h1>6. ARQUITECTURA DEL SISTEMA Y MODELADO UML EN STARUML (CORREGIDOS)</h1>

  <h2>6.1 Arquitectura de Componentes e Interfaces</h2>
  <div class="diagram-container">
    <img src="extracted_pdf_images/page_9_X24.png" alt="Arquitectura de Componentes">
    <div class="diagram-caption">Figura 6. Arquitectura de componentes desacoplados: SPA Web, Servidor REST Concurrente y Persistencia SQLite en modo WAL.</div>
  </div>

  <h2>6.2 Diagrama de Paquetes UML con Dependencias (Corregido)</h2>
  <p>
    En atención a las observaciones del docente, se estructuró el diagrama de paquetes bajo la notación formal UML tipo carpeta (<em>tabbed folder</em>), reflejando la jerarquía de capas y las relaciones de dependencia unidireccionales (<code>&laquo;use&raquo;</code> y <code>&laquo;access&raquo;</code>):
  </p>
  <div class="diagram-container">
    <img src="diagramas/Diagrama_Paquetes_Arquitectura_Corregido.png" alt="Diagrama de Paquetes Corregido">
    <div class="diagram-caption">Figura 7. Diagrama de paquetes UML corregido: separación estricta en capas (Presentación, Controladores/API, Dominio y Persistencia) con dependencias explícitas.</div>
  </div>

  <div class="page-break"></div>

  <h2>6.3 Diagrama de Casos de Uso Corregido (Sintaxis Estricta OMG UML 2.5)</h2>
  <p>
    Se efectuaron las siguientes correcciones rigurosas de modelado:
  </p>
  <ul>
    <li><strong>Dirección de «extend»:</strong> La flecha apunta estrictamente <strong>desde el caso de uso que extiende (extensión) hacia el caso base</strong>, tal como lo exige el estándar OMG UML 2.5 (ej. <code>CU-06a Denegar por Mora</code> &rarr; <code>CU-02 Validar Mensualidad</code>; <code>CU-06c Bloquear Duplicado</code> &rarr; <code>CU-04 Registrar Entrada</code>; <code>CU-06d Rechazar Placa Inexistente</code> &rarr; <code>CU-01 Consultar Placa</code>; <code>CU-08b Denegar Salida</code> &rarr; <code>CU-07 Registrar Salida</code>).</li>
    <li><strong>Eliminación de «include» hacia Actores:</strong> En UML, los actores no admiten relaciones de inclusión. El actor secundario <em>Reloj del Servidor 24/7</em> interactúa mediante asociaciones de comunicación estándar, y las funciones de estampar timestamp y liquidar permanencia se modelaron como casos de uso incluidos legítimos (<code>CU-11</code> y <code>CU-12</code>).</li>
  </ul>
  <div class="diagram-container">
    <img src="diagramas/Diagrama_Casos_de_Uso_Iteracion_1_Corregido.png" alt="Casos de Uso Corregido">
    <div class="diagram-caption">Figura 8. Diagrama de casos de uso corregido conforme a los lineamientos OMG UML 2.5.</div>
  </div>

  <div class="page-break"></div>

  <h2>6.4 Diagrama de Clases del Dominio</h2>
  <div class="diagram-container">
    <img src="extracted_pdf_images/page_16_X48.jpg" alt="Diagrama de Clases">
    <div class="diagram-caption">Figura 9. Diagrama de clases del dominio en StarUML: entidades (Propietario, Vehiculo, Mensualidad, Celda, RegistroAcceso) y clase orquestadora ParqueaderoService.</div>
  </div>

  <h2>6.5 Diagramas de Secuencia: Ingreso y Salida</h2>
  <div class="diagram-container">
    <img src="extracted_pdf_images/page_17_X51.png" alt="Secuencia Ingreso">
    <div class="diagram-caption">Figura 10. Diagrama de secuencia del proceso de ingreso y asignación aleatoria de celdas.</div>
  </div>

  <div class="page-break"></div>

  <div class="diagram-container">
    <img src="extracted_pdf_images/page_18_X55.png" alt="Secuencia Salida">
    <div class="diagram-caption">Figura 11. Diagrama de secuencia del proceso de egreso, cálculo de permanencia y liberación inmediata de celdas.</div>
  </div>

  <!-- 7. DISEÑO DE BASE DE DATOS -->
  <h1>7. DISEÑO DE BASE DE DATOS (MER, MR Y MODELO FÍSICO)</h1>
  <p>
    El esquema relacional fue diseñado y normalizado en Tercera Forma Normal (3FN), garantizando integridad referencial, soporte concurrente WAL y consultas de alta velocidad mediante índices especializados:
  </p>
  <div class="diagram-container">
    <img src="extracted_pdf_images/page_20_X62.png" alt="MER y MR">
    <div class="diagram-caption">Figura 12. Modelo Entidad-Relación (MER) y Modelo Relacional (MR) en 3FN con llaves primarias (PK) y foráneas (FK).</div>
  </div>
  <p>
    <strong>Modelo Físico SQL:</strong> Implementado en el archivo ejecutable <code>database_schema.sql</code>, el cual incluye las sentencias DDL para las tablas maestras (<code>propietario</code>, <code>vehiculo</code>, <code>mensualidad</code>, <code>celda</code> y <code>registro_acceso</code>) y precarga las 80 celdas físicas reglamentarias (10 para motos y 70 para carros).
  </p>

  <div class="page-break"></div>

  <!-- 8. BATERÍA DE PRUEBAS AUTOMATIZADAS -->
  <h1>8. BATERÍA DE PRUEBAS AUTOMATIZADAS (VERIFICACIÓN DE CRITERIOS)</h1>
  <p>
    Con el fin de validar el 100% de los requerimientos y los criterios de aceptación evaluados por el docente, se ejecutó la suite de pruebas unitarias y de integración en Python (<code>tests_iteracion1_corregido.py</code>), arrojando una tasa de éxito perfecta (<strong>7 de 7 pruebas aprobadas</strong>):
  </p>

  <table class="data-table">
    <thead>
      <tr>
        <th style="width: 12%;">Prueba</th>
        <th style="width: 28%;">Requerimiento / Criterio</th>
        <th style="width: 25%;">Condición de Entrada</th>
        <th style="width: 25%;">Resultado Verificado</th>
        <th style="width: 10%;">Estado</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>CP-01</strong></td>
        <td>Ingreso Exitoso y Sorteo de Celda</td>
        <td>Placa <code>TOY-456</code> al día en pago</td>
        <td>Asignada celda libre de carro (C-XX); estado ADENTRO</td>
        <td><strong style="color: #16a34a;">APROBADO</strong></td>
      </tr>
      <tr>
        <td><strong>CP-02</strong></td>
        <td>Placa Inexistente (Criterio HU-01)</td>
        <td>Placa no registrada <code>ZZZ-999</code></td>
        <td>Rechazo <code>NO_REGISTRADO</code>; barrera bloqueada</td>
        <td><strong style="color: #16a34a;">APROBADO</strong></td>
      </tr>
      <tr>
        <td><strong>CP-03</strong></td>
        <td>Ingreso Duplicado (Criterio HU-01)</td>
        <td>Vehículo que ya figura ADENTRO</td>
        <td>Rechazo <code>YA_ADENTRO</code>; celda actual informada</td>
        <td><strong style="color: #16a34a;">APROBADO</strong></td>
      </tr>
      <tr>
        <td><strong>CP-04</strong></td>
        <td>Mensualidad Vencida (Criterio HU-02)</td>
        <td>Placa <code>XYZ-999</code> con fecha vencida</td>
        <td>Rechazo <code>MENSUALIDAD_VENCIDA</code> (0 días de gracia)</td>
        <td><strong style="color: #16a34a;">APROBADO</strong></td>
      </tr>
      <tr>
        <td><strong>CP-05</strong></td>
        <td>Salida y Liberación de Celda (HU-05)</td>
        <td>Placa <code>TOY-456</code> estacionada</td>
        <td>Celda liberada a DISPONIBLE y tiempo liquidado</td>
        <td><strong style="color: #16a34a;">APROBADO</strong></td>
      </tr>
      <tr>
        <td><strong>CP-06</strong></td>
        <td>Salida sin Registro Activo (HU-05)</td>
        <td>Placa <code>TOY-456</code> que ya salió</td>
        <td>Rechazo <code>NO_ADENTRO</code>; no altera ninguna celda</td>
        <td><strong style="color: #16a34a;">APROBADO</strong></td>
      </tr>
      <tr>
        <td><strong>CP-07</strong></td>
        <td>Control de Ocupación Backend (RNF-03)</td>
        <td>Validación de aforo global</td>
        <td>Límite estricto de 70 carros y 10 motos respetado</td>
        <td><strong style="color: #16a34a;">APROBADO</strong></td>
      </tr>
    </tbody>
  </table>

  <!-- 9. CONCLUSIONES -->
  <h1>9. CONCLUSIONES</h1>
  <ol>
    <li><strong>Subsanación Integral de Observaciones:</strong> Se atendieron con rigor técnico todos los comentarios de la evaluación: se ampliaron los criterios de aceptación en Gherkin para placas inexistentes, ingresos duplicados y salidas sin registro activo; se corrigió el diagrama de casos de uso invirtiendo la dirección de <code>&laquo;extend&raquo;</code> y eliminando includes a actores; se estandarizó el diagrama de paquetes con dependencias explícitas; y se profundizó el RNF-03 documentando el control transaccional de ocupación en backend.</li>
    <li><strong>Garantía de Reglas de Negocio sin Errores Humanos:</strong> El parqueadero opera de forma confiable bajo modalidad exclusiva de mensualidad ($250.000 carro / $100.000 moto), cero periodo de gracia y asignación aleatoria de celdas, resguardando la capacidad máxima de 80 celdas mediante esclusas transaccionales <code>db_lock</code> y <code>BEGIN IMMEDIATE</code> en SQLite WAL.</li>
    <li><strong>Arquitectura Escalable para Siguientes Fases:</strong> La estricta separación de responsabilidades en capas (Presentación, Controladores REST, Dominio y Persistencia) garantiza una base modular sólida para la incorporación ágil de la administración de usuarios RBAC (Iteración 2) y facturación (Iteración 3).</li>
  </ol>

  <!-- 10. REFERENCIAS -->
  <h1>10. REFERENCIAS BIBLIOGRÁFICAS (NORMAS APA 7.ª EDICIÓN)</h1>
  <ul>
    <li>Booch, G., Rumbaugh, J., & Jacobson, I. (2006). <em>El lenguaje unificado de modelado: Guía del usuario</em> (2.ª ed.). Addison-Wesley.</li>
    <li>Elmasri, R., & Navathe, S. B. (2017). <em>Fundamentos de sistemas de bases de datos</em> (7.ª ed.). Pearson Educación.</li>
    <li>Fowler, M. (2003). <em>Patterns of enterprise application architecture</em>. Addison-Wesley Professional.</li>
    <li>Object Management Group (OMG). (2017). <em>OMG Unified Modeling Language (OMG UML) Specification, Version 2.5.1</em>. Object Management Group.</li>
    <li>Pressman, R. S., & Maxim, B. R. (2021). <em>Ingeniería del software: Un enfoque práctico</em> (9.ª ed.). McGraw-Hill.</li>
    <li>Sommerville, I. (2016). <em>Ingeniería de software</em> (10.ª ed.). Pearson Educación.</li>
  </ul>

  <div class="footer-text">
    Sistema de Información Parqueadero Autos Colombia 24/7 &bull; Evidencia de Aprendizaje 1 (Iteración 1 - Corregido) &bull; IU Digital de Antioquia
  </div>

</body>
</html>
"""

def compilar():
    print("[*] Escribiendo archivo HTML imprimible...")
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[OK] Archivo HTML actualizado: {HTML_PATH}")

    print("[*] Compilando a PDF con Microsoft Edge Headless...")
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
        print(f"[EXITO] PDF Oficial generado: {PDF_PATH} ({size} bytes)")

        # Generar copias con nombres oficiales solicitados
        entrega_estudiante_pdf = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), "PalaciosTurriago_CamiloAlberto_EA1.pdf")
        shutil.copyfile(PDF_PATH, entrega_estudiante_pdf)
        print(f"[OK] Copia para entrega generada: {entrega_estudiante_pdf}")

        entrega_corregida_pdf = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), "SISTEMA DE GESTION DE OPERACIONES_ PARQUEADERO _AUTOS COLOMBIA__CORREGIDO.pdf")
        shutil.copyfile(PDF_PATH, entrega_corregida_pdf)
        print(f"[OK] Copia para entrega generada: {entrega_corregida_pdf}")

    except Exception as e:
        print(f"[ERROR] Error al compilar PDF: {e}")

if __name__ == "__main__":
    compilar()
