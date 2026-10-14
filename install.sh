#!/usr/bin/env bash
# Makes Linux Mint Cinnamon behave more like macOS.
# Usage: ./install.sh            run every module
#        ./install.sh launcher   run only the named module(s)
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=lib.sh
source "$ROOT/lib.sh"
# shellcheck source=config.sh
source "$ROOT/config.sh"

if [[ $EUID -eq 0 ]]; then
    echo "Run as your normal user, not root; sudo is used where needed." >&2
    exit 1
fi

if (($#)); then
    modules=()
    for name in "$@"; do
        modules+=("$ROOT/modules/$name.sh")
    done
else
    modules=("$ROOT"/modules/*.sh)
fi

for module in "${modules[@]}"; do
    [[ -f $module ]] || { echo "No such module: $module" >&2; exit 1; }
done

# Modules change the shortcuts the toggle saved; restore them first so turning
# it back on later does not undo this run.
if [[ -f ${XDG_STATE_HOME:-$HOME/.local/state}/cinnamon-apple/mac-keyboard.json ]]; then
    log "Turning the Mac keyboard back on"
    "$ROOT/files/cinnamon-apple-toggle" on
fi

for module in "${modules[@]}"; do
    log "$(basename "$module" .sh)"
    # shellcheck source=/dev/null
    source "$module"
done

log "Done"
