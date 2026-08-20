#!/bin/bash
#
# install.sh — DroneEngage Sound Module setup script
#
# Installs system dependencies (espeak-ng, alsa-utils, mpg123, ffmpeg),
# the Python dependency (colorama), and verifies everything is in place.
#
# Tested on Ubuntu / Debian / Raspberry Pi OS.
# Run with:  ./install.sh   (or)   bash install.sh
#
# Use --user to install the Python package into the user site instead of
# system-wide:  ./install.sh --user
#

set -e

# --- colors (plain ANSI so we don't depend on colorama yet) -----------------
RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
NC='\033[0m'

info()    { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()      { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
fail()    { echo -e "${RED}[FAIL]${NC}  $*"; exit 1; }

# --- parse args -------------------------------------------------------------
PIP_INSTALL_ARGS=""
if [ "$1" = "--user" ]; then
    PIP_INSTALL_ARGS="--user"
fi

# --- detect package manager -------------------------------------------------
PKG_MANAGER=""
if command -v apt-get >/dev/null 2>&1; then
    PKG_MANAGER="apt-get"
elif command -v dnf >/dev/null 2>&1; then
    PKG_MANAGER="dnf"
elif command -v yum >/dev/null 2>&1; then
    PKG_MANAGER="yum"
elif command -v pacman >/dev/null 2>&1; then
    PKG_MANAGER="pacman"
else
    warn "No supported package manager found (apt/dnf/yum/pacman)."
    warn "You will need to install system dependencies manually."
fi

# --- helper: install apt packages -------------------------------------------
install_apt() {
    info "Updating package list..."
    sudo apt-get update -y
    info "Installing: $*"
    sudo apt-get install -y "$@"
}

install_dnf() {
    info "Installing: $*"
    sudo dnf install -y "$@"
}

install_yum() {
    info "Installing: $*"
    sudo yum install -y "$@"
}

install_pacman() {
    info "Installing: $*"
    sudo pacman -S --noconfirm "$@"
}

sys_install() {
    case "$PKG_MANAGER" in
        apt-get) install_apt "$@" ;;
        dnf)     install_dnf "$@" ;;
        yum)     install_yum "$@" ;;
        pacman)  install_pacman "$@" ;;
        *)       warn "Cannot auto-install: $* — please install manually." ;;
    esac
}

# --- 1. System dependencies -------------------------------------------------
info "Checking system dependencies..."

MISSING_SYS=()

# espeak-ng — required for text-to-speech
if ! command -v espeak-ng >/dev/null 2>&1; then
    MISSING_SYS+=("espeak-ng")
else
    ok "espeak-ng found"
fi

# aplay (alsa-utils) — .wav playback
if ! command -v aplay >/dev/null 2>&1; then
    MISSING_SYS+=("alsa-utils")
else
    ok "aplay found (alsa-utils)"
fi

# mpg123 — .mp3 playback
if ! command -v mpg123 >/dev/null 2>&1; then
    MISSING_SYS+=("mpg123")
else
    ok "mpg123 found"
fi

# ffplay (ffmpeg) — fallback for .ogg and other formats
if ! command -v ffplay >/dev/null 2>&1; then
    MISSING_SYS+=("ffmpeg")
else
    ok "ffplay found (ffmpeg)"
fi

if [ ${#MISSING_SYS[@]} -gt 0 ]; then
    info "Installing missing system packages: ${MISSING_SYS[*]}"
    sys_install "${MISSING_SYS[@]}"
else
    ok "All system dependencies are already installed."
fi

# --- 2. Python dependency (colorama) ----------------------------------------
info "Checking Python dependencies..."

if ! python3 -c "import colorama" >/dev/null 2>&1; then
    info "Installing colorama..."
    pip3 install $PIP_INSTALL_ARGS colorama
else
    ok "colorama found"
fi

# --- 3. Optional: install the module itself ---------------------------------
if [ -f "setup.py" ]; then
    info "Installing de_sound_module package..."
    pip3 install $PIP_INSTALL_ARGS -e .
fi

# --- 4. Final verification --------------------------------------------------
info "Verifying installation..."

ALL_GOOD=1

for cmd in espeak-ng aplay mpg123 ffplay; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        warn "$cmd is still not on PATH"
        ALL_GOOD=0
    fi
done

if ! python3 -c "import colorama" >/dev/null 2>&1; then
    warn "colorama is still not importable"
    ALL_GOOD=0
fi

echo ""
if [ "$ALL_GOOD" -eq 1 ]; then
    ok "=============================================="
    ok "  DroneEngage Sound Module — ready to run!"
    ok "=============================================="
    echo ""
    echo "  Start the module with:"
    echo "    python3 de_sound_module.py"
    echo ""
    echo "  Or with a custom config:"
    echo "    python3 de_sound_module.py -c /path/to/de_snd.config.module.json"
    echo ""
else
    warn "Some dependencies are still missing. Check the warnings above."
    warn "You can still run the module — it will print install instructions"
    warn "for whatever is not found at startup."
fi
