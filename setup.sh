#!/usr/bin/env bash
set -e
BASE="https://raw.githubusercontent.com/akkan-dai/tesla-deck-kit/main"
DIR="${1:-/home/claude/w}"
mkdir -p "$DIR"
cd "$DIR"
for f in _TEMPLATE_deck_ja.html _TEMPLATE_deck_en.html build.py count.py inject.py verify.py png.py overlap.py validate_json.py data_test.js HANDOFF.md; do
  curl -fsSL "$BASE/$f" -o "$f"
  printf '  ok %s\n' "$f"
done
mkdir -p "$DIR/img"
python3 - <<'PY'
try:
    from playwright.sync_api import sync_playwright
    print("playwright: ready")
except Exception:
    print("playwright: 未導入。pip install playwright --break-system-packages を実行してください")
PY
echo "setup done -> $DIR"
