# Guion de Sustentación en Video — Evidencia de Aprendizaje 3 (Iteración 3: Gestión de Pagos)

**Institución Universitaria Digital de Antioquia (IU Digital)**  
**Asignatura:** Ingeniería de Software (`PREICA2602B020053`) — **Grupo 25**  
**Docente:** Prof. Reinaldo Rojas  
**Integrantes:** Adriana Andrea Agudelo Agudelo · Camilo Alberto Palacios Turriago · Juan Daniel Pulgarin García  
**Duración estimada total:** 7:30 a 8:30 minutos (Presentación documental + Demostración en vivo del aplicativo)  

---

## Recomendaciones previas a la grabación

1. Abrir el documento oficial [`Palacios_Camilo_EA3.pdf`](../documento/Palacios_Camilo_EA3.pdf) en pantalla completa al 100 % o ajustar a ancho de página.
2. Tener abierta en paralelo la terminal dentro de `aplicacion de parqueo` y una pestaña del navegador en `http://localhost:8000` (con `python app.py` ya iniciado antes de la demo en vivo).
3. Al finalizar y subir el video a YouTube (*Oculto/Público*) o Google Drive (*Cualquier persona con el enlace puede ver*), ejecutar:
   ```bash
   python actualizar_enlace_video.py "https://enlace-de-tu-video"
   ```
   para actualizar automáticamente el HTML, el Word y el PDF definitivo.

---

## Parte 1 — Páginas 1 a 7 (Duración aprox.: 0:00 – 2:15)

* **Pantalla:** Página 1 (Portada Oficial) y Página 2 (Tabla de Contenido e Introducción).
* **Locución sugerida:**

> "Un cordial saludo, profesor Reinaldo Rojas y compañeros de la IU Digital.  
> Somos el **Grupo 25** de Ingeniería de Software, conformado por **Adriana Andrea Agudelo Agudelo**, **Camilo Alberto Palacios Turriago** y **Juan Daniel Pulgarin García**.  
> En este video sustentamos la **Evidencia de Aprendizaje 3 (Entrega Final)** del sistema **Autos Colombia 24/7**, dedicada exclusivamente al módulo de **Gestión de Pagos** y su acoplamiento con las iteraciones anteriores.  
> Como se acordó en la sesión de la Semana 6, los pagos se registran **directamente en la plataforma** por el Operario de Cabina o el Administrador, **sin pasarela de pagos externa**, manejando tarifas planas de **$250.000 COP** para carros y **$100.000 COP** para motos en Efectivo, Código QR, Transferencia Bancaria o Consignación.  
> El principio rector del módulo es separar estrictamente la `fecha_pago` —prohibiendo fechas futuras— de la `fecha_vencimiento`: los pagos anticipados conservan los días restantes, los pagos en mora corren de forma consecutiva desde la fecha vencida sin regalar días por atraso y ninguna transacción o abonado se borra físicamente."

* **Pantalla:** Páginas 3 y 4 (Ítem A — Requerimientos Funcionales `RF-19` a `RF-24`, Matriz RBAC y `RNF-11` a `RNF-14`).
* **Locución sugerida:**

> "En las **páginas 3 y 4**, correspondientes al **Ítem A**, formulamos los seis requerimientos funcionales exclusivos de esta iteración (`RF-19` a `RF-24`), cada uno en correspondencia exacta 1 a 1 con su caso de uso y su historia de usuario.  
> En la Matriz RBAC de la página 4 incorporamos dos permisos financieros: `GESTION_PAGOS`, habilitado para `ADMIN` y `OPERARIO`, y `ANULAR_PAGOS`, reservado **exclusivamente para `ADMIN`**. El perfil `AUDITOR` mantiene estricto bloqueo HTTP 403 sobre cualquier escritura.  
> En los requerimientos no funcionales (`RNF-11` a `RNF-14`) garantizamos atomicidad transaccional `BEGIN IMMEDIATE` en SQLite WAL, prohibición absoluta de `DELETE` físico, determinismo de fechas y cumplimiento de calidad estática bajo criterios de SonarQube sin código duplicado."

* **Pantalla:** Páginas 5, 6 y 7 (Ítem B — Casos de Uso StarUML `CU-11` a `CU-16` e inicio del Ítem C `HU-11`, `HU-12`).
* **Locución sugerida:**

> "En las **páginas 5 y 6 (Ítem B)** presentamos el Diagrama de Casos de Uso exclusivo del módulo de Pagos elaborado en StarUML bajo UML 2.5, junto con las especificaciones de `CU-11` a `CU-16`. Notamos la herencia entre actores (`Administrador --|> Operario --|> Auditor`), inclusiones obligatorias `<<include>>` hacia el cálculo consecutivo, verificación RBAC y auditoría, y la relación `<<extend>>` para alertas preventivas de cobro.  
> En la **página 7** abrimos el **Ítem C** con `HU-11` y `HU-12` en formato Gherkin (`Dado / Cuando / Entonces`), detallando la validación de fecha no futura y las tres variantes de vigencia: pago anticipado, pago puntual y mora consecutiva incluso multi-mes. Cedo la palabra para las páginas 8 a 13."

---

## Parte 2 — Páginas 8 a 13 (Duración aprox.: 2:15 – 4:15)

* **Pantalla:** Páginas 8 y 9 (Cierre del Ítem C — Historias de Usuario `HU-13` a `HU-16`).
* **Locución sugerida:**

> "Muchas gracias. Continuando en las **páginas 8 y 9**, completamos las Historias de Usuario de Pagos:  
> * **`HU-13`** cubre la emisión automática de recibos consecutivos `REC-YYYYMMDD-XXXX` y el filtrado del Libro Mayor.  
> * **`HU-14`** restringe al Administrador la anulación lógica de un pago erróneo con motivo contable obligatorio y reversión automática del corte.  
> * **`HU-15`** controla la baja lógica del servicio (`vehiculo.activo = 0`, `mensualidad = CANCELADA`), impidiendo retirar clientes con vehículo `ADENTRO` o con `MORA_PENDIENTE`, y permite reactivar luego cobrando 30 días desde la nueva fecha de pago.  
> * Y **`HU-16`** consolida el flujo de caja por método y categoría vehicular junto con el envío auditado de alertas preventivas."

* **Pantalla:** Páginas 10, 11, 12 y 13 (Ítem D — Mockups de Cobalt Bay OS).
* **Locución sugerida:**

> "Entre las **páginas 10 y 13 (Ítem D)** exhibimos las capturas reales de la interfaz Cobalt Bay OS diseñadas específicamente para Gestión de Pagos:  
> * En la **página 10** observamos el formulario de registro directo previsualizando `MORA_CONSECUTIVA` sobre la placa `XYZ-999`: el sistema explica al operario que se suman 30 días desde el corte vencido sin correr fechas, mientras a la derecha se desglosa la caja y las alertas de mora.  
> * En la **página 11** evidenciamos el caso `PAGO_ANTICIPADO` sobre `ABC-123` conservando sus días ya vigentes, junto al Libro Mayor inferior filtrable por placa o método y con botón `Anular` visible solo para `ADMIN`.  
> * En la **página 12** vemos el modal oficial del Comprobante listo para impresión.  
> * Y en la **página 13** el modal de Baja Lógica integrado en el padrón de abonados, protegiendo la integridad referencial. Doy paso a mi compañero para arquitectura, pruebas y demo en vivo."

---

## Parte 3 — Páginas 14 a 22 (Duración aprox.: 4:15 – 6:15)

* **Pantalla:** Páginas 14, 15 y 16 (Ítem E — Diagramas de Secuencia `3A`, `3B` y `3C` actualizado).
* **Locución sugerida:**

> "Gracias. En las **páginas 14 a 16 (Ítem E)** respetamos el principio de no repetir diagramas sin cambios de la entrega anterior, presentando únicamente los dos diagramas nuevos y la actualización del flujo de ingreso:  
> * En la **Secuencia 3A** seguimos la previsualización en vivo y la transacción atómica de registro de pago con rechazo a fechas futuras y bloqueos RBAC.  
> * En la **Secuencia 3B** modelamos la baja lógica validada, la reactivación de servicio y la anulación exclusiva de `ADMIN`.  
> * Y en la **Secuencia 3C** (actualización de `2C`) mostramos el cruce entre módulos: cuando la barrera rechaza a un abonado por mora, el operario cobra directamente en plataforma y reintenta la entrada obteniendo asignación inmediata de celda."

* **Pantalla:** Páginas 17, 18 y 19 (Ítem F — Diagrama de Componentes, Clases y MER 3FN de 9 Tablas).
* **Locución sugerida:**

> "En las **páginas 17 a 19 (Ítem F)** detallamos la arquitectura técnica actualizada para las tres iteraciones: el Diagrama de Componentes acopla la interfaz `IGestionPagos` y la vista de Caja sobre SQLite WAL; el Diagrama de Clases integra `Pago` en composición con `Mensualidad`; y el Modelo Entidad-Relación físico en Tercera Forma Normal evoluciona de 8 a **9 tablas normalizadas** al incorporar `PAGO` vinculada por llaves foráneas a `VEHICULO`, `MENSUALIDAD` y `USUARIO`."

* **Pantalla:** Páginas 20, 21 y 22 (Ítem G — Plan de Pruebas `CP-21` a `CP-32`, Ítems H e I, Conclusiones).
* **Locución sugerida:**

> "En las **páginas 20 y 21 (Ítem G)** resumimos los **12 casos de prueba exclusivos de Pagos (`CP-21` a `CP-32`)** consignados en el archivo Excel adjunto y automatizados en `tests_iteracion3_pagos.py`. Como veremos enseguida, las 12 pruebas de pagos pasaron al 100 % sin romper ninguna de las 20 pruebas previas de las Iteraciones 1 y 2.  
> Finalmente, en la **página 22 (Ítems H e I)** presentamos la URL del repositorio público en GitHub, el enlace a este video, nuestras conclusiones técnicas y las referencias en norma APA 7. Ahora pasemos brevemente a la aplicación en ejecución."

---

## Parte 4 — Demostración en Vivo del Sistema (Duración aprox.: 6:15 – 8:30)

1. **Terminal — Batería de Pruebas (`tests_iteracion3_pagos.py` y `tests_iteracion2.py`):**
   ```bash
   python -X utf8 tests_iteracion3_pagos.py
   python -X utf8 tests_iteracion2.py
   python app.py
   ```
   > *"Ejecutamos la suite de Iteración 3 (`Ran 12 tests ... OK`) y la suite de regresión (`Ran 20 tests ... OK`). Iniciamos `app.py` y abrimos `http://localhost:8000`."*

2. **Navegador — Bloqueo en Barrera por Mora + Enlace directo (`adriana_op / operario123`):**
   - Iniciar sesión como `adriana_op` (`OPERARIO`).
   - En **1. Entrada / Salida**, verificar la placa en mora `XYZ-999`: mostrar mensaje `MENSUALIDAD_VENCIDA` y pulsar **`Ir a Registrar Pago`**.
   > *"Aquí observamos en vivo el flujo del Diagrama de Secuencia 3C: la barrera bloquea `XYZ-999` por mora y redirige directo a Pagos."*

3. **Mora Consecutiva y Pago Anticipado:**
   - En **6. Gestión de Pagos y Caja**, seleccionar `XYZ-999` (hoy, `1 Mes`, `CODIGO_QR`, referencia `QR-DEMO-01`), mostrar la caja verde/ámbar explicando `MORA_CONSECUTIVA` (corte suma 30 días desde el vencimiento atrasado, sin regalar días) y confirmar pago.
   - Seleccionar luego `ABC-123` (`VIGENTE`), elegir hoy y verificar la previsualización `PAGO_ANTICIPADO` conservando los días restantes + 30 días adicionales. Confirmar y abrir el modal **Recibo** (`REC-...`).
   - Regresar brevemente a **1. Entrada / Salida**, ingresar `XYZ-999` y mostrar asignación inmediata de celda.

4. **Validaciones de Negocio, Alertas, RBAC, Anulación y Baja Lógica:**
   - Intentar digitar una **fecha futura** en el formulario -> mostrar rechazo inmediato (`FECHA_FUTURA`).
   - Pulsar **Notificar WhatsApp** en una alerta de cartera vencida y verificar el mensaje generado + bitácora.
   - Mostrar que como `OPERARIO` no aparece/no se permite anular pagos, luego cambiar sesión a `admin / admin123`, ir al Libro Mayor de Pagos, pulsar **Anular** ingresando un motivo y evidenciar que el registro pasa a estado **`ANULADO`** (sin eliminarse de SQLite) y la fecha de corte se revierte.
   - Mostrar en **5. Clientes Abonados (CRUD)** un botón **Dar Baja** (`vehiculo.activo=0`) y su posterior opción **Reactivar**.
   - Iniciar sesión brevemente como `auditor / auditor123` para comprobar visibilidad en modo solo lectura de Flujo de Caja, Libro Mayor y **7. Bitácora Auditoría 24/7**.

> *"Con esta demostración comprobamos en funcionamiento real el 100 % de los requisitos acordados para la Iteración 3. Muchas gracias al profesor Reinaldo Rojas por su orientación durante todo el curso. ¡Feliz resto de día!"*
