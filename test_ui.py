from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    def handle_console(msg):
        print(f"BROWSER CONSOLE: {msg.type} - {msg.text}")

    def handle_error(err):
        print(f"BROWSER ERROR: {err.message}")

    page.on("console", handle_console)
    page.on("pageerror", handle_error)

    print("Navigating to http://127.0.0.1:8000")
    page.goto("http://127.0.0.1:8000")
    page.wait_for_timeout(2000)

    device_html = page.locator('#device-list').inner_html()
    print("DEVICE LIST HTML:")
    print(device_html)

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
