"""
Clase Candle y funciones relacionadas para el manejo de velas japonesas.

Clase:
- Candle: Representa una vela japonesa con sus atributos y métodos.

Funciones:
- from_list_to_df: Convierte una lista de objetos Candle en un DataFrame de pandas.

"""
import logging
import os
import pandas as pd

# Crear la carpeta si no existe
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

class Candle:
    """
    Clase para representar una vela japonesa.

    Atributos:
    - time_last_candle (int): Tiempo de la última vela.
    - open (float): Precio de apertura de la vela.
    - close (float): Precio de cierre de la vela.
    - high (float): Precio máximo alcanzado durante la vela.
    - low (float): Precio mínimo alcanzado durante la vela.
    - volume (float): Volumen de la vela.

    Métodos:
    - set_open: Establece los valores de los atributos al abrir una vela.
    - get_info: Devuelve una lista con la información de la vela.
    """

    def __init__(self):
        self.time_last_candle = 0
        self.open = 0
        self.close = 0
        self.high = 0
        self.low = 0
        self.volume = 0

    def set(self, timestamp, open, high, low, close, tick_volume):
        """
        Establece los valores de los atributos al abrir una vela.

        Parámetros:
        - timestamp (int): Tiempo de la vela.
        - open (float): Precio de apertura de la vela.
        - high (float): Precio máximo alcanzado durante la vela.
        - low (float): Precio mínimo alcanzado durante la vela.
        - close (float): Precio de cierre de la vela.
        - tick_volume (float): Volumen de la vela.

        """
        try:
            self.time_last_candle = timestamp
            self.open = open
            self.close = close
            self.high = high
            self.low = low
            self.volume = tick_volume
        except Exception as e:
            logging.error(f"An unexpected error occurred in set_open: {e}")

    def get(self):
        """
        Devuelve una lista con la información de la vela.

        Devuelve:
        - List[float]: Lista con los valores de open, close, high, low, volume y timestamp.

        """
        try:
            return [self.open, self.close, self.high, self.low, self.volume, self.time_last_candle]
        except Exception as e:
            logging.error(f"Error a la hora obtener los datos: {e}")


def obtener_datos(candles):
    """
    Convierte una lista de objetos Candle en un DataFrame de pandas.

    Parámetros:
    - candles (list): Lista de objetos Candle.

    Devuelve:
    - pd.DataFrame: DataFrame de pandas con columnas OPEN, CLOSE, HIGH, LOW, VOLUME y TIME-UTC.

    """
    try:
        candle_df = pd.DataFrame(columns=["OPEN", "CLOSE", "HIGH", "LOW", "VOLUME", "TIME-UTC"])
        for i, candle in enumerate(candles):
            candle_df.loc[i] = candle.get()
        return candle_df
    except Exception as e:
            logging.error(f"Error a la hora de convertir los datos de las velas: {e}")
            return pd.DataFrame()