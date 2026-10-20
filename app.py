"""
Servidor Principal de Aplicación - Autos Colombia 24/7
Iteración 1: Módulo de Entrada y Salida de Vehículos
Docente: Reinaldo Rojas
Ejecución: python app.py
"""

import http.server
import socketserver
import json
import urllib.parse
import os
import sys
import webbrowser
from datetime import datetime

import database
import models

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

class AutosColombiaHandler(http.server.SimpleHTTPRequestHandler):
    """Manejador HTTP para la API REST y la Interfaz Web de Autos Colombia 24/7."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def _send_json(self, data, status_code=200):
        response_bytes = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
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

        # Rutas de la API REST
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
                "sistema": "Autos Colombia 24/7 - Iteración 1",
                "docente": "Reinaldo Rojas",
                "timestamp": datetime.now().isoformat()
            })

        # Servir el Frontend estático
        if path == "/" or path == "":
            self.path = "/index.html"
            return super().do_GET()

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Leer body JSON
        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception:
            body = {}

        if path == "/api/ingreso":
            placa = body.get("placa")
            observaciones = body.get("observaciones", "Ingreso regular mensualidad")
            if not placa:
                return self._send_json({"success": False, "mensaje": "La placa es obligatoria"}, 400)
            
            resultado = models.registrar_ingreso(placa, observaciones)
            status_code = 200 if resultado.get("success") else 400
            return self._send_json(resultado, status_code)

        elif path == "/api/salida":
            placa = body.get("placa")
            if not placa:
                return self._send_json({"success": False, "mensaje": "La placa es obligatoria"}, 400)
            
            resultado = models.registrar_salida(placa)
            status_code = 200 if resultado.get("success") else 400
            return self._send_json(resultado, status_code)

        elif path == "/api/abonado":
            resultado = models.registrar_nuevo_abonado(body)
            status_code = 200 if resultado.get("success") else 400
            return self._send_json(resultado, status_code)

        return self._send_json({"error": "Endpoint no encontrado"}, 404)

def iniciar_servidor():
    """Inicializa la base de datos y arranca el servidor web local."""
    print("=" * 70)
    print(" PARQUEADERO AUTOS COLOMBIA 24/7 - ITERACIÓN 1")
    print(" Docente: Reinaldo Rojas")
    print(" Control Exclusivo de Entrada y Salida por Mensualidad")
    print("=" * 70)
    
    # 1. Asegurar base de datos inicializada
    database.inicializar_base_datos()
    resumen = models.obtener_resumen_operativo()
    print(f"-> Capacidad Total: {resumen['capacidad_total']} celdas")
    print(f"   - Carros: {resumen['carros']['total']} celdas ({resumen['carros']['libres']} libres)")
    print(f"   - Motos:  {resumen['motos']['total']} celdas ({resumen['motos']['libres']} libres)")
    
    # 2. Iniciar servidor HTTP
    handler = AutosColombiaHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"\n[OK] Servidor en ejecución en: {url}")
        print("-> Presiona Ctrl + C en cualquier momento para detener el servidor.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido por el usuario.")

if __name__ == "__main__":
    iniciar_servidor()
