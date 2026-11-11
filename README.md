# 🚗 Autos Colombia 24/7 — Sistema Integral de Operaciones de Parqueadero
### Institución Universitaria Digital de Antioquia (IU Digital) • Ingeniería de Software (`PREICA2602B020053`)
**Docente:** Prof. Reinaldo Rojas | **Grupo:** 25  
**Integrantes:** Adriana Andrea Agudelo Agudelo · Camilo Alberto Palacios Turriago · Juan Daniel Pulgarin García  
**Alcance Actual:** **Iteraciones 1, 2 y 3 Unificadas** *(Control de Acceso 24/7 + Usuarios RBAC + 80 Celdas + Gestión de Pagos)*

---

## 📌 1. Descripción Arquitectónica (Iteraciones 1, 2 y 3)

**Autos Colombia 24/7** es una aplicación web transaccional multi-operario diseñada para administrar la operación continua (24 horas / 7 días) de un parqueadero corporativo bajo contratos exclusivos de mensualidad sobre un aforo físico reglamentario de **80 celdas numeradas** (**70 para automóviles `C-01..C-70`** en Pisos 1 y 2, y **10 para motocicletas `M-01..M-10`**).

### Módulos Integrados en esta Entrega Final:
1. **Control de Acceso 24/7 (Iteración 1 + Integración Iteraciones 2 y 3):**
   - Verificación estricta de vigencia mensual sin días de gracia (`$250.000 COP` Carro / `$100.000 COP` Moto).
   - Sorteo dinámico aleatorio sobre celdas `DISPONIBLE` compatibles, **excluyendo automáticamente toda celda en estado `MANTENIMIENTO` o `INACTIVA`**.
   - Registro de novedades físicas de seguridad en ronda y salida con liberación atómica de celda.
2. **Gestión de Usuarios, Roles y Permisos — RBAC + SHA-256 (Iteración 2):**
   - Dispersión criptográfica de contraseñas mediante `SHA-256` (cero claves en texto plano).
   - Matriz declarativa de Control de Acceso Basado en Roles (**`ADMIN`**, **`OPERARIO`**, **`AUDITOR`**) validada en cada endpoint HTTP (`401 Unauthorized` / `403 Forbidden`).
   - CRUD completo de usuarios internos, restablecimiento de clave, protección contra desactivación/degradación del último `ADMIN` activo y baja lógica (`activo = 0`).
   - Padrón CRUD de Clientes Abonados y actualización de datos de titulares y vehículos asociados.
3. **Administración CRUD, Mantenimiento y Reubicación de 80 Celdas (Iteración 2):**
   - Alta, consulta multicriterio, edición estructural (zona, piso, categoría) y eliminación validada de celdas físicas.
   - Bloqueo operativo (`MANTENIMIENTO` / `INACTIVA`) con motivo técnico y bitácora en `historial_celda`.
   - **Reubicación transaccional atómica (`BEGIN IMMEDIATE`)** de vehículos estacionados ante contingencias físicas.
4. **Gestión de Pagos en Plataforma, Vigencia Consecutiva y Flujo de Caja (Iteración 3):**
   - Recaudo directo en plataforma por **Operario o Admin** (Efectivo, Código QR, Transferencia Bancaria y Consignación), sin pasarela externa.
   - Separación estricta entre `fecha_pago` (prohibición de fechas futuras) y `fecha_vencimiento` (corte consecutivo de 30 días sin pérdida de días en pagos anticipados ni corrimiento de fecha en mora).
   - Emisión de comprobantes (`REC-YYYYMMDD-XXXX`), anulación lógica auditada por `ADMIN` (sin `DELETE` físico), flujo de caja mensual, alertas de vencimiento y control de baja lógica / reactivación de servicio.
5. **Bitácora Central Inmutable de Auditoría 24/7:**
   - Trazabilidad cronológica inalterable en `auditoria_accion` de cada inicio de sesión, rechazo RBAC, operación CRUD, reubicación, movimiento de barrera y transacción financiera.

---

## 🚀 2. Ejecución Rápida (Cero Dependencias Externas)

El proyecto utiliza exclusivamente la **librería estándar de Python 3** (`http.server.ThreadingHTTPServer`, `sqlite3` en modo `WAL`, `hashlib`, `threading`, `unittest`). No requiere `pip install`.

### Iniciar el Servidor Web Concurrente
```powershell
python app.py
```
Luego abre en cualquier navegador: 👉 **[http://localhost:8000](http://localhost:8000)**

### Ejecutar las Suites de Pruebas Automatizadas (32 Casos QA)
```powershell
python -X utf8 tests_iteracion2.py
python -X utf8 tests_iteracion3_pagos.py
```
Resultado verificado: **20/20 OK** en Iteraciones 1–2 y **12/12 OK** exclusivos del módulo de Pagos (Iteración 3). *(Ambas suites restauran automáticamente `autos_colombia.db` al estado semilla limpio al finalizar).*

---

## 🔐 3. Cuentas Semilla RBAC para Pruebas y Sustentación

| Usuario (`username`) | Contraseña | Rol RBAC | Titular Asignado | Privilegios Verificables |
| :--- | :--- | :---: | :--- | :--- |
| **`admin`** | `admin123` | `ADMIN` | Camilo Alberto Palacios Turriago | Control total: CRUD Usuarios, CRUD estructural de Celdas, Mantenimiento, Reubicación, Abonados y Acceso 24/7. |
| **`adriana_op`** | `operario123` | `OPERARIO` | Adriana Andrea Agudelo Agudelo | Cabina Norte 24/7: Entrada/Salida, Novedades, Mantenimiento/Reubicación de Celdas y Padrón Abonados (`HTTP 403` en CRUD Admin). |
| **`daniel_op`** | `operario123` | `OPERARIO` | Juan Daniel Pulgarin García | Cabina Sur 24/7: Operación multi-cabina concurrente sobre SQLite WAL. |
| **`auditor`** | `auditor123` | `AUDITOR` | Auditor de Calidad y Seguridad | Supervisión estricta de Solo Lectura: bloquea con `HTTP 403` cualquier escritura. |

---

## 🔌 4. Resumen de Endpoints REST API (`app.py`)

| Método | Ruta | Permiso RBAC Requerido | Descripción |
| :---: | :--- | :--- | :--- |
| `GET` | `/api/salud` | Público / Monitoreo | Estado del servidor concurrente y motor SQLite WAL. |
| `GET` | `/api/resumen` | `CONSULTA_AUDITORIA` | KPIs de las 80 celdas, vehículos adentro y abonados. |
| `GET` | `/api/vehiculo?placa=...` | `CONSULTA_AUDITORIA` | Ficha técnica, titular y vigencia estricta por placa. |
| `GET` | `/api/celdas` | `CONSULTA_AUDITORIA` | Inventario filtrable de celdas (`estado`, `tipo`, `zona`, `q`). |
| `GET` | `/api/celdas/historial` | `CONSULTA_AUDITORIA` | Bitácora técnica de cambios y mantenimientos (`historial_celda`). |
| `GET` | `/api/usuarios` | `CONSULTA_AUDITORIA` | Listado de usuarios internos sin exponer `password_hash`. |
| `GET` | `/api/roles` | `CONSULTA_AUDITORIA` | Matriz declarativa de roles y permisos RBAC. |
| `GET` | `/api/abonados` | `CONSULTA_AUDITORIA` | Padrón completo de propietarios, vehículos y vigencias. |
| `GET` | `/api/auditoria` | `CONSULTA_AUDITORIA` | Bitácora central inmutable filtrable por `modulo`. |
| `POST` | `/api/auth/login` | Autenticación `SHA-256` | Valida credenciales, actualiza `ultimo_login` y emite sesión RBAC. |
| `POST` | `/api/usuarios` | `GESTION_USUARIOS` (`ADMIN`) | Crea nuevo usuario interno con dispersión `SHA-256`. |
| `POST` | `/api/usuarios/actualizar` | `GESTION_USUARIOS` (`ADMIN`) | Actualiza perfil, rol RBAC y estado protegiendo al último `ADMIN`. |
| `POST` | `/api/usuarios/clave` | `GESTION_USUARIOS` (`ADMIN`) | Restablece contraseña con nuevo hash `SHA-256`. |
| `POST` | `/api/usuarios/eliminar` | `GESTION_USUARIOS` (`ADMIN`) | Elimina cuenta o aplica baja lógica si posee historial de auditoría. |
| `POST` | `/api/abonado` | `GESTION_ABONADOS` | Registra nuevo cliente abonado y vehículo asociado. |
| `POST` | `/api/abonado/actualizar` | `GESTION_ABONADOS` | Actualiza contacto del titular o características del vehículo. |
| `POST` | `/api/celdas` | `CRUD_CELDAS` (`ADMIN`) | Registra nueva celda física de expansión. |
| `POST` | `/api/celdas/actualizar` | `CRUD_CELDAS` (`ADMIN`) | Edita zona, piso, categoría o estado operativo de celda. |
| `POST` | `/api/celdas/eliminar` | `CRUD_CELDAS` (`ADMIN`) | Elimina celda libre sin historial referencial. |
| `POST` | `/api/celdas/estado` | `MANTENIMIENTO_CELDAS` | Cambia estado (`DISPONIBLE` / `MANTENIMIENTO` / `INACTIVA`). |
| `POST` | `/api/celdas/reubicar` | `MANTENIMIENTO_CELDAS` | Traslado transaccional atómico (`BEGIN IMMEDIATE`) entre celdas. |
| `GET` | `/api/pagos` | `CONSULTA_AUDITORIA` | Historial de pagos, flujo de caja mensual y cartera. |
| `GET` | `/api/pagos/previsualizar` | `CONSULTA_AUDITORIA` | Simula cálculo consecutivo de vencimiento y tarifa. |
| `GET` | `/api/pagos/recibo` | `CONSULTA_AUDITORIA` | Consulta comprobante detallado por `numero_recibo`. |
| `POST` | `/api/pagos` | `GESTION_PAGOS` | Registra pago en plataforma sin pasarela externa. |
| `POST` | `/api/pagos/anular` | `ANULAR_PAGOS` (`ADMIN`) | Anulación lógica auditada revirtiendo fecha de corte. |
| `POST` | `/api/pagos/notificar` | `GESTION_PAGOS` | Emite y audita alerta de vencimiento o mora. |
| `POST` | `/api/abonado/baja` | `GESTION_PAGOS` | Baja lógica de suscripción (valida no adentro ni mora). |
| `POST` | `/api/abonado/reactivar` | `GESTION_PAGOS` | Reactiva servicio cobrando 30 días desde `fecha_pago`. |
| `POST` | `/api/ingreso` | `OPERACION_ACCESO` | Entrada 24/7 con sorteo aleatorio excluyendo celdas en mantenimiento. |
| `POST` | `/api/novedad` | `OPERACION_ACCESO` | Anexa novedad física de seguridad sobre vehículo estacionado. |
| `POST` | `/api/salida` | `OPERACION_ACCESO` | Registra salida, calcula permanencia y libera celda a `DISPONIBLE`. |

---

## 📂 5. Estructura del Repositorio

```text
aplicacion de parqueo/
├── app.py                        # Servidor HTTP multi-hilo (ThreadedHTTPServer) y 32 endpoints REST
├── models.py                     # Dominio unificado: RBAC, Usuarios, Celdas, Acceso 24/7 y Pagos
├── database.py                   # Conexión SQLite WAL concurrente, migración idempotente y semillas
├── database_schema.sql           # DDL físico 3FN (9 tablas, 9 índices, 80 celdas y hashes SHA-256 reales)
├── tests_iteracion2.py           # Suite QA automatizada de 20 casos de prueba (CP-01 a CP-20)
├── tests_iteracion3_pagos.py     # Suite QA automatizada de 12 casos de Pagos (CP-21 a CP-32)
├── autos_colombia.db             # Base de datos SQLite inicializada y limpia (80 celdas disponibles)
├── static/
│   ├── index.html                # Interfaz SPA Cobalt Bay OS (7 módulos + 12 modales no bloqueantes)
│   └── app.js                    # Estado reactivo RBAC, cliente Fetch API, pagos y flujo de caja
└── docs/                         # Documentación técnica, diagramas UML, mockups y guiones
```
