# cinnamon-apple

Makes Linux Mint Cinnamon behave more like macOS. Alt plays the role of Cmd.
Ctrl+Alt+Win+M switches the shortcuts off and on again, e.g. for a game.

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
| `keyboard`    | Alt+C/V/X/Z and other Cmd shortcuts in every app       |
| `screenshots` | Flameshot with macOS screenshot shortcuts              |
| `launcher`    | Ulauncher (Spotlight replacement) on Alt+Space         |
| `window`      | macOS window shortcuts, title bar buttons on the left  |
| `touchpad`    | Tap to click, three-finger gestures                    |
| `quicklook`   | Space to preview files in Nemo                         |
| `dock`        | Plank dock at the bottom, panel at the top as menu bar |
| `toggle`      | Ctrl+Alt+Win+M switches the Mac shortcuts off and on   |
| `appearance`  | Ctrl+Alt+Win+D switches between dark and light mode    |
| `terminal`    | Terminator light/dark profiles that follow the mode    |

### Keyboard

| Shortcut       | Action           | In terminals sends |
|----------------|------------------|--------------------|
| Alt+C          | Copy             | Ctrl+Shift+C       |
| Alt+V          | Paste            | Ctrl+Shift+V       |
| Alt+X          | Cut              | nothing            |
| Alt+Z          | Undo             | nothing            |
| Shift+Alt+Z    | Redo             | nothing            |
| Alt+A          | Select all       | Ctrl+Shift+A       |
| Alt+F          | Find             | Ctrl+Shift+F       |
| Alt+T          | New tab          | Ctrl+Shift+T       |
| Alt+W          | Close tab        | Ctrl+Shift+W       |

Each is a Cinnamon shortcut that runs `cinnamon-apple-key`, which sends the
Ctrl version of the key to the focused window with `xdotool`. In terminals it
sends the Ctrl+Shift version instead, so Ctrl+C still interrupts, and Alt+Z
does nothing rather than suspend the running program. When the clipboard holds
an image, Alt+V in a terminal sends Ctrl+V, so tools like Claude Code can paste
screenshots. Terminals are recognised by window class; the list is in
`files/cinnamon-apple-key`.

Nothing watches the keyboard; only these key combinations reach the script.
The trade-off is that apps no longer receive these Alt keys themselves, such as
Alt+F for a File menu, and that holding a key repeats slightly slower than a
real Ctrl shortcut. Win is not remapped, and Ctrl keeps working as usual.

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

Ctrl+Alt+Win+M switches between the Mac shortcuts and stock Cinnamon, for games
such as Dota 2 that use Alt shortcuts. Off resets every shortcut cinnamon-apple
sets to Cinnamon's default, so Alt+Q no longer closes the window; a notification says which mode is on. The
same keys switch it back on. Your shortcuts are saved in
`~/.local/state/cinnamon-apple/` while it is off, and it switches back on when
you log in.

From a terminal: `cinnamon-apple-toggle`, or `cinnamon-apple-toggle off` / `on`.

### Appearance

Ctrl+Alt+Win+D switches between dark and light mode. macOS has no shortcut for
this; the keys are Ctrl+Option+Cmd+D on a Mac keyboard. It does what the Mode
buttons under System Settings > Themes do: the colour you picked stays, and
apps that follow the system's dark mode preference switch along. Going light
returns to the mode you came from, so Mint's default mixed mode (light windows,
dark panel) comes back as it was. The theme has to be one of the styles listed
in Themes; with a custom combination a notification says so and nothing
changes. Like the other shortcuts, it is off while the Mac shortcuts are
switched off.

To switch other things along, put an executable in
`~/.config/cinnamon-apple/appearance.d/`. Each one runs afterwards with `dark`
or `light` as its argument, e.g. a script that changes the terminal's profile.

From a terminal: `cinnamon-apple-appearance`, or `cinnamon-apple-appearance dark` / `light`.

### Terminal

Installs Terminator and gives it two profiles, `light` (GitHub Light colours)
and `dark` (One Dark). A small Terminator plugin follows Dark mode under System
Settings > Themes, which the [appearance](#appearance) shortcut also sets: open
terminals on `light`, `dark` or `default` switch at once, and new windows open
with the matching profile. Mixed mode counts as light. Terminals you put on
another profile yourself keep it.

Claude Code with its theme set to `auto` (`/theme`) and Codex take their colours
from the terminal, so they switch along.

The profiles start as copies of `default`, so your font and scrollback carry
over; re-running the module resets only their colours. Terminator reads its
config at start, so close every Terminator window after installing. It also
writes back the config it loaded when you save its preferences, so close it
before re-running the module too.

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
