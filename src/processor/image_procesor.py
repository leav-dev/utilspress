from PIL import Image as pl
import os
from datetime import date as _date

try:
    from utils.paths import get_output_base
except ImportError:  # instalado como paquete `src.*`
    from src.utils.paths import get_output_base

OUTPUT_BASE = get_output_base()


# Firma anti-reproceso: viaja dentro del propio archivo, sin sidecars.
# PNG -> chunk tEXt "utilspress" | JPEG -> marcador COM | WEBP -> EXIF
# UserComment (0x9286). Formato: "<op>:<setting>:<aaaammdd>".
_MARK_KEY = "utilspress"
_EXIF_USER_COMMENT = 0x9286


def _marker_payload(op, setting):
    return f"{op}:{setting}:{_date.today().strftime('%Y%m%d')}"


def _marker_match(stored, op, setting):
    try:
        parts = (stored or "").split(":")
        return len(parts) >= 2 and parts[0] == op and parts[1] == setting
    except Exception:
        return False


def _read_image_marker(img):
    """Read our marker from an open Pillow image. Never raises."""
    try:
        txt = getattr(img, "text", None)
        if isinstance(txt, dict) and _MARK_KEY in txt:
            return txt[_MARK_KEY]
        info = getattr(img, "info", None) or {}
        c = info.get("comment")
        if isinstance(c, bytes):
            c = c.decode("utf-8", "replace")
        if isinstance(c, str) and c:
            return c
        try:
            ex = img.getexif()
        except Exception:
            ex = None
        v = ex.get(_EXIF_USER_COMMENT) if ex else None
        if isinstance(v, str) and v:
            return v
    except Exception:
        pass
    return None


def _marker_write_kwargs(img, img_format, payload):
    """Save kwargs that embed our marker for the target format."""
    fmt = (img_format or "").upper()
    if fmt == "PNG":
        from PIL.PngImagePlugin import PngInfo
        info = PngInfo()
        info.add_text(_MARK_KEY, payload)
        return {"pnginfo": info}
    if fmt in ("JPEG", "JPG"):
        return {"comment": payload.encode("utf-8")}
    if fmt == "WEBP":
        try:
            ex = img.getexif()
        except Exception:
            ex = None
        if ex is None:
            from PIL.Image import Exif as _Exif
            ex = _Exif()
        ex[_EXIF_USER_COMMENT] = payload
        return {"exif": ex}
    return {}


def _output_image_marked(output_path, op, setting):
    """True if an existing output file already carries our op marker."""
    try:
        if not output_path or not os.path.isfile(output_path):
            return False
        probe = pl.open(output_path)
        probe.load()
        try:
            stored = _read_image_marker(probe)
        finally:
            probe.close()
        return _marker_match(stored, op, setting)
    except Exception:
        return False


# ── Helpers ──────────────────────────────────────────────────────────

def _size_str(bytes_val):
    if bytes_val >= 1024 * 1024:
        return f"{bytes_val / (1024*1024):.2f} MB"
    return f"{bytes_val / 1024:.2f} KB"


def _collect_images(path, formato=None):
    """Return a list of image paths from a file or directory."""
    if os.path.isdir(path):
        images = detectar_imagenes(path, formato or "")
        if not images and not formato:
            ext_map = {"JPEG": ".jpg", "JPG": ".jpg", "PNG": ".png", "WEBP": ".webp"}
            images = detectar_imagenes(path, "JPG") + detectar_imagenes(path, "JPEG") + detectar_imagenes(path, "PNG") + detectar_imagenes(path, "WEBP")
        return images
    elif os.path.isfile(path):
        return [path]
    return []


# ── Funciones originales (CLI) ───────────────────────────────────────

def detectar_imagenes(ruta, formato):
    imagenes = []
    archivos = os.listdir(ruta)
    for archivo in archivos:
        ruta_archivo = os.path.join(ruta, archivo)
        if os.path.isfile(ruta_archivo):
            ruta_archivo = os.path.join(ruta, archivo)
            _, extension = os.path.splitext(archivo)
            extension = extension.replace(".", "").upper()
            if extension == formato.upper():
                imagenes.append(ruta_archivo)
    return imagenes

def imagen_compresor(ruta):
    from rich import print
    image = pl.open(ruta)
    _, extension = os.path.splitext(ruta)
    extension = extension.replace(".", "").upper()
    tamañoI = os.path.getsize(ruta)
    save_args = {"optimize": True}

    if extension == "JPEG" or extension == "JPG":
        save_args["quality"] = 85
    elif extension == "PNG":
        save_args["compress_level"] = 6
    elif extension == "WEBP":
        save_args["format"] = "WEBP"
        save_args["quality"] = 80
    else:
        save_args["format"] = image.format

    image.save(ruta, **save_args)
    tamañoF = os.path.getsize(ruta)
    ahorro = 100 * (1-tamañoF / tamañoI)
    print(f"se comprimio la imagen en la ruta: {ruta}. la imagen se redujo en {ahorro:.2f}%")
    return ahorro

def procesar(ruta, args: dict):
    from rich import print
    proceso = args['proceso']
    formato = args['formato']
    conta = 0
    total_ahorro = 0.0
    lista_imagenes = []
    if os.path.isdir(ruta):
        images = detectar_imagenes(ruta, formato)
        if proceso =="comprimir":
            for image in images:
                conta += 1
                total_ahorro += imagen_compresor(image)
        if proceso =="formatear":
            for image in images:
                args['formato']
                lista_imagenes.append(image)
        if proceso =="redimensionar":
            for image in images:
                ancho = args['ancho']
                alto = args['alto']
                lista_imagenes.append(image)
    else:
        images = ruta
        if proceso =="comprimir":
            total_ahorro += imagen_compresor(images)
        if proceso =="formatear":
            lista_imagenes.append(images)
        if proceso =="redimensionar":
            lista_imagenes.append(images)
        conta += 1
    if conta > 0:
        if proceso == "comprimir":
            promedio = total_ahorro / conta
            print(f"\n✅ Se procesaron {conta} imagen(es).")
            print(f"📉 Ahorro promedio: {promedio:.2f}%")
        if proceso == "formatear":
            images.sort()
            lista_imagenes.sort()
            if len(images) == len(lista_imagenes):
                print("Se formatearon tod")
            for imagenO, imagenM in zip(images, lista_imagenes):
                print(f"Se formateo la imagen {imagenO} -> {imagenM}")
        if proceso == "redeimensionar":
            images.sort()
            lista_imagenes.sort()
            for imagenO, imagenM in zip(images, lista_imagenes):
                print(f"Reformateo la imagen {imagenO} -> {imagenM}")
    else:
        print("⚠ No se procesaron imágenes.")
    return

def comprimir():
    from rich import print
    from rich.text import Text
    from rich.console import Console
    from rich.padding import Padding
    console = Console()
    text = Text()
    text.append("puede definir la ruta que quiere del archivo o carrpeta de imagenes que quiere comprimir:")
    text_paddind = Padding(text, (1,3))
    console.print(text_paddind, style= "bold magenta")
    ruta = input().strip()

    confir = input("¿La ruta especificada es correcta? (Y/N): ").strip().upper()
    if confir == "Y":
        print("Que formato quiere comprirmir ([cyan]JPG, PNG, WEBP[/cyan]).\n[yellow]Si no encuentra el escribalo para proceder[/yellow]")
        formato = input().strip()
        procesar(ruta, {"proceso":"comprimir", "formato": formato})
    else:
        comprimir()


# ── Nuevas funciones puras (Web GUI) ─────────────────────────────────

def _overwrite_with_tmp(img, final_path, save_args, fmt=None):
    """Save to a temp file and atomically replace final_path.

    The temp round-trip avoids truncating the source while Pillow still
    holds it open (required on Windows, where open files can't be replaced).
    """
    tmp_path = final_path + ".utilspress-tmp"
    kwargs = dict(save_args)
    if fmt:
        kwargs["format"] = fmt
    img.save(tmp_path, **kwargs)
    img.close()  # release the source handle before replacing (Windows)
    os.replace(tmp_path, final_path)


def compress_images(paths, output_dir=None, quality=None, compress_level=None, on_progress=None, in_place=False, on_start=None, force=False):
    if isinstance(paths, str):
        paths = _collect_images(paths)
    else:
        expanded = []
        for p in paths:
            expanded.extend(_collect_images(p))
        paths = expanded
    if on_start:
        on_start(len(paths))
    if output_dir is None and not in_place:
        output_dir = OUTPUT_BASE
    if not in_place:
        os.makedirs(output_dir, exist_ok=True)

    results = []
    for path in paths:
        filename = os.path.basename(path)
        ext = os.path.splitext(filename)[1].replace(".", "").upper()
        original_size = os.path.getsize(path)

        if ext in ("JPEG", "JPG"):
            setting = f"q{quality if quality is not None else 85}"
        elif ext == "PNG":
            setting = f"c{compress_level if compress_level is not None else 6}"
        elif ext == "WEBP":
            setting = f"q{quality if quality is not None else 80}"
        else:
            setting = None  # formato sin soporte de firma: siempre procesar
        payload = _marker_payload("compress", setting) if setting else None

        if in_place:
            output_path = path
        else:
            output_path = os.path.join(output_dir, filename)

        img = pl.open(path)
        img.load()
        pillow_format = img.format

        if (setting and not force
                and (_marker_match(_read_image_marker(img), "compress", setting)
                     or (not in_place and _output_image_marked(output_path, "compress", setting)))):
            img.close()
            s = _size_str(original_size)
            result = {
                "file": filename,
                "original_size": original_size,
                "original_size_str": s,
                "final_size": original_size,
                "final_size_str": s,
                "savings_percent": 0,
                "skipped": True,
                "note": f"Ya comprimido ({setting}), omitido",
            }
            results.append(result)
            if on_progress:
                on_progress(result)
            continue

        save_args = {"optimize": True}

        if ext in ("JPEG", "JPG"):
            save_args["quality"] = quality if quality is not None else 85
        elif ext == "PNG":
            save_args["compress_level"] = compress_level if compress_level is not None else 6
        elif ext == "WEBP":
            save_args["quality"] = quality if quality is not None else 80

        marker_kw = _marker_write_kwargs(img, pillow_format, payload) if payload else {}
        if in_place:
            _overwrite_with_tmp(img, output_path, {**save_args, **marker_kw}, fmt=pillow_format)
        else:
            img.save(output_path, **save_args, **marker_kw)
            img.close()
        final_size = os.path.getsize(output_path)
        savings = 100 * (1 - final_size / original_size) if original_size > 0 else 0

        result = {
            "file": filename,
            "original_size": original_size,
            "original_size_str": _size_str(original_size),
            "final_size": final_size,
            "final_size_str": _size_str(final_size),
            "savings_percent": round(savings, 2),
        }
        results.append(result)
        if on_progress:
            on_progress(result)

    return results


def convert_images(paths, target_format, output_dir=None, on_progress=None, in_place=False, on_start=None, force=False):
    if isinstance(paths, str):
        paths = _collect_images(paths)
    else:
        expanded = []
        for p in paths:
            expanded.extend(_collect_images(p))
        paths = expanded
    if on_start:
        on_start(len(paths))
    if output_dir is None and not in_place:
        output_dir = OUTPUT_BASE
    if not in_place:
        os.makedirs(output_dir, exist_ok=True)

    fmt = target_format.upper()
    if fmt == "JPG":
        fmt = "JPEG"

    results = []
    for path in paths:
        filename = os.path.basename(path)
        name_no_ext = os.path.splitext(filename)[0]
        original_size = os.path.getsize(path)
        setting = fmt.lower()
        payload = _marker_payload("convert", setting)

        img = pl.open(path)
        img.load()
        output_filename = f"{name_no_ext}.{fmt.lower()}"
        if in_place:
            output_path = os.path.join(os.path.dirname(path), output_filename)
        else:
            output_path = os.path.join(output_dir, output_filename)

        if (not force
                and (_marker_match(_read_image_marker(img), "convert", setting)
                     or (not in_place and _output_image_marked(output_path, "convert", setting)))):
            img.close()
            s = _size_str(original_size)
            result = {
                "file": filename,
                "new_file": output_filename,
                "original_size": original_size,
                "original_size_str": s,
                "final_size": original_size,
                "final_size_str": s,
                "skipped": True,
                "note": f"Ya convertido a {setting}, omitido",
            }
            results.append(result)
            if on_progress:
                on_progress(result)
            continue

        marker_kw = _marker_write_kwargs(img, fmt, payload)
        if fmt == "JPEG" and img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        if in_place:
            _overwrite_with_tmp(img, output_path, marker_kw, fmt=fmt)
            if os.path.abspath(output_path) != os.path.abspath(path):
                os.remove(path)
        else:
            img.save(output_path, format=fmt, **marker_kw)
            img.close()
        final_size = os.path.getsize(output_path)

        orig_str = _size_str(original_size)
        final_str = _size_str(final_size)
        result = {
            "file": filename,
            "new_file": output_filename,
            "original_size": original_size,
            "original_size_str": orig_str,
            "final_size": final_size,
            "final_size_str": final_str,
        }
        results.append(result)
        if on_progress:
            on_progress(result)

    return results


def resize_images(paths, width, height, output_dir=None, maintain_aspect=True, on_progress=None, in_place=False, on_start=None, force=False):
    if isinstance(paths, str):
        paths = _collect_images(paths)
    else:
        expanded = []
        for p in paths:
            expanded.extend(_collect_images(p))
        paths = expanded
    if on_start:
        on_start(len(paths))
    if output_dir is None and not in_place:
        output_dir = OUTPUT_BASE
    if not in_place:
        os.makedirs(output_dir, exist_ok=True)

    setting = f"{width}x{height}{'a' if maintain_aspect else 'f'}"
    payload = _marker_payload("resize", setting)

    results = []
    for path in paths:
        filename = os.path.basename(path)
        original_size = os.path.getsize(path)

        if in_place:
            output_path = path
        else:
            output_path = os.path.join(output_dir, filename)

        img = pl.open(path)
        img.load()
        pillow_format = img.format
        orig_w, orig_h = img.size

        if (not force
                and (_marker_match(_read_image_marker(img), "resize", setting)
                     or (not in_place and _output_image_marked(output_path, "resize", setting)))):
            img.close()
            s = _size_str(original_size)
            dims = f"{orig_w}x{orig_h}"
            result = {
                "file": filename,
                "original_size": original_size,
                "original_size_str": s,
                "final_size": original_size,
                "final_size_str": s,
                "original_dims": dims,
                "final_dims": dims,
                "skipped": True,
                "note": f"Ya redimensionado a {setting}, omitido",
            }
            results.append(result)
            if on_progress:
                on_progress(result)
            continue

        marker_kw = _marker_write_kwargs(img, pillow_format, payload)
        if maintain_aspect:
            img.thumbnail((width, height), pl.LANCZOS)
        else:
            img = img.resize((width, height), pl.LANCZOS)

        if in_place:
            _overwrite_with_tmp(img, output_path, marker_kw, fmt=pillow_format)
        else:
            img.save(output_path, **marker_kw)
            img.close()
        final_size = os.path.getsize(output_path)

        orig_str = _size_str(original_size)
        final_str = _size_str(final_size)
        orig_dims = f"{orig_w}x{orig_h}"
        final_dims = f"{img.width}x{img.height}"
        result = {
            "file": filename,
            "original_size": original_size,
            "original_size_str": orig_str,
            "final_size": final_size,
            "final_size_str": final_str,
            "original_dims": orig_dims,
            "final_dims": final_dims,
        }
        results.append(result)
        if on_progress:
            on_progress(result)

    return results
