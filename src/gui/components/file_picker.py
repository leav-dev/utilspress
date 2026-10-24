import sys
import shutil
import flet as ft

FILE_FILTERS = {
    "images": (ft.FilePickerFileType.IMAGE, None),
    "pdf": (ft.FilePickerFileType.CUSTOM, ["pdf"]),
}


def _check_zenity():
    if sys.platform == "linux" and shutil.which("zenity") is None:
        return (
            "Zenity no está instalado. Es necesario para seleccionar archivos en Linux.\n"
            "Instalalo con:  sudo apt-get install zenity"
        )
    return None


async def pick_files_async(page, file_types="images"):
    # Flet >= 0.80: FilePicker es un Service y se auto-registra al
    # construirlo (Service.init() -> page._services). NO va en
    # page.overlay: montarlo ahi produce "Unknown control: filepicker".
    # Patron oficial: await ft.FilePicker().pick_files(...).
    err = _check_zenity()
    if err:
        return None, err
    file_type, allowed_ext = FILE_FILTERS.get(file_types, FILE_FILTERS["images"])
    try:
        files = await ft.FilePicker().pick_files(
            allow_multiple=True,
            file_type=file_type,
            allowed_extensions=allowed_ext,
        )
        if files:
            return [f.path for f in files if f.path], None
        return [], None
    except Exception as e:
        return None, str(e)


async def pick_dir_async(page):
    # Idem arriba: Service auto-registrado, sin page.overlay.
    err = _check_zenity()
    if err:
        return None, err
    try:
        path = await ft.FilePicker().get_directory_path()
        return path, None
    except Exception as e:
        return None, str(e)
