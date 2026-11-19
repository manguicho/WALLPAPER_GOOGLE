"""Soporte de Windows: poner el fondo, detectar la pantalla y el cambio automático.

El fondo se pone con la API de Windows (SystemParametersInfoW) y el cambio
automático es una tarea del Programador de tareas que corre al iniciar sesión
y cada X minutos. No hace falta ser administrador.
"""

import ctypes
import os
import re
import subprocess
import sys
import tempfile
import winreg
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

TASK = "wallpaper-google"
SPI_SETDESKWALLPAPER = 0x14
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02


def screen_resolution() -> tuple:
    user32 = ctypes.windll.user32
    try:
        # Sin esto, con escalado (125%, 150%...) Windows devuelve una resolución menor.
        user32.SetProcessDPIAware()
    except (AttributeError, OSError):
        pass
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


def set_wallpaper(path) -> None:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0,
                        winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, "10")  # Rellenar
        winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, "0")
    ok = ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER, 0, str(Path(path).resolve()),
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
    if not ok:
        raise ctypes.WinError()


def minutes(every: str) -> int:
    """'30min', '1h', '2h', '45', '1d' -> minutos."""
    m = re.fullmatch(r"\s*(\d+)\s*([a-z]*)\s*", every.lower())
    units = {"": 1, "m": 1, "min": 1, "mins": 1, "minutos": 1, "h": 60, "hr": 60,
             "hora": 60, "horas": 60, "hour": 60, "hours": 60, "d": 1440, "dia": 1440,
             "dias": 1440, "day": 1440, "days": 1440, "s": 1 / 60, "sec": 1 / 60}
    if not m or m[2] not in units:
        raise SystemExit(f"No entiendo el intervalo '{every}'. Usá por ejemplo 15min, 30min, 1h o 2h.")
    return max(1, round(int(m[1]) * units[m[2]]))


def _pythonw() -> str:
    # pythonw.exe es igual que python.exe pero sin abrir una ventana negra.
    exe = Path(sys.executable)
    w = exe.with_name("pythonw.exe")
    return str(w if w.exists() else exe)


def task_xml(every_min: int, user: str, with_logon: bool = True) -> str:
    workdir = Path(__file__).resolve().parent.parent
    start = datetime.now().replace(second=0, microsecond=0).isoformat()
    logon = (f"<LogonTrigger><Enabled>true</Enabled><UserId>{escape(user)}</UserId>"
             "<Delay>PT1M</Delay></LogonTrigger>") if with_logon else ""
    return f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo><Description>Cambia el fondo de pantalla con una foto de Google Fotos</Description></RegistrationInfo>
  <Triggers>
    {logon}
    <TimeTrigger>
      <StartBoundary>{start}</StartBoundary>
      <Enabled>true</Enabled>
      <Repetition><Interval>PT{every_min}M</Interval><StopAtDurationEnd>false</StopAtDurationEnd></Repetition>
    </TimeTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>{escape(user)}</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <StartWhenAvailable>true</StartWhenAvailable>
    <ExecutionTimeLimit>PT10M</ExecutionTimeLimit>
    <Enabled>true</Enabled>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{escape(_pythonw())}</Command>
      <Arguments>-m wallpaper_google siguiente</Arguments>
      <WorkingDirectory>{escape(str(workdir))}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"""


def _schtasks(*args, check=True):
    return subprocess.run(["schtasks", *args], capture_output=True, text=True, check=check)


def _register(xml: str):
    fd, tmp = tempfile.mkstemp(suffix=".xml")
    os.close(fd)
    try:
        Path(tmp).write_text(xml, encoding="utf-16")
        return _schtasks("/Create", "/TN", TASK, "/XML", tmp, "/F", check=False)
    finally:
        os.unlink(tmp)


def install(every: str) -> None:
    n = minutes(every)
    user = f"{os.environ.get('USERDOMAIN', '')}\\{os.environ['USERNAME']}".lstrip("\\")
    r = _register(task_xml(n, user))
    logon = True
    if r.returncode != 0:
        # Algunas PCs no dejan crear el disparador "al iniciar sesión" sin ser administrador.
        logon = False
        r = _register(task_xml(n, user, with_logon=False))
    if r.returncode != 0:
        raise SystemExit("No pude crear la tarea programada:\n" + (r.stderr or r.stdout))
    _schtasks("/Run", "/TN", TASK, check=False)
    print(f"Listo: el fondo cambiará cada {every}"
          + (" y al iniciar sesión." if logon else "."))


def uninstall() -> None:
    _schtasks("/Delete", "/TN", TASK, "/F", check=False)
    print("Cambio automático desactivado.")
