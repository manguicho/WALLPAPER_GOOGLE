# WALLPAPER_GOOGLE

Pone de fondo de pantalla, al azar, una foto elegida de tu Google Fotos.
Pensado para Linux con GNOME (probado para Pop!_OS 22.04, X11).

## Cómo funciona

Desde marzo de 2025 Google ya no deja que una app lea un álbum entero por su cuenta.
Lo que sí permite es abrir la ventana oficial de Google Fotos (Photos Picker), donde
**tú** entras al álbum y seleccionas las fotos. La app las descarga a
`~/.local/share/wallpaper-google/photos/` y rota el fondo desde ahí.
Cuando quieras cambiar de selección, vuelves a ejecutar `wallpaper-google elegir`.

## 1. Crear las credenciales de Google (una sola vez, unos 5 minutos)

1. Entra a <https://console.cloud.google.com/> y crea un proyecto nuevo (por ejemplo, `wallpaper`).
2. En **APIs y servicios → Biblioteca**, busca **Google Photos Picker API** y pulsa **Habilitar**.
3. En **Google Auth Platform → Branding** (pantalla de consentimiento), configúrala como
   **Externa** con tu correo. En **Público/Audience**, añade tu correo como **usuario de prueba**.
4. En **Google Auth Platform → Clientes**, crea un cliente OAuth de tipo **App de escritorio**
   y descarga el JSON.
5. Guárdalo así:

   ```bash
   mkdir -p ~/.config/wallpaper-google
   mv ~/Descargas/client_secret_*.json ~/.config/wallpaper-google/client_secret.json
   ```

> Mientras la app esté en modo "Prueba", Google caduca el login cada 7 días. Esto solo
> afecta a `elegir`: el cambio de fondo usa las fotos ya descargadas y sigue funcionando.
> Si quieres evitarlo, en **Público/Audience** pulsa **Publicar app** (verás un aviso de
> "app no verificada" al iniciar sesión; es normal porque la app es tuya).

## 2. Instalar

```bash
sudo apt install -y pipx git
pipx ensurepath
git clone https://github.com/manguicho/WALLPAPER_GOOGLE.git
pipx install ./WALLPAPER_GOOGLE
```

(Abre una terminal nueva después de `pipx ensurepath`.)

## 3. Usar

```bash
wallpaper-google elegir        # abre Google Fotos: entra al álbum y selecciona las fotos
wallpaper-google siguiente     # pone otra foto al azar ahora mismo
wallpaper-google auto 30min    # cambia el fondo solo cada 30 minutos (15min, 1h, 2h...)
wallpaper-google auto-off      # desactiva el cambio automático
wallpaper-google estado        # cuántas fotos hay y si falta algo
```

`elegir --reemplazar` borra la selección anterior antes de descargar la nueva. Sin esa
opción, las fotos nuevas se suman a las que ya tenías.

En el Picker se pueden elegir como máximo 2000 fotos por vez.

## Actualizar

```bash
cd WALLPAPER_GOOGLE && git pull && pipx install --force .
```

## Archivos

| Qué | Dónde |
|---|---|
| Credenciales y login | `~/.config/wallpaper-google/` |
| Fotos descargadas | `~/.local/share/wallpaper-google/photos/` |
| Temporizador | `~/.config/systemd/user/wallpaper-google.{service,timer}` |
