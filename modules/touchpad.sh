# Tap to click and macOS-style three-finger gestures.
#   3 fingers up      overview of all workspaces (Mission Control)
#   3 fingers down    windows on this workspace (App Expose)
#   3 fingers left    next workspace
#   3 fingers right   previous workspace
# Scroll direction is left alone unless NATURAL_SCROLL in config.sh is set.

touchpad=org.cinnamon.desktop.peripherals.touchpad
gsettings set "$touchpad" tap-to-click true

if [[ -n $NATURAL_SCROLL ]]; then
    if [[ $NATURAL_SCROLL != true && $NATURAL_SCROLL != false ]]; then
        echo "NATURAL_SCROLL must be 'true' or 'false', got '$NATURAL_SCROLL'" >&2
        exit 1
    fi
    gsettings set "$touchpad" natural-scroll "$NATURAL_SCROLL"
fi

apt_install touchegg

gestures=org.cinnamon.gestures
gsettings set "$gestures" enabled true
gsettings set "$gestures" swipe-up-3 'TOGGLE_EXPO::end'
gsettings set "$gestures" swipe-down-3 'TOGGLE_OVERVIEW::end'
gsettings set "$gestures" swipe-left-3 'WORKSPACE_NEXT::end'
gsettings set "$gestures" swipe-right-3 'WORKSPACE_PREVIOUS::end'
# Cinnamon's default two-finger swipes tile windows, which fires when
# scrolling sideways the way you would on a Mac.
for direction in up down left right; do
    gsettings set "$gestures" "swipe-$direction-2" ''
done
