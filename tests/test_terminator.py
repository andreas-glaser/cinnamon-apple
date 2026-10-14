import os
import subprocess
import tempfile
import textwrap
import unittest

FILES = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "files"))
SYSTEM_PYTHON = "/usr/bin/python3"

CONFIG = """\
[global_config]
  always_split_with_profile = True
[profiles]
  [[default]]
    background_color = "#000000"
    font = Mono 13
    scrollback_lines = 10000
  [[light]]
    background_color = "#ffffff"
    font = Mono 9
  [[ssh]]
    background_color = "#330000"
[layouts]
  [[default]]
    [[[window0]]]
      type = Window
      parent = ""
    [[[child1]]]
      type = Terminal
      parent = window0
      profile = default
"""


def system_python_has(*modules):
    check = "; ".join(f"import {m}" for m in modules)
    result = subprocess.run([SYSTEM_PYTHON, "-I", "-c", check], capture_output=True)
    return result.returncode == 0


class TerminatorTestCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.config_home = os.path.join(tmp.name, "config")
        self.config = os.path.join(self.config_home, "terminator", "config")
        os.makedirs(os.path.dirname(self.config))
        with open(self.config, "w") as f:
            f.write(CONFIG)
        self.env = {
            "PATH": "/usr/bin:/bin",
            "HOME": tmp.name,
            "XDG_CONFIG_HOME": self.config_home,
            "GSETTINGS_BACKEND": "keyfile",
        }

    def run_python(self, *args, **kwargs):
        return subprocess.run([SYSTEM_PYTHON, "-I", "-B", *args], env=self.env,
                              capture_output=True, text=True, **kwargs)

    def write_profiles(self):
        result = self.run_python(os.path.join(FILES, "terminator_profiles.py"), self.config)
        self.assertEqual(result.returncode, 0, result.stderr)


@unittest.skipUnless(system_python_has("configobj"), "needs python3-configobj")
class ProfilesTest(TerminatorTestCase):
    def read(self):
        from_python = self.run_python("-c", textwrap.dedent(f"""
            import json
            from configobj import ConfigObj
            print(json.dumps(ConfigObj({self.config!r}).dict()))
        """))
        import json
        return json.loads(from_python.stdout)

    def test_adds_profiles_from_default_and_enables_plugin(self):
        self.write_profiles()
        config = self.read()
        dark, light = config["profiles"]["dark"], config["profiles"]["light"]

        self.assertEqual(dark["background_color"], "#1e2228")
        self.assertEqual(dark["font"], "Mono 13")
        self.assertEqual(dark["scrollback_lines"], "10000")
        self.assertEqual(light["background_color"], "#fafaf8")
        self.assertEqual(light["font"], "Mono 9")
        self.assertEqual(config["profiles"]["default"]["background_color"], "#000000")
        self.assertEqual(config["profiles"]["ssh"]["background_color"], "#330000")
        self.assertEqual(config["global_config"]["enabled_plugins"], [
            "LaunchpadBugURLHandler", "LaunchpadCodeURLHandler", "APTURLHandler",
            "CinnamonAppleAppearance",
        ])
        self.assertEqual(config["global_config"]["always_split_with_profile"], "True")

    def test_rerun_changes_nothing(self):
        self.write_profiles()
        with open(self.config) as f:
            first = f.read()
        self.write_profiles()
        with open(self.config) as f:
            self.assertEqual(f.read(), first)

    def test_keeps_an_existing_plugin_list(self):
        with open(self.config, "a") as f:
            f.write("[plugins]\n")
        with open(self.config) as f:
            text = f.read().replace(
                "[global_config]\n", "[global_config]\n  enabled_plugins = TerminalShot\n")
        with open(self.config, "w") as f:
            f.write(text)
        self.write_profiles()
        self.assertEqual(self.read()["global_config"]["enabled_plugins"],
                         ["TerminalShot", "CinnamonAppleAppearance"])


@unittest.skipUnless(system_python_has("configobj", "terminatorlib"), "needs Terminator")
class AppearancePluginTest(TerminatorTestCase):
    def test_follows_dark_mode(self):
        self.write_profiles()
        script = textwrap.dedent(f"""
            import sys
            sys.path.insert(0, {FILES!r})
            from gi.repository import Gio, GLib
            from terminatorlib.config import Config
            import terminator_appearance

            class FakeTerminal:
                def __init__(self, profile):
                    self.profile = profile
                def get_profile(self):
                    return self.profile
                def force_set_profile(self, _widget, profile):
                    self.profile = profile

            class FakeTerminator:
                terminals = [FakeTerminal("default"), FakeTerminal("light"), FakeTerminal("ssh")]

            # The real one needs a display.
            terminator_appearance.Terminator = FakeTerminator
            terminals = FakeTerminator.terminals
            portal = Gio.Settings.new("org.x.apps.portal")

            def report(label):
                layout = Config().layout_get_config("default")["child1"]["profile"]
                print(label, layout, *[t.profile for t in terminals])

            portal.set_string("color-scheme", "prefer-dark")
            plugin = terminator_appearance.CinnamonAppleAppearance()
            report("start")
            for scheme in ["prefer-light", "default", "prefer-dark"]:
                portal.set_string("color-scheme", scheme)
                while GLib.MainContext.default().iteration(False):
                    pass
                report(scheme)
        """)
        result = self.run_python("-c", script, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), [
            "start dark dark dark ssh",
            "prefer-light light light light ssh",
            "default light light light ssh",
            "prefer-dark dark dark dark ssh",
        ])


if __name__ == "__main__":
    unittest.main()
