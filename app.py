"""
Servidor Principal Concurrente (Multi-Operario) - Autos Colombia 24/7
Iteración 1: Módulo Exclusivo de Entrada y Salida de Vehículos
Docente: Reinaldo Rojas
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

        if path == "/api/resumen":
            data = models.obtener_resumen_operativo()
            return self._send_json(data)

        elif path == "/api/vehiculo":
            placa = params.get("placa", [""])[0]
            if not placa:
                return self._send_json({"error": "Debe especificar el parámetro 'placa'"}, 400)
            data = models.consultar_vehiculo(placa)
            if data:
                return self._send_json(data)
            else:
                return self._send_json({"error": f"Vehículo con placa '{placa}' no encontrado"}, 404)

        elif path == "/api/salud":
            return self._send_json({
                "status": "OK",
                "sistema": "Autos Colombia 24/7 - Iteración 1 (Multi-Operario Concurrente)",
                "docente": "Reinaldo Rojas",
                "timestamp": datetime.now().isoformat()
            })

        if path == "/" or path == "":
            self.path = "/index.html"
            return super().do_GET()

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception:
            body = {}

        if path == "/api/ingreso":
            placa = body.get("placa")
            observaciones = body.get("observaciones", "")
            puerta = body.get("puerta", "Puerta 1 (Norte)")
            if not placa:
                return self._send_json({"success": False, "mensaje": "La placa es obligatoria"}, 400)
            
            resultado = models.registrar_ingreso(placa, observaciones, puerta)
            status_code = 200 if resultado.get("success") else 400
            return self._send_json(resultado, status_code)

        elif path == "/api/salida":
            placa = body.get("placa")
            observaciones = body.get("observaciones", "")
            puerta = body.get("puerta", "Puerta 1 (Norte)")
            if not placa:
                return self._send_json({"success": False, "mensaje": "La placa es obligatoria"}, 400)
            
            resultado = models.registrar_salida(placa, observaciones, puerta)
            status_code = 200 if resultado.get("success") else 400
            return self._send_json(resultado, status_code)

        elif path == "/api/abonado":
            resultado = models.registrar_nuevo_abonado(body)
            status_code = 200 if resultado.get("success") else 400
            return self._send_json(resultado, status_code)

        return self._send_json({"error": "Endpoint no encontrado"}, 404)

def iniciar_servidor():
    """Inicializa la base de datos y arranca el servidor web multi-hilo local."""
    print("=" * 72)
    print(" PARQUEADERO AUTOS COLOMBIA 24/7 - ITERACIÓN 1 (MULTI-OPERARIO)")
    print(" Docente: Reinaldo Rojas")
    print(" Control Exclusivo de Entrada y Salida por Mensualidad")
    print("=" * 72)
    
    database.inicializar_base_datos()
    resumen = models.obtener_resumen_operativo()
    print(f"-> Capacidad Total: {resumen['capacidad_total']} celdas")
    print(f"   - Carros: {resumen['carros']['total']} celdas ({resumen['carros']['libres']} libres)")
    print(f"   - Motos:  {resumen['motos']['total']} celdas ({resumen['motos']['libres']} libres)")
    
    with ThreadedHTTPServer(("", PORT), AutosColombiaHandler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"\n[OK] Servidor Concurrente en ejecución en: {url}")
        print("-> Soportando múltiples operarios / puertas de acceso simultáneas.")
        print("-> Presiona Ctrl + C en cualquier momento para detener el servidor.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido por el usuario.")

if __name__ == "__main__":
    iniciar_servidor()
