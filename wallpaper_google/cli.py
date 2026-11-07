import argparse
import re

from . import __version__, paths, store


def main(argv=None) -> None:
    p = argparse.ArgumentParser(
        prog="wallpaper-google",
        description="Fondo de pantalla al azar desde un álbum compartido de Google Fotos (GNOME).",
    )
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("album", help="Configurar el enlace del álbum compartido")
    a.add_argument("enlace")
    sub.add_parser("siguiente", help="Bajar una foto al azar y ponerla de fondo ahora")
    t = sub.add_parser("auto", help="Cambiar el fondo automáticamente")
    t.add_argument("cada", nargs="?", default="30min",
                   help="Intervalo (ej. 15min, 1h, 2h). Por defecto 30min")
    sub.add_parser("auto-off", help="Desactivar el cambio automático")
    r = sub.add_parser("resolucion", help="Fijar la resolución de descarga (ej. 2560x1440)")
    r.add_argument("tam", help="ANCHOxALTO, o 'auto' para detectarla de la pantalla")
    v = sub.add_parser("verticales", help="Incluir o no las fotos verticales (por defecto no)")
    v.add_argument("valor", choices=["si", "no"])
    sub.add_parser("estado", help="Mostrar la configuración actual")
    args = p.parse_args(argv)
    cfg = store.load(paths.CONFIG_FILE)

    if args.cmd == "album":
        from .album import refresh
        n = len(refresh(args.enlace, verbose=True))
        cfg["album"] = args.enlace
        store.save(paths.CONFIG_FILE, cfg)
        print(f"Álbum guardado: {n} fotos encontradas.")
    elif args.cmd == "siguiente":
        from .wallpaper import next_random
        next_random()
        print("Fondo cambiado.")
    elif args.cmd == "auto":
        from .timer import install
        install(args.cada)
    elif args.cmd == "auto-off":
        from .timer import uninstall
        uninstall()
    elif args.cmd == "resolucion":
        if args.tam == "auto":
            cfg.pop("resolucion", None)
        else:
            m = re.fullmatch(r"(\d+)x(\d+)", args.tam)
            if not m:
                p.error("usa el formato ANCHOxALTO, por ejemplo 2560x1440")
            cfg["resolucion"] = [int(m[1]), int(m[2])]
        store.save(paths.CONFIG_FILE, cfg)
        print("Resolución guardada.")
    elif args.cmd == "verticales":
        cfg["verticales"] = args.valor == "si"
        store.save(paths.CONFIG_FILE, cfg)
        print("Fotos verticales " + ("incluidas." if cfg["verticales"] else "excluidas."))
    elif args.cmd == "estado":
        from .wallpaper import screen_resolution
        data = store.load(paths.ALBUM_FILE)
        print(f"Álbum: {cfg.get('album', 'sin configurar')}")
        fotos = data.get("photos", [])
        horiz = sum(1 for f in fotos if isinstance(f, list) and f[1] >= f[2])
        print(f"Fotos en la lista: {len(fotos)} ({horiz} horizontales)")
        print(f"Verticales: {'incluidas' if cfg.get('verticales') else 'excluidas'}")
        res = cfg.get("resolucion") or screen_resolution()
        print(f"Resolución de descarga: {res[0]}x{res[1]}")


if __name__ == "__main__":
    main()
