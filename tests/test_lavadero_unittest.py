# tests/test_lavadero_unittest.py

import unittest
# Importamos la clase Lavadero desde el módulo padre
from lavadero import Lavadero

class TestLavadero(unittest.TestCase):
    
    # Método que se ejecuta antes de cada test.
    # Es el equivalente del @pytest.fixture en este contexto.
    def setUp(self):
        """Prepara una nueva instancia de Lavadero antes de cada prueba."""
        self.lavadero = Lavadero()

    # ----------------------------------------------------------------------
    # Función auxiliar movida DENTRO del test (Mejor práctica)
    # ----------------------------------------------------------------------

    def ejecutar_y_obtener_fases(self, prelavado, secado, encerado):
        """Ejecuta un ciclo completo y devuelve la lista de fases visitadas."""
        self.lavadero.hacerLavado(prelavado, secado, encerado)
        
        fases_visitadas = [self.lavadero.fase]
        # Bucle while con condición compuesta para evitar usar break (mejor práctica)
        pasos = 0
        while self.lavadero.ocupado and pasos < 20:
            self.lavadero.avanzarFase()
            fases_visitadas.append(self.lavadero.fase)
            pasos += 1
            
        return fases_visitadas

    # ----------------------------------------------------------------------    
    # Función para resetear el estado cuanto terminamos una ejecución de lavado
    # ----------------------------------------------------------------------
    def test_reseteo_estado_con_terminar(self):
        """Test 0: Verifica que terminar() resetea todas las flags y el estado."""
        self.lavadero.hacerLavado(True, True, True)
        self.lavadero._cobrar()
        self.lavadero.terminar()
        
        self.assertEqual(self.lavadero.fase, Lavadero.FASE_INACTIVO)
        self.assertFalse(self.lavadero.ocupado)
        self.assertFalse(self.lavadero.prelavado_a_mano)
        self.assertTrue(self.lavadero.ingresos > 0) # Los ingresos deben mantenerse
        
    # ----------------------------------------------------------------------
    # TESTS  
    # ----------------------------------------------------------------------
        
    def test1_estado_inicial_correcto(self):
        """Test 1: Verifica que el estado inicial es Inactivo y con 0 ingresos."""
        self.assertEqual(self.lavadero.fase, Lavadero.FASE_INACTIVO)
        self.assertEqual(self.lavadero.ingresos, 0.0)
        self.assertFalse(self.lavadero.ocupado)
        self.assertFalse(self.lavadero.prelavado_a_mano)
        self.assertFalse(self.lavadero.secado_a_mano)
        self.assertFalse(self.lavadero.encerado)
   
    def test2_excepcion_encerado_sin_secado(self):
        """Test 2: Comprueba que encerar sin secado a mano lanza ValueError."""
        # self.lavadero.hacerLavado: (Prelavado: False, Secado a mano: False, Encerado: True)
        with self.assertRaises(ValueError):
            self.lavadero.hacerLavado(False, False, True)

    #Cuando se intenta hacer un lavado mientras que otro ya está en marcha, se produce una ValueError.
    def test3_excepcion_lavado_mientras_ocupado(self):
        """Test 3: Comprueba que iniciar un lavado mientras está ocupado lanza RuntimeError."""
        # Iniciamos un lavado primero
        self.lavadero.hacerLavado(False, False, False)
        
        # Intentamos iniciar otro lavado mientras el primero está en curso
        with self.assertRaises(RuntimeError):
            self.lavadero.hacerLavado(True, True, True)

    #Si seleccionamos un lavado con prelavado a mano, los ingresos de lavadero son 6,50€.
    def test4_ingresos_lavado_con_prelavado(self):
        """Test 4: Verifica los ingresos al hacer un lavado con prelavado a mano."""
        self.lavadero.hacerLavado(True, False, False)
        self.lavadero._cobrar()
        self.assertAlmostEqual(self.lavadero.ingresos, 6.50)

    #Si seleccionamos un lavado con secado a mano, los ingresos son 6,00€.
    def test5_ingresos_lavado_con_secado(self):
        """Test 5: Verifica los ingresos al hacer un lavado con secado a mano."""
        self.lavadero.hacerLavado(False, True, False)
        self.lavadero._cobrar()
        self.assertAlmostEqual(self.lavadero.ingresos, 6.00)

    #Si seleccionamos un lavado con secado a mano y encerado, los ingresos son 7,20€.
    def test6_ingresos_lavado_con_secado_y_encerado(self):
        """Test 6: Verifica los ingresos al hacer un lavado con secado a mano y encerado."""
        self.lavadero.hacerLavado(False, True, True)
        self.lavadero._cobrar()
        self.assertAlmostEqual(self.lavadero.ingresos, 7.20)

    #Si seleccionamos un lavado con prelavado a mano y secado a mano, los ingresos son 7,50€.
    def test7_ingresos_lavado_con_prelavado_y_secado(self):
        """Test 7: Verifica los ingresos al hacer un lavado con prelavado a mano y secado a mano."""
        self.lavadero.hacerLavado(True, True, False)
        self.lavadero._cobrar()
        self.assertAlmostEqual(self.lavadero.ingresos, 7.50)

    #Si seleccionamos un lavado con prelavado a mano, secado a mano y encerado, los ingresos son 8,70€.
    def test8_ingresos_lavado_completo(self):
        """Test 8: Verifica los ingresos al hacer un lavado completo con todas las opciones."""
        self.lavadero.hacerLavado(True, True, True)
        self.lavadero._cobrar()
        self.assertAlmostEqual(self.lavadero.ingresos, 8.70)


    # ----------------------------------------------------------------------
    # Tests de flujo de fases
    # Utilizamos la función def ejecutar_y_obtener_fases(self, prelavado, secado, encerado)
    # ----------------------------------------------------------------------
    def test9_flujo_rapido_sin_extras(self):
        """Test 9: Simula el flujo rápido sin opciones opcionales."""
        fases_esperadas = [0, 1, 3, 4, 5, 6, 0]
         
        # Ejecutar el ciclo completo y obtener las fases
        fases_obtenidas = self.ejecutar_y_obtener_fases(False, False, False)
        
        # Verificar que las fases obtenidas coinciden con las esperadas
        self.assertEqual(fases_obtenidas, fases_esperadas)
        
    
    #Si seleccionamos un lavado con prelavado a mano y vamos avanzando fases, el lavadero pasa por las fases 0, 1, 2, 3, 4, 5, 6, 0.
    def test10_flujo_rapido_con_prelavado(self):
        """Test 10: Simula el flujo rápido con prelavado a mano."""
        fases_esperadas = [0, 1, 2, 3, 4, 5, 6, 0]
         
        # Ejecutar el ciclo completo y obtener las fases
        fases_obtenidas = self.ejecutar_y_obtener_fases(prelavado=True, secado=False, encerado=False)
        
        # Verificar que las fases obtenidas coinciden con las esperadas
        self.assertEqual(fases_obtenidas, fases_esperadas)
        
    #Si seleccionamos un lavado con secado a mano y vamos avanzando fases, el lavadero pasa por las fases 0, 1, 3, 4, 5, 7, 0.12.
    def test11_flujo_rapido_con_secado(self):
        """Test 11: Simula el flujo rápido con secado a mano."""
        fases_esperadas = [0, 1, 3, 4, 5, 7, 0]
         
        # Ejecutar el ciclo completo y obtener las fases
        fases_obtenidas = self.ejecutar_y_obtener_fases(prelavado=False, secado=True, encerado=False)
        
        # Verificar que las fases obtenidas coinciden con las esperadas
        self.assertEqual(fases_obtenidas, fases_esperadas)

    #Si seleccionamos un lavado con secado a mano y encerado y vamos avanzando fases, el lavadero pasa por las fases 0, 1, 3, 4, 5, 7, 8, 0.
    def test12_flujo_rapido_con_secado_y_encerado(self):
        """Test 12: Simula el flujo rápido con secado a mano y encerado."""
        fases_esperadas = [0, 1, 3, 4, 5, 7, 8, 0]
         
        # Ejecutar el ciclo completo y obtener las fases
        fases_obtenidas = self.ejecutar_y_obtener_fases(prelavado=False, secado=True, encerado=True)
        
        # Verificar que las fases obtenidas coinciden con las esperadas
        self.assertEqual(fases_obtenidas, fases_esperadas)

    #Si seleccionamos un lavado con prelavado a mano y secado a mano y vamos avanzando fases, el lavadero pasa por las fases 0, 1, 2, 3, 4, 5, 7, 0.
    def test13_flujo_rapido_con_prelavado_y_secado(self):
        """Test 13: Simula el flujo rápido con prelavado a mano y secado a mano."""
        fases_esperadas = [0, 1, 2, 3, 4, 5, 7, 0]
         
        # Ejecutar el ciclo completo y obtener las fases
        fases_obtenidas = self.ejecutar_y_obtener_fases(prelavado=True, secado=True, encerado=False)
        
        # Verificar que las fases obtenidas coinciden con las esperadas
        self.assertEqual(fases_obtenidas, fases_esperadas)

    #Si seleccionamos un lavado con prelavado a mano, secado a mano y encerado y vamos avanzando fases, el lavadero pasa por las fases 0, 1, 2, 3, 4, 5, 7, 8, 0.
    def test14_flujo_rapido_con_prelavado_secado_y_encerado(self):
        """Test 14: Simula el flujo rápido con prelavado a mano, secado a mano y encerado."""
        fases_esperadas = [0, 1, 2, 3, 4, 5, 7, 8, 0]
         
        # Ejecutar el ciclo completo y obtener las fases
        fases_obtenidas = self.ejecutar_y_obtener_fases(prelavado=True, secado=True, encerado=True)
        
        # Verificar que las fases obtenidas coinciden con las esperadas
        self.assertEqual(fases_obtenidas, fases_esperadas)

# Bloque de ejecución para ejecutar los tests si el archivo es corrido directamente
if __name__ == '__main__':
    unittest.main()
