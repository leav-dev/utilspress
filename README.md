<div align="center">

# utilspress

**Procesamiento de imágenes y PDF desde tu escritorio**

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Flet](https://img.shields.io/badge/flet-0.28+-informational)
![PyMuPDF](https://img.shields.io/badge/PyMuPDF-latest-green)
[![Build](https://img.shields.io/github/actions/workflow/status/leav-dev/utilspress/build.yml?branch=main&label=build)](https://github.com/leav-dev/utilspress/actions)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

</div>

utilspress es una aplicación de escritorio con interfaz gráfica moderna para procesar imágenes y PDFs. Compresión, conversión de formatos, redimensionado y más — todo desde una GUI limpia construida con [Flet](https://flet.dev).

## ✨ Funcionalidades

- **Comprimir imágenes** — Reduce el peso de JPG, PNG y WEBP manteniendo calidad visual.
- **Convertir formatos** — Transforma imágenes entre JPG, PNG y WEBP al instante.
- **Redimensionar** — Ajusta dimensiones manteniendo o no la relación de aspecto.
- **Comprimir PDFs** — Cuatro presets de compresión (Screen, eBook, Printer, Prepress) vía PyMuPDF.
- **Comprimir carpetas** — Empaqueta y comprime directorios completos a ZIP.

## ⚡ Quick Start

```bash
pip install utilspress
utilspress
```

## 🛠️ Build desde código

```bash
git clone https://github.com/leav-dev/utilspress.git
cd utilspress
pip install -r requirements.txt
uv run python src/main.py
```

## 📦 Build para distribución

El proyecto incluye un workflow de GitHub Actions que genera ejecutables para **Linux**, **macOS** y **Windows** automáticamente en cada push a `main`.

También podés generar un ejecutable localmente:

```bash
flet build linux      # Linux
flet build macos      # macOS
flet build windows    # Windows
```

## 🧰 Tecnologías

| Tecnología | Uso |
|---|---|
| [Python](https://python.org) | Lenguaje principal (3.10+) |
| [Flet](https://flet.dev) | GUI de escritorio multiplataforma |
| [Pillow](https://python-pillow.org) | Procesamiento de imágenes |
| [PyMuPDF](https://pymupdf.readthedocs.io) | Compresión de PDFs |

## 📄 Licencia

Distribuido bajo licencia MIT. Ver [LICENSE](LICENSE) para más información.
