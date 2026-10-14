"""Add the light and dark profiles to a Terminator config and enable the plugin.

Usage: terminator_profiles.py CONFIG

Only the colours of the two profiles are managed. A profile that does not
exist yet starts as a copy of "default", so font, scrollback and the like carry
over, and later changes to anything but the colours are kept.
"""
import os
import sys
import tempfile

from configobj import ConfigObj

PLUGIN = "CinnamonAppleAppearance"
# Terminator's built-in list, which applies while the config does not set one.
DEFAULT_PLUGINS = ["LaunchpadBugURLHandler", "LaunchpadCodeURLHandler", "APTURLHandler"]

COLOURS = {
    # GitHub Light
    "light": {
        "background_color": "#fafaf8",
        "foreground_color": "#1f2328",
        "cursor_color_default": "False",
        "cursor_bg_color": "#0969da",
        "cursor_fg_color": "#fafaf8",
        "palette": "#24292f:#c4202b:#116329:#8a5a00:#0550ae:#8250df:#0e6f78:#6e7781:"
                   "#57606a:#a40e26:#1a7f37:#7d4e00:#0969da:#6639ba:#1b7c83:#8c959f",
    },
    # One Dark
    "dark": {
        "background_color": "#1e2228",
        "foreground_color": "#d7dae0",
        "cursor_color_default": "False",
        "cursor_bg_color": "#61afef",
        "cursor_fg_color": "#1e2228",
        "palette": "#3a3f4b:#e06c75:#98c379:#e5c07b:#61afef:#c678dd:#56b6c2:#abb2bf:"
                   "#5c6370:#f08a93:#b0d68f:#f0d090:#80c0f5:#d8a0ea:#70ccd6:#eef0f4",
    },
}


def main(path):
    config = ConfigObj(path, encoding="utf-8")

    profiles = config.setdefault("profiles", {})
    for name, colours in COLOURS.items():
        if name not in profiles:
            profiles[name] = dict(profiles.get("default", {}))
        profiles[name].update(colours)

    global_config = config.setdefault("global_config", {})
    plugins = global_config.get("enabled_plugins", DEFAULT_PLUGINS)
    if isinstance(plugins, str):
        plugins = [plugins]
    if PLUGIN not in plugins:
        global_config["enabled_plugins"] = list(plugins) + [PLUGIN]

    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=directory, prefix=".config.")
    os.close(fd)
    try:
        config.filename = tmp_path
        config.write()
        if os.path.exists(path):
            os.chmod(tmp_path, os.stat(path).st_mode & 0o777)
        os.replace(tmp_path, path)
    except BaseException:
        os.unlink(tmp_path)
        raise


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__.splitlines()[2])
    main(sys.argv[1])
