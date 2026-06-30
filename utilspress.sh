#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python3"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "No se encontró el entorno virtual en .venv/"
    echo "Crealo con: python3 -m venv .venv"
    echo "Y después instalá las dependencias con: .venv/bin/pip install -r requirements.txt"
    exit 1
fi

"$VENV_PYTHON" -m pip install -q -r "$SCRIPT_DIR/requirements.txt"

if [[ "$1" == "--web" ]]; then
    "$VENV_PYTHON" "$SCRIPT_DIR/src/main.py" --web
else
    "$VENV_PYTHON" "$SCRIPT_DIR/src/main.py" "$@"
fi
