"""
Servidor Principal Concurrente (Multi-Operario) - Autos Colombia 24/7
Iteración 1 y 2 Unificada: Gestión de Usuarios, Gestión de Celdas y Control de Acceso
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

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Servidor HTTP Multi-hilo para soportar varios operarios en simultáneo (Concurrencia 24/7)."""
    allow_reuse_address = True
    daemon_threads = True

class AutosColombiaHandler(http.server.SimpleHTTPRequestHandler):
    """Manejador HTTP para la API REST y la Interfaz Web de Autos Colombia 24/7."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def _send_json(self, data, status_code=200):
        response_bytes = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        # 1. Resumen Operativo General (Dashboard)
        if path == "/api/resumen":
            data = models.obtener_resumen_operativo()
            return self._send_json(data)

        # 2. Consulta de Vehículo por Placa
        elif path == "/api/vehiculo":
            placa = params.get("placa", [""])[0]
            if not placa:
                return self._send_json({"error": "Debe especificar el parámetro 'placa'"}, 400)
            data = models.consultar_vehiculo(placa)
            if data:
                return self._send_json(data)
            else:
                return self._send_json({"error": f"Vehículo con placa '{placa}' no encontrado"}, 404)

        # 3. Lista de Usuarios del Sistema (Gestión de Usuarios - Iteración 2)
        elif path == "/api/usuarios":
            rol_filtro = params.get("rol", [None])[0]
            solo_activos = params.get("activos", ["false"])[0].lower() == "true"
            usuarios = models.listar_usuarios(rol_filtro, solo_activos)
            return self._send_json({"total": len(usuarios), "usuarios": usuarios})

        # 4. Administración de Celdas (Gestión de Celdas - Iteración 2)
        elif path == "/api/celdas":
            tipo = params.get("tipo", [None])[0]
            estado = params.get("estado", [None])[0]
            zona = params.get("zona", [None])[0]
            celdas = models.listar_celdas_administracion(tipo, estado, zona)
            return self._send_json({"total": len(celdas), "celdas": celdas})

        # 5. Bitácora de Auditoría del Sistema
        elif path == "/api/auditoria":
            limite = int(params.get("limite", [50])[0])
            items = models.obtener_auditoria_sistema(limite)
            return self._send_json({"total": len(items), "auditoria": items})

        # 6. Historial de Cambios de Celdas
        elif path == "/api/historial_celdas":
            limite = int(params.get("limite", [50])[0])
            items = models.obtener_historial_celdas(limite)
            return self._send_json({"total": len(items), "historial": items})

        # 7. Endpoint de Salud del Sistema
        elif path == "/api/salud":
            return self._send_json({
                "status": "OK",
                "sistema": "Autos Colombia 24/7 - Iteración 1 y 2 Unificada",
                "docente": "Reinaldo Rojas",
                "grupo": "25",
                "modulos": ["Control de Acceso", "Gestión de Usuarios y Roles", "Gestión y Mantenimiento de Celdas", "Padrón de Abonados"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        # Servir Frontend SPA
        if path == "/" or path == "":
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

        # 1. Autenticación / Login de Usuario (Iteración 2)
        if path == "/api/auth/login":
            username = datos.get("username", "")
            password = datos.get("password", "")
            ip = datos.get("terminal", "Cabina Principal")
            resultado = models.autenticar_usuario(username, password, ip)
            status = 200 if resultado["success"] else 401
            return self._send_json(resultado, status)

        # 2. Crear Nuevo Usuario del Sistema (Iteración 2)
        elif path == "/api/usuarios":
            admin_id = int(datos.get("admin_id", 1))
            resultado = models.crear_usuario(datos, admin_id)
            status = 201 if resultado["success"] else 400
            return self._send_json(resultado, status)

        # 3. Actualizar Usuario del Sistema (Iteración 2)
        elif path == "/api/usuarios/actualizar":
            user_id = int(datos.get("user_id", 0))
            admin_id = int(datos.get("admin_id", 1))
            resultado = models.actualizar_usuario(user_id, datos, admin_id)
            status = 200 if resultado["success"] else 400
            return self._send_json(resultado, status)

        # 4. Cambiar Contraseña de Usuario (Iteración 2)
        elif path == "/api/usuarios/clave":
            user_id = int(datos.get("user_id", 0))
            nueva_clave = datos.get("nueva_password", "")
            admin_id = int(datos.get("admin_id", 1))
            resultado = models.cambiar_password(user_id, nueva_clave, admin_id)
            status = 200 if resultado["success"] else 400
            return self._send_json(resultado, status)

        # 5. Cambiar Estado de Celda (Mantenimiento, Disponible, Inactiva) (Iteración 2)
        elif path == "/api/celdas/estado":
            codigo = datos.get("codigo", "")
            nuevo_estado = datos.get("nuevo_estado", "")
            motivo = datos.get("motivo", "")
            usuario_id = int(datos.get("usuario_id", 1))
            resultado = models.cambiar_estado_celda(codigo, nuevo_estado, motivo, usuario_id)
            status = 200 if resultado["success"] else 400
            return self._send_json(resultado, status)

        # 6. Reubicar Vehículo entre Celdas (Iteración 2)
        elif path == "/api/celdas/reubicar":
            placa = datos.get("placa", "")
            nueva_celda = datos.get("nueva_celda", "")
            motivo = datos.get("motivo", "")
            marcar_mantenimiento = datos.get("marcar_anterior_mantenimiento", False)
            usuario_id = int(datos.get("usuario_id", 1))
            resultado = models.reubicar_vehiculo_celda(placa, nueva_celda, motivo, marcar_mantenimiento, usuario_id)
            status = 200 if resultado["success"] else 400
            return self._send_json(resultado, status)

        # 7. Registrar Entrada de Vehículo (Iteración 1 & 2)
        elif path == "/api/ingreso":
            placa = datos.get("placa", "")
            observaciones = datos.get("observaciones", None)
            puerta = datos.get("puerta", "Puerta 1 (Norte)")
            usuario_id = int(datos.get("usuario_id", 2))
            resultado = models.registrar_ingreso(placa, observaciones, puerta, usuario_id)
            status = 200 if resultado["success"] else 400
            return self._send_json(resultado, status)

        # 8. Registrar Salida de Vehículo (Iteración 1 & 2)
        elif path == "/api/salida":
            placa = datos.get("placa", "")
            observaciones_salida = datos.get("observaciones_salida", None)
            puerta = datos.get("puerta", "Puerta 1 (Norte)")
            usuario_id = int(datos.get("usuario_id", 2))
            resultado = models.registrar_salida(placa, observaciones_salida, puerta, usuario_id)
            status = 200 if resultado["success"] else 400
            return self._send_json(resultado, status)

        # 9. Registrar Nuevo Abonado (Padrón de Abonados)
        elif path == "/api/abonado":
            usuario_id = int(datos.get("usuario_id", 1))
            resultado = models.registrar_nuevo_abonado(datos, usuario_id)
            status = 200 if resultado["success"] else 400
            return self._send_json(resultado, status)

        return self._send_json({"error": "Ruta POST no encontrada"}, 404)

def iniciar_servidor():
    database.inicializar_base_datos()
    with ThreadedHTTPServer(("", PORT), AutosColombiaHandler) as httpd:
        print("=" * 70)
        print("   SISTEMA DE GESTIÓN AUTOS COLOMBIA 24/7 - ITERACIÓN 1 & 2")
        print("   Docente: Prof. Reinaldo Rojas | Grupo: 25 | IU Digital")
        print(f"   Servidor activo en: http://localhost:{PORT}")
        print("   - Módulo 1: Gestión de Entrada y Salida 24/7")
        print("   - Módulo 2: Gestión de Usuarios y Roles (RBAC: Admin, Operario, Auditor)")
        print("   - Módulo 3: Gestión y Mantenimiento de Celdas (80 Celdas)")
        print("   - Módulo 4: Padrón de Abonados y Auditoría")
        print("=" * 70)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido ordenadamente.")

if __name__ == "__main__":
    iniciar_servidor()
