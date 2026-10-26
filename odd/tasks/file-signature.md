# Firma anti-reproceso en PDF e imágenes

## Diseño
- La firma viaja **dentro del propio archivo**, sin sidecars ni renombres:
  - PDF → metadatos `Keywords`: `utilspress:<preset>:<aaaammdd>` (keywords
    del usuario se preservan, token viejo se reemplaza). Solo se tocan claves
    Info conocidas (fitz devuelve extras que `set_metadata` rechaza).
  - PNG → chunk tEXt `utilspress` | JPG → marcador COM | WEBP → EXIF
    UserComment. Formato: `<op>:<setting>:<fecha>` (compress `q85`/`c6`,
    convert `jpeg`, resize `800x600a`).
- Regla de omisión: misma op + mismo setting → fila "omitida" (ahorro 0,
  cuenta como procesada para que la barra cierre al 100%). Distinto preset /
  calidad / tamaño → se reprocesa solo. `force=True` omite el chequeo.
- In-place: la marca se lee del propio archivo. Copy-mode: se lee del output
  previo con igual ruta relativa (cubre el default de la GUI que guarda en
  Desktop).
- GUI: checkbox "Reprocesar archivos ya marcados" en las 4 pestañas + columna
  "Estado" (solo visible si hay omitidos/errores; gris vs rojo) + contador de
  omitidos en el estado final del PDF.
- CLI: `--force` en compress/convert/resize/pdf + línea `[omitido: ...]`.

## Límites honestos
- Archivos marcados con versiones viejas (sin firma) se procesan una vez más
  y ahí quedan marcados.
- Si editás un archivo a mano después de marcarlo, la firma no lo detecta:
  para eso está el checkbox Forzar (la alternativa era guardar mtime/size,
  circular e imposible sin re-abrir: se descartó a conciencia).

## Evidencia
- `compileall` OK.
- Test real: PDF in-place (marca → omitido → preset distinto reprocesa →
  force reprocesa), PDF copy-mode, PNG/JPG/WEBP (marca/omisión, y PNG ignora
  bien un cambio de quality porque usa compress_level), convert + resize.
- App relanzada (flet.exe nuevo) con el código nuevo.
