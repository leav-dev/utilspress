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

### Descargar ejecutable (recomendado)

Descargá la última versión desde [Releases](https://github.com/leav-dev/utilspress/releases). No requiere Python ni dependencias.

| Plataforma | Archivo | Uso |
|---|---|---|
| **Linux** | `utilspress-linux.AppImage` | Doble clic → "Run" |
| **macOS** | `utilspress-macos.dmg` | Abrir y arrastrar a Applications |
| **Windows** | `utilspress-windows.exe` | Doble clic para extraer y ejecutar |

### Con Python y pip

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

### GitHub Releases

El proyecto incluye un workflow de GitHub Actions que compila para **Linux**, **macOS** y **Windows**, empaquetando cada uno como un solo archivo ejecutable autónomo. Para publicar una nueva versión, creá un tag con formato `v*`:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Esto genera automáticamente una Release en GitHub con los ejecutables adjuntos y notas de versión.

### Build local

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
