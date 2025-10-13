import sys
import time
from playwright.sync_api import sync_playwright

def take_screenshot(url, output_path, width=1920, height=1480):
    """
    Launches a browser, navigates to a URL, and saves a screenshot.
    This function is designed to be called from the command line.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_viewport_size({"width": width, "height": height})
            page.goto(url)
            time.sleep(5)
            page.screenshot(path=output_path)
            browser.close()
        print(f"Screenshot saved successfully to {output_path}")
    except Exception as e:
        print(f"An error occurred in Playwright: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) !=5 :
        print("Usage: python screenshot_script.py <URL> <output_path> [width] [height]", file=sys.stderr)
        sys.exit(1)
    
    url_arg = sys.argv[1]
    path_arg = sys.argv[2]
    width_arg = sys.argv[3]
    height_arg = sys.argv[4]
    
    take_screenshot(url_arg, path_arg, width_arg, height_arg)