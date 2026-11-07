# WALLPAPER_GOOGLE

Pone de fondo de pantalla una foto al azar de un álbum compartido de Google Fotos,
y la va cambiando cada cierto tiempo. Anda en Linux con GNOME (Pop!_OS 22.04, X11) y en Windows 10/11.

No descarga el álbum entero: guarda solo la lista de fotos y baja **una foto cada vez**,
a la resolución de tu pantalla.

## Cómo funciona

1. Compartís el álbum por enlace (Google Fotos → álbum → Compartir → Crear enlace).
2. La app lee la página pública del álbum y guarda la lista de todas las fotos (se actualiza una vez al día; un álbum de 10.000 fotos tarda unos 30 segundos).
3. Cada X tiempo baja una foto al azar y la pone de fondo (con `gsettings` en GNOME, con la API de Windows en Windows). Sin repetir las últimas.

> No usa la API oficial de Google (desde 2025 ya no permite leer álbumes), así que no hacen
> falta credenciales. Como contrapartida, cualquiera con el enlace puede ver el álbum, y si
> Google cambia su página habrá que ajustar la app.

## Instalar en Linux

No necesita sudo ni dependencias, solo `python3` y `git`.

```bash
git clone https://github.com/manguicho/WALLPAPER_GOOGLE.git ~/WALLPAPER_GOOGLE
~/WALLPAPER_GOOGLE/install.sh
```

## Instalar en Windows

Tampoco necesita ser administrador. Abrí **PowerShell** (tecla Windows → escribí "PowerShell")
y pegá esto. Si ya tenés Python y Git, salteá la primera línea.

```powershell
winget install -e --id Python.Python.3.12; winget install -e --id Git.Git
```

Cerrá PowerShell, abrilo de nuevo (para que encuentre `python` y `git`) y seguí:

```powershell
git clone https://github.com/manguicho/WALLPAPER_GOOGLE.git $HOME\WALLPAPER_GOOGLE
powershell -ExecutionPolicy Bypass -File $HOME\WALLPAPER_GOOGLE\install.ps1
```

Cerrá y abrí PowerShell otra vez, y ya podés usar `wallpaper-google` igual que en Linux
(ver abajo). `wallpaper-google auto 30min` crea una tarea en el **Programador de tareas**
que cambia el fondo al iniciar sesión y cada 30 minutos, sin abrir ventanas.

Si no querés instalar Git, en GitHub tocá **Code → Download ZIP**, descomprimilo en
`%USERPROFILE%\WALLPAPER_GOOGLE` y corré solo la línea del `install.ps1`.

## Usar

```bash
wallpaper-google album https://photos.app.goo.gl/XXXX   # una sola vez
wallpaper-google siguiente      # cambia el fondo ahora
wallpaper-google auto 30min     # cambia solo cada 30 minutos (15min, 1h, 2h...)
wallpaper-google auto-off       # desactiva el cambio automático
wallpaper-google resolucion 2560x1440   # o "auto" para detectarla de la pantalla
wallpaper-google verticales si   # por defecto solo usa fotos horizontales
wallpaper-google estado
```

## Actualizar

```bash
cd ~/WALLPAPER_GOOGLE && git pull          # Linux
cd $HOME\WALLPAPER_GOOGLE; git pull        # Windows (PowerShell)
```

## Archivos

| Qué | Linux | Windows |
|---|---|---|
| Configuración (enlace, resolución) | `~/.config/wallpaper-google/config.json` | `%APPDATA%\wallpaper-google\config.json` |
| Lista de fotos y fondo actual | `~/.cache/wallpaper-google/` | `%LOCALAPPDATA%\wallpaper-google\cache\` |
| Cambio automático | `~/.config/systemd/user/wallpaper-google.{service,timer}` | Programador de tareas → `wallpaper-google` |
