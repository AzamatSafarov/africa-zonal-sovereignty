import json
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8931/index.html"
out = {"errors": [], "vp": {}}

with sync_playwright() as p:
    br = p.chromium.launch(channel="msedge", headless=True)
    for w,h,name in [(1440,1000,"d1440"),(390,844,"m390"),(320,700,"m320")]:
        ctx = br.new_context(viewport={"width":w,"height":h})
        pg = ctx.new_page()
        pg.on("pageerror", lambda e, n=name: out["errors"].append(f"{n}: {e}"))
        pg.goto(URL, wait_until="load")
        pg.wait_for_timeout(4000)
        out["vp"][name] = pg.evaluate("""() => ({
          sw: document.documentElement.scrollWidth,
          iw: window.innerWidth,
          overflow: document.documentElement.scrollWidth > window.innerWidth + 2,
          countries: document.querySelectorAll('#map .country').length,
          edges: document.querySelectorAll('#map path.edge').length,
          mapBox: (()=>{const b=document.querySelector('#map').getBoundingClientRect();return [Math.round(b.width),Math.round(b.height)];})(),
          caseCards: document.querySelectorAll('#caseList .case').length
        })""")
        pg.screenshot(path=f"shot_{name}.png", full_page=False)
        ctx.close()
    br.close()

print(json.dumps(out, ensure_ascii=False, indent=1))