"""One-Time Interactive Session Initializer for Meta (Facebook & Instagram).
Opens Microsoft Edge in visible mode pointing to data/meta_session.
Log in once, and your session will be saved for fully automated headless scraping.
"""

import os
import sys
import time

SESSION_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "meta_session"))
os.makedirs(SESSION_DIR, exist_ok=True)

def main():
    print("=" * 70)
    print("  AIESEC EVENT RADAR - ONE-TIME META SESSION INITIALIZER")
    print("=" * 70)
    print(f"\nSession Directory: {SESSION_DIR}")
    print("\nLaunching Microsoft Edge in interactive mode...")
    print("Please log in to Facebook and/or Instagram.")
    print("Once logged in, you can close the browser window or press Enter here.\n")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Error: Playwright not installed. Run: pip install playwright")
        sys.exit(1)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            channel="msedge",
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--disable-blink-features=AutomationControlled"]
        )

        page = context.new_page()
        page.goto("https://www.facebook.com/events/")

        print("Browser is open. Waiting for you to log in...")
        print("Press ENTER in this terminal when finished logging in (or close the browser):")
        try:
            input()
        except (KeyboardInterrupt, EOFError):
            pass

        print("Saving session state and cookies...")
        context.close()
        print("\nDone! Session saved. Headless scraping is now 100% automated.")

if __name__ == "__main__":
    main()
