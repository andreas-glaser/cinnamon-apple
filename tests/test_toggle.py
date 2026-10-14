import os
import subprocess
import tempfile
import unittest

TOGGLE = os.path.join(os.path.dirname(__file__), "..", "files", "cinnamon-apple-toggle")
WM = "org.cinnamon.desktop.keybindings.wm"
KEYS = "org.cinnamon.desktop.keybindings"

STUB = """#!/bin/sh
echo "$(basename "$0") $*" >>"$STUB_LOG"
[ "$1 $2" = "--user cat" ] && [ -f "$STUB_DIR/no-toshy" ] && exit 1
exit 0
"""


def has_cinnamon_schemas():
    source = subprocess.run(["gsettings", "list-schemas"], capture_output=True, text=True)
    return WM in source.stdout.split()


@unittest.skipUnless(has_cinnamon_schemas(), "needs Cinnamon's GSettings schemas")
class ToggleTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = tmp.name
        bin_dir = os.path.join(self.tmp, "bin")
        os.mkdir(bin_dir)
        for name in ["systemctl", "notify-send"]:
            path = os.path.join(bin_dir, name)
            with open(path, "w") as f:
                f.write(STUB)
            os.chmod(path, 0o755)
        self.log = os.path.join(self.tmp, "calls.log")
        self.env = {
            "PATH": f"{bin_dir}:/usr/bin:/bin",
            "HOME": self.tmp,
            "XDG_CONFIG_HOME": os.path.join(self.tmp, "config"),
            "XDG_STATE_HOME": os.path.join(self.tmp, "state"),
            "GSETTINGS_BACKEND": "keyfile",
            "STUB_LOG": self.log,
            "STUB_DIR": self.tmp,
        }
        self.saved = os.path.join(self.tmp, "state", "cinnamon-apple", "mac-keyboard.json")

        self.gset(WM, "close", "['<Alt>F4', '<Alt>q']")
        self.gset(WM, "activate-window-menu", "@as []")
        self.gset(KEYS, "custom-list",
                  "['custom-cinnamon-apple-shot-full', 'custom0', 'custom-cinnamon-apple-toggle']")

    def gset(self, schema, key, value):
        subprocess.run(["gsettings", "set", schema, key, value], env=self.env, check=True)

    def gget(self, schema, key):
        return subprocess.run(["gsettings", "get", schema, key], env=self.env, check=True,
                              capture_output=True, text=True).stdout.strip()

    def toggle(self, *args):
        return subprocess.run([TOGGLE, *args], env=self.env, capture_output=True, text=True)

    def calls(self):
        if not os.path.exists(self.log):
            return []
        with open(self.log) as f:
            calls = f.read().splitlines()
        os.remove(self.log)
        return [c for c in calls if not c.startswith("systemctl --user cat")]

    def test_off_resets_shortcuts_and_on_restores_them(self):
        self.assertEqual(self.toggle("off").returncode, 0)
        self.assertEqual(self.gget(WM, "close"), "['<Alt>F4']")
        self.assertEqual(self.gget(WM, "activate-window-menu"), "['<Alt>space']")
        self.assertEqual(self.gget(KEYS, "custom-list"), "['custom0', 'custom-cinnamon-apple-toggle']")
        self.assertTrue(os.path.exists(self.saved))
        calls = self.calls()
        self.assertIn("systemctl --user stop toshy-config.service", calls)
        self.assertTrue(calls[-1].startswith("notify-send"), calls)
        self.assertIn("Mac keyboard off", calls[-1])

        self.gset(KEYS, "custom-list", "['custom0', 'custom-cinnamon-apple-toggle', 'custom1']")
        self.assertEqual(self.toggle("on").returncode, 0)
        self.assertEqual(self.gget(WM, "close"), "['<Alt>F4', '<Alt>q']")
        self.assertEqual(self.gget(WM, "activate-window-menu"), "@as []")
        self.assertEqual(
            self.gget(KEYS, "custom-list"),
            "['custom0', 'custom-cinnamon-apple-toggle', 'custom1', 'custom-cinnamon-apple-shot-full']",
        )
        self.assertFalse(os.path.exists(self.saved))
        calls = self.calls()
        self.assertIn("systemctl --user start toshy-config.service", calls)
        self.assertIn("Mac keyboard on", calls[-1])

    def test_no_argument_flips_the_mode(self):
        self.toggle()
        self.assertTrue(os.path.exists(self.saved))
        self.toggle()
        self.assertFalse(os.path.exists(self.saved))
        self.assertEqual(self.gget(WM, "close"), "['<Alt>F4', '<Alt>q']")

    def test_second_off_keeps_the_first_snapshot(self):
        self.toggle("off")
        self.toggle("off")
        self.toggle("on")
        self.assertEqual(self.gget(WM, "close"), "['<Alt>F4', '<Alt>q']")

    def test_on_while_on_only_starts_toshy(self):
        self.assertEqual(self.toggle("on").returncode, 0)
        self.assertEqual(self.calls(), ["systemctl --user start toshy-config.service"])
        self.assertEqual(self.gget(WM, "close"), "['<Alt>F4', '<Alt>q']")

    def test_works_without_toshy(self):
        open(os.path.join(self.tmp, "no-toshy"), "w").close()
        self.assertEqual(self.toggle("off").returncode, 0)
        self.assertFalse(any(c.startswith("systemctl") for c in self.calls()))
        self.assertEqual(self.gget(WM, "close"), "['<Alt>F4']")

    def test_rejects_unknown_argument(self):
        result = self.toggle("sideways")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Usage", result.stderr)
        self.assertEqual(self.calls(), [])


if __name__ == "__main__":
    unittest.main()
