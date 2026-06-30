import threading
import flet as ft
from processor.image_procesor import compress_images, OUTPUT_BASE
from ..components.results_view import build_results_table
from ..components.file_picker import pick_files_async, pick_dir_async


def build_compress_tab(page: ft.Page):
    state = {"paths": []}

    quality_value = ft.Text("85%", size=13, weight=ft.FontWeight.W_600, width=50)
    compress_value = ft.Text("6", size=13, weight=ft.FontWeight.W_600, width=50)

    quality_slider = ft.Slider(
        min=1, max=100, value=85, label="{value}%", width=300,
        on_change=lambda e: setattr(quality_value, "value", f"{int(e.control.value)}%") or page.update(),
    )
    compress_slider = ft.Slider(
        min=0, max=9, value=6, label="{value}", width=300,
        on_change=lambda e: setattr(compress_value, "value", str(int(e.control.value))) or page.update(),
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

    def _compress():
        acc = []

        def on_progress(result):
            acc.append(result)
            output = f"{OUTPUT_BASE}"
            results_area.controls = [build_results_table(acc, "compress", output)]
            page.update()

        results = compress_images(
            state["paths"],
            quality=int(quality_slider.value),
            compress_level=int(compress_slider.value),
            on_progress=on_progress,
        )
        progress.visible = False
        if not acc:
            output = f"{OUTPUT_BASE}"
            results_area.controls = [build_results_table(results, "compress", output)]
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
        ft.Text("Calidad (JPG / WebP)", size=13, weight=ft.FontWeight.W_500),
        ft.Row([quality_slider, quality_value], vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ft.Text("Compresión PNG (0 = sin compresión, 9 = máxima)", size=13, weight=ft.FontWeight.W_500),
        ft.Row([compress_slider, compress_value], vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ft.Divider(height=12, color=ft.Colors.TRANSPARENT),
        ft.Button("Comprimir", icon=ft.Icons.COMPRESS, on_click=on_compress),
        progress,
        results_area,
    ], scroll=ft.ScrollMode.AUTO, expand=True)

    return content
