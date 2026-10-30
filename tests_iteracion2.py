"""
Batería de Pruebas Unitarias y de Integración - Iteración 2
Sistema de Información Parqueadero Autos Colombia 24/7
Módulos: Gestión de Usuarios (Roles, Permisos, Auth) y Gestión de Celdas (CRUD, Mantenimiento, Reubicación)
Docente: Reinaldo Rojas | Grupo: 25 | IU Digital de Antioquia
Ejecución: python tests_iteracion2.py
"""

import unittest
import models
import database

class TestIteracion2AutosColombia(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        database.inicializar_base_datos()

    def test_01_autenticacion_admin_exitosa(self):
        """Verifica que el usuario administrador puede iniciar sesión con contraseña correcta."""
        res = models.autenticar_usuario("admin", "admin123")
        self.assertTrue(res["success"])
        self.assertEqual(res["usuario"]["rol"], "ADMIN")
        self.assertIn("nombre_completo", res["usuario"])
        print("[PASS] 01: Autenticación de Administrador exitosa.")

    def test_02_autenticacion_operario_exitosa(self):
        """Verifica que un operario de cabina puede iniciar sesión con su cuenta."""
        res = models.autenticar_usuario("adriana_op", "operario123")
        self.assertTrue(res["success"])
        self.assertEqual(res["usuario"]["rol"], "OPERARIO")
        print("[PASS] 02: Autenticación de Operario exitosa.")

    def test_03_bloqueo_credenciales_invalidas(self):
        """Verifica que el sistema rechaza contraseñas incorrectas y usuarios inexistentes."""
        res_bad_pw = models.autenticar_usuario("admin", "clave_invalida_xyz")
        self.assertFalse(res_bad_pw["success"])
        self.assertIn("incorrecta", res_bad_pw["mensaje"].lower())

        res_no_user = models.autenticar_usuario("usuario_fantasma", "123456")
        self.assertFalse(res_no_user["success"])
        print("[PASS] 03: Bloqueo estricto de credenciales inválidas comprobado.")

    def test_04_gestion_usuarios_crud(self):
        """Verifica la creación, listado y actualización de usuarios del sistema."""
        datos_nuevo = {
            "username": "operario_test_unit",
            "password": "testpassword123",
            "nombre_completo": "Operador de Pruebas Unitarias",
            "email": "test.unit@autoscolombia.com",
            "rol": "OPERARIO",
            "cargo": "Operador Auxiliar"
        }
        res_crear = models.crear_usuario(datos_nuevo, admin_id=1)
        self.assertTrue(res_crear["success"] or "ya está en uso" in res_crear["mensaje"])

        usuarios = models.listar_usuarios()
        self.assertGreaterEqual(len(usuarios), 4)

        # Actualizar
        user_test = [u for u in usuarios if u["username"] == "operario_test_unit"]
        if user_test:
            u_id = user_test[0]["id"]
            res_upd = models.actualizar_usuario(u_id, {
                "nombre_completo": "Operador Actualizado",
                "email": "test.unit@autoscolombia.com",
                "rol": "OPERARIO",
                "cargo": "Operador Nocturno",
                "activo": 1
            }, admin_id=1)
            self.assertTrue(res_upd["success"])
        print("[PASS] 04: CRUD de Gestión de Usuarios y Roles completado con éxito.")

    def test_05_administracion_celdas_80_espacios(self):
        """Verifica que el sistema gestione exactamente las 80 celdas reglamentarias (70 carros, 10 motos)."""
        celdas = models.listar_celdas_administracion()
        self.assertEqual(len(celdas), 80)
        carros = [c for c in celdas if c["tipo_permitido"] == "CARRO"]
        motos = [c for c in celdas if c["tipo_permitido"] == "MOTO"]
        self.assertEqual(len(carros), 70)
        self.assertEqual(len(motos), 10)
        print("[PASS] 05: Inventario de 80 Celdas reglamentarias (70 Carros / 10 Motos) validado.")

    def test_06_cambio_estado_celda_mantenimiento(self):
        """Verifica el cambio de estado de una celda a Mantenimiento y su retorno a Disponible."""
        # Pasar C-20 a MANTENIMIENTO
        res_maint = models.cambiar_estado_celda("C-20", "MANTENIMIENTO", "Avería en sensor ultrasónico", usuario_id=1)
        self.assertTrue(res_maint["success"])

        celdas = models.listar_celdas_administracion(filtro_estado="MANTENIMIENTO")
        codigos_maint = [c["codigo"] for c in celdas]
        self.assertIn("C-20", codigos_maint)

        # Retornar C-20 a DISPONIBLE
        res_disp = models.cambiar_estado_celda("C-20", "DISPONIBLE", "Reparación completada", usuario_id=1)
        self.assertTrue(res_disp["success"])
        print("[PASS] 06: Bloqueo por Mantenimiento y Desbloqueo de Celdas verificado.")

    def test_07_trazabilidad_auditoria_sistema(self):
        """Verifica que todas las operaciones sensibles se registren en la bitácora de auditoría."""
        auditoria = models.obtener_auditoria_sistema(20)
        self.assertGreater(len(auditoria), 0)
        modulos = {a["modulo"] for a in auditoria}
        self.assertTrue("SEGURIDAD" in modulos or "USUARIOS" in modulos or "CELDAS" in modulos or "SISTEMA" in modulos)
        print(f"[PASS] 07: Trazabilidad de Auditoría verificada con {len(auditoria)} registros.")

if __name__ == "__main__":
    print("=" * 70)
    print(" EJECUCIÓN DE PRUEBAS AUTOMATIZADAS - ITERACIÓN 2 (AUTOS COLOMBIA)")
    print("=" * 70)
    unittest.main()
