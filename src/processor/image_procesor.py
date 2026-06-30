from PIL import Image as pl
from rich import print
from rich.text import Text
from rich.console import Console
from rich.padding import Padding
import os

OUTPUT_BASE = os.path.join(os.path.expanduser("~"), "Desktop")


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

def compress_images(paths, output_dir=None, quality=None, compress_level=None):
    if isinstance(paths, str):
        paths = _collect_images(paths)
    if output_dir is None:
        output_dir = OUTPUT_BASE
    os.makedirs(output_dir, exist_ok=True)

    results = []
    for path in paths:
        filename = os.path.basename(path)
        ext = os.path.splitext(filename)[1].replace(".", "").upper()
        original_size = os.path.getsize(path)

        img = pl.open(path)
        save_args = {"optimize": True}

        if ext in ("JPEG", "JPG"):
            save_args["quality"] = quality if quality is not None else 85
        elif ext == "PNG":
            save_args["compress_level"] = compress_level if compress_level is not None else 6
        elif ext == "WEBP":
            save_args["quality"] = quality if quality is not None else 80

        output_path = os.path.join(output_dir, filename)
        img.save(output_path, **save_args)
        final_size = os.path.getsize(output_path)
        savings = 100 * (1 - final_size / original_size) if original_size > 0 else 0

        results.append({
            "file": filename,
            "original_size": original_size,
            "original_size_str": _size_str(original_size),
            "final_size": final_size,
            "final_size_str": _size_str(final_size),
            "savings_percent": round(savings, 2),
        })

    return results


def convert_images(paths, target_format, output_dir=None):
    if isinstance(paths, str):
        paths = _collect_images(paths)
    if output_dir is None:
        output_dir = OUTPUT_BASE
    os.makedirs(output_dir, exist_ok=True)

    results = []
    for path in paths:
        filename = os.path.basename(path)
        name_no_ext = os.path.splitext(filename)[0]
        original_size = os.path.getsize(path)

        img = pl.open(path)
        output_filename = f"{name_no_ext}.{target_format.lower()}"
        output_path = os.path.join(output_dir, output_filename)

        img.save(output_path, format=target_format.upper())
        final_size = os.path.getsize(output_path)

        results.append({
            "file": filename,
            "new_file": output_filename,
            "original_size": original_size,
            "original_size_str": _size_str(original_size),
            "final_size": final_size,
            "final_size_str": _size_str(final_size),
        })

    return results


def resize_images(paths, width, height, output_dir=None, maintain_aspect=True):
    if isinstance(paths, str):
        paths = _collect_images(paths)
    if output_dir is None:
        output_dir = OUTPUT_BASE
    os.makedirs(output_dir, exist_ok=True)

    results = []
    for path in paths:
        filename = os.path.basename(path)
        original_size = os.path.getsize(path)

        img = pl.open(path)
        orig_w, orig_h = img.size

        if maintain_aspect:
            img.thumbnail((width, height), pl.LANCZOS)
        else:
            img = img.resize((width, height), pl.LANCZOS)

        output_path = os.path.join(output_dir, filename)
        img.save(output_path)
        final_size = os.path.getsize(output_path)

        results.append({
            "file": filename,
            "original_size": original_size,
            "original_size_str": _size_str(original_size),
            "final_size": final_size,
            "final_size_str": _size_str(final_size),
            "original_dims": f"{orig_w}x{orig_h}",
            "final_dims": f"{img.width}x{img.height}",
        })

    return results
