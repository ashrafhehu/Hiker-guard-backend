import os
import time
import http.server
import socketserver
import threading
from playwright.sync_api import sync_playwright

PORT = 8089
DIRECTORY = os.path.abspath('.')

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_server():
    try:
        with ReusableTCPServer(("127.0.0.1", PORT), Handler) as httpd:
            httpd.serve_forever()
    except Exception as e:
        print("Server error:", e)

def capture():
    # Start local HTTP server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(1.5)

    url = f"http://127.0.0.1:{PORT}/AGAIF2026_BC1_CA3_MY-411_Muhammad%20Ashraf/index.html"
    out_dir = os.path.abspath("AGAIF2026_BC1_CA3_MY-411_Muhammad Ashraf/screenshots")
    os.makedirs(out_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 850})
        
        print(f"Navigating to {url}...")
        page.goto(url)
        page.wait_for_timeout(3500) # Allow Leaflet tiles & GeoJSON to render

        # 1. Screenshot: Overview
        img1 = os.path.join(out_dir, "map_overview.png")
        page.screenshot(path=img1)
        print(f"Captured: {img1}")

        # 2. Screenshot: Search Filter for Kuala Lumpur
        page.fill("#search-input", "Kuala Lumpur")
        page.wait_for_timeout(1500)
        img2 = os.path.join(out_dir, "map_filter_search.png")
        page.screenshot(path=img2)
        print(f"Captured: {img2}")

        # 3. Screenshot: Open popup card via helper
        page.evaluate("window.openPlacePopup('Kuala Lumpur')")
        page.wait_for_timeout(1500)
        img3 = os.path.join(out_dir, "map_popup_detail.png")
        page.screenshot(path=img3)
        print(f"Captured: {img3}")

        browser.close()

if __name__ == "__main__":
    capture()
