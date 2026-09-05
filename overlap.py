#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""overlap.py <deck.html>
全スライドを1枚ずつ実描画して、重なりとはみ出しを検出する。
検出: 出典×凡例の衝突 / 本文が出典に近すぎる / 横のはみ出し / 縦1080pxの超過
注意: ハッシュ遷移だけではスライドが display:none のままなので、
      png.py と同じ方式で .shot クラスを当てて強制的に描画する。"""
import sys, os
from playwright.sync_api import sync_playwright

deck = os.path.abspath(sys.argv[1])
bad = 0
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1920, "height": 1080})
    pg.goto("file://" + deck)
    pg.wait_for_timeout(700)
    ids = pg.evaluate("DATA.slides.map(s=>s.id)")
    types = pg.evaluate("DATA.slides.map(s=>s.type)")
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
        pg.wait_for_timeout(120)
        r = pg.evaluate("""(sid)=>{
          const el=document.getElementById(sid);
          const s=el.querySelector('.src'), l=el.querySelector('.legend'), fit=el.querySelector('.fit')||el;
          if(!s) return null;
          const rg=document.createRange(); rg.selectNodeContents(s);
          const sr=rg.getBoundingClientRect();
          const lr=l?l.getBoundingClientRect():null;
          let bot=0, who='';
          el.querySelectorAll('*').forEach(e=>{
            if(e.closest('.src')||e.closest('.legend')) return;
            if(!e.getClientRects().length) return;
            const tag=e.tagName.toLowerCase();
            const isMedia=(tag==='img'||tag==='svg');
            const hasText=e.children.length===0 && (e.textContent||'').trim().length>0;
            if(!isMedia && !hasText) return;
            const q=e.getBoundingClientRect();
            if(q.bottom>bot){bot=q.bottom; who=tag+'.'+(e.className||'');}
          });
          const fr=fit.getBoundingClientRect();
          let over=0, ow='';
          el.querySelectorAll('*').forEach(e=>{
            if(!e.getClientRects().length) return;
            const q=e.getBoundingClientRect();
            if(q.right>fr.right+2 && q.right-fr.right>over){over=q.right-fr.right; ow=e.tagName.toLowerCase()+'.'+(e.className||'');}
          });
          return {over:Math.round(over), ow:ow, sx:sr.right, sy:sr.top, sb:sr.bottom,
                  lx:lr?lr.left:null, ly:lr?lr.top:null, lb:lr?lr.bottom:null,
                  bot:bot, who:who, h:fit.offsetHeight};}""", sid)
        if not r:
            print("  !! %s: .src が見つかりません" % sid); bad += 1; continue
        if r["h"] == 0:
            print("  !! %s: 描画されていません（測定不能）" % sid); bad += 1; continue
        m = []
        if r["lx"] is not None and r["sx"] > r["lx"] - 28 and r["sb"] > r["ly"] and r["sy"] < r["lb"]:
            m.append("出典×凡例")
        if r["bot"] and r["bot"] > r["sy"] - 18:
            m.append("本文×出典 (%s が %dpx まで、出典の上端は %dpx)" % (r["who"], r["bot"], r["sy"]))
        if r.get("over", 0) > 4:
            m.append("横にはみ出し %dpx (%s)" % (r["over"], r["ow"]))
        if r["h"] > 1080:
            m.append("縦にはみ出し %dpx" % r["h"])
        if m:
            bad += 1
            print("  !! %s (%s): %s" % (sid, types[i], " / ".join(m)))
    b.close()
print("%s: %d 件" % (os.path.basename(deck), bad))
sys.exit(1 if bad else 0)
