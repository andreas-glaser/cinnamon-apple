# Settings for install.sh. An environment variable of the same name overrides
# the value here, e.g. DOCK_POSITION=left ./install.sh dock

# Touchpad scroll direction: true (macOS), false, or empty to leave it alone.
: "${NATURAL_SCROLL=}"

# Where Shift+Alt+3/4 put screenshots: clipboard or file. Adding Ctrl uses the other.
: "${SCREENSHOTS_TO=clipboard}"

# Dock edge: bottom, left or right.
: "${DOCK_POSITION=bottom}"

# Apps that keep the plain PC keyboard: no Alt/Cmd swap and no Mac shortcuts.
# Space-separated regexes matched against the window class, case-insensitive;
# run `xprop WM_CLASS` and click a window to see its class. The defaults cover
# Steam games through Proton, anything running in Wine (Lutris, Heroic,
# Bottles) and gamescope. Add native games here.
: "${PC_KEYBOARD_APPS=steam_app_.* .*\.exe gamescope}"
