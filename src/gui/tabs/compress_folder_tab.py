import threading
import flet as ft
from processor.zip_procesor import compress_folder
from ..components.file_picker import pick_dir_async
from ..components.results_view import build_results_table


def build_compress_folder_tab(page: ft.Page):
    state = {"path": None}

    level_value = ft.Text("6", size=13, weight=ft.FontWeight.W_600, width=50)
    level_slider = ft.Slider(min=0, max=9, value=6, label="{value}", width=300,
        on_change=lambda e: setattr(level_value, "value", str(int(e.control.value))) or page.update(),
    )
    path_label = ft.Text("Ninguna carpeta seleccionada", size=13, color=ft.Colors.GREY_600)
    progress = ft.ProgressBar(visible=False, width=600)
    results_area = ft.Column()

    def set_path(path):
        state["path"] = path
        if path:
            path_label.value = path
            path_label.color = ft.Colors.GREEN
        else:
            path_label.value = "Ninguna carpeta seleccionada"
            path_label.color = ft.Colors.GREY_600
        page.update()

    async def pick_folder(e):
        path, error = await pick_dir_async(page)
        if error:
            path_label.value = f"Error: {error}"
            path_label.color = ft.Colors.RED
            page.update()
            return
        set_path(path)

    def _compress():
        if not state["path"]:
            return
        result = compress_folder(
            state["path"],
            level=int(level_slider.value),
        )
        progress.visible = False
        results_area.controls = [build_results_table([result], "compress", result["output_path"])]
        page.update()

    def on_compress(e):
        if not state["path"]:
            return
        results_area.controls.clear()
        progress.visible = True
        page.update()
        threading.Thread(target=_compress, daemon=True).start()

    content = ft.Column([
        ft.Row([
            ft.Button("Seleccionar carpeta", icon=ft.Icons.FOLDER_OPEN, on_click=pick_folder),
        ]),
        path_label,
        ft.Divider(height=16, color=ft.Colors.TRANSPARENT),
        ft.Text("Nivel de compresión (0 = sin compresión, 9 = máxima)", size=13, weight=ft.FontWeight.W_500),
        ft.Row([level_slider, level_value], vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ft.Divider(height=12, color=ft.Colors.TRANSPARENT),
        ft.Button("Comprimir ZIP", icon=ft.Icons.FOLDER_ZIP, on_click=on_compress),
        progress,
        results_area,
    ], scroll=ft.ScrollMode.AUTO, expand=True)

    return content
