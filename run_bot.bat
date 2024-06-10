@echo off
REM Guardar la ruta del directorio donde se encuentra el .bat
set SCRIPT_DIR=%~dp0

REM Navegar al directorio del script
cd /d "%SCRIPT_DIR%"

REM Activar el entorno virtual
call venv\Scripts\activate.bat

REM Instalar las dependencias (si es necesario)
pip install -r requirements.txt

cd src

REM Ejecutar el bot de trading (asegúrate de cambiar 'main.py' al archivo principal de tu bot)
python main.py

REM
cd ..

REM Desactivar el entorno virtual
deactivate

pause