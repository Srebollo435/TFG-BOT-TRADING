"""
Clase BotDBCSV

Esta clase proporciona una interfaz simple para interactuar con un archivo CSV que almacena información sobre operaciones de trading.

Atributos:
- csv_file (str): Ruta al archivo CSV.

Métodos:
- __init__: Constructor que recibe la ruta al archivo CSV.
- create_csv: Método para crear el archivo CSV con encabezados si no existe.
- insert_operation: Método para insertar una nueva operación en el archivo CSV.

Ejemplo de uso:
db_csv = BotDBCSV(csv_file='operaciones.csv')

# Crear el archivo CSV si no existe
db_csv.create_csv()

# Insertar operaciones
db_csv.insert_operation('Compra', '2023-01-01 12:00:00', '2023-01-01 13:00:00', 100.0, 110.0, 10.0)
db_csv.insert_operation('Venta', '2023-02-01 14:00:00', '2023-02-01 15:00:00', 120.0, 115.0, -5.0)

"""

import csv
import logging
import os

log_folder = r'C:\Users\Usuario\PycharmProjects\TFG-BOT_TRADING - csv - copia\Log.errors'
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

# Ruta completa del archivo de registro
log_file_path = os.path.join(log_folder, 'errors.log')

# Borrar el contenido del archivo si existe
with open(log_file_path, 'w'):
    pass

# Configurar el logger para que guarde los registros en el archivo dentro de la carpeta
logging.basicConfig(filename=log_file_path, level=logging.ERROR)


class BotDBCSV:

    def __init__(self, csv_file):
        """
        Constructor de la clase BotDBCSV.

        Parámetros:
        - csv_file (str): Ruta al archivo CSV.

        """
        self.csv_file = csv_file

    def create_csv(self):
        """
        Crea el archivo CSV con encabezados si no existe.

        """
        try:
            with open(self.csv_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['tipo_operacion', 'fecha_apertura', 'fecha_cierre', 'precio_apertura', 'precio_cierre',
                                 'dinero_ganado_perdido'])
        except Exception as e:
            logging.error(f"Error en la creación del archivo csv: {e}")

    def insert_operation(self, tipo_operacion, fecha_apertura, fecha_cierre, precio_apertura, precio_cierre, dinero_ganado_perdido):
        """
        Inserta una nueva operación en el archivo CSV.

        Parámetros:
        - tipo_operacion (str): Tipo de operación ('Compra' o 'Venta').
        - fecha_apertura (str): Fecha de apertura en formato 'YYYY-MM-DD HH:MM:SS'.
        - fecha_cierre (str): Fecha de cierre en formato 'YYYY-MM-DD HH:MM:SS'.
        - precio_apertura (float): Precio de apertura de la operación.
        - precio_cierre (float): Precio de cierre de la operación.
        - dinero_ganado_perdido (float): Cantidad de dinero ganado o perdido en la operación.

        """
        try:
            with open(self.csv_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([tipo_operacion, fecha_apertura, fecha_cierre, precio_apertura, precio_cierre,
                                 dinero_ganado_perdido])

        except Exception as e:
            logging.error(f"Error a la hora de insertar los datos en el csv: {e}")