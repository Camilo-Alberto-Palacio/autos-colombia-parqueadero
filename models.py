"""
Lógica del Negocio y Control de Acceso 24/7 - Autos Colombia
Iteración 1: Gestión Exclusiva de Entrada y Salida
Docente: Reinaldo Rojas
Incluye:
  - Concurrencia segura para múltiples operarios/puertas simultáneas
  - Asignación dinámica/aleatoria de celdas (70 Carros, 10 Motos)
  - Validación estricta de mensualidad sin periodo de gracia
  - Registro de novedades/observaciones del estado físico al ingresar y salir
"""

import random
from datetime import datetime, date, timedelta
from database import get_connection, db_lock

TARIFA_CARRO = 250000.00
TARIFA_MOTO = 100000.00
CAPACIDAD_CARROS = 70
CAPACIDAD_MOTOS = 10
CAPACIDAD_TOTAL = 80

def limpiar_placa(placa: str) -> str:
    """Normaliza la placa eliminando guiones, espacios y convirtiendo a mayúsculas."""
    if not placa:
        return ""
    return placa.replace("-", "").replace(" ", "").strip().upper()

def formatear_placa(placa: str) -> str:
    """Devuelve la placa en formato visual estándar AAA-000."""
    p = limpiar_placa(placa)
    if len(p) == 6:
        return f"{p[:3]}-{p[3:]}"
    return p

def consultar_vehiculo(placa_raw: str):
    """
    Busca un vehículo por placa, verifica su información técnica (tipo, marca, modelo, color),
    estado de la mensualidad y si está actualmente dentro del parqueadero.
    """
    placa = limpiar_placa(placa_raw)
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT 
        v.placa,
        v.tipo_vehiculo,
        v.marca,
        v.modelo,
        v.color,
        v.activo,
        p.id AS propietario_id,
        p.nombre_completo AS propietario_nombre,
        p.telefono AS propietario_telefono,
        p.documento AS propietario_doc
    FROM vehiculo v
    JOIN propietario p ON v.propietario_id = p.id
    WHERE REPLACE(REPLACE(v.placa, '-', ''), ' ', '') = ?
    """
    cursor.execute(query, (placa,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    vehiculo = dict(row)

    # Buscar la última mensualidad registrada
    query_mensualidad = """
    SELECT id, fecha_pago, fecha_vencimiento, valor_pagado, estado
    FROM mensualidad
    WHERE vehiculo_placa = ?
    ORDER BY fecha_vencimiento DESC
    LIMIT 1
    """
    cursor.execute(query_mensualidad, (vehiculo['placa'],))
    mensualidad_row = cursor.fetchone()

    hoy = date.today()
    if mensualidad_row:
        m = dict(mensualidad_row)
        fecha_venc = datetime.strptime(m['fecha_vencimiento'], "%Y-%m-%d").date()
        m['dias_restantes'] = (fecha_venc - hoy).days
        # Regla estricta: Sin periodo de gracia. Si fecha_venc < hoy, está vencida.
        m['al_dia'] = (fecha_venc >= hoy) and (m['estado'] == 'ACTIVA')
        vehiculo['mensualidad'] = m
    else:
        vehiculo['mensualidad'] = None

    # Verificar si actualmente se encuentra dentro del parqueadero
    query_adentro = """
    SELECT r.id, r.celda_codigo, r.fecha_ingreso, r.estado, r.observaciones
    FROM registro_acceso r
    WHERE r.vehiculo_placa = ? AND r.estado = 'ADENTRO'
    ORDER BY r.fecha_ingreso DESC
    LIMIT 1
    """
    cursor.execute(query_adentro, (vehiculo['placa'],))
    adentro_row = cursor.fetchone()
    vehiculo['esta_adentro'] = adentro_row is not None
    vehiculo['registro_actual'] = dict(adentro_row) if adentro_row else None

    conn.close()
    return vehiculo

def registrar_ingreso(placa_raw: str, observaciones: str = None, puerta: str = "Puerta 1 (Norte)"):
    """
    Valida y procesa el ingreso de un vehículo al parqueadero 24/7 con bloqueo transaccional
    para soportar múltiples operarios en simultáneo sin colisión de celdas.
    """
    with db_lock:
        placa = limpiar_placa(placa_raw)
        vehiculo = consultar_vehiculo(placa)

        if not vehiculo:
            return {
                "success": False,
                "codigo_error": "NO_REGISTRADO",
                "mensaje": f"El vehículo con placa '{formatear_placa(placa)}' NO se encuentra registrado en el sistema de abonados.",
                "detalle": "El parqueadero opera exclusivamente por mensualidad."
            }

        if vehiculo['esta_adentro']:
            celda = vehiculo['registro_actual']['celda_codigo']
            return {
                "success": False,
                "codigo_error": "YA_ADENTRO",
                "mensaje": f"Control de duplicidad: El vehículo '{formatear_placa(placa)}' ya figura ADENTRO en la celda {celda}.",
                "detalle": "No se puede registrar doble ingreso sin haber registrado antes su salida."
            }

        mensualidad = vehiculo['mensualidad']
        if not mensualidad or not mensualidad['al_dia']:
            fecha_v = mensualidad['fecha_vencimiento'] if mensualidad else "Sin registro"
            return {
                "success": False,
                "codigo_error": "MENSUALIDAD_VENCIDA",
                "mensaje": f"Acceso Denegado: La mensualidad del vehículo '{formatear_placa(placa)}' está VENCIDA ({fecha_v}).",
                "detalle": "No existe periodo de gracia. El pago debe estar vigente para autorizar el ingreso.",
                "vehiculo": vehiculo
            }

        tipo = vehiculo['tipo_vehiculo']
        conn = get_connection()
        cursor = conn.cursor()

        try:
            # Iniciar transacción inmediata para evitar condición de carrera entre operarios
            cursor.execute("BEGIN IMMEDIATE;")

            cursor.execute("""
                SELECT codigo, piso, zona 
                FROM celda 
                WHERE tipo_permitido = ? AND estado = 'DISPONIBLE'
            """, (tipo,))
            celdas_libres = [dict(r) for r in cursor.fetchall()]

            if not celdas_libres:
                conn.rollback()
                conn.close()
                return {
                    "success": False,
                    "codigo_error": "SIN_CUPO",
                    "mensaje": f"Capacidad máxima alcanzada para {tipo}s. No hay celdas disponibles.",
                    "detalle": f"Aforo máximo reglamentario: {CAPACIDAD_CARROS if tipo == 'CARRO' else CAPACIDAD_MOTOS} celdas para {tipo.lower()}s."
                }

            # Asignación DINÁMICA / ALEATORIA requerida por el profesor
            celda_elegida = random.choice(celdas_libres)
            codigo_celda = celda_elegida['codigo']
            fecha_ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            obs_limpia = (observaciones or "").strip()
            texto_obs = f"[{puerta}] {obs_limpia}" if obs_limpia else f"[{puerta}] Sin novedades físicas al ingreso"

            # Marcar celda como OCUPADA
            cursor.execute("""
                UPDATE celda 
                SET estado = 'OCUPADA' 
                WHERE codigo = ?
            """, (codigo_celda,))

            # Registrar el acceso
            cursor.execute("""
                INSERT INTO registro_acceso (vehiculo_placa, celda_codigo, fecha_ingreso, estado, observaciones)
                VALUES (?, ?, ?, 'ADENTRO', ?)
            """, (vehiculo['placa'], codigo_celda, fecha_ahora, texto_obs))

            registro_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return {
                "success": True,
                "registro_id": registro_id,
                "mensaje": f"¡Barrera Abierta en {puerta}! Ingreso autorizado para {formatear_placa(placa)}.",
                "celda_asignada": codigo_celda,
                "zona": celda_elegida['zona'],
                "piso": celda_elegida['piso'],
                "fecha_ingreso": fecha_ahora,
                "observaciones": texto_obs,
                "vehiculo": vehiculo
            }
        except Exception as e:
            conn.rollback()
            conn.close()
            return {
                "success": False,
                "codigo_error": "ERROR_TRANSACCION",
                "mensaje": f"Error de concurrencia al asignar celda: {str(e)}"
            }

def registrar_salida(placa_raw: str, observaciones_salida: str = None, puerta: str = "Puerta 1 (Norte)"):
    """
    Registra la salida del vehículo (por placa o selección) y libera automáticamente su celda.
    Permite anexar observaciones de salida.
    """
    with db_lock:
        placa = limpiar_placa(placa_raw)
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT r.id, r.vehiculo_placa, r.celda_codigo, r.fecha_ingreso, r.observaciones,
               v.tipo_vehiculo, v.marca, v.modelo, v.color, p.nombre_completo AS conductor
        FROM registro_acceso r
        JOIN vehiculo v ON r.vehiculo_placa = v.placa
        JOIN propietario p ON v.propietario_id = p.id
        WHERE REPLACE(REPLACE(r.vehiculo_placa, '-', ''), ' ', '') = ? AND r.estado = 'ADENTRO'
        ORDER BY r.fecha_ingreso DESC
        LIMIT 1
        """
        cursor.execute(query, (placa,))
        registro = cursor.fetchone()

        if not registro:
            conn.close()
            return {
                "success": False,
                "codigo_error": "NO_ESTA_ADENTRO",
                "mensaje": f"El vehículo '{formatear_placa(placa)}' no se encuentra actualmente dentro del parqueadero."
            }

        reg_dict = dict(registro)
        fecha_salida = datetime.now()
        fecha_ingreso = datetime.strptime(reg_dict['fecha_ingreso'], "%Y-%m-%d %H:%M:%S")
        duracion = fecha_salida - fecha_ingreso
        horas = int(duracion.total_seconds() // 3600)
        minutos = int((duracion.total_seconds() % 3600) // 60)
        segundos = int(duracion.total_seconds() % 60)
        if horas > 0:
            tiempo_texto = f"{horas}h {minutos}m"
        elif minutos > 0:
            tiempo_texto = f"{minutos}m {segundos}s"
        else:
            tiempo_texto = f"{segundos} seg"

        fecha_salida_str = fecha_salida.strftime("%Y-%m-%d %H:%M:%S")

        obs_previa = reg_dict.get('observaciones') or ""
        if observaciones_salida and observaciones_salida.strip():
            obs_final = f"{obs_previa} | Salida ({puerta}): {observaciones_salida.strip()}"
        else:
            obs_final = f"{obs_previa} | Salida ({puerta}): OK"

        try:
            cursor.execute("BEGIN IMMEDIATE;")
            # Finalizar registro de acceso
            cursor.execute("""
                UPDATE registro_acceso 
                SET fecha_salida = ?, estado = 'FINALIZADO', observaciones = ?
                WHERE id = ?
            """, (fecha_salida_str, obs_final, reg_dict['id']))

            # Liberar la celda inmediatamente
            cursor.execute("""
                UPDATE celda 
                SET estado = 'DISPONIBLE' 
                WHERE codigo = ?
            """, (reg_dict['celda_codigo'],))

            conn.commit()
            conn.close()
        except Exception as e:
            conn.rollback()
            conn.close()
            return {"success": False, "mensaje": f"Error al liberar celda: {str(e)}"}

        return {
            "success": True,
            "registro_id": reg_dict['id'],
            "mensaje": f"Salida registrada en {puerta}. Celda {reg_dict['celda_codigo']} liberada inmediatamente.",
            "placa": formatear_placa(reg_dict['vehiculo_placa']),
            "celda_liberada": reg_dict['celda_codigo'],
            "fecha_ingreso": reg_dict['fecha_ingreso'],
            "fecha_salida": fecha_salida_str,
            "tiempo_permanencia": tiempo_texto,
            "observaciones": obs_final,
            "vehiculo": {
                "marca": reg_dict['marca'],
                "modelo": reg_dict['modelo'],
                "color": reg_dict['color'],
                "tipo": reg_dict['tipo_vehiculo'],
                "conductor": reg_dict['conductor']
            }
        }

def obtener_resumen_operativo():
    """
    Retorna métricas operativas en tiempo real de capacidad,
    celdas ocupadas/libres, vehículos adentro, listado de las 80 celdas,
    padrón de abonados y últimos movimientos.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Contadores por tipo y estado
    cursor.execute("""
        SELECT tipo_permitido, estado, count(*) as cantidad
        FROM celda
        GROUP BY tipo_permitido, estado
    """)
    conteos = cursor.fetchall()

    carros_libres = 0
    carros_ocupados = 0
    motos_libres = 0
    motos_ocupadas = 0

    for c in conteos:
        tipo = c['tipo_permitido']
        estado = c['estado']
        cant = c['cantidad']
        if tipo == 'CARRO':
            if estado == 'DISPONIBLE':
                carros_libres = cant
            elif estado == 'OCUPADA':
                carros_ocupados = cant
        elif tipo == 'MOTO':
            if estado == 'DISPONIBLE':
                motos_libres = cant
            elif estado == 'OCUPADA':
                motos_ocupadas = cant

    # Lista de vehículos actualmente adentro
    cursor.execute("""
        SELECT 
            r.id AS registro_id,
            r.vehiculo_placa,
            r.celda_codigo,
            r.fecha_ingreso,
            r.observaciones,
            v.tipo_vehiculo,
            v.marca,
            v.modelo,
            v.color,
            p.nombre_completo AS conductor,
            p.telefono AS conductor_telefono
        FROM registro_acceso r
        JOIN vehiculo v ON r.vehiculo_placa = v.placa
        JOIN propietario p ON v.propietario_id = p.id
        WHERE r.estado = 'ADENTRO'
        ORDER BY r.fecha_ingreso DESC
    """)
    vehiculos_adentro = [dict(r) for r in cursor.fetchall()]

    ahora = datetime.now()
    for v in vehiculos_adentro:
        try:
            f_in = datetime.strptime(v['fecha_ingreso'], "%Y-%m-%d %H:%M:%S")
            diff = ahora - f_in
            h = int(diff.total_seconds() // 3600)
            m = int((diff.total_seconds() % 3600) // 60)
            v['tiempo_transcurrido'] = f"{h}h {m}m" if h > 0 else f"{m}m"
        except:
            v['tiempo_transcurrido'] = "Reciente"

    # Mapeo de todas las 80 celdas
    cursor.execute("""
        SELECT 
            c.codigo, 
            c.tipo_permitido, 
            c.estado, 
            c.piso, 
            c.zona,
            r.id AS registro_id,
            r.vehiculo_placa,
            r.fecha_ingreso,
            r.observaciones,
            v.marca,
            v.modelo,
            v.color,
            p.nombre_completo AS conductor
        FROM celda c
        LEFT JOIN registro_acceso r ON c.codigo = r.celda_codigo AND r.estado = 'ADENTRO'
        LEFT JOIN vehiculo v ON r.vehiculo_placa = v.placa
        LEFT JOIN propietario p ON v.propietario_id = p.id
        ORDER BY c.tipo_permitido DESC, c.codigo ASC
    """)
    celdas = [dict(r) for r in cursor.fetchall()]

    # Padrón completo de vehículos abonados registrados en BD
    cursor.execute("""
        SELECT 
            v.placa,
            v.tipo_vehiculo,
            v.marca,
            v.modelo,
            v.color,
            p.nombre_completo AS propietario,
            p.documento,
            p.telefono,
            m.fecha_pago,
            m.fecha_vencimiento,
            m.valor_pagado,
            m.estado AS estado_mensualidad
        FROM vehiculo v
        JOIN propietario p ON v.propietario_id = p.id
        LEFT JOIN mensualidad m ON m.id = (
            SELECT id FROM mensualidad 
            WHERE vehiculo_placa = v.placa 
            ORDER BY fecha_vencimiento DESC LIMIT 1
        )
        ORDER BY v.fecha_creacion DESC, v.placa ASC
    """)
    abonados = []
    hoy = date.today()
    for row in cursor.fetchall():
        ab = dict(row)
        if ab['fecha_vencimiento']:
            fv = datetime.strptime(ab['fecha_vencimiento'], "%Y-%m-%d").date()
            ab['al_dia'] = (fv >= hoy) and (ab['estado_mensualidad'] == 'ACTIVA')
            ab['dias_restantes'] = (fv - hoy).days
        else:
            ab['al_dia'] = False
            ab['dias_restantes'] = -99
        abonados.append(ab)

    # Últimos 20 movimientos (historial)
    cursor.execute("""
        SELECT 
            r.id,
            r.vehiculo_placa,
            r.celda_codigo,
            r.fecha_ingreso,
            r.fecha_salida,
            r.estado,
            r.observaciones,
            v.tipo_vehiculo,
            v.marca,
            v.modelo,
            v.color
        FROM registro_acceso r
        JOIN vehiculo v ON r.vehiculo_placa = v.placa
        ORDER BY r.id DESC
        LIMIT 20
    """)
    historial = [dict(r) for r in cursor.fetchall()]

    conn.close()

    total_ocupadas = carros_ocupados + motos_ocupadas
    total_libres = carros_libres + motos_libres

    return {
        "capacidad_total": CAPACIDAD_TOTAL,
        "total_ocupadas": total_ocupadas,
        "total_libres": total_libres,
        "carros": {
            "total": CAPACIDAD_CARROS,
            "ocupadas": carros_ocupados,
            "libres": carros_libres
        },
        "motos": {
            "total": CAPACIDAD_MOTOS,
            "ocupadas": motos_ocupadas,
            "libres": motos_libres
        },
        "vehiculos_adentro": vehiculos_adentro,
        "total_adentro": len(vehiculos_adentro),
        "celdas": celdas,
        "abonados": abonados,
        "historial": historial
    }

def registrar_nuevo_abonado(datos: dict):
    """
    Registra un vehículo de prueba con su mensualidad (Exactamente 1 mes desde fecha de pago).
    """
    with db_lock:
        placa = limpiar_placa(datos.get('placa'))
        if not placa:
            return {"success": False, "error": "La placa es obligatoria."}
        tipo = datos.get('tipo_vehiculo', 'CARRO').upper()
        marca = datos.get('marca', 'Genérica')
        modelo = datos.get('modelo', '2024')
        color = datos.get('color', 'Blanco')
        conductor = datos.get('conductor', 'Cliente Abonado')
        telefono = datos.get('telefono', '3001234567')
        documento = datos.get('documento', f"CC{random.randint(10000000, 99999999)}")
        estado_pago = datos.get('estado_pago', 'ACTIVA')

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT id FROM propietario WHERE documento = ?", (documento,))
            prop = cursor.fetchone()
            if prop:
                prop_id = prop['id']
            else:
                cursor.execute("""
                    INSERT INTO propietario (documento, nombre_completo, telefono, email)
                    VALUES (?, ?, ?, ?)
                """, (documento, conductor, telefono, f"{documento.lower()}@autoscolombia.com"))
                prop_id = cursor.lastrowid

            cursor.execute("""
                INSERT OR REPLACE INTO vehiculo (placa, tipo_vehiculo, marca, modelo, color, propietario_id, activo)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (placa, tipo, marca, modelo, color, prop_id))

            tarifa = TARIFA_CARRO if tipo == 'CARRO' else TARIFA_MOTO
            hoy = date.today()
            if estado_pago == 'ACTIVA':
                fecha_pago = hoy - timedelta(days=5)
                fecha_venc = hoy + timedelta(days=25)
            else:
                fecha_pago = hoy - timedelta(days=40)
                fecha_venc = hoy - timedelta(days=10)

            cursor.execute("""
                INSERT INTO mensualidad (vehiculo_placa, fecha_pago, fecha_vencimiento, valor_pagado, estado)
                VALUES (?, ?, ?, ?, ?)
            """, (placa, fecha_pago.strftime("%Y-%m-%d"), fecha_venc.strftime("%Y-%m-%d"), tarifa, estado_pago))

            conn.commit()
            conn.close()
            return {"success": True, "mensaje": f"Vehículo {placa} registrado con éxito."}
        except Exception as e:
            conn.close()
            return {"success": False, "error": str(e)}
