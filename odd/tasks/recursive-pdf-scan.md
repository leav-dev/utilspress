# Feature: escaneo recursivo de PDFs

## Objetivo
`compress_pdfs` debe detectar y comprimir PDFs en la carpeta elegida **y en todas
sus subcarpetas hijas, a cualquier profundidad** (nietos, bisnietos, etc.),
para compresiones masivas sin tener que seleccionar carpeta por carpeta.

## Alcance
- Solo procesador PDF (`src/processor/pdf_procesor.py`).
- Imágenes quedan como están (no recursivo) — fuera de este pedido.
- Sin cambios en la GUI (usa `compress_pdfs`, hereda el comportamiento).
- Ajuste menor del texto de ayuda del CLI que hoy dice "non-recursively".

## Diseño
1. `_collect_pdfs`: `os.listdir` → `os.walk` (recursivo).
2. En modo `output_dir` (no in-place): replicar la estructura relativa de
   subcarpetas bajo el destino, para que dos PDFs homónimos en distintas
   subcarpetas no se pisen entre sí.
3. En modo `in_place`: se escribe sobre el mismo archivo, sin colisiones.

## Verificación
- Script descartable en /tmp: árbol de 3 niveles con PDFs, corre en ambos
  modos y comprueba que todos se procesan y la estructura se preserva.
- Sin regresión para entrada de archivo suelto o lista de archivos.

## Evidencia
- Commit de unidad de trabajo en rama `feat/recursive-pdf-scan` (sin push).
