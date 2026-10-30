"""
Suite Automatizada de Pruebas Unitarias, de Integración y Endpoints HTTP (CP-01 a CP-20)
Sistema de Información Autos Colombia 24/7 — Iteraciones 1 y 2 Unificadas
Asignatura: Ingeniería de Software - PREICA2602B020053
Docente: Prof. Reinaldo Rojas | Grupo: 25
Ejecución: python -X utf8 tests_iteracion2.py
"""

import os
import json
import threading
import unittest
import urllib.request
import urllib.error

import database
import models
import app


def resetear_base_datos_limpia():
    """Restaura la base de datos al estado semilla exacto (80 celdas, 4 usuarios RBAC, 6 vehículos)."""
    for sufijo in ("", "-wal", "-shm"):
        ruta = database.DB_PATH + sufijo
        if os.path.exists(ruta):
            try:
                os.remove(ruta)
            except OSError:
                pass
    database.inicializar_base_datos()


class PlanPruebasIteracion2TestCase(unittest.TestCase):
    """Ejecuta los 20 Casos de Prueba (CP-01 a CP-20) definidos en el Plan de Pruebas Resumido."""

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
        # Dejar la base de datos limpia y lista para demostración al finalizar toda la suite
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

    def test_cp01_autenticacion_exitosa_tres_roles_rbac(self):
        """CP-01: Autenticación SHA-256 exitosa para ADMIN, OPERARIO y AUDITOR con matriz de permisos."""
        r_admin = models.autenticar_usuario("admin", "admin123", "TestSuite")
        r_oper = models.autenticar_usuario("adriana_op", "operario123", "TestSuite")
        r_audi = models.autenticar_usuario("auditor", "auditor123", "TestSuite")

        self.assertTrue(r_admin["success"])
        self.assertEqual(r_admin["usuario"]["rol"], "ADMIN")
        self.assertIn("GESTION_USUARIOS", r_admin["usuario"]["permisos"])
        self.assertIn("CRUD_CELDAS", r_admin["usuario"]["permisos"])

        self.assertTrue(r_oper["success"])
        self.assertEqual(r_oper["usuario"]["rol"], "OPERARIO")
        self.assertIn("OPERACION_ACCESO", r_oper["usuario"]["permisos"])
        self.assertNotIn("GESTION_USUARIOS", r_oper["usuario"]["permisos"])

        self.assertTrue(r_audi["success"])
        self.assertEqual(r_audi["usuario"]["rol"], "AUDITOR")
        self.assertEqual(r_audi["usuario"]["permisos"], ["CONSULTA_AUDITORIA"])

    def test_cp02_rechazo_login_credenciales_invalidas(self):
        """CP-02: Rechazo HTTP 401 ante contraseña errónea o usuario inexistente."""
        status, body = self._http_post("/api/auth/login", {"username": "admin", "password": "wrong_password"})
        self.assertEqual(status, 401)
        self.assertFalse(body["success"])

        r_inex = models.autenticar_usuario("fantasma_99", "clave123")
        self.assertFalse(r_inex["success"])

    def test_cp03_crud_crear_usuario_y_unicidad(self):
        """CP-03: Alta de nuevo usuario por ADMIN y rechazo de username/correo duplicados."""
        status, nuevo = self._http_post(
            "/api/usuarios",
            {
                "username": "carlos_turno",
                "password": "turno2026",
                "nombre_completo": "Carlos Andrés Mendoza",
                "email": "carlos.mendoza@autoscolombia.com",
                "rol": "OPERARIO",
                "cargo": "Operador Nocturno",
                "admin_id": 1,
            },
        )
        self.assertEqual(status, 201)
        self.assertTrue(nuevo["success"])

        # Intento duplicado
        dup = models.crear_usuario(
            {
                "username": "carlos_turno",
                "password": "turno2026",
                "nombre_completo": "Duplicado",
                "email": "otro@autoscolombia.com",
                "rol": "OPERARIO",
            },
            admin_id=1,
        )
        self.assertFalse(dup["success"])

    def test_cp04_actualizar_perfil_rol_y_cambio_clave_sha256(self):
        """CP-04: Edición de rol/cargo y restablecimiento criptográfico de contraseña SHA-256."""
        usuarios = models.listar_usuarios(busqueda="carlos_turno")
        self.assertEqual(len(usuarios), 1)
        uid = usuarios[0]["id"]

        upd = models.actualizar_usuario(uid, {"rol": "AUDITOR", "cargo": "Auditor Nocturno"}, admin_id=1)
        self.assertTrue(upd["success"])

        pw = models.cambiar_password(uid, "nuevaSegura99", admin_id=1)
        self.assertTrue(pw["success"])

        login_nuevo = models.autenticar_usuario("carlos_turno", "nuevaSegura99")
        self.assertTrue(login_nuevo["success"])
        self.assertEqual(login_nuevo["usuario"]["rol"], "AUDITOR")

    def test_cp05_proteccion_ultimo_administrador_activo(self):
        """CP-05: Impedir desactivar o degradar al único usuario con rol ADMIN activo."""
        intento_degradar = models.actualizar_usuario(1, {"rol": "OPERARIO", "activo": 1}, admin_id=1)
        self.assertFalse(intento_degradar["success"])

        intento_inactivar = models.actualizar_usuario(1, {"rol": "ADMIN", "activo": 0}, admin_id=1)
        self.assertFalse(intento_inactivar["success"])

    def test_cp06_bloqueo_cuenta_suspendida_y_baja_logica(self):
        """CP-06: Suspensión de cuenta impide login; baja de usuario con auditoría aplica baja lógica."""
        usuarios = models.listar_usuarios(busqueda="carlos_turno")
        uid = usuarios[0]["id"]

        # Como carlos_turno ya inició sesión en CP-04, tiene traza en auditoria_accion -> Baja Lógica
        baja = models.eliminar_usuario(uid, admin_id=1)
        self.assertTrue(baja["success"])
        self.assertEqual(baja["modo"], "BAJA_LOGICA")

        login_bloq = models.autenticar_usuario("carlos_turno", "nuevaSegura99")
        self.assertFalse(login_bloq["success"])

    def test_cp07_control_acceso_estricto_rbac_http_403(self):
        """CP-07: Verificación HTTP 403 cuando OPERARIO o AUDITOR invocan rutas sin privilegio RBAC."""
        # Operario (id=2) intentando crear usuario -> 403
        st1, b1 = self._http_post(
            "/api/usuarios",
            {
                "username": "intruso",
                "password": "clave123",
                "nombre_completo": "Intruso",
                "email": "intruso@autoscolombia.com",
                "rol": "ADMIN",
                "admin_id": 2,
            },
        )
        self.assertEqual(st1, 403)
        self.assertEqual(b1["codigo_error"], "PERMISO_DENEGADO")

        # Operario (id=2) intentando crear celda física -> 403
        st2, b2 = self._http_post(
            "/api/celdas",
            {"codigo": "C-99", "tipo_permitido": "CARRO", "zona": "ZONA X", "piso": 1, "usuario_id": 2},
        )
        self.assertEqual(st2, 403)

        # Auditor (id=4) intentando registrar ingreso vehicular -> 403
        st3, b3 = self._http_post(
            "/api/ingreso",
            {"placa": "ABC-123", "puerta": "Puerta 1", "usuario_id": 4},
        )
        self.assertEqual(st3, 403)

    def test_cp08_crud_clientes_abonados_y_actualizacion_vehiculo(self):
        """CP-08: Registro de nuevo abonado y actualización posterior de datos del titular y automotor."""
        alta = models.registrar_nuevo_abonado(
            {
                "placa": "NEW-777",
                "tipo_vehiculo": "CARRO",
                "marca": "Mazda",
                "modelo": "CX-30 Grand Touring",
                "color": "Rojo Diamante",
                "conductor": "Laura Sofía Mejía",
                "documento": "1098765432",
                "telefono": "3112223344",
                "estado_pago": "ACTIVA",
            },
            usuario_id=2,
        )
        self.assertTrue(alta["success"])

        edicion = models.actualizar_abonado_vehiculo(
            "NEW-777",
            {"color": "Gris Polimetálico", "telefono": "3159998877", "modelo": "CX-30 Híbrida 2026"},
            usuario_id=2,
        )
        self.assertTrue(edicion["success"])

        ficha = models.consultar_vehiculo("NEW-777")
        self.assertEqual(ficha["color"], "Gris Polimetálico")
        self.assertEqual(ficha["propietario_telefono"], "3159998877")

    def test_cp09_inventario_reglamentario_80_celdas_y_filtros(self):
        """CP-09: Verificación exacta de las 80 celdas base (70 Carros + 10 Motos) y filtros administrativos."""
        todas = models.listar_celdas_administracion()
        carros = models.listar_celdas_administracion(filtro_tipo="CARRO")
        motos = models.listar_celdas_administracion(filtro_tipo="MOTO")
        piso2 = [c for c in todas if c["piso"] == 2]

        self.assertEqual(len(todas), 80)
        self.assertEqual(len(carros), 70)
        self.assertEqual(len(motos), 10)
        self.assertEqual(len(piso2), 20)

    def test_cp10_crud_completo_celda_expansion_c71(self):
        """CP-10: Crear, editar zona/piso y eliminar celda física sin historial (C-71) restaurando 80 celdas."""
        crear = models.crear_celda(
            {"codigo": "C-71", "tipo_permitido": "CARRO", "zona": "ZONA EXPANSIÓN", "piso": 2, "estado": "DISPONIBLE"},
            usuario_id=1,
        )
        self.assertTrue(crear["success"])
        self.assertEqual(len(models.listar_celdas_administracion()), 81)

        editar = models.actualizar_celda(
            "C-71",
            {"zona": "ZONA VIP PISO 2", "piso": 2, "estado": "INACTIVA", "motivo_bloqueo": "Demarcación"},
            usuario_id=1,
        )
        self.assertTrue(editar["success"])

        borrar = models.eliminar_celda("C-71", usuario_id=1)
        self.assertTrue(borrar["success"])
        self.assertEqual(len(models.listar_celdas_administracion()), 80)

    def test_cp11_cambio_estado_celda_mantenimiento_e_historial(self):
        """CP-11: Bloqueo operativo de celda libre (C-10 -> MANTENIMIENTO) y trazabilidad en historial_celda."""
        res = models.cambiar_estado_celda("C-10", "MANTENIMIENTO", "Reparación de sensor ultrasónico", usuario_id=2)
        self.assertTrue(res["success"])

        hist = models.obtener_historial_celdas(limite=5)
        self.assertTrue(any(h["celda_codigo"] == "C-10" and h["estado_nuevo"] == "MANTENIMIENTO" for h in hist))

        # Rehabilitar para pruebas siguientes
        rehab = models.cambiar_estado_celda("C-10", "DISPONIBLE", "Sensor calibrado", usuario_id=2)
        self.assertTrue(rehab["success"])

    def test_cp12_bloqueo_mantenimiento_y_eliminacion_en_celda_ocupada(self):
        """CP-12: Prohibición de pasar a MANTENIMIENTO o eliminar una celda actualmente ocupada."""
        ing = models.registrar_ingreso("ABC-123", "Ingreso de prueba CP-12", "Puerta 1", usuario_id=2)
        self.assertTrue(ing["success"])
        celda_ocupada = ing["celda_asignada"]

        bloq = models.cambiar_estado_celda(celda_ocupada, "MANTENIMIENTO", "Intento inválido", usuario_id=1)
        self.assertFalse(bloq["success"])

        elim = models.eliminar_celda(celda_ocupada, usuario_id=1)
        self.assertFalse(elim["success"])

        models.registrar_salida("ABC-123", "Salida limpieza CP-12", "Puerta 1", usuario_id=2)

    def test_cp13_exclusion_celdas_mantenimiento_en_sorteo_ingreso(self):
        """CP-13: El algoritmo aleatorio de ingreso excluye celdas en MANTENIMIENTO o INACTIVA."""
        # Bloquear 9 de las 10 celdas de moto dejando únicamente M-07 DISPONIBLE
        for i in range(1, 11):
            cod = f"M-{i:02d}"
            if cod != "M-07":
                models.cambiar_estado_celda(cod, "MANTENIMIENTO", "Prueba exclusión sorteo", usuario_id=1)

        ing_moto = models.registrar_ingreso("MOT-808", "Casco entregado", "Puerta 1", usuario_id=2)
        self.assertTrue(ing_moto["success"])
        self.assertEqual(ing_moto["celda_asignada"], "M-07")

        # Si entra otra moto vigente (KLR-500), debe indicar SIN_CUPO porque las otras 9 están en mantenimiento
        sin_cupo = models.registrar_ingreso("KLR-500", "", "Puerta 1", usuario_id=2)
        self.assertFalse(sin_cupo["success"])
        self.assertEqual(sin_cupo["codigo_error"], "SIN_CUPO")

        # Limpiar estado
        models.registrar_salida("MOT-808", "Salida CP-13", "Puerta 1", usuario_id=2)
        for i in range(1, 11):
            cod = f"M-{i:02d}"
            if cod != "M-07":
                models.cambiar_estado_celda(cod, "DISPONIBLE", "Fin prueba CP-13", usuario_id=1)

    def test_cp14_ingreso_exitoso_carro_y_moto_mensualidad_vigente(self):
        """CP-14: Autorización de acceso y asignación de celda compatible para carro y moto al día."""
        r_carro = models.registrar_ingreso("TOY-456", "Sin rayones", "Puerta 1 - Norte", usuario_id=2)
        r_moto = models.registrar_ingreso("KLR-500", "Maletero cerrado", "Puerta 2 - Sur", usuario_id=3)

        self.assertTrue(r_carro["success"])
        self.assertTrue(r_carro["celda_asignada"].startswith("C-"))
        self.assertTrue(r_moto["success"])
        self.assertTrue(r_moto["celda_asignada"].startswith("M-"))

    def test_cp15_rechazo_mensualidad_vencida_y_no_registrado(self):
        """CP-15: Rechazo estricto sin días de gracia para morosos (XYZ-999) y no registrados."""
        mora = models.registrar_ingreso("XYZ-999", "", "Puerta 1", usuario_id=2)
        self.assertFalse(mora["success"])
        self.assertEqual(mora["codigo_error"], "MENSUALIDAD_VENCIDA")

        no_reg = models.registrar_ingreso("ZZZ-000", "", "Puerta 1", usuario_id=2)
        self.assertFalse(no_reg["success"])
        self.assertEqual(no_reg["codigo_error"], "NO_REGISTRADO")

    def test_cp16_control_antiduplicidad_vehiculo_ya_adentro(self):
        """CP-16: Bloqueo de doble entrada cuando el vehículo ya registra estado ADENTRO."""
        dup = models.registrar_ingreso("TOY-456", "", "Puerta 2", usuario_id=2)
        self.assertFalse(dup["success"])
        self.assertEqual(dup["codigo_error"], "YA_ADENTRO")

    def test_cp17_reubicacion_atomica_vehiculo_con_bloqueo_origen(self):
        """CP-17: Traslado atómico de vehículo estacionado hacia nueva celda libre marcando origen en MANTENIMIENTO."""
        ficha_antes = models.consultar_vehiculo("TOY-456")
        celda_origen = ficha_antes["registro_actual"]["celda_codigo"]
        celda_destino = "C-01" if celda_origen != "C-01" else "C-02"

        reub = models.reubicar_vehiculo_celda(
            "TOY-456",
            celda_destino,
            motivo="Filtración de agua sobre celda origen",
            marcar_anterior_mantenimiento=True,
            usuario_id=2,
        )
        self.assertTrue(reub["success"])
        self.assertEqual(reub["celda_destino"], celda_destino)
        self.assertEqual(reub["estado_origen"], "MANTENIMIENTO")

        # Rehabilitar celda origen tras validar
        models.cambiar_estado_celda(celda_origen, "DISPONIBLE", "Filtración corregida", usuario_id=1)

    def test_cp18_rechazo_reubicacion_categoria_incompatible(self):
        """CP-18: Rechazo al intentar reubicar un CARRO hacia una celda exclusiva de MOTO."""
        incomp = models.reubicar_vehiculo_celda("TOY-456", "M-01", "Intento cruzado", False, usuario_id=1)
        self.assertFalse(incomp["success"])

    def test_cp19_registro_novedad_fisica_y_salida_liberando_celda(self):
        """CP-19: Anotación de novedad física en bitácora (HU-03) y liberación de celdas al registrar salida."""
        nov = models.registrar_novedad_vehiculo("TOY-456", "Luz interior encendida reportada en ronda", usuario_id=2)
        self.assertTrue(nov["success"])

        sal_carro = models.registrar_salida("TOY-456", "Retiro conforme por titular", "Puerta 1", usuario_id=2)
        sal_moto = models.registrar_salida("KLR-500", "Salida sin novedad", "Puerta 2", usuario_id=3)
        self.assertTrue(sal_carro["success"])
        self.assertTrue(sal_moto["success"])

        resumen = models.obtener_resumen_operativo()
        self.assertEqual(resumen["total_ocupadas"], 0)
        self.assertEqual(resumen["total_libres"], 80)

    def test_cp20_auditoria_inmutable_y_endpoints_rest_salud(self):
        """CP-20: Verificación integral de endpoints HTTP GET y bitácora inmutable de auditoría 24/7."""
        st_salud, b_salud = self._http_get("/api/salud")
        st_res, b_res = self._http_get("/api/resumen")
        st_aud, b_aud = self._http_get("/api/auditoria?limite=30")

        self.assertEqual(st_salud, 200)
        self.assertEqual(b_salud["status"], "OK")
        self.assertEqual(st_res, 200)
        self.assertEqual(b_res["capacidad_total"], 80)
        self.assertEqual(st_aud, 200)
        self.assertGreaterEqual(b_aud["total"], 10)


if __name__ == "__main__":
    print("=" * 76)
    print(" EJECUTANDO SUITE OFICIAL DE 20 PRUEBAS — AUTOS COLOMBIA 24/7 (ITER. 1 & 2)")
    print("=" * 76)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(PlanPruebasIteracion2TestCase)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
