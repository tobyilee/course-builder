#!/usr/bin/env bash
# Validate a .ssml file against basic W3C SSML 1.1 structural rules.
# This is a lightweight validator using xmllint (no remote XSD fetch).
# Usage: validate-ssml.sh <file.ssml>

set -euo pipefail

FILE="${1:?Usage: validate-ssml.sh <file.ssml>}"

if [ ! -f "$FILE" ]; then
  echo "ERROR: $FILE not found" >&2
  exit 2
fi

if ! command -v xmllint >/dev/null 2>&1; then
  echo "WARN: xmllint not available, skipping deep validation" >&2
  # Minimal grep-based sanity check
  grep -q '<speak' "$FILE" || { echo "ERROR: missing <speak> root" >&2; exit 3; }
  grep -q 'xml:lang' "$FILE" || { echo "ERROR: missing xml:lang" >&2; exit 3; }
  echo "OK (shallow): $FILE"
  exit 0
fi

# Well-formedness
xmllint --noout "$FILE" 2>&1 || { echo "ERROR: not well-formed XML" >&2; exit 4; }

# Structural checks
if ! grep -q '<speak[^>]*xmlns="http://www.w3.org/2001/10/synthesis"' "$FILE"; then
  echo "ERROR: missing SSML namespace on <speak>" >&2
  exit 5
fi

if ! grep -q 'xml:lang=' "$FILE"; then
  echo "ERROR: missing xml:lang attribute" >&2
  exit 6
fi

echo "OK: $FILE"
