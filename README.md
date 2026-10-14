# cinnamon-apple

Makes Linux Mint Cinnamon behave more like macOS. Alt plays the role of Cmd.
Ctrl+Alt+Win+M switches it off and on again, e.g. for a game.

## Requirements

Linux Mint 22 with Cinnamon on X11 (tested on 22.3). It changes desktop
settings and installs packages from third-party repositories, and there is no
single uninstall step, so read what a module does before running it.

## Usage

```sh
git clone https://github.com/andreas-glaser/cinnamon-apple.git
cd cinnamon-apple
./install.sh              # everything
./install.sh screenshots  # only selected modules
```

Safe to re-run. Run as your normal user; it calls `sudo` for package installs.

Options live in `config.sh` (screenshot destination, dock edge, scroll
direction). An environment variable of the same name overrides the file for one
run, e.g. `DOCK_POSITION=left ./install.sh dock`.

## Modules

| Module        | What it does                                           |
|---------------|--------------------------------------------------------|
| `keyboard`    | macOS keyboard layout everywhere via Toshy             |
| `screenshots` | Flameshot with macOS screenshot shortcuts              |
| `launcher`    | Ulauncher (Spotlight replacement) on Alt+Space         |
| `window`      | macOS window shortcuts, title bar buttons on the left  |
| `touchpad`    | Tap to click, three-finger gestures                    |
| `quicklook`   | Space to preview files in Nemo                         |
| `dock`        | Plank dock at the bottom, panel at the top as menu bar |
| `toggle`      | Ctrl+Alt+Win+M switches the Mac keyboard off and on    |

### Keyboard

Installs [Toshy](https://github.com/RedBearAK/toshy) (pinned release, commit
hash verified) so a PC keyboard behaves like a Mac one in every app:

| Physical key | Acts as |
|--------------|---------|
| Alt          | Cmd     |
| Win          | Option  |
| Ctrl         | Ctrl    |

Alt+C/V/X/Z/A/T/W/F work as on macOS, in terminals too (where Ctrl+C still
interrupts). In terminals Alt+V sends Ctrl+V when the clipboard holds an image,
so tools like Claude Code can paste screenshots, and Ctrl+Shift+V otherwise.
The other shortcuts in this README keep working because a small keymap
translates them for Cinnamon; it lives in Toshy's `user_apps` slice in
`~/.config/toshy/toshy_config.py` between `cinnamon-apple` markers and survives
Toshy upgrades. Anything else you put in that slice is left alone.

Games get the plain PC keyboard: Alt is Alt and none of the Mac shortcuts
apply. Toshy treats them like a virtual machine or remote desktop, which it
leaves unremapped. `PC_KEYBOARD_APPS` in `config.sh` lists them as patterns
matched against the window class; the default covers Steam games through
Proton, anything running in Wine (Lutris, Heroic, Bottles) and gamescope. For a
native game, run `xprop WM_CLASS`, click its window, add the class to the list
and re-run `./install.sh keyboard`. To switch remapping off for everything,
use Stop Toshy Services in the Toshy tray menu (Re/Start turns it back on).

Cinnamon's own shortcuts from the other modules (Alt+Q, Alt+H, Alt+M,
Alt+Space, Shift+Alt+3/4/5) still work in those apps. For a game that uses
them, switch the Mac keyboard off with the [toggle](#toggle).

The Toshy installer runs only if Toshy is not installed yet; re-running the
module just refreshes the keymap and the app list. Its questions are
pre-answered, so expect only the sudo password prompt.

Security: Toshy reads all keyboard input and injects key events. Its installer
grants your user access to input devices and `/dev/uinput` (udev rule plus the
`input` group), so any program you run gets that access too. On X11 programs
can already read and inject keys through the X server, so the added exposure
is small; it matters more on Wayland. The installer also pulls the keymapper
`xwaykeyz` from its `main` branch, which cannot be pinned.

To remove Toshy, clone the same release and run `./setup_toshy.py uninstall`.

### Screenshots

| Shortcut           | Action                              |
|--------------------|-------------------------------------|
| Shift+Alt+3        | Full screen                         |
| Shift+Alt+4        | Region                              |
| Ctrl+Shift+Alt+3   | Full screen, other destination      |
| Ctrl+Shift+Alt+4   | Region, other destination           |
| Shift+Alt+5        | Region with annotation tools        |

Shift+Alt+3/4 copy to the clipboard by default; adding Ctrl saves to
`~/Pictures/Screenshots` instead. Set `SCREENSHOTS_TO=file` in `config.sh` to
swap them, as on a stock Mac.

### Launcher

Installs Ulauncher from `ppa:agornostal/ulauncher`, opens it with Alt+Space
and starts it at login. The hotkey is a Cinnamon shortcut running
`ulauncher-toggle`, so Ulauncher's own hotkey setting is left empty. Cinnamon's
Alt+Space binding (window menu) is cleared to make room.

### Window

| Shortcut        | Action                                   |
|-----------------|------------------------------------------|
| Alt+Q           | Close window (Alt+F4 still works)        |
| Alt+M, Alt+H    | Minimize                                 |
| Ctrl+Alt+F      | Toggle fullscreen                        |
| Ctrl+Win+F      | Fill the screen (toggles maximize)       |
| Ctrl+Win+C      | Center                                   |
| Ctrl+Win+R      | Return to previous size                  |
| Ctrl+Win+arrows | Tile to that half of the screen          |
| Ctrl+Alt+Q      | Lock screen (Ctrl+Alt+L still works)     |
| Ctrl+Alt+T      | Open a terminal (Cinnamon default)       |

Ctrl+Win stands in for Fn+Ctrl, the macOS window tiling shortcuts, since a PC
keyboard's Fn key never reaches the system. They use Cinnamon's tiling, which
differs from macOS in two ways: arrows push the window, so Up then Right gives
the top-right quarter and the opposite arrow undoes the last step; and Return
to previous size restores the size but leaves the window where it was tiled.
Super+arrows (Cinnamon's own tiling) and Alt+F10 still work.

Close, minimize and maximize move to the left of the title bar.

### Touchpad

| Gesture            | Action                                       |
|--------------------|----------------------------------------------|
| 3 fingers up       | Overview of all workspaces (Mission Control) |
| 3 fingers down     | Windows on this workspace (App Expose)       |
| 3 fingers left     | Next workspace                               |
| 3 fingers right    | Previous workspace                           |

Cinnamon's two-finger swipe gestures (window tiling) are turned off so
sideways scrolling does not tile windows. Scroll direction is left as it is
unless `NATURAL_SCROLL` in `config.sh` is `true` (content follows your fingers,
as on macOS) or `false` (traditional).

### Toggle

Ctrl+Alt+Win+M switches between the Mac keyboard and stock Cinnamon, for games
such as Dota 2 that use Alt shortcuts. Off stops Toshy and resets every
shortcut cinnamon-apple sets to Cinnamon's default, so Alt is plain Alt and
Alt+Q no longer closes the window; a notification says which mode is on. The
same keys switch it back on. Your shortcuts are saved in
`~/.local/state/cinnamon-apple/` while it is off, and it switches back on when
you log in.

From a terminal: `cinnamon-apple-toggle`, or `cinnamon-apple-toggle off` / `on`.

### Dock

Installs [Plank Reloaded](https://github.com/zquestz/plank-reloaded) from its
author's apt repository; the signing key is checked against a pinned
fingerprint before the repository is added. The dock sits on the edge set by
`DOCK_POSITION` in `config.sh` (bottom, left or right), with magnification,
and hides when a window overlaps it. Drag apps onto it to pin them.

Cinnamon's panel moves to the top and loses its window list, launchers and
separators, which the dock replaces. The original layout is saved the first
time the module runs; to restore it:

```sh
bash ~/.local/state/cinnamon-apple/panel-backup.sh
```

## Adding a module

Drop a `modules/<name>.sh` file in. It is sourced by `install.sh`, so it can use
the helpers in `lib.sh` (`log`, `apt_install`, `set_keybinding`).

## Tests

```sh
python3 -B -m unittest discover -s tests
```

## License

MIT, see [LICENSE](LICENSE).
