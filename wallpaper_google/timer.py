"""Temporizador de systemd (usuario) para cambiar el fondo automáticamente."""

import shutil
import subprocess
import sys
from pathlib import Path

UNIT_DIR = Path.home() / ".config" / "systemd" / "user"
NAME = "wallpaper-google"


def install(every: str) -> None:
    exe = shutil.which("wallpaper-google") or f"{sys.executable} -m wallpaper_google"
    UNIT_DIR.mkdir(parents=True, exist_ok=True)
    (UNIT_DIR / f"{NAME}.service").write_text(
        "[Unit]\nDescription=Cambia el fondo de pantalla con una foto de Google Fotos\n\n"
        f"[Service]\nType=oneshot\nExecStart={exe} siguiente\n"
    )
    (UNIT_DIR / f"{NAME}.timer").write_text(
        "[Unit]\nDescription=Cambio periódico de fondo de pantalla\n\n"
        f"[Timer]\nOnStartupSec=1min\nOnUnitActiveSec={every}\nUnit={NAME}.service\n\n"
        "[Install]\nWantedBy=timers.target\n"
    )
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "--user", "enable", "--now", f"{NAME}.timer"], check=True)
    subprocess.run(["systemctl", "--user", "restart", f"{NAME}.timer"], check=True)
    print(f"Listo: el fondo cambiará cada {every}.")


def uninstall() -> None:
    subprocess.run(["systemctl", "--user", "disable", "--now", f"{NAME}.timer"], check=False)
    for ext in ("service", "timer"):
        (UNIT_DIR / f"{NAME}.{ext}").unlink(missing_ok=True)
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
    print("Cambio automático desactivado.")
