#!/usr/bin/env bash
# Fetch and build drat-trim, the independent DRAT proof checker used to verify
# every UNSAT answer this project relies on. MIT licensed (Heule & Wetzler).
# Not vendored: the checker must be a third-party artifact for the verification
# argument to mean anything.
set -euo pipefail
DEST="${1:-$(dirname "$0")/drat-trim}"
if [ -x "$DEST/drat-trim" ]; then echo "already built: $DEST/drat-trim"; exit 0; fi
rm -rf "$DEST"
git clone -q --depth 1 https://github.com/marijnheule/drat-trim.git "$DEST"
( cd "$DEST" && gcc -O2 -o drat-trim drat-trim.c )
echo "built: $DEST/drat-trim"
"$DEST/drat-trim" 2>&1 | head -2 || true
