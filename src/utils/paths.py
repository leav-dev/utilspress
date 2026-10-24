"""Carpetas reales del usuario (a prueba de Windows en español / OneDrive).

Solo stdlib. Ninguna función de este módulo lanza excepciones: ante
cualquier error se devuelve un fallback razonable.

Contexto: el motor de Flet crea su storage en
``%USERPROFILE%\\Documents\\flet``. En Windows en español esa carpeta suele
no existir (la real es ``Documentos`` o está redirigida a
``OneDrive\\...``) y la app crashea al arrancar con ``PathNotFoundException``.
Nuestro código tenía la misma fragilidad con ``~/Desktop``.
"""

from __future__ import annotations

import os

# GUIDs de Known Folders de Windows (SHGetKnownFolderPath).
_FOLDERID_DOCUMENTS = "{FDD39AD0-238F-46AF-ADB4-6C85480369C7}"
_FOLDERID_DESKTOP = "{B4BFCC3A-DB2C-424C-B029-7FE99A87C641}"


def _known_folder_path(folder_id: str) -> str | None:
    """Devuelve la ruta real de un Known Folder de Windows, o None.

    Usa ctypes SHGetKnownFolderPath. Solo tiene efecto en win32; en cualquier
    otra plataforma (o ante cualquier error) retorna None sin lanzar.
    """
    try:
        if os.name != "nt":
            return None
        import ctypes
        from ctypes import wintypes

        class GUID(ctypes.Structure):
            _fields_ = [
                ("Data1", wintypes.DWORD),
                ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD),
                ("Data4", wintypes.BYTE * 8),
            ]

        def _parse_guid(text: str) -> "GUID":
            text = text.strip().strip("{}")
            parts = text.split("-")
            d4 = bytes.fromhex(parts[3] + parts[4])
            return GUID(
                int(parts[0], 16),
                int(parts[1], 16),
                int(parts[2], 16),
                (wintypes.BYTE * 8)(*d4),
            )

        shell32 = ctypes.windll.shell32
        ole32 = ctypes.windll.ole32
        path_ptr = ctypes.c_wchar_p()
        hr = shell32.SHGetKnownFolderPath(
            _parse_guid(folder_id), 0, None, ctypes.byref(path_ptr)
        )
        if hr != 0 or not path_ptr.value:
            return None
        value = str(path_ptr.value)
        try:
            ole32.CoTaskMemFree(path_ptr)
        except Exception:
            pass
        return value or None
    except Exception:
        return None


def _home() -> str:
    try:
        return os.path.expanduser("~")
    except Exception:
        return "~"


def get_documents_dir() -> str:
    """Carpeta Documentos real del usuario. Nunca lanza excepciones."""
    try:
        real = _known_folder_path(_FOLDERID_DOCUMENTS)
        if real:
            return real
        home = _home()
        for candidate in (
            os.path.join(home, "OneDrive", "Documentos"),
            os.path.join(home, "OneDrive", "Documents"),
            os.path.join(home, "Documentos"),
            os.path.join(home, "Documents"),
        ):
            try:
                if os.path.isdir(candidate):
                    return candidate
            except Exception:
                continue
        return os.path.join(home, "Documents")
    except Exception:
        return os.path.join(_home(), "Documents")


def get_desktop_dir() -> str:
    """Carpeta Escritorio real del usuario. Nunca lanza excepciones."""
    try:
        real = _known_folder_path(_FOLDERID_DESKTOP)
        if real:
            return real
        home = _home()
        for candidate in (
            os.path.join(home, "OneDrive", "Escritorio"),
            os.path.join(home, "OneDrive", "Desktop"),
            os.path.join(home, "Escritorio"),
            os.path.join(home, "Desktop"),
        ):
            try:
                if os.path.isdir(candidate):
                    return candidate
            except Exception:
                continue
        return os.path.join(home, "Desktop")
    except Exception:
        return os.path.join(_home(), "Desktop")


def get_output_base() -> str:
    """Carpeta destino por defecto: Escritorio real si existe, si no.

    Documentos real, si no el home. Solo lectura: no crea nada.
    """
    try:
        desktop = get_desktop_dir()
        if desktop and os.path.isdir(desktop):
            return desktop
    except Exception:
        pass
    try:
        documents = get_documents_dir()
        if documents and os.path.isdir(documents):
            return documents
    except Exception:
        pass
    return _home()


def ensure_flet_storage() -> str | None:
    """Pre-crea ``<Documentos real>/flet`` para que Flet no crashee al arrancar.

    NUNCA lanza: ante cualquier error retorna None. Retorna la ruta creada
    (o ya existente) o None si no se pudo crear.
    """
    try:
        documents = get_documents_dir()
        if not documents:
            return None
        target = os.path.join(documents, "flet")
        os.makedirs(target, exist_ok=True)
        return target
    except Exception:
        return None
