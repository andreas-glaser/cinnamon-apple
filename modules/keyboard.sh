# macOS keyboard layout everywhere via Toshy (https://github.com/RedBearAK/toshy).
# On a PC keyboard: Alt acts as Cmd, Win as Option, Ctrl as Ctrl. Alt+C/V/X/Z
# work in every app, including terminals, where Ctrl+C still interrupts.
# Apps matching PC_KEYBOARD_APPS in config.sh, such as games, are left unremapped.

TOSHY_TAG=Toshy_v26.08.0
TOSHY_COMMIT=c39ee06d8d7fa299a082034d75275e6da97e0275
toshy_config="$HOME/.config/toshy/toshy_config.py"

install_toshy() (
    toshy_src=$(mktemp -d)
    trap 'rm -rf "$toshy_src"' EXIT
    git -c advice.detachedHead=false clone --quiet --depth 1 --branch "$TOSHY_TAG" \
        https://github.com/RedBearAK/toshy.git "$toshy_src/toshy"
    toshy_head=$(git -C "$toshy_src/toshy" rev-parse HEAD)
    if [[ $toshy_head != "$TOSHY_COMMIT" ]]; then
        echo "Toshy $TOSHY_TAG resolved to $toshy_head, expected $TOSHY_COMMIT" >&2
        exit 1
    fi
    # Pre-answer the installer's questions the same way Toshy's own bootstrap.sh
    # does; these flags are hidden from --help, hence the pinned release.
    cd "$toshy_src/toshy"
    ./setup_toshy.py install --admin-capable yes --skip-update-check
)

if [[ ! -f $toshy_config ]]; then
    apt_install git
    install_toshy
fi

# The terminal paste override checks the clipboard for images with xclip.
apt_install xclip
read -r -a pc_keyboard_apps <<<"$PC_KEYBOARD_APPS"
python3 -I "$ROOT/files/toshy_apply_config.py" "$toshy_config" "$ROOT/files/toshy_keymap.py" \
    "${pc_keyboard_apps[@]}"
systemctl --user restart toshy-config.service
