def entry_point():
    # Pre-crea <Documentos real>/flet antes de que Flet inicie su storage.
    # En Windows en español / OneDrive esa carpeta no existe y Flet crashea
    # al arrancar; esto nunca debe romper el arranque (defensivo extra).
    try:
        try:
            from utils.paths import ensure_flet_storage
        except ImportError:  # instalado como paquete `src.*`
            from src.utils.paths import ensure_flet_storage
        ensure_flet_storage()
    except Exception:
        pass
    from gui.app import start
    start()


if __name__ == "__main__":
    entry_point()
