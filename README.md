# 🚗 Autos Colombia 24/7 - Sistema de Control de Acceso
### Proyecto Académico: Desarrollo de Software / Ingeniería de Software
**Docente:** Reinaldo Rojas  
**Iteración:** 1 (Módulo Exclusivo de Entrada y Salida de Vehículos)  
**Modalidad de Operación:** Exclusiva por Mensualidad · 24 Horas / 7 Días a la Semana  
**Capacidad Oficial:** 80 Celdas (70 Carros y 10 Motos)

---

## 📌 1. Descripción del Proyecto

**Autos Colombia 24/7** es una aplicación integral desarrollada para la gestión automatizada del control de acceso vehicular en parqueaderos corporativos que operan bajo el modelo de suscripción mensual. 

Conforme a las directrices de la **Iteración 1** dictadas por el profesor Reinaldo Rojas:
* El sistema se enfoca **exclusivamente en la gestión de Entrada y Salida de vehículos**.
* Se excluye para esta entrega la administración compleja de usuarios y pasarelas de pago (programadas para iteraciones 2 y 3).
* La asignación de celdas es **100% dinámica y aleatoria** por software entre las celdas disponibles para el tipo de automotor (no hay celdas fijas por cliente).
* El cobro se realiza **por vehículo** (\$250.000 COP Carro, \$100.000 COP Moto). Si la mensualidad está vencida, el sistema **deniega el ingreso**.
* Aforo estricto de **80 celdas físicas** (10 para motos y 70 para vehículos/carros).

---

## 🚀 2. Ejecución Rápida en 1 Solo Paso

La aplicación fue desarrollada en **Python 3** utilizando la librería estándar para garantizar **cero dependencias externas**. No requiere configurar entornos virtuales complejos ni instalar librerías pesadas con `pip`.

### Paso 1: Iniciar el Servidor
Abre tu terminal en la carpeta del proyecto y ejecuta:

```bash
python app.py
```

### Paso 2: Abrir la Aplicación Web
Ingresa en cualquier navegador web a:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 🧪 3. Guía de Pruebas Rápidas para el Docente

La interfaz cuenta con **botones de prueba rápida en 1 clic** en el módulo de entrada para verificar inmediatamente todas las reglas de negocio:

1. **Prueba de Ingreso Autorizado (Carro):**
   - Haz clic en el botón `ABC-123 (Carro Al Día)`.
   - Se cargarán los datos: *Renault Duster Intens 2.0 (Gris Plata)*, conductor *Juan Carlos Pérez*, mensualidad vigente.
   - Pulsa **`🟢 ¡ABRIR BARRERA DE ENTRADA!`**.
   - El sistema sorteará y asignará una celda aleatoria disponible (ej: `C-24`), marcará la celda como ocupada, guardará el timestamp y actualizará los contadores.

2. **Prueba de Ingreso Autorizado (Moto):**
   - Haz clic en el botón `MOT-808 (Moto Al Día)`.
   - Se cargarán los datos: *Yamaha NMAX 155 (Azul Mate)*.
   - Pulsa **`🟢 ¡ABRIR BARRERA DE ENTRADA!`**.
   - Se asignará una celda aleatoria exclusiva para motos entre `M-01` y `M-10`.

3. **Prueba de Bloqueo por Mensualidad Vencida (Mora):**
   - Haz clic en `XYZ-999 (Carro Vencido)` o `MOT-101 (Moto Vencida)`.
   - El sistema mostrará una tarjeta en color rojo: **`MENSUALIDAD VENCIDA - ACCESO DENEGADO`**.
   - El botón de apertura quedará deshabilitado para impedir el paso.

4. **Prueba de Salida Rápida y Liberación Inmediata de Celda:**
   - En la columna derecha ("Vehículos Estacionados Adentro"), pulsa el botón **`Dar Salida`** de cualquier vehículo.
   - La celda se liberará inmediatamente, volverá al pool de disponibles y se calculará el tiempo de permanencia sin cobros adicionales en efectivo.

5. **Inspección del Mapa de las 80 Celdas:**
   - Navega a la pestaña **`2. Mapa 80 Celdas`**.
   - Observa la matriz de 80 celdas en tiempo real con semáforo verde (libre) y rojo (ocupado).
   - Haz clic sobre cualquier celda para ver su ficha técnica, placa ocupante y conductor.

---

## 📂 4. Estructura del Repositorio y Entregables

```text
aplicacion de parqueo/
├── app.py                      # Servidor HTTP nativo y API REST (Python 3)
├── database.py                 # Conexión SQLite, ORM transaccional y DDL automático
├── models.py                   # Lógica del dominio (asignación aleatoria, control de aforo)
├── database_schema.sql         # Script SQL físico DDL/DML (Entregable Base de Datos)
├── autos_colombia.db           # Base de datos SQLite inicializada con 80 celdas
│
├── static/                     # Frontend SPA basado en Cobalt Bay OS (Stitch)
│   ├── index.html              # Interfaz de usuario interactiva y responsiva
│   └── app.js                  # Lógica del cliente, polling 24/7 y mapa de celdas
│
├── docs/                       # Documentación técnica completa exigida
│   ├── DOCUMENTACION_TECNICA_ITERACION_1.md # Documento formal (RF, RNF, Historias de Usuario)
│   ├── MODELADO_STARUML_Y_ARQUITECTURA.md  # Arquitectura en capas y diagramas UML
│   ├── staruml_diagrams.puml               # Código fuente PlantUML compatible con StarUML
│   ├── BASE_DE_DATOS_MER_MR.md             # MER Conceptual, MR Lógico y Diccionario de Datos
│   ├── DISENO_VISUAL_FIGMA_Y_STITCH.md     # Especificación de tokens, Figma y Cobalt Bay OS
│   └── GUIA_GITHUB_Y_ENTREGA.md            # Guía para subir a GitHub y checklist de entrega
│
└── stitch_parking_app_design/  # Diseños y capturas de alta fidelidad provistas en Stitch
```

---

## 📑 5. Resumen de Entregables Académicos

| Entregable | Ubicación / Archivo | Estado |
|---|---|---|
| **Documentación Escrita (PDF/MD)** | `docs/DOCUMENTACION_TECNICA_ITERACION_1.md` | ✅ Completo (Portada, RF, RNF, Historias de Usuario Gherkin) |
| **Modelado en StarUML** | `docs/MODELADO_STARUML_Y_ARQUITECTURA.md` y `docs/staruml_diagrams.puml` | ✅ Completo (Arquitectura, Casos de Uso, Clases, Paquetes, Secuencia) |
| **Base de Datos (MER, MR y SQL Físico)** | `docs/BASE_DE_DATOS_MER_MR.md` y `database_schema.sql` | ✅ Completo (80 celdas: 10 motos + 70 carros, datos semilla de prueba) |
| **Diseño Visual (Figma / Stitch)** | `docs/DISENO_VISUAL_FIGMA_Y_STITCH.md` y `stitch_parking_app_design/` | ✅ Completo (Sistema Cobalt Bay OS, interfaz responsiva 24/7) |
| **Código Fuente y Repositorio** | `app.py`, `models.py`, `database.py`, `static/` | ✅ Completo (Funcional, cero dependencias, listo para GitHub) |

---

## 🛠️ Tecnologías Utilizadas

* **Backend:** Python 3 (HTTP REST API, SQLite3 transaccional, PRAGMA Foreign Keys ON).
* **Frontend:** HTML5, Tailwind CSS, JavaScript Vanilla (Fetch API, Reactividad DOM).
* **Tipografías:** Plus Jakarta Sans (Encabezados), JetBrains Mono (Placas y Códigos LPR), Inter (Tablas y métricas).
* **Diseño e Iconografía:** Cobalt Bay OS (Stitch Design System), SVG estándar.
* **Control de Versiones:** Git & GitHub.
