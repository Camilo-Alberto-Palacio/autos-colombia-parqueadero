# PARQUEADERO AUTOS COLOMBIA 24/7
## DOCUMENTO DE ESPECIFICACIÓN DE REQUERIMIENTOS Y DISEÑO TÉCNICO
### ITERACIÓN 1: MÓDULO EXCLUSIVO DE CONTROL DE ENTRADA Y SALIDA

---

**Asignatura:** Desarrollo de Software / Ingeniería de Software  
**Docente:** Reinaldo Rojas  
**Proyecto:** Sistema de Gestión y Control de Parqueadero "Autos Colombia 24/7"  
**Versión del Documento:** 1.0 (Iteración 1)  
**Fecha:** Octubre de 2026  

---

## 1. INTRODUCCIÓN Y CONTEXTO DEL PROYECTO

El presente documento técnico formaliza el análisis, diseño e implementación de la primera fase del sistema de información para el parqueadero **Autos Colombia 24/7**. El parqueadero opera en una modalidad especializada orientada a clientes corporativos y recurrentes bajo suscripción mensual, funcionando ininterrumpidamente las 24 horas del día, los 7 días de la semana.

El propósito fundamental de esta primera iteración es dotar a la cabina de control de una herramienta ágil, confiable y automatizada para gestionar el flujo vehicular de ingreso y egreso, validando en tiempo real la vigencia de los derechos de permanencia (mensualidades), garantizando el cumplimiento estricto del aforo físico de la sede y asignando dinámicamente los espacios de parqueo disponibles.

---

## 2. ALCANCE DE LA PRIMERA ENTREGA (ITERACIÓN 1)

### 2.1 Módulos Incluidos
* **Módulo de Entrada:** 
  - Lectura y validación de placa vehicular.
  - Verificación del estado de vigencia de la mensualidad del vehículo.
  - Validación de existencia de celdas libres acordes al tipo de vehículo.
  - Asignación dinámica y aleatoria de la celda de parqueo.
  - Apertura lógica de barrera y registro de estampilla de tiempo (*timestamp* de ingreso).
* **Módulo de Salida:**
  - Identificación del vehículo que egresa de las instalaciones.
  - Registro de estampilla de tiempo (*timestamp* de egreso) y cálculo de permanencia.
  - Liberación inmediata e incondicional de la celda ocupada hacia el *pool* de celdas disponibles.
* **Control de Capacidad Física (Aforo 80 Celdas):**
  - Monitoreo en tiempo real de 70 celdas para automóviles/camionetas y 10 celdas para motocicletas.
  - Prevención automática de sobrecupo.

### 2.2 Exclusiones Explícitas para la Iteración 1
* **Gestión Completa de Usuarios y Roles:** No se implementa módulo de creación/edición de cuentas administrativas, perfiles RBAC ni gestión de personal (postergado para Iteración 2).
* **Pasarela y Recaudo de Pagos:** No se incluyen cobros en sitio, arqueo de caja, facturación electrónica ni procesamiento de tarjetas (postergado para Iteración 3). Los vehículos cuentan con mensualidades pre-cargadas en el modelo relacional para validar su estado de vigencia.

---

## 3. REGLAS DE NEGOCIO (BUSINESS RULES)

* **RN-01 (Modalidad Exclusiva por Mensualidad):** El establecimiento opera única y exclusivamente mediante suscripciones mensuales. No se admite cobro por fracción, hora o día.
* **RN-02 (Aforo y Distribución de Celdas):** La sede dispone exactamente de **80 celdas de parqueo**, segmentadas en:
  - 10 celdas para motocicletas: Nomenclatura oficial `M-01` a `M-10`.
  - 70 celdas para vehículos/carros: Nomenclatura oficial `C-01` a `C-70`.
* **RN-03 (Asignación Dinámica / Aleatoria):** No existen puestos fijos asignados contractualmente por usuario. Al autorizar la entrada, el software sortea aleatoriamente una de las celdas disponibles para su categoría vehicular.
* **RN-04 (Cobro y Tarifa por Vehículo):** El pago de la mensualidad se aplica a la placa vehicular, independientemente de que un mismo titular posea varios automotores.
  - Tarifa Carro: **\$250.000 COP** mensuales.
  - Tarifa Moto: **\$100.000 COP** mensuales.
* **RN-05 (Vigencia Exacta de Mensualidad):** La cobertura abarca exactamente un mes calendario a partir del día del pago. Si `fecha_vencimiento < fecha_actual`, el sistema deniega el acceso automáticamente bajo alerta de mora.
* **RN-06 (Control de Duplicidad en Sitio):** Un vehículo que figure con estado `ADENTRO` en el registro de acceso tiene prohibido un nuevo ingreso hasta tanto no se registre su salida.
* **RN-07 (Trazabilidad y Seguridad):** El sistema debe consultar y desplegar la información completa de identificación vehicular: Placa, Tipo (Carro/Moto), Marca, Modelo, Color y Propietario.
* **RN-08 (Operación 24/7):** La cabina opera de forma continua con actualización en vivo de reloj y estados de barrera.

---

## 4. REQUERIMIENTOS FUNCIONALES (RF)

| ID | Nombre | Descripción | Criterio de Éxito |
|---|---|---|---|
| **RF-01** | Búsqueda y Validación de Placa | El operador ingresa la placa o el sistema la lee; se normaliza a mayúsculas y formato estándar. | Recupera ficha técnica y estado de mensualidad en < 500 ms. |
| **RF-02** | Validación de Suscripción Vigente | Verifica si la mensualidad asociada a la placa está activa y con fecha de expiración mayor o igual a la actual. | Si está vigente habilita botón de apertura; si está vencida deniega el paso. |
| **RF-03** | Verificación de Aforo Disponible | Comprueba que la cantidad de celdas libres para el tipo de vehículo sea mayor a cero. | Si cupo = 0, genera alerta de aforo lleno y bloquea el ingreso. |
| **RF-04** | Asignación Aleatoria de Celda | Entre las celdas disponibles del tipo correspondiente, el sistema elige una al azar. | La celda elegida pasa a estado `OCUPADA` de inmediato. |
| **RF-05** | Registro de Ingreso | Almacena fecha, hora, placa, celda asignada y estado `ADENTRO`. | Genera un nuevo registro de acceso con ID único. |
| **RF-06** | Consulta de Vehículos Adentro | Presenta una lista en vivo de todos los vehículos actualmente estacionados. | Muestra placa, modelo, celda ocupada, conductor y tiempo transcurrido. |
| **RF-07** | Búsqueda Rápida en Salida | Permite filtrar los vehículos adentro por placa, modelo o número de celda. | Filtro instantáneo sin recargar la página. |
| **RF-08** | Registro de Egreso | Al hacer clic en "Dar Salida" o buscar la placa, se registra fecha y hora de salida. | El estado pasa a `FINALIZADO` y se calcula tiempo de estancia. |
| **RF-09** | Liberación Automática de Celda | Al registrar la salida, la celda ocupada pasa a estado `DISPONIBLE`. | La celda se reintegra al pool de disponibles para asignaciones aleatorias. |
| **RF-10** | Semáforo de Capacidad en Vivo | Despliega contadores visuales de carros libres (sobre 70) y motos libres (sobre 10). | Sincronización en tiempo real tras cada movimiento. |
| **RF-11** | Mapa Interactivo de las 80 Celdas | Matriz visual de 80 bloques interactivos con código de color (verde: libre, rojo: ocupado). | Permite hacer clic en cualquier celda para inspeccionar placa y conductor. |
| **RF-12** | Registro Rápido de Vehículos de Prueba | Modal utilitario para agregar vehículos de prueba (con mensualidad activa o vencida) para demostración docente. | Inserta datos en la base de datos SQLite y permite probar inmediatamente. |

---

## 5. REQUERIMIENTOS NO FUNCIONALES (RNF)

* **RNF-01 (Rendimiento):** Las respuestas a transacciones de entrada, salida y consulta deben ejecutarse en menos de 200 milisegundos.
* **RNF-02 (Disponibilidad y Concurrencia):** Operación 24/7 sin bloqueos de base de datos gracias a SQLite configurado en modo transaccional seguro y claves foráneas activas.
* **RNF-03 (Usabilidad e Interfaz):** Interfaz basada en el sistema de diseño industrial *Cobalt Bay OS*, con tipografías `JetBrains Mono` para placas legibles a distancia y botones táctiles de alto contraste.
* **RNF-04 (Portabilidad y Cero Dependencias):** El backend funciona en cualquier máquina con Python 3 estándar sin obligar a la instalación de frameworks pesados de terceros.
* **RNF-05 (Integridad Referencial):** Integridad forzada por base de datos relacional (claves primarias y foráneas con restricciones de eliminación).
* **RNF-06 (Seguridad en Cabina):** Identificación visual del vehículo (color, marca y modelo) para que el operador corrobore físicamente que el automotor corresponde a la placa registrada.

---

## 6. HISTORIAS DE USUARIO (USER STORIES)

### HU-01: Control de Entrada con Mensualidad Vigente
* **Como:** Operador de cabina del parqueadero.
* **Quiero:** Digitar la placa de un vehículo para validar su mensualidad y abrirle la barrera.
* **Para:** Garantizar que solo ingresen automotores autorizados y asignarle su celda correspondiente.
* **Criterios de Aceptación (Gherkin):**
  - **Dado** que un vehículo con placa `ABC-123` tiene una mensualidad activa y existen celdas disponibles para Carro.
  - **Cuando** el operador consulta la placa y presiona "Abrir Barrera de Entrada".
  - **Entonces** el sistema sortea aleatoriamente una celda libre (ej: `C-24`), cambia su estado a `OCUPADA`, guarda el registro con fecha y hora actual, y muestra en pantalla la celda asignada.

### HU-02: Bloqueo de Entrada por Mensualidad Vencida
* **Como:** Operador de cabina del parqueadero.
* **Quiero:** Que el sistema me alerte si la mensualidad de un vehículo expiró.
* **Para:** Impedir el paso de usuarios morosos conforme a la política del parqueadero.
* **Criterios de Aceptación (Gherkin):**
  - **Dado** que un vehículo con placa `XYZ-999` tiene mensualidad con fecha de vencimiento en el pasado.
  - **Cuando** se ingresa la placa en el módulo de entrada.
  - **Entonces** el sistema muestra una tarjeta en rojo "MENSUALIDAD VENCIDA - ACCESO DENEGADO", deshabilita el botón de apertura y bloquea el ingreso.

### HU-03: Control de Capacidad Máxima (Aforo Lleno)
* **Como:** Administrador del parqueadero.
* **Quiero:** Que el sistema no permita el ingreso de más de 70 carros o más de 10 motos.
* **Para:** Evitar hacinamiento vehicular y respetar los 80 cupos físicos de la sede.
* **Criterios de Aceptación (Gherkin):**
  - **Dado** que las 10 celdas de moto se encuentran ocupadas.
  - **Cuando** una moto con mensualidad al día intenta ingresar.
  - **Entonces** el sistema rechaza el ingreso indicando "Capacidad máxima alcanzada para Motos. No hay celdas disponibles."

### HU-04: Registro de Salida y Liberación de Cupo en 1 Clic
* **Como:** Operador de cabina.
* **Quiero:** Registrar el retiro de un vehículo del parqueadero pulsando un botón.
* **Para:** Desocupar la celda inmediatamente sin tener que liquidar cobros de dinero en efectivo.
* **Criterios de Aceptación (Gherkin):**
  - **Dado** que el vehículo `ABC-123` está en la lista de vehículos adentro ocupando la celda `C-24`.
  - **Cuando** el operador pulsa "Dar Salida".
  - **Entonces** el sistema actualiza la fecha y hora de salida, pasa la celda `C-24` a `DISPONIBLE` y recalcula los contadores en tiempo real.

### HU-05: Visualización de las 80 Celdas en Planta
* **Como:** Supervisor de turno.
* **Quiero:** Un mapa interactivo de las 80 celdas con semaforización verde/rojo.
* **Para:** Conocer al instante qué puestos están libres y quién está estacionado en cada uno.
* **Criterios de Aceptación (Gherkin):**
  - **Dado** el mapa de celdas en pantalla.
  - **Cuando** el usuario hace clic sobre la celda `C-24`.
  - **Entonces** el panel lateral muestra la placa, modelo, color, conductor y tiempo transcurrido del vehículo estacionado.

---

## 7. ANEXO VISUAL: DIAGRAMAS DEL SISTEMA

### 7.1 Diagrama de Paquetes
![Diagrama de Paquetes](diagramas/1_diagrama_paquetes.png)

### 7.2 Diagrama de Casos de Uso
![Diagrama de Casos de Uso](diagramas/2_diagrama_casos_de_uso.png)

### 7.3 Diagrama de Clases del Dominio
![Diagrama de Clases](diagramas/3_diagrama_de_clases.png)

### 7.4 Diagrama de Secuencia: Proceso de Ingreso
![Secuencia de Entrada](diagramas/4_diagrama_secuencia_entrada.png)

### 7.5 Diagrama de Secuencia: Proceso de Salida
![Secuencia de Salida](diagramas/5_diagrama_secuencia_salida.png)

