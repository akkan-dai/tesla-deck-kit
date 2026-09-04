#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""png.py <deck.html> <outdir>
全スライドを 1920x1080 の PNG に書き出す。"""
import sys, os, re, io
from playwright.sync_api import sync_playwright

deck = os.path.abspath(sys.argv[1])
outdir = os.path.abspath(sys.argv[2])
os.makedirs(outdir, exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
    pg.goto("file://" + deck)
    pg.wait_for_timeout(800)
    ids = pg.evaluate("DATA.slides.map(s=>s.id)")
    # スケーリングを無効化して等倍で撮る
    pg.add_style_tag(content="#stageWrap{transform:none!important;left:0!important;top:0!important;position:static!important}"
                             "#hud,#grid{display:none!important}"
                             "#stage .slide{position:static!important;display:none}"
                             "#stage .slide.shot{display:flex!important;width:1920px!important;height:1080px!important}"
                             "#stage .slide.shot>.fit{width:100%!important;box-sizing:border-box!important}")
    for i, sid in enumerate(ids):
        pg.evaluate("""(sid)=>{
          document.querySelectorAll('#stage .slide').forEach(e=>e.classList.remove('shot'));
          document.getElementById(sid).classList.add('shot');
        }""", sid)
        pg.wait_for_timeout(140)
        el = pg.query_selector("#" + sid)
        out = os.path.join(outdir, "%02d_%s.png" % (i, sid))
        el.screenshot(path=out)
    b.close()

n = len([f for f in os.listdir(outdir) if f.endswith(".png")])
print("PNG: %d files -> %s" % (n, outdir))
