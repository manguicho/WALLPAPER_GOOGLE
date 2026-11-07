"""Lee la lista de fotos de un álbum compartido por enlace de Google Fotos.

No usa la API oficial: lee la página pública del álbum (primer lote de 300) y
pide el resto con el mismo endpoint interno que usa la web (RPC "snAcKc").
Solo se guarda la lista; cada foto se baja cuando toca ponerla de fondo.
"""

import json
import re
import time
import urllib.parse
import urllib.request

from . import paths, store

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
BATCH_URL = "https://photos.google.com/_/PhotosUi/data/batchexecute"
DS1_RE = re.compile(r"AF_initDataCallback\(\{key: 'ds:1',.*?data:(.*?), sideChannel: \{\}\}\);", re.S)
PHOTO_RE = re.compile(
    r'\["(https://lh3\.googleusercontent\.com/pw/[A-Za-z0-9_\-]+)",(\d+),(\d+)'
)
REFRESH_SECONDS = 24 * 3600
MAX_PAGES = 1000


def fetch(url: str, data: bytes = None, timeout: int = 60) -> bytes:
    headers = {"User-Agent": UA, "Accept-Language": "es"}
    if data is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded;charset=UTF-8"
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _items(page) -> list:
    out = []
    for item in page[1] or []:
        try:
            url, w, h = item[1][0], int(item[1][1]), int(item[1][2])
        except (IndexError, TypeError, ValueError):
            continue
        if isinstance(url, str) and url.startswith("https://"):
            out.append([url, w, h])
    return out


def _next_page(album_id: str, token: str, auth_key: str):
    req = json.dumps([[["snAcKc", json.dumps([album_id, token, None, auth_key]), None, "generic"]]])
    body = fetch(BATCH_URL, urllib.parse.urlencode({"f.req": req}).encode()).decode("utf-8", "replace")
    for line in body.splitlines():
        if line.startswith('[["wrb.fr"'):
            return json.loads(json.loads(line)[0][2])
    raise ValueError("respuesta inesperada de Google Fotos")


def scrape(album_url: str, verbose: bool = False) -> list:
    html = fetch(album_url).decode("utf-8", "replace")
    m = DS1_RE.search(html)
    if not m:
        # Si Google cambió la página, al menos usamos lo que se vea en el HTML.
        return [[u, int(w), int(h)] for u, w, h in dict.fromkeys(PHOTO_RE.findall(html))]
    page = json.loads(m.group(1))
    meta = page[3]
    album_id, auth_key = meta[0], meta[19]
    total = meta[21] if len(meta) > 21 and isinstance(meta[21], int) else None
    photos = _items(page)
    token = page[2]
    pages = 1
    while token and pages < MAX_PAGES:
        if verbose:
            print(f"\r  {len(photos)}" + (f"/{total}" if total else "") + " fotos...", end="", flush=True)
        page = _next_page(album_id, token, auth_key)
        photos += _items(page)
        token = page[2]
        pages += 1
    if verbose:
        print()
    seen = set()
    return [p for p in photos if not (p[0] in seen or seen.add(p[0]))]


def refresh(album_url: str, verbose: bool = False) -> list:
    photos = scrape(album_url, verbose)
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
    cached = data.get("photos") if data.get("url") == album_url else None
    if cached and not isinstance(cached[0], list):
        cached = None
    if cached and time.time() - data.get("updated", 0) < REFRESH_SECONDS:
        return cached
    try:
        return refresh(album_url)
    except (OSError, ValueError, SystemExit, IndexError, TypeError):
        if cached:
            return cached
        raise
