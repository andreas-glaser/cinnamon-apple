"""Write cinnamon-apple's blocks into the user slices of a Toshy config.

Usage: toshy_apply_config.py CONFIG KEYMAP [PC_KEYBOARD_APP...]

KEYMAP goes into the user_apps slice. Each PC_KEYBOARD_APP is a regex matched
against WM_CLASS; matching apps are added to Toshy's remotes, which it leaves
almost entirely unremapped, so games get the plain PC keyboard.

Toshy keeps the contents of its slices across upgrades and reinstalls. Only
the blocks between our own markers are touched, so any other customisation in
a slice is preserved.
"""
import os
import re
import sys
import tempfile

BEGIN = "# >>> cinnamon-apple >>>"
END = "# <<< cinnamon-apple <<<"
BLOCK = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n", re.S)


def pc_keyboard_lists(apps):
    for app in apps:
        try:
            re.compile(app)
        except re.error as err:
            sys.exit(f"PC_KEYBOARD_APPS: invalid pattern {app!r}: {err}")
        # toRgxStr anchors each entry; an alternation would escape the anchors.
        if "|" in app:
            sys.exit(f"PC_KEYBOARD_APPS: list {app!r} as separate patterns instead of using '|'")
    # Toshy derives these from remotes before this slice and reads them after it.
    return "\n".join([
        f"remotes += {[app.casefold() for app in apps]!r}",
        "remoteStr = toRgxStr(remotes)",
        "terms_and_remotes_Str = toRgxStr(terminals + remotes)",
        "vscodes_and_remotes_Str = toRgxStr(vscodes + remotes)",
    ])


def set_block(config, slice_name, body):
    start = f"###  SLICE_MARK_START: {slice_name}  ###"
    end = f"###  SLICE_MARK_END: {slice_name}  ###"
    if config.count(start) != 1 or config.count(end) != 1 or config.find(end) < config.find(start):
        sys.exit(f"cannot find a single {slice_name} slice to edit")
    head, rest = config.split(start)
    content, tail = rest.split(end)

    block = f"{BEGIN}\n{body.strip()}\n{END}\n"
    if BLOCK.search(content):
        content = BLOCK.sub(lambda _: block, content, count=1)
    else:
        content += block + "\n"
    return head + start + content + end + tail


def main(config_path, keymap_path, *pc_keyboard_apps):
    with open(config_path) as f:
        config = f.read()
    with open(keymap_path) as f:
        keymap = f.read()

    config = set_block(config, "user_custom_lists", pc_keyboard_lists(pc_keyboard_apps))
    config = set_block(config, "user_apps", keymap)
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
    if len(sys.argv) < 3:
        sys.exit(__doc__.splitlines()[2])
    main(*sys.argv[1:])
