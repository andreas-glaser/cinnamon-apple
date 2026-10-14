"""Terminator plugin from cinnamon-apple: follow the desktop's Dark mode.

When Dark mode in System Settings > Themes changes, open terminals on the
light, dark or default profile switch to the matching one, and new windows
open with it. Mixed mode counts as light, since it leaves apps light.
"""
from gi.repository import Gio

from terminatorlib import plugin
from terminatorlib.config import Config
from terminatorlib.terminator import Terminator
from terminatorlib.util import err

AVAILABLE = ["CinnamonAppleAppearance"]

SCHEMA = "org.x.apps.portal"
FOLLOWING = {"default", "light", "dark"}


def profile_for(color_scheme):
    return "dark" if color_scheme == "prefer-dark" else "light"


class CinnamonAppleAppearance(plugin.Plugin):
    capabilities = []

    def __init__(self):
        plugin.Plugin.__init__(self)
        self.settings = None
        # Gio aborts the whole process on a missing schema.
        if Gio.SettingsSchemaSource.get_default().lookup(SCHEMA, True) is None:
            err(f"cinnamon-apple: no {SCHEMA} schema, not following Dark mode")
            return
        self.settings = Gio.Settings.new(SCHEMA)
        self.handler = self.settings.connect("changed::color-scheme", self.apply)
        self.apply()

    def unload(self):
        if self.settings is not None:
            self.settings.disconnect(self.handler)

    def apply(self, *_args):
        profile = profile_for(self.settings.get_string("color-scheme"))
        config = Config()
        if profile not in config.list_profiles():
            err(f"cinnamon-apple: no {profile} profile; run ./install.sh terminal")
            return

        # New windows, including ones another `terminator` call asks for over
        # D-Bus, are built from the default layout held in memory.
        layout = config.layout_get_config("default") or {}
        for child in layout.values():
            if child.get("type") == "Terminal":
                child["profile"] = profile

        for terminal in Terminator().terminals:
            if terminal.get_profile() in FOLLOWING:
                terminal.force_set_profile(None, profile)
