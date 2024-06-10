"""
Este script proporciona una interfaz de usuario para configurar y ejecutar un bot de trading.

El usuario puede seleccionar el lotaje y el archivo CSV histórico a utilizar para el bot.
El bot se inicia cuando se presiona el botón "Iniciar Bot", siempre que se haya seleccionado
un lotaje válido y un archivo CSV histórico.

El bot realiza varias operaciones basadas en el análisis técnico de los datos históricos,
como cálculo de velas, índice de fuerza relativa (RSI), medias móviles simples (SMA) y niveles
de Fibonacci.

El resultado de las operaciones se guarda en un archivo de registro y se muestra al usuario.
"""

import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import os
import traceback
import logging
from src import BOT

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

class TradingBotUI:

    def __init__(self, root):
        """
        Inicializa la interfaz de usuario del bot de trading.

        Args:
            root: La ventana principal de la interfaz de usuario.
        """
        self.root = root
        self.root.title("Configuración del Bot de Trading")

        self.lotaje_label = tk.Label(root, text="Lotaje:")
        self.lotaje_label.grid(row=0, column=0, padx=10, pady=10)

        self.lotaje_entry = tk.Entry(root)
        self.lotaje_entry.grid(row=0, column=1, padx=10, pady=10)

        self.historico_label = tk.Label(root, text="Seleccionar Historico:")
        self.historico_label.grid(row=1, column=0, padx=10, pady=10)

        self.historico_combobox = ttk.Combobox(root, state="readonly", width=30)
        self.historico_combobox.grid(row=1, column=1, padx=10, pady=10)

        self.select_historico_files()

        self.start_button = tk.Button(root, text="Iniciar Bot", command=self.start_bot)
        self.start_button.grid(row=2, column=0, columnspan=2, pady=10)

    def select_historico_files(self):
        """
        Selecciona los archivos históricos disponibles y los muestra en un menú desplegable.
        """
        try:
            historico_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                            "HistóricosDivisas")

            csv_files = [f for f in os.listdir(historico_folder) if f.endswith('.csv')]

            self.historico_combobox['values'] = csv_files
            self.historico_combobox.set("Seleccionar archivo")
        except Exception as e:
            messagebox.showerror("Error", f"Error al seleccionar archivos históricos: {e}")
            traceback.print_exc()

    def start_bot(self):
        """
        Inicia el bot de trading con la configuración especificada por el usuario.
        """
        lotaje = self.lotaje_entry.get()
        selected_file = self.historico_combobox.get()

        if not lotaje or selected_file == "Seleccionar archivo":
            messagebox.showwarning("Advertencia", "Por favor, selecciona el lotaje y el archivo CSV.")
        else:
            try:
                lotaje = float(lotaje)  # Intentar convertir lotaje a un número decimal
                historico_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                "HistóricosDivisas", selected_file)

                if os.path.exists(historico_folder):
                    self.run_bot(lotaje, historico_folder, selected_file)
                    self.root.destroy()
                else:
                    messagebox.showwarning("Advertencia",
                                           f"No se pudo encontrar el archivo histórico: {historico_folder}")
            except ValueError:
                messagebox.showwarning("Advertencia", "El lotaje debe ser un número entero o decimal.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al iniciar el bot: {e}")
                traceback.print_exc()

    def run_bot(self, lotaje, historico_folder, selected_file):
        """
        Ejecuta el bot de trading con la configuración especificada.

        Args:
            lotaje: El tamaño de lote para las operaciones del bot.
            historico_folder: La carpeta que contiene el archivo CSV histórico.
            selected_file: El archivo CSV histórico seleccionado por el usuario.
        """
        try:
            print(f"Iniciando el bot con lotaje {lotaje} y datos históricos en {historico_folder}")

            Bot1 = BOT.Bot(lotaje, historico_folder)
            Bot1.thread_candle()
            Bot1.thread_RSI()
            Bot1.thread_sma()
            Bot1.thread_fibonacci()
            Bot1.thread_orders()
            Bot1.stop()

            operaciones_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                              "Operaciones")
            operaciones_file = os.path.join(operaciones_folder, selected_file)
            if os.path.exists(operaciones_file):
                print('El fichero existe: ' + operaciones_file)
                subprocess.Popen(['notepad.exe', operaciones_file], shell=True)
            else:
                print(f"El archivo de operaciones {operaciones_file} no existe.")
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la ejecución del bot: {e}")
            traceback.print_exc()