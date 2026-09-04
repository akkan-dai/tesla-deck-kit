#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""inject.py <deck.html> [imgdir]
imgdir(既定 /home/claude/img)の画像を base64 データURIにして const IMAGES に注入する。
DATA の img キーで参照されているものだけを入れる。"""
import sys, io, os, re, base64, json

deck_p = sys.argv[1]
imgdir = sys.argv[2] if len(sys.argv) > 2 else "/home/claude/img"

html = io.open(deck_p, encoding="utf-8").read()
used = set(re.findall(r'img\s*:\s*"([^"]+)"', html))

MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
imgs, missing = {}, []
for name in sorted(used):
    hit = None
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        p = os.path.join(imgdir, name + ext)
        if os.path.exists(p):
            hit = (p, ext); break
    if not hit:
        missing.append(name); continue
    p, ext = hit
    b = base64.b64encode(io.open(p, "rb").read()).decode("ascii")
    imgs[name] = "data:%s;base64,%s" % (MIME[ext], b)
    print("  + %-8s %s (%.0f KB)" % (name, os.path.basename(p), os.path.getsize(p) / 1024.0))

if missing:
    print("  !! 画像が見つかりません: %s" % ", ".join(missing))

body = json.dumps(imgs, ensure_ascii=False)
new = "const IMAGES = " + body + ";"
html2, n = re.subn(r"const IMAGES = \{.*?\};", lambda m: new, html, count=1, flags=re.S)
if n == 0:
    print("!! const IMAGES が見つかりません"); sys.exit(1)
io.open(deck_p, "w", encoding="utf-8").write(html2)
print("injected: %s (%d images, %.1f MB)" % (deck_p, len(imgs), len(html2) / 1048576.0))
