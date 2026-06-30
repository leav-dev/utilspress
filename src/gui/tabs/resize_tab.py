import threading
import flet as ft
from processor.image_procesor import resize_images, OUTPUT_BASE
from ..components.results_view import build_results_table
from ..components.file_picker import pick_files_async, pick_dir_async


def build_resize_tab(page: ft.Page):
    state = {"paths": []}

    width_input = ft.TextField(label="Ancho (px)", value="1920", width=150)
    height_input = ft.TextField(label="Alto (px)", value="1080", width=150)
    aspect_cb = ft.Checkbox(label="Mantener relación de aspecto", value=True)
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

    def _resize():
        acc = []

        def on_progress(result):
            acc.append(result)
            output = f"{OUTPUT_BASE}"
            results_area.controls = [build_results_table(acc, "resize", output)]
            page.update()

        w = int(width_input.value)
        h = int(height_input.value)
        results = resize_images(
            state["paths"],
            w, h,
            maintain_aspect=aspect_cb.value,
            on_progress=on_progress,
        )
        progress.visible = False
        if not acc:
            output = f"{OUTPUT_BASE}"
            results_area.controls = [build_results_table(results, "resize", output)]
            page.update()

    def on_resize(e):
        if not state["paths"]:
            return
        try:
            w = int(width_input.value)
            h = int(height_input.value)
            if w <= 0 or h <= 0:
                raise ValueError
        except (ValueError, TypeError):
            path_label.value = "Dimensiones inválidas (deben ser números > 0)"
            path_label.color = ft.Colors.RED
            page.update()
            return
        results_area.controls.clear()
        progress.visible = True
        page.update()
        threading.Thread(target=_resize, daemon=True).start()

    content = ft.Column([
        ft.Row([
            ft.Button("Seleccionar archivos", icon=ft.Icons.FILE_UPLOAD, on_click=pick_files),
            ft.Button("Seleccionar carpeta", icon=ft.Icons.FOLDER_OPEN, on_click=pick_dir),
        ]),
        path_label,
        ft.Divider(height=16, color=ft.Colors.TRANSPARENT),
        ft.Text("Dimensiones", size=13, weight=ft.FontWeight.W_500),
        ft.Row([width_input, height_input]),
        aspect_cb,
        ft.Divider(height=12, color=ft.Colors.TRANSPARENT),
        ft.Button("Redimensionar", icon=ft.Icons.ASPECT_RATIO, on_click=on_resize),
        progress,
        results_area,
    ], scroll=ft.ScrollMode.AUTO, expand=True)

    return content
