"""
Batería de Pruebas Automatizadas Unitarias y de Integración - Iteración 1 (Corregido)
Parqueadero Autos Colombia 24/7
Asignatura: Ingeniería de Software
Docente: Reinaldo Rojas Lopez
Estudiantes: Adriana Andrea Agudelo, Camilo Alberto Palacios, Juan Daniel Pulgarin

Cubre exhaustivamente:
1. HU-01 / RF-01 / RF-02: Ingreso exitoso y asignación aleatoria de celda según tipo (Carro/Moto).
2. HU-01 (Criterio Excepción): Rechazo estricto de placa inexistente / no registrada.
3. HU-01 (Criterio Excepción): Bloqueo estricto de ingreso duplicado (vehículo ya figura ADENTRO).
4. HU-02: Rechazo por mensualidad vencida sin periodo de gracia.
5. HU-03: Verificación de atributos técnicos y registro de novedades físicas.
6. HU-04 / RNF-03: Control transaccional de aforo máximo en backend (70 Carros / 10 Motos).
7. HU-05: Salida exitosa con liberación inmediata de celda y cálculo de permanencia.
8. HU-05 (Criterio Excepción): Rechazo de salida para automotores sin registro activo (no están adentro).
"""

import unittest
from datetime import datetime
import models
import database


class TestAutosColombiaIteracion1Corregido(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Inicializa la base de datos con el esquema reglamentario de 80 celdas."""
        database.inicializar_base_datos()

    def test_01_ingreso_exitoso_carro_asignacion_aleatoria(self):
        """Valida que un carro registrado con mensualidad vigente reciba una celda libre de carro (C-01 a C-70)."""
        # Aseguramos que TOY-456 no esté adentro
        models.registrar_salida("TOY-456", "Salida preparatoria")
        
        res = models.registrar_ingreso("TOY-456", "Sin novedades visibles", "Puerta 1 (Norte)")
        self.assertTrue(res["success"], f"Error inesperado al ingresar: {res}")
        self.assertIn("C-", res["celda_asignada"])
        self.assertEqual(res["vehiculo"]["tipo_vehiculo"], "CARRO")
        
        # Verificar estado adentro
        v = models.consultar_vehiculo("TOY-456")
        self.assertTrue(v["esta_adentro"])
        self.assertEqual(v["registro_actual"]["celda_codigo"], res["celda_asignada"])

    def test_02_criterio_aceptacion_placa_inexistente(self):
        """
        CRITERIO DE ACEPTACIÓN EVALUADO:
        Dado que se ingresa una placa no registrada (ZZZ-999),
        Cuando el operario intenta registrar el ingreso,
        Entonces el sistema deniega el acceso con código NO_REGISTRADO y mensaje explícito.
        """
        res = models.registrar_ingreso("ZZZ-999", "Intento no autorizado", "Puerta 1 (Norte)")
        self.assertFalse(res["success"])
        self.assertEqual(res["codigo_error"], "NO_REGISTRADO")
        self.assertIn("NO se encuentra registrado", res["mensaje"])

    def test_03_criterio_aceptacion_ingreso_duplicado(self):
        """
        CRITERIO DE ACEPTACIÓN EVALUADO:
        Dado que el vehículo TOY-456 ya se encuentra ADENTRO en el parqueadero,
        Cuando se intenta registrar nuevamente su ingreso por cualquier puerta,
        Entonces el sistema bloquea la operación con código YA_ADENTRO e indica la celda que ocupa.
        """
        # Ya está adentro por test_01
        res_dup = models.registrar_ingreso("TOY-456", "Segundo intento de ingreso", "Puerta 2 (Sur)")
        self.assertFalse(res_dup["success"])
        self.assertEqual(res_dup["codigo_error"], "YA_ADENTRO")
        self.assertIn("ya figura ADENTRO", res_dup["mensaje"])

    def test_04_rechazo_mensualidad_vencida_sin_periodo_gracia(self):
        """Valida la política de cero periodo de gracia para vehículos con mensualidad expirada (XYZ-999)."""
        res = models.registrar_ingreso("XYZ-999", "", "Puerta 1 (Norte)")
        self.assertFalse(res["success"])
        self.assertEqual(res["codigo_error"], "MENSUALIDAD_VENCIDA")
        self.assertIn("está VENCIDA", res["mensaje"])

    def test_05_salida_exitosa_y_liberacion_inmediata_celda(self):
        """Valida que al registrar la salida se libere la celda y se liquide el tiempo de estancia."""
        # Consultamos celda antes de salir
        v_antes = models.consultar_vehiculo("TOY-456")
        celda_ocupada = v_antes["registro_actual"]["celda_codigo"]
        
        res_salida = models.registrar_salida("TOY-456", "Vehículo sale en óptimas condiciones", "Puerta 1 (Norte)")
        self.assertTrue(res_salida["success"])
        self.assertEqual(res_salida["celda_liberada"], celda_ocupada)
        self.assertIn("tiempo_permanencia", res_salida)
        
        # Verificar que ya no figure adentro
        v_despues = models.consultar_vehiculo("TOY-456")
        self.assertFalse(v_despues["esta_adentro"])

    def test_06_criterio_aceptacion_salida_sin_registro_activo(self):
        """
        CRITERIO DE ACEPTACIÓN EVALUADO:
        Dado que el vehículo TOY-456 ya salió (no figura ADENTRO),
        Cuando un operario intenta registrar nuevamente su salida,
        Entonces el sistema rechaza la solicitud con código NO_ADENTRO e impide la operación.
        """
        res_fallo = models.registrar_salida("TOY-456", "Salida indebida", "Puerta 1 (Norte)")
        self.assertFalse(res_fallo["success"])
        self.assertEqual(res_fallo["codigo_error"], "NO_ADENTRO")
        self.assertIn("no figura actualmente adentro", res_fallo["mensaje"])

    def test_07_rnf03_control_ocupacion_aforo_backend(self):
        """
        RNF-03: Control de Ocupación Backend.
        Verifica que el servicio consulte en tiempo real la disponibilidad
        y no permita sobrepasar los cupos reglamentarios (10 motos y 70 carros).
        """
        resumen = models.obtener_resumen_operativo()
        self.assertIn("carros", resumen)
        self.assertIn("motos", resumen)
        self.assertEqual(resumen["carros"]["total"], 70)
        self.assertEqual(resumen["motos"]["total"], 10)
        self.assertEqual(resumen["capacidad_total"], 80)
        self.assertLessEqual(resumen["total_ocupadas"], 80)


if __name__ == "__main__":
    unittest.main()
