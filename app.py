"""
Servidor Principal Concurrente (Multi-Operario) - Autos Colombia 24/7
Iteraciones 1 y 2 Unificadas: Gestión de Usuarios (RBAC), Gestión CRUD de Celdas y Control de Acceso
Asignatura: Ingeniería de Software - PREICA2602B020053
Docente: Reinaldo Rojas | Grupo: 25
Ejecución: python app.py
"""

import http.server
import socketserver
import json
import urllib.parse
import os
from datetime import datetime

import database
import models

PORT = int(os.environ.get("PORT", 8000))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")


class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Servidor HTTP Multi-hilo para soportar múltiples terminales y operarios en simultáneo (24/7)."""
    allow_reuse_address = True
    daemon_threads = True


class AutosColombiaHandler(http.server.SimpleHTTPRequestHandler):
    """Manejador HTTP para la API REST y la Interfaz Web SPA de Autos Colombia 24/7."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def log_message(self, format, *args):
        # Registro limpio en consola sin ruido innecesario
        if os.environ.get("QUIET_SERVER") != "1":
            super().log_message(format, *args)

    def _status_for_result(self, resultado: dict, success_code: int = 200) -> int:
        if resultado.get("success"):
            return success_code
        codigo = resultado.get("codigo_error", "")
        if codigo in ("PERMISO_DENEGADO", "CUENTA_INACTIVA"):
            return 403
        if codigo in ("SESION_REQUERIDA", "USUARIO_NO_EXISTE"):
            return 401
        return 400

    def _send_json(self, data, status_code=200):
        response_bytes = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        # 1. Resumen Operativo General (Dashboard 24/7)
        if path == "/api/resumen":
            return self._send_json(models.obtener_resumen_operativo())

        # 2. Matriz RBAC de Roles y Permisos
        elif path == "/api/roles":
            return self._send_json({"roles": models.obtener_matriz_rbac()})

        # 3. Consulta de Vehículo por Placa
        elif path == "/api/vehiculo":
            placa = params.get("placa", [""])[0]
            if not placa:
                return self._send_json({"error": "Debe especificar el parámetro 'placa'"}, 400)
            data = models.consultar_vehiculo(placa)
            if data:
                return self._send_json(data)
            return self._send_json({"error": f"Vehículo con placa '{placa}' no encontrado"}, 404)

        # 4. Listado y Filtro de Usuarios del Sistema (Iteración 2)
        elif path == "/api/usuarios":
            rol_filtro = params.get("rol", [None])[0]
            solo_activos = params.get("activos", ["false"])[0].lower() == "true"
            busqueda = params.get("q", [None])[0]
            usuarios = models.listar_usuarios(rol_filtro, solo_activos, busqueda)
            return self._send_json({"total": len(usuarios), "usuarios": usuarios})

        # 5. Inventario y Filtros de Celdas (Iteración 2)
        elif path == "/api/celdas":
            tipo = params.get("tipo", [None])[0]
            estado = params.get("estado", [None])[0]
            zona = params.get("zona", [None])[0]
            busqueda = params.get("q", [None])[0]
            celdas = models.listar_celdas_administracion(tipo, estado, zona, busqueda)
            return self._send_json({"total": len(celdas), "celdas": celdas})

        # 6. Listado y Búsqueda de Clientes Abonados y Vehículos (Iteración 2)
        elif path == "/api/abonados":
            busqueda = params.get("q", [None])[0]
            abonados = models.listar_abonados(busqueda)
            return self._send_json({"total": len(abonados), "abonados": abonados})

        # 7. Bitácora Central de Auditoría 24/7
        elif path == "/api/auditoria":
            limite = int(params.get("limite", [60])[0])
            modulo = params.get("modulo", [None])[0]
            items = models.obtener_auditoria_sistema(limite, modulo)
            return self._send_json({"total": len(items), "auditoria": items})

        # 8. Historial Técnico de Cambios y Mantenimiento de Celdas
        elif path == "/api/historial_celdas":
            limite = int(params.get("limite", [60])[0])
            items = models.obtener_historial_celdas(limite)
            return self._send_json({"total": len(items), "historial": items})

        # 9. Endpoint de Salud del Sistema
        elif path == "/api/salud":
            return self._send_json(
                {
                    "status": "OK",
                    "sistema": "Autos Colombia 24/7 - Iteraciones 1 y 2 Unificadas",
                    "docente": "Reinaldo Rojas",
                    "grupo": "25",
                    "modulos": [
                        "Control de Acceso 24/7 (Entrada/Salida/Novedades)",
                        "Gestión CRUD de Usuarios y Control RBAC (Admin, Operario, Auditor)",
                        "Gestión CRUD, Mantenimiento y Reubicación de Celdas (80 Plazas)",
                        "Gestión CRUD de Clientes Abonados y Vehículos",
                        "Auditoría Inmutable 24/7",
                    ],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

        # Servir Frontend SPA
        if path in ("/", ""):
            self.path = "/index.html"

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            datos = json.loads(body.decode("utf-8")) if body else {}
        except json.JSONDecodeError:
            return self._send_json({"success": False, "mensaje": "Cuerpo JSON inválido"}, 400)

        # 1. Autenticación / Inicio de Sesión (SHA-256 + RBAC)
        if path == "/api/auth/login":
            username = datos.get("username", "")
            password = datos.get("password", "")
            ip = datos.get("terminal", "Cabina Principal")
            resultado = models.autenticar_usuario(username, password, ip)
            return self._send_json(resultado, 200 if resultado["success"] else 401)

        # 2. CRUD Usuarios: Crear Usuario
        elif path == "/api/usuarios":
            admin_id = int(datos.get("admin_id", 1))
            resultado = models.crear_usuario(datos, admin_id)
            return self._send_json(resultado, self._status_for_result(resultado, 201))

        # 3. CRUD Usuarios: Actualizar Perfil / Rol / Estado
        elif path == "/api/usuarios/actualizar":
            user_id = int(datos.get("user_id", 0))
            admin_id = int(datos.get("admin_id", 1))
            resultado = models.actualizar_usuario(user_id, datos, admin_id)
            return self._send_json(resultado, self._status_for_result(resultado, 200))

        # 4. CRUD Usuarios: Restablecer Contraseña
        elif path == "/api/usuarios/clave":
            user_id = int(datos.get("user_id", 0))
            nueva_clave = datos.get("nueva_password", "")
            admin_id = int(datos.get("admin_id", 1))
            resultado = models.cambiar_password(user_id, nueva_clave, admin_id)
            return self._send_json(resultado, self._status_for_result(resultado, 200))

        # 5. CRUD Usuarios: Eliminar / Baja Lógica de Usuario
        elif path == "/api/usuarios/eliminar":
            user_id = int(datos.get("user_id", 0))
            admin_id = int(datos.get("admin_id", 1))
            resultado = models.eliminar_usuario(user_id, admin_id)
            return self._send_json(resultado, self._status_for_result(resultado, 200))

        # 6. CRUD Celdas: Crear Nueva Celda
        elif path == "/api/celdas":
            usuario_id = int(datos.get("usuario_id", 1))
            resultado = models.crear_celda(datos, usuario_id)
            return self._send_json(resultado, self._status_for_result(resultado, 201))

        # 7. CRUD Celdas: Actualizar Parámetros de Celda (Zona, Piso, Tipo, Estado)
        elif path == "/api/celdas/actualizar":
            codigo = datos.get("codigo", "")
            usuario_id = int(datos.get("usuario_id", 1))
            resultado = models.actualizar_celda(codigo, datos, usuario_id)
            return self._send_json(resultado, self._status_for_result(resultado, 200))

        # 8. CRUD Celdas: Eliminar Celda (con validación de integridad)
        elif path == "/api/celdas/eliminar":
            codigo = datos.get("codigo", "")
            usuario_id = int(datos.get("usuario_id", 1))
            resultado = models.eliminar_celda(codigo, usuario_id)
            return self._send_json(resultado, self._status_for_result(resultado, 200))

        # 9. Gestión Operativa de Celdas: Cambiar Estado (Disponible / Mantenimiento / Inactiva)
        elif path == "/api/celdas/estado":
            codigo = datos.get("codigo", "")
            nuevo_estado = datos.get("nuevo_estado", "")
            motivo = datos.get("motivo", "")
            usuario_id = int(datos.get("usuario_id", 1))
            resultado = models.cambiar_estado_celda(codigo, nuevo_estado, motivo, usuario_id)
            return self._send_json(resultado, self._status_for_result(resultado, 200))

        # 10. Gestión Operativa de Celdas: Reubicación Atómica de Vehículo
        elif path == "/api/celdas/reubicar":
            placa = datos.get("placa", "")
            nueva_celda = datos.get("nueva_celda", "")
            motivo = datos.get("motivo", "")
            marcar_mantenimiento = bool(datos.get("marcar_anterior_mantenimiento", False))
            usuario_id = int(datos.get("usuario_id", 1))
            resultado = models.reubicar_vehiculo_celda(
                placa, nueva_celda, motivo, marcar_mantenimiento, usuario_id
            )
            return self._send_json(resultado, self._status_for_result(resultado, 200))

        # 11. Control de Acceso: Registrar Entrada de Vehículo (Iteración 1 + 2)
        elif path == "/api/ingreso":
            placa = datos.get("placa", "")
            observaciones = datos.get("observaciones", None)
            puerta = datos.get("puerta", "Puerta 1 (Norte)")
            usuario_id = int(datos.get("usuario_id", 2))
            resultado = models.registrar_ingreso(placa, observaciones, puerta, usuario_id)
            return self._send_json(resultado, self._status_for_result(resultado, 200))

        # 12. Control de Acceso: Registrar Novedad Física sobre Vehículo Estacionado
        elif path == "/api/novedad":
            placa = datos.get("placa", "")
            novedad = datos.get("novedad", "")
            usuario_id = int(datos.get("usuario_id", 2))
            resultado = models.registrar_novedad_vehiculo(placa, novedad, usuario_id)
            return self._send_json(resultado, self._status_for_result(resultado, 200))

        # 13. Control de Acceso: Registrar Salida de Vehículo y Liberar Celda
        elif path == "/api/salida":
            placa = datos.get("placa", "")
            observaciones_salida = datos.get("observaciones_salida", None)
            puerta = datos.get("puerta", "Puerta 1 (Norte)")
            usuario_id = int(datos.get("usuario_id", 2))
            resultado = models.registrar_salida(placa, observaciones_salida, puerta, usuario_id)
            return self._send_json(resultado, self._status_for_result(resultado, 200))

        # 14. CRUD Abonados: Registrar Nuevo Cliente Abonado y Vehículo
        elif path == "/api/abonado":
            usuario_id = int(datos.get("usuario_id", 1))
            resultado = models.registrar_nuevo_abonado(datos, usuario_id)
            return self._send_json(resultado, self._status_for_result(resultado, 201))

        # 15. CRUD Abonados: Actualizar Datos del Titular y Vehículo
        elif path == "/api/abonado/actualizar":
            placa = datos.get("placa", "")
            usuario_id = int(datos.get("usuario_id", 1))
            resultado = models.actualizar_abonado_vehiculo(placa, datos, usuario_id)
            return self._send_json(resultado, self._status_for_result(resultado, 200))

        return self._send_json({"error": "Ruta POST no encontrada"}, 404)


def iniciar_servidor():
    database.inicializar_base_datos()
    with ThreadedHTTPServer(("", PORT), AutosColombiaHandler) as httpd:
        print("=" * 72)
        print("   SISTEMA DE GESTIÓN AUTOS COLOMBIA 24/7 - ITERACIONES 1 & 2")
        print("   Docente: Prof. Reinaldo Rojas | Grupo: 25 | IU Digital de Antioquia")
        print(f"   Servidor activo en: http://localhost:{PORT}")
        print("   - Módulo 1: Gestión de Entrada, Salida y Novedades 24/7")
        print("   - Módulo 2: Gestión CRUD de Usuarios y Control RBAC (Admin/Operario/Auditor)")
        print("   - Módulo 3: Gestión CRUD, Mantenimiento y Reubicación de Celdas (80 Plazas)")
        print("   - Módulo 4: Gestión CRUD de Clientes Abonados y Auditoría Inmutable")
        print("=" * 72)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido ordenadamente.")


if __name__ == "__main__":
    iniciar_servidor()
