def cinnamon_apple_terminal_paste():
    # Terminal paste (Ctrl+Shift+V) only carries text. TUIs such as Claude Code
    # read a clipboard image themselves when they receive a literal Ctrl+V.
    try:
        targets = subprocess.run(
            ["xclip", "-selection", "clipboard", "-t", "TARGETS", "-o"],
            capture_output=True, text=True, timeout=0.5,
        ).stdout.split()
    except (OSError, subprocess.TimeoutExpired) as err:
        error(f"cinnamon-apple: cannot read clipboard targets, pasting as text: {err}")
        targets = []
    if any(target.startswith("image/") for target in targets):
        return C("C-v")
    return C("C-Shift-v")


keymap("cinnamon-apple terminals", {
    C("RC-V"):                  cinnamon_apple_terminal_paste,  # Paste images too
}, when = lambda ctx:
    cnfg.screen_has_focus and
    ctx_app_is_terminal
)

keymap("cinnamon-apple", {
    C("RC-Space"):              [iEF2NT(), C("Alt-Space")],     # Ulauncher
    C("RC-H"):                  C("Alt-h"),                     # Hide (minimize)
    C("RC-M"):                  C("Alt-m"),                     # Minimize
    C("Super-RC-f"):            C("C-Alt-f"),                   # Fullscreen
    C("LC-RC-f"):               C("C-Alt-f"),                   # Fullscreen (terminals)
    # Ctrl+Win stands in for Fn+Ctrl window tiling; Ctrl is Super in GUI apps, LC in terminals
    C("Super-Alt-f"):           C("C-Super-f"),                 # Fill (maximize toggle)
    C("LC-Alt-f"):              C("C-Super-f"),                 # Fill (terminals)
    C("Super-Alt-c"):           C("C-Super-c"),                 # Center
    C("LC-Alt-c"):              C("C-Super-c"),                 # Center (terminals)
    C("Super-Alt-r"):           C("C-Super-r"),                 # Return to previous size
    C("LC-Alt-r"):              C("C-Super-r"),                 # Return to previous size (terminals)
    C("Super-Alt-Left"):        C("C-Super-Left"),              # Tile left half
    C("LC-Alt-Left"):           C("C-Super-Left"),              # Tile left half (terminals)
    C("Super-Alt-Right"):       C("C-Super-Right"),             # Tile right half
    C("LC-Alt-Right"):          C("C-Super-Right"),             # Tile right half (terminals)
    C("Super-Alt-Up"):          C("C-Super-Up"),                # Tile top half
    C("LC-Alt-Up"):             C("C-Super-Up"),                # Tile top half (terminals)
    C("Super-Alt-Down"):        C("C-Super-Down"),              # Tile bottom half
    C("LC-Alt-Down"):           C("C-Super-Down"),              # Tile bottom half (terminals)
    C("Super-RC-Alt-m"):        C("C-Alt-Super-m"),             # Toggle Mac keyboard
    C("LC-RC-Alt-m"):           C("C-Alt-Super-m"),             # Toggle Mac keyboard (terminals)
    C("Super-RC-Alt-d"):        C("C-Alt-Super-d"),             # Toggle dark mode
    C("LC-RC-Alt-d"):           C("C-Alt-Super-d"),             # Toggle dark mode (terminals)
    C("Super-RC-q"):            C("C-Alt-q"),                   # Lock screen
    C("LC-RC-q"):               C("C-Alt-q"),                   # Lock screen (terminals)
    C("Super-RC-t"):            C("C-Alt-t"),                   # Open terminal
    C("LC-RC-t"):               C("C-Alt-t"),                   # Open terminal (terminals)
    C("Shift-RC-Key_3"):        C("Shift-Alt-Key_3"),           # Screenshot full screen
    C("Shift-RC-Key_4"):        C("Shift-Alt-Key_4"),           # Screenshot region
    C("Shift-RC-Key_5"):        C("Shift-Alt-Key_5"),           # Screenshot with annotation
    C("Super-Shift-RC-Key_3"):  C("C-Shift-Alt-Key_3"),         # Screenshot full screen, other destination
    C("Super-Shift-RC-Key_4"):  C("C-Shift-Alt-Key_4"),         # Screenshot region, other destination
    C("LC-Shift-RC-Key_3"):     C("C-Shift-Alt-Key_3"),         # (terminals)
    C("LC-Shift-RC-Key_4"):     C("C-Shift-Alt-Key_4"),         # (terminals)
}, when = lambda ctx:
    cnfg.screen_has_focus and
    not ctx_app_is_remote
)
