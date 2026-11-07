#!/bin/sh
# Instala el comando wallpaper-google en ~/.local/bin (sin sudo ni dependencias).
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/wallpaper-google" <<SH
#!/bin/sh
PYTHONPATH="$DIR" exec python3 -m wallpaper_google "\$@"
SH
chmod +x "$HOME/.local/bin/wallpaper-google"
echo "Instalado en ~/.local/bin/wallpaper-google"
