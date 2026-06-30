import flet as ft
from .tabs.compress_tab import build_compress_tab
from .tabs.convert_tab import build_convert_tab
from .tabs.resize_tab import build_resize_tab
from .tabs.pdf_tab import build_pdf_tab


def main(page: ft.Page):
    page.title = "utilspress"
    page.window.width = 850
    page.window.height = 680
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 20

    tabs = ft.Tabs(
        length=4,
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="Comprimir", icon=ft.Icons.COMPRESS),
                        ft.Tab(label="Convertir", icon=ft.Icons.SWAP_HORIZ),
                        ft.Tab(label="Redimensionar", icon=ft.Icons.ASPECT_RATIO),
                        ft.Tab(label="PDF", icon=ft.Icons.PICTURE_AS_PDF),
                    ],
                ),
                ft.TabBarView(
                    expand=True,
                    controls=[
                        build_compress_tab(page),
                        build_convert_tab(page),
                        build_resize_tab(page),
                        build_pdf_tab(page),
                    ],
                ),
            ],
        ),
    )

    page.add(tabs)


def start():
    ft.run(main)
