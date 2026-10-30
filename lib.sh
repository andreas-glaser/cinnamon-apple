# Shared helpers, sourced by install.sh before running modules.

KEYS_SCHEMA=org.cinnamon.desktop.keybindings
CUSTOM_KEY_SCHEMA=org.cinnamon.desktop.keybindings.custom-keybinding
CUSTOM_KEY_PATH=/org/cinnamon/desktop/keybindings/custom-keybindings

log() {
    printf '\033[1;34m==>\033[0m %s\n' "$*"
}

apt_install() {
    local missing=()
    for pkg in "$@"; do
        dpkg -s "$pkg" >/dev/null 2>&1 || missing+=("$pkg")
    done
    if ((${#missing[@]})); then
        log "Installing ${missing[*]} with apt (needs sudo)"
        sudo apt-get install -y "${missing[@]}"
    fi
}

# Usage: set_keybinding <id> <name> <command> <binding>
# Re-running with the same id updates the shortcut instead of adding a duplicate.
set_keybinding() {
    local id=$1 name=$2 command=$3 binding=$4
    # On reload Cinnamon only unregisters ids containing "custom"; any other id
    # keeps its first command until Cinnamon restarts.
    if [[ $id != *custom* ]]; then
        echo "set_keybinding: id '$id' must contain 'custom'" >&2
        return 1
    fi
    local path="$CUSTOM_KEY_PATH/$id/"
    gsettings set "$CUSTOM_KEY_SCHEMA:$path" name "$name"
    gsettings set "$CUSTOM_KEY_SCHEMA:$path" command "$command"
    gsettings set "$CUSTOM_KEY_SCHEMA:$path" binding "['$binding']"

    # Cinnamon only reloads custom shortcuts when custom-list changes, so the id
    # is taken out and put back even when it is already listed.
    local list
    list=$(gsettings get "$KEYS_SCHEMA" custom-list)
    list=${list//", '$id'"/}
    list=${list//"'$id', "/}
    list=${list//"'$id'"/}
    [[ $list == "[]" ]] && list="@as []"
    gsettings set "$KEYS_SCHEMA" custom-list "$list"
    if [[ $list == "@as []" ]]; then
        list="['$id']"
    else
        list="${list%]}, '$id']"
    fi
    gsettings set "$KEYS_SCHEMA" custom-list "$list"
}
