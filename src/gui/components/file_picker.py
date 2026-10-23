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
    err = _check_zenity()
    if err:
        return None, err
    file_type, allowed_ext = FILE_FILTERS.get(file_types, FILE_FILTERS["images"])
    picker = ft.FilePicker()
    # The picker must be mounted on the page overlay before use,
    # otherwise pick_files() raises "Control must be added to the page first".
    page.overlay.append(picker)
    page.update()
    try:
        files = await picker.pick_files(
            allow_multiple=True,
            file_type=file_type,
            allowed_extensions=allowed_ext,
        )
        if files:
            return [f.path for f in files if f.path], None
        return [], None
    except Exception as e:
        return None, str(e)
    finally:
        if picker in page.overlay:
            page.overlay.remove(picker)
            page.update()


async def pick_dir_async(page):
    err = _check_zenity()
    if err:
        return None, err
    picker = ft.FilePicker()
    # The picker must be mounted on the page overlay before use,
    # otherwise get_directory_path() raises "Control must be added to the page first".
    page.overlay.append(picker)
    page.update()
    try:
        path = await picker.get_directory_path()
        return path, None
    except Exception as e:
        return None, str(e)
    finally:
        if picker in page.overlay:
            page.overlay.remove(picker)
            page.update()
