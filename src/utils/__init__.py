"""Utilidades compartidas (solo stdlib)."""

from .paths import (
    ensure_flet_storage,
    get_desktop_dir,
    get_documents_dir,
    get_output_base,
)

__all__ = [
    "ensure_flet_storage",
    "get_desktop_dir",
    "get_documents_dir",
    "get_output_base",
]
