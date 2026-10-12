import os
import re
import runpy
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "files", "toshy_apply_config.py")

# A cut-down Toshy config: the remote lists are built before user_custom_lists
# and matched after it, as in the real file.
CONFIG = '''\
def toRgxStr(lst_of_str):
    lst_of_str_clean = [str(x).replace('^','').replace('$','') for x in lst_of_str]
    return "|".join('^'+x.casefold()+'$' for x in lst_of_str_clean)

terminals = ["gnome-terminal"]
vscodes = ["code"]
remotes = ["virtualbox"]
remoteStr = toRgxStr(remotes)
terms_and_remotes_Str = toRgxStr(terminals + remotes)
vscodes_and_remotes_Str = toRgxStr(vscodes + remotes)

###  SLICE_MARK_START: user_custom_lists  ###  EDITS OUTSIDE THESE MARKS WILL BE LOST ON UPGRADE
user_list = ["mine"]
###  SLICE_MARK_END: user_custom_lists  ###  EDITS OUTSIDE THESE MARKS WILL BE LOST ON UPGRADE

###  SLICE_MARK_START: user_apps  ###  EDITS OUTSIDE THESE MARKS WILL BE LOST ON UPGRADE
user_keymap = "mine"
###  SLICE_MARK_END: user_apps  ###  EDITS OUTSIDE THESE MARKS WILL BE LOST ON UPGRADE
'''

DEFAULT_APPS = ["steam_app_.*", r".*\.exe", "gamescope"]


def matches(pattern, wm_class):
    return re.search(pattern, wm_class, re.I) is not None


class ApplyConfigTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.config = os.path.join(self.dir.name, "toshy_config.py")
        self.keymap = os.path.join(self.dir.name, "keymap.py")
        self.write(self.config, CONFIG)
        self.write(self.keymap, 'cinnamon_apple_keymap = "v1"\n')

    def write(self, path, text):
        with open(path, "w") as f:
            f.write(text)

    def read_config(self):
        with open(self.config) as f:
            return f.read()

    def apply(self, *apps):
        return subprocess.run(
            [sys.executable, "-I", SCRIPT, self.config, self.keymap, *apps],
            capture_output=True, text=True,
        )

    def test_pc_keyboard_apps_are_treated_as_remotes(self):
        self.assertEqual(self.apply(*DEFAULT_APPS).returncode, 0)
        ns = runpy.run_path(self.config)

        for wm_class in ["steam_app_570", "Game.EXE", "gamescope", "VirtualBox"]:
            self.assertTrue(matches(ns["remoteStr"], wm_class), wm_class)
            self.assertTrue(matches(ns["vscodes_and_remotes_Str"], wm_class), wm_class)
            self.assertTrue(matches(ns["terms_and_remotes_Str"], wm_class), wm_class)
        for wm_class in ["firefox", "steam", "exe", "gamescope-wl"]:
            self.assertFalse(matches(ns["remoteStr"], wm_class), wm_class)
        self.assertEqual(ns["cinnamon_apple_keymap"], "v1")

    def test_rerun_replaces_blocks_and_keeps_user_content(self):
        self.apply(*DEFAULT_APPS)
        self.write(self.keymap, 'cinnamon_apple_keymap = "v2"\n')
        self.assertEqual(self.apply("dota2").returncode, 0)

        config = self.read_config()
        self.assertEqual(config.count("# >>> cinnamon-apple >>>"), 2)
        ns = runpy.run_path(self.config)
        self.assertEqual(ns["cinnamon_apple_keymap"], "v2")
        self.assertEqual(ns["remotes"], ["virtualbox", "dota2"])
        self.assertEqual(ns["user_list"], ["mine"])
        self.assertEqual(ns["user_keymap"], "mine")

        self.apply("dota2")
        self.assertEqual(self.read_config(), config)

    def test_no_apps_leaves_remotes_unchanged(self):
        self.assertEqual(self.apply().returncode, 0)
        self.assertEqual(runpy.run_path(self.config)["remotes"], ["virtualbox"])

    def test_rejects_bad_patterns_without_touching_config(self):
        for app in ["steam_app_(", "a|b"]:
            result = self.apply(app)
            self.assertNotEqual(result.returncode, 0, app)
            self.assertIn("PC_KEYBOARD_APPS", result.stderr)
            self.assertEqual(self.read_config(), CONFIG)

    def test_fails_when_a_slice_is_missing(self):
        self.write(self.config, CONFIG.replace("user_custom_lists", "something_else"))
        result = self.apply(*DEFAULT_APPS)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("user_custom_lists", result.stderr)
        self.assertNotIn("cinnamon-apple", self.read_config())


if __name__ == "__main__":
    unittest.main()
