import flet as ft
from .tabs.compress_tab import build_compress_tab
from .tabs.convert_tab import build_convert_tab
from .tabs.resize_tab import build_resize_tab
from .tabs.pdf_tab import build_pdf_tab
from .tabs.compress_folder_tab import build_compress_folder_tab


def main(page: ft.Page):
    page.title = "utilspress"
    page.window.width = 850
    page.window.height = 680
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 20

    image_tabs = ft.Tabs(
        length=3,
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="Comprimir", icon=ft.Icons.COMPRESS),
                        ft.Tab(label="Convertir", icon=ft.Icons.SWAP_HORIZ),
                        ft.Tab(label="Redimensionar", icon=ft.Icons.ASPECT_RATIO),
                    ],
                ),
                ft.TabBarView(
                    expand=True,
                    controls=[
                        build_compress_tab(page),
                        build_convert_tab(page),
                        build_resize_tab(page),
                    ],
                ),
            ],
        ),
    )

    pdf_content = build_pdf_tab(page)
    zip_content = build_compress_folder_tab(page)

    content_area = ft.Column(expand=True, controls=[image_tabs])

    def on_rail_change(e):
        index = e.control.selected_index
        if index == 0:
            content_area.controls = [image_tabs]
        elif index == 1:
            content_area.controls = [pdf_content]
        else:
            content_area.controls = [zip_content]
        page.update()

    rail = ft.NavigationRail(
        selected_index=0,
        width=100,
        label_type=ft.NavigationRailLabelType.ALL,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.IMAGE,
                label="Imágenes",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.PICTURE_AS_PDF,
                label="PDF",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.FOLDER_ZIP,
                label="ZIP",
            ),
        ],
        on_change=on_rail_change,
    )

    page.add(
        ft.Row(
            expand=True,
            controls=[
                rail,
                ft.VerticalDivider(width=1),
                content_area,
            ],
        )
    )


def start():
    ft.run(main)
