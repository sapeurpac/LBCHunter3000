# test_lbc.py - diagnostic rapide du scraper LBC Hunter 3000
import re, time, datetime, traceback
from playwright.sync_api import sync_playwright
import analyser

SEL_PRIX = 'div[data-qa-id="adview_price"], span[class*="price"]'
log = []
def w(msg):
    print(msg); log.append(str(msg))

w(f"=== Test LBC Hunter 3000 - {datetime.datetime.now():%Y-%m-%d %H:%M} ===")
try:
    with sync_playwright() as p:
        b = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        ctx = b.new_context(viewport={"width": 1366, "height": 768})
        ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        pg = ctx.new_page()
        r = pg.goto("https://www.leboncoin.fr/recherche?text=rtx%204070", wait_until="domcontentloaded", timeout=30000)
        try: pg.click("#didomi-notice-agree-button", timeout=3000); w("Cookies: bouton didomi OK")
        except Exception: w("Cookies: bouton didomi INTROUVABLE")
        time.sleep(3)
        w(f"Recherche: HTTP {r.status if r else '?'} | titre page = {pg.title()!r}")
        links = pg.locator('a[href*="/ad/"]').all()
        urls = []
        for l in links:
            h = l.get_attribute("href")
            if h:
                u = ("https://www.leboncoin.fr" + h if not h.startswith("http") else h).split("?")[0]
                if u not in urls: urls.append(u)
        w(f"Annonces trouvees (selecteur a[href*='/ad/']): {len(urls)}")
        nb_next = pg.locator('a[id*="next"], a[aria-label*="suivante"]').count()
        w(f"Bouton page suivante: {nb_next}")
        pg.screenshot(path="test_recherche.png")
        for u in urls[:3]:
            w(f"\n--- {u}")
            pg.goto(u, wait_until="domcontentloaded", timeout=15000); time.sleep(2)
            def get(sel):
                try: return pg.locator(sel).first.inner_text(timeout=1500).replace("\n", " ")[:120]
                except Exception: return None
            w(f"  titre (h1)      : {get('h1')}")
            w(f"  prix            : {get(SEL_PRIX)}")
            ville = pg.evaluate("() => { try { return JSON.parse(document.getElementById('__NEXT_DATA__').textContent).props.pageProps.ad.location.city_label } catch (e) { return null } }")
            w(f"  ville           : {ville}")
            d = get("div[data-qa-id='adview_description_container'] p")
            w(f"  description     : {d}")
            w(f"  specs extraites : {analyser.extract_specs(get('h1') or '', d or '')}")
        pg.screenshot(path="test_annonce.png")
        b.close()
except Exception:
    w("ERREUR:\n" + traceback.format_exc())

open("test_resultat.txt", "w", encoding="utf-8").write("\n".join(log))
w("\nResultat ecrit dans test_resultat.txt")
