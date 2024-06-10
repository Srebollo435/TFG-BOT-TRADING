#!/bin/bash
# Guardar la ruta del directorio donde se encuentra el script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Navegar al directorio del script
cd "$SCRIPT_DIR"

# Activar el entorno virtual
source venv/bin/activate

# Instalar las dependencias (si es necesario)
pip install -r requirements.txt

cd src

# Ejecutar el bot de trading (asegúrate de cambiar 'main.py' al archivo principal de tu bot)
python3 main.py

cd ..

# Desactivar el entorno virtual
deactivate

read -p "Presiona cualquier tecla para salir..."
