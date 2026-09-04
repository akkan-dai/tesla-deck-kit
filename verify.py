#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify.py <deck.html>
全スライドを実描画して不具合を検出する。
検出: undefined / [object Object] / NaN / %% / はみ出し / 英語デッキ内の日本語
注意: 「書いたのに表示されない」は検出できない。新しい型を使うときはPNGを目視すること。"""
import sys, io, re, os
from playwright.sync_api import sync_playwright

deck = os.path.abspath(sys.argv[1])
src = io.open(deck, encoding="utf-8").read()
LANG = "en" if re.search(r'const LANG\s*=\s*"en"', src) else "ja"
BAD = ["undefined", "[object Object]", "NaN", "%%"]
JP = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff\u30fb\uff01-\uff60\u3000-\u303f]")

errs, warns = [], []
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1920, "height": 1080})
    pg.goto("file://" + deck)
    pg.wait_for_timeout(700)
    ids = pg.evaluate("DATA.slides.map(s=>s.id)")
    types = pg.evaluate("DATA.slides.map(s=>s.type)")
    print("slides: %d  LANG=%s" % (len(ids), LANG))

    for i, sid in enumerate(ids):
        pg.evaluate("i=>{location.hash='#'+DATA.slides[i].id;}", i)
        pg.wait_for_timeout(120)
        info = pg.evaluate("""(sid)=>{
          const el=document.getElementById(sid);
          if(!el) return null;
          const fit=el.querySelector('.fit')||el;
          return {text: el.innerText, h: fit.offsetHeight, w: fit.offsetWidth};
        }""", sid)
        if not info:
            errs.append("%s: スライド要素が見つからない" % sid); continue
        t = info["text"]
        for badstr in BAD:
            if badstr in t:
                errs.append("%s (%s): '%s' が表示されている" % (sid, types[i], badstr))
        if info["h"] > 1080:
            errs.append("%s (%s): 縦にはみ出し %dpx (>1080)" % (sid, types[i], info["h"]))
        if LANG == "en":
            jp = JP.findall(t)
            if jp:
                warns.append("%s (%s): 英語デッキに日本語 %s" % (sid, types[i], "".join(sorted(set(jp)))[:40]))
    b.close()

print("-" * 50)
for e in errs: print("ERROR  " + e)
for w in warns: print("WARN   " + w)
if not errs and not warns:
    print("OK  問題は検出されませんでした")
print("-" * 50)
sys.exit(1 if errs else 0)
