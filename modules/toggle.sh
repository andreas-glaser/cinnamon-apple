# Ctrl+Alt+Win+M switches between the Mac keyboard and stock Cinnamon, for
# games and other apps that need the plain Alt shortcuts. Off resets every
# shortcut the other modules set to Cinnamon's default; on puts them back. Off
# lasts until you switch back or log in again.

apt_install libnotify-bin python3-gi

toggle="$HOME/.local/bin/cinnamon-apple-toggle"
install -D -m 0755 "$ROOT/files/cinnamon-apple-toggle" "$toggle"

set_keybinding custom-cinnamon-apple-toggle "Toggle Mac keyboard" "$toggle" "<Primary><Alt><Super>m"

mkdir -p "$HOME/.config/autostart"
cat >"$HOME/.config/autostart/cinnamon-apple-toggle.desktop" <<DESKTOP
[Desktop Entry]
Name=Mac keyboard on at login
Exec=$toggle on
Type=Application
NoDisplay=true
X-GNOME-Autostart-enabled=true
DESKTOP
