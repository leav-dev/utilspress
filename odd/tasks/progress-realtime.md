# Progreso en tiempo real (fix retraso vs SO)

## Diagnóstico
- `ProgressBar` indeterminada (sin `value`): nunca muestra x/N.
- `on_progress` reconstruye el `DataTable` completo por cada archivo + `page.update()`
  desde el hilo worker. Flet encola esos updates por websocket; con muchos archivos
  la UI se atrasa frente al filesystem (el SO ve el `os.replace` al instante).
- PDF en paralelo (`jobs=0`, hasta 8 workers) dispara varios `on_progress`
  concurrentes → rebuilds simultáneos, más cola y resultados desordenados.
- Bug extra: `progress.visible = False` al final no hace `page.update()` cuando
  `acc` no está vacío → el spinner queda visible.

## Plan
1. Processors (`image_procesor`, `pdf_procesor`): nuevo callback `on_start(total)`
   antes del loop, sin cambiar firma existente.
2. 4 tabs (compress, convert, resize, pdf): barra determinada + `status x/N –
   archivo actual`, update liviano por archivo (sin rebuild de tabla),
   tabla completa una sola vez al final, lock para PDF paralelo.
3. ZIP tab: texto de estado + fix del hide.
4. Verificar con `compileall`.

## Evidencia
- `python -m compileall -q src` → OK.
- `uv run python src/main.py` → arranca (bloquea como corresponde a Flet desktop,
  sin tracebacks; timeout a los 30s por app en ejecución).
