"""
Funciones para el hilo de órdenes

Este código define funciones para el hilo encargado de gestionar las órdenes de compra y venta.

Funciones:
- thread_orders: Función principal del hilo que gestiona las órdenes de compra y venta.
- condiciones_operacion: Función para establecer las condiciones de operación basadas en análisis técnico.
- beneficio_perdida: Función para gestionar el beneficio o pérdida de las operaciones.

"""
import os
import traceback
import logging

import src.VELAS_1
import src.BotCSV
import datetime

# Crear la carpeta si no existe


SIGNAL_RSI_BUY = 40
SIGNAL_RSI_SELL = 60

CANDLES_BETWEEN_OPERATIONS = 6

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

def thread_orders(pill2kill, data, barrera, operation, total, lotaje, HistoricoDivisas, stop_event):
    """
    Función principal del hilo encargado de gestionar las órdenes de compra y venta.

    Parámetros:
    - stop_event (threading.Event): Evento para señalizar la finalización del hilo.
    - data (dict): Diccionario que contiene datos relacionados con el trading y el análisis técnico.
    - barrera (threading.Barrier): Barrera para sincronizar los hilos.
    - operation (list): Lista para almacenar información sobre las operaciones.
    - total (float): Variable para rastrear el beneficio o pérdida total.

    """
    try:
        nombre_archivo = os.path.basename(HistoricoDivisas)

        # Construir el nuevo path para el archivo CSV en la carpeta Operaciones
        ruta_csv = os.path.join('..', 'Operaciones', nombre_archivo)
        contador = 0
        FLAG = False
        db_csv = src.BotCSV.BotDBCSV(csv_file=ruta_csv)
        db_csv.create_csv()

        while not data["sma_ready"] and not data["fibo_ready"] and not data['rsi_ready']:
            pass

        while not pill2kill.wait(0.1):

            candle_df = src.VELAS_1.obtener_datos(data["candles"])
            cur_time = candle_df['TIME-UTC'].iloc[-1]

            # Actualiza previous_open
            condiciones_operacion(data, operation, candle_df, cur_time, contador, FLAG)
            beneficio_perdida(candle_df, operation, total, db_csv, lotaje)
            barrera.wait()
            if stop_event.is_set():
                break
            # Verifica si cur_time no ha cambiado desde la última iteración

    except Exception as e:
        logging.error(f"Error al abrir las operaciones: {e}")

def condiciones_operacion(data, operation, candle_df, cur_time, contador, FLAG):
    """
    Establece las condiciones de operación basadas en análisis técnico.

    Parámetros:
    - data (dict): Diccionario que contiene datos relacionados con el trading y el análisis técnico.
    - operation (list): Lista para almacenar información sobre las operaciones.
    - candle_df (pd.DataFrame): DataFrame con datos de velas.
    - cur_time (str): Hora actual.

    """
    try:
        if FLAG == False:
            if data['SMA'] == 'Bull' and candle_df['LOW'].iloc[-1] <= data['FIBO_38']['level'] and data['SMA'] != 'Range' \
                    and candle_df['OPEN'].iloc[-1] > candle_df['CLOSE'].iloc[-1] and data['FIBO_38']['min'][1] < \
                    data['FIBO_38']['max'][1] \
                    and data['RSI'][-1] < SIGNAL_RSI_BUY:  # Open buy
                last_operation_time = cur_time
                data['OPERATION'] = ('Comprar', last_operation_time, data["FIBO_61"], data['FIBO_38']['level'])
                print('Comprar, precio: ' + str(data['FIBO_38']['level']) + '; Hora: ' + str(
                    datetime.datetime.fromtimestamp(candle_df['TIME-UTC'].iloc[-1])))
                oper = ['BUY', data['FIBO_38']['level'], data['FIBO_38']['max'][0], data['FIBO_38']['min'][0], data["FIBO_61"], last_operation_time]

                if oper not in operation:
                    operation.append(oper)
                FLAG = True
            elif data['SMA'] == 'Bear' and candle_df['HIGH'].iloc[-1] >= data['FIBO_38']['level'] and data['SMA'] != 'Range' \
                    and candle_df['OPEN'].iloc[-1] < candle_df['CLOSE'].iloc[-1] and data['FIBO_38']['min'][1] > \
                    data['FIBO_38']['max'][1] \
                    and data['RSI'][-1] > SIGNAL_RSI_SELL:  # Open sell
                last_operation_time = cur_time
                data['OPERATION'] = ('Vender', last_operation_time, data["FIBO_61"], data['FIBO_38']['level'])
                print('Vender, precio: ' + str(data['FIBO_38']['level']))
                oper = ['SELL', data['FIBO_38']['level'], data['FIBO_38']['max'][0], data['FIBO_38']['min'][0], data["FIBO_61"], last_operation_time]
                if oper not in operation:
                    operation.append(oper)
                FLAG = True
            elif contador == 6:
                FLAG = False
                contador = 0
        else:
            contador = contador + 1


    except Exception as e:
        logging.error(f"Error en las condiciones para abrir las operaciones: {e}")

def beneficio_perdida(candle_df, operation, total, db_csv, lotaje):
    """
    Gestiona el beneficio o pérdida de las operaciones.

    Parámetros:
    - candle_df (pd.DataFrame): DataFrame con datos de velas.
    - operation (list): Lista para almacenar información sobre las operaciones.
    - total (float): Variable para rastrear el beneficio o pérdida total.
    - db_csv (BotCSV.BotDBCSV): Instancia de la clase BotDBCSV para interactuar con el archivo CSV.
    - lotaje (float): El lotaje para calcular el stop loss y el take profit.

    """
    try:

        if len(operation) != 0:
            for i, op in enumerate(operation):
                apalancamiento = 30  # Apalancamiento 1:30

                if operation[i][0] == 'SELL':
                    stop_loss = op[4] + (op[4] * 0.001)
                    take_profit = take_expansion_fibonacci(op[1], op[3], op[2], 'SELL')

                    beneficio_take_profit = abs(op[1] - take_profit) * lotaje * (10 ** 4)
                    beneficio_stop_loss = (op[1] - stop_loss) * lotaje * (10 ** 4)

                    if candle_df['LOW'].iloc[-1] < take_profit:
                        total += beneficio_take_profit
                        db_csv.insert_operation('SELL', datetime.datetime.fromtimestamp(op[5]),
                                                datetime.datetime.fromtimestamp(candle_df['TIME-UTC'].iloc[-1]), op[1],
                                                take_profit, beneficio_take_profit)
                        print(f'Take profit: {take_profit}, Beneficio: {beneficio_take_profit}')
                        del operation[i]

                    elif candle_df['HIGH'].iloc[-1] > stop_loss:
                        total -= beneficio_stop_loss
                        db_csv.insert_operation('SELL', datetime.datetime.fromtimestamp(op[5]),
                                                datetime.datetime.fromtimestamp(candle_df['TIME-UTC'].iloc[-1]), op[1],
                                                stop_loss, '-' + str(beneficio_stop_loss))
                        print(f'Precio entrada: {op[1]}, Stop Loss: {stop_loss}, Pérdida: {beneficio_stop_loss}')
                        del operation[i]

                elif operation[i][0] == 'BUY':
                    stop_loss = op[4] - (op[4] * 0.001)
                    take_profit = take_expansion_fibonacci(op[1], op[3], op[2], 'BULL')

                    beneficio_take_profit = abs(take_profit - op[1]) * lotaje * (10 ** 4)
                    beneficio_stop_loss = (stop_loss - op[1]) * lotaje * (10 ** 4)

                    if candle_df['HIGH'].iloc[-1] > take_profit:
                        total += beneficio_take_profit
                        db_csv.insert_operation('BUY', datetime.datetime.fromtimestamp(op[5]),
                                                datetime.datetime.fromtimestamp(candle_df['TIME-UTC'].iloc[-1]), op[1],
                                                take_profit, beneficio_take_profit)
                        print(f'Take profit: {take_profit}, Beneficio: {beneficio_take_profit}')
                        del operation[i]

                    elif candle_df['LOW'].iloc[-1] < stop_loss:
                        total -= beneficio_stop_loss
                        db_csv.insert_operation('BUY', datetime.datetime.fromtimestamp(op[5]),
                                                datetime.datetime.fromtimestamp(candle_df['TIME-UTC'].iloc[-1]), op[1],
                                                stop_loss, '-' + str(beneficio_stop_loss))
                        print(f'Precio entrada: {op[1]}, Stop Loss: {stop_loss}, Pérdida: {beneficio_stop_loss}')
                        del operation[i]
    except Exception as e:
        logging.error(f"Error al gestionar beneficio/pérdida: {e}")
        traceback.print_exc()

def take_expansion_fibonacci( entrada, min, max, tipo):
        if tipo == 'BULL':
            distancia = entrada - min
            salida = entrada + distancia
            return salida

        elif tipo == 'SELL':
            distancia = max - entrada
            salida = entrada - distancia
            return salida