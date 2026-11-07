import os
from pathlib import Path

APP = "wallpaper-google"

CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / APP
CACHE_DIR = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / APP

CONFIG_FILE = CONFIG_DIR / "config.json"
ALBUM_FILE = CACHE_DIR / "album.json"
STATE_FILE = CACHE_DIR / "state.json"


def ensure_dirs() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
