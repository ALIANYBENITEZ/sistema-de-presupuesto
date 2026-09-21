"""
Archivo WSGI de EJEMPLO para PythonAnywhere.

NO se ejecuta en local. Es la plantilla que hay que pegar en el archivo WSGI
que PythonAnywhere genera al crear la Web App (en la pestaña "Web" del panel,
enlace "WSGI configuration file").

IMPORTANTE:
  - Reemplazá 'TU_USUARIO' por tu nombre de usuario real de PythonAnywhere.
  - La ruta del proyecto debe apuntar a donde clonaste el repositorio.
  - Si clonaste con git, la carpeta suele quedar en:
        /home/TU_USUARIO/sistema_de_presupuesto/vielma-moto-repuestos
    Ajustá la ruta según dónde haya quedado tu app.py.
"""

import sys
import os

# 1) Ruta ABSOLUTA a la carpeta que contiene app.py
ruta_proyecto = '/home/TU_USUARIO/sistema_de_presupuesto/vielma-moto-repuestos'

if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)

# 2) (Opcional pero recomendado) clave secreta de sesión en producción.
#    Cambiá el valor por una cadena larga y aleatoria propia.
os.environ.setdefault('SECRET_KEY', 'CAMBIA-ESTO-por-una-clave-larga-y-secreta')

# 3) Importar la aplicación Flask. PythonAnywhere espera el nombre 'application'.
from app import app as application
