# macOS window shortcuts and title bar buttons on the left.
#   Alt+Q           close window (Alt+F4 still works)
#   Alt+M, Alt+H    minimize
#   Ctrl+Alt+F      toggle fullscreen
#   Ctrl+Alt+Q      lock screen (Ctrl+Alt+L still works)

gsettings set "$KEYS_SCHEMA.wm" close "['<Alt>F4', '<Alt>q']"
gsettings set "$KEYS_SCHEMA.wm" minimize "['<Alt>m', '<Alt>h']"
gsettings set "$KEYS_SCHEMA.wm" toggle-fullscreen "['<Primary><Alt>f']"
gsettings set "$KEYS_SCHEMA.media-keys" screensaver \
    "['<Primary><Alt>l', 'XF86ScreenSaver', '<Primary><Alt>q']"

# The GNOME key covers apps that draw their own title bars.
gsettings set org.cinnamon.desktop.wm.preferences button-layout 'close,minimize,maximize:'
gsettings set org.gnome.desktop.wm.preferences button-layout 'close,minimize,maximize:'
