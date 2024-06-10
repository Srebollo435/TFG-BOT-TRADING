import os
import sys


# Trabajo de Fin de Grado
# Ingeniería Informática
# Universidad de Burgos
# Realizado por Sergio Rebollo Ortega

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import Interfaz
from src import BOT
import tkinter as tk


# Punto de entrada de la aplicación
if __name__ == "__main__":
    # Crear la ventana principal
    root = tk.Tk()

    # Inicializar la interfaz del bot de trading
    app = Interfaz.TradingBotUI(root)

    # Iniciar el bucle principal de la interfaz gráfica
    root.mainloop()




