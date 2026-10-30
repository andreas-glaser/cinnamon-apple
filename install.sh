#!/usr/bin/env bash
# Makes Linux Mint Cinnamon behave more like macOS. Run with --help for usage.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=lib.sh
source "$ROOT/lib.sh"
# shellcheck source=config.sh
source "$ROOT/config.sh"

usage() {
    cat <<'EOF'
Usage: ./install.sh            describe each module and ask which to set up
       ./install.sh --all      set up every module without asking
       ./install.sh NAME...    set up only the named module(s)
       ./install.sh --list     list the modules and what they do
EOF
}

# A module's description is the comment block at the top of its file.
describe() {
    awk '/^#/ { sub(/^# ?/, "    "); print; next } { exit }' "$1"
}

module_name() {
    basename "$1" .sh
}

# Usage: ask <question>; succeeds on yes, which is also the default.
ask() {
    local reply
    while true; do
        read -r -p "$1 [Y/n] " reply || { echo; return 1; }
        case ${reply,,} in
            "" | y | yes) return 0 ;;
            n | no) return 1 ;;
        esac
    done
}

if [[ $EUID -eq 0 ]]; then
    echo "Run as your normal user, not root; sudo is used where needed." >&2
    exit 1
fi

available=("$ROOT"/modules/*.sh)
modules=()
interactive=false
case ${1:-} in
    -h | --help)
        usage
        exit 0
        ;;
    --list)
        for module in "${available[@]}"; do
            printf '\033[1m%s\033[0m\n' "$(module_name "$module")"
            describe "$module"
        done
        exit 0
        ;;
    --all)
        (($# == 1)) || { usage >&2; exit 1; }
        modules=("${available[@]}")
        ;;
    -*)
        usage >&2
        exit 1
        ;;
    "")
        if [[ ! -t 0 ]]; then
            echo "No terminal to ask in; pass --all or module names (see --list)." >&2
            exit 1
        fi
        interactive=true
        ;;
    *)
        for name in "$@"; do
            module="$ROOT/modules/$name.sh"
            [[ -f $module ]] || { echo "No such module: $name (see --list)" >&2; exit 1; }
            modules+=("$module")
        done
        ;;
esac

if $interactive; then
    echo "Each module changes one part of the desktop. Answer y to set it up, n to skip."
    for module in "${available[@]}"; do
        printf '\n\033[1m%s\033[0m\n' "$(module_name "$module")"
        describe "$module"
        if ask "Set up $(module_name "$module")?"; then
            modules+=("$module")
        fi
    done
    echo
    if ((${#modules[@]} == 0)); then
        echo "Nothing selected."
        exit 0
    fi
    names=()
    for module in "${modules[@]}"; do
        names+=("$(module_name "$module")")
    done
    echo "Will set up: ${names[*]}"
    echo "Missing packages are installed with sudo, so you may be asked for your password."
    ask "Continue?" || exit 0
fi

current=""
trap 'status=$?; if ((status != 0)) && [[ -n $current ]]; then
    echo "Module $current failed; the modules before it are set up. Fix the error and re-run it with ./install.sh $current" >&2
fi' EXIT

# Modules change the shortcuts the toggle saved; restore them first so turning
# it back on later does not undo this run.
if [[ -f ${XDG_STATE_HOME:-$HOME/.local/state}/cinnamon-apple/mac-keyboard.json ]]; then
    log "Turning the Mac shortcuts back on"
    "$ROOT/files/cinnamon-apple-toggle" on
fi

done_names=()
for i in "${!modules[@]}"; do
    module=${modules[$i]}
    current=$(module_name "$module")
    log "[$((i + 1))/${#modules[@]}] $current"
    # shellcheck source=/dev/null
    source "$module"
    done_names+=("$current")
done
current=""

log "Done: ${done_names[*]}"
