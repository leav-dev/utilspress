# BIBLIOTECAS
from rich import print
from rich.text import Text
from rich.console import Console
from rich.padding import Padding
import time

# ARCHIVOS INTERNOS
from processor.image_procesor import *

def bienvenida():
    console = Console()
    text = Text()
    text.append("Que quieres hacer:")
    text_paddind = Padding(text, (1,3))
    console.print(text_paddind, style= "bold magenta")
    print("0. salir")
    print("1. Comprimir imagenes")
    print("2. Cambiar formatos de imagenes")
    # print("1. Comprimir imagenes")
    # print("1. Comprimir imagenes")
    print("\n [bold]Cual opcion usara: [/bold]")
    opcion = input().strip()
    if opcion == "1":
        # text = Text()
        # text.append("puede definir la ruta que quiere del archivo o carrpeta de imagenes que quiere comprimir:")
        # text_paddind = Padding(text, (1,3))
        # console.print(text_paddind, style= "bold magenta")
        # ruta = input().strip()
        comprimir()
        return
    elif opcion == "2":
        return
    elif opcion == "0":
        print("[yellow]Saliendo...[/yellow]")
        time.sleep(1)
        return
    else:
        print("[red]seleciona una de las opciones disponibles.[/red]")
        bienvenida()



# def detectar_opcion():
#     return

if __name__ == "__main__":
    bienvenida()


