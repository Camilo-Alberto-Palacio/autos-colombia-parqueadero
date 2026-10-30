"""
Lógica del Negocio, Gestión de Usuarios (RBAC), Gestión CRUD de Celdas y Control de Acceso 24/7
Sistema de Información Autos Colombia - Iteraciones 1 y 2 Unificadas
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

ROLES_PERMITIDOS = ("ADMIN", "OPERARIO", "AUDITOR")
ESTADOS_CELDA = ("DISPONIBLE", "OCUPADA", "MANTENIMIENTO", "INACTIVA")

# MATRIZ OFICIAL DE CONTROL DE ACCESO BASADO EN ROLES (RBAC) - ITERACIÓN 2
PERMISOS_POR_ROL = {
    "ADMIN": {
        "descripcion": "Administrador General del Parqueadero (Control Total)",
        "permisos": [
            "OPERACION_ACCESO",
            "MANTENIMIENTO_CELDAS",
            "CRUD_CELDAS",
            "GESTION_USUARIOS",
            "GESTION_ABONADOS",
            "CONSULTA_AUDITORIA",
        ],
    },
    "OPERARIO": {
        "descripcion": "Operador de Cabina 24/7 (Acceso, Mantenimiento Operativo y Padrón)",
        "permisos": [
            "OPERACION_ACCESO",
            "MANTENIMIENTO_CELDAS",
            "GESTION_ABONADOS",
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
            ORDER BY fecha_vencimiento DESC LIMIT 1
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
    ORDER BY fecha_vencimiento DESC
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
    ORDER BY r.fecha_ingreso DESC
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
        "rbac": PERMISOS_POR_ROL,
    }
