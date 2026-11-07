"""Baja una foto al azar del álbum y la pone de fondo en GNOME."""

import random
import re
import subprocess

from . import album, paths, store

DEFAULT_RES = (1920, 1080)
HISTORY = 50  # no repetir las últimas N fotos (si el álbum es más grande)


def screen_resolution() -> tuple:
    try:
        out = subprocess.run(["xrandr", "--current"], capture_output=True, text=True,
                             timeout=5).stdout
    except (OSError, subprocess.SubprocessError):
        return DEFAULT_RES
    sizes = [(int(w), int(h)) for w, h in re.findall(r" connected.*? (\d+)x(\d+)\+", out)]
    return max(sizes, key=lambda s: s[0] * s[1]) if sizes else DEFAULT_RES


def set_wallpaper(path) -> None:
    uri = path.resolve().as_uri()
    schema = "org.gnome.desktop.background"
    subprocess.run(["gsettings", "set", schema, "picture-uri", uri], check=True)
    # GNOME 42+ usa una clave aparte para el modo oscuro.
    subprocess.run(["gsettings", "set", schema, "picture-uri-dark", uri], check=False,
                   stderr=subprocess.DEVNULL)
    subprocess.run(["gsettings", "set", schema, "picture-options", "zoom"], check=True)


def next_random() -> str:
    cfg = store.load(paths.CONFIG_FILE)
    url = cfg.get("album")
    if not url:
        raise SystemExit("No hay álbum configurado. Ejecuta: wallpaper-google album <enlace>")
    pool = album.photos(url)
    if not cfg.get("verticales"):
        pool = [p for p in pool if p[1] >= p[2]] or pool
    pool = [p[0] for p in pool]
    state = store.load(paths.STATE_FILE)
    recent = state.get("recent", [])
    keep = min(HISTORY, len(pool) // 2)
    recent = recent[-keep:] if keep else []
    choices = [p for p in pool if p not in recent] or pool
    chosen = random.choice(choices)

    w, h = cfg.get("resolucion") or screen_resolution()
    data = album.fetch(f"{chosen}=w{w}-h{h}")
    paths.ensure_dirs()
    # Nombre distinto cada vez: GNOME no recarga la imagen si la ruta no cambia.
    n = state.get("n", 0) + 1
    dest = paths.CACHE_DIR / f"fondo-{n % 2}.jpg"
    dest.write_bytes(data)
    set_wallpaper(dest)

    recent.append(chosen)
    store.save(paths.STATE_FILE, {"n": n, "recent": recent, "current": chosen})
    return chosen
