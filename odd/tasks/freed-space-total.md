# Mostrar total liberado al reemplazar originales

## Diagnóstico
- `build_results_table` muestra promedio % pero no bytes totales liberados.
- En modo in-place (`Reemplazar archivos originales`) el usuario quiere ver
  cuánto disco recuperó: `total_orig - total_final` formateado.
- CLI (`cmd_compress`, `cmd_pdf`, etc.) imprime promedio pero no total.

## Tareas
1. [x] Diseñar total liberado en GUI y CLI.
2. [x] Implementar total en `results_view.py` + `cli.py`.
3. [ ] Verificar compile y render sin regresión.

## Evidencia
- (pendiente) commit en feature branch.
