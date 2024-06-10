"""
Funciones para el hilo de niveles de Fibonacci

Este código define funciones para el hilo encargado de calcular niveles de Fibonacci basados en datos de velas.

Funciones:
- thread_fibonacci: Función principal del hilo que calcula los niveles de Fibonacci y los carga en el diccionario de datos.
- maximos_minimos: Función auxiliar para encontrar máximos y mínimos en el conjunto de datos de velas.

"""
import logging
import os
import src.VELAS_1
import numpy as np
import time


CANDLES_BETWEEN_OPERATIONS = 10

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

def thread_fibonacci(pill2kill, data: dict, barrera, stop_event):
    """
    Función principal del hilo encargado de calcular los niveles de Fibonacci.

    Parámetros:
    - pill2kill (threading.Event): Evento para señalizar la finalización del hilo.
    - data (dict): Diccionario que contiene datos relacionados con el trading y el análisis técnico.
    - barrera (threading.Barrier): Barrera para sincronizar los hilos.

    """
    try:
        print('[Hilo Niveles de Fibonacci] - Esperando velas...')

        max_min = {'max': [],
                   'min': []}

        while not data["candles_ready"]:
            time.sleep(1)

        data["fibo"] = True

        # Calcular los niveles de soporte y resistencia
        candle_df = src.VELAS_1.obtener_datos(data["candles"])
        maximos_minimos(candle_df, max_min, data)

        data["fibo_ready"] = True

        print('fibo_ready')

        print('[Hilo Niveles de Fibonacci] - Cargando FIBO...')

        while not pill2kill.wait(0.1):

            candle_df = src.VELAS_1.obtener_datos(data["candles"])
            cur_time = candle_df['TIME-UTC'].iloc[-1]

            max = candle_df["HIGH"].iloc[-1]
            min = candle_df["LOW"].iloc[-1]

            if data['SMA'] == 'Range':

                last_50_LOW = candle_df['LOW'].tail(40)
                last_50_HIGH = candle_df['HIGH'].tail(40)

                max_min['max'] = last_50_HIGH.max()
                max_min['min'] = last_50_LOW.min()

            else:

                if len(data['OPERATION']) > 0:

                    if data['OPERATION'][0] == 'Comprar':
                        max_min['min'] = max_min['max']
                        data['OPERATION'] = {}

                    elif data['OPERATION'][0] == 'Vender':
                        max_min['max'] = max_min['min']
                        data['OPERATION'] = {}

                else:

                    if max_min['max'] < max:
                        retro_61 = max_min['min'] + (max - max_min['min']) * 0.618
                        retro_38 = max_min['min'] + (max - max_min['min']) * 0.382
                        max_min['max'] = max
                        data["FIBO_61"] = retro_38
                        data["FIBO_38"]['level'] = retro_61
                        data["FIBO_38"]['max'] = max, candle_df["TIME-UTC"].iloc[-1]

                    if max_min['min'] > min:
                        retro_61 = min + (max_min['max'] - min) * 0.618
                        retro_38 = min + (max_min['max'] - min) * 0.382
                        max_min['min'] = min
                        data["FIBO_61"] = retro_38
                        data["FIBO_38"]['level'] = retro_61
                        data["FIBO_38"]['min'] = min, candle_df["TIME-UTC"].iloc[-1]
            barrera.wait()
            if stop_event.is_set():
                break

        print("FIBO.")
    except Exception as e:
        logging.error(f"Error al calcular las zonas de fibonacci: {e}")

def maximos_minimos(candle_df, max_min: dict, data):
    """
    Función auxiliar para encontrar máximos y mínimos en el conjunto de datos de velas.

    Parámetros:
    - candle_df (pd.DataFrame): DataFrame con datos de velas.
    - max_min (dict): Diccionario para almacenar máximos y mínimos.
    - data (dict): Diccionario que contiene datos relacionados con el trading y el análisis técnico.

    """
    try:
        max = np.array(candle_df["HIGH"])
        min = np.array(candle_df["LOW"])

        n = 1

        new_max = max[:-n]
        new_min = min[:-n]

        indice_maximo = new_max.argmax()
        indice_minimo = new_min.argmin()

        tiempo_maximo = candle_df.iloc[indice_maximo]["TIME-UTC"]
        tiempo_minimo = candle_df.iloc[indice_minimo]["TIME-UTC"]

        max_min['max'] = new_max.max()
        max_min['min'] = new_min.min()

        data["FIBO_38"]['max'] = max_min['max'], tiempo_maximo
        data["FIBO_38"]['min'] = max_min['min'], tiempo_minimo

    except Exception as e:
        logging.error(f"Error al calcular los mínimos y los máximos: {e}")
