# Linux: AppImage con linuxdeploy (sin deps manuales)

## Diagnóstico
- AppImage actual = `cp build/linux/*` + AppRun fino + appimagetool continuous.
- No bundlea sysdeps GTK/mpv/secret/gstreamer; AppRun no exporta `LD_LIBRARY_PATH` ni schemas.
- En host distinto al runner o sin `libfuse2`, la app se queda esperando (boot screen apagada, sin log visible).
- Verificación local: `src/main.py` arranca OK con `flet run`; el cuelgue es del envoltorio, no del código.

## Tareas
1. [x] Diagnosticar AppImage actual y definir fix linuxdeploy.
2. [x] Migrar job Linux del workflow a `linuxdeploy --plugin gtk` + tar.gz fallback.
3. [ ] Verificar YAML y documentar uso sin dependencias.

## Evidencia
- (pendiente) commit del workflow en feature branch.
