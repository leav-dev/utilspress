import os
import queue
import threading
import time
from datetime import date as _date
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


# Firma anti-reproceso: se guarda en los metadatos (Keywords) del propio PDF,
# viaja con el archivo y no requiere sidecars ni renombres.
# Formato: "utilspress:<preset>:<aaaammdd>".
_MARK_PREFIX = "utilspress:"
_META_KEYS = ("title", "author", "subject", "keywords", "creator",
               "producer", "creationDate", "modDate", "trapped")


def _marker_payload(quality):
    return f"{_MARK_PREFIX}{quality}:{_date.today().strftime('%Y%m%d')}"


def _read_marker(metadata):
    """Return (preset, date) from Keywords, or None. Never raises."""
    try:
        kw = (metadata or {}).get("keywords") or ""
        for token in kw.split(";"):
            token = token.strip()
            if token.startswith(_MARK_PREFIX):
                parts = token.split(":")
                if len(parts) >= 3 and parts[1]:
                    return (parts[1], parts[2])
    except Exception:
        pass
    return None


def _write_marker(metadata, quality):
    """Return a metadata dict with our token appended to Keywords.

    Only known Info keys are kept (fitz may return extra keys that
    set_metadata rejects). Existing user keywords are preserved."""
    try:
        kw = (metadata or {}).get("keywords") or ""
    except Exception:
        kw = ""
    kept = [t.strip() for t in kw.split(";")
            if t.strip() and not t.strip().startswith(_MARK_PREFIX)]
    kept.append(_marker_payload(quality))
    out = {}
    try:
        for k, v in (metadata or {}).items():
            if k in _META_KEYS:
                out[k] = v
    except Exception:
        pass
    out["keywords"] = "; ".join(kept)
    return out


def _output_has_marker(output_path, quality):
    """True if an existing output file already carries our preset marker."""
    try:
        if not output_path or not os.path.isfile(output_path):
            return False
        doc = fitz.open(output_path)
        try:
            mark = _read_marker(doc.metadata)
        finally:
            doc.close()
        return bool(mark and mark[0] == quality)
    except Exception:
        return False


def _skipped_result(filename, size, quality, note):
    s = _size_str(size)
    return {
        "file": filename,
        "original_size": size,
        "original_size_str": s,
        "final_size": size,
        "final_size_str": s,
        "savings_percent": 0,
        "preset": quality,
        "skipped": True,
        "note": note,
    }


# Archivos comprimidos: se ignoran por completo (ni se listan ni se tocan).
# Solo se procesan PDFs sueltos. Incluye doble extension (doc.pdf.zip)
# y deteccion por firma para PDFs mal nombrados que en realidad son ZIP.
_ARCHIVE_EXTS = {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2",
                  ".xz", ".cbz", ".cbr"}
_ARCHIVE_MAGICS = (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08",
                     b"Rar!", b"7z\xbc\xaf\x27\x1c")


def _is_archive(path):
    """True si es un archivo comprimido (por extension o firma). Nunca lanza."""
    try:
        lowered = path.lower()
        for ext in _ARCHIVE_EXTS:
            if lowered.endswith(ext):
                return True
        with open(path, "rb") as fh:
            head = fh.read(4)
        return head.startswith(_ARCHIVE_MAGICS)
    except Exception:
        return False


def _iter_pdf_candidates(inputs):
    """Yield (source_root or None, file_path) lazily.

    Only filters by extension (cheap string check, no file opens) so the
    first candidate is available almost immediately even on huge trees.
    Archive-signature filtering is deferred to the worker thread.
    """
    for p in inputs:
        if os.path.isdir(p):
            for dirpath, _, filenames in os.walk(p):
                for entry in filenames:
                    if entry.lower().endswith(".pdf"):
                        yield (p, os.path.join(dirpath, entry))
        elif os.path.isfile(p):
            yield (None, p)


def _collect_pdfs(path):
    """Collect PDFs from a single file or a directory.

    Directories are scanned recursively: PDFs in the folder itself and in
    subfolders at any depth (children, grandchildren, ...) are included.
    Compressed archives (.zip, .rar, .7z, ...) are ignored entirely:
    neither listed nor opened, even if passed directly.
    """
    if os.path.isdir(path):
        pdfs = []
        for dirpath, _, filenames in os.walk(path):
            for entry in filenames:
                if entry.lower().endswith(".pdf"):
                    full = os.path.join(dirpath, entry)
                    if not _is_archive(full):
                        pdfs.append(full)
        return pdfs
    elif os.path.isfile(path):
        if _is_archive(path):
            return []
        return [path]
    return []


def _resolve_jobs(jobs):
    """Resolve worker count: None/0 means auto, 1 is sequential legacy."""
    if jobs is None or jobs == 0:
        return min(8, os.cpu_count() or 4)
    return max(1, int(jobs))


def _output_path(root, path, output_dir, in_place):
    """Resolve the destination path, creating subfolders for mirrored trees."""
    if in_place:
        return path
    if root is not None:
        # Mirror the subfolder structure under output_dir.
        rel = os.path.relpath(path, root)
        out = os.path.join(output_dir, rel)
        parent = os.path.dirname(out)
        if parent:
            os.makedirs(parent, exist_ok=True)
        return out
    return os.path.join(output_dir, os.path.basename(path))


def _compress_single(root, path, output_dir, in_place, params, quality, force=False):
    """Compress a single PDF. Thread-safe: no shared state, no callbacks.

    Unless force=True, files already carrying our preset marker are skipped:
    in-place mode reads the marker from the file itself, copy mode from a
    previous output with the same relative path.
    """
    filename = os.path.basename(path)
    try:
        original_size = os.path.getsize(path)
    except OSError:
        return {
            "file": filename,
            "original_size": 0,
            "original_size_str": "0 B",
            "final_size": 0,
            "final_size_str": "0 B",
            "savings_percent": 0,
            "preset": quality,
            "error": "No se pudo leer el archivo",
        }

    if original_size == 0:
        return {
            "file": filename,
            "original_size": 0,
            "original_size_str": "0 B",
            "final_size": 0,
            "final_size_str": "0 B",
            "savings_percent": 0,
            "preset": quality,
        }

    output_path = _output_path(root, path, output_dir, in_place)

    if not force and not in_place and _output_has_marker(output_path, quality):
        return _skipped_result(filename, original_size, quality,
                               f"Ya comprimido ({quality}), omitido")

    try:
        doc = fitz.open(path)
    except Exception:
        return {
            "file": filename,
            "original_size": original_size,
            "original_size_str": _size_str(original_size),
            "final_size": original_size,
            "final_size_str": _size_str(original_size),
            "savings_percent": 0,
            "preset": quality,
            "error": "Error al comprimir",
        }

    if in_place and not force:
        mark = _read_marker(doc.metadata)
        if mark and mark[0] == quality:
            doc.close()
            return _skipped_result(filename, original_size, quality,
                                   f"Ya comprimido ({quality}), omitido")

    try:
        doc.set_metadata(_write_marker(doc.metadata, quality))
        if in_place:
            tmp_path = output_path + ".utilspress-tmp"
            doc.save(tmp_path, **params)
            doc.close()  # release the source handle before replacing (Windows)
            os.replace(tmp_path, output_path)
        else:
            doc.save(output_path, **params)
            doc.close()
    except Exception:
        try:
            doc.close()
        except Exception:
            pass
        return {
            "file": filename,
            "original_size": original_size,
            "original_size_str": _size_str(original_size),
            "final_size": original_size,
            "final_size_str": _size_str(original_size),
            "savings_percent": 0,
            "preset": quality,
            "error": "Error al comprimir",
        }

    final_size = os.path.getsize(output_path)
    savings = 100 * (1 - final_size / original_size) if original_size > 0 else 0

    return {
        "file": filename,
        "original_size": original_size,
        "original_size_str": _size_str(original_size),
        "final_size": final_size,
        "final_size_str": _size_str(final_size),
        "savings_percent": round(savings, 2),
        "preset": quality,
    }


_SENTINEL = object()


def compress_pdfs(paths, output_dir=None, quality="ebook", on_progress=None, in_place=False, jobs=None, on_start=None, on_discover=None, force=False):
    """Compress PDFs with overlapping scan + process (streaming).

    The directory walk runs in a scanner thread that feeds a bounded queue
    while worker threads compress candidates as they arrive: the first
    file starts processing long before counting finishes (key for 1000+
    file batches). Callbacks:
      - on_discover(found): throttled, grows while scanning.
      - on_start(total): exact total, once scanning completes.
      - on_progress(result): once per finished file (incl. skipped/error).
    Results are returned in discovery order.
    Unless force=True, files already carrying our preset marker
    (utilspress:<preset>:<date> in Keywords) are skipped.
    """
    if isinstance(paths, str):
        inputs = [paths]
    else:
        inputs = list(paths)

    if output_dir is None and not in_place:
        output_dir = OUTPUT_BASE

    if not in_place:
        os.makedirs(output_dir, exist_ok=True)

    params = PRESETS.get(quality, PRESETS["ebook"])
    workers = _resolve_jobs(jobs)
    consumers = workers if workers > 1 else 1

    q = queue.Queue(maxsize=256)
    ordered = {}  # index -> result dict
    state_lock = threading.Lock()
    next_index = 0
    found = 0
    last_emit = {"t": 0.0, "n": 0}

    def maybe_emit(n, force=False):
        if not on_discover:
            return
        now = time.monotonic()
        if force or n - last_emit["n"] >= 25 or now - last_emit["t"] >= 0.3:
            last_emit["n"] = n
            last_emit["t"] = now
            on_discover(n)

    def _scan():
        nonlocal next_index, found
        try:
            for root, path in _iter_pdf_candidates(inputs):
                with state_lock:
                    idx = next_index
                    next_index += 1
                    found += 1
                    n = found
                q.put((idx, root, path))
                maybe_emit(n)
        finally:
            # Exact count, even if the walk failed midway: workers must
            # always terminate, and the UI must always leave "searching".
            with state_lock:
                total = next_index
            if on_discover:
                on_discover(total)
            if on_start:
                on_start(total)
            for _ in range(consumers):
                q.put(_SENTINEL)

    def _consume():
        while True:
            item = q.get()
            if item is _SENTINEL:
                return
            idx, root, path = item
            try:
                if _is_archive(path):
                    filename = os.path.basename(path)
                    try:
                        size = os.path.getsize(path)
                    except OSError:
                        size = 0
                    result = _skipped_result(
                        filename, size, quality,
                        "Omitido: es un archivo comprimido")
                else:
                    result = _compress_single(root, path, output_dir, in_place, params, quality, force)
            except Exception as exc:  # a loose file must never stall 1000-file batches
                filename = os.path.basename(path)
                result = {
                    "file": filename,
                    "original_size": 0,
                    "original_size_str": "0 B",
                    "final_size": 0,
                    "final_size_str": "0 B",
                    "savings_percent": 0,
                    "preset": quality,
                    "error": f"Error inesperado: {exc}",
                }
            with state_lock:
                ordered[idx] = result
            if on_progress:
                on_progress(result)

    scanner = threading.Thread(target=_scan, name="pdf-scan", daemon=True)
    scanner.start()
    if workers == 1:
        _consume()  # sequential: main thread is the single consumer
        scanner.join()
    else:
        pool = [
            threading.Thread(target=_consume, name=f"pdf-work-{i}", daemon=True)
            for i in range(workers)
        ]
        for t in pool:
            t.start()
        scanner.join()
        for t in pool:
            t.join()
    return [ordered[i] for i in sorted(ordered)]
