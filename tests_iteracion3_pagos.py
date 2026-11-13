"""
Suite Automatizada de Pruebas Unitarias, Integración y Endpoints HTTP — Iteración 3 (Gestión de Pagos)
Casos de Prueba: CP-21 a CP-32 (Exclusivo del Módulo de Gestión de Pagos y Mensualidades)
Sistema de Información Autos Colombia 24/7
Asignatura: Ingeniería de Software - PREICA2602B020053
Docente: Prof. Reinaldo Rojas | Grupo: 25
Ejecución: python -X utf8 tests_iteracion3_pagos.py
"""

import json
import os
import threading
import unittest
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta

import app
import database
import models


def resetear_base_datos_limpia():
    """Restaura la base de datos al estado semilla exacto de las Iteraciones 1, 2 y 3."""
    for sufijo in ("", "-wal", "-shm"):
        ruta = database.DB_PATH + sufijo
        if os.path.exists(ruta):
            try:
                os.remove(ruta)
            except OSError:
                pass
    database.inicializar_base_datos()


class PlanPruebasIteracion3PagosTestCase(unittest.TestCase):
    """Ejecuta los 12 Casos de Prueba (CP-21 a CP-32) exclusivos de Gestión de Pagos."""

    @classmethod
    def setUpClass(cls):
        os.environ["QUIET_SERVER"] = "1"
        resetear_base_datos_limpia()
        cls.httpd = app.ThreadedHTTPServer(("127.0.0.1", 0), app.AutosColombiaHandler)
        cls.port = cls.httpd.server_address[1]
        cls.base_url = f"http://127.0.0.1:{cls.port}"
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        resetear_base_datos_limpia()

    def _http_post(self, path: str, payload: dict):
        req = urllib.request.Request(
            self.base_url + path,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            return err.code, json.loads(err.read().decode("utf-8"))

    def _http_get(self, path: str):
        req = urllib.request.Request(self.base_url + path, method="GET")
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            return err.code, json.loads(err.read().decode("utf-8"))

    def test_cp21_registro_directo_pago_plataforma_operario(self):
        """CP-21: Registro directo de pago en plataforma por OPERARIO (QR/Efectivo) generando recibo HTTP 201."""
        hoy_str = date.today().strftime("%Y-%m-%d")
        status, body = self._http_post(
            "/api/pagos",
            {
                "placa": "MOT-101",
                "fecha_pago": hoy_str,
                "meses_pagados": 1,
                "metodo_pago": "CODIGO_QR",
                "referencia_comprobante": "QR-CABINA-9901",
                "observaciones": "Pago en cabina norte con QR",
                "usuario_id": 2,  # OPERARIO adriana_op
            },
        )
        self.assertEqual(status, 201)
        self.assertTrue(body["success"])
        self.assertTrue(body["numero_recibo"].startswith("REC-"))
        self.assertEqual(body["tipo_aplicacion"], "MORA_CONSECUTIVA")
        self.assertEqual(body["nuevo_estado_mensualidad"], "ACTIVA")

    def test_cp22_control_rbac_pagos_y_anulacion_http_403(self):
        """CP-22: Bloqueo HTTP 403 a AUDITOR en escritura de pagos y a OPERARIO al intentar anular pagos."""
        hoy_str = date.today().strftime("%Y-%m-%d")
        # AUDITOR (id=4) no puede registrar pagos, dar bajas ni notificar
        st_pago, b_pago = self._http_post(
            "/api/pagos",
            {"placa": "ABC-123", "fecha_pago": hoy_str, "metodo_pago": "EFECTIVO", "usuario_id": 4},
        )
        self.assertEqual(st_pago, 403)
        self.assertEqual(b_pago["codigo_error"], "PERMISO_DENEGADO")

        st_baja, _ = self._http_post("/api/abonado/baja", {"placa": "ABC-123", "usuario_id": 4})
        self.assertEqual(st_baja, 403)

        st_notif, _ = self._http_post("/api/pagos/notificar", {"placa": "ABC-123", "usuario_id": 4})
        self.assertEqual(st_notif, 403)

        # OPERARIO (id=2) no puede anular pagos (solo ADMIN id=1)
        st_anul, b_anul = self._http_post(
            "/api/pagos/anular",
            {"pago_id": 1, "motivo": "Intento sin privilegios", "usuario_id": 2},
        )
        self.assertEqual(st_anul, 403)
        self.assertEqual(b_anul["codigo_error"], "PERMISO_DENEGADO")

    def test_cp23_rechazo_fecha_futura_monto_invalido_y_sin_referencia(self):
        """CP-23: Rechazo estricto de pagos a futuro, montos incorrectos y QR/Transferencia sin referencia."""
        manana_str = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        hoy_str = date.today().strftime("%Y-%m-%d")

        # 1. Fecha futura prohibida
        r_fut = models.registrar_pago_mensualidad(
            {"placa": "ABC-123", "fecha_pago": manana_str, "metodo_pago": "EFECTIVO"},
            usuario_id=2,
        )
        self.assertFalse(r_fut["success"])
        self.assertEqual(r_fut["codigo_error"], "FECHA_FUTURA")

        # 2. Transferencia bancaria sin comprobante obligatorio
        r_ref = models.registrar_pago_mensualidad(
            {"placa": "ABC-123", "fecha_pago": hoy_str, "metodo_pago": "TRANSFERENCIA_BANCARIA", "referencia_comprobante": ""},
            usuario_id=2,
        )
        self.assertFalse(r_ref["success"])
        self.assertEqual(r_ref["codigo_error"], "REFERENCIA_REQUERIDA")

        # 3. Valor pagado distinto a la tarifa reglamentaria ($250.000 para carro)
        r_monto = models.registrar_pago_mensualidad(
            {"placa": "ABC-123", "fecha_pago": hoy_str, "metodo_pago": "EFECTIVO", "valor_pagado": 120000},
            usuario_id=2,
        )
        self.assertFalse(r_monto["success"])
        self.assertEqual(r_monto["codigo_error"], "MONTO_INVALIDO")

        # 4. Parámetros HTTP no numéricos rechazados limpiamente con HTTP 400 (sin Error 500)
        st_bad_q, b_bad_q = self._http_get("/api/auditoria?limite=invalido")
        self.assertEqual(st_bad_q, 400)
        self.assertEqual(b_bad_q.get("codigo_error"), "PARAMETRO_INVALIDO")

        st_bad_p, b_bad_p = self._http_post("/api/pagos/anular", {"pago_id": "abc", "motivo": "Prueba", "admin_id": 1})
        self.assertEqual(st_bad_p, 400)
        self.assertEqual(b_bad_p.get("codigo_error"), "PARAMETRO_INVALIDO")

    def test_cp24_pago_anticipado_preserva_dias_restantes(self):
        """CP-24: Pago anticipado (ABC-123 vence en +20d) suma +30d al corte vigente alcanzando +50d."""
        hoy = date.today()
        ficha_antes = models.consultar_vehiculo("ABC-123")
        corte_antes = datetime_parse(ficha_antes["mensualidad"]["fecha_vencimiento"])
        esperado = (corte_antes + timedelta(days=30)).strftime("%Y-%m-%d")

        res = models.registrar_pago_mensualidad(
            {
                "placa": "ABC-123",
                "fecha_pago": hoy.strftime("%Y-%m-%d"),
                "metodo_pago": "TRANSFERENCIA_BANCARIA",
                "referencia_comprobante": "BANCOL-ANT-01",
            },
            usuario_id=2,
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["tipo_aplicacion"], "PAGO_ANTICIPADO")
        self.assertEqual(res["nueva_fecha_vencimiento"], esperado)
        self.assertEqual(res["pago"]["periodo_inicio"], (corte_antes + timedelta(days=1)).strftime("%Y-%m-%d"))

    def test_cp25_pago_puntual_en_fecha_de_vencimiento(self):
        """CP-25: Pago realizado exactamente en la fecha de corte (fecha_pago == fecha_vencimiento)."""
        hoy = date.today()
        hoy_str = hoy.strftime("%Y-%m-%d")

        # Crear abonado cuyo corte venza exactamente hoy
        models.registrar_nuevo_abonado(
            {
                "placa": "PUN-100",
                "tipo_vehiculo": "CARRO",
                "marca": "Kia",
                "modelo": "Sportage",
                "color": "Blanco",
                "conductor": "Marta Elena Ríos",
                "documento": "1099112233",
                "telefono": "3101112233",
                "estado_pago": "ACTIVA",
            },
            usuario_id=2,
        )
        conn = database.get_connection()
        conn.execute("UPDATE mensualidad SET fecha_vencimiento = ? WHERE vehiculo_placa = 'PUN100'", (hoy_str,))
        conn.commit()
        conn.close()

        res = models.registrar_pago_mensualidad(
            {"placa": "PUN-100", "fecha_pago": hoy_str, "metodo_pago": "EFECTIVO"},
            usuario_id=2,
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["tipo_aplicacion"], "PAGO_PUNTUAL")
        self.assertEqual(res["nueva_fecha_vencimiento"], (hoy + timedelta(days=30)).strftime("%Y-%m-%d"))

    def test_cp26_pago_en_mora_consecutiva_sin_corrimiento_e_ingreso(self):
        """CP-26: Pago en mora (XYZ-999 vencido hace 15d) corre consecutivo (+15d, no +30d) y desbloquea barrera."""
        hoy = date.today()
        ficha_antes = models.consultar_vehiculo("XYZ-999")
        corte_ant = datetime_parse(ficha_antes["mensualidad"]["fecha_vencimiento"])
        self.assertFalse(ficha_antes["mensualidad"]["al_dia"])

        # Antes de pagar, ingreso debe estar bloqueado
        ing_previo = models.registrar_ingreso("XYZ-999", "", "Puerta 1", usuario_id=2)
        self.assertFalse(ing_previo["success"])
        self.assertEqual(ing_previo["codigo_error"], "MENSUALIDAD_VENCIDA")

        # Registrar pago hoy -> nuevo vencimiento DEBE ser corte_ant + 30d (no hoy + 30d)
        res = models.registrar_pago_mensualidad(
            {
                "placa": "XYZ-999",
                "fecha_pago": hoy.strftime("%Y-%m-%d"),
                "metodo_pago": "CONSIGNACION",
                "referencia_comprobante": "CONS-XYZ-442",
            },
            usuario_id=2,
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["tipo_aplicacion"], "MORA_CONSECUTIVA")
        corte_esperado = (corte_ant + timedelta(days=30)).strftime("%Y-%m-%d")
        self.assertEqual(res["nueva_fecha_vencimiento"], corte_esperado)
        self.assertNotEqual(res["nueva_fecha_vencimiento"], (hoy + timedelta(days=30)).strftime("%Y-%m-%d"))

        # Tras el pago, el vehículo entra inmediatamente por barrera
        ing_ok = models.registrar_ingreso("XYZ-999", "Mensualidad recién normalizada", "Puerta 1", usuario_id=2)
        self.assertTrue(ing_ok["success"])
        models.registrar_salida("XYZ-999", "Salida CP-26", "Puerta 1", usuario_id=2)

    def test_cp27_mora_multimes_superior_a_30_dias(self):
        """CP-27: Mora > 30 días (hace 45 días) exige cubrir 2 meses para reactivar vigencia ACTIVA."""
        hoy = date.today()
        models.registrar_nuevo_abonado(
            {
                "placa": "MOR-200",
                "tipo_vehiculo": "MOTO",
                "marca": "Honda",
                "modelo": "CB 190R",
                "color": "Negro",
                "conductor": "Felipe Giraldo",
                "documento": "1088776655",
                "telefono": "3145556677",
                "estado_pago": "VENCIDA",
            },
            usuario_id=2,
        )
        corte_45 = (hoy - timedelta(days=45)).strftime("%Y-%m-%d")
        conn = database.get_connection()
        conn.execute("UPDATE mensualidad SET fecha_vencimiento = ? WHERE vehiculo_placa = 'MOR200'", (corte_45,))
        conn.commit()
        conn.close()

        # Abonar 1 solo mes deja el corte en hoy - 15d -> sigue VENCIDA
        p1 = models.registrar_pago_mensualidad(
            {"placa": "MOR-200", "fecha_pago": hoy.strftime("%Y-%m-%d"), "meses_pagados": 1, "metodo_pago": "EFECTIVO"},
            usuario_id=2,
        )
        self.assertTrue(p1["success"])
        self.assertEqual(p1["nuevo_estado_mensualidad"], "VENCIDA")

        # Abonar el 2do mes lleva el corte a hoy + 15d -> ACTIVA
        p2 = models.registrar_pago_mensualidad(
            {"placa": "MOR-200", "fecha_pago": hoy.strftime("%Y-%m-%d"), "meses_pagados": 1, "metodo_pago": "EFECTIVO"},
            usuario_id=2,
        )
        self.assertTrue(p2["success"])
        self.assertEqual(p2["nuevo_estado_mensualidad"], "ACTIVA")
        self.assertEqual(p2["nueva_fecha_vencimiento"], (hoy + timedelta(days=15)).strftime("%Y-%m-%d"))

    def test_cp28_comprobante_recibo_previsualizacion_y_filtros_libro(self):
        """CP-28: Consulta GET /api/pagos/previsualizar, /api/pagos/recibo y filtros del libro mayor."""
        hoy_str = date.today().strftime("%Y-%m-%d")
        st_prev, b_prev = self._http_get(f"/api/pagos/previsualizar?placa=TOY-456&fecha_pago={hoy_str}&meses=2")
        self.assertEqual(st_prev, 200)
        self.assertTrue(b_prev["success"])
        self.assertEqual(b_prev["valor_total"], 500000.0)
        self.assertEqual(b_prev["tipo_aplicacion"], "PAGO_ANTICIPADO")

        st_rec, b_rec = self._http_get("/api/pagos/recibo?numero_recibo=REC-SEED-0001")
        self.assertEqual(st_rec, 200)
        self.assertEqual(b_rec["pago"]["vehiculo_placa"], "ABC123")

        st_list, b_list = self._http_get("/api/pagos?placa=XYZ999&metodo=CONSIGNACION")
        self.assertEqual(st_list, 200)
        self.assertGreaterEqual(b_list["total_pagos"], 1)

    def test_cp29_anulacion_logica_pago_admin_y_reversion_corte(self):
        """CP-29: Anulación auditada por ADMIN (sin DELETE) revierte corte de mensualidad y descuenta caja."""
        hoy = date.today()
        ficha_pre = models.consultar_vehiculo("KLR-500")
        corte_original = ficha_pre["mensualidad"]["fecha_vencimiento"]

        pago_nuevo = models.registrar_pago_mensualidad(
            {
                "placa": "KLR-500",
                "fecha_pago": hoy.strftime("%Y-%m-%d"),
                "metodo_pago": "CODIGO_QR",
                "referencia_comprobante": "QR-ERR-123",
            },
            usuario_id=2,
        )
        self.assertTrue(pago_nuevo["success"])
        pago_id = pago_nuevo["pago_id"]

        st_anul, b_anul = self._http_post(
            "/api/pagos/anular",
            {"pago_id": pago_id, "motivo": "Comprobante digitado a placa equivocada", "admin_id": 1},
        )
        self.assertEqual(st_anul, 200)
        self.assertTrue(b_anul["success"])

        # Verificar que el recibo NO fue borrado sino marcado ANULADO y el corte volvió al original
        recibo = models.obtener_recibo_pago(pago_nuevo["numero_recibo"])
        self.assertIsNotNone(recibo)
        self.assertEqual(recibo["estado"], "ANULADO")
        ficha_post = models.consultar_vehiculo("KLR-500")
        self.assertEqual(ficha_post["mensualidad"]["fecha_vencimiento"], corte_original)

    def test_cp30_bloqueos_baja_logica_vehiculo_adentro_o_con_mora(self):
        """CP-30: Impedir dar de baja un servicio si el vehículo está ADENTRO o si presenta mora pendiente."""
        # 1. Vehículo ADENTRO (TOY-456)
        ing = models.registrar_ingreso("TOY-456", "Prueba baja CP-30", "Puerta 1", usuario_id=2)
        self.assertTrue(ing["success"])
        baja_adentro = models.cancelar_suscripcion_abonado("TOY-456", "Intento con vehículo adentro", usuario_id=1)
        self.assertFalse(baja_adentro["success"])
        self.assertEqual(baja_adentro["codigo_error"], "VEHICULO_ADENTRO")
        models.registrar_salida("TOY-456", "Salida CP-30", "Puerta 1", usuario_id=2)

        # 2. Vehículo con MORA pendiente
        models.registrar_nuevo_abonado(
            {
                "placa": "DEB-300",
                "tipo_vehiculo": "CARRO",
                "marca": "Renault",
                "modelo": "Logan",
                "color": "Gris",
                "conductor": "Carlos Mora",
                "documento": "1077665544",
                "telefono": "3189990011",
                "estado_pago": "VENCIDA",
            },
            usuario_id=2,
        )
        baja_mora = models.cancelar_suscripcion_abonado("DEB-300", "Intento con deuda", usuario_id=1)
        self.assertFalse(baja_mora["success"])
        self.assertEqual(baja_mora["codigo_error"], "MORA_PENDIENTE")

    def test_cp31_baja_logica_y_reactivacion_desde_fecha_pago(self):
        """CP-31: Baja lógica (sin DELETE) bloquea barrera y reactivación reinicia vigencia desde fecha_pago."""
        hoy = date.today()
        hoy_str = hoy.strftime("%Y-%m-%d")

        # Dar de baja a KLR-500 (está al día y afuera)
        baja = models.cancelar_suscripcion_abonado("KLR-500", "Viaje de vacaciones 20 días", usuario_id=2)
        self.assertTrue(baja["success"])

        ficha_inact = models.consultar_vehiculo("KLR-500")
        self.assertIsNotNone(ficha_inact)
        self.assertEqual(ficha_inact["activo"], 0)
        self.assertEqual(ficha_inact["mensualidad"]["estado"], "CANCELADA")

        # Vehículo dado de baja no puede ingresar por barrera
        ing_bloq = models.registrar_ingreso("KLR-500", "", "Puerta 1", usuario_id=2)
        self.assertFalse(ing_bloq["success"])
        self.assertEqual(ing_bloq["codigo_error"], "VEHICULO_INACTIVO")

        # Reactivar servicio pagando hoy -> nueva vigencia = hoy + 30d
        st_react, b_react = self._http_post(
            "/api/abonado/reactivar",
            {
                "placa": "KLR-500",
                "fecha_pago": hoy_str,
                "metodo_pago": "EFECTIVO",
                "usuario_id": 2,
            },
        )
        self.assertEqual(st_react, 200)
        self.assertTrue(b_react["success"])
        self.assertEqual(b_react["tipo_aplicacion"], "INICIAL_REACTIVACION")
        self.assertEqual(b_react["nueva_fecha_vencimiento"], (hoy + timedelta(days=30)).strftime("%Y-%m-%d"))

        # Rechazar reactivación duplicada si el vehículo ya se encuentra activo
        st_dup, b_dup = self._http_post(
            "/api/abonado/reactivar",
            {"placa": "KLR-500", "fecha_pago": hoy_str, "metodo_pago": "EFECTIVO", "usuario_id": 2},
        )
        self.assertEqual(st_dup, 400)
        self.assertEqual(b_dup.get("codigo_error"), "VEHICULO_YA_ACTIVO")

        # Anular la reactivación como ADMIN debe revertir el vehículo a activo=0 y mensualidad CANCELADA
        st_anul_r, b_anul_r = self._http_post(
            "/api/pagos/anular",
            {"pago_id": b_react["pago_id"], "motivo": "Prueba reversión de reactivación", "admin_id": 1},
        )
        self.assertEqual(st_anul_r, 200)
        self.assertTrue(b_anul_r["success"])
        ficha_rev = models.consultar_vehiculo("KLR-500")
        self.assertEqual(ficha_rev["activo"], 0)
        self.assertEqual(ficha_rev["mensualidad"]["estado"], "CANCELADA")

        # Reactivación definitiva para verificar prioridad sobre contratos CANCELADA previos
        st_react2, b_react2 = self._http_post(
            "/api/abonado/reactivar",
            {"placa": "KLR-500", "fecha_pago": hoy_str, "metodo_pago": "EFECTIVO", "usuario_id": 2},
        )
        self.assertEqual(st_react2, 200)
        self.assertTrue(b_react2["success"])
        ficha_fin = models.consultar_vehiculo("KLR-500")
        self.assertEqual(ficha_fin["activo"], 1)
        self.assertTrue(ficha_fin["mensualidad"]["al_dia"])

    def test_cp32_flujo_caja_mensual_cartera_y_alerta_vencimiento(self):
        """CP-32: Flujo de caja consolidado por método/categoría, clasificación de cartera y alerta auditada."""
        st, estado = self._http_get("/api/pagos")
        self.assertEqual(st, 200)

        fc = estado["flujo_caja"]
        suma_metodos = sum(fc["por_metodo"].values())
        suma_categorias = sum(fc["por_categoria"].values())
        self.assertAlmostEqual(fc["recaudo_total"], suma_metodos, places=2)
        self.assertAlmostEqual(fc["recaudo_total"], suma_categorias, places=2)
        self.assertGreater(fc["recaudo_mes"], 0)

        st_notif, b_notif = self._http_post(
            "/api/pagos/notificar",
            {"placa": "DEB-300", "canal": "WHATSAPP", "usuario_id": 2},
        )
        self.assertEqual(st_notif, 200)
        self.assertTrue(b_notif["success"])
        self.assertIn("DEB-300", b_notif["mensaje_enviado"])


def datetime_parse(fecha_str: str) -> date:
    return datetime.strptime(fecha_str, "%Y-%m-%d").date()


if __name__ == "__main__":
    print("=" * 76)
    print(" EJECUTANDO SUITE DE 12 PRUEBAS DE PAGOS — AUTOS COLOMBIA 24/7 (ITER. 3)")
    print("=" * 76)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(PlanPruebasIteracion3PagosTestCase)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
