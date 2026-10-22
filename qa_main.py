import json, sys
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8931/index.html"
out = {"errors": [], "console": [], "checks": {}}

with sync_playwright() as p:
    br = p.chromium.launch(channel="msedge", headless=True)
    ctx = br.new_context(viewport={"width":1440,"height":1000})
    pg = ctx.new_page()
    pg.on("console", lambda m: out["console"].append(m.type+": "+m.text) if m.type in ("error","warning") else None)
    pg.on("pageerror", lambda e: out["errors"].append(str(e)))
    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(5000)

    out["checks"] = pg.evaluate("""() => ({
      title: document.title,
      land: document.querySelectorAll('#map path.land').length,
      countries: document.querySelectorAll('#map path.country').length,
      edges: document.querySelectorAll('#map path.edge').length,
      edgeWithD: Array.from(document.querySelectorAll('#map path.edge')).filter(e=>e.getAttribute('d')).length,
      dots: document.querySelectorAll('#map circle.hubdot').length,
      cases: document.querySelectorAll('#caseList .case').length,
      roles: document.querySelectorAll('#rolesPane .case').length,
      waveBars: document.querySelectorAll('#waveChart rect').length,
      bigyear: document.getElementById('bigyear').textContent,
      conf: document.getElementById('confCounts').textContent,
      fill2026: Array.from(document.querySelectorAll('#map path.country')).slice(0,8).map(e=>e.getAttribute('fill')),
      overflow: document.documentElement.scrollWidth > window.innerWidth + 2
    })""")

    pg.eval_on_selector("#slider", "el => { el.value=2021; el.dispatchEvent(new Event('input',{bubbles:true})); }")
    pg.wait_for_timeout(900)
    out["checks"]["year_2021"] = pg.text_content("#bigyear")
    out["checks"]["cases_2021"] = pg.eval_on_selector_all("#caseList .case", "els=>els.length")
    out["checks"]["fill2021"] = pg.evaluate("Array.from(document.querySelectorAll('#map path.country')).slice(0,8).map(e=>e.getAttribute('fill'))")

    pg.eval_on_selector("#slider", "el => { el.value=2013; el.dispatchEvent(new Event('input',{bubbles:true})); }")
    pg.wait_for_timeout(900)
    out["checks"]["year_2013"] = pg.text_content("#bigyear")
    out["checks"]["cases_2013"] = pg.eval_on_selector_all("#caseList .case", "els=>els.length")
    out["checks"]["dots_2013"] = pg.eval_on_selector_all("#map circle.hubdot","els=>els.length")

    pg.evaluate("selectCountry('NG')")
    pg.wait_for_timeout(500)
    out["checks"]["country_pane_head"] = pg.eval_on_selector("#countryPane","el=>el.innerText.slice(0,140)")

    pg.click(".tabs button[data-pane='roles']"); pg.wait_for_timeout(300)
    out["checks"]["roles_display"] = pg.eval_on_selector("#pane-roles","el=>getComputedStyle(el).display")
    pg.click(".tabs button[data-pane='method']"); pg.wait_for_timeout(300)
    out["checks"]["method_display"] = pg.eval_on_selector("#pane-method","el=>getComputedStyle(el).display")

    pg.screenshot(path="shot_1440.png")
    br.close()

print(json.dumps(out, ensure_ascii=False, indent=1))