# WALLPAPER_GOOGLE

Pone de fondo de pantalla una foto al azar de un álbum compartido de Google Fotos,
y la va cambiando cada cierto tiempo. Pensado para Linux con GNOME (Pop!_OS 22.04, X11).

No descarga el álbum entero: guarda solo la lista de fotos y baja **una foto cada vez**,
a la resolución de tu pantalla.

## Cómo funciona

1. Compartes el álbum por enlace (Google Fotos → álbum → Compartir → Crear enlace).
2. La app lee la página pública del álbum y guarda la lista de fotos (se actualiza una vez al día).
3. Cada X tiempo baja una foto al azar y la pone de fondo con `gsettings`. Sin repetir las últimas.

> No usa la API oficial de Google (desde 2025 ya no permite leer álbumes), así que no hacen
> falta credenciales. Como contrapartida, cualquiera con el enlace puede ver el álbum, y si
> Google cambia su página habrá que ajustar la app.

## Instalar

No necesita sudo ni dependencias, solo `python3` y `git`.

```bash
git clone https://github.com/manguicho/WALLPAPER_GOOGLE.git ~/WALLPAPER_GOOGLE
~/WALLPAPER_GOOGLE/install.sh
```

## Usar

```bash
wallpaper-google album https://photos.app.goo.gl/XXXX   # una sola vez
wallpaper-google siguiente      # cambia el fondo ahora
wallpaper-google auto 30min     # cambia solo cada 30 minutos (15min, 1h, 2h...)
wallpaper-google auto-off       # desactiva el cambio automático
wallpaper-google resolucion 2560x1440   # o "auto" para detectarla con xrandr
wallpaper-google verticales si   # por defecto solo usa fotos horizontales
wallpaper-google estado
```

## Actualizar

```bash
cd ~/WALLPAPER_GOOGLE && git pull
```

## Archivos

| Qué | Dónde |
|---|---|
| Configuración (enlace, resolución) | `~/.config/wallpaper-google/config.json` |
| Lista de fotos y fondo actual | `~/.cache/wallpaper-google/` |
| Temporizador | `~/.config/systemd/user/wallpaper-google.{service,timer}` |
