# Ctrl+Alt+Win+D switches the desktop between dark and light mode, keeping the
# colour picked in Themes. Executables in ~/.config/cinnamon-apple/appearance.d
# run afterwards with "dark" or "light", e.g. to switch the terminal along.

apt_install libnotify-bin python3-gi

appearance="$HOME/.local/bin/cinnamon-apple-appearance"
install -D -m 0755 "$ROOT/files/cinnamon-apple-appearance" "$appearance"
mkdir -p "${XDG_CONFIG_HOME:-$HOME/.config}/cinnamon-apple/appearance.d"

set_keybinding custom-cinnamon-apple-appearance "Toggle dark mode" "$appearance" "<Primary><Alt><Super>d"
