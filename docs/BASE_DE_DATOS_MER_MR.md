# PARQUEADERO AUTOS COLOMBIA 24/7
## DISEÑO DE BASE DE DATOS: MER, MODELO RELACIONAL Y DICCIONARIO
### ITERACIÓN 1: CONTROL DE ENTRADA Y SALIDA
**Docente:** Reinaldo Rojas

---

## 1. MODELO ENTIDAD-RELACIÓN (MER CONCEPTUAL)

El diseño conceptual refleja las entidades necesarias para gobernar las reglas de negocio de la Iteración 1:

```
    +---------------+               +---------------+
    |  PROPIETARIO  | 1           * |   VEHICULO    |
    |---------------|---------------|---------------|
    | id (PK)       |    posee      | placa (PK)    |
    | documento     |               | tipo_vehiculo |
    | nombre        |               | marca, modelo |
    +---------------+               | color         |
                                    +---------------+
                                      1 |         1 |
                                        |         |
                                  tiene |         | registra
                                      * |         | *
                        +---------------+         |
                        |  MENSUALIDAD  |         |
                        |---------------|         |
                        | id (PK)       |         |
                        | fecha_pago    |         |
                        | fecha_venc    |         |
                        | valor_pagado  |         |
                        | estado        |         |
                        +---------------+         |
                                                  v
    +---------------+               +-------------------+
    |     CELDA     | 1           * |  REGISTRO_ACCESO  |
    |---------------|---------------|-------------------|
    | codigo (PK)   |    aloja      | id (PK)           |
    | tipo_permitido|               | vehiculo_placa(FK)|
    | estado        |               | celda_codigo (FK) |
    | piso, zona    |               | fecha_ingreso     |
    +---------------+               | fecha_salida      |
                                    | estado            |
                                    +-------------------+
```

### Cardinalidades y Justificación de Negocio:
* **Propietario (1) a Vehículo (\*):** Un cliente abonado puede tener uno o varios vehículos registrados a su nombre, pero un vehículo pertenece a un único titular.
* **Vehículo (1) a Mensualidad (\*):** El cobro se realiza estrictamente **por vehículo** (\$250.000 carro, \$100.000 moto). Un vehículo acumula un historial de pagos mensuales a lo largo del tiempo.
* **Vehículo (1) a RegistroAcceso (\*):** Un vehículo puede tener múltiples ingresos y salidas 24/7 a través de las barreras.
* **Celda (1) a RegistroAcceso (\*):** Una celda puede haber albergado múltiples vehículos en distintos momentos históricos, pero en un instante dado solo puede estar ocupada por un vehículo si su estado es `OCUPADA`. La asignación es **dinámica y aleatoria** entre las celdas disponibles.

---

## 2. MODELO RELACIONAL (MR LÓGICO)

Esquema relacional formal normalizado en Tercera Forma Normal (3FN):

1. **PROPIETARIO** (
   <u>id</u> INT [PK], 
   documento VARCHAR(20) [UNIQUE, NOT NULL], 
   nombre_completo VARCHAR(120) [NOT NULL], 
   telefono VARCHAR(20) [NOT NULL], 
   email VARCHAR(100), 
   fecha_registro DATETIME
)

2. **VEHICULO** (
   <u>placa</u> VARCHAR(10) [PK], 
   tipo_vehiculo VARCHAR(10) [CHECK IN ('CARRO', 'MOTO'), NOT NULL], 
   marca VARCHAR(50) [NOT NULL], 
   modelo VARCHAR(50) [NOT NULL], 
   color VARCHAR(30) [NOT NULL], 
   propietario_id INT [FK -> PROPIETARIO(id), NOT NULL], 
   activo BOOLEAN [DEFAULT 1], 
   fecha_creacion DATETIME
)

3. **MENSUALIDAD** (
   <u>id</u> INT [PK], 
   vehiculo_placa VARCHAR(10) [FK -> VEHICULO(placa), NOT NULL], 
   fecha_pago DATE [NOT NULL], 
   fecha_vencimiento DATE [NOT NULL], 
   valor_pagado DECIMAL(10,2) [NOT NULL], 
   estado VARCHAR(15) [CHECK IN ('ACTIVA', 'VENCIDA', 'CANCELADA'), NOT NULL]
)

4. **CELDA** (
   <u>codigo</u> VARCHAR(10) [PK], 
   tipo_permitido VARCHAR(10) [CHECK IN ('CARRO', 'MOTO'), NOT NULL], 
   estado VARCHAR(15) [CHECK IN ('DISPONIBLE', 'OCUPADA', 'MANTENIMIENTO'), DEFAULT 'DISPONIBLE', NOT NULL], 
   piso INT [DEFAULT 1], 
   zona VARCHAR(20)
)

5. **REGISTRO_ACCESO** (
   <u>id</u> INT [PK], 
   vehiculo_placa VARCHAR(10) [FK -> VEHICULO(placa), NOT NULL], 
   celda_codigo VARCHAR(10) [FK -> CELDA(codigo), NOT NULL], 
   fecha_ingreso DATETIME [NOT NULL], 
   fecha_salida DATETIME [NULLABLE], 
   estado VARCHAR(15) [CHECK IN ('ADENTRO', 'FINALIZADO'), DEFAULT 'ADENTRO', NOT NULL], 
   observaciones TEXT
)

---

## 3. DICCIONARIO DE DATOS EXHAUSTIVO

### 3.1 Tabla: `propietario`
Almacena la información de los clientes abonados titulares de contratos de parqueo.

| Campo | Tipo | Nulo | Clave | Descripción / Restricción |
|---|---|---|---|---|
| `id` | INTEGER | NO | PK (AI) | Identificador secuencial único del propietario |
| `documento` | VARCHAR(20) | NO | UNIQUE | Cédula de ciudadanía o NIT |
| `nombre_completo` | VARCHAR(120) | NO | - | Nombres y apellidos completos |
| `telefono` | VARCHAR(20) | NO | - | Teléfono celular de contacto para emergencias y avisos |
| `email` | VARCHAR(100) | SI | - | Correo electrónico para facturas y recordatorios |
| `fecha_registro` | DATETIME | NO | - | Fecha de suscripción en el parqueadero |

### 3.2 Tabla: `vehiculo`
Almacena el registro técnico de los automotores autorizados para ingresar.

| Campo | Tipo | Nulo | Clave | Descripción / Restricción |
|---|---|---|---|---|
| `placa` | VARCHAR(10) | NO | PK | Placa alfanumérica sin espacios (ej: ABC123) |
| `tipo_vehiculo` | VARCHAR(10) | NO | - | CHECK `IN ('CARRO', 'MOTO')` |
| `marca` | VARCHAR(50) | NO | - | Marca del automotor (ej: Renault, Toyota, Yamaha) |
| `modelo` | VARCHAR(50) | NO | - | Línea / modelo comercial (ej: Duster 2.0, NMAX 155) |
| `color` | VARCHAR(30) | NO | - | Color para verificación visual en cabina de control |
| `propietario_id` | INTEGER | NO | FK | Clave foránea referenciando a `propietario(id)` |
| `activo` | BOOLEAN | NO | - | 1: Activo en sistema, 0: Retirado |
| `fecha_creacion` | DATETIME | NO | - | Estampilla de tiempo de registro |

### 3.3 Tabla: `mensualidad`
Gobierna la regla de cobro por vehículo y vigencia de servicio.

| Campo | Tipo | Nulo | Clave | Descripción / Restricción |
|---|---|---|---|---|
| `id` | INTEGER | NO | PK (AI) | Identificador único del recibo de mensualidad |
| `vehiculo_placa` | VARCHAR(10) | NO | FK | Referencia a `vehiculo(placa)` |
| `fecha_pago` | DATE | NO | - | Fecha en que se efectuó el pago |
| `fecha_vencimiento`| DATE | NO | - | Fecha de corte (exactamente 1 mes desde el pago) |
| `valor_pagado` | DECIMAL(10,2) | NO | - | \$250.000 para Carro o \$100.000 para Moto |
| `estado` | VARCHAR(15) | NO | - | CHECK `IN ('ACTIVA', 'VENCIDA', 'CANCELADA')` |

### 3.4 Tabla: `celda`
Representa físicamente las **80 celdas reglamentarias** de la sede.

| Campo | Tipo | Nulo | Clave | Descripción / Restricción |
|---|---|---|---|---|
| `codigo` | VARCHAR(10) | NO | PK | Nomenclatura oficial: `M-01` a `M-10` y `C-01` a `C-70` |
| `tipo_permitido` | VARCHAR(10) | NO | - | CHECK `IN ('CARRO', 'MOTO')` |
| `estado` | VARCHAR(15) | NO | - | CHECK `IN ('DISPONIBLE', 'OCUPADA', 'MANTENIMIENTO')` |
| `piso` | INTEGER | NO | - | Nivel de estacionamiento (1 o 2) |
| `zona` | VARCHAR(20) | SI | - | Sector físico (Zona Motos, Zona A, Zona B, etc.) |

### 3.5 Tabla: `registro_acceso`
Registra los movimientos 24/7 de entrada y salida con sus estampillas temporales.

| Campo | Tipo | Nulo | Clave | Descripción / Restricción |
|---|---|---|---|---|
| `id` | INTEGER | NO | PK (AI) | Consecutivo de movimiento de acceso |
| `vehiculo_placa` | VARCHAR(10) | NO | FK | Referencia a `vehiculo(placa)` |
| `celda_codigo` | VARCHAR(10) | NO | FK | Celda sorteada y asignada (`celda(codigo)`) |
| `fecha_ingreso` | DATETIME | NO | - | Timestamp exacto de ingreso |
| `fecha_salida` | DATETIME | SI | - | Timestamp exacto de egreso (NULL mientras esté adentro) |
| `estado` | VARCHAR(15) | NO | - | CHECK `IN ('ADENTRO', 'FINALIZADO')` |
| `observaciones` | TEXT | SI | - | Novedades registradas por el operador |

---

## 4. MODELO FÍSICO SQL

El código SQL DDL y DML ejecutable se encuentra implementado en el archivo:
📁 **`database_schema.sql`**

Dicho script:
1. Crea las 5 tablas relacionales con sus restricciones de dominio, checks y claves foráneas.
2. Crea índices de optimización para búsquedas rápidas por placa y celda.
3. Inserta obligatoriamente las **80 celdas fijas**:
   - 10 celdas de Motos (`M-01` a `M-10`).
   - 70 celdas de Carros (`C-01` a `C-70`).
4. Inserta automotores y mensualidades de prueba (vigentes y vencidas) para la demostración docente.
