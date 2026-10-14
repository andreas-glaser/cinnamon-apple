# macOS window shortcuts and title bar buttons on the left.
#   Alt+Q           close window (Alt+F4 still works)
#   Alt+M, Alt+H    minimize
#   Ctrl+Alt+F      toggle fullscreen
#   Ctrl+Alt+Q      lock screen (Ctrl+Alt+L still works)
#   Ctrl+Win+F      fill the screen (maximize toggle)
#   Ctrl+Win+C      center
#   Ctrl+Win+R      return to previous size
#   Ctrl+Win+arrows tile to that half of the screen

gsettings set "$KEYS_SCHEMA.wm" close "['<Alt>F4', '<Alt>q']"
gsettings set "$KEYS_SCHEMA.wm" minimize "['<Alt>m', '<Alt>h']"
gsettings set "$KEYS_SCHEMA.wm" toggle-fullscreen "['<Primary><Alt>f']"
gsettings set "$KEYS_SCHEMA.media-keys" screensaver \
    "['<Primary><Alt>l', 'XF86ScreenSaver', '<Primary><Alt>q']"

# Ctrl+Win stands in for Fn+Ctrl, macOS's window tiling modifier, which a PC
# keyboard cannot send. Without Toshy, Ctrl+Win arrives as Ctrl+Super itself.
gsettings set "$KEYS_SCHEMA.wm" toggle-maximized "['<Alt>F10', '<Primary><Super>f']"
gsettings set "$KEYS_SCHEMA.wm" move-to-center "['<Primary><Super>c']"
gsettings set "$KEYS_SCHEMA.wm" unmaximize "['<Alt>F5', '<Primary><Super>r']"
for direction in Left Right Up Down; do
    gsettings set "$KEYS_SCHEMA.wm" "push-tile-${direction,,}" \
        "['<Super>$direction', '<Primary><Super>$direction']"
done

# The GNOME key covers apps that draw their own title bars.
gsettings set org.cinnamon.desktop.wm.preferences button-layout 'close,minimize,maximize:'
gsettings set org.gnome.desktop.wm.preferences button-layout 'close,minimize,maximize:'
