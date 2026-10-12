"""Insert or refresh our keymap inside the user_apps slice of a Toshy config.

Toshy keeps the contents of its slices across upgrades and reinstalls, and
keymaps there take priority over its defaults. Only the block between our own
markers is touched, so any other customisation in the slice is preserved.
"""
import os
import re
import sys
import tempfile

BEGIN = "# >>> cinnamon-apple >>>"
END = "# <<< cinnamon-apple <<<"
SLICE_END = "###  SLICE_MARK_END: user_apps  ###"


def main(config_path, keymap_path):
    with open(config_path) as f:
        config = f.read()
    with open(keymap_path) as f:
        managed = f"{BEGIN}\n{f.read().strip()}\n{END}\n"

    existing = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n", re.S)
    if existing.search(config):
        config = existing.sub(lambda _: managed, config, count=1)
    elif config.count(SLICE_END) == 1:
        config = config.replace(SLICE_END, managed + "\n" + SLICE_END)
    else:
        sys.exit(f"{config_path}: cannot find a single user_apps slice to edit")

    compile(config, config_path, "exec")

    directory = os.path.dirname(config_path)
    fd, tmp_path = tempfile.mkstemp(dir=directory, prefix=".toshy_config.")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(config)
        os.chmod(tmp_path, os.stat(config_path).st_mode & 0o777)
        os.replace(tmp_path, config_path)
    except BaseException:
        os.unlink(tmp_path)
        raise


if __name__ == "__main__":
    main(*sys.argv[1:])
