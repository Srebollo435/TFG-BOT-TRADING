"""
Funciones para el hilo de SMA (Simple Moving Average)

Este código define funciones para el hilo encargado de calcular y actualizar la Media Móvil Simple (SMA).

Funciones:
- thread_SMA: Función principal del hilo que calcula y actualiza la SMA.
- parameters_SMA: Función que calcula y actualiza los valores de la SMA.

"""

import logging
import os
from src.VELAS_1 import obtener_datos
import time

# Crear la carpeta si no exist
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

def thread_SMA(pill2kill, data: dict, barrera, stop_event):
    """
    Función principal del hilo encargado de calcular y actualizar la Media Móvil Simple (SMA).

    Parámetros:
    - pill2kill (threading.Event): Evento para señalizar la finalización del hilo.
    - data (dict): Diccionario que contiene datos relacionados con el análisis técnico.
    - barrera (threading.Barrier): Barrera para sincronizar los hilos.

    """
    try:

        print('[Thread SMA] - Waiting for candles...')

        while not data["candles_ready"]:
            time.sleep(1)

        parameters_SMA(data)
        data["sma_ready"] = True

        print('sma_ready')

        print('[Thread SMA] - Loading SMA...')

        while not pill2kill.wait(0.1):

            candle_df = obtener_datos(data["candles"])

            parameters_SMA(data)
            barrera.wait()
            if stop_event.is_set():
                break
    except Exception as e:
        logging.error(f"Error en el arranque del hilo SMA: {e}")

def parameters_SMA(data: dict):
    """
    Calcula y actualiza los valores de la Media Móvil Simple (SMA).

    Parámetros:
    - data (dict): Diccionario que contiene datos relacionados con el análisis técnico.

    """
    try:

        candle_df = obtener_datos(data["candles"])
        Media = candle_df['CLOSE'].rolling(window=200).mean()
        # Media = TA.SMA(candle_df, period=100)
        last_close = candle_df['CLOSE'].iloc[-1]

        candle_df.set_index('TIME-UTC', inplace=True)

        tolerance = 0.005

        if last_close > Media.iloc[-1] * (1 + tolerance):
            data["SMA"] = 'Bull'
        elif last_close < Media.iloc[-1] * (1 - tolerance):
            data["SMA"] = 'Bear'
        else:
            data["SMA"] = 'Range'

    except Exception as e:
        logging.error(f"Error en el cálculo de la tendencia del precio: {e}")
