import threading
import flet as ft
from processor.pdf_procesor import compress_pdfs, OUTPUT_BASE, PRESET_LABELS
from ..components.results_view import build_results_table
from ..components.file_picker import pick_files_async, pick_dir_async


def build_pdf_tab(page: ft.Page):
    state = {"paths": []}

    preset_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(k, v) for k, v in PRESET_LABELS.items()],
        value="ebook",
        width=300,
    )
    path_label = ft.Text("Ningún archivo seleccionado", size=13, color=ft.Colors.GREY_600)
    progress = ft.ProgressBar(visible=False, width=600)
    results_area = ft.Column()

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
        results = compress_pdfs(
            state["paths"],
            quality=preset_dropdown.value,
        )
        progress.visible = False
        output = f"{OUTPUT_BASE}"
        results_area.controls = [build_results_table(results, "pdf", output)]
        page.update()

    def on_compress(e):
        if not state["paths"]:
            return
        results_area.controls.clear()
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
        ft.Divider(height=12, color=ft.Colors.TRANSPARENT),
        ft.Button("Comprimir PDF", icon=ft.Icons.COMPRESS, on_click=on_compress),
        progress,
        results_area,
    ], scroll=ft.ScrollMode.AUTO, expand=True)

    return content
