# PARQUEADERO AUTOS COLOMBIA 24/7
## DISEÑO VISUAL: SISTEMA COBALT BAY OS, FIGMA Y PROTOTIPO STITCH
### ITERACIÓN 1: MÓDULO DE ENTRADA Y SALIDA
**Docente:** Reinaldo Rojas

---

## 1. FUNDAMENTOS DEL DISEÑO VISUAL (COBALT BAY OS)

Para el desarrollo del sistema de parqueadero **Autos Colombia 24/7**, se adoptó el sistema de diseño industrial y operativo **Cobalt Bay OS** (diseñado originalmente en Stitch e integrado en la aplicación web funcional). Este sistema está optimizado para interfaces táctiles y consolas de operadores de control en turnos continuos de 8 a 12 horas, minimizando la fatiga visual y garantizando legibilidad instantánea a más de un metro de distancia de la pantalla.

### Tokens de Color Principales
* **Primario (Acción y Apertura):** Cobalt Blue `#1D4ED8` y Emerald Green `#10B981` (Apertura de Barrera y Celdas Libres).
* **Alerta y Denegación (Mora / Vencimiento):** Crimson Red `#EF4444` y Amber Warning `#F59E0B`.
* **Fondo Canvas 24/7:** Light Slate Surface `#F8FAFC` con paneles en blanco `#FFFFFF` delimitados por bordes de 1px en `#E2E8F0`.
* **Modo Noche / Puestos:** Slate `#0F172A` para indicadores técnicos y cabina de control.

### Tipografía Operativa
* **Machine Identifiers & Placas LPR:** `JetBrains Mono` con espaciado (*letter-spacing*) de `0.08em` para evitar cualquier confusión entre caracteres como `0` y `O` o `1` e `I`.
* **Títulos y Contadores:** `Plus Jakarta Sans` en pesos `700` y `800`.
* **Cuerpo y Tablas de Auditoría:** `Inter` con números tabulares (`tnum`).

---

## 2. PANTALLAS DISEÑADAS Y PROTOTIPADAS

El entregable cuenta con las siguientes pantallas y componentes visuales creados para la entrega:

### Pantalla 1: Punto de Control de Entrada y Salida 24/7 (Principal)
* **Header Operativo:** Semáforo con disponibilidad en vivo de Carros (`18 Libres / 70`) y Motos (`3 Libres / 10`), estado 24/7 y reloj en vivo.
* **Módulo de Entrada (Paso 1):**
  - Caja de entrada de placa en tamaño gigante monospace con formato de máscara automática (`AAA-000`).
  - Botonera rápida de prueba en 1 clic para el docente (`ABC-123`, `MOT-808`, `XYZ-999`, `MOT-101`).
  - Ficha técnica del vehículo (Marca, Modelo, Color, Conductor).
  - Alerta de estado de pago (Verde: Mensualidad Vigente / Rojo: Mensualidad Vencida - Acceso Denegado).
  - Bloque visual de asignación aleatoria/dinámica de celda.
  - Botón táctil principal: `🟢 ¡ABRIR BARRERA DE ENTRADA!`.
* **Módulo de Vehículos Adentro y Salida Rápida (Paso 2):**
  - Contador de vehículos en sede.
  - Buscador reactivo por placa, modelo o celda.
  - Tarjetas de vehículos estacionados con tiempo transcurrido y botón `Dar Salida` en 1 clic.

### Pantalla 2: Mapa Visual de las 80 Celdas
* **Grilla Interactiva 80 Bays:**
  - 10 celdas para Motos (`M-01` a `M-10`).
  - 70 celdas para Carros (`C-01` a `C-70`).
  - Semáforo de estado: Verde (Disponible) y Rojo (Ocupado con la placa visible).
  - Filtros rápidos: Todas (80), Carros (70), Motos (10), Solo Libres, Solo Ocupadas.
  - Panel de inspección detallado al hacer clic sobre cualquier celda.

### Pantalla 3: Padrón de Abonados y Tarifas
* Resumen de cartera: Al día (\$250k Carro, \$100k Moto) y vencidos.
* Tabla completa de clientes registrados y opción de registrar nuevos vehículos de prueba.

### Pantalla 4: Auditoría de Movimientos 24/7
* Registro cronológico de ingresos y egresos con celda asignada, hora de entrada, hora de salida y estado.

---

## 3. INTEGRACIÓN CON FIGMA Y PROTOTIPO STITCH

La carpeta provista en el proyecto:
📁 `stitch_parking_app_design/`
contiene los archivos fuente y prototipos originales:
* `cobalt_bay_os/DESIGN.md`: Documento maestro de tokens de diseño, espaciados y jerarquía visual.
* `autos_colombia_24_7_prototipo_funcional_unificado/code.html` y `screen.png`: Prototipo interactivo visual de alta fidelidad.
* `autos_colombia_control_24_7_entrada_y_salida/code.html` y `screen.png`: Prototipo de cabina y checkout.

### Cómo importar y presentar en Figma:
1. Abrir **Figma**.
2. Crear un nuevo archivo de diseño llamado **"Autos Colombia 24/7 - UI Design"**.
3. Importar los archivos de imagen `screen.png` presentes en las subcarpetas de `stitch_parking_app_design/` como base de los frames (1440x900px Desktop).
4. O utilizar el plugin **HTML to Design** de Figma e importar la URL local o el archivo `static/index.html` para convertir directamente la interfaz en capas editables de Figma.
5. El enlace al archivo Figma generado por el equipo puede ser adjuntado en la entrega final del repositorio según las indicaciones del docente.
