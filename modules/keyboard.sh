# macOS editing shortcuts in apps, with Alt standing in for Cmd:
#   Alt+C/V/X       copy, paste, cut
#   Alt+Z           undo (Shift+Alt+Z redo)
#   Alt+A/F         select all, find
#   Alt+T/W         new tab, close tab
#   Alt+R           reload
# Each is a Cinnamon shortcut that sends the Ctrl version with xdotool, or the
# Ctrl+Shift version in terminals. Nothing reads the keyboard in between.

apt_install xdotool xclip x11-utils libnotify-bin

key="$HOME/.local/bin/cinnamon-apple-key"
install -D -m 0755 "$ROOT/files/cinnamon-apple-key" "$key"

for letter in c v x z a f t w r; do
    set_keybinding "custom-cinnamon-apple-key-$letter" "Mac shortcut: Alt+${letter^^}" \
        "$key $letter" "<Alt>$letter"
done
set_keybinding custom-cinnamon-apple-key-shift-z "Mac shortcut: Shift+Alt+Z" \
    "$key shift+z" "<Shift><Alt>z"
