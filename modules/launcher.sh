# Ulauncher as a Spotlight replacement on Alt+Space.

if ! dpkg -s ulauncher >/dev/null 2>&1; then
    sudo add-apt-repository -y ppa:agornostal/ulauncher
    # Mint's add-apt-repository does not refresh the package lists itself.
    sudo apt-get update
    apt_install ulauncher
fi

# Cinnamon binds Alt+Space to the window menu, which would swallow the hotkey.
gsettings set "$KEYS_SCHEMA.wm" activate-window-menu "[]"

# Cinnamon owns the hotkey rather than Ulauncher, so the toggle module can turn
# it off with the other shortcuts.
set_keybinding custom-cinnamon-apple-launcher "Ulauncher" "ulauncher-toggle" "<Alt>space"

# Ulauncher rewrites its settings file on exit, so stop it before editing.
pkill -f /usr/bin/ulauncher || true

python3 -I - "$HOME/.config/ulauncher/settings.json" <<'EOF'
import json, os, sys
path = sys.argv[1]
settings = {}
if os.path.exists(path):
    with open(path) as f:
        settings = json.load(f)
# Empty, not absent: a missing hotkey makes Ulauncher grab Ctrl+Space.
settings["hotkey-show-app"] = ""
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w") as f:
    json.dump(settings, f, indent=4)
EOF

mkdir -p "$HOME/.config/autostart"
cat >"$HOME/.config/autostart/ulauncher.desktop" <<'EOF'
[Desktop Entry]
Name=Ulauncher
Exec=ulauncher --hide-window
Icon=ulauncher
Type=Application
X-GNOME-Autostart-enabled=true
EOF

setsid ulauncher --hide-window >/dev/null 2>&1 &
