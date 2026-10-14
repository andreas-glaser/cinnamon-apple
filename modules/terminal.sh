# Terminator with "light" and "dark" profiles that follow the desktop: Dark
# mode in System Settings > Themes switches every open terminal and picks the
# profile for new windows. Claude Code (theme "auto") and Codex take their
# colours from the terminal, so they follow too.

apt_install terminator

install -D -m 0644 "$ROOT/files/terminator_appearance.py" \
    "$HOME/.config/terminator/plugins/cinnamon_apple_appearance.py"
# System Python: Terminator's configobj is not in a virtualenv earlier on PATH.
/usr/bin/python3 -I "$ROOT/files/terminator_profiles.py" "$HOME/.config/terminator/config"

# Terminator reads its config and plugins only at start, and saving its
# preferences would write back the copy it loaded.
if pgrep -f '^/usr/bin/python3 /usr/bin/terminator( |$)' >/dev/null; then
    log "Close every Terminator window to load the light and dark profiles"
fi
