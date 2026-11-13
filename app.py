"""
Servidor Principal Concurrente (Multi-Operario) - Autos Colombia 24/7
Iteraciones 1, 2 y 3 Unificadas: Control de Acceso, Usuarios (RBAC), Celdas y Gestión de Pagos
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

    def _safe_int(self, valor, default=None, campo: str = "parámetro") -> int:
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            if default is not None:
                return default
            raise ValueError(f"El campo '{campo}' es obligatorio y debe ser un entero.")
        if isinstance(valor, bool):
            raise ValueError(f"El campo '{campo}' debe ser un número entero válido.")
        try:
            return int(str(valor).strip()) if isinstance(valor, str) else int(valor)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"El campo '{campo}' debe ser un número entero válido.") from exc

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
        try:
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(response_bytes)))
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
            self.wfile.write(response_bytes)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _payload_salud(self):
        return {
            "status": "OK",
            "sistema": "Autos Colombia 24/7 - Iteraciones 1, 2 y 3 Unificadas",
            "docente": "Reinaldo Rojas",
            "grupo": "25",
            "modulos": [
                "Control de Acceso 24/7 (Entrada/Salida/Novedades)",
                "Gestión CRUD de Usuarios y Control RBAC (Admin, Operario, Auditor)",
                "Gestión CRUD, Mantenimiento y Reubicación de Celdas (80 Plazas)",
                "Gestión CRUD de Clientes Abonados y Vehículos",
                "Gestión de Pagos en Plataforma, Vigencia Consecutiva y Flujo de Caja (Iteración 3)",
                "Auditoría Inmutable 24/7",
            ],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _despachar_get_api(self, path: str, params: dict):
        rutas_simples = {
            "/api/resumen": lambda: models.obtener_resumen_operativo(),
            "/api/roles": lambda: {"roles": models.obtener_matriz_rbac()},
            "/api/usuarios": lambda: (
                lambda u: {"total": len(u), "usuarios": u}
            )(
                models.listar_usuarios(
                    params.get("rol", [None])[0],
                    params.get("activos", ["false"])[0].lower() == "true",
                    params.get("q", [None])[0],
                )
            ),
            "/api/celdas": lambda: (
                lambda c: {"total": len(c), "celdas": c}
            )(
                models.listar_celdas_administracion(
                    params.get("tipo", [None])[0],
                    params.get("estado", [None])[0],
                    params.get("zona", [None])[0],
                    params.get("q", [None])[0],
                )
            ),
            "/api/abonados": lambda: (
                lambda a: {"total": len(a), "abonados": a}
            )(models.listar_abonados(params.get("q", [None])[0])),
            "/api/auditoria": lambda: (
                lambda it: {"total": len(it), "auditoria": it}
            )(
                models.obtener_auditoria_sistema(
                    self._safe_int(params.get("limite", [60])[0], 60, "limite"),
                    params.get("modulo", [None])[0],
                )
            ),
            "/api/historial_celdas": lambda: (
                lambda it: {"total": len(it), "historial": it}
            )(
                models.obtener_historial_celdas(
                    self._safe_int(params.get("limite", [60])[0], 60, "limite")
                )
            ),
            "/api/pagos": lambda: models.obtener_estado_pagos_y_caja(
                params.get("placa", [None])[0],
                params.get("metodo", [None])[0],
                params.get("desde", [None])[0],
                params.get("hasta", [None])[0],
            ),
            "/api/salud": self._payload_salud,
        }
        if path in rutas_simples:
            return rutas_simples[path](), 200

        if path == "/api/vehiculo":
            placa = params.get("placa", [""])[0]
            if not placa:
                return {"error": "Debe especificar el parámetro 'placa'"}, 400
            data = models.consultar_vehiculo(placa)
            if data:
                return data, 200
            return {"error": f"Vehículo con placa '{placa}' no encontrado"}, 404

        if path == "/api/pagos/previsualizar":
            res = models.previsualizar_pago_mensualidad(
                params.get("placa", [""])[0],
                params.get("fecha_pago", [None])[0],
                params.get("meses", [1])[0],
                params.get("reactivacion", ["false"])[0].lower() == "true",
            )
            return res, self._status_for_result(res, 200)

        if path == "/api/pagos/recibo":
            numero_recibo = params.get("numero_recibo", [""])[0]
            recibo = models.obtener_recibo_pago(numero_recibo)
            if recibo:
                return {"success": True, "pago": recibo}, 200
            return {"success": False, "mensaje": f"Recibo '{numero_recibo}' no encontrado."}, 404

        return None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        if path.startswith("/api/"):
            try:
                res = self._despachar_get_api(path, params)
                if res is not None:
                    return self._send_json(res[0], res[1])
                return self._send_json({"error": "Ruta GET no encontrada"}, 404)
            except ValueError as exc:
                return self._send_json({"success": False, "codigo_error": "PARAMETRO_INVALIDO", "mensaje": str(exc)}, 400)

        if path in ("/", ""):
            self.path = "/index.html"

        return super().do_GET()

    def _leer_json_body(self):
        content_length = self._safe_int(self.headers.get("Content-Length", 0), 0, "Content-Length")
        if content_length < 0:
            raise ValueError("Content-Length no puede ser negativo.")
        body = self.rfile.read(content_length)
        datos = json.loads(body.decode("utf-8")) if body else {}
        if not isinstance(datos, dict):
            raise ValueError("El cuerpo JSON debe ser un objeto JSON clave-valor.")
        return datos

    def _despachar_post_usuarios(self, path: str, datos: dict):
        admin_id = self._safe_int(datos.get("admin_id", 1), 1, "admin_id")
        if path == "/api/usuarios":
            return models.crear_usuario(datos, admin_id), 201
        if path == "/api/usuarios/actualizar":
            user_id = self._safe_int(datos.get("user_id", 0), 0, "user_id")
            return models.actualizar_usuario(user_id, datos, admin_id), 200
        if path == "/api/usuarios/clave":
            user_id = self._safe_int(datos.get("user_id", 0), 0, "user_id")
            return models.cambiar_password(user_id, datos.get("nueva_password", ""), admin_id), 200
        if path == "/api/usuarios/eliminar":
            user_id = self._safe_int(datos.get("user_id", 0), 0, "user_id")
            return models.eliminar_usuario(user_id, admin_id), 200
        return None

    def _despachar_post_celdas(self, path: str, datos: dict):
        usuario_id = self._safe_int(datos.get("usuario_id", 1), 1, "usuario_id")
        if path == "/api/celdas":
            return models.crear_celda(datos, usuario_id), 201
        if path == "/api/celdas/actualizar":
            return models.actualizar_celda(datos.get("codigo", ""), datos, usuario_id), 200
        if path == "/api/celdas/eliminar":
            return models.eliminar_celda(datos.get("codigo", ""), usuario_id), 200
        if path == "/api/celdas/estado":
            return models.cambiar_estado_celda(
                datos.get("codigo", ""), datos.get("nuevo_estado", ""), datos.get("motivo", ""), usuario_id
            ), 200
        if path == "/api/celdas/reubicar":
            return models.reubicar_vehiculo_celda(
                datos.get("placa", ""),
                datos.get("nueva_celda", ""),
                datos.get("motivo", ""),
                bool(datos.get("marcar_anterior_mantenimiento", False)),
                usuario_id,
            ), 200
        return None

    def _despachar_post_operacion_y_pagos(self, path: str, datos: dict):
        if path == "/api/ingreso":
            uid = self._safe_int(datos.get("usuario_id", 2), 2, "usuario_id")
            return models.registrar_ingreso(
                datos.get("placa", ""), datos.get("observaciones", None), datos.get("puerta", "Puerta 1 (Norte)"), uid
            ), 200
        if path == "/api/novedad":
            uid = self._safe_int(datos.get("usuario_id", 2), 2, "usuario_id")
            return models.registrar_novedad_vehiculo(datos.get("placa", ""), datos.get("novedad", ""), uid), 200
        if path == "/api/salida":
            uid = self._safe_int(datos.get("usuario_id", 2), 2, "usuario_id")
            return models.registrar_salida(
                datos.get("placa", ""), datos.get("observaciones_salida", None), datos.get("puerta", "Puerta 1 (Norte)"), uid
            ), 200
        if path == "/api/abonado":
            uid = self._safe_int(datos.get("usuario_id", 1), 1, "usuario_id")
            return models.registrar_nuevo_abonado(datos, uid), 201
        if path == "/api/abonado/actualizar":
            uid = self._safe_int(datos.get("usuario_id", 1), 1, "usuario_id")
            return models.actualizar_abonado_vehiculo(datos.get("placa", ""), datos, uid), 200
        if path == "/api/pagos":
            uid = self._safe_int(datos.get("usuario_id", 2), 2, "usuario_id")
            return models.registrar_pago_mensualidad(datos, uid), 201
        if path == "/api/pagos/anular":
            pago_id = self._safe_int(datos.get("pago_id", 0), 0, "pago_id")
            admin_id = self._safe_int(datos.get("admin_id", datos.get("usuario_id", 1)), 1, "admin_id")
            return models.anular_pago(pago_id, datos.get("motivo", ""), admin_id), 200
        if path == "/api/pagos/notificar":
            uid = self._safe_int(datos.get("usuario_id", 2), 2, "usuario_id")
            return models.registrar_alerta_vencimiento(datos.get("placa", ""), datos.get("canal", "WHATSAPP"), uid), 200
        if path == "/api/abonado/baja":
            uid = self._safe_int(datos.get("usuario_id", 1), 1, "usuario_id")
            return models.cancelar_suscripcion_abonado(datos.get("placa", ""), datos.get("motivo", ""), uid), 200
        if path == "/api/abonado/reactivar":
            uid = self._safe_int(datos.get("usuario_id", 2), 2, "usuario_id")
            return models.reactivar_suscripcion_abonado(datos, uid), 200
        return None

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path

        try:
            datos = self._leer_json_body()
        except json.JSONDecodeError:
            return self._send_json({"success": False, "mensaje": "Cuerpo JSON inválido"}, 400)
        except ValueError as exc:
            return self._send_json({"success": False, "codigo_error": "PARAMETRO_INVALIDO", "mensaje": str(exc)}, 400)

        if path == "/api/auth/login":
            resultado = models.autenticar_usuario(
                datos.get("username", ""), datos.get("password", ""), datos.get("terminal", "Cabina Principal")
            )
            return self._send_json(resultado, 200 if resultado["success"] else 401)

        try:
            despacho = (
                self._despachar_post_usuarios(path, datos)
                or self._despachar_post_celdas(path, datos)
                or self._despachar_post_operacion_y_pagos(path, datos)
            )
        except ValueError as exc:
            return self._send_json({"success": False, "codigo_error": "PARAMETRO_INVALIDO", "mensaje": str(exc)}, 400)

        if despacho:
            resultado, ok_code = despacho
            return self._send_json(resultado, self._status_for_result(resultado, ok_code))

        return self._send_json({"error": "Ruta POST no encontrada"}, 404)


def iniciar_servidor():
    database.inicializar_base_datos()
    with ThreadedHTTPServer(("", PORT), AutosColombiaHandler) as httpd:
        print("=" * 72)
        print("   SISTEMA DE GESTIÓN AUTOS COLOMBIA 24/7 - ITERACIONES 1, 2 Y 3")
        print("   Docente: Prof. Reinaldo Rojas | Grupo: 25 | IU Digital de Antioquia")
        print(f"   Servidor activo en: http://localhost:{PORT}")
        print("   - Módulo 1: Gestión de Entrada, Salida y Novedades 24/7")
        print("   - Módulo 2: Gestión CRUD de Usuarios y Control RBAC (Admin/Operario/Auditor)")
        print("   - Módulo 3: Gestión CRUD, Mantenimiento y Reubicación de Celdas (80 Plazas)")
        print("   - Módulo 4: Gestión CRUD de Clientes Abonados y Auditoría Inmutable")
        print("   - Módulo 5: Gestión de Pagos, Mensualidades Consecutivas y Flujo de Caja")
        print("=" * 72)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido ordenadamente.")


if __name__ == "__main__":
    iniciar_servidor()
