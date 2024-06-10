"""
Funciones para el hilo de Velas Japonesas (Candles)

Este código define funciones para el hilo encargado de cargar y actualizar las velas japonesas desde un archivo CSV.

Funciones:
- update_candles: Carga y actualiza las velas japonesas desde un archivo CSV.
- thread_candles: Función principal del hilo que carga y actualiza las velas japonesas.

"""

import csv
import logging
import os
import pandas as pd
from src.VELAS_1 import Candle
import datetime

WINDOW_CANDLES = 200

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


def update_candles(fichero):
    """
    Carga y actualiza las velas japonesas desde un archivo CSV.

    Parámetros:
    - fichero (str): Ruta del archivo CSV con las velas japonesas.

    Devuelve:
    - candles (list): Lista de objetos Candle, puede ser una lista vacía si hay un error o no hay datos.
    """

    # Abre el archivo CSV para leer los datos de las velas
    candles = []
    try:
        with open(fichero, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            next(reader)  # Salta el encabezado

            for i, row in enumerate(reader, start=1):
                try:
                    # Verificamos si la fila contiene información de hora
                    if any(':' in column for column in row):  # Suponiendo que la tercera columna contiene la hora
                        fecha_hora_str = row[0].replace(".", "-") + " " + row[1]
                        fecha_hora_obj = datetime.datetime.strptime(fecha_hora_str, '%Y-%m-%d %H:%M:%S')
                        fecha_hora_timestamp = int(fecha_hora_obj.timestamp())

                        if len(candles) < WINDOW_CANDLES:
                            candle = Candle()
                            candle.set(fecha_hora_timestamp, float(row[2]), float(row[3]),
                                       float(row[4]), float(row[5]), float(row[6]))
                            candles.append(candle)

                    else:
                        # Procesamiento para el caso en que no hay información de hora
                        fecha_str = row[0].replace(".", "-")  # Suponiendo que la fecha está en la primera columna
                        fecha_obj = datetime.datetime.strptime(fecha_str, '%Y-%m-%d')
                        fecha_timestamp = int(fecha_obj.timestamp())

                        if len(candles) < WINDOW_CANDLES:
                            candle = Candle()
                            candle.set(fecha_timestamp, float(row[1]), float(row[2]),
                                       float(row[3]), float(row[4]), float(row[5]))
                            candles.append(candle)

                except ValueError as e:
                    logging.error(f"Error al convertir fecha y hora en la línea {i}: {e}")

    except Exception as e:
        logging.error(f"Error en el arranque del hilo velas: {e}")

    return candles

def thread_candles(pill2kill, data, barrera, fichero, stop_event):
    """
    Función principal del hilo encargado de cargar y actualizar las velas japonesas.

    Parámetros:
    - pill2kill (threading.Event): Evento para señalizar la finalización del hilo.
    - data (dict): Diccionario que contiene datos relacionados con las velas japonesas.
    - barrera (threading.Barrier): Barrera para sincronizar los hilos.
    """
    try:
        candle_df = pd.DataFrame(columns=["OPEN", "CLOSE", "HIGH", "LOW", "VOLUME", "TIME-UTC"])

        data['candles'] = update_candles(fichero)
        data["candles_ready"] = True

        with open(fichero, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            next(reader)  # Salta el encabezado

            # Inicializa un índice para recorrer las filas del archivo CSV
            fila_actual = 0
            lineas = list(reader)  # Convertimos el iterador reader a una lista para poder indexar

            while not pill2kill.wait(0.1):


                row = lineas[fila_actual]
                try:
                    if any(':' in column for column in row):  # Verifica si la fila tiene información de hora
                        fecha_hora_str = row[0].replace(".", "-") + " " + row[1]
                        fecha_hora_obj = datetime.datetime.strptime(fecha_hora_str, '%Y-%m-%d %H:%M:%S')
                        fecha_hora_timestamp = int(fecha_hora_obj.timestamp())

                        candle = Candle()
                        candle.set(fecha_hora_timestamp, float(row[2]), float(row[3]),
                                   float(row[4]), float(row[5]), float(row[6]))
                        data['candles'].append(candle)
                    else:
                        # Procesamiento para el caso en que no hay información de hora
                        fecha_str = row[0].replace(".", "-")  # Suponiendo que la fecha está en la primera columna
                        fecha_obj = datetime.datetime.strptime(fecha_str, '%Y-%m-%d')
                        fecha_timestamp = int(fecha_obj.timestamp())

                        candle = Candle()
                        candle.set(fecha_timestamp, float(row[1]), float(row[2]),
                                   float(row[3]), float(row[4]), float(row[5]))
                        data['candles'].append(candle)

                    if len(data['candles']) > WINDOW_CANDLES:
                        del data['candles'][0]

                except ValueError as e:
                    logging.error(f"Error al convertir fecha y hora en la línea {fila_actual + 1}: {e}")

                fila_actual += 1  # Incrementa el índice para la siguiente fila

                barrera.wait()
                if fila_actual >= len(lineas):
                    print("Se ha alcanzado el final del archivo.")
                    stop_event.set()
                    break

            print("VELAS.")

    except Exception as e:
        logging.error(f"Error en el hilo: {e}")


