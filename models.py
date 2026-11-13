"""
Lógica del Negocio, Gestión de Usuarios (RBAC), Gestión CRUD de Celdas, Control de Acceso 24/7 y Gestión de Pagos
Sistema de Información Autos Colombia - Iteraciones 1, 2 y 3 Unificadas
Asignatura: Ingeniería de Software - PREICA2602B020053
Docente: Reinaldo Rojas | Grupo: 25
Integrantes:
  - Adriana Andrea Agudelo Agudelo
  - Camilo Alberto Palacios Turriago
  - Juan Daniel Pulgarin García
"""

import random
import re
import hashlib
from datetime import datetime, date, timedelta
from database import get_connection, db_lock

# CONSTANTES DE NEGOCIO Y TARIFAS MENSUALES REGLAMENTARIAS
TARIFA_CARRO = 250000.00
TARIFA_MOTO = 100000.00
CAPACIDAD_CARROS_BASE = 70
CAPACIDAD_MOTOS_BASE = 10
CAPACIDAD_TOTAL_BASE = 80
DIAS_MENSUALIDAD = 30

ROLES_PERMITIDOS = ("ADMIN", "OPERARIO", "AUDITOR")
ESTADOS_CELDA = ("DISPONIBLE", "OCUPADA", "MANTENIMIENTO", "INACTIVA")
METODOS_PAGO = ("EFECTIVO", "TRANSFERENCIA_BANCARIA", "CODIGO_QR", "CONSIGNACION")
METODOS_CON_REFERENCIA = ("TRANSFERENCIA_BANCARIA", "CODIGO_QR", "CONSIGNACION")

# MATRIZ OFICIAL DE CONTROL DE ACCESO BASADO EN ROLES (RBAC) - ITERACIÓN 3
PERMISOS_POR_ROL = {
    "ADMIN": {
        "descripcion": "Administrador General del Parqueadero (Control Total)",
        "permisos": [
            "OPERACION_ACCESO",
            "MANTENIMIENTO_CELDAS",
            "CRUD_CELDAS",
            "GESTION_USUARIOS",
            "GESTION_ABONADOS",
            "GESTION_PAGOS",
            "ANULAR_PAGOS",
            "CONSULTA_AUDITORIA",
        ],
    },
    "OPERARIO": {
        "descripcion": "Operador de Cabina 24/7 (Acceso, Mantenimiento, Abonados y Recaudo de Pagos)",
        "permisos": [
            "OPERACION_ACCESO",
            "MANTENIMIENTO_CELDAS",
            "GESTION_ABONADOS",
            "GESTION_PAGOS",
            "CONSULTA_AUDITORIA",
        ],
    },
    "AUDITOR": {
        "descripcion": "Auditor de Calidad y Seguridad (Supervisión de Solo Lectura)",
        "permisos": [
            "CONSULTA_AUDITORIA",
        ],
    },
}


# ====================================================================
# UTILIDADES GENERALES, SEGURIDAD CRIPTOGRÁFICA Y RBAC
# ====================================================================

def hash_password(password: str) -> str:
    """Genera hash criptográfico SHA-256 para almacenamiento seguro de credenciales."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


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
    """Registra una acción de manera inmutable en la bitácora de auditoría del sistema."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO auditoria_accion (usuario_id, modulo, accion, detalle, ip_terminal)
            VALUES (?, ?, ?, ?, ?)
            """,
            (usuario_id, modulo, accion, detalle, ip),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[AUDITORIA ERROR] No se pudo registrar auditoría: {e}")


def obtener_matriz_rbac():
    """Retorna la matriz declarativa de roles y permisos RBAC del sistema."""
    return PERMISOS_POR_ROL


def verificar_permiso(actor_id: int, permiso_requerido: str, modulo: str = "SEGURIDAD"):
    """
    Verifica en la base de datos que el usuario actor exista, esté ACTIVO y su rol posea
    el permiso requerido según la Matriz RBAC. Registra intentos no autorizados.
    """
    if not actor_id:
        return {
            "autorizado": False,
            "codigo_error": "SESION_REQUERIDA",
            "mensaje": "Debe iniciar sesión con un usuario válido para ejecutar esta operación.",
        }

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, nombre_completo, rol, activo FROM usuario WHERE id = ?",
        (actor_id,),
    )
    actor = cursor.fetchone()
    conn.close()

    if not actor:
        return {
            "autorizado": False,
            "codigo_error": "USUARIO_NO_EXISTE",
            "mensaje": "El usuario de la sesión activa no existe en el sistema.",
        }

    if not actor["activo"]:
        registrar_auditoria(
            actor["id"],
            modulo,
            "ACCESO_DENEGADO_INACTIVO",
            f"Cuenta inactiva '{actor['username']}' intentó ejecutar permiso {permiso_requerido}",
        )
        return {
            "autorizado": False,
            "codigo_error": "CUENTA_INACTIVA",
            "mensaje": f"La cuenta '{actor['username']}' se encuentra suspendida.",
        }

    rol = actor["rol"]
    permisos_rol = PERMISOS_POR_ROL.get(rol, {}).get("permisos", [])
    if permiso_requerido not in permisos_rol:
        registrar_auditoria(
            actor["id"],
            modulo,
            "ACCESO_DENEGADO_RBAC",
            f"Usuario '{actor['username']}' (Rol {rol}) sin permiso '{permiso_requerido}'",
        )
        return {
            "autorizado": False,
            "codigo_error": "PERMISO_DENEGADO",
            "mensaje": f"Acceso Denegado (RBAC): El rol '{rol}' no posee privilegios para '{permiso_requerido}'.",
        }

    return {"autorizado": True, "actor": dict(actor)}


# ====================================================================
# MÓDULO 1: GESTIÓN DE USUARIOS, ROLES Y PERMISOS (ITERACIÓN 2)
# ====================================================================

def autenticar_usuario(username: str, password_raw: str, ip: str = "Terminal Web"):
    """
    Autentica un usuario verificando su identificador y contraseña con hash SHA-256.
    Valida que la cuenta esté activa, retorna sus permisos RBAC y registra el acceso en auditoría.
    """
    if not username or not password_raw:
        return {"success": False, "mensaje": "Usuario y contraseña requeridos."}

    user_clean = username.strip().lower()
    pw_hash = hash_password(password_raw)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, username, password_hash, nombre_completo, email, rol, cargo, activo, fecha_creacion
        FROM usuario
        WHERE LOWER(username) = ?
        """,
        (user_clean,),
    )
    user = cursor.fetchone()

    if not user:
        conn.close()
        registrar_auditoria(None, "SEGURIDAD", "LOGIN_USUARIO_INEXISTENTE", f"Intento con usuario inexistente: {user_clean}", ip)
        return {"success": False, "mensaje": f"El usuario '{username}' no existe en el sistema."}

    user_dict = dict(user)

    if not user_dict["activo"]:
        conn.close()
        registrar_auditoria(
            user_dict["id"],
            "SEGURIDAD",
            "LOGIN_BLOQUEADO",
            f"Intento de ingreso con usuario inactivo: {user_clean}",
            ip,
        )
        return {
            "success": False,
            "mensaje": "Esta cuenta de usuario ha sido suspendida. Contacte al Administrador.",
        }

    if user_dict["password_hash"] != pw_hash:
        conn.close()
        registrar_auditoria(
            user_dict["id"],
            "SEGURIDAD",
            "LOGIN_FALLIDO",
            f"Contraseña errónea para: {user_clean}",
            ip,
        )
        return {"success": False, "mensaje": "Contraseña incorrecta. Verifique sus credenciales."}

    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE usuario SET ultimo_login = ? WHERE id = ?", (ahora, user_dict["id"]))
    conn.commit()
    conn.close()

    registrar_auditoria(
        user_dict["id"],
        "SEGURIDAD",
        "LOGIN_EXITOSO",
        f"Sesión iniciada por '{user_dict['username']}' con rol {user_dict['rol']}",
        ip,
    )

    del user_dict["password_hash"]
    user_dict["ultimo_login"] = ahora
    user_dict["permisos"] = PERMISOS_POR_ROL.get(user_dict["rol"], {}).get("permisos", [])
    return {
        "success": True,
        "mensaje": f"Bienvenido(a), {user_dict['nombre_completo']} ({user_dict['rol']}).",
        "usuario": user_dict,
    }


def listar_usuarios(rol_filtro: str = None, solo_activos: bool = False, busqueda: str = None):
    """Retorna la lista de usuarios del sistema con sus roles, estado y permisos."""
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
    if busqueda and busqueda.strip():
        q = f"%{busqueda.strip()}%"
        sql += " AND (username LIKE ? OR nombre_completo LIKE ? OR email LIKE ? OR cargo LIKE ?)"
        params.extend([q, q, q, q])

    sql += " ORDER BY id ASC"
    cursor.execute(sql, params)
    usuarios = []
    for r in cursor.fetchall():
        d = dict(r)
        d["permisos"] = PERMISOS_POR_ROL.get(d["rol"], {}).get("permisos", [])
        usuarios.append(d)
    conn.close()
    return usuarios


def crear_usuario(datos: dict, admin_id: int = 1):
    """Crea una nueva cuenta de usuario validando privilegios RBAC de Administrador y unicidad."""
    check = verificar_permiso(admin_id, "GESTION_USUARIOS", "USUARIOS")
    if not check["autorizado"]:
        return {"success": False, "codigo_error": check["codigo_error"], "mensaje": check["mensaje"]}

    with db_lock:
        username = (datos.get("username") or "").strip().lower()
        password = datos.get("password") or ""
        nombre = (datos.get("nombre_completo") or "").strip()
        email = (datos.get("email") or "").strip().lower()
        rol = (datos.get("rol") or "OPERARIO").strip().upper()
        cargo = (datos.get("cargo") or "Operador de Cabina").strip()

        if not username or len(username) < 3 or not re.match(r"^[a-z0-9_.-]+$", username):
            return {
                "success": False,
                "mensaje": "El nombre de usuario debe tener mínimo 3 caracteres alfanuméricos (sin espacios).",
            }
        if not password or len(password) < 6:
            return {"success": False, "mensaje": "La contraseña debe contener al menos 6 caracteres."}
        if not nombre:
            return {"success": False, "mensaje": "El nombre completo es obligatorio."}
        if not email or "@" not in email or "." not in email.split("@")[-1]:
            return {"success": False, "mensaje": "Debe suministrar un correo electrónico válido."}
        if rol not in ROLES_PERMITIDOS:
            return {"success": False, "mensaje": f"Rol no válido. Permitidos: {', '.join(ROLES_PERMITIDOS)}."}

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM usuario WHERE LOWER(username) = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return {"success": False, "mensaje": f"El nombre de usuario '{username}' ya está registrado."}

        cursor.execute("SELECT id FROM usuario WHERE LOWER(email) = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return {"success": False, "mensaje": f"El correo '{email}' ya pertenece a otro usuario."}

        pw_hash = hash_password(password)
        cursor.execute(
            """
            INSERT INTO usuario (username, password_hash, nombre_completo, email, rol, cargo, activo)
            VALUES (?, ?, ?, ?, ?, ?, 1)
            """,
            (username, pw_hash, nombre, email, rol, cargo),
        )
        nuevo_id = cursor.lastrowid
        conn.commit()
        conn.close()

        registrar_auditoria(
            admin_id,
            "USUARIOS",
            "CREAR_USUARIO",
            f"Creado usuario '{username}' con rol {rol} (ID: {nuevo_id})",
        )
        return {
            "success": True,
            "mensaje": f"Usuario '{username}' creado exitosamente con rol {rol}.",
            "usuario_id": nuevo_id,
        }


def actualizar_usuario(user_id: int, datos: dict, admin_id: int = 1):
    """Actualiza perfil, rol, cargo o estado activo de un usuario con protección de último ADMIN."""
    check = verificar_permiso(admin_id, "GESTION_USUARIOS", "USUARIOS")
    if not check["autorizado"]:
        return {"success": False, "codigo_error": check["codigo_error"], "mensaje": check["mensaje"]}

    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, username, nombre_completo, email, rol, cargo, activo FROM usuario WHERE id = ?",
            (user_id,),
        )
        actual = cursor.fetchone()
        if not actual:
            conn.close()
            return {"success": False, "mensaje": "Usuario no encontrado."}

        nombre = (datos.get("nombre_completo") or actual["nombre_completo"]).strip()
        email = (datos.get("email") or actual["email"]).strip().lower()
        rol = (datos.get("rol") or actual["rol"]).strip().upper()
        cargo = (datos.get("cargo") or actual["cargo"] or "Operador").strip()
        activo_raw = datos.get("activo", actual["activo"])
        activo = 1 if activo_raw in (1, True, "1", "true", "ACTIVO") else 0

        if rol not in ROLES_PERMITIDOS:
            conn.close()
            return {"success": False, "mensaje": f"Rol inválido: {rol}."}

        if "@" not in email:
            conn.close()
            return {"success": False, "mensaje": "El correo electrónico suministrado no es válido."}

        # Verificar unicidad de email si cambió
        cursor.execute("SELECT id FROM usuario WHERE LOWER(email) = ? AND id != ?", (email, user_id))
        if cursor.fetchone():
            conn.close()
            return {"success": False, "mensaje": f"El correo '{email}' ya está asignado a otra cuenta."}

        # Regla crítica: No degradar ni desactivar al único administrador activo del sistema
        if actual["rol"] == "ADMIN" and actual["activo"] == 1 and (activo == 0 or rol != "ADMIN"):
            cursor.execute("SELECT count(*) AS total FROM usuario WHERE rol = 'ADMIN' AND activo = 1")
            total_admins = cursor.fetchone()["total"]
            if total_admins <= 1:
                conn.close()
                return {
                    "success": False,
                    "mensaje": "Regla de Seguridad: No se puede desactivar ni cambiar el rol del único Administrador activo del sistema.",
                }

        cursor.execute(
            """
            UPDATE usuario
            SET nombre_completo = ?, email = ?, rol = ?, cargo = ?, activo = ?
            WHERE id = ?
            """,
            (nombre, email, rol, cargo, activo, user_id),
        )
        conn.commit()
        conn.close()

        registrar_auditoria(
            admin_id,
            "USUARIOS",
            "ACTUALIZAR_USUARIO",
            f"Actualizado usuario ID {user_id} ({actual['username']}): Rol={rol}, Activo={activo}",
        )
        return {"success": True, "mensaje": f"Usuario '{actual['username']}' actualizado correctamente."}


def cambiar_password(user_id: int, nueva_clave: str, admin_id: int = 1):
    """Restablece la contraseña de un usuario (requiere rol ADMIN o ser el propio usuario activo)."""
    if admin_id != user_id:
        check = verificar_permiso(admin_id, "GESTION_USUARIOS", "USUARIOS")
        if not check["autorizado"]:
            return {"success": False, "codigo_error": check["codigo_error"], "mensaje": check["mensaje"]}

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

        registrar_auditoria(
            admin_id,
            "USUARIOS",
            "CAMBIO_PASSWORD",
            f"Contraseña restablecida con hash SHA-256 para '{u['username']}' (ID: {user_id})",
        )
        return {"success": True, "mensaje": f"Contraseña actualizada exitosamente para '{u['username']}'."}


def eliminar_usuario(user_id: int, admin_id: int = 1):
    """
    Elimina una cuenta de usuario si no posee registros históricos asociados;
    si tiene trazabilidad histórica, ejecuta baja lógica (inactivación) preservando auditoría.
    """
    check = verificar_permiso(admin_id, "GESTION_USUARIOS", "USUARIOS")
    if not check["autorizado"]:
        return {"success": False, "codigo_error": check["codigo_error"], "mensaje": check["mensaje"]}

    if user_id == admin_id:
        return {"success": False, "mensaje": "No puede eliminar su propia cuenta en sesión activa."}

    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, rol, activo FROM usuario WHERE id = ?", (user_id,))
        u = cursor.fetchone()
        if not u:
            conn.close()
            return {"success": False, "mensaje": "Usuario no encontrado."}

        if u["rol"] == "ADMIN" and u["activo"] == 1:
            cursor.execute("SELECT count(*) AS total FROM usuario WHERE rol = 'ADMIN' AND activo = 1")
            if cursor.fetchone()["total"] <= 1:
                conn.close()
                return {"success": False, "mensaje": "No se puede eliminar al único Administrador activo."}

        cursor.execute("SELECT count(*) AS c FROM registro_acceso WHERE usuario_id = ?", (user_id,))
        tiene_accesos = cursor.fetchone()["c"] > 0
        cursor.execute("SELECT count(*) AS c FROM auditoria_accion WHERE usuario_id = ?", (user_id,))
        tiene_auditoria = cursor.fetchone()["c"] > 0

        if tiene_accesos or tiene_auditoria:
            cursor.execute("UPDATE usuario SET activo = 0 WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()
            registrar_auditoria(
                admin_id,
                "USUARIOS",
                "BAJA_LOGICA_USUARIO",
                f"Cuenta '{u['username']}' desactivada para preservar trazabilidad histórica",
            )
            return {
                "success": True,
                "modo": "BAJA_LOGICA",
                "mensaje": f"El usuario '{u['username']}' posee historial de auditoría; se aplicó baja lógica (INACTIVO).",
            }

        cursor.execute("DELETE FROM usuario WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        registrar_auditoria(
            admin_id,
            "USUARIOS",
            "ELIMINAR_USUARIO",
            f"Usuario '{u['username']}' (ID: {user_id}) eliminado físicamente",
        )
        return {
            "success": True,
            "modo": "ELIMINACION_FISICA",
            "mensaje": f"Usuario '{u['username']}' eliminado exitosamente del sistema.",
        }


# ====================================================================
# MÓDULO 2: GESTIÓN Y ADMINISTRACIÓN CRUD DE CELDAS (ITERACIÓN 2)
# ====================================================================

def listar_celdas_administracion(
    filtro_tipo: str = None,
    filtro_estado: str = None,
    filtro_zona: str = None,
    busqueda: str = None,
):
    """
    Retorna el inventario completo de celdas con ocupante actual, datos del propietario,
    piso, zona y motivo de bloqueo/mantenimiento.
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
    if busqueda and busqueda.strip():
        q = f"%{busqueda.strip().upper()}%"
        sql += " AND (UPPER(c.codigo) LIKE ? OR UPPER(c.zona) LIKE ? OR UPPER(COALESCE(r.vehiculo_placa, '')) LIKE ?)"
        params.extend([q, q, q])

    sql += " ORDER BY c.tipo_permitido ASC, c.codigo ASC"
    cursor.execute(sql, params)
    celdas = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return celdas


def crear_celda(datos: dict, usuario_id: int = 1):
    """
    Operación CREATE del CRUD de Celdas (exclusiva de ADMIN).
    Permite registrar una nueva celda física validando código único, tipo permitido, piso y zona.
    """
    check = verificar_permiso(usuario_id, "CRUD_CELDAS", "CELDAS")
    if not check["autorizado"]:
        return {"success": False, "codigo_error": check["codigo_error"], "mensaje": check["mensaje"]}

    with db_lock:
        codigo = (datos.get("codigo") or "").strip().upper()
        tipo = (datos.get("tipo_permitido") or "CARRO").strip().upper()
        zona = (datos.get("zona") or "ZONA ESPECIAL").strip().upper()
        motivo = (datos.get("motivo_bloqueo") or "").strip() or None
        estado = (datos.get("estado") or "DISPONIBLE").strip().upper()

        try:
            piso = int(datos.get("piso", 1))
        except (ValueError, TypeError):
            return {"success": False, "mensaje": "El número de piso debe ser un entero válido."}

        if not codigo or not re.match(r"^[A-Z0-9-]{2,10}$", codigo):
            return {"success": False, "mensaje": "Código de celda inválido (use formato ej. C-71 o M-11)."}
        if tipo not in ("CARRO", "MOTO"):
            return {"success": False, "mensaje": "Tipo permitido inválido. Use CARRO o MOTO."}
        if estado not in ("DISPONIBLE", "MANTENIMIENTO", "INACTIVA"):
            return {"success": False, "mensaje": "Estado inicial inválido para creación de celda."}
        if piso < 1 or piso > 10:
            return {"success": False, "mensaje": "El piso debe estar entre 1 y 10."}

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT codigo FROM celda WHERE codigo = ?", (codigo,))
        if cursor.fetchone():
            conn.close()
            return {"success": False, "mensaje": f"Ya existe una celda registrada con el código '{codigo}'."}

        cursor.execute(
            """
            INSERT INTO celda (codigo, tipo_permitido, estado, piso, zona, motivo_bloqueo)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (codigo, tipo, estado, piso, zona, motivo if estado != "DISPONIBLE" else None),
        )
        cursor.execute(
            """
            INSERT INTO historial_celda (celda_codigo, estado_anterior, estado_nuevo, motivo, usuario_id)
            VALUES (?, 'NUEVA', ?, ?, ?)
            """,
            (codigo, estado, f"Alta de celda en {zona} (Piso {piso})", usuario_id),
        )
        conn.commit()
        conn.close()

        registrar_auditoria(
            usuario_id,
            "CELDAS",
            "CREAR_CELDA",
            f"Creada celda {codigo} ({tipo}) en {zona}, Piso {piso}, Estado {estado}",
        )
        return {"success": True, "mensaje": f"Celda '{codigo}' creada exitosamente en {zona} (Piso {piso})."}


def actualizar_celda(codigo: str, datos: dict, usuario_id: int = 1):
    """
    Operación UPDATE del CRUD de Celdas (exclusiva de ADMIN).
    Permite editar piso, zona, tipo permitido (si no está ocupada) y observación técnica.
    """
    check = verificar_permiso(usuario_id, "CRUD_CELDAS", "CELDAS")
    if not check["autorizado"]:
        return {"success": False, "codigo_error": check["codigo_error"], "mensaje": check["mensaje"]}

    with db_lock:
        codigo_clean = (codigo or "").strip().upper()
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM celda WHERE codigo = ?", (codigo_clean,))
        actual = cursor.fetchone()
        if not actual:
            conn.close()
            return {"success": False, "mensaje": f"La celda '{codigo_clean}' no existe."}

        nuevo_tipo = (datos.get("tipo_permitido") or actual["tipo_permitido"]).strip().upper()
        nueva_zona = (datos.get("zona") or actual["zona"]).strip().upper()
        nuevo_estado = (datos.get("estado") or actual["estado"]).strip().upper()
        nuevo_motivo = datos.get("motivo_bloqueo", actual["motivo_bloqueo"])
        if isinstance(nuevo_motivo, str):
            nuevo_motivo = nuevo_motivo.strip() or None

        try:
            nuevo_piso = int(datos.get("piso", actual["piso"]))
        except (ValueError, TypeError):
            conn.close()
            return {"success": False, "mensaje": "El piso debe ser numérico."}

        if nuevo_tipo not in ("CARRO", "MOTO"):
            conn.close()
            return {"success": False, "mensaje": "Tipo permitido inválido (CARRO o MOTO)."}

        # Verificar si tiene vehículo adentro antes de cambiar tipo o bloquear
        cursor.execute(
            "SELECT vehiculo_placa FROM registro_acceso WHERE celda_codigo = ? AND estado = 'ADENTRO'",
            (codigo_clean,),
        )
        ocupante = cursor.fetchone()

        if ocupante:
            if nuevo_tipo != actual["tipo_permitido"]:
                conn.close()
                return {
                    "success": False,
                    "mensaje": f"No se puede cambiar el tipo de la celda {codigo_clean} mientras está ocupada por {ocupante['vehiculo_placa']}.",
                }
            if nuevo_estado != "OCUPADA":
                conn.close()
                return {
                    "success": False,
                    "mensaje": f"La celda {codigo_clean} está ocupada por {ocupante['vehiculo_placa']}. Reubique el vehículo antes de cambiar su estado.",
                }
        else:
            if nuevo_estado == "OCUPADA":
                conn.close()
                return {"success": False, "mensaje": "No se puede marcar OCUPADA manualmente sin un vehículo ingresado."}

        cursor.execute(
            """
            UPDATE celda
            SET tipo_permitido = ?, piso = ?, zona = ?, estado = ?, motivo_bloqueo = ?
            WHERE codigo = ?
            """,
            (
                nuevo_tipo,
                nuevo_piso,
                nueva_zona,
                nuevo_estado,
                nuevo_motivo if nuevo_estado != "DISPONIBLE" else None,
                codigo_clean,
            ),
        )

        cursor.execute(
            """
            INSERT INTO historial_celda (celda_codigo, estado_anterior, estado_nuevo, motivo, usuario_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                codigo_clean,
                actual["estado"],
                nuevo_estado,
                f"Actualización CRUD ({nueva_zona}, Piso {nuevo_piso}, Tipo {nuevo_tipo})",
                usuario_id,
            ),
        )
        conn.commit()
        conn.close()

        registrar_auditoria(
            usuario_id,
            "CELDAS",
            "ACTUALIZAR_CELDA",
            f"Editada celda {codigo_clean}: Tipo={nuevo_tipo}, Zona={nueva_zona}, Piso={nuevo_piso}, Estado={nuevo_estado}",
        )
        return {"success": True, "mensaje": f"Parámetros de la celda '{codigo_clean}' actualizados correctamente."}


def eliminar_celda(codigo: str, usuario_id: int = 1):
    """
    Operación DELETE del CRUD de Celdas (exclusiva de ADMIN).
    Impide eliminar celdas ocupadas o con registros de acceso históricos (aplicando integridad referencial).
    """
    check = verificar_permiso(usuario_id, "CRUD_CELDAS", "CELDAS")
    if not check["autorizado"]:
        return {"success": False, "codigo_error": check["codigo_error"], "mensaje": check["mensaje"]}

    with db_lock:
        codigo_clean = (codigo or "").strip().upper()
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT codigo, estado FROM celda WHERE codigo = ?", (codigo_clean,))
        celda = cursor.fetchone()
        if not celda:
            conn.close()
            return {"success": False, "mensaje": f"La celda '{codigo_clean}' no existe."}

        if celda["estado"] == "OCUPADA":
            conn.close()
            return {
                "success": False,
                "mensaje": f"Integridad Operativa: No se puede eliminar la celda '{codigo_clean}' porque está OCUPADA.",
            }

        cursor.execute("SELECT count(*) AS total FROM registro_acceso WHERE celda_codigo = ?", (codigo_clean,))
        usos = cursor.fetchone()["total"]
        if usos > 0:
            conn.close()
            return {
                "success": False,
                "mensaje": f"Integridad Referencial: La celda '{codigo_clean}' posee {usos} movimiento(s) histórico(s). Utilice el estado INACTIVA en lugar de eliminarla.",
            }

        cursor.execute("DELETE FROM celda WHERE codigo = ?", (codigo_clean,))
        conn.commit()
        conn.close()

        registrar_auditoria(
            usuario_id,
            "CELDAS",
            "ELIMINAR_CELDA",
            f"Eliminada físicamente la celda {codigo_clean} sin movimientos asociados",
        )
        return {"success": True, "mensaje": f"Celda '{codigo_clean}' eliminada físicamente del inventario."}


def cambiar_estado_celda(codigo: str, nuevo_estado: str, motivo: str = None, usuario_id: int = 1):
    """
    Cambia el estado operativo de una celda (DISPONIBLE, MANTENIMIENTO, INACTIVA).
    Regla estricta: Requiere permiso MANTENIMIENTO_CELDAS y prohíbe bloquear una celda ocupada.
    """
    check = verificar_permiso(usuario_id, "MANTENIMIENTO_CELDAS", "CELDAS")
    if not check["autorizado"]:
        return {"success": False, "codigo_error": check["codigo_error"], "mensaje": check["mensaje"]}

    with db_lock:
        codigo_clean = (codigo or "").strip().upper()
        estado_clean = (nuevo_estado or "").strip().upper()

        if estado_clean not in ("DISPONIBLE", "MANTENIMIENTO", "INACTIVA"):
            return {"success": False, "mensaje": f"Estado no admitido para cambio manual: {nuevo_estado}."}

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT codigo, estado, tipo_permitido FROM celda WHERE codigo = ?", (codigo_clean,))
        celda = cursor.fetchone()
        if not celda:
            conn.close()
            return {"success": False, "mensaje": f"La celda '{codigo_clean}' no existe."}

        estado_anterior = celda["estado"]

        cursor.execute(
            "SELECT vehiculo_placa FROM registro_acceso WHERE celda_codigo = ? AND estado = 'ADENTRO'",
            (codigo_clean,),
        )
        ocupante = cursor.fetchone()

        if ocupante and estado_clean in ("MANTENIMIENTO", "INACTIVA"):
            conn.close()
            return {
                "success": False,
                "mensaje": f"Conflicto Operativo: La celda {codigo_clean} está ocupada por el vehículo {ocupante['vehiculo_placa']}. Debe reubicarlo antes de pasarla a {estado_clean}.",
            }

        motivo_limpio = (motivo or "").strip()
        if estado_clean in ("MANTENIMIENTO", "INACTIVA") and not motivo_limpio:
            motivo_limpio = f"Orden operativa de paso a {estado_clean}"

        cursor.execute(
            """
            UPDATE celda 
            SET estado = ?, motivo_bloqueo = ? 
            WHERE codigo = ?
            """,
            (estado_clean, motivo_limpio if estado_clean != "DISPONIBLE" else None, codigo_clean),
        )

        cursor.execute(
            """
            INSERT INTO historial_celda (celda_codigo, estado_anterior, estado_nuevo, motivo, usuario_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (codigo_clean, estado_anterior, estado_clean, motivo_limpio or "Habilitación a DISPONIBLE", usuario_id),
        )

        conn.commit()
        conn.close()

        registrar_auditoria(
            usuario_id,
            "CELDAS",
            "CAMBIO_ESTADO",
            f"Celda {codigo_clean} cambió de {estado_anterior} a {estado_clean}. Motivo: {motivo_limpio or 'Habilitada'}",
        )
        return {
            "success": True,
            "mensaje": f"Celda {codigo_clean} actualizada con éxito a estado {estado_clean}.",
        }


def reubicar_vehiculo_celda(
    placa_raw: str,
    nueva_celda_codigo: str,
    motivo: str = None,
    marcar_anterior_mantenimiento: bool = False,
    usuario_id: int = 1,
):
    """
    Reubica de manera atómica un vehículo estacionado de su celda actual a una nueva celda libre
    del mismo tipo, permitiendo opcionalmente poner en mantenimiento la celda origen por avería física.
    """
    check = verificar_permiso(usuario_id, "MANTENIMIENTO_CELDAS", "CELDAS")
    if not check["autorizado"]:
        return {"success": False, "codigo_error": check["codigo_error"], "mensaje": check["mensaje"]}

    with db_lock:
        placa = limpiar_placa(placa_raw)
        nueva_celda = (nueva_celda_codigo or "").strip().upper()

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("BEGIN IMMEDIATE;")

            cursor.execute(
                """
                SELECT r.id, r.celda_codigo, v.tipo_vehiculo
                FROM registro_acceso r
                JOIN vehiculo v ON r.vehiculo_placa = v.placa
                WHERE r.vehiculo_placa = ? AND r.estado = 'ADENTRO'
                """,
                (placa,),
            )
            movimiento = cursor.fetchone()

            if not movimiento:
                conn.rollback()
                conn.close()
                return {
                    "success": False,
                    "mensaje": f"El vehículo {formatear_placa(placa)} no se encuentra dentro del parqueadero.",
                }

            celda_origen = movimiento["celda_codigo"]
            tipo_vehiculo = movimiento["tipo_vehiculo"]

            if celda_origen == nueva_celda:
                conn.rollback()
                conn.close()
                return {"success": False, "mensaje": "La nueva celda seleccionada es idéntica a la celda actual."}

            cursor.execute("SELECT tipo_permitido, estado FROM celda WHERE codigo = ?", (nueva_celda,))
            c_destino = cursor.fetchone()

            if not c_destino:
                conn.rollback()
                conn.close()
                return {"success": False, "mensaje": f"La celda destino {nueva_celda} no existe."}

            if c_destino["tipo_permitido"] != tipo_vehiculo:
                conn.rollback()
                conn.close()
                return {
                    "success": False,
                    "mensaje": f"Incompatibilidad de Categoría: La celda {nueva_celda} es exclusiva para {c_destino['tipo_permitido']} y el vehículo es {tipo_vehiculo}.",
                }

            if c_destino["estado"] != "DISPONIBLE":
                conn.rollback()
                conn.close()
                return {
                    "success": False,
                    "mensaje": f"La celda destino {nueva_celda} no está DISPONIBLE (Estado actual: {c_destino['estado']}).",
                }

            cursor.execute(
                "UPDATE celda SET estado = 'OCUPADA', motivo_bloqueo = NULL WHERE codigo = ?",
                (nueva_celda,),
            )

            nuevo_estado_origen = "MANTENIMIENTO" if marcar_anterior_mantenimiento else "DISPONIBLE"
            motivo_origen = (
                f"Reubicación hacia {nueva_celda}: {motivo or 'Avería o reordenamiento'}"
                if marcar_anterior_mantenimiento
                else None
            )
            cursor.execute(
                "UPDATE celda SET estado = ?, motivo_bloqueo = ? WHERE codigo = ?",
                (nuevo_estado_origen, motivo_origen, celda_origen),
            )

            nota_reubicacion = (
                f" [Reubicado de {celda_origen} a {nueva_celda} el "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M')}: {motivo or 'Reordenamiento'}]"
            )
            cursor.execute(
                """
                UPDATE registro_acceso 
                SET celda_codigo = ?, observaciones = COALESCE(observaciones, '') || ?
                WHERE id = ?
                """,
                (nueva_celda, nota_reubicacion, movimiento["id"]),
            )

            cursor.execute(
                """
                INSERT INTO historial_celda (celda_codigo, estado_anterior, estado_nuevo, motivo, usuario_id)
                VALUES (?, 'OCUPADA', ?, ?, ?)
                """,
                (celda_origen, nuevo_estado_origen, f"Vehículo {placa} reubicado a {nueva_celda}", usuario_id),
            )

            cursor.execute(
                """
                INSERT INTO historial_celda (celda_codigo, estado_anterior, estado_nuevo, motivo, usuario_id)
                VALUES (?, 'DISPONIBLE', 'OCUPADA', ?, ?)
                """,
                (nueva_celda, f"Recepción de vehículo {placa} reubicado desde {celda_origen}", usuario_id),
            )

            conn.commit()
            conn.close()

            registrar_auditoria(
                usuario_id,
                "CELDAS",
                "REUBICACION_VEHICULO",
                f"Vehículo {placa} trasladado de {celda_origen} a {nueva_celda}. Origen quedó en: {nuevo_estado_origen}",
            )
            return {
                "success": True,
                "celda_origen": celda_origen,
                "celda_destino": nueva_celda,
                "estado_origen": nuevo_estado_origen,
                "mensaje": f"Vehículo {formatear_placa(placa)} trasladado exitosamente de {celda_origen} a {nueva_celda}.",
            }
        except Exception as e:
            conn.rollback()
            conn.close()
            return {"success": False, "mensaje": f"Error transaccional al reubicar: {str(e)}"}


def obtener_auditoria_sistema(limite: int = 60, modulo_filtro: str = None):
    """Retorna las últimas acciones registradas en la bitácora de auditoría del sistema."""
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        SELECT a.id, a.modulo, a.accion, a.detalle, a.ip_terminal, a.fecha,
               u.username, u.nombre_completo, u.rol
        FROM auditoria_accion a
        LEFT JOIN usuario u ON a.usuario_id = u.id
        WHERE 1=1
    """
    params = []
    if modulo_filtro:
        sql += " AND a.modulo = ?"
        params.append(modulo_filtro.upper())
    sql += " ORDER BY a.id DESC LIMIT ?"
    params.append(limite)

    cursor.execute(sql, params)
    items = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return items


def obtener_historial_celdas(limite: int = 60):
    """Retorna la bitácora histórica de cambios de estado y mantenimientos aplicados sobre celdas."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT h.id, h.celda_codigo, h.estado_anterior, h.estado_nuevo, h.motivo, h.fecha_cambio,
               u.username, u.nombre_completo, u.rol
        FROM historial_celda h
        LEFT JOIN usuario u ON h.usuario_id = u.id
        ORDER BY h.id DESC
        LIMIT ?
        """,
        (limite,),
    )
    items = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return items


# ====================================================================
# MÓDULO 3: GESTIÓN CRUD DE CLIENTES ABONADOS Y VEHÍCULOS (ITERACIÓN 2)
# ====================================================================

def _denegar_si_sin_permiso(usuario_id: int, permiso: str, modulo: str):
    """Retorna diccionario de rechazo RBAC si el actor carece del permiso requerido, o None."""
    check = verificar_permiso(usuario_id, permiso, modulo)
    if not check["autorizado"]:
        return {
            "success": False,
            "codigo_error": check["codigo_error"],
            "mensaje": check["mensaje"],
        }
    return None


def _abortar_tx(conn, payload: dict):
    """Revierte la transacción activa, cierra la conexión SQLite y retorna el payload."""
    conn.rollback()
    conn.close()
    return payload


def listar_abonados(busqueda: str = None):
    """Lista los clientes abonados, sus vehículos registrados y estado de vigencia."""
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        SELECT 
            v.placa,
            v.tipo_vehiculo,
            v.marca,
            v.modelo,
            v.color,
            v.activo,
            p.id AS propietario_id,
            p.nombre_completo,
            p.documento,
            p.telefono,
            p.email,
            p.direccion,
            m.fecha_pago,
            m.fecha_vencimiento,
            m.valor_pagado,
            m.estado AS estado_mensualidad
        FROM vehiculo v
        JOIN propietario p ON v.propietario_id = p.id
        LEFT JOIN mensualidad m ON m.id = (
            SELECT id FROM mensualidad 
            WHERE vehiculo_placa = v.placa 
            ORDER BY CASE WHEN estado = 'CANCELADA' THEN 1 ELSE 0 END ASC, fecha_vencimiento DESC, id DESC LIMIT 1
        )
        WHERE 1=1
    """
    params = []
    if busqueda and busqueda.strip():
        q = f"%{busqueda.strip()}%"
        sql += " AND (v.placa LIKE ? OR p.nombre_completo LIKE ? OR p.documento LIKE ? OR v.marca LIKE ?)"
        params.extend([q.upper(), q, q, q])
    sql += " ORDER BY v.fecha_creacion DESC"

    cursor.execute(sql, params)
    abonados = []
    hoy = date.today()
    for row in cursor.fetchall():
        ab = dict(row)
        if ab["fecha_vencimiento"]:
            fv = datetime.strptime(ab["fecha_vencimiento"], "%Y-%m-%d").date()
            ab["al_dia"] = (fv >= hoy) and (ab["estado_mensualidad"] == "ACTIVA") and bool(ab["activo"])
            ab["dias_restantes"] = (fv - hoy).days
        else:
            ab["al_dia"] = False
            ab["dias_restantes"] = -99
        abonados.append(ab)
    conn.close()
    return abonados


def registrar_nuevo_abonado(datos: dict, usuario_id: int = 1):
    """Registra un nuevo cliente abonado y su automotor en el padrón del parqueadero."""
    check = verificar_permiso(usuario_id, "GESTION_ABONADOS", "ABONADOS")
    if not check["autorizado"]:
        return {"success": False, "codigo_error": check["codigo_error"], "mensaje": check["mensaje"]}

    with db_lock:
        placa = limpiar_placa(datos.get("placa"))
        if not placa or len(placa) < 5:
            return {"success": False, "mensaje": "Debe suministrar una placa válida (mínimo 5 caracteres)."}

        tipo = (datos.get("tipo_vehiculo") or "CARRO").strip().upper()
        if tipo not in ("CARRO", "MOTO"):
            return {"success": False, "mensaje": "Tipo de vehículo no válido (use CARRO o MOTO)."}

        marca = (datos.get("marca") or "Genérica").strip()
        modelo = (datos.get("modelo") or "2025").strip()
        color = (datos.get("color") or "Blanco").strip()
        conductor = (datos.get("conductor") or datos.get("nombre_completo") or "").strip()
        telefono = (datos.get("telefono") or "").strip()
        documento = (datos.get("documento") or "").strip()
        email = (datos.get("email") or "").strip()
        direccion = (datos.get("direccion") or "Medellín, Antioquia").strip()
        estado_pago = (datos.get("estado_pago") or "ACTIVA").strip().upper()

        if not conductor or not documento:
            return {"success": False, "mensaje": "El nombre completo y documento del titular son obligatorios."}
        if not telefono:
            telefono = "3000000000"
        if not email:
            email = f"{documento.lower()}@abonados.autoscolombia.com"

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT placa FROM vehiculo WHERE placa = ?", (placa,))
            if cursor.fetchone():
                conn.close()
                return {
                    "success": False,
                    "mensaje": f"El vehículo con placa '{formatear_placa(placa)}' ya se encuentra registrado en el padrón.",
                }

            cursor.execute("SELECT id FROM propietario WHERE documento = ?", (documento,))
            prop = cursor.fetchone()
            if prop:
                prop_id = prop["id"]
                cursor.execute(
                    """
                    UPDATE propietario
                    SET nombre_completo = ?, telefono = ?, email = ?, direccion = ?
                    WHERE id = ?
                    """,
                    (conductor, telefono, email, direccion, prop_id),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO propietario (documento, nombre_completo, telefono, email, direccion)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (documento, conductor, telefono, email, direccion),
                )
                prop_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO vehiculo (placa, tipo_vehiculo, marca, modelo, color, propietario_id, activo)
                VALUES (?, ?, ?, ?, ?, ?, 1)
                """,
                (placa, tipo, marca, modelo, color, prop_id),
            )

            tarifa = TARIFA_CARRO if tipo == "CARRO" else TARIFA_MOTO
            hoy = date.today()
            if estado_pago == "ACTIVA":
                fecha_pago = hoy
                fecha_venc = hoy + timedelta(days=30)
            else:
                fecha_pago = hoy - timedelta(days=40)
                fecha_venc = hoy - timedelta(days=10)
                estado_pago = "VENCIDA"

            cursor.execute(
                """
                INSERT INTO mensualidad (vehiculo_placa, fecha_pago, fecha_vencimiento, valor_pagado, estado)
                VALUES (?, ?, ?, ?, ?)
                """,
                (placa, fecha_pago.strftime("%Y-%m-%d"), fecha_venc.strftime("%Y-%m-%d"), tarifa, estado_pago),
            )
            mensualidad_id = cursor.lastrowid
            if estado_pago == "ACTIVA":
                recibo_ini = f"REC-{hoy.strftime('%Y%m%d')}-INI{mensualidad_id:03d}"
                cursor.execute(
                    """
                    INSERT INTO pago (
                        numero_recibo, vehiculo_placa, mensualidad_id, fecha_pago,
                        periodo_inicio, periodo_fin, meses_pagados, valor_pagado,
                        metodo_pago, referencia_comprobante, tipo_aplicacion, estado, observaciones, usuario_id
                    )
                    VALUES (?, ?, ?, ?, ?, ?, 1, ?, 'EFECTIVO', ?, 'INICIAL_REACTIVACION', 'CONFIRMADO', 'Suscripción inicial de abonado', ?)
                    """,
                    (
                        recibo_ini,
                        placa,
                        mensualidad_id,
                        fecha_pago.strftime("%Y-%m-%d"),
                        fecha_pago.strftime("%Y-%m-%d"),
                        fecha_venc.strftime("%Y-%m-%d"),
                        tarifa,
                        f"INI-{placa}",
                        usuario_id,
                    ),
                )

            conn.commit()
            conn.close()

            registrar_auditoria(
                usuario_id,
                "ABONADOS",
                "CREAR_ABONADO",
                f"Registrado vehículo {placa} ({tipo}) para titular {conductor} (Doc: {documento})",
            )
            return {
                "success": True,
                "mensaje": f"Abonado '{conductor}' y vehículo '{formatear_placa(placa)}' registrados exitosamente.",
            }
        except Exception as e:
            conn.close()
            return {"success": False, "mensaje": f"Error al registrar abonado: {str(e)}"}


def actualizar_abonado_vehiculo(placa_raw: str, datos: dict, usuario_id: int = 1):
    """
    Actualiza los datos personales del titular abonado y/o las características físicas del vehículo
    (marca, modelo, color, tipo, estado activo).
    """
    check = verificar_permiso(usuario_id, "GESTION_ABONADOS", "ABONADOS")
    if not check["autorizado"]:
        return {"success": False, "codigo_error": check["codigo_error"], "mensaje": check["mensaje"]}

    with db_lock:
        placa = limpiar_placa(placa_raw)
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT v.placa, v.tipo_vehiculo, v.marca, v.modelo, v.color, v.activo, v.propietario_id,
                   p.documento, p.nombre_completo, p.telefono, p.email, p.direccion
            FROM vehiculo v
            JOIN propietario p ON v.propietario_id = p.id
            WHERE v.placa = ?
            """,
            (placa,),
        )
        actual = cursor.fetchone()
        if not actual:
            conn.close()
            return {"success": False, "mensaje": f"No se encontró el vehículo con placa '{formatear_placa(placa)}'."}

        nuevo_tipo = (datos.get("tipo_vehiculo") or actual["tipo_vehiculo"]).strip().upper()
        nueva_marca = (datos.get("marca") or actual["marca"]).strip()
        nuevo_modelo = (datos.get("modelo") or actual["modelo"]).strip()
        nuevo_color = (datos.get("color") or actual["color"]).strip()
        activo_raw = datos.get("activo", actual["activo"])
        nuevo_activo = 1 if activo_raw in (1, True, "1", "true", "ACTIVO") else 0

        nuevo_nombre = (datos.get("nombre_completo") or datos.get("conductor") or actual["nombre_completo"]).strip()
        nuevo_tel = (datos.get("telefono") or actual["telefono"]).strip()
        nuevo_email = (datos.get("email") or actual["email"] or "").strip()
        nueva_dir = (datos.get("direccion") or actual["direccion"] or "").strip()

        # Verificar si el vehículo está actualmente adentro antes de inactivarlo o cambiarle categoría
        cursor.execute(
            "SELECT celda_codigo FROM registro_acceso WHERE vehiculo_placa = ? AND estado = 'ADENTRO'",
            (placa,),
        )
        adentro = cursor.fetchone()
        if adentro and (nuevo_activo == 0 or nuevo_tipo != actual["tipo_vehiculo"]):
            conn.close()
            return {
                "success": False,
                "mensaje": f"El vehículo {formatear_placa(placa)} está estacionado en {adentro['celda_codigo']}. Registre primero su salida antes de inactivarlo o cambiar su categoría.",
            }

        cursor.execute(
            """
            UPDATE propietario
            SET nombre_completo = ?, telefono = ?, email = ?, direccion = ?
            WHERE id = ?
            """,
            (nuevo_nombre, nuevo_tel, nuevo_email, nueva_dir, actual["propietario_id"]),
        )
        cursor.execute(
            """
            UPDATE vehiculo
            SET tipo_vehiculo = ?, marca = ?, modelo = ?, color = ?, activo = ?
            WHERE placa = ?
            """,
            (nuevo_tipo, nueva_marca, nuevo_modelo, nuevo_color, nuevo_activo, placa),
        )
        conn.commit()
        conn.close()

        registrar_auditoria(
            usuario_id,
            "ABONADOS",
            "ACTUALIZAR_ABONADO",
            f"Actualizados datos de {placa}: Titular={nuevo_nombre}, Vehículo={nueva_marca} {nuevo_modelo} ({nuevo_color}), Activo={nuevo_activo}",
        )
        return {
            "success": True,
            "mensaje": f"Datos del abonado y vehículo '{formatear_placa(placa)}' actualizados correctamente.",
        }


# ====================================================================
# MÓDULO 4: CONTROL DE ACCESO (INTEGRACIÓN ITERACIONES 1 Y 2)
# ====================================================================

def consultar_vehiculo(placa_raw: str):
    """Busca un vehículo por placa, verifica su información técnica, titular, mensualidad y estado de acceso."""
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
        p.documento AS propietario_doc,
        p.email AS propietario_email
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

    query_mensualidad = """
    SELECT id, fecha_pago, fecha_vencimiento, valor_pagado, estado
    FROM mensualidad
    WHERE vehiculo_placa = ?
    ORDER BY CASE WHEN estado = 'CANCELADA' THEN 1 ELSE 0 END ASC, fecha_vencimiento DESC, id DESC
    LIMIT 1
    """
    cursor.execute(query_mensualidad, (vehiculo["placa"],))
    mensualidad_row = cursor.fetchone()

    hoy = date.today()
    if mensualidad_row:
        m = dict(mensualidad_row)
        fecha_venc = datetime.strptime(m["fecha_vencimiento"], "%Y-%m-%d").date()
        m["dias_restantes"] = (fecha_venc - hoy).days
        m["al_dia"] = (fecha_venc >= hoy) and (m["estado"] == "ACTIVA") and bool(vehiculo["activo"])
        vehiculo["mensualidad"] = m
    else:
        vehiculo["mensualidad"] = None

    query_adentro = """
    SELECT r.id, r.celda_codigo, r.fecha_ingreso, r.estado, r.observaciones
    FROM registro_acceso r
    WHERE r.vehiculo_placa = ? AND r.estado = 'ADENTRO'
    ORDER BY r.fecha_ingreso DESC, r.id DESC
    LIMIT 1
    """
    cursor.execute(query_adentro, (vehiculo["placa"],))
    adentro_row = cursor.fetchone()
    vehiculo["esta_adentro"] = adentro_row is not None
    vehiculo["registro_actual"] = dict(adentro_row) if adentro_row else None

    conn.close()
    return vehiculo


def registrar_ingreso(placa_raw: str, observaciones: str = None, puerta: str = "Puerta 1 (Norte)", usuario_id: int = 2):
    """
    Valida rol operativo RBAC y procesa el ingreso al parqueadero 24/7 bajo control transaccional concurrente,
    asignando únicamente celdas DISPONIBLES (excluyendo OCUPADA, MANTENIMIENTO e INACTIVA).
    """
    check = verificar_permiso(usuario_id, "OPERACION_ACCESO", "ACCESO")
    if not check["autorizado"]:
        return {"success": False, "codigo_error": check["codigo_error"], "mensaje": check["mensaje"]}

    with db_lock:
        placa = limpiar_placa(placa_raw)
        vehiculo = consultar_vehiculo(placa)

        if not vehiculo:
            return {
                "success": False,
                "codigo_error": "NO_REGISTRADO",
                "mensaje": f"El vehículo con placa '{formatear_placa(placa)}' NO se encuentra registrado en el padrón de abonados.",
                "detalle": "El parqueadero opera exclusivamente bajo modalidad de mensualidad.",
            }

        if not vehiculo.get("activo", 1):
            return {
                "success": False,
                "codigo_error": "VEHICULO_INACTIVO",
                "mensaje": f"Acceso Denegado: El vehículo '{formatear_placa(placa)}' se encuentra INACTIVO en el padrón.",
                "detalle": "Contacte al Administrador o actualice el estado del abonado.",
            }

        if vehiculo["esta_adentro"]:
            celda = vehiculo["registro_actual"]["celda_codigo"]
            return {
                "success": False,
                "codigo_error": "YA_ADENTRO",
                "mensaje": f"Control de duplicidad: El vehículo '{formatear_placa(placa)}' ya figura ADENTRO en la celda {celda}.",
                "detalle": "No se puede registrar doble ingreso sin haber registrado antes su salida.",
            }

        mensualidad = vehiculo["mensualidad"]
        if not mensualidad or not mensualidad["al_dia"]:
            fecha_v = mensualidad["fecha_vencimiento"] if mensualidad else "Sin registro"
            return {
                "success": False,
                "codigo_error": "MENSUALIDAD_VENCIDA",
                "mensaje": f"Acceso Denegado: La mensualidad del vehículo '{formatear_placa(placa)}' está VENCIDA ({fecha_v}).",
                "detalle": "No existe periodo de gracia. El contrato debe estar vigente para autorizar el ingreso.",
                "vehiculo": vehiculo,
            }

        tipo = vehiculo["tipo_vehiculo"]
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("BEGIN IMMEDIATE;")

            cursor.execute(
                """
                SELECT codigo, piso, zona 
                FROM celda 
                WHERE tipo_permitido = ? AND estado = 'DISPONIBLE'
                """,
                (tipo,),
            )
            celdas_libres = [dict(r) for r in cursor.fetchall()]

            if not celdas_libres:
                conn.rollback()
                conn.close()
                return {
                    "success": False,
                    "codigo_error": "SIN_CUPO",
                    "mensaje": f"Capacidad máxima alcanzada para {tipo}s (o celdas restantes en mantenimiento).",
                    "detalle": f"No existen celdas DISPONIBLES en este momento para {tipo.lower()}s.",
                }

            celda_elegida = random.choice(celdas_libres)
            codigo_celda = celda_elegida["codigo"]
            fecha_ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            obs_limpia = (observaciones or "").strip()
            texto_obs = f"[{puerta}] {obs_limpia}" if obs_limpia else f"[{puerta}] Sin novedades físicas al ingreso"

            cursor.execute("UPDATE celda SET estado = 'OCUPADA' WHERE codigo = ?", (codigo_celda,))

            cursor.execute(
                """
                INSERT INTO registro_acceso (vehiculo_placa, celda_codigo, fecha_ingreso, estado, observaciones, usuario_id)
                VALUES (?, ?, ?, 'ADENTRO', ?, ?)
                """,
                (vehiculo["placa"], codigo_celda, fecha_ahora, texto_obs, usuario_id),
            )

            registro_id = cursor.lastrowid
            conn.commit()
            conn.close()

            registrar_auditoria(
                usuario_id,
                "ACCESO",
                "INGRESO_VEHICULO",
                f"Ingreso autorizado vehículo {placa} en celda {codigo_celda} ({puerta})",
            )
            return {
                "success": True,
                "registro_id": registro_id,
                "mensaje": f"¡Barrera Abierta en {puerta}! Ingreso autorizado para {formatear_placa(placa)}.",
                "celda_asignada": codigo_celda,
                "zona": celda_elegida["zona"],
                "piso": celda_elegida["piso"],
                "fecha_ingreso": fecha_ahora,
                "observaciones": texto_obs,
                "vehiculo": vehiculo,
            }
        except Exception as e:
            conn.rollback()
            conn.close()
            return {
                "success": False,
                "codigo_error": "ERROR_TRANSACCION",
                "mensaje": f"Error de concurrencia al asignar celda: {str(e)}",
            }


def registrar_novedad_vehiculo(placa_raw: str, novedad: str, usuario_id: int = 2):
    """Agrega una novedad u observación de seguridad sobre un vehículo actualmente estacionado (HU-03)."""
    check = verificar_permiso(usuario_id, "OPERACION_ACCESO", "ACCESO")
    if not check["autorizado"]:
        return {"success": False, "codigo_error": check["codigo_error"], "mensaje": check["mensaje"]}

    if not novedad or not novedad.strip():
        return {"success": False, "mensaje": "Debe describir la novedad física u operativa."}

    with db_lock:
        placa = limpiar_placa(placa_raw)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, celda_codigo, observaciones FROM registro_acceso WHERE vehiculo_placa = ? AND estado = 'ADENTRO'",
            (placa,),
        )
        reg = cursor.fetchone()
        if not reg:
            conn.close()
            return {"success": False, "mensaje": f"El vehículo {formatear_placa(placa)} no está estacionado actualmente."}

        marca_tiempo = datetime.now().strftime("%H:%M")
        nueva_obs = (reg["observaciones"] or "") + f" | [Novedad {marca_tiempo}]: {novedad.strip()}"
        cursor.execute("UPDATE registro_acceso SET observaciones = ? WHERE id = ?", (nueva_obs, reg["id"]))
        conn.commit()
        conn.close()

        registrar_auditoria(
            usuario_id,
            "ACCESO",
            "NOVEDAD_VEHICULO",
            f"Novedad registrada sobre {placa} (Celda {reg['celda_codigo']}): {novedad.strip()}",
        )
        return {"success": True, "mensaje": f"Novedad registrada en la bitácora del vehículo {formatear_placa(placa)}."}


def registrar_salida(
    placa_raw: str,
    observaciones_salida: str = None,
    puerta: str = "Puerta 1 (Norte)",
    usuario_id: int = 2,
):
    """Registra la salida del vehículo, calcula permanencia exacta y libera inmediatamente su celda."""
    check = verificar_permiso(usuario_id, "OPERACION_ACCESO", "ACCESO")
    if not check["autorizado"]:
        return {"success": False, "codigo_error": check["codigo_error"], "mensaje": check["mensaje"]}

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
                "mensaje": f"El vehículo '{formatear_placa(placa)}' no figura actualmente adentro del parqueadero.",
            }

        registro_id = reg["id"]
        celda_codigo = reg["celda_codigo"]
        fecha_ingreso_dt = datetime.strptime(reg["fecha_ingreso"], "%Y-%m-%d %H:%M:%S")
        fecha_salida_dt = datetime.now()
        fecha_salida_str = fecha_salida_dt.strftime("%Y-%m-%d %H:%M:%S")

        duracion_segundos = max(0, int((fecha_salida_dt - fecha_ingreso_dt).total_seconds()))
        horas = duracion_segundos // 3600
        minutos = (duracion_segundos % 3600) // 60
        segundos = duracion_segundos % 60
        tiempo_texto = f"{horas}h {minutos}m {segundos}s"

        obs_final = reg["observaciones"] or ""
        if observaciones_salida and observaciones_salida.strip():
            obs_final += f" | Salida por {puerta}: {observaciones_salida.strip()}"

        try:
            cursor.execute("BEGIN IMMEDIATE;")

            cursor.execute(
                """
                UPDATE registro_acceso
                SET fecha_salida = ?, estado = 'FINALIZADO', observaciones = ?
                WHERE id = ?
                """,
                (fecha_salida_str, obs_final, registro_id),
            )

            cursor.execute("UPDATE celda SET estado = 'DISPONIBLE', motivo_bloqueo = NULL WHERE codigo = ?", (celda_codigo,))

            conn.commit()
            conn.close()

            registrar_auditoria(
                usuario_id,
                "ACCESO",
                "SALIDA_VEHICULO",
                f"Salida vehículo {placa} liberando celda {celda_codigo} ({puerta}) - Permanencia: {tiempo_texto}",
            )
            return {
                "success": True,
                "mensaje": f"¡Salida Exitosa! Barrera abierta en {puerta}. Celda {celda_codigo} liberada.",
                "placa": formatear_placa(placa),
                "celda_liberada": celda_codigo,
                "conductor": reg["conductor"],
                "tipo_vehiculo": reg["tipo_vehiculo"],
                "fecha_ingreso": reg["fecha_ingreso"],
                "fecha_salida": fecha_salida_str,
                "tiempo_permanencia": tiempo_texto,
            }
        except Exception as e:
            conn.rollback()
            conn.close()
            return {"success": False, "mensaje": f"Error al procesar salida: {str(e)}"}


def obtener_resumen_operativo():
    """Retorna métricas operativas en tiempo real de celdas, vehículos estacionados, abonados y usuarios."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT estado, tipo_permitido, count(*) AS cantidad FROM celda GROUP BY estado, tipo_permitido;")
    conteo = cursor.fetchall()

    carros_libres = carros_ocupados = carros_mantenimiento = 0
    motos_libres = motos_ocupadas = motos_mantenimiento = 0

    for c in conteo:
        tipo = c["tipo_permitido"]
        est = c["estado"]
        qty = c["cantidad"]
        if tipo == "CARRO":
            if est == "DISPONIBLE":
                carros_libres += qty
            elif est == "OCUPADA":
                carros_ocupados += qty
            elif est in ("MANTENIMIENTO", "INACTIVA"):
                carros_mantenimiento += qty
        elif tipo == "MOTO":
            if est == "DISPONIBLE":
                motos_libres += qty
            elif est == "OCUPADA":
                motos_ocupadas += qty
            elif est in ("MANTENIMIENTO", "INACTIVA"):
                motos_mantenimiento += qty

    total_carros = carros_libres + carros_ocupados + carros_mantenimiento
    total_motos = motos_libres + motos_ocupadas + motos_mantenimiento
    capacidad_total = total_carros + total_motos

    cursor.execute(
        """
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
        """
    )
    vehiculos_adentro = [dict(r) for r in cursor.fetchall()]

    cursor.execute(
        """
        SELECT c.codigo, c.tipo_permitido, c.estado, c.piso, c.zona, c.motivo_bloqueo,
               r.vehiculo_placa, v.marca, v.modelo, v.color, p.nombre_completo AS conductor
        FROM celda c
        LEFT JOIN registro_acceso r ON r.celda_codigo = c.codigo AND r.estado = 'ADENTRO'
        LEFT JOIN vehiculo v ON r.vehiculo_placa = v.placa
        LEFT JOIN propietario p ON v.propietario_id = p.id
        ORDER BY c.tipo_permitido ASC, c.codigo ASC
        """
    )
    celdas = [dict(r) for r in cursor.fetchall()]
    conn.close()

    abonados = listar_abonados()
    usuarios = listar_usuarios()
    pagos_info = obtener_estado_pagos_y_caja()

    total_ocupadas = carros_ocupados + motos_ocupadas
    total_libres = carros_libres + motos_libres
    total_mantenimiento = carros_mantenimiento + motos_mantenimiento

    return {
        "capacidad_total": capacidad_total,
        "total_ocupadas": total_ocupadas,
        "total_libres": total_libres,
        "total_mantenimiento": total_mantenimiento,
        "carros": {
            "total": total_carros,
            "ocupadas": carros_ocupados,
            "libres": carros_libres,
            "mantenimiento": carros_mantenimiento,
        },
        "motos": {
            "total": total_motos,
            "ocupadas": motos_ocupadas,
            "libres": motos_libres,
            "mantenimiento": motos_mantenimiento,
        },
        "vehiculos_adentro": vehiculos_adentro,
        "total_adentro": len(vehiculos_adentro),
        "celdas": celdas,
        "abonados": abonados,
        "usuarios": usuarios,
        "pagos_resumen": {
            "flujo_caja": pagos_info["flujo_caja"],
            "conteo_cartera": pagos_info["conteo_cartera"],
        },
        "rbac": PERMISOS_POR_ROL,
    }


# ====================================================================
# MÓDULO 5: GESTIÓN DE PAGOS, MENSUALIDADES Y FLUJO DE CAJA (ITERACIÓN 3)
# ====================================================================

def _tarifa_por_tipo(tipo_vehiculo: str) -> float:
    return TARIFA_CARRO if tipo_vehiculo == "CARRO" else TARIFA_MOTO


def _parsear_fecha_pago(fecha_pago_str: str = None):
    """Valida formato YYYY-MM-DD y prohíbe explícitamente pagos con fecha futura."""
    hoy = date.today()
    if not fecha_pago_str or not str(fecha_pago_str).strip():
        return {"ok": True, "fecha": hoy}
    try:
        fecha_dt = datetime.strptime(str(fecha_pago_str).strip(), "%Y-%m-%d").date()
    except ValueError:
        return {
            "ok": False,
            "codigo_error": "FECHA_INVALIDA",
            "mensaje": "Formato de fecha inválido. Use el estándar AAAA-MM-DD.",
        }
    if fecha_dt > hoy:
        return {
            "ok": False,
            "codigo_error": "FECHA_FUTURA",
            "mensaje": f"No se permiten pagos con fecha futura ({fecha_dt.strftime('%Y-%m-%d')} > {hoy.strftime('%Y-%m-%d')}).",
        }
    return {"ok": True, "fecha": fecha_dt}


def _calcular_nueva_vigencia(mensualidad_row, fecha_pago: date, meses_pagados: int, es_reactivacion: bool = False):
    """
    Calcula la nueva fecha de vencimiento (corte) separando estrictamente fecha_pago y vigencia:
      - Pago Anticipado (fecha_pago < corte_anterior): mantiene días restantes y suma 30*meses días al corte.
      - Pago Puntual (fecha_pago == corte_anterior): suma 30*meses días exactos desde el corte.
      - Mora Consecutiva (fecha_pago > corte_anterior): suma 30*meses días desde el corte anterior (no corre la fecha).
      - Reactivación o Contrato Nuevo: inicia desde fecha_pago + 30*meses días.
    """
    hoy = date.today()
    dias_adicionales = DIAS_MENSUALIDAD * meses_pagados

    if es_reactivacion or mensualidad_row is None or mensualidad_row["estado"] == "CANCELADA":
        periodo_inicio = fecha_pago
        nueva_fecha_venc = fecha_pago + timedelta(days=dias_adicionales)
        tipo_aplicacion = "INICIAL_REACTIVACION"
        corte_anterior = None
    else:
        v_ant = datetime.strptime(mensualidad_row["fecha_vencimiento"], "%Y-%m-%d").date()
        corte_anterior = v_ant
        periodo_inicio = v_ant + timedelta(days=1)
        nueva_fecha_venc = v_ant + timedelta(days=dias_adicionales)
        if fecha_pago < v_ant:
            tipo_aplicacion = "PAGO_ANTICIPADO"
        elif fecha_pago == v_ant:
            tipo_aplicacion = "PAGO_PUNTUAL"
        else:
            tipo_aplicacion = "MORA_CONSECUTIVA"

    nuevo_estado = "ACTIVA" if nueva_fecha_venc >= hoy else "VENCIDA"
    return {
        "corte_anterior": corte_anterior.strftime("%Y-%m-%d") if corte_anterior else None,
        "periodo_inicio": periodo_inicio.strftime("%Y-%m-%d"),
        "nueva_fecha_vencimiento": nueva_fecha_venc.strftime("%Y-%m-%d"),
        "tipo_aplicacion": tipo_aplicacion,
        "nuevo_estado": nuevo_estado,
    }


def _generar_numero_recibo(cursor, fecha_pago: date) -> str:
    cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 AS sig FROM pago")
    sig = cursor.fetchone()["sig"]
    return f"REC-{fecha_pago.strftime('%Y%m%d')}-{sig:04d}"


def _construir_explicacion_vigencia(calculo: dict, fecha_pago: date, meses: int) -> str:
    tipo = calculo["tipo_aplicacion"]
    corte_ant = calculo["corte_anterior"]
    nuevo_corte = calculo["nueva_fecha_vencimiento"]
    fp_str = fecha_pago.strftime("%Y-%m-%d")

    if tipo == "PAGO_ANTICIPADO":
        dias_restantes = (datetime.strptime(corte_ant, "%Y-%m-%d").date() - fecha_pago).days
        return (
            f"PAGO ANTICIPADO: El corte vigente es {corte_ant} ({dias_restantes} días restantes). "
            f"Al pagar el {fp_str}, no pierde sus días acumulados; se suman {meses * DIAS_MENSUALIDAD} días "
            f"consecutivos desde {corte_ant} hasta el {nuevo_corte}."
        )
    if tipo == "PAGO_PUNTUAL":
        return (
            f"PAGO PUNTUAL: Pago realizado exactamente en la fecha de vencimiento ({corte_ant}). "
            f"La vigencia se extiende hasta el {nuevo_corte}."
        )
    if tipo == "MORA_CONSECUTIVA":
        dias_mora = (fecha_pago - datetime.strptime(corte_ant, "%Y-%m-%d").date()).days
        return (
            f"MORA CONSECUTIVA ({dias_mora} días de atraso): La mensualidad venció el {corte_ant}. "
            f"Para evitar corrimiento de fechas, los {meses * DIAS_MENSUALIDAD} días corren consecutivamente "
            f"desde {corte_ant} hasta el {nuevo_corte} (Estado resultante: {calculo['nuevo_estado']})."
        )
    return (
        f"CONTRATO NUEVO / REACTIVACIÓN: Vigencia calculada desde la fecha de pago {fp_str} "
        f"por {meses * DIAS_MENSUALIDAD} días hasta el {nuevo_corte}."
    )


def previsualizar_pago_mensualidad(
    placa_raw: str,
    fecha_pago_str: str = None,
    meses_pagados: int = 1,
    es_reactivacion: bool = False,
):
    """Previsualiza la regla de fechas y monto reglamentario antes de confirmar el pago."""
    placa = limpiar_placa(placa_raw)
    if not placa:
        return {"success": False, "mensaje": "Debe suministrar una placa válida."}

    try:
        meses = int(meses_pagados)
    except (ValueError, TypeError):
        return {"success": False, "mensaje": "La cantidad de meses debe ser un entero entre 1 y 12."}
    if meses < 1 or meses > 12:
        return {"success": False, "mensaje": "La cantidad de meses debe estar entre 1 y 12."}

    fecha_res = _parsear_fecha_pago(fecha_pago_str)
    if not fecha_res["ok"]:
        return {"success": False, "codigo_error": fecha_res["codigo_error"], "mensaje": fecha_res["mensaje"]}
    fecha_pago = fecha_res["fecha"]

    vehiculo = consultar_vehiculo(placa)
    if not vehiculo:
        return {"success": False, "codigo_error": "NO_REGISTRADO", "mensaje": f"Vehículo '{formatear_placa(placa)}' no encontrado."}

    tarifa = _tarifa_por_tipo(vehiculo["tipo_vehiculo"])
    valor_total = tarifa * meses
    calculo = _calcular_nueva_vigencia(vehiculo["mensualidad"], fecha_pago, meses, es_reactivacion=es_reactivacion)

    return {
        "success": True,
        "placa": vehiculo["placa"],
        "placa_visual": formatear_placa(vehiculo["placa"]),
        "activo": bool(vehiculo["activo"]),
        "tipo_vehiculo": vehiculo["tipo_vehiculo"],
        "propietario_nombre": vehiculo["propietario_nombre"],
        "tarifa_mensual": tarifa,
        "meses_pagados": meses,
        "valor_total": valor_total,
        "fecha_pago": fecha_pago.strftime("%Y-%m-%d"),
        **calculo,
        "explicacion": _construir_explicacion_vigencia(calculo, fecha_pago, meses),
    }


def _validar_datos_pago(datos: dict):
    """Valida método de pago, referencia obligatoria en canales electrónicos, meses y fecha."""
    placa = limpiar_placa(datos.get("placa"))
    if not placa:
        return {"ok": False, "codigo_error": "PLACA_REQUERIDA", "mensaje": "Debe indicar la placa del vehículo."}

    fecha_res = _parsear_fecha_pago(datos.get("fecha_pago"))
    if not fecha_res["ok"]:
        return fecha_res

    metodo = (datos.get("metodo_pago") or "EFECTIVO").strip().upper()
    if metodo not in METODOS_PAGO:
        return {
            "ok": False,
            "codigo_error": "METODO_INVALIDO",
            "mensaje": f"Método de pago no válido. Permitidos: {', '.join(METODOS_PAGO)}.",
        }

    referencia = (datos.get("referencia_comprobante") or "").strip()
    if metodo in METODOS_CON_REFERENCIA and not referencia:
        return {
            "ok": False,
            "codigo_error": "REFERENCIA_REQUERIDA",
            "mensaje": f"El método {metodo} exige registrar el número de comprobante o referencia.",
        }

    try:
        meses = int(datos.get("meses_pagados", 1))
    except (ValueError, TypeError):
        return {"ok": False, "codigo_error": "MESES_INVALIDOS", "mensaje": "Cantidad de meses inválida."}
    if meses < 1 or meses > 12:
        return {"ok": False, "codigo_error": "MESES_INVALIDOS", "mensaje": "Debe pagar entre 1 y 12 mensualidades."}

    return {
        "ok": True,
        "placa": placa,
        "fecha_pago": fecha_res["fecha"],
        "metodo_pago": metodo,
        "referencia": referencia or "CAJA-DIRECTA",
        "meses": meses,
        "observaciones": (datos.get("observaciones") or "").strip(),
        "es_reactivacion": bool(datos.get("es_reactivacion", False)),
    }


def _validar_monto_pago(valor_recibido_raw, tipo_vehiculo: str, meses: int):
    """Valida que el monto recibido coincida exactamente con la tarifa reglamentaria."""
    tarifa = _tarifa_por_tipo(tipo_vehiculo)
    valor_esperado = tarifa * meses
    if valor_recibido_raw is None or str(valor_recibido_raw).strip() == "":
        return {"ok": True, "valor": valor_esperado}
    try:
        valor_recibido = float(valor_recibido_raw)
    except (ValueError, TypeError):
        return {"ok": False, "codigo_error": "MONTO_INVALIDO", "mensaje": "Valor pagado no es numérico."}
    if valor_recibido <= 0 or abs(valor_recibido - valor_esperado) > 0.01:
        return {
            "ok": False,
            "codigo_error": "MONTO_INVALIDO",
            "mensaje": f"Valor incorrecto para {tipo_vehiculo} ({meses} mes/es). Tarifa exacta: ${valor_esperado:,.0f} COP.",
        }
    return {"ok": True, "valor": valor_recibido}


def _persistir_mensualidad_y_pago(cursor, val: dict, calculo: dict, valor_recibido: float, m_actual, usuario_id: int):
    """Actualiza o crea la mensualidad activa e inserta el recibo inmutable en pago."""
    fecha_pago_str = val["fecha_pago"].strftime("%Y-%m-%d")
    if val["es_reactivacion"]:
        cursor.execute("UPDATE vehiculo SET activo = 1 WHERE placa = ?", (val["placa"],))

    if m_actual and m_actual["estado"] != "CANCELADA":
        mensualidad_id = m_actual["id"]
        cursor.execute(
            """
            UPDATE mensualidad
            SET fecha_pago = ?, fecha_vencimiento = ?, valor_pagado = ?, estado = ?
            WHERE id = ?
            """,
            (fecha_pago_str, calculo["nueva_fecha_vencimiento"], valor_recibido, calculo["nuevo_estado"], mensualidad_id),
        )
    else:
        cursor.execute(
            """
            INSERT INTO mensualidad (vehiculo_placa, fecha_pago, fecha_vencimiento, valor_pagado, estado)
            VALUES (?, ?, ?, ?, ?)
            """,
            (val["placa"], fecha_pago_str, calculo["nueva_fecha_vencimiento"], valor_recibido, calculo["nuevo_estado"]),
        )
        mensualidad_id = cursor.lastrowid

    numero_recibo = _generar_numero_recibo(cursor, val["fecha_pago"])
    obs = val["observaciones"] or _construir_explicacion_vigencia(calculo, val["fecha_pago"], val["meses"])
    cursor.execute(
        """
        INSERT INTO pago (
            numero_recibo, vehiculo_placa, mensualidad_id, fecha_pago,
            periodo_inicio, periodo_fin, meses_pagados, valor_pagado,
            metodo_pago, referencia_comprobante, tipo_aplicacion, estado, observaciones, usuario_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'CONFIRMADO', ?, ?)
        """,
        (
            numero_recibo,
            val["placa"],
            mensualidad_id,
            fecha_pago_str,
            calculo["periodo_inicio"],
            calculo["nueva_fecha_vencimiento"],
            val["meses"],
            valor_recibido,
            val["metodo_pago"],
            val["referencia"],
            calculo["tipo_aplicacion"],
            obs,
            usuario_id,
        ),
    )
    return numero_recibo, cursor.lastrowid


def registrar_pago_mensualidad(datos: dict, usuario_id: int = 2):
    """
    Registra directamente en plataforma un pago de mensualidad (Operario o Admin),
    sin pasarela externa, aplicando la lógica consecutiva de fechas de corte.
    """
    denegado = _denegar_si_sin_permiso(usuario_id, "GESTION_PAGOS", "PAGOS")
    if denegado:
        return denegado

    val = _validar_datos_pago(datos)
    if not val["ok"]:
        return {"success": False, "codigo_error": val["codigo_error"], "mensaje": val["mensaje"]}

    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("BEGIN IMMEDIATE;")
            cursor.execute(
                """
                SELECT v.placa, v.tipo_vehiculo, v.activo, p.nombre_completo AS propietario_nombre
                FROM vehiculo v
                JOIN propietario p ON v.propietario_id = p.id
                WHERE v.placa = ?
                """,
                (val["placa"],),
            )
            veh = cursor.fetchone()
            if not veh:
                return _abortar_tx(conn, {
                    "success": False,
                    "codigo_error": "NO_REGISTRADO",
                    "mensaje": f"El vehículo '{formatear_placa(val['placa'])}' no existe en el padrón de abonados.",
                })

            if veh["activo"] == 0 and not val["es_reactivacion"]:
                return _abortar_tx(conn, {
                    "success": False,
                    "codigo_error": "VEHICULO_INACTIVO",
                    "mensaje": f"El vehículo '{formatear_placa(val['placa'])}' está dado de baja. Utilice la opción Reactivar Servicio.",
                })

            if val["es_reactivacion"] and veh["activo"] == 1:
                return _abortar_tx(conn, {
                    "success": False,
                    "codigo_error": "VEHICULO_YA_ACTIVO",
                    "mensaje": f"El vehículo '{formatear_placa(val['placa'])}' ya tiene una suscripción activa. Registre un pago ordinario.",
                })

            monto = _validar_monto_pago(datos.get("valor_pagado"), veh["tipo_vehiculo"], val["meses"])
            if not monto["ok"]:
                return _abortar_tx(conn, {
                    "success": False,
                    "codigo_error": monto["codigo_error"],
                    "mensaje": monto["mensaje"],
                })
            valor_recibido = monto["valor"]

            cursor.execute(
                """
                SELECT id, fecha_pago, fecha_vencimiento, valor_pagado, estado
                FROM mensualidad
                WHERE vehiculo_placa = ?
                ORDER BY CASE WHEN estado = 'CANCELADA' THEN 1 ELSE 0 END ASC, fecha_vencimiento DESC, id DESC
                LIMIT 1
                """,
                (val["placa"],),
            )
            m_actual = cursor.fetchone()

            calculo = _calcular_nueva_vigencia(
                m_actual,
                val["fecha_pago"],
                val["meses"],
                es_reactivacion=val["es_reactivacion"],
            )
            numero_recibo, pago_id = _persistir_mensualidad_y_pago(
                cursor, val, calculo, valor_recibido, m_actual, usuario_id
            )
            conn.commit()
            conn.close()

            accion_audit = "REACTIVAR_SUSCRIPCION" if val["es_reactivacion"] else "REGISTRAR_PAGO"
            registrar_auditoria(
                usuario_id,
                "PAGOS",
                accion_audit,
                f"Recibo {numero_recibo} | Placa {val['placa']} | ${valor_recibido:,.0f} ({val['metodo_pago']}) | {calculo['tipo_aplicacion']} -> Vigente hasta {calculo['nueva_fecha_vencimiento']}",
            )

            recibo = obtener_recibo_pago(numero_recibo)
            return {
                "success": True,
                "pago_id": pago_id,
                "numero_recibo": numero_recibo,
                "tipo_aplicacion": calculo["tipo_aplicacion"],
                "nuevo_estado_mensualidad": calculo["nuevo_estado"],
                "nueva_fecha_vencimiento": calculo["nueva_fecha_vencimiento"],
                "mensaje": f"Pago registrado ({numero_recibo}). Vigencia actualizada hasta {calculo['nueva_fecha_vencimiento']} ({calculo['nuevo_estado']}).",
                "pago": recibo,
            }
        except Exception as e:
            return _abortar_tx(conn, {"success": False, "mensaje": f"Error transaccional al registrar pago: {str(e)}"})


def _revertir_mensualidad_por_anulacion(cursor, p):
    """Revierte el estado y fechas de la mensualidad afectada al anular un pago confirmado."""
    cursor.execute(
        """
        SELECT * FROM pago
        WHERE vehiculo_placa = ? AND estado = 'CONFIRMADO' AND id != ?
        ORDER BY id DESC LIMIT 1
        """,
        (p["vehiculo_placa"], p["id"]),
    )
    pago_prev = cursor.fetchone()
    hoy = date.today()

    if pago_prev and pago_prev["mensualidad_id"] == p["mensualidad_id"]:
        fv_prev = datetime.strptime(pago_prev["periodo_fin"], "%Y-%m-%d").date()
        est_prev = "ACTIVA" if fv_prev >= hoy else "VENCIDA"
        cursor.execute(
            """
            UPDATE mensualidad
            SET fecha_pago = ?, fecha_vencimiento = ?, valor_pagado = ?, estado = ?
            WHERE id = ?
            """,
            (pago_prev["fecha_pago"], pago_prev["periodo_fin"], pago_prev["valor_pagado"], est_prev, p["mensualidad_id"]),
        )
        return

    if p["tipo_aplicacion"] == "INICIAL_REACTIVACION":
        cursor.execute("UPDATE mensualidad SET estado = 'CANCELADA' WHERE id = ?", (p["mensualidad_id"],))
        cursor.execute(
            "SELECT id FROM mensualidad WHERE vehiculo_placa = ? AND id != ? LIMIT 1",
            (p["vehiculo_placa"], p["mensualidad_id"]),
        )
        if cursor.fetchone():
            # Si existía un contrato previo antes de esta reactivación, el vehículo vuelve a estado inactivo
            cursor.execute("UPDATE vehiculo SET activo = 0 WHERE placa = ?", (p["vehiculo_placa"],))
        return

    corte_prev = datetime.strptime(p["periodo_inicio"], "%Y-%m-%d").date() - timedelta(days=1)
    est_prev = "ACTIVA" if corte_prev >= hoy else "VENCIDA"
    cursor.execute(
        "UPDATE mensualidad SET fecha_vencimiento = ?, estado = ? WHERE id = ?",
        (corte_prev.strftime("%Y-%m-%d"), est_prev, p["mensualidad_id"]),
    )


def anular_pago(pago_id: int, motivo: str, admin_id: int = 1):
    """
    Anula lógicamente (sin DELETE) el último pago confirmado de un vehículo,
    revirtiendo la fecha de vencimiento al corte previo bajo control estricto de rol ADMIN.
    """
    denegado = _denegar_si_sin_permiso(admin_id, "ANULAR_PAGOS", "PAGOS")
    if denegado:
        return denegado

    motivo_limpio = (motivo or "").strip()
    if not motivo_limpio:
        return {"success": False, "mensaje": "Debe especificar el motivo técnico/contable de la anulación."}

    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("BEGIN IMMEDIATE;")
            cursor.execute("SELECT * FROM pago WHERE id = ?", (pago_id,))
            p = cursor.fetchone()
            if not p:
                return _abortar_tx(conn, {"success": False, "mensaje": "Registro de pago no encontrado."})

            if p["estado"] == "ANULADO":
                return _abortar_tx(conn, {"success": False, "mensaje": f"El recibo {p['numero_recibo']} ya fue anulado previamente."})

            cursor.execute(
                """
                SELECT id FROM pago
                WHERE vehiculo_placa = ? AND estado = 'CONFIRMADO'
                ORDER BY id DESC LIMIT 1
                """,
                (p["vehiculo_placa"],),
            )
            ultimo = cursor.fetchone()
            if ultimo and ultimo["id"] != p["id"]:
                return _abortar_tx(conn, {
                    "success": False,
                    "mensaje": "Solo se puede anular el último pago confirmado de la placa para preservar la secuencia de cortes.",
                })

            obs_nueva = (p["observaciones"] or "") + f" | [ANULADO: {motivo_limpio}]"
            cursor.execute(
                "UPDATE pago SET estado = 'ANULADO', observaciones = ? WHERE id = ?",
                (obs_nueva, pago_id),
            )
            _revertir_mensualidad_por_anulacion(cursor, p)

            conn.commit()
            conn.close()

            registrar_auditoria(
                admin_id,
                "PAGOS",
                "ANULAR_PAGO",
                f"Anulado recibo {p['numero_recibo']} (Placa {p['vehiculo_placa']}, ${p['valor_pagado']:,.0f}). Motivo: {motivo_limpio}",
            )
            return {
                "success": True,
                "mensaje": f"Pago {p['numero_recibo']} anulado correctamente y vigencia revertida.",
            }
        except Exception as e:
            return _abortar_tx(conn, {"success": False, "mensaje": f"Error al anular pago: {str(e)}"})


def cancelar_suscripcion_abonado(placa_raw: str, motivo: str = "", usuario_id: int = 1):
    """
    Da de baja lógica (cancelación de servicio) a un cliente abonado sin eliminar registros de BD.
    Exige: (1) Vehículo NO esté adentro del parqueadero, (2) No tenga mora pendiente.
    """
    denegado = _denegar_si_sin_permiso(usuario_id, "GESTION_PAGOS", "PAGOS")
    if denegado:
        return denegado

    with db_lock:
        placa = limpiar_placa(placa_raw)
        vehiculo = consultar_vehiculo(placa)
        if not vehiculo:
            return {"success": False, "mensaje": f"Vehículo '{formatear_placa(placa)}' no encontrado."}

        if not vehiculo["activo"]:
            return {"success": False, "mensaje": f"El vehículo '{formatear_placa(placa)}' ya se encuentra inactivo / dado de baja."}

        if vehiculo["esta_adentro"]:
            return {
                "success": False,
                "codigo_error": "VEHICULO_ADENTRO",
                "mensaje": f"No se puede cancelar el servicio mientras '{formatear_placa(placa)}' esté estacionado adentro (Celda {vehiculo['registro_actual']['celda_codigo']}). Registre primero su salida.",
            }

        m = vehiculo.get("mensualidad")
        if m and not m["al_dia"]:
            return {
                "success": False,
                "codigo_error": "MORA_PENDIENTE",
                "mensaje": f"El vehículo '{formatear_placa(placa)}' presenta mora pendiente (vencida el {m['fecha_vencimiento']}). Debe quedar al día antes de cancelar el servicio.",
            }

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("BEGIN IMMEDIATE;")
            cursor.execute("UPDATE vehiculo SET activo = 0 WHERE placa = ?", (placa,))
            if m:
                cursor.execute("UPDATE mensualidad SET estado = 'CANCELADA' WHERE id = ?", (m["id"],))
            conn.commit()
            conn.close()
        except Exception as e:
            return _abortar_tx(conn, {"success": False, "mensaje": f"Error transaccional al cancelar suscripción: {str(e)}"})

        motivo_txt = (motivo or "Retiro voluntario del servicio").strip()
        registrar_auditoria(
            usuario_id,
            "PAGOS",
            "BAJA_SUSCRIPCION",
            f"Suscripción cancelada (baja lógica) para placa {placa}. Motivo: {motivo_txt}",
        )
        return {
            "success": True,
            "mensaje": f"Servicio cancelado para '{formatear_placa(placa)}'. Historial preservado en base de datos para auditoría o futura reactivación.",
        }


def reactivar_suscripcion_abonado(datos: dict, usuario_id: int = 2):
    """Reactiva un cliente dado de baja cobrando nueva mensualidad desde su fecha de pago."""
    datos_react = dict(datos)
    datos_react["es_reactivacion"] = True
    return registrar_pago_mensualidad(datos_react, usuario_id=usuario_id)


def obtener_recibo_pago(numero_recibo: str):
    """Retorna el comprobante detallado de un pago por su número de recibo."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            pg.id, pg.numero_recibo, pg.vehiculo_placa, pg.mensualidad_id,
            pg.fecha_pago, pg.fecha_registro, pg.periodo_inicio, pg.periodo_fin,
            pg.meses_pagados, pg.valor_pagado, pg.metodo_pago, pg.referencia_comprobante,
            pg.tipo_aplicacion, pg.estado, pg.observaciones,
            v.tipo_vehiculo, v.marca, v.modelo, v.color,
            p.nombre_completo AS propietario_nombre, p.documento AS propietario_doc, p.telefono AS propietario_telefono,
            u.username AS recaudador_username, u.nombre_completo AS recaudador_nombre, u.rol AS recaudador_rol
        FROM pago pg
        JOIN vehiculo v ON pg.vehiculo_placa = v.placa
        JOIN propietario p ON v.propietario_id = p.id
        LEFT JOIN usuario u ON pg.usuario_id = u.id
        WHERE pg.numero_recibo = ?
        """,
        (numero_recibo,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def _consultar_lista_pagos(cursor, placa: str = None, metodo: str = None, desde: str = None, hasta: str = None):
    """Consulta el historial filtrado de pagos con datos de titular y recaudador."""
    sql = """
        SELECT
            pg.id, pg.numero_recibo, pg.vehiculo_placa, pg.fecha_pago, pg.fecha_registro,
            pg.periodo_inicio, pg.periodo_fin, pg.meses_pagados, pg.valor_pagado,
            pg.metodo_pago, pg.referencia_comprobante, pg.tipo_aplicacion, pg.estado, pg.observaciones,
            v.tipo_vehiculo, p.nombre_completo AS propietario_nombre,
            u.username AS recaudador_username, u.rol AS recaudador_rol
        FROM pago pg
        JOIN vehiculo v ON pg.vehiculo_placa = v.placa
        JOIN propietario p ON v.propietario_id = p.id
        LEFT JOIN usuario u ON pg.usuario_id = u.id
        WHERE 1=1
    """
    params = []
    if placa and placa.strip():
        sql += " AND pg.vehiculo_placa LIKE ?"
        params.append(f"%{limpiar_placa(placa)}%")
    if metodo and metodo.strip():
        sql += " AND pg.metodo_pago = ?"
        params.append(metodo.strip().upper())
    if desde and desde.strip():
        sql += " AND pg.fecha_pago >= ?"
        params.append(desde.strip())
    if hasta and hasta.strip():
        sql += " AND pg.fecha_pago <= ?"
        params.append(hasta.strip())

    sql += " ORDER BY pg.id DESC"
    cursor.execute(sql, params)
    return [dict(r) for r in cursor.fetchall()]


def _calcular_metricas_caja(rows_pagos):
    """Calcula el cuadre total, diario, mensual y por método/categoría excluyendo anulados."""
    hoy_str = date.today().strftime("%Y-%m-%d")
    mes_prefijo = date.today().strftime("%Y-%m")
    recaudo_total = 0.0
    recaudo_hoy = 0.0
    recaudo_mes = 0.0
    confirmados = 0
    anulados = 0
    por_metodo = {m: 0.0 for m in METODOS_PAGO}
    por_categoria = {"CARRO": 0.0, "MOTO": 0.0}

    for row in rows_pagos:
        if row["estado"] == "ANULADO":
            anulados += 1
            continue
        confirmados += 1
        val = float(row["valor_pagado"])
        recaudo_total += val
        if row["fecha_pago"] == hoy_str:
            recaudo_hoy += val
        if str(row["fecha_pago"]).startswith(mes_prefijo):
            recaudo_mes += val
        if row["metodo_pago"] in por_metodo:
            por_metodo[row["metodo_pago"]] += val
        if row["tipo_vehiculo"] in por_categoria:
            por_categoria[row["tipo_vehiculo"]] += val

    return {
        "recaudo_total": recaudo_total,
        "recaudo_hoy": recaudo_hoy,
        "recaudo_mes": recaudo_mes,
        "confirmados": confirmados,
        "anulados": anulados,
        "por_metodo": por_metodo,
        "por_categoria": por_categoria,
    }


def _clasificar_cartera_abonados(abonados):
    """Clasifica el padrón de abonados en al día, próximos a vencer, en mora e inactivos."""
    al_dia_list = []
    proximos_list = []
    mora_list = []
    inactivos_list = []

    for ab in abonados:
        if not ab["activo"]:
            inactivos_list.append(ab)
        elif ab["al_dia"]:
            if ab["dias_restantes"] <= 5:
                proximos_list.append(ab)
            else:
                al_dia_list.append(ab)
        else:
            mora_list.append(ab)

    return {
        "al_dia": al_dia_list,
        "proximos_vencer": proximos_list,
        "en_mora": mora_list,
        "inactivos": inactivos_list,
    }


def obtener_estado_pagos_y_caja(
    placa: str = None,
    metodo: str = None,
    desde: str = None,
    hasta: str = None,
):
    """Consolida el historial de pagos, flujo de caja por método/categoría y alertas de cartera."""
    conn = get_connection()
    cursor = conn.cursor()
    pagos = _consultar_lista_pagos(cursor, placa, metodo, desde, hasta)
    cursor.execute(
        """
        SELECT
            pg.valor_pagado, pg.metodo_pago, pg.fecha_pago, pg.estado, v.tipo_vehiculo
        FROM pago pg
        JOIN vehiculo v ON pg.vehiculo_placa = v.placa
        """
    )
    todos = cursor.fetchall()
    conn.close()

    flujo_caja = _calcular_metricas_caja(todos)
    cartera = _clasificar_cartera_abonados(listar_abonados())

    return {
        "pagos": pagos,
        "total_pagos": len(pagos),
        "flujo_caja": flujo_caja,
        "cartera": cartera,
        "conteo_cartera": {
            "al_dia": len(cartera["al_dia"]) + len(cartera["proximos_vencer"]),
            "proximos_vencer": len(cartera["proximos_vencer"]),
            "en_mora": len(cartera["en_mora"]),
            "inactivos": len(cartera["inactivos"]),
        },
    }


def registrar_alerta_vencimiento(placa_raw: str, canal: str = "WHATSAPP", usuario_id: int = 2):
    """Genera y audita un recordatorio preventivo de vencimiento o cobro para el cliente."""
    denegado = _denegar_si_sin_permiso(usuario_id, "GESTION_PAGOS", "PAGOS")
    if denegado:
        return denegado

    placa = limpiar_placa(placa_raw)
    vehiculo = consultar_vehiculo(placa)
    if not vehiculo:
        return {"success": False, "mensaje": f"Vehículo '{formatear_placa(placa)}' no encontrado."}

    m = vehiculo.get("mensualidad")
    tarifa = _tarifa_por_tipo(vehiculo["tipo_vehiculo"])
    canal_clean = (canal or "WHATSAPP").strip().upper()
    if canal_clean not in ("WHATSAPP", "EMAIL", "SMS"):
        canal_clean = "WHATSAPP"

    fecha_v = m["fecha_vencimiento"] if m else "Sin contrato"
    estado_txt = "en MORA" if (not m or not m["al_dia"]) else f"próximo a vencer (corte {fecha_v})"
    destino = vehiculo["propietario_telefono"] if canal_clean in ("WHATSAPP", "SMS") else vehiculo["propietario_email"]

    texto_alerta = (
        f"Autos Colombia 24/7 informa a {vehiculo['propietario_nombre']}: "
        f"la mensualidad del vehículo {formatear_placa(placa)} se encuentra {estado_txt}. "
        f"Valor renovación mensual: ${tarifa:,.0f} COP."
    )

    registrar_auditoria(
        usuario_id,
        "PAGOS",
        "NOTIFICACION_COBRO",
        f"Alerta enviada vía {canal_clean} a {destino} ({placa}): {estado_txt}",
    )
    return {
        "success": True,
        "canal": canal_clean,
        "destino": destino,
        "mensaje_enviado": texto_alerta,
        "mensaje": f"Recordatorio enviado vía {canal_clean} al {destino}.",
    }
