"""
Clase Bot

Esta clase representa un bot de trading que utiliza varios hilos para realizar diversas tareas, como procesar datos de velas, calcular indicadores técnicos y realizar operaciones de trading.

Atributos:
- threads (lista): Una lista para almacenar objetos de hilo para diferentes tareas.
- data (diccionario): Un diccionario para almacenar diversos datos relacionados con el trading y el análisis técnico.
- operation (lista): Una lista para almacenar información sobre operaciones de trading.
- pill2kill (threading.Event): Un evento para señalizar a los hilos que detengan la ejecución.
- mutex (threading.Lock): Un cerrojo para gestionar el acceso a recursos compartidos.
- barrera (threading.Barrier): Una barrera para sincronizar hilos.
- total (int): Un contador para realizar un seguimiento de algún valor total.

Métodos:
- __init__: Método del constructor para inicializar la instancia del bot.
- thread_candle: Método para lanzar un hilo para procesar datos de velas.
- thread_RSI: Método para lanzar un hilo para calcular el RSI.
- thread_orders: Método para lanzar un hilo para gestionar órdenes de trading.
- thread_sma: Método para lanzar un hilo para calcular la SMA.
- thread_fibonacci: Método para lanzar un hilo para el análisis de Fibonacci.
- kill_threads: Método para detener todos los hilos en ejecución.
- wait: Método para esperar la entrada del usuario y detener el bot.

"""
import logging
import os
import src.FIBO
import src.SMA
import src.VELAS, src.RSI, threading, src.ORDER


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

class Bot:
    def __init__(self, lotaje, HistoricoDivisas):
        """
        Inicializa la instancia del bot.

        Atributos:
        - threads: Lista para almacenar objetos de hilo para diferentes tareas.
        - data: Diccionario para almacenar varios datos relacionados con el trading y el análisis técnico.
        - operation: Lista para almacenar información sobre operaciones de trading.
        - pill2kill: Evento para señalizar a los hilos que detengan la ejecución.
        - mutex: Cerrojo para gestionar el acceso a recursos compartidos.
        - barrera: Barrera para sincronizar hilos.
        - total: Contador para realizar un seguimiento de algún valor total.

        """
        try:
            self.threads = []
            self.data = {
                'candles': [],
                'RSI': [],
                'SMA': [],
                'SUPPORT': [],
                'RESISTANCE': [],
                'FIBO_61': [],
                'FIBO_38': {
                    'level': [],
                    'max': [],
                    'min': [],
                },
                'OPERATION': [],
                'candles_ready': False,
                'levels_ready': False,
                'rsi_ready': False,
                'sma_ready': False,
                'fibo_ready': False
            }
            self.operation = []
            self.pill2kill = threading.Event()
            self.stop_event = threading.Event()
            self.barrera = threading.Barrier(5)
            self.total = 0
            self.fichero = HistoricoDivisas
            self.lotaje = lotaje


        except Exception as e:
            logging.error(f"Error a la hora de inicializar el Bot: {e}")
    def thread_candle(self):
        """
        Lanza un hilo para procesar datos de velas.

        """
        try:
            t = threading.Thread(target=src.VELAS.thread_candles,
                                 args=(self.pill2kill, self.data, self.barrera, self.fichero, self.stop_event))
            self.threads.append(t)
            t.start()
            print('Hilo - VELA. Lanzado')
        except Exception as e:
            logging.error(f"Error a la hora de lanzar el hilo candle: {e}")

    def thread_RSI(self):
        """
        Lanza un hilo para calcular el RSI.

        """
        try:
            t = threading.Thread(target=src.RSI.thread_rsi,
                                 args=(self.pill2kill, self.data, self.barrera, self.stop_event))
            self.threads.append(t)
            t.start()
            print('Hilo - RSI. Lanzado')
        except Exception as e:
            logging.error(f"Error a la hora de lanzar el hilo RSI: {e}")

    def thread_orders(self):
        """
        Lanza un hilo para gestionar órdenes de trading.

        """
        try:
            t = threading.Thread(target=src.ORDER.thread_orders,
                                 args=(self.pill2kill, self.data, self.barrera, self.operation, self.total, self.lotaje, self.fichero, self.stop_event))
            self.threads.append(t)
            t.start()
            print('Hilo - ÓRDENES. Lanzado')
        except Exception as e:
            logging.error(f"Error a la hora de lanzar el hilo orders: {e}")

    def thread_sma(self):
        """
        Lanza un hilo para calcular la SMA.

        """
        try:
            t = threading.Thread(target=src.SMA.thread_SMA,
                                 args=(self.pill2kill, self.data, self.barrera, self.stop_event))
            self.threads.append(t)
            t.start()
            print('Hilo - SMA. Lanzado')
        except Exception as e:
            logging.error(f"Error a la hora de lanzar el hilo SMA: {e}")

    def thread_fibonacci(self):
        """
        Lanza un hilo para el análisis de Fibonacci.

        """
        try:
            t = threading.Thread(target=src.FIBO.thread_fibonacci,
                                 args=(self.pill2kill, self.data, self.barrera, self.stop_event))
            self.threads.append(t)
            t.start()
            print('Hilo - FIBO. Lanzado')
        except Exception as e:
            logging.error(f"Error a la hora de lanzar el hilo fibonacci: {e}")

    def kill_threads(self):
        """
        Detiene todos los hilos en ejecución.

        """
        try:
            self.pill2kill.set()
            self.stop_event.set()
            for thread in self.threads:
                thread.join()
            print('Hilos - Deteniendo hilos')
        except Exception as e:
            logging.error(f"Error a la hora de terminar con los hilos: {e}")

    """def wait(self):
        
        Espera la entrada del usuario para detener el bot.

        
        try:
            print('\nPresiona ENTER para detener el bot\n')
            input()
            self.kill_threads()
        except Exception as e:
            logging.error(f"Error a la hora de terminar el bot: {e}")"""

    def stop(self):
        """
                Ayuda a detiene todos los hilos en ejecución.

        """
        try:
            while not self.stop_event.is_set():
                pass
            self.kill_threads()

        except Exception as e:
            logging.error(f"Error a la hora de terminar con los hilos: {e}")


