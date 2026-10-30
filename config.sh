# Settings for install.sh. An environment variable of the same name overrides
# the value here, e.g. DOCK_POSITION=left ./install.sh dock

# Touchpad scroll direction: true (macOS), false, or empty to leave it alone.
: "${NATURAL_SCROLL=}"

# Where Shift+Alt+3/4 put screenshots: clipboard or file. Adding Ctrl uses the other.
: "${SCREENSHOTS_TO=clipboard}"

# Dock edge: bottom, left or right.
: "${DOCK_POSITION=bottom}"

