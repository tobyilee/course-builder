#!/usr/bin/env bash
# Render slide.source.md → slide.html using Marp CLI.
# Usage: render-marp.sh <class_dir>
# Exits non-zero on render error.

set -euo pipefail

CLASS_DIR="${1:?Usage: render-marp.sh <class_dir>}"
SRC="$CLASS_DIR/slide.source.md"
OUT="$CLASS_DIR/slide.html"

if [ ! -f "$SRC" ]; then
  echo "ERROR: $SRC not found" >&2
  exit 2
fi

if ! command -v marp >/dev/null 2>&1; then
  echo "ERROR: marp CLI not found. Install: npm install -g @marp-team/marp-cli" >&2
  exit 3
fi

marp --html --allow-local-files "$SRC" -o "$OUT" 2>&1
echo "OK: rendered $OUT"
