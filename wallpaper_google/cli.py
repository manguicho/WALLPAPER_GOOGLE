import argparse

from . import __version__, paths


def main(argv=None) -> None:
    p = argparse.ArgumentParser(
        prog="wallpaper-google",
        description="Fondos de pantalla aleatorios desde Google Fotos (GNOME).",
    )
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("login", help="Iniciar sesión en Google")
    e = sub.add_parser("elegir", help="Elegir fotos en Google Fotos y descargarlas")
    e.add_argument("--reemplazar", action="store_true",
                   help="Borra las fotos que ya tenías antes de descargar las nuevas")
    sub.add_parser("siguiente", help="Poner un fondo al azar ahora")
    a = sub.add_parser("auto", help="Cambiar el fondo automáticamente")
    a.add_argument("cada", nargs="?", default="30min",
                   help="Intervalo (ej. 15min, 1h, 2h). Por defecto 30min")
    sub.add_parser("auto-off", help="Desactivar el cambio automático")
    sub.add_parser("estado", help="Mostrar cuántas fotos hay y dónde")
    args = p.parse_args(argv)

    if args.cmd == "login":
        from .auth import get_credentials
        get_credentials()
        print("Sesión iniciada.")
    elif args.cmd == "elegir":
        from .auth import session
        from .picker import download, pick
        sess = session()
        picked = pick(sess)
        if args.reemplazar:
            for f in paths.PHOTOS_DIR.glob("*"):
                f.unlink()
        n = download(sess, picked)
        print(f"{n} fotos listas en {paths.PHOTOS_DIR}")
        if n:
            from .wallpaper import next_random
            print(f"Fondo puesto: {next_random().name}")
    elif args.cmd == "siguiente":
        from .wallpaper import next_random
        print(f"Fondo puesto: {next_random().name}")
    elif args.cmd == "auto":
        from .timer import install
        install(args.cada)
    elif args.cmd == "auto-off":
        from .timer import uninstall
        uninstall()
    elif args.cmd == "estado":
        from .wallpaper import photos
        print(f"Fotos: {len(photos())} en {paths.PHOTOS_DIR}")
        print(f"Credenciales: {paths.CLIENT_SECRET} "
              f"({'ok' if paths.CLIENT_SECRET.exists() else 'falta'})")
        print(f"Sesión: {'ok' if paths.TOKEN_FILE.exists() else 'sin iniciar'}")


if __name__ == "__main__":
    main()
