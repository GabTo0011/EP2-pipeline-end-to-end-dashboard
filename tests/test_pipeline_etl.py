import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import requests
import sys
import os

# Añadimos la ruta del proyecto al sys.path para poder importar el pipeline
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from etl.pipeline_etl import extraer_datos, guardar_csv, ejecutar_pipeline

class TestPipelineETL(unittest.TestCase):

    @patch('etl.pipeline_etl.requests.get')
    def test_extraer_datos_success(self, mock_get):
        """
        Prueba que la función extraer_datos procese correctamente una respuesta exitosa de la API.
        """
        # Preparamos una respuesta simulada (mock) exitosa de la API
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [{'id': 1, 'nombre': 'test'}]
        mock_get.return_value = mock_response

        # Ejecutamos la función a probar
        datos = extraer_datos("http://fakeurl.com/api/test")

        # Verificamos que el resultado sea el esperado
        self.assertEqual(datos, [{'id': 1, 'nombre': 'test'}])
        mock_get.assert_called_once_with("http://fakeurl.com/api/test")

    @patch('etl.pipeline_etl.requests.get')
    def test_extraer_datos_failure(self, mock_get):
        """
        Prueba que la función extraer_datos maneje correctamente un error de la API.
        """
        # Preparamos una respuesta simulada con error (ej. 404 Not Found)
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        # Verificamos que la función levante la excepción esperada
        with self.assertRaises(requests.exceptions.HTTPError):
            extraer_datos("http://fakeurl.com/api/error")

    @patch('pandas.DataFrame.to_csv')
    def test_guardar_csv(self, mock_to_csv):
        """
        Prueba que la función guardar_csv llame correctamente al método to_csv de pandas.
        """
        # Datos de prueba
        datos_prueba = [{'col1': 'a', 'col2': 1}, {'col1': 'b', 'col2': 2}]
        nombre_archivo_prueba = "test.csv"

        # Ejecutamos la función
        guardar_csv(datos_prueba, nombre_archivo_prueba)

        # Verificamos que to_csv fue llamado una vez con los argumentos correctos
        mock_to_csv.assert_called_once_with(
            nombre_archivo_prueba,
            index=False,
            encoding="utf-8"
        )

    @patch('etl.pipeline_etl.guardar_csv')
    @patch('etl.pipeline_etl.extraer_datos')
    def test_ejecutar_pipeline(self, mock_extraer, mock_guardar):
        """
        Prueba la ejecución completa del pipeline, verificando que se llamen las funciones
        de extracción y guardado para cada fuente de datos.
        """
        # Configuramos el mock para que no haga nada cuando se llame
        mock_extraer.return_value = [{'data': 'dummy'}]

        # Ejecutamos el pipeline
        ejecutar_pipeline()

        # Verificamos que la función de extracción se llamó 5 veces (una por cada URL)
        self.assertEqual(mock_extraer.call_count, 5)
        # Verificamos que la función de guardado se llamó 5 veces
        self.assertEqual(mock_guardar.call_count, 5)

if __name__ == '__main__':
    # Para generar un informe de las pruebas en formato XML
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)