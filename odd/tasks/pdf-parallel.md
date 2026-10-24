# PDF: compresión paralela para Windows

## Diagnóstico
- `compress_pdfs` es secuencial: 1 PDF por vez en un solo hilo.
- 211 PDFs en ~90 min ≈ 25 s/archivo. En un PC Windows de 4-8 núcleos,
  el paralelismo da speedup casi lineal (3-6x) porque PyMuPDF libera el GIL en C.
- Sin workers, la GUI además reconstruye la tabla + `page.update()` por archivo.
- ThreadPoolExecutor (no procesos) es lo seguro en Flet exe Windows:
  evita `spawn`/`freeze_support` de multiprocessing en PyInstaller.

## Tareas
1. [x] Diseñar paralelización apta para Windows exe.
2. [x] Workers en `pdf_procesor.py` + `--jobs` en CLI + auto en GUI.
3. [ ] Verificar (benchmark rápido, imports, CLI --help) y cerrar.

## Evidencia
- (pendiente) commit en feature branch.
