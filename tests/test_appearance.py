import json
import os
import subprocess
import tempfile
import unittest

APPEARANCE = os.path.join(os.path.dirname(__file__), "..", "files", "cinnamon-apple-appearance")
INTERFACE = "org.cinnamon.desktop.interface"
CINNAMON_THEME = "org.cinnamon.theme"
PORTAL = "org.x.apps.portal"
SCHEMA_DIR = "/usr/share/glib-2.0/schemas"

STYLES = {
    "styles": [
        {
            "name": "Test",
            "mixed": [
                {"name": "aqua", "color": "#000000", "themes": "T-Aqua", "cinnamon": "T-Dark-Aqua",
                 "icons": "T-Icons", "cursor": "T-Cursor"},
                {"name": "red", "color": "#000000", "themes": "T-Red", "cinnamon": "T-Dark-Red",
                 "icons": "T-Icons", "cursor": "T-Cursor"},
            ],
            "dark": [
                {"name": "aqua", "color": "#000000", "themes": "T-Dark-Aqua",
                 "icons": "T-Icons", "cursor": "T-Cursor", "default": "true"},
            ],
            "light": [
                {"name": "aqua", "color": "#000000", "themes": "T-Aqua",
                 "icons": "T-Icons", "cursor": "T-Cursor"},
            ],
        }
    ]
}

NOTIFY_STUB = """#!/bin/sh
echo "notify-send $*" >>"$STUB_LOG"
"""

HOOK = """#!/bin/sh
echo "$(basename "$0") $1" >>"$STUB_LOG"
"""


def has_schemas():
    source = subprocess.run(["gsettings", "list-schemas"], capture_output=True, text=True)
    return {INTERFACE, CINNAMON_THEME, PORTAL} <= set(source.stdout.split())


def write_executable(path, text):
    with open(path, "w") as f:
        f.write(text)
    os.chmod(path, 0o755)


@unittest.skipUnless(has_schemas(), "needs Cinnamon's GSettings schemas")
class AppearanceTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = tmp.name
        share = os.path.join(self.tmp, "share")
        for theme in ["T-Aqua", "T-Dark-Aqua", "T-Red", "T-Dark-Red"]:
            os.makedirs(os.path.join(share, "themes", theme))
        for icons in ["T-Icons", "T-Cursor"]:
            os.makedirs(os.path.join(share, "icons", icons))
        os.makedirs(os.path.join(share, "cinnamon", "styles.d"))
        with open(os.path.join(share, "cinnamon", "styles.d", "test.styles"), "w") as f:
            json.dump(STYLES, f)

        bin_dir = os.path.join(self.tmp, "bin")
        os.mkdir(bin_dir)
        write_executable(os.path.join(bin_dir, "notify-send"), NOTIFY_STUB)
        self.hooks = os.path.join(self.tmp, "config", "cinnamon-apple", "appearance.d")
        self.log = os.path.join(self.tmp, "calls.log")
        self.env = {
            "PATH": f"{bin_dir}:/usr/bin:/bin",
            "HOME": self.tmp,
            "XDG_CONFIG_HOME": os.path.join(self.tmp, "config"),
            "XDG_STATE_HOME": os.path.join(self.tmp, "state"),
            "XDG_DATA_HOME": os.path.join(self.tmp, "data"),
            "XDG_DATA_DIRS": share,
            "GSETTINGS_BACKEND": "keyfile",
            "GSETTINGS_SCHEMA_DIR": SCHEMA_DIR,
            "STUB_LOG": self.log,
        }
        self.set_themes("T-Aqua", "T-Dark-Aqua")

    def gset(self, schema, key, value):
        subprocess.run(["gsettings", "set", schema, key, value], env=self.env, check=True)

    def gget(self, schema, key):
        return subprocess.run(["gsettings", "get", schema, key], env=self.env, check=True,
                              capture_output=True, text=True).stdout.strip()

    def set_themes(self, gtk, cinnamon):
        self.gset(INTERFACE, "gtk-theme", gtk)
        self.gset(INTERFACE, "icon-theme", "T-Icons")
        self.gset(INTERFACE, "cursor-theme", "T-Cursor")
        self.gset(CINNAMON_THEME, "name", cinnamon)

    def themes(self):
        return (self.gget(INTERFACE, "gtk-theme"), self.gget(CINNAMON_THEME, "name"),
                self.gget(PORTAL, "color-scheme"))

    def switch(self, *args):
        return subprocess.run([APPEARANCE, *args], env=self.env, capture_output=True, text=True)

    def calls(self):
        if not os.path.exists(self.log):
            return []
        with open(self.log) as f:
            return f.read().splitlines()

    def add_hook(self, name, text=HOOK):
        os.makedirs(self.hooks, exist_ok=True)
        write_executable(os.path.join(self.hooks, name), text)

    def test_flips_from_mixed_to_dark_and_back(self):
        self.assertEqual(self.switch().returncode, 0)
        self.assertEqual(self.themes(), ("'T-Dark-Aqua'", "'T-Dark-Aqua'", "'prefer-dark'"))
        self.assertEqual(self.switch().returncode, 0)
        self.assertEqual(self.themes(), ("'T-Aqua'", "'T-Dark-Aqua'", "'default'"))

    def test_light_returns_to_light_mode(self):
        self.set_themes("T-Aqua", "T-Aqua")
        self.switch("dark")
        self.assertEqual(self.switch("light").returncode, 0)
        self.assertEqual(self.themes(), ("'T-Aqua'", "'T-Aqua'", "'prefer-light'"))

    def test_dark_while_dark_changes_nothing(self):
        self.set_themes("T-Dark-Aqua", "T-Dark-Aqua")
        self.assertEqual(self.switch("dark").returncode, 0)
        self.assertEqual(self.gget(INTERFACE, "gtk-theme"), "'T-Dark-Aqua'")
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "state", "cinnamon-apple", "light-mode")))

    def test_colour_missing_in_dark_uses_the_default(self):
        self.set_themes("T-Red", "T-Dark-Red")
        self.assertEqual(self.switch().returncode, 0)
        self.assertEqual(self.themes(), ("'T-Dark-Aqua'", "'T-Dark-Aqua'", "'prefer-dark'"))

    def test_hooks_get_the_new_mode(self):
        self.add_hook("10-terminal")
        self.add_hook("20-other")
        with open(os.path.join(self.hooks, "README"), "w") as f:
            f.write("not executable\n")
        self.switch()
        self.switch()
        self.assertEqual(self.calls(), ["10-terminal dark", "20-other dark",
                                        "10-terminal light", "20-other light"])

    def test_failing_hook_is_reported_after_the_rest_run(self):
        self.add_hook("10-broken", "#!/bin/sh\nexit 3\n")
        self.add_hook("20-terminal")
        result = self.switch()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.gget(INTERFACE, "gtk-theme"), "'T-Dark-Aqua'")
        calls = self.calls()
        self.assertIn("20-terminal dark", calls)
        self.assertIn("10-broken", calls[-1])
        self.assertTrue(calls[-1].startswith("notify-send"), calls)

    def test_unknown_theme_changes_nothing(self):
        self.set_themes("Adwaita", "cinnamon")
        self.add_hook("10-terminal")
        result = self.switch()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.gget(INTERFACE, "gtk-theme"), "'Adwaita'")
        calls = self.calls()
        self.assertEqual(len(calls), 1)
        self.assertIn("not one of the styles", calls[0])

    def test_rejects_unknown_argument(self):
        result = self.switch("sideways")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Usage", result.stderr)
        self.assertEqual(self.gget(INTERFACE, "gtk-theme"), "'T-Aqua'")


if __name__ == "__main__":
    unittest.main()
