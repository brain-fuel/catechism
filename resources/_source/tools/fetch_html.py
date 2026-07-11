import os, time
from playwright.sync_api import sync_playwright

URL = "https://chatgpt.com/share/6a518709-9160-83ea-ae50-ef486c0bca53"
chrome = os.path.expanduser("~/.cache/ms-playwright/chromium-1181/chrome-linux/chrome")

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path=chrome, args=["--no-sandbox"])
    pg = b.new_context(user_agent=("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
         "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")).new_page()
    pg.goto(URL, wait_until="networkidle", timeout=60000)
    pg.wait_for_timeout(3000)
    html = pg.content()
    open("share.html", "w", encoding="utf-8").write(html)
    # try known SSR data hooks
    for var in ["__NEXT_DATA__", "window.__remixContext", "__reactRouterContext"]:
        try:
            v = pg.evaluate(f"() => {{ try{{return JSON.stringify(eval('{var}'))}}catch(e){{return null}} }}")
            if v:
                open(f"data_{var.strip('_').replace('window.','').replace('.','_')}.json","w",encoding="utf-8").write(v)
                print("captured", var, len(v))
        except Exception as e:
            print("miss", var, e)
    print("html chars:", len(html))
    b.close()
