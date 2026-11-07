"""Poner el fondo de pantalla en GNOME y elegir uno al azar."""

import json
import random
import subprocess

from . import paths

EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def photos() -> list:
    if not paths.PHOTOS_DIR.exists():
        return []
    return sorted(p for p in paths.PHOTOS_DIR.iterdir() if p.suffix.lower() in EXTS)


def _last() -> str:
    try:
        return json.loads(paths.STATE_FILE.read_text()).get("current", "")
    except (OSError, ValueError):
        return ""


def set_wallpaper(path) -> None:
    uri = path.resolve().as_uri()
    schema = "org.gnome.desktop.background"
    subprocess.run(["gsettings", "set", schema, "picture-uri", uri], check=True)
    # GNOME 42+ usa una clave aparte para el modo oscuro.
    subprocess.run(["gsettings", "set", schema, "picture-uri-dark", uri], check=False,
                   stderr=subprocess.DEVNULL)
    subprocess.run(["gsettings", "set", schema, "picture-options", "zoom"], check=True)
    paths.ensure_dirs()
    paths.STATE_FILE.write_text(json.dumps({"current": str(path)}))


def next_random():
    pool = photos()
    if not pool:
        raise SystemExit("No hay fotos descargadas. Ejecuta: wallpaper-google elegir")
    last = _last()
    choices = [p for p in pool if str(p) != last] or pool
    chosen = random.choice(choices)
    set_wallpaper(chosen)
    return chosen
