import threading
import flet as ft
from processor.image_procesor import convert_images, OUTPUT_BASE
from ..components.results_view import build_results_table
from ..components.file_picker import pick_files_async, pick_dir_async


def build_convert_tab(page: ft.Page):
    state = {"paths": []}

    format_dd = ft.Dropdown(
        width=200,
        value="PNG",
        options=[
            ft.dropdown.Option("JPEG"),
            ft.dropdown.Option("PNG"),
            ft.dropdown.Option("WEBP"),
        ],
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
        files, error = await pick_files_async(page)
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

    def _convert():
        results = convert_images(state["paths"], format_dd.value)
        progress.visible = False
        output = f"{OUTPUT_BASE}"
        results_area.controls = [build_results_table(results, "convert", output)]
        page.update()

    def on_convert(e):
        if not state["paths"]:
            return
        results_area.controls.clear()
        progress.visible = True
        page.update()
        threading.Thread(target=_convert, daemon=True).start()

    content = ft.Column([
        ft.Row([
            ft.Button("Seleccionar archivos", icon=ft.Icons.FILE_UPLOAD, on_click=pick_files),
            ft.Button("Seleccionar carpeta", icon=ft.Icons.FOLDER_OPEN, on_click=pick_dir),
        ]),
        path_label,
        ft.Divider(height=16, color=ft.Colors.TRANSPARENT),
        ft.Text("Formato destino", size=13, weight=ft.FontWeight.W_500),
        format_dd,
        ft.Divider(height=12, color=ft.Colors.TRANSPARENT),
        ft.Button("Convertir", icon=ft.Icons.SWAP_HORIZ, on_click=on_convert),
        progress,
        results_area,
    ], scroll=ft.ScrollMode.AUTO, expand=True)

    return content
