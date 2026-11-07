"""Lee la lista de fotos de un álbum compartido por enlace de Google Fotos.

No usa la API oficial: descarga la página pública del álbum y saca de ahí las
URLs de las fotos (lh3.googleusercontent.com). Solo se guarda la lista; cada
foto se baja cuando toca ponerla de fondo.
"""

import re
import time
import urllib.request

from . import paths, store

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
PHOTO_RE = re.compile(
    r'\["(https://lh3\.googleusercontent\.com/pw/[A-Za-z0-9_\-]+)",(\d+),(\d+)'
)
REFRESH_SECONDS = 24 * 3600


def fetch(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "es"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def scrape(album_url: str) -> list:
    html = fetch(album_url).decode("utf-8", "replace")
    seen, photos = set(), []
    for u, w, h in PHOTO_RE.findall(html):
        if u not in seen:
            seen.add(u)
            photos.append([u, int(w), int(h)])
    return photos


def refresh(album_url: str) -> list:
    photos = scrape(album_url)
    if not photos:
        raise SystemExit(
            "No encontré fotos en ese enlace. ¿Es un álbum compartido por enlace "
            "(photos.app.goo.gl/... o photos.google.com/share/...)?"
        )
    store.save(paths.ALBUM_FILE, {"url": album_url, "updated": time.time(), "photos": photos})
    return photos


def photos(album_url: str) -> list:
    """Lista de [url, ancho, alto], refrescándola si tiene más de un día (y si hay red)."""
    data = store.load(paths.ALBUM_FILE)
    fresh = data.get("url") == album_url and time.time() - data.get("updated", 0) < REFRESH_SECONDS
    if fresh and data.get("photos") and isinstance(data["photos"][0], list):
        return data["photos"]
    try:
        return refresh(album_url)
    except (OSError, SystemExit):
        if data.get("url") == album_url and data.get("photos"):
            return data["photos"]
        raise
