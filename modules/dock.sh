# macOS layout: Plank Reloaded as the dock (edge set by DOCK_POSITION in
# config.sh), Cinnamon's panel at the top as the menu bar. The panel's window
# list, launchers and separators are removed, since the dock does that job. The
# original panel layout is saved once to
# ~/.local/state/cinnamon-apple/panel-backup.sh; run it with bash to restore.
# Plank Reloaded comes from its author's apt repository, whose signing key is
# checked against a pinned fingerprint.

PLANK_REPO=https://zquestz.github.io/ppa/ubuntu
PLANK_KEY_FINGERPRINT=B6DE3514E07E30BB5F408D74E49B7E0000228DDD
plank_keyring=/etc/apt/keyrings/zquestz.gpg

add_plank_repo() (
    tmp=$(mktemp -d)
    trap 'rm -rf "$tmp"' EXIT
    curl -fsSL --max-time 30 -o "$tmp/key.asc" "$PLANK_REPO/KEY.gpg"
    keys=$(gpg --quiet --homedir "$tmp" --show-keys --with-colons "$tmp/key.asc")
    primary_keys=$(grep -c '^pub:' <<<"$keys")
    fingerprint=$(awk -F: '/^fpr:/ { print $10; exit }' <<<"$keys")
    if [[ $primary_keys != 1 || $fingerprint != "$PLANK_KEY_FINGERPRINT" ]]; then
        echo "Plank Reloaded signing key does not match $PLANK_KEY_FINGERPRINT" >&2
        exit 1
    fi
    gpg --quiet --homedir "$tmp" --dearmor -o "$tmp/key.gpg" "$tmp/key.asc"
    sudo install -D -m 0644 "$tmp/key.gpg" "$plank_keyring"
    echo "deb [signed-by=$plank_keyring] $PLANK_REPO ./" |
        sudo tee /etc/apt/sources.list.d/zquestz.list >/dev/null
    sudo apt-get update
)

if ! dpkg -s plank-reloaded >/dev/null 2>&1; then
    add_plank_repo
    apt_install plank-reloaded
fi
apt_install python3-gi

case $DOCK_POSITION in
    bottom | left | right) ;;
    *)
        echo "DOCK_POSITION must be 'bottom', 'left' or 'right', got '$DOCK_POSITION'" >&2
        exit 1
        ;;
esac

dock_schema=net.launchpad.plank.dock.settings:/net/launchpad/plank/docks/dock1/
gsettings set "$dock_schema" position "$DOCK_POSITION"
gsettings set "$dock_schema" hide-mode intelligent
gsettings set "$dock_schema" zoom-enabled true
gsettings set "$dock_schema" zoom-percent 150

mkdir -p "$HOME/.config/autostart"
cat >"$HOME/.config/autostart/plank.desktop" <<'EOF'
[Desktop Entry]
Name=Plank
Exec=plank
Icon=plank
Type=Application
X-GNOME-Autostart-enabled=true
EOF
pgrep -x plank >/dev/null || setsid plank >/dev/null 2>&1 &

panel_backup="${XDG_STATE_HOME:-$HOME/.local/state}/cinnamon-apple/panel-backup.sh"
if [[ ! -f $panel_backup ]]; then
    mkdir -p "$(dirname "$panel_backup")"
    for key in panels-enabled panels-height panels-autohide enabled-applets; do
        printf 'gsettings set org.cinnamon %s %q\n' "$key" "$(gsettings get org.cinnamon "$key")"
    done >"$panel_backup"
    log "Saved the original panel layout to $panel_backup"
fi

# System Python: a virtualenv earlier on PATH would not have the GLib bindings.
/usr/bin/python3 -I - <<'EOF'
from gi.repository import Gio

REPLACED_BY_DOCK = {
    "window-list@cinnamon.org",
    "grouped-window-list@cinnamon.org",
    "panel-launchers@cinnamon.org",
    "separator@cinnamon.org",
}

settings = Gio.Settings.new("org.cinnamon")

panels = settings.get_strv("panels-enabled")
top_monitors = {p.split(":")[1] for p in panels if p.endswith(":top")}
moved = []
for panel in panels:
    panel_id, monitor, position = panel.split(":")
    if position == "bottom" and monitor not in top_monitors:
        position = "top"
        top_monitors.add(monitor)
    moved.append(f"{panel_id}:{monitor}:{position}")

applets = settings.get_strv("enabled-applets")
kept = [a for a in applets if a.split(":")[3] not in REPLACED_BY_DOCK]

settings.set_strv("panels-enabled", moved)
settings.set_strv("enabled-applets", kept)
Gio.Settings.sync()
EOF
