import os
import zipfile


def _size_str(bytes_val):
    if bytes_val >= 1024 * 1024:
        return f"{bytes_val / (1024 * 1024):.2f} MB"
    return f"{bytes_val / 1024:.2f} KB"


def compress_folder(folder_path, output_path=None, level=6):
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"'{folder_path}' no es una carpeta")

    if output_path is None:
        output_path = folder_path.rstrip("/") + ".zip"

    original_size = 0
    for dirpath, _, filenames in os.walk(folder_path):
        for f in filenames:
            original_size += os.path.getsize(os.path.join(dirpath, f))

    with zipfile.ZipFile(
        output_path, "w", zipfile.ZIP_DEFLATED, compresslevel=level
    ) as zf:
        for dirpath, _, filenames in os.walk(folder_path):
            for f in filenames:
                full = os.path.join(dirpath, f)
                arcname = os.path.relpath(full, os.path.dirname(folder_path))
                zf.write(full, arcname)

    final_size = os.path.getsize(output_path)
    savings = 100 * (1 - final_size / original_size) if original_size > 0 else 0

    return {
        "file": os.path.basename(output_path),
        "original_size": original_size,
        "original_size_str": _size_str(original_size),
        "final_size": final_size,
        "final_size_str": _size_str(final_size),
        "savings_percent": round(savings, 2),
        "output_path": output_path,
    }
