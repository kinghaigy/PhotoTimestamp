#!/usr/bin/env bash
# Run Linux and Mac.sh — stamp photos with date and children's ages.
# Place this file next to photo_timestamp.py.
# Put your photos in a folder called 'photos' in the same directory.
# Edit the CHILDREN line below to match your kids' names and dates of birth.
# Double-click or run with:  bash "Run Linux and Mac.sh"

# ── Configuration ────────────────────────────────────────────────────────────
CHILDREN=(
    "ChildName1=YYYY-MM-DD"
    "ChildName2=YYYY-MM-DD"
)
# ─────────────────────────────────────────────────────────────────────────────

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PHOTOS_DIR="$SCRIPT_DIR/photos"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON="$VENV_DIR/bin/python"

if [ ! -d "$PHOTOS_DIR" ]; then
    echo "ERROR: No 'photos' folder found next to this script."
    echo "Create a folder called 'photos' and put your images in it."
    read -p "Press Enter to exit..."
    exit 1
fi

# Create virtual environment if it doesn't exist yet
if [ ! -f "$PYTHON" ]; then
    echo "Creating Python environment (first run only)..."
    python3 -m venv "$VENV_DIR"
fi

# Always ensure dependencies are installed / up to date
echo "Checking dependencies..."
"$VENV_DIR/bin/pip" install --quiet -r "$SCRIPT_DIR/requirements.txt"

# Update the .desktop icon path to match this machine's location
DESKTOP_FILE="$SCRIPT_DIR/Stamp Photos.desktop"
if [ -f "$DESKTOP_FILE" ]; then
    sed -i "s|^Icon=.*|Icon=$SCRIPT_DIR/icon.svg|" "$DESKTOP_FILE"
fi

# Forward --overwrite if passed to this script
EXTRA_ARGS=""
for arg in "$@"; do
    if [ "$arg" = "--overwrite" ]; then
        EXTRA_ARGS="--overwrite"
    fi
done

echo "Stamping photos..."
"$PYTHON" "$SCRIPT_DIR/photo_timestamp.py" "$PHOTOS_DIR" --children "${CHILDREN[@]}" $EXTRA_ARGS

echo ""
echo "Finished! Stamped images are in: ${PHOTOS_DIR}_stamped"
read -p "Press Enter to exit..."
