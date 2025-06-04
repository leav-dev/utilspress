#!/bin/bash

# Obtener la ruta absoluta del directorio donde está este script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Instalar las dependencias
pip install -r "$SCRIPT_DIR/requirements.txt"

# Ejecutar la app principal
python3 "$SCRIPT_DIR/src/main.py" "$@"
