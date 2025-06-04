from PIL import Image as pl
from rich import print
from rich.text import Text
from rich.console import Console
from rich.padding import Padding
import os

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

# def formatear():


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