# Guion Estructurado para el Video Demostrativo — Iteración 2 (Autos Colombia 24/7)

- **Asignatura:** Ingeniería de Software (`PREICA2602B020053`) — Docente: **Prof. Reinaldo Rojas**
- **Grupo 25:** Adriana Andrea Agudelo Agudelo, Camilo Alberto Palacios Turriago y Juan Daniel Pulgarin García
- **Duración recomendada:** 5 a 7 minutos
- **Requisito estricto de rúbrica (10 puntos):** Subir a **YouTube** (*Público* o *No listado*) o **Google Drive** configurado como **"Cualquier persona con el enlace puede ver"** (verificar abriendo el enlace en ventana de incógnito antes de enviar).

---

## Paso Previo antes de Grabar (30 segundos)

1. Abre una terminal en `C:\Users\Camilo Palacios\Documents\aplicacion de parqueo`.
2. Ejecuta primero las pruebas automatizadas para tenerlas listas en pantalla:
   ```powershell
   python -X utf8 tests_iteracion2.py
   ```
3. Inicia el servidor web multi-hilo:
   ```powershell
   python -X utf8 app.py
   ```
4. Abre el navegador en `http://localhost:8000`.

---

## Estructura Minuto a Minuto de la Sustentación

### 1. Presentación e Integración Arquitectónica (0:00 – 0:50)
- Saludo formal presentando a los integrantes del **Grupo 25** y el objetivo de la **Iteración 2**: incorporar **Gestión de Usuarios con Control RBAC (Roles y Permisos)** y **Gestión CRUD / Mantenimiento / Reubicación de las 80 Celdas** (70 carros `C-01..C-70` y 10 motos `M-01..M-10`), integrados sobre el control de entrada/salida de la Iteración 1 (*aclarando que la Gestión de Pagos queda reservada para la Iteración 3*).
- Muestra brevemente el repositorio en GitHub (`https://github.com/Camilo-Alberto-Palacio/autos-colombia-parqueadero`) y la terminal donde los **20 casos de prueba (`tests_iteracion2.py`)** pasaron al 100% (`OK`).

### 2. Demostración de Autenticación SHA-256 y Control RBAC (0:50 – 2:15)
- En la barra superior haz clic en **"Cambiar Sesión"**:
  1. Inicia sesión como **`admin` (`admin123`)**: muestra que todos los controles CRUD están habilitados y entra a la pestaña **4. Usuarios y Roles**.
  2. Crea un usuario en vivo (ej. `carlos_op`, rol `OPERARIO`), restablece su contraseña SHA-256 e intenta suspender al único `ADMIN` para evidenciar la **regla de protección del último Administrador**.
  3. Cambia de sesión con 1 clic a **`auditor` (`auditor123`)**: señala el banner esmeralda de **Solo Lectura** y cómo los botones de escritura quedan protegidos por RBAC (`HTTP 403`).
  4. Cambia a **`adriana_op` (`operario123`)** y luego regresa a **`admin`** para continuar la demostración completa.

### 3. Gestión CRUD de Clientes Abonados y Vehículos (2:15 – 3:00)
- Abre la pestaña **5. Abonados**:
  - Muestra el padrón con tarifas reglamentarias (\$250.000 Carro / \$100.000 Moto).
  - Haz clic en **"Editar Datos"** sobre `ABC-123` (ej. cambia el color o teléfono del titular) para mostrar cómo se actualiza el registro cuando un abonado actualiza su vehículo, tal como se indicó en el encuentro sincrónico.

### 4. Gestión CRUD de Celdas, Mantenimiento y Exclusión en Sorteo (3:00 – 4:45)
- Abre la pestaña **3. CRUD Celdas**:
  1. Muestra los indicadores en tiempo real (**80 Celdas: 70 Carros / 10 Motos**).
  2. Pulsa **"+ Nueva Celda (CRUD)"**, crea la celda `C-71` en Piso 2 (pasa a 81 celdas), edítala y luego pulsa **"Eliminar"** para demostrar el ciclo CRUD completo volviendo a las **80 celdas reglamentarias**.
  3. Sobre la celda `C-05`, pulsa **"Estado"**, pásala a **`MANTENIMIENTO`** indicando *"Reparación de sensor ultrasónico"* y muestra cómo aparece inmediatamente en la **Bitácora Técnica de Historial de Celdas** y en ámbar dentro de **2. Mapa 80 Celdas**.

### 5. Integración Iteración 1 + 2: Entrada, Reubicación Atómica y Salida (4:45 – 6:15)
- Ve a **1. Entrada / Salida**:
  1. Prueba `XYZ-999` (En Mora) -> muestra que el ingreso está **bloqueado sin días de gracia**.
  2. Verifica `ABC-123` (Vigente) -> pulsa **"ABRIR BARRERA Y ASIGNAR CELDA ALEATORIA"** (explica que el sorteo excluye automáticamente las celdas en `MANTENIMIENTO` como `C-05`).
  3. En la tarjeta del vehículo estacionado adentro, pulsa **"Reubicar Celda"**, selecciona otra celda libre compatible (ej. `C-01`), deja marcado *"Bloquear automáticamente celda origen en MANTENIMIENTO"* y ejecuta el traslado transaccional.
  4. Finalmente pulsa **"Dar Salida"** para liberar la celda a `DISPONIBLE` y muestra la trazabilidad completa en **6. Auditoría 24/7**.

---

## Cómo Insertar tu Enlace Público en el PDF en 5 Segundos

Una vez subido el video y verificado el acceso público, ejecuta este comando en PowerShell para incrustar automáticamente tu enlace real en el documento oficial HTML y regenerar los PDFs listos para Canvas:

```powershell
python -X utf8 "C:\Users\Camilo Palacios\Documents\IU_Digital_Ingenieria_Software_Entrega_Actividad_2_Iteracion_2_Parqueadero\01_Evidencia_Aprendizaje_2_Iteracion_2_Parqueadero\sustentacion_y_video\actualizar_enlace_video.py" "https://youtu.be/TU_ENLACE_PUBLICO_AQUI"
```
