#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tc.py <script.md> ja|en
台本の各 ## Sxx にタイムコードを付け直す。既存のタイムコードは上書きする。
日本語335字/分、英語152wpm。"""
import sys, io, re

path, lang = sys.argv[1], sys.argv[2]
s = io.open(path, encoding="utf-8").read()
s = re.sub(r"^## \[(S\d+)\][^\n]*?[　 ]{1,2}", lambda m: "## %s " % m.group(1), s, flags=re.M)

blocks, cur, buf = [], None, []
for ln in s.split("\n"):
    m = re.match(r"^## (S\d+)", ln)
    if m:
        if cur: blocks.append((cur, "\n".join(buf)))
        cur, buf = m.group(1), []
        continue
    if cur is not None: buf.append(ln)
if cur: blocks.append((cur, "\n".join(buf)))

def mmss(x):
    t = int(round(x))
    return "%d:%02d" % (t // 60, t % 60)

t, tc = 0.0, {}
for bid, body in blocks:
    b = re.sub(r"^\s*[#>|\-*].*$", "", body, flags=re.M)
    if lang == "en":
        n = len(re.findall(r"[A-Za-z0-9'’\-]+", b)); d = n / 152.0 * 60
    else:
        n = len(re.sub(r"\s", "", b)); d = n / 335.0 * 60
    tc[bid] = "%s-%s" % (mmss(t), mmss(t + d))
    t += d

sep = "  " if lang == "en" else "　"
s = re.sub(r"^## (S\d+)(.*)$",
           lambda m: "## [%s] %s%s%s" % (m.group(1), tc[m.group(1)], sep, m.group(2).strip()),
           s, flags=re.M)
io.open(path, "w", encoding="utf-8").write(s)
print("TOTAL " + mmss(t))
for k, v in tc.items(): print("  %-4s %s" % (k, v))
