# PARQUEADERO AUTOS COLOMBIA 24/7
## MODELADO ORIENTADO A OBJETOS Y ARQUITECTURA DEL SISTEMA (STARUML)
### ITERACIÓN 1: CONTROL DE ENTRADA Y SALIDA
**Docente:** Reinaldo Rojas

---

Este documento contiene la especificación formal de la arquitectura de software y los diagramas UML solicitados para la entrega de la **Iteración 1**. Los diagramas están desarrollados en sintaxis estándar **PlantUML**, compatible directamente con herramientas de modelado como **StarUML**, Visual Paradigm, y editores PlantUML/Mermaid.

---

## 1. ARQUITECTURA DEL SISTEMA (ARQUITECTURA EN CAPAS)

El sistema adopta una arquitectura desacoplada en tres capas principales (**3-Tier Layered Architecture**):

1. **Capa de Presentación (Frontend SPA / UI):**
   - Interfaz web responsiva basada en el sistema de diseño industrial *Cobalt Bay OS*.
   - Consumo asíncrono de API REST vía Fetch API (`app.js`, `index.html`).
   - Gestión reactiva del mapa de 80 celdas y reloj operativo 24/7.
2. **Capa de Lógica de Negocio y Controladores (Backend / Application Layer):**
   - Servidor HTTP y API REST (`app.py`).
   - Servicios del dominio (`models.py`): Reglas de negocio de mensualidades, cálculo de tiempos, control de aforo y algoritmo de asignación aleatoria/dinámica de celdas.
3. **Capa de Datos y Persistencia (Data Layer):**
   - Motor relacional SQLite (`autos_colombia.db`).
   - Módulo de conexión y transacciones (`database.py`).
   - Esquema físico con claves foráneas e integridad referencial (`database_schema.sql`).

```
+-------------------------------------------------------------+
|               CAPA DE PRESENTACIÓN (UI / FRONTEND)          |
|  - index.html (Tailwind CSS, Plus Jakarta Sans, JetBrains)  |
|  - app.js (Controlador de eventos, Mapa reactivo de celdas) |
+-------------------------------------------------------------+
                              |  (HTTP REST / JSON)
                              v
+-------------------------------------------------------------+
|             CAPA DE NEGOCIO Y API (BACKEND PYTHON)          |
|  - AutosColombiaHandler (app.py): Enrutador REST API        |
|  - ParqueaderoService (models.py): Lógica de Dominio        |
|    * Validador de Mensualidad y Restricción de Mora         |
|    * Algoritmo de Asignación Aleatoria de Celdas            |
|    * Gestor de Aforo (70 Carros / 10 Motos)                 |
|    * Controlador de Apertura/Cierre de Barrera              |
+-------------------------------------------------------------+
                              |  (SQL Queries / Transacciones)
                              v
+-------------------------------------------------------------+
|               CAPA DE PERSISTENCIA (BASE DE DATOS)          |
|  - database.py: Pool de conexiones y DDL Inicializador      |
|  - autos_colombia.db (SQLite3 Relacional)                   |
|    [propietario] 1--* [vehiculo] 1--* [mensualidad]         |
|    [celda] 1--* [registro_acceso] *--1 [vehiculo]           |
+-------------------------------------------------------------+
```

---

## 2. DIAGRAMA DE PAQUETES (PACKAGE DIAGRAM)

Representa la organización modular del código fuente:

```plantuml
@startuml Diagrama_Paquetes_AutosColombia
skinparam packageStyle rectangle

package "Capa Presentación" {
    [index.html]
    [app.js]
    [style.css]
}

package "Capa de Controladores y API" {
    [app.py\n(AutosColombiaHandler)] as AppServer
}

package "Capa de Dominio y Negocio" {
    [models.py\n(Logica de Control de Acceso)] as Models
    package "Entidades del Dominio" {
        [Vehiculo]
        [Celda]
        [Mensualidad]
        [Propietario]
        [RegistroAcceso]
    }
}

package "Capa de Persistencia" {
    [database.py\n(ConnectionManager)] as DBManager
    database "autos_colombia.db\n(SQLite Relacional)" as DB
}

[app.js] ..> AppServer : HTTP REST JSON
AppServer ..> Models : Invoca servicios
Models ..> [Vehiculo] : Instancia
Models ..> [Celda] : Asigna dinamicamente
Models ..> [Mensualidad] : Valida vigencia
Models ..> DBManager : Solicita conexion
DBManager ..> DB : Ejecuta SQL (PRAGMA FK=ON)
@enduml
```

---

## 3. DIAGRAMA DE CASOS DE USO (USE CASE DIAGRAM)

Actores involucrados:
- **Operador de Cabina (Actor Principal):** Personal en turno 24/7 encargado de ingresar placas y operar las barreras.
- **Sensor / Cámara LPR (Actor Secundario):** Dispositivo de lectura óptica de placa vehicular.
- **Reloj de Sistema 24/7 (Actor de Sistema):** Provee el timestamp exacto.

```plantuml
@startuml Diagrama_Casos_Uso_AutosColombia
left to right direction
skinparam packageStyle rectangle

actor "Operador de Cabina" as Operador
actor "Cámara / Sensor LPR" as LPR
actor "Reloj del Sistema 24/7" as Reloj

rectangle "Sistema de Control de Acceso Autos Colombia (Iteración 1)" {
    usecase "CU-01: Consultar Vehículo por Placa" as CU01
    usecase "CU-02: Validar Vigencia de Mensualidad" as CU02
    usecase "CU-03: Verificar Aforo por Tipo de Vehículo" as CU03
    usecase "CU-04: Registrar Entrada y Asignar Celda Aleatoria" as CU04
    usecase "CU-05: Abrir Barrera de Entrada" as CU05
    usecase "CU-06: Denegar Acceso por Mora / Sobrecupo" as CU06
    usecase "CU-07: Registrar Salida de Vehículo" as CU07
    usecase "CU-08: Liberar Celda de Parqueo" as CU08
    usecase "CU-09: Visualizar Mapa de 80 Celdas en Vivo" as CU09
    usecase "CU-10: Auditar Historial de Movimientos" as CU10
}

Operador --> CU01
LPR --> CU01
Operador --> CU04
Operador --> CU07
Operador --> CU09
Operador --> CU10

CU01 ..> CU02 : <<include>>
CU04 ..> CU02 : <<include>>
CU04 ..> CU03 : <<include>>
CU04 ..> CU05 : <<include>>
CU02 ..> CU06 : <<extend>> (si esta vencida)
CU03 ..> CU06 : <<extend>> (si aforo lleno)

CU07 ..> CU08 : <<include>>
CU04 ..> Reloj : <<include>> (estampa hora)
CU07 ..> Reloj : <<include>> (calcula duracion)
@enduml
```

---

## 4. DIAGRAMA DE CLASES (CLASS DIAGRAM)

Modela las clases del dominio, atributos con tipos de datos, visibilidad y relaciones con multiplicidad:

```plantuml
@startuml Diagrama_Clases_AutosColombia
skinparam classAttributeIconSize true

enum TipoVehiculo {
    CARRO
    MOTO
}

enum EstadoCelda {
    DISPONIBLE
    OCUPADA
    MANTENIMIENTO
}

enum EstadoMensualidad {
    ACTIVA
    VENCIDA
    CANCELADA
}

enum EstadoAcceso {
    ADENTRO
    FINALIZADO
}

class Propietario {
    - id: Integer
    - documento: String
    - nombreCompleto: String
    - telefono: String
    - email: String
    - fechaRegistro: DateTime
    + getVehiculos(): List<Vehiculo>
}

class Vehiculo {
    - placa: String
    - tipoVehiculo: TipoVehiculo
    - marca: String
    - modelo: String
    - color: String
    - activo: Boolean
    + tieneMensualidadVigente(): Boolean
    + estaDentro(): Boolean
}

class Mensualidad {
    - id: Integer
    - fechaPago: Date
    - fechaVencimiento: Date
    - valorPagado: Decimal
    - estado: EstadoMensualidad
    + estaVigente(fechaActual: Date): Boolean
    + diasRestantes(): Integer
}

class Celda {
    - codigo: String
    - tipoPermitido: TipoVehiculo
    - estado: EstadoCelda
    - piso: Integer
    - zona: String
    + ocupar(): void
    + liberar(): void
    + estaDisponible(): Boolean
}

class RegistroAcceso {
    - id: Integer
    - fechaIngreso: DateTime
    - fechaSalida: DateTime
    - estado: EstadoAcceso
    - observaciones: String
    + registrarSalida(fecha: DateTime): Duration
}

class ParqueaderoService {
    + {static} CAPACIDAD_CARROS: int = 70
    + {static} CAPACIDAD_MOTOS: int = 10
    + {static} TARIFA_CARRO: Decimal = 250000.00
    + {static} TARIFA_MOTO: Decimal = 100000.00
    + consultarVehiculo(placa: String): VehiculoDTO
    + registrarIngreso(placa: String): ResultadoIngresoDTO
    + registrarSalida(placa: String): ResultadoSalidaDTO
    + asignarCeldaAleatoria(tipo: TipoVehiculo): Celda
    + obtenerEstado80Celdas(): ResumenDTO
}

' Relaciones y Multiplicidades
Propietario "1" o-- "1..*" Vehiculo : posee
Vehiculo "1" *-- "1..*" Mensualidad : tiene
Vehiculo "1" -- "0..*" RegistroAcceso : registra
Celda "1" -- "0..*" RegistroAcceso : aloja
ParqueaderoService ..> Vehiculo : gestiona
ParqueaderoService ..> Celda : asigna
ParqueaderoService ..> RegistroAcceso : crea/actualiza
@enduml
```

---

## 5. DIAGRAMAS DE SECUENCIA (SEQUENCE DIAGRAMS)

### 5.1 Secuencia de Entrada (Ingreso con Validación y Asignación Aleatoria)

```plantuml
@startuml Secuencia_Ingreso_Vehiculo
autonumber
actor "Operador de Cabina" as Op
participant "Interfaz Web (UI)" as UI
participant "Controlador REST (app.py)" as API
participant "Servicio Dominio (models.py)" as Service
database "Base de Datos SQLite" as DB
entity "Barrera de Entrada" as Barrera

Op -> UI : Ingresa placa "ABC-123" y pulsa "Abrir Barrera"
UI -> API : POST /api/ingreso { placa: "ABC-123" }
API -> Service : registrar_ingreso("ABC-123")
Service -> DB : SELECT * FROM vehiculo WHERE placa = 'ABC123'
DB --> Service : Retorna datos (Renault Duster, Carro)

Service -> DB : SELECT * FROM mensualidad WHERE placa = 'ABC123' ORDER BY fecha DESC
DB --> Service : Retorna mensualidad (Vigente, vence en +20 dias)

Service -> DB : SELECT * FROM celda WHERE tipo_permitido = 'CARRO' AND estado = 'DISPONIBLE'
DB --> Service : Retorna lista de celdas libres (ej: C-04, C-19, C-24, C-50...)

alt Hay celdas libres y Mensualidad Vigente
    Service -> Service : random.choice(celdas_libres) -> Celda "C-24"
    Service -> DB : UPDATE celda SET estado = 'OCUPADA' WHERE codigo = 'C-24'
    Service -> DB : INSERT INTO registro_acceso (placa, celda, fecha_ingreso, estado='ADENTRO')
    DB --> Service : Confirmación OK
    Service --> API : JSON { success: true, celda: "C-24", placa: "ABC-123" }
    API --> UI : HTTP 200 OK
    UI -> Barrera : Abre Barrera Física / Animación Verde
    UI --> Op : Mensaje de Éxito: "Celda C-24 Asignada Aleatoriamente"
else Mensualidad Vencida
    Service --> API : JSON { success: false, error: "MENSUALIDAD_VENCIDA" }
    API --> UI : HTTP 400 Bad Request
    UI --> Op : Alerta Roja: "Acceso Denegado por Mensualidad Vencida"
else Aforo Lleno
    Service --> API : JSON { success: false, error: "SIN_CUPO" }
    API --> UI : HTTP 400 Bad Request
    UI --> Op : Alerta Amarilla: "Capacidad Máxima Alcanzada"
end
@enduml
```

### 5.2 Secuencia de Salida (Egreso y Liberación Automática de Celda)

```plantuml
@startuml Secuencia_Salida_Vehiculo
autonumber
actor "Operador de Cabina" as Op
participant "Interfaz Web (UI)" as UI
participant "Controlador REST (app.py)" as API
participant "Servicio Dominio (models.py)" as Service
database "Base de Datos SQLite" as DB

Op -> UI : Clic en "Dar Salida" sobre el vehículo "ABC-123"
UI -> API : POST /api/salida { placa: "ABC-123" }
API -> Service : registrar_salida("ABC-123")
Service -> DB : SELECT * FROM registro_acceso WHERE placa = 'ABC123' AND estado = 'ADENTRO'
DB --> Service : Retorna registro activo (Celda C-24, Ingreso: 14:30)

Service -> Service : Calcular duracion (ahora - fecha_ingreso)
Service -> DB : UPDATE registro_acceso SET fecha_salida = NOW(), estado = 'FINALIZADO'
Service -> DB : UPDATE celda SET estado = 'DISPONIBLE' WHERE codigo = 'C-24'
DB --> Service : Commit exitoso

Service --> API : JSON { success: true, celda_liberada: "C-24", duracion: "1h 45m" }
API --> UI : HTTP 200 OK
UI --> Op : Notificación: "Salida registrada. Celda C-24 liberada sin cobro de dinero."
UI -> UI : Actualiza contadores y mapa de 80 celdas
@enduml
```

---

## 6. DIAGRAMA DE ARQUITECTURA DE COMPONENTES E INTERFACES DE COMUNICACIÓN

Representa los componentes de software ejecutables y las interfaces provistas/requeridas mediante las cuales se comunican (incluyendo soporte multi-operario concurrente):

```plantuml
@startuml Arquitectura_Componentes_Interfaces
skinparam componentStyle uml2

node "Cliente Web (Terminales Operarios 24/7)" {
    component "UI Cabina de Control\n(index.html + app.js)" as WebUI
    component "Monitor Mapa 80 Celdas\n(Sincronización Real-Time)" as MapUI
}

interface "IHttpRestApi\n(GET/POST JSON)" as IRest

node "Servidor de Aplicación Concurrente (Python 3)" {
    component "Controlador HTTP Multi-Hilo\n(app.py / ThreadedHTTPServer)" as HttpController
    interface "IServicioParqueadero" as IService
    component "Motor Reglas de Negocio\n(models.py)" as BusinessEngine
    interface "IConexionDatos\n(Transacción Atómica)" as IDB
    component "Gestor de Persistencia\n(database.py + Lock)" as DataAccess
}

database "Motor Relacional SQLite\n(autos_colombia.db - Modo WAL)" as SQLite {
    frame "Tablas Normalizadas (3FN)" as Tablas
}

WebUI --( IRest : Consume API
MapUI --( IRest : Polling 24/7
IRest - HttpController : Expone

HttpController --( IService : Invoca
IService - BusinessEngine : Implementa

BusinessEngine --( IDB : BEGIN IMMEDIATE
IDB - DataAccess : Provee

DataAccess --> Tablas : SQL + PRAGMA FK=ON
@enduml
```

---

## 7. DIAGRAMA ENTIDAD-RELACIÓN Y MODELO RELACIONAL (BASE DE DATOS)

```plantuml
@startuml Diagrama_MER_AutosColombia
hide circle
skinparam linetype ortho

entity "PROPIETARIO" as prop {
    * **id** : INTEGER <<PK>>
    --
    * documento : VARCHAR(20) <<UNIQUE>>
    * nombre_completo : VARCHAR(120)
    * telefono : VARCHAR(20)
    email : VARCHAR(100)
    fecha_registro : DATETIME
}

entity "VEHICULO" as veh {
    * **placa** : VARCHAR(10) <<PK>>
    --
    * tipo_vehiculo : VARCHAR(10) <<CARRO|MOTO>>
    * marca : VARCHAR(50)
    * modelo : VARCHAR(50)
    * color : VARCHAR(30)
    * propietario_id : INTEGER <<FK>>
    * activo : BOOLEAN
    fecha_creacion : DATETIME
}

entity "MENSUALIDAD" as mens {
    * **id** : INTEGER <<PK>>
    --
    * vehiculo_placa : VARCHAR(10) <<FK>>
    * fecha_pago : DATE
    * fecha_vencimiento : DATE
    * valor_pagado : DECIMAL(10,2)
    * estado : VARCHAR(15) <<ACTIVA|VENCIDA>>
}

entity "CELDA" as celda {
    * **codigo** : VARCHAR(10) <<PK>>
    --
    * tipo_permitido : VARCHAR(10) <<CARRO|MOTO>>
    * estado : VARCHAR(15) <<DISPONIBLE|OCUPADA>>
    * piso : INTEGER
    zona : VARCHAR(20)
}

entity "REGISTRO_ACCESO" as reg {
    * **id** : INTEGER <<PK>>
    --
    * vehiculo_placa : VARCHAR(10) <<FK>>
    * celda_codigo : VARCHAR(10) <<FK>>
    * fecha_ingreso : DATETIME
    fecha_salida : DATETIME
    * estado : VARCHAR(15) <<ADENTRO|FINALIZADO>>
    observaciones : TEXT
}

prop ||--|{ veh : "posee (1:N)"
veh ||--|{ mens : "paga mensualidad (1:N)"
veh ||--o{ reg : "registra ingreso/salida (1:N)"
celda ||--o{ reg : "asigna dinámicamente (1:N)"
@enduml
```

---

## 8. INSTRUCCIONES DE APERTURA EN STARUML

1. Abrir **StarUML**.
2. Seleccionar `File -> Open...` y elegir el archivo nativo **`docs/Autos_Colombia_StarUML.mdj`** incluido en esta carpeta.
3. También dispone de todos los diagramas exportados en alta resolución en `docs/diagramas/` (formatos `.png` y `.svg`) y el código fuente `.puml` en `docs/staruml_diagrams.puml`.
