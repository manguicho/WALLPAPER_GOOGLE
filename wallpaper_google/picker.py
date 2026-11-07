"""Google Photos Picker API: elegir fotos y descargarlas a disco.

Desde 2025 Google no deja a las apps leer álbumes completos; el usuario elige
las fotos en la ventana del Picker (puede entrar a un álbum y seleccionarlas
todas). Las guardamos en local y rotamos desde ahí.
"""

import hashlib
import time
import webbrowser

from . import paths

API = "https://photospicker.googleapis.com/v1"
MAX_W, MAX_H = 3840, 2160


def _duration(value: str, default: float) -> float:
    try:
        return float(value.rstrip("s"))
    except (AttributeError, ValueError):
        return default


def pick(sess) -> list:
    r = sess.post(f"{API}/sessions", json={})
    r.raise_for_status()
    picker = r.json()
    sid = picker["id"]
    url = picker["pickerUri"].rstrip("/") + "/autoclose"
    print("Abre este enlace y elige las fotos (puedes entrar a un álbum y seleccionarlas todas):")
    print(url)
    webbrowser.open(url)

    poll = picker.get("pollingConfig", {})
    interval = _duration(poll.get("pollInterval"), 5)
    deadline = time.time() + _duration(poll.get("timeoutIn"), 1800)
    try:
        while time.time() < deadline:
            time.sleep(interval)
            s = sess.get(f"{API}/sessions/{sid}")
            s.raise_for_status()
            if s.json().get("mediaItemsSet"):
                break
            print(".", end="", flush=True)
        else:
            raise SystemExit("\nSe acabó el tiempo para elegir fotos.")
        print()
        return _list_items(sess, sid)
    except BaseException:
        sess.delete(f"{API}/sessions/{sid}")
        raise


def _list_items(sess, sid: str) -> list:
    items, token = [], None
    while True:
        params = {"sessionId": sid, "pageSize": 100}
        if token:
            params["pageToken"] = token
        r = sess.get(f"{API}/mediaItems", params=params)
        r.raise_for_status()
        data = r.json()
        items += data.get("mediaItems", [])
        token = data.get("nextPageToken")
        if not token:
            break
    # Las URLs de descarga duran 60 min, así que descargamos antes de cerrar la sesión.
    return [(sid, i) for i in items]


def download(sess, picked: list) -> int:
    paths.ensure_dirs()
    count = 0
    sids = set()
    for sid, item in picked:
        sids.add(sid)
        if item.get("type") != "PHOTO":
            continue
        media = item["mediaFile"]
        ext = {"image/png": ".png", "image/webp": ".webp"}.get(media.get("mimeType"), ".jpg")
        name = hashlib.sha1(item["id"].encode()).hexdigest()[:16] + ext
        dest = paths.PHOTOS_DIR / name
        if dest.exists():
            count += 1
            continue
        r = sess.get(f"{media['baseUrl']}=w{MAX_W}-h{MAX_H}", timeout=120)
        r.raise_for_status()
        tmp = dest.with_suffix(dest.suffix + ".part")
        tmp.write_bytes(r.content)
        tmp.rename(dest)
        count += 1
        print(f"  {count}: {media.get('filename', name)}")
    for sid in sids:
        sess.delete(f"{API}/sessions/{sid}")
    return count
