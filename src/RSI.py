"""
Funciones para el hilo de RSI

Este código define funciones para el hilo encargado de calcular el indicador RSI (Índice de Fuerza Relativa).

Funciones:
- thread_rsi: Función principal del hilo que calcula y actualiza el RSI.
- parameters_RSI: Función que calcula y actualiza los valores del RSI.

"""
import logging
import os
from src.VELAS_1 import obtener_datos
from ta.momentum import RSIIndicator
import time


# Crear la carpeta si no existe
log_folder = 'Log.errors'
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

# Ruta completa del archivo de registro
log_file_path = os.path.join(log_folder, 'errors.log')

# Borrar el contenido del archivo si existe
with open(log_file_path, 'w'):
    pass

# Configurar el logger para que guarde los registros en el archivo dentro de la carpeta
logging.basicConfig(filename=log_file_path, level=logging.ERROR)




def thread_rsi(pill2kill, data: dict, barrera , stop_event):
    """
    Función principal del hilo encargado de calcular y actualizar el indicador RSI.

    Parámetros:
    - pill2kill (threading.Event): Evento para señalizar la finalización del hilo.
    - data (dict): Diccionario que contiene datos relacionados con el análisis técnico.
    - barrera (threading.Barrier): Barrera para sincronizar los hilos.

    """
    try:
        print('[Thread RSI] - Waiting for candles...')
        while not data["candles_ready"]:
            time.sleep(1)

        parameters_RSI(data)
        data["rsi_ready"] = True

        print('rsi_ready')

        print('[Thread RSI] - Loading RSI...')

        while not pill2kill.wait(0.1):

            parameters_RSI(data)
            barrera.wait()
            if stop_event.is_set():
                break
    except Exception as e:
            logging.error(f"Error al arrancar el hilo RSI: {e}")

def parameters_RSI(data: dict):
    """
    Calcula y actualiza los valores del indicador RSI.

    Parámetros:
    - data (dict): Diccionario que contiene datos relacionados con el análisis técnico.

    """
    try:

        candle_df = obtener_datos(data["candles"])
        rsi_object = RSIIndicator(candle_df["CLOSE"], window=14, fillna=True)
        rsi_series = rsi_object.rsi()
        data["RSI"] = [rsi_series.iloc[-2], rsi_series.iloc[-3]]

    except Exception as e:
        logging.error(f"Error a la hora de calcular el RSI: {e}")