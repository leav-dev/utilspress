# PDF streaming: procesar mientras se sigue contando

## Diagnóstico
- Con 1000+ PDFs el flujo era contar-todo → procesar: la UI quedaba en
  "Contando archivos…" sin feedback hasta que el `os.walk` + filtro por
  firma terminaba. TTFP (primer archivo procesado) = costo total del conteo.

## Diseño
- `pdf_procesor`: hilo escáner (`_iter_pdf_candidates`, solo filtro por
  extensión, sin abrir archivos) alimenta una `queue` acotada (256) mientras
  N workers comprimen en paralelo. `jobs=1` consume en el hilo principal.
- Callbacks: `on_discover(found)` throttled (cada 25 o 0.3s) → UI muestra
  "🔎 Encontrados X · procesados Y" con barra indeterminada; `on_start(total)`
  al cerrar el escaneo → barra determinada. `finally` garantiza sentinels
  y `on_start` aunque el walk falle (los workers nunca cuelgan).
- Filtro de firma (`_is_archive`) diferido al worker: antes excluía en el
  conteo, ahora aparece como fila "Omitido: es un archivo comprimido" para
  que hecho == encontrado == total y la barra siempre llegue al 100%.
- Worker con `try/except` amplio: un archivo suelto/movido no frena el lote.
- `results_view`: tabla capada a 200 filas + aviso (el resumen/totales siempre
  cubre el 100%). Evita congelar la UI con 1000 filas. Componente compartido:
  beneficia a todas las pestañas.
- Solo PDF por decisión del usuario; imágenes quedan en dos fases (su conteo
  es un `listdir` barato frente a Pillow).

## Evidencia
- `compileall` OK.
- Test real: 6 PDFs + 1 falso (firma ZIP) → 7 resultados en orden, fila fake
  marcada omitida, `on_start(7)`, `EMPTY_JOBS1_OK` en dir vacío con jobs=1.
- Liberado en vivo (solo pestaña PDF): `live` acumula `original - final` por
  `on_progress` bajo lock → "💾 Liberado hasta ahora: X"; al final muestra
  el total. Ventana vieja cerrada y app relanzada con el código nuevo.
