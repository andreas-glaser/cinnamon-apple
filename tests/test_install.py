import os
import pty
import shutil
import subprocess
import tempfile
import unittest

REPO = os.path.join(os.path.dirname(__file__), "..")

# Each fake module records that it ran; "broken" fails part way.
MODULES = {
    "alpha": "# Alpha does the first thing.\n\necho alpha >>\"$RAN\"\n",
    "beta": "# Beta does the second thing.\n#   over two lines\n\necho beta >>\"$RAN\"\n",
    "broken": "# Broken fails.\n\nfalse\necho broken >>\"$RAN\"\n",
}


class InstallTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = tmp.name
        for name in ["install.sh", "lib.sh", "config.sh"]:
            shutil.copy(os.path.join(REPO, name), self.root)
        os.mkdir(os.path.join(self.root, "modules"))
        self.ran = os.path.join(self.root, "ran")
        self.env = {
            "PATH": "/usr/bin:/bin",
            "HOME": self.root,
            "XDG_STATE_HOME": os.path.join(self.root, "state"),
            "RAN": self.ran,
        }

    def add_modules(self, *names):
        for name in names:
            with open(os.path.join(self.root, "modules", f"{name}.sh"), "w") as f:
                f.write(MODULES[name])

    def install(self, *args):
        return subprocess.run([os.path.join(self.root, "install.sh"), *args], env=self.env,
                              stdin=subprocess.DEVNULL, capture_output=True, text=True)

    def install_in_terminal(self, answers):
        master, slave = pty.openpty()
        proc = subprocess.Popen([os.path.join(self.root, "install.sh")], env=self.env,
                                stdin=slave, stdout=slave, stderr=slave)
        os.close(slave)
        os.write(master, answers.encode())
        output = b""
        while True:
            try:
                chunk = os.read(master, 4096)
            except OSError:
                break
            if not chunk:
                break
            output += chunk
        os.close(master)
        return proc.wait(timeout=10), output.decode()

    def ran_modules(self):
        if not os.path.exists(self.ran):
            return []
        with open(self.ran) as f:
            return f.read().split()

    def test_asks_about_each_module_and_runs_the_chosen_ones(self):
        self.add_modules("alpha", "beta")
        status, output = self.install_in_terminal("n\n\ny\n")
        self.assertEqual(status, 0, output)
        self.assertIn("Alpha does the first thing.", output)
        self.assertIn("over two lines", output)
        self.assertIn("Will set up: beta", output)
        self.assertEqual(self.ran_modules(), ["beta"])

    def test_declining_the_summary_runs_nothing(self):
        self.add_modules("alpha")
        status, output = self.install_in_terminal("y\nn\n")
        self.assertEqual(status, 0, output)
        self.assertEqual(self.ran_modules(), [])

    def test_selecting_nothing_runs_nothing(self):
        self.add_modules("alpha", "beta")
        status, output = self.install_in_terminal("n\nn\n")
        self.assertEqual(status, 0, output)
        self.assertIn("Nothing selected", output)
        self.assertEqual(self.ran_modules(), [])

    def test_without_a_terminal_it_refuses_to_guess(self):
        self.add_modules("alpha")
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--all", result.stderr)
        self.assertEqual(self.ran_modules(), [])

    def test_all_runs_every_module_without_asking(self):
        self.add_modules("alpha", "beta")
        result = self.install("--all")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.ran_modules(), ["alpha", "beta"])
        self.assertIn("[2/2] beta", result.stdout)

    def test_named_modules_run_in_the_given_order(self):
        self.add_modules("alpha", "beta")
        result = self.install("beta", "alpha")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.ran_modules(), ["beta", "alpha"])

    def test_unknown_module_runs_nothing(self):
        self.add_modules("alpha")
        result = self.install("alpha", "nope")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("No such module: nope", result.stderr)
        self.assertEqual(self.ran_modules(), [])

    def test_failing_module_is_named(self):
        self.add_modules("alpha", "broken")
        result = self.install("--all")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Module broken failed", result.stderr)
        self.assertEqual(self.ran_modules(), ["alpha"])

    def test_list_shows_descriptions(self):
        self.add_modules("alpha", "beta")
        result = self.install("--list")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Beta does the second thing.", result.stdout)
        self.assertEqual(self.ran_modules(), [])


if __name__ == "__main__":
    unittest.main()
