import os
import subprocess
import tempfile
import unittest

KEY = os.path.join(os.path.dirname(__file__), "..", "files", "cinnamon-apple-key")

XPROP_STUB = """#!/bin/sh
if [ "$1" = "-root" ]; then
    echo "_NET_ACTIVE_WINDOW(WINDOW): window id # $STUB_WINDOW"
else
    echo "WM_CLASS(STRING) = $STUB_CLASS"
fi
"""

XCLIP_STUB = """#!/bin/sh
[ -n "$STUB_TARGETS" ] || { echo "Error: target TARGETS not available" >&2; exit 1; }
printf '%s\\n' $STUB_TARGETS
"""

LOG_STUB = """#!/bin/sh
echo "$(basename "$0") $*" >>"$STUB_LOG"
"""


class KeyTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        bin_dir = os.path.join(tmp.name, "bin")
        os.mkdir(bin_dir)
        for name, text in [("xprop", XPROP_STUB), ("xclip", XCLIP_STUB),
                           ("xdotool", LOG_STUB), ("notify-send", LOG_STUB)]:
            path = os.path.join(bin_dir, name)
            with open(path, "w") as f:
                f.write(text)
            os.chmod(path, 0o755)
        self.log = os.path.join(tmp.name, "calls.log")
        self.env = {
            "PATH": f"{bin_dir}:/usr/bin:/bin",
            "STUB_LOG": self.log,
            "STUB_WINDOW": "0x8200003",
            "STUB_CLASS": '"Navigator", "firefox"',
            "STUB_TARGETS": "",
        }

    def key(self, *args, **env):
        result = subprocess.run([KEY, *args], env={**self.env, **env},
                                capture_output=True, text=True)
        calls = []
        if os.path.exists(self.log):
            with open(self.log) as f:
                calls = f.read().splitlines()
            os.remove(self.log)
        return result, calls

    def test_app_gets_ctrl(self):
        result, calls = self.key("c")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(calls, ["xdotool keyup c key --clearmodifiers ctrl+c"])

    def test_redo(self):
        _, calls = self.key("shift+z")
        self.assertEqual(calls, ["xdotool keyup z key --clearmodifiers ctrl+shift+z"])

    def test_terminal_gets_ctrl_shift(self):
        _, calls = self.key("c", STUB_CLASS='"terminator", "Terminator"')
        self.assertEqual(calls, ["xdotool keyup c key --clearmodifiers ctrl+shift+c"])

    def test_terminal_pastes_text_with_ctrl_shift_v(self):
        _, calls = self.key("v", STUB_CLASS='"terminator", "Terminator"',
                            STUB_TARGETS="TARGETS UTF8_STRING text/plain")
        self.assertEqual(calls, ["xdotool keyup v key --clearmodifiers ctrl+shift+v"])

    def test_terminal_pastes_image_with_ctrl_v(self):
        _, calls = self.key("v", STUB_CLASS='"terminator", "Terminator"',
                            STUB_TARGETS="TARGETS image/png")
        self.assertEqual(calls, ["xdotool keyup v key --clearmodifiers ctrl+v"])

    def test_terminal_with_empty_clipboard_pastes_text(self):
        _, calls = self.key("v", STUB_CLASS='"terminator", "Terminator"')
        self.assertEqual(calls, ["xdotool keyup v key --clearmodifiers ctrl+shift+v"])

    def test_terminal_never_gets_ctrl_z(self):
        result, calls = self.key("z", STUB_CLASS='"terminator", "Terminator"')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(calls, [])

    def test_reload(self):
        _, calls = self.key("r")
        self.assertEqual(calls, ["xdotool keyup r key --clearmodifiers ctrl+r"])

    def test_terminal_never_gets_reload(self):
        result, calls = self.key("r", STUB_CLASS='"terminator", "Terminator"')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(calls, [])

    def test_no_focused_window_counts_as_app(self):
        _, calls = self.key("v", STUB_WINDOW="0x0")
        self.assertEqual(calls, ["xdotool keyup v key --clearmodifiers ctrl+v"])

    def test_rejects_unknown_key(self):
        result, calls = self.key("q")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Usage", result.stderr)
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
