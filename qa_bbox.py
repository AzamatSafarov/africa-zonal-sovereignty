import json
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8931/index.html"
out = {}
with sync_playwright() as p:
    br = p.chromium.launch(channel="msedge", headless=True)
    ctx = br.new_context(viewport={"width":1500,"height":1180})
    pg = ctx.new_page()
    errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(URL, wait_until="load"); pg.wait_for_timeout(4500)

    # рамка континента в пикселях проекции: проверяем, что все страны внутри viewBox
    out["bbox"] = pg.evaluate("""() => {
      const paths=[...document.querySelectorAll('#map .country')];
      let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;
      paths.forEach(p=>{
        let b;
        try{ b=p.getBBox(); }catch(e){ return; }
        x0=Math.min(x0,b.x); y0=Math.min(y0,b.y); x1=Math.max(x1,b.x+b.width); y1=Math.max(y1,b.y+b.height);
      });
      const svg=document.getElementById('map');
      return {minX:Math.round(x0),minY:Math.round(y0),maxX:Math.round(x1),maxY:Math.round(y1),
              vb:svg.getAttribute('viewBox'), count:paths.length};
    }""")
    out["errors"]=errs
    pg.screenshot(path="shot_fixed_map.png")
    pg.locator("#map").screenshot(path="shot_only_map.png")
    br.close()
print(json.dumps(out, ensure_ascii=False, indent=1))