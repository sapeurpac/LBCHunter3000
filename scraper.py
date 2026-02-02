# scraper.py (Version RAPIDE / FAIL FAST)
import sys
import time
import random
import re
import urllib.parse
from playwright.sync_api import sync_playwright

import database
import analyser

MAX_PAGES = 3

def run_scraper(search_query):
    database.init_db()
    
    encoded_query = urllib.parse.quote(search_query)
    base_url = f"https://www.leboncoin.fr/recherche?text={encoded_query}"
    
    new_items_count = 0 
    
    with sync_playwright() as p:
        # Lancement simple
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(viewport={"width": 1366, "height": 768})
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = context.new_page()

        # OPTIMISATION : On bloque les images pour que ça charge très vite
        def intercept_route(route):
            if route.request.resource_type in ["image", "media", "font"]:
                route.abort()
            else:
                route.continue_()
        page.route("**/*", intercept_route)

        collected_urls = []

        try:
            # --- PHASE 1 : RECHERCHE ---
            page.goto(base_url, wait_until="domcontentloaded", timeout=30000)
            
            try: page.click("#didomi-notice-agree-button", timeout=2000)
            except: pass

            current_page = 1
            while current_page <= MAX_PAGES:
                # Scroll rapide
                for _ in range(2):
                    page.mouse.wheel(0, 1500)
                    time.sleep(0.5)

                links = page.locator('a[href*="/ad/"]').all()
                for link in links:
                    href = link.get_attribute("href")
                    if href:
                        full_url = "https://www.leboncoin.fr" + href.split('?')[0] if not href.startswith("http") else href.split('?')[0]
                        if full_url not in collected_urls:
                            collected_urls.append(full_url)
                
                next_btn = page.locator('a[id*="next"], a[aria-label*="suivante"]').last
                if next_btn.is_visible() and not next_btn.get_attribute("disabled"):
                    next_btn.click()
                    time.sleep(1)
                    current_page += 1
                else:
                    break
            
            # --- PHASE 2 : ANALYSE RAPIDE ---
            for i, url in enumerate(collected_urls):
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=15000)
                    # Pause courte (juste assez pour ne pas crash, mais rapide)
                    time.sleep(random.uniform(1.0, 1.5))

                    # FAIL FAST : On utilise des timeouts courts (500ms). 
                    # Si l'info n'est pas là tout de suite, on passe.
                    
                    try: titre = page.locator("h1").first.inner_text(timeout=500)
                    except: titre = "Inconnu"

                    try: 
                        p_text = page.locator('div[data-qa-id="adview_price"], span[class*="price"]').first.inner_text(timeout=500)
                        prix = int("".join(re.findall(r'\d+', p_text)))
                    except: prix = 0

                    try: ville = page.locator("div[class*='location']").first.inner_text(timeout=500).replace("\n", " ")
                    except: ville = "Inconnue"

                    try: description = page.locator("div[data-qa-id='adview_description_container'] p").inner_text(timeout=500)
                    except: description = ""

                    specs = analyser.extract_specs(titre, description)

                    # Petit filtre anti-déchet (pour éviter d'enregistrer les pages d'erreur 403)
                    forbidden_words = ["403", "forbidden", "access denied", "cloudflare"]
                    if any(w in titre.lower() for w in forbidden_words) or (titre == "Inconnu" and prix == 0):
                        continue

                    data = {
                        "url": url, "titre": titre, "prix": prix, "ville": ville,
                        "description": description, "specs": specs
                    }
                    
                    if database.save_annonce(data):
                         new_items_count += 1

                except Exception:
                    continue

        except Exception as e:
            sys.stderr.write(f"Erreur Scraper: {e}\n")
        finally:
            browser.close()
            
    return new_items_count

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = sys.argv[1]
        print(run_scraper(query))