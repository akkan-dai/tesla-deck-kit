import sys,os
from playwright.sync_api import sync_playwright
deck=os.path.abspath(sys.argv[1])
bad=0
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":1920,"height":1080})
    pg.goto("file://"+deck); pg.wait_for_timeout(700)
    ids=pg.evaluate("DATA.slides.map(s=>s.id)")
    for i,sid in enumerate(ids):
        pg.evaluate("i=>{location.hash='#'+DATA.slides[i].id;}",i); pg.wait_for_timeout(90)
        r=pg.evaluate("""(sid)=>{const el=document.getElementById(sid);
          const s=el.querySelector('.src'), l=el.querySelector('.legend');
          if(!s) return null;
          const rg=document.createRange(); rg.selectNodeContents(s);
          const sr=rg.getBoundingClientRect();
          const lr=l?l.getBoundingClientRect():null;
          let bot=0; el.querySelectorAll('*').forEach(e=>{
            if(e.closest('.src')||e.closest('.legend')) return;
            if(!e.getClientRects().length) return;
            const tag=e.tagName.toLowerCase();
            const isMedia = (tag==='img'||tag==='svg');
            const hasText = e.children.length===0 && (e.textContent||'').trim().length>0;
            if(!isMedia && !hasText) return;
            const q=e.getBoundingClientRect(); if(q.bottom>bot)bot=q.bottom;});
          return {sx:sr.right, sy:sr.top, sb:sr.bottom, lx:lr?lr.left:null, ly:lr?lr.top:null, lb:lr?lr.bottom:null, bot:bot};}""",sid)
        if not r: continue
        m=[]
        if r["lx"] is not None and r["sx"]>r["lx"]-10 and r["sb"]>r["ly"] and r["sy"]<r["lb"]: m.append("src x legend")
        if r["bot"] and r["bot"]>r["sy"]-18: m.append("content x src (余白不足)")
        if m: bad+=1; print("  !! %s: %s (src right=%d, legend left=%s, content bottom=%d, src top=%d)"%(sid,", ".join(m),r["sx"],r["lx"],r["bot"],r["sy"]))
    b.close()
print("%s: %d issue(s)"%(os.path.basename(deck),bad))
