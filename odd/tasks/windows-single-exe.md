# Windows: error Documents\flet + exe de un solo archivo

## Diagnóstico
- Error: `PathNotFoundException: Creation Failed, path = 'C:\Users\Usuario\Documents\flet'` (errno 2).
- Causa: el motor de Flet crea su storage en `%USERPROFILE%\Documents\flet`, pero esa
  carpeta no existe en ese Windows (Windows en español usa `Documentos`, y/o OneDrive
  movió las carpetas conocidas a `OneDrive\...`). No es código nuestro: crashea al arrancar.
- El `OUTPUT_BASE = ~/Desktop` de `image_procesor.py` / `pdf_procesor.py` tiene la misma
  fragilidad (Escritorio redirigido por OneDrive o localizado como `Escritorio`).
- Pasar a un solo `.exe` NO corrige el crash; son dos trabajos separados.

## Tareas
1. [x] Diagnosticar error con traceback real.
2. [ ] Helper robusto de carpetas (`src/utils/paths.py`): Documents/Desktop reales vía
   Known Folder + fallbacks (OneDrive, Documentos/Documents, Escritorio/Desktop, home).
3. [ ] Pre-crear `<Documents>\flet` al arrancar, antes de `ft.run()` (nunca debe tumbar el inicio).
4. [ ] Usar el helper para `OUTPUT_BASE` en ambos procesadores.
5. [ ] Migrar job Windows del workflow a `flet pack` (PyInstaller `--onefile`): un solo `.exe`.
6. [ ] Verificar (imports, checks funcionales, `flet pack --help`) y cerrar.

## Evidencia
- Commit `87ffd02` en `main` + tag `v0.4.0` pusheados (dispara build + release en CI).
- Verificación local: `compileall` OK, imports OK, helper detecta `~/Escritorio` y `~/Documentos` en máquina ES.
