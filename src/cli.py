"""utilspress CLI — terminal version of the desktop app.

By default the original files are replaced in place. Pass -o/--output-dir
to write the results to a folder instead and keep the originals.

Usage:
    utilspress-cli compress <path...> [-o DIR] [--quality 85] [--compress-level 6]
    utilspress-cli convert <path...> --to jpg|png|webp [-o DIR]
    utilspress-cli resize <path...> --width W --height H [--no-keep-aspect] [-o DIR]
    utilspress-cli pdf <path...> [--preset screen|ebook|printer|prepress] [-o DIR]
    utilspress-cli zip <folder> [--output FILE.zip] [--level 0-9]

Each <path> can be a file or a directory (PDF folders are scanned
recursively including subfolders, image folders non-recursively,
same as the GUI).
"""

import argparse
import os
import sys

# Allow both `python src/cli.py` and installed `utilspress-cli` entry point.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from processor.image_procesor import compress_images, convert_images, resize_images
    from processor.pdf_procesor import compress_pdfs, PRESETS
    from processor.zip_procesor import compress_folder
except ImportError:  # installed as `src.cli`
    from src.processor.image_procesor import compress_images, convert_images, resize_images
    from src.processor.pdf_procesor import compress_pdfs, PRESETS
    from src.processor.zip_procesor import compress_folder

KEEP_ORIGINALS_HELP = ("Carpeta destino; si se omite, "
                       "los archivos originales se reemplazan")


def _describe_dest(output_dir):
    return output_dir if output_dir else "originales (reemplazados)"


def _print_image_result(r, kind):
    if kind == "convert":
        print(f"  {r['file']} -> {r['new_file']} "
              f"({r['original_size_str']} -> {r['final_size_str']})")
    elif kind == "resize":
        print(f"  {r['file']} {r['original_dims']} -> {r['final_dims']} "
              f"({r['original_size_str']} -> {r['final_size_str']})")
    else:
        print(f"  {r['file']} "
              f"({r['original_size_str']} -> {r['final_size_str']}, "
              f"ahorro {r['savings_percent']}%)")


def cmd_compress(args):
    in_place = args.output_dir is None
    results = compress_images(
        args.paths,
        output_dir=args.output_dir,
        quality=args.quality,
        compress_level=args.compress_level,
        in_place=in_place,
    )
    if not results:
        print("No se encontraron imagenes para comprimir.")
        return 1
    for r in results:
        _print_image_result(r, "compress")
    avg = sum(r["savings_percent"] for r in results) / len(results)
    print(f"Se procesaron {len(results)} imagen(es) en "
          f"{_describe_dest(args.output_dir)}. "
          f"Ahorro promedio: {avg:.2f}%")
    return 0


def cmd_convert(args):
    in_place = args.output_dir is None
    results = convert_images(
        args.paths,
        args.to.upper(),
        output_dir=args.output_dir,
        in_place=in_place,
    )
    if not results:
        print("No se encontraron imagenes para convertir.")
        return 1
    for r in results:
        _print_image_result(r, "convert")
    print(f"Se convirtieron {len(results)} imagen(es) a {args.to.upper()} "
          f"en {_describe_dest(args.output_dir)}.")
    return 0


def cmd_resize(args):
    in_place = args.output_dir is None
    results = resize_images(
        args.paths,
        args.width,
        args.height,
        output_dir=args.output_dir,
        maintain_aspect=args.keep_aspect,
        in_place=in_place,
    )
    if not results:
        print("No se encontraron imagenes para redimensionar.")
        return 1
    for r in results:
        _print_image_result(r, "resize")
    print(f"Se redimensionaron {len(results)} imagen(es) en "
          f"{_describe_dest(args.output_dir)}.")
    return 0


def cmd_pdf(args):
    in_place = args.output_dir is None
    results = compress_pdfs(
        args.paths,
        output_dir=args.output_dir,
        quality=args.preset,
        in_place=in_place,
    )
    if not results:
        print("No se encontraron PDFs para comprimir.")
        return 1
    for r in results:
        extra = f" [ERROR: {r['error']}]" if "error" in r else ""
        print(f"  {r['file']} "
              f"({r['original_size_str']} -> {r['final_size_str']}, "
              f"ahorro {r['savings_percent']}%){extra}")
    print(f"Se procesaron {len(results)} PDF(s) con preset '{args.preset}' "
          f"en {_describe_dest(args.output_dir)}.")
    return 0


def cmd_zip(args):
    result = compress_folder(
        args.folder,
        output_path=args.output,
        level=args.level,
    )
    print(f"  {result['file']} "
          f"({result['original_size_str']} -> {result['final_size_str']}, "
          f"ahorro {result['savings_percent']}%)")
    print(f"Carpeta comprimida en {result['output_path']}.")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog="utilspress-cli",
        description="Procesa imagenes y PDFs desde la terminal.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("compress", help="Comprime JPG, PNG y WEBP.")
    c.add_argument("paths", nargs="+", help="Archivo(s) o carpeta(s).")
    c.add_argument("-o", "--output-dir", default=None, help=KEEP_ORIGINALS_HELP)
    c.add_argument("--quality", type=int, default=85,
                   help="Calidad JPG/WEBP 1-100 (defecto: 85).")
    c.add_argument("--compress-level", type=int, default=6,
                   help="Nivel PNG 0-9 (defecto: 6).")
    c.set_defaults(func=cmd_compress)

    c = sub.add_parser("convert", help="Convierte entre JPG, PNG y WEBP.")
    c.add_argument("paths", nargs="+", help="Archivo(s) o carpeta(s).")
    c.add_argument("--to", required=True, choices=["jpg", "jpeg", "png", "webp"],
                   help="Formato destino.")
    c.add_argument("-o", "--output-dir", default=None, help=KEEP_ORIGINALS_HELP)
    c.set_defaults(func=cmd_convert)

    c = sub.add_parser("resize", help="Redimensiona imagenes.")
    c.add_argument("paths", nargs="+", help="Archivo(s) o carpeta(s).")
    c.add_argument("--width", type=int, required=True)
    c.add_argument("--height", type=int, required=True)
    c.add_argument("--no-keep-aspect", dest="keep_aspect",
                   action="store_false", default=True,
                   help="No mantener relacion de aspecto.")
    c.add_argument("-o", "--output-dir", default=None, help=KEEP_ORIGINALS_HELP)
    c.set_defaults(func=cmd_resize)

    c = sub.add_parser("pdf", help="Comprime PDFs.")
    c.add_argument("paths", nargs="+", help="Archivo(s) o carpeta(s).")
    c.add_argument("--preset", default="ebook", choices=sorted(PRESETS),
                   help="Preset de compresion (defecto: ebook).")
    c.add_argument("-o", "--output-dir", default=None, help=KEEP_ORIGINALS_HELP)
    c.set_defaults(func=cmd_pdf)

    c = sub.add_parser("zip", help="Comprime una carpeta a ZIP.")
    c.add_argument("folder", help="Carpeta a comprimir.")
    c.add_argument("-o", "--output", default=None,
                   help="Archivo ZIP destino (defecto: <carpeta>.zip).")
    c.add_argument("--level", type=int, default=6,
                   help="Nivel de compresion 0-9 (defecto: 6).")
    c.set_defaults(func=cmd_zip)

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
