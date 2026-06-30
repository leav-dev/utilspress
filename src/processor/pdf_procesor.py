import os
import fitz

OUTPUT_BASE = os.path.join(os.path.expanduser("~"), "Desktop")

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
    if os.path.isdir(path):
        pdfs = []
        for entry in os.listdir(path):
            full = os.path.join(path, entry)
            if os.path.isfile(full) and entry.lower().endswith(".pdf"):
                pdfs.append(full)
        return pdfs
    elif os.path.isfile(path):
        return [path]
    return []


def compress_pdfs(paths, output_dir=None, quality="ebook", on_progress=None):
    if isinstance(paths, str):
        paths = _collect_pdfs(paths)
    else:
        expanded = []
        for p in paths:
            expanded.extend(_collect_pdfs(p))
        paths = expanded

    if output_dir is None:
        output_dir = OUTPUT_BASE

    os.makedirs(output_dir, exist_ok=True)

    params = PRESETS.get(quality, PRESETS["ebook"])
    results = []

    for path in paths:
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

        output_path = os.path.join(output_dir, filename)

        try:
            doc = fitz.open(path)
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
