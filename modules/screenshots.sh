# Flameshot with macOS-style shortcuts (Alt stands in for Cmd).
#   Shift+Alt+3        full screen
#   Shift+Alt+4        region
#   Ctrl+Shift+Alt+3   full screen, the other destination
#   Ctrl+Shift+Alt+4   region, the other destination
#   Shift+Alt+5        region with annotation tools
# SCREENSHOTS_TO in config.sh picks where Shift+Alt+3/4 go; adding Ctrl sends
# to the other destination.

screenshot_dir="$(xdg-user-dir PICTURES)/Screenshots"
case $SCREENSHOTS_TO in
    clipboard) main_target="-c";                     alt_target="-p \"$screenshot_dir\"" ;;
    file)      main_target="-p \"$screenshot_dir\""; alt_target="-c" ;;
    *)
        echo "SCREENSHOTS_TO must be 'clipboard' or 'file', got '$SCREENSHOTS_TO'" >&2
        exit 1
        ;;
esac

apt_install flameshot
mkdir -p "$screenshot_dir"

set_keybinding custom-cinnamon-apple-shot-full "Screenshot: full screen" \
    "flameshot full $main_target" "<Shift><Alt>3"
set_keybinding custom-cinnamon-apple-shot-region "Screenshot: region" \
    "flameshot gui -s $main_target" "<Shift><Alt>4"
set_keybinding custom-cinnamon-apple-shot-full-ctrl "Screenshot: full screen (other destination)" \
    "flameshot full $alt_target" "<Primary><Shift><Alt>3"
set_keybinding custom-cinnamon-apple-shot-region-ctrl "Screenshot: region (other destination)" \
    "flameshot gui -s $alt_target" "<Primary><Shift><Alt>4"
set_keybinding custom-cinnamon-apple-shot-annotate "Screenshot: region with annotation" \
    "flameshot gui" "<Shift><Alt>5"
