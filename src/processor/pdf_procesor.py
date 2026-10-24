import os
import fitz

try:
    from utils.paths import get_output_base
except ImportError:  # instalado como paquete `src.*`
    from src.utils.paths import get_output_base

OUTPUT_BASE = get_output_base()

PRESETS = {
    "screen": {"garbage": 4, "deflate": True, "deflate_images": True, "deflate_fonts": True, "clean": True},
    "ebook": {"garbage": 4, "deflate": True, "deflate_images": True, "clean": True},
    "printer": {"garbage": 3, "deflate": True, "clean": True},
    "prepress": {"garbage": 1, "deflate": True},
}

PRESET_LABELS = {
    "screen": "Screen (72 DPI)",
    "ebook": "eBook (150 DPI)",
    "printer": "Printer (300 DPI)",
    "prepress": "Prepress (300 DPI, color)",
}


def _size_str(bytes_val):
    if bytes_val >= 1024 * 1024:
        return f"{bytes_val / (1024 * 1024):.2f} MB"
    return f"{bytes_val / 1024:.2f} KB"


def _collect_pdfs(path):
    """Collect PDFs from a single file or a directory.

    Directories are scanned recursively: PDFs in the folder itself and in
    subfolders at any depth (children, grandchildren, ...) are included.
    """
    if os.path.isdir(path):
        pdfs = []
        for dirpath, _, filenames in os.walk(path):
            for entry in filenames:
                if entry.lower().endswith(".pdf"):
                    pdfs.append(os.path.join(dirpath, entry))
        return pdfs
    elif os.path.isfile(path):
        return [path]
    return []


def compress_pdfs(paths, output_dir=None, quality="ebook", on_progress=None, in_place=False):
    if isinstance(paths, str):
        paths = [paths]
    # Keep the source root of each directory input so the relative folder
    # structure can be mirrored under output_dir (avoids name collisions
    # between same-named PDFs in different subfolders).
    collected = []  # [(source_root or None, file_path)]
    for p in paths:
        if os.path.isdir(p):
            for f in _collect_pdfs(p):
                collected.append((p, f))
        else:
            for f in _collect_pdfs(p):
                collected.append((None, f))
    paths = collected

    if output_dir is None and not in_place:
        output_dir = OUTPUT_BASE

    if not in_place:
        os.makedirs(output_dir, exist_ok=True)

    params = PRESETS.get(quality, PRESETS["ebook"])
    results = []

    for root, path in paths:
        filename = os.path.basename(path)
        original_size = os.path.getsize(path)

        if original_size == 0:
            result = {
                "file": filename,
                "original_size": 0,
                "original_size_str": "0 B",
                "final_size": 0,
                "final_size_str": "0 B",
                "savings_percent": 0,
                "preset": quality,
            }
            results.append(result)
            if on_progress:
                on_progress(result)
            continue

        if in_place:
            output_path = path
        elif root is not None:
            # Mirror the subfolder structure under output_dir.
            rel = os.path.relpath(path, root)
            output_path = os.path.join(output_dir, rel)
            parent = os.path.dirname(output_path)
            if parent:
                os.makedirs(parent, exist_ok=True)
        else:
            output_path = os.path.join(output_dir, filename)

        try:
            doc = fitz.open(path)
            if in_place:
                tmp_path = output_path + ".utilspress-tmp"
                doc.save(tmp_path, **params)
                doc.close()  # release the source handle before replacing (Windows)
                os.replace(tmp_path, output_path)
            else:
                doc.save(output_path, **params)
                doc.close()
        except Exception:
            result = {
                "file": filename,
                "original_size": original_size,
                "original_size_str": _size_str(original_size),
                "final_size": original_size,
                "final_size_str": _size_str(original_size),
                "savings_percent": 0,
                "preset": quality,
                "error": "Error al comprimir",
            }
            results.append(result)
            if on_progress:
                on_progress(result)
            continue

        final_size = os.path.getsize(output_path)
        savings = 100 * (1 - final_size / original_size) if original_size > 0 else 0

        result = {
            "file": filename,
            "original_size": original_size,
            "original_size_str": _size_str(original_size),
            "final_size": final_size,
            "final_size_str": _size_str(final_size),
            "savings_percent": round(savings, 2),
            "preset": quality,
        }
        results.append(result)
        if on_progress:
            on_progress(result)

    return results
