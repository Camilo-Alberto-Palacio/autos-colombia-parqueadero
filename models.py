"""
Lógica del Negocio, Gestión de Usuarios, Gestión de Celdas y Control de Acceso 24/7
Sistema de Información Autos Colombia - Iteración 1 y 2 Unificada
Asignatura: Ingeniería de Software - PREICA2602B020053
Docente: Reinaldo Rojas | Grupo: 25
Integrantes:
  - Camilo Alberto Palacios Turriago
  - Adriana Andrea Agudelo Agudelo
  - Juan Daniel Pulgarin García
"""

import random
import hashlib
from datetime import datetime, date, timedelta
from database import get_connection, db_lock

# CONSTANTES DE NEGOCIO Y TARIFAS MENSUALES
TARIFA_CARRO = 250000.00
TARIFA_MOTO = 100000.00
CAPACIDAD_CARROS = 70
CAPACIDAD_MOTOS = 10
CAPACIDAD_TOTAL = 80

ROLES_PERMITIDOS = ('ADMIN', 'OPERARIO', 'AUDITOR')
ESTADOS_CELDA = ('DISPONIBLE', 'OCUPADA', 'MANTENIMIENTO', 'INACTIVA')

# ====================================================================
# UTILIDADES GENERALES Y SEGURIDAD
# ====================================================================

def hash_password(password: str) -> str:
    """Genera hash criptográfico SHA-256 para almacenamiento seguro de credenciales."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

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

def registrar_auditoria(usuario_id: int, modulo: str, accion: str, detalle: str, ip: str = "Terminal Cabina"):
    """Registra una acción en la bitácora de auditoría del sistema."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO auditoria_accion (usuario_id, modulo, accion, detalle, ip_terminal)
            VALUES (?, ?, ?, ?, ?)
        """, (usuario_id, modulo, accion, detalle, ip))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[AUDITORIA ERROR] No se pudo registrar auditoría: {e}")

# ====================================================================
# MÓDULO 1: GESTIÓN DE USUARIOS Y CONTROL DE ACCESO (ITERACIÓN 2)
# ====================================================================

def autenticar_usuario(username: str, password_raw: str, ip: str = "Terminal Web"):
    """
    Autentica un usuario verificando su identificador y contraseña con hash SHA-256.
    Valida que la cuenta esté activa y registra el acceso en auditoría.
    """
    if not username or not password_raw:
        return {"success": False, "mensaje": "Usuario y contraseña requeridos."}

    user_clean = username.strip().lower()
    pw_hash = hash_password(password_raw)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, username, password_hash, nombre_completo, email, rol, cargo, activo
        FROM usuario
        WHERE LOWER(username) = ?
    """, (user_clean,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return {"success": False, "mensaje": f"El usuario '{username}' no existe en el sistema."}

    user_dict = dict(user)

    if not user_dict['activo']:
        conn.close()
        registrar_auditoria(user_dict['id'], 'SEGURIDAD', 'LOGIN_BLOQUEADO', f"Intento de ingreso con usuario inactivo: {user_clean}", ip)
        return {"success": False, "mensaje": "Esta cuenta de usuario ha sido desactivada. Contacte al Administrador."}

    if user_dict['password_hash'] != pw_hash:
        conn.close()
        registrar_auditoria(user_dict['id'], 'SEGURIDAD', 'LOGIN_FALLIDO', f"Contraseña errónea para: {user_clean}", ip)
        return {"success": False, "mensaje": "Contraseña incorrecta. Verifique sus credenciales."}

    # Actualizar fecha y hora de último login
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE usuario SET ultimo_login = ? WHERE id = ?", (ahora, user_dict['id']))
    conn.commit()
    conn.close()

    registrar_auditoria(user_dict['id'], 'SEGURIDAD', 'LOGIN_EXITOSO', f"Sesión iniciada con rol {user_dict['rol']}", ip)

    # Remover hash antes de retornar
    del user_dict['password_hash']
    user_dict['ultimo_login'] = ahora
    return {
        "success": True,
        "mensaje": f"Bienvenido(a), {user_dict['nombre_completo']}.",
        "usuario": user_dict
    }

def listar_usuarios(rol_filtro: str = None, solo_activos: bool = False):
    """Retorna la lista de usuarios del sistema con sus respectivos roles y estadísticas."""
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        SELECT id, username, nombre_completo, email, rol, cargo, activo, fecha_creacion, ultimo_login
        FROM usuario
        WHERE 1=1
    """
    params = []
    if rol_filtro:
        sql += " AND rol = ?"
        params.append(rol_filtro.upper())
    if solo_activos:
        sql += " AND activo = 1"

    sql += " ORDER BY id ASC"
    cursor.execute(sql, params)
    usuarios = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return usuarios

def crear_usuario(datos: dict, admin_id: int = 1):
    """Crea una nueva cuenta de usuario con validación estricta de rol y unicidad."""
    with db_lock:
        username = (datos.get('username') or "").strip().lower()
        password = datos.get('password') or ""
        nombre = (datos.get('nombre_completo') or "").strip()
        email = (datos.get('email') or "").strip().lower()
        rol = (datos.get('rol') or "OPERARIO").strip().upper()
        cargo = (datos.get('cargo') or "Operador de Cabina").strip()

        if not username or len(username) < 3:
            return {"success": False, "mensaje": "El nombre de usuario debe tener mínimo 3 caracteres."}
        if not password or len(password) < 6:
            return {"success": False, "mensaje": "La contraseña debe contener al menos 6 caracteres."}
        if not nombre:
            return {"success": False, "mensaje": "El nombre completo es obligatorio."}
        if not email or "@" not in email:
            return {"success": False, "mensaje": "Debe suministrar un correo electrónico válido."}
        if rol not in ROLES_PERMITIDOS:
            return {"success": False, "mensaje": f"Rol no válido. Permitidos: {', '.join(ROLES_PERMITIDOS)}."}

        conn = get_connection()
        cursor = conn.cursor()

        # Verificar unicidad
        cursor.execute("SELECT id FROM usuario WHERE LOWER(username) = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return {"success": False, "mensaje": f"El nombre de usuario '{username}' ya está en uso."}

        cursor.execute("SELECT id FROM usuario WHERE LOWER(email) = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return {"success": False, "mensaje": f"El correo '{email}' ya se encuentra registrado."}

        pw_hash = hash_password(password)
        cursor.execute("""
            INSERT INTO usuario (username, password_hash, nombre_completo, email, rol, cargo, activo)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (username, pw_hash, nombre, email, rol, cargo))
        nuevo_id = cursor.lastrowid
        conn.commit()
        conn.close()

        registrar_auditoria(admin_id, 'USUARIOS', 'CREAR_USUARIO', f"Creado usuario '{username}' con rol {rol} (ID: {nuevo_id})")
        return {
            "success": True,
            "mensaje": f"Usuario '{username}' creado exitosamente.",
            "usuario_id": nuevo_id
        }

def actualizar_usuario(user_id: int, datos: dict, admin_id: int = 1):
    """Actualiza la información de perfil, rol o estado activo de un usuario."""
    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, username, rol, activo FROM usuario WHERE id = ?", (user_id,))
        actual = cursor.fetchone()
        if not actual:
            conn.close()
            return {"success": False, "mensaje": "Usuario no encontrado."}

        nombre = (datos.get('nombre_completo') or "").strip()
        email = (datos.get('email') or "").strip().lower()
        rol = (datos.get('rol') or actual['rol']).strip().upper()
        cargo = (datos.get('cargo') or "Operador").strip()
        activo = 1 if datos.get('activo', actual['activo']) in (1, True, '1', 'true') else 0

        # Regla: No se puede desactivar al único administrador activo
        if actual['rol'] == 'ADMIN' and activo == 0:
            cursor.execute("SELECT count(*) as total FROM usuario WHERE rol = 'ADMIN' AND activo = 1")
            total_admins = cursor.fetchone()['total']
            if total_admins <= 1:
                conn.close()
                return {"success": False, "mensaje": "Regla de Seguridad: No puede desactivar al único Administrador activo del sistema."}

        cursor.execute("""
            UPDATE usuario
            SET nombre_completo = ?, email = ?, rol = ?, cargo = ?, activo = ?
            WHERE id = ?
        """, (nombre or actual['nombre_completo'], email or actual['email'], rol, cargo, activo, user_id))
        conn.commit()
        conn.close()

        registrar_auditoria(admin_id, 'USUARIOS', 'ACTUALIZAR_USUARIO', f"Actualizado usuario ID {user_id} ({actual['username']}): Rol {rol}, Activo {activo}")
        return {"success": True, "mensaje": f"Usuario '{actual['username']}' actualizado correctamente."}

def cambiar_password(user_id: int, nueva_clave: str, admin_id: int = 1):
    """Restablece la contraseña de un usuario."""
    with db_lock:
        if not nueva_clave or len(nueva_clave) < 6:
            return {"success": False, "mensaje": "La nueva contraseña debe tener mínimo 6 caracteres."}

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM usuario WHERE id = ?", (user_id,))
        u = cursor.fetchone()
        if not u:
            conn.close()
            return {"success": False, "mensaje": "Usuario no encontrado."}

        pw_hash = hash_password(nueva_clave)
        cursor.execute("UPDATE usuario SET password_hash = ? WHERE id = ?", (pw_hash, user_id))
        conn.commit()
        conn.close()

        registrar_auditoria(admin_id, 'USUARIOS', 'CAMBIO_PASSWORD', f"Clave restablecida para usuario {u['username']} (ID: {user_id})")
        return {"success": True, "mensaje": f"Contraseña restablecida exitosamente para {u['username']}."}

# ====================================================================
# MÓDULO 2: GESTIÓN Y ADMINISTRACIÓN DE CELDAS (ITERACIÓN 2)
# ====================================================================

def listar_celdas_administracion(filtro_tipo: str = None, filtro_estado: str = None, filtro_zona: str = None):
    """
    Retorna el estado completo de las 80 celdas, incluyendo vehículo ocupante actual,
    motivo de mantenimiento y trazabilidad.
    """
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        SELECT 
            c.codigo,
            c.tipo_permitido,
            c.estado,
            c.piso,
            c.zona,
            c.motivo_bloqueo,
            r.vehiculo_placa AS ocupante_placa,
            r.fecha_ingreso AS ocupante_desde,
            v.marca AS ocupante_marca,
            v.modelo AS ocupante_modelo,
            v.color AS ocupante_color,
            p.nombre_completo AS ocupante_conductor
        FROM celda c
        LEFT JOIN registro_acceso r ON r.celda_codigo = c.codigo AND r.estado = 'ADENTRO'
        LEFT JOIN vehiculo v ON r.vehiculo_placa = v.placa
        LEFT JOIN propietario p ON v.propietario_id = p.id
        WHERE 1=1
    """
    params = []
    if filtro_tipo:
        sql += " AND c.tipo_permitido = ?"
        params.append(filtro_tipo.upper())
    if filtro_estado:
        sql += " AND c.estado = ?"
        params.append(filtro_estado.upper())
    if filtro_zona:
        sql += " AND c.zona LIKE ?"
        params.append(f"%{filtro_zona}%")

    sql += " ORDER BY c.tipo_permitido ASC, c.codigo ASC"
    cursor.execute(sql, params)
    celdas = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return celdas

def cambiar_estado_celda(codigo: str, nuevo_estado: str, motivo: str = None, usuario_id: int = 1):
    """
    Cambia el estado operativo de una celda (DISPONIBLE, MANTENIMIENTO, INACTIVA).
    Regla estricta: No se puede bloquear una celda que tenga un vehículo adentro.
    """
    with db_lock:
        codigo_clean = codigo.strip().upper()
        estado_clean = nuevo_estado.strip().upper()

        if estado_clean not in ('DISPONIBLE', 'MANTENIMIENTO', 'INACTIVA'):
            return {"success": False, "mensaje": f"Estado no admitido para cambio manual: {nuevo_estado}."}

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT codigo, estado, tipo_permitido FROM celda WHERE codigo = ?", (codigo_clean,))
        celda = cursor.fetchone()
        if not celda:
            conn.close()
            return {"success": False, "mensaje": f"La celda '{codigo_clean}' no existe."}

        estado_anterior = celda['estado']

        # Verificar si la celda tiene un vehículo adentro
        cursor.execute("SELECT vehiculo_placa FROM registro_acceso WHERE celda_codigo = ? AND estado = 'ADENTRO'", (codigo_clean,))
        ocupante = cursor.fetchone()

        if ocupante and estado_clean in ('MANTENIMIENTO', 'INACTIVA'):
            conn.close()
            return {
                "success": False,
                "mensaje": f"Conflicto Operativo: La celda {codigo_clean} está ocupada por el vehículo {ocupante['vehiculo_placa']}. Debe reubicarlo antes de pasarla a {estado_clean}."
            }

        # Actualizar celda
        cursor.execute("""
            UPDATE celda 
            SET estado = ?, motivo_bloqueo = ? 
            WHERE codigo = ?
        """, (estado_clean, motivo if estado_clean != 'DISPONIBLE' else None, codigo_clean))

        # Registrar en historial_celda
        cursor.execute("""
            INSERT INTO historial_celda (celda_codigo, estado_anterior, estado_nuevo, motivo, usuario_id)
            VALUES (?, ?, ?, ?, ?)
        """, (codigo_clean, estado_anterior, estado_clean, motivo or "Cambio de estado operativo", usuario_id))

        conn.commit()
        conn.close()

        registrar_auditoria(usuario_id, 'CELDAS', 'CAMBIO_ESTADO', f"Celda {codigo_clean} cambió de {estado_anterior} a {estado_clean}. Motivo: {motivo or 'N/A'}")
        return {
            "success": True,
            "mensaje": f"Celda {codigo_clean} actualizada con éxito a estado {estado_clean}."
        }

def reubicar_vehiculo_celda(placa_raw: str, nueva_celda_codigo: str, motivo: str = None, marcar_anterior_mantenimiento: bool = False, usuario_id: int = 1):
    """
    Reubica de manera atómica un vehículo estacionado de su celda actual a una nueva celda libre
    del mismo tipo, permitiendo opcionalmente poner en mantenimiento la celda origen por avería física.
    """
    with db_lock:
        placa = limpiar_placa(placa_raw)
        nueva_celda = nueva_celda_codigo.strip().upper()

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("BEGIN IMMEDIATE;")

            # 1. Buscar movimiento activo del vehículo
            cursor.execute("""
                SELECT r.id, r.celda_codigo, v.tipo_vehiculo
                FROM registro_acceso r
                JOIN vehiculo v ON r.vehiculo_placa = v.placa
                WHERE r.vehiculo_placa = ? AND r.estado = 'ADENTRO'
            """, (placa,))
            movimiento = cursor.fetchone()

            if not movimiento:
                conn.rollback()
                conn.close()
                return {"success": False, "mensaje": f"El vehículo {formatear_placa(placa)} no se encuentra dentro del parqueadero."}

            celda_origen = movimiento['celda_codigo']
            tipo_vehiculo = movimiento['tipo_vehiculo']

            if celda_origen == nueva_celda:
                conn.rollback()
                conn.close()
                return {"success": False, "mensaje": "La nueva celda seleccionada es idéntica a la celda actual."}

            # 2. Validar disponibilidad y compatibilidad de la nueva celda
            cursor.execute("SELECT tipo_permitido, estado FROM celda WHERE codigo = ?", (nueva_celda,))
            c_destino = cursor.fetchone()

            if not c_destino:
                conn.rollback()
                conn.close()
                return {"success": False, "mensaje": f"La celda destino {nueva_celda} no existe."}

            if c_destino['tipo_permitido'] != tipo_vehiculo:
                conn.rollback()
                conn.close()
                return {"success": False, "mensaje": f"Incompatibilidad: La celda {nueva_celda} es para {c_destino['tipo_permitido']}s y el vehículo es un {tipo_vehiculo}."}

            if c_destino['estado'] != 'DISPONIBLE':
                conn.rollback()
                conn.close()
                return {"success": False, "mensaje": f"La celda destino {nueva_celda} no está DISPONIBLE (Estado: {c_destino['estado']})."}

            # 3. Ocupar la nueva celda
            cursor.execute("UPDATE celda SET estado = 'OCUPADA', motivo_bloqueo = NULL WHERE codigo = ?", (nueva_celda,))

            # 4. Actualizar celda origen (disponible o mantenimiento)
            nuevo_estado_origen = 'MANTENIMIENTO' if marcar_anterior_mantenimiento else 'DISPONIBLE'
            motivo_origen = f"Reubicación hacia {nueva_celda}: {motivo or 'Avería o reordenamiento'}" if marcar_anterior_mantenimiento else None
            cursor.execute("UPDATE celda SET estado = ?, motivo_bloqueo = ? WHERE codigo = ?", (nuevo_estado_origen, motivo_origen, celda_origen))

            # 5. Actualizar el registro_acceso activo
            nota_reubicacion = f" [Reubicado de {celda_origen} a {nueva_celda} el {datetime.now().strftime('%Y-%m-%d %H:%M')}: {motivo or 'Reordenamiento'}]"
            cursor.execute("""
                UPDATE registro_acceso 
                SET celda_codigo = ?, observaciones = COALESCE(observaciones, '') || ?
                WHERE id = ?
            """, (nueva_celda, nota_reubicacion, movimiento['id']))

            # 6. Historial de ambas celdas
            cursor.execute("""
                INSERT INTO historial_celda (celda_codigo, estado_anterior, estado_nuevo, motivo, usuario_id)
                VALUES (?, 'OCUPADA', ?, ?, ?)
            """, (celda_origen, nuevo_estado_origen, f"Vehículo {placa} reubicado a {nueva_celda}", usuario_id))

            cursor.execute("""
                INSERT INTO historial_celda (celda_codigo, estado_anterior, estado_nuevo, motivo, usuario_id)
                VALUES (?, 'DISPONIBLE', 'OCUPADA', ?, ?)
            """, (nueva_celda, f"Recepción de vehículo {placa} reubicado desde {celda_origen}", usuario_id))

            conn.commit()
            conn.close()

            registrar_auditoria(usuario_id, 'CELDAS', 'REUBICACION_VEHICULO', f"Vehículo {placa} trasladado de {celda_origen} a {nueva_celda}. Origen quedó en: {nuevo_estado_origen}")
            return {
                "success": True,
                "mensaje": f"Vehículo {formatear_placa(placa)} trasladado exitosamente a la celda {nueva_celda}."
            }
        except Exception as e:
            conn.rollback()
            conn.close()
            return {"success": False, "mensaje": f"Error transaccional al reubicar: {str(e)}"}

def obtener_auditoria_sistema(limite: int = 50):
    """Retorna las últimas acciones registradas en el sistema por cualquier usuario u operador."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id, a.modulo, a.accion, a.detalle, a.ip_terminal, a.fecha,
               u.username, u.nombre_completo, u.rol
        FROM auditoria_accion a
        LEFT JOIN usuario u ON a.usuario_id = u.id
        ORDER BY a.id DESC
        LIMIT ?
    """, (limite,))
    items = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return items

def obtener_historial_celdas(limite: int = 50):
    """Retorna la bitácora de cambios y mantenimientos aplicados sobre las celdas."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT h.id, h.celda_codigo, h.estado_anterior, h.estado_nuevo, h.motivo, h.fecha_cambio,
               u.username, u.nombre_completo
        FROM historial_celda h
        LEFT JOIN usuario u ON h.usuario_id = u.id
        ORDER BY h.id DESC
        LIMIT ?
    """, (limite,))
    items = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return items

# ====================================================================
# MÓDULO 3: CONTROL DE ACCESO (INTEGRACIÓN ITERACIÓN 1 Y 2)
# ====================================================================

def consultar_vehiculo(placa_raw: str):
    """Busca un vehículo por placa, verifica su información técnica, mensualidad y estado de acceso."""
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

    # Última mensualidad registrada
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
        m['al_dia'] = (fecha_venc >= hoy) and (m['estado'] == 'ACTIVA')
        vehiculo['mensualidad'] = m
    else:
        vehiculo['mensualidad'] = None

    # Verificar si está adentro
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

def registrar_ingreso(placa_raw: str, observaciones: str = None, puerta: str = "Puerta 1 (Norte)", usuario_id: int = 2):
    """
    Valida y procesa el ingreso al parqueadero 24/7 con control transaccional concurrente,
    asignando únicamente celdas disponibles que no estén en mantenimiento ni inactivas.
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
            cursor.execute("BEGIN IMMEDIATE;")

            # Filtrar estrictamente celdas DISPONIBLES (ignora MANTENIMIENTO e INACTIVA)
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
                    "mensaje": f"Capacidad máxima alcanzada para {tipo}s o celdas en mantenimiento.",
                    "detalle": f"No hay celdas aptas y libres en este momento para {tipo.lower()}s."
                }

            # Asignación aleatoria entre las celdas disponibles
            celda_elegida = random.choice(celdas_libres)
            codigo_celda = celda_elegida['codigo']
            fecha_ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            obs_limpia = (observaciones or "").strip()
            texto_obs = f"[{puerta}] {obs_limpia}" if obs_limpia else f"[{puerta}] Sin novedades físicas al ingreso"

            # Marcar celda como OCUPADA
            cursor.execute("UPDATE celda SET estado = 'OCUPADA' WHERE codigo = ?", (codigo_celda,))

            # Registrar acceso vinculando usuario/operario responsable
            cursor.execute("""
                INSERT INTO registro_acceso (vehiculo_placa, celda_codigo, fecha_ingreso, estado, observaciones, usuario_id)
                VALUES (?, ?, ?, 'ADENTRO', ?, ?)
            """, (vehiculo['placa'], codigo_celda, fecha_ahora, texto_obs, usuario_id))

            registro_id = cursor.lastrowid
            conn.commit()
            conn.close()

            registrar_auditoria(usuario_id, 'ACCESO', 'INGRESO_VEHICULO', f"Ingreso vehículo {placa} a celda {codigo_celda} ({puerta})")
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

def registrar_salida(placa_raw: str, observaciones_salida: str = None, puerta: str = "Puerta 1 (Norte)", usuario_id: int = 2):
    """Registra la salida del vehículo y libera automáticamente su celda."""
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
        reg = cursor.fetchone()

        if not reg:
            conn.close()
            return {
                "success": False,
                "codigo_error": "NO_ADENTRO",
                "mensaje": f"El vehículo '{formatear_placa(placa)}' no figura actualmente adentro del parqueadero."
            }

        registro_id = reg['id']
        celda_codigo = reg['celda_codigo']
        fecha_ingreso_dt = datetime.strptime(reg['fecha_ingreso'], "%Y-%m-%d %H:%M:%S")
        fecha_salida_dt = datetime.now()
        fecha_salida_str = fecha_salida_dt.strftime("%Y-%m-%d %H:%M:%S")

        duracion_segundos = int((fecha_salida_dt - fecha_ingreso_dt).total_seconds())
        horas = duracion_segundos // 3600
        minutos = (duracion_segundos % 3600) // 60
        segundos = duracion_segundos % 60
        tiempo_texto = f"{horas}h {minutos}m {segundos}s"

        obs_final = reg['observaciones'] or ""
        if observaciones_salida and observaciones_salida.strip():
            obs_final += f" | Salida por {puerta}: {observaciones_salida.strip()}"

        try:
            cursor.execute("BEGIN IMMEDIATE;")

            # Cerrar registro de acceso
            cursor.execute("""
                UPDATE registro_acceso
                SET fecha_salida = ?, estado = 'FINALIZADO', observaciones = ?
                WHERE id = ?
            """, (fecha_salida_str, obs_final, registro_id))

            # Liberar celda
            cursor.execute("UPDATE celda SET estado = 'DISPONIBLE' WHERE codigo = ?", (celda_codigo,))

            conn.commit()
            conn.close()

            registrar_auditoria(usuario_id, 'ACCESO', 'SALIDA_VEHICULO', f"Salida vehículo {placa} de celda {celda_codigo} ({puerta}) - Permanencia: {tiempo_texto}")
            return {
                "success": True,
                "mensaje": f"¡Salida Exitosa! Barrera abierta en {puerta}. Celda {celda_codigo} liberada.",
                "placa": formatear_placa(placa),
                "celda_liberada": celda_codigo,
                "conductor": reg['conductor'],
                "tipo_vehiculo": reg['tipo_vehiculo'],
                "fecha_ingreso": reg['fecha_ingreso'],
                "fecha_salida": fecha_salida_str,
                "tiempo_permanencia": tiempo_texto
            }
        except Exception as e:
            conn.rollback()
            conn.close()
            return {"success": False, "mensaje": f"Error al procesar salida: {str(e)}"}

def obtener_resumen_operativo():
    """Retorna métricas operativas completas, incluyendo distribución de celdas y usuarios."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT estado, tipo_permitido, count(*) as cantidad FROM celda GROUP BY estado, tipo_permitido;")
    conteo = cursor.fetchall()

    carros_libres = 0
    carros_ocupados = 0
    carros_mantenimiento = 0
    motos_libres = 0
    motos_ocupadas = 0
    motos_mantenimiento = 0

    for c in conteo:
        tipo = c['tipo_permitido']
        est = c['estado']
        qty = c['cantidad']
        if tipo == 'CARRO':
            if est == 'DISPONIBLE': carros_libres += qty
            elif est == 'OCUPADA': carros_ocupados += qty
            elif est in ('MANTENIMIENTO', 'INACTIVA'): carros_mantenimiento += qty
        elif tipo == 'MOTO':
            if est == 'DISPONIBLE': motos_libres += qty
            elif est == 'OCUPADA': motos_ocupadas += qty
            elif est in ('MANTENIMIENTO', 'INACTIVA'): motos_mantenimiento += qty

    # Vehículos adentro actualmente
    cursor.execute("""
        SELECT 
            r.id,
            r.vehiculo_placa,
            r.celda_codigo,
            r.fecha_ingreso,
            r.observaciones,
            v.tipo_vehiculo,
            v.marca,
            v.modelo,
            v.color,
            p.nombre_completo AS conductor,
            p.telefono
        FROM registro_acceso r
        JOIN vehiculo v ON r.vehiculo_placa = v.placa
        JOIN propietario p ON v.propietario_id = p.id
        WHERE r.estado = 'ADENTRO'
        ORDER BY r.fecha_ingreso ASC
    """)
    vehiculos_adentro = [dict(r) for r in cursor.fetchall()]

    # Lista de todas las 80 celdas
    cursor.execute("""
        SELECT c.codigo, c.tipo_permitido, c.estado, c.piso, c.zona, c.motivo_bloqueo,
               r.vehiculo_placa, v.marca, v.modelo, v.color, p.nombre_completo as conductor
        FROM celda c
        LEFT JOIN registro_acceso r ON r.celda_codigo = c.codigo AND r.estado = 'ADENTRO'
        LEFT JOIN vehiculo v ON r.vehiculo_placa = v.placa
        LEFT JOIN propietario p ON v.propietario_id = p.id
        ORDER BY c.tipo_permitido ASC, c.codigo ASC
    """)
    celdas = [dict(r) for r in cursor.fetchall()]

    # Abonados registrados
    cursor.execute("""
        SELECT 
            v.placa,
            v.tipo_vehiculo,
            v.marca,
            v.modelo,
            v.color,
            p.id as propietario_id,
            p.nombre_completo,
            p.documento,
            p.telefono,
            p.email,
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
        ORDER BY v.fecha_creacion DESC
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

    # Usuarios del sistema
    cursor.execute("SELECT id, username, nombre_completo, email, rol, cargo, activo, ultimo_login FROM usuario ORDER BY id ASC")
    usuarios = [dict(r) for r in cursor.fetchall()]

    conn.close()

    total_ocupadas = carros_ocupados + motos_ocupadas
    total_libres = carros_libres + motos_libres
    total_mantenimiento = carros_mantenimiento + motos_mantenimiento

    return {
        "capacidad_total": CAPACIDAD_TOTAL,
        "total_ocupadas": total_ocupadas,
        "total_libres": total_libres,
        "total_mantenimiento": total_mantenimiento,
        "carros": {
            "total": CAPACIDAD_CARROS,
            "ocupadas": carros_ocupados,
            "libres": carros_libres,
            "mantenimiento": carros_mantenimiento
        },
        "motos": {
            "total": CAPACIDAD_MOTOS,
            "ocupadas": motos_ocupadas,
            "libres": motos_libres,
            "mantenimiento": motos_mantenimiento
        },
        "vehiculos_adentro": vehiculos_adentro,
        "total_adentro": len(vehiculos_adentro),
        "celdas": celdas,
        "abonados": abonados,
        "usuarios": usuarios
    }

def registrar_nuevo_abonado(datos: dict, usuario_id: int = 1):
    """Registra un abonado y su automotor en el padrón del parqueadero."""
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
        email = datos.get('email', f"{documento.lower()}@autoscolombia.com")
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
                """, (documento, conductor, telefono, email))
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

            registrar_auditoria(usuario_id, 'ABONADOS', 'REGISTRO_ABONADO', f"Registrado vehículo {placa} para propietario {conductor}")
            return {"success": True, "mensaje": f"Vehículo {placa} registrado con éxito."}
        except Exception as e:
            conn.close()
            return {"success": False, "error": str(e)}
