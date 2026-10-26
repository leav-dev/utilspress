import threading
import flet as ft
from processor.pdf_procesor import compress_pdfs, OUTPUT_BASE, PRESET_LABELS
from ..components.results_view import build_results_table
from ..components.file_picker import pick_files_async, pick_dir_async


def _fmt_freed(bytes_val):
    if bytes_val >= 1024 ** 3:
        return f"{bytes_val / (1024 ** 3):.2f} GB"
    if bytes_val >= 1024 * 1024:
        return f"{bytes_val / (1024 * 1024):.2f} MB"
    if bytes_val >= 1024:
        return f"{bytes_val / 1024:.2f} KB"
    return f"{int(bytes_val)} B"


def build_pdf_tab(page: ft.Page):
    state = {"paths": []}

    preset_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(k, v) for k, v in PRESET_LABELS.items()],
        value="ebook",
        width=300,
    )
    path_label = ft.Text("Ningún archivo seleccionado", size=13, color=ft.Colors.GREY_600)
    status = ft.Text("", size=13, weight=ft.FontWeight.W_500)
    live = ft.Text("", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN)
    progress = ft.ProgressBar(visible=False, width=600, value=0)
    results_area = ft.Column()
    overwrite_cb = ft.Checkbox(label="Reemplazar archivos originales", value=False)
    force_cb = ft.Checkbox(label="Reprocesar archivos ya marcados", value=False)

    def set_paths(paths):
        state["paths"] = paths
        p = state["paths"]
        if not p:
            path_label.value = "Ningún archivo seleccionado"
            path_label.color = ft.Colors.GREY_600
        elif len(p) == 1:
            path_label.value = p[0]
            path_label.color = ft.Colors.GREEN
        else:
            path_label.value = f"{len(p)} archivo(s) seleccionado(s)"
            path_label.color = ft.Colors.GREEN
        page.update()

    async def pick_files(e):
        files, error = await pick_files_async(page, file_types="pdf")
        if error:
            path_label.value = f"Error: {error}"
            path_label.color = ft.Colors.RED
            page.update()
            return
        set_paths(files)

    async def pick_dir(e):
        path, error = await pick_dir_async(page)
        if error:
            path_label.value = f"Error: {error}"
            path_label.color = ft.Colors.RED
            page.update()
            return
        set_paths([path] if path else [])

    def _compress():
        acc = []
        counters = {"found": 0, "total": None, "done": 0, "freed": 0}
        lock = threading.Lock()

        in_place = overwrite_cb.value
        output = "Archivos originales (reemplazados)" if in_place else f"{OUTPUT_BASE}"

        def on_discover(found):
            # Escaneo en curso (streaming): total aún desconocido.
            # Barra indeterminada + vivos encontrados/procesados.
            with lock:
                counters["found"] = found
                if counters["total"] is None:
                    status.value = f"🔎 Encontrados {found} · procesados {counters['done']}…"
                    progress.value = None
            page.update()

        def on_start(total):
            with lock:
                counters["total"] = total
                if total == 0:
                    status.value = "Sin archivos"
                    progress.value = 0
                elif counters["done"] == 0:
                    status.value = f"0/{total} PDFs…"
                    progress.value = 0
            page.update()

        def on_progress(result):
            # Viene de hasta 8 workers + hilo de escaneo: todo bajo lock.
            with lock:
                acc.append(result)
                counters["done"] += 1
                counters["freed"] += max(
                    0, result["original_size"] - result["final_size"]
                )
                done = counters["done"]
                freed_str = _fmt_freed(counters["freed"])
                total = counters["total"]
                if total is None:
                    found = counters["found"] or done
                    progress.value = None
                    status.value = f"🔎 {done}/{found} – {result['file']}"
                else:
                    progress.value = done / total if total else 1
                    status.value = f"{done}/{total} – {result['file']}"
                live.value = f"💾 Liberado hasta ahora: {freed_str}"
            page.update()

        results = compress_pdfs(
            state["paths"],
            quality=preset_dropdown.value,
            on_progress=on_progress,
            in_place=in_place,
            jobs=0,
            on_start=on_start,
            on_discover=on_discover,
            force=force_cb.value,
        )
        progress.visible = False
        total = counters["total"]
        if total is None:
            total = len(results)
        status.value = f"Listo: {len(results)}/{total} PDFs"
        skipped = sum(1 for r in results if r.get("skipped"))
        if skipped:
            status.value += f" ({skipped} omitidos por marca)"
        live.value = (
            f"💾 Total liberado: {_fmt_freed(counters['freed'])}"
            if results else ""
        )
        results_area.controls = [build_results_table(results, "pdf", output)]
        page.update()

    def on_compress(e):
        if not state["paths"]:
            return
        results_area.controls.clear()
        live.value = ""
        status.value = "Buscando PDFs…"
        progress.value = None
        progress.visible = True
        page.update()
        threading.Thread(target=_compress, daemon=True).start()

    content = ft.Column([
        ft.Row([
            ft.Button("Seleccionar archivos", icon=ft.Icons.FILE_UPLOAD, on_click=pick_files),
            ft.Button("Seleccionar carpeta", icon=ft.Icons.FOLDER_OPEN, on_click=pick_dir),
        ]),
        path_label,
        ft.Divider(height=16, color=ft.Colors.TRANSPARENT),
        ft.Text("Preset de compresión", size=13, weight=ft.FontWeight.W_500),
        preset_dropdown,
        overwrite_cb,
        force_cb,
        ft.Divider(height=12, color=ft.Colors.TRANSPARENT),
        ft.Button("Comprimir PDF", icon=ft.Icons.COMPRESS, on_click=on_compress),
        status,
        live,
        progress,
        results_area,
    ], scroll=ft.ScrollMode.AUTO, expand=True)

    return content
