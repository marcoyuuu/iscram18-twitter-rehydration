@echo off
REM Cambia al directorio del proyecto (opcional si ya estás ahí)
cd /d "%~dp0"

REM Crear entorno virtual si no existe
if not exist ".venv\Scripts\activate" (
    echo Creando entorno virtual con Python 3.11...
    py -3.11 -m venv .venv
)

REM Activar el entorno virtual
call .venv\Scripts\activate

REM Actualizar pip
pip install --upgrade pip

REM Instalar dependencias
pip install -r requirements.txt

REM Ejecutar el script de hidratación
python hydrate_maria.py

pause
