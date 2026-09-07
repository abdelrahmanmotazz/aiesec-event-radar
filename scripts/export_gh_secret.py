"""Export Facebook Authenticated Session for GitHub Actions Cloud Scraper.

Prints the base64-encoded storage state that you can paste into your
GitHub Repository Secrets as 'FB_STORAGE_STATE'.
"""

import base64
import json
import os
import sys

SESSION_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "meta_session"))
STATE_FILE = os.path.join(SESSION_DIR, "storage_state.json")

def main():
    print("=" * 70)
    print("  AIESEC EVENT RADAR - GITHUB ACTIONS CLOUD SECRET EXPORTER")
    print("=" * 70)

    if not os.path.exists(STATE_FILE):
        print("\nStorage state not found on disk. Generating from saved session...")
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=SESSION_DIR,
                    channel="msedge",
                    headless=True
                )
                context.storage_state(path=STATE_FILE)
                context.close()
        except Exception as e:
            print(f"Error generating storage state: {e}")
            sys.exit(1)

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    b64_val = base64.b64encode(content.encode("utf-8")).decode("ascii")

    print("\n[SUCCESS] Your Facebook authenticated session is ready for GitHub Actions!\n")
    print("To enable 100% automated daily cloud scraping on your live website:")
    print("1. Go to your GitHub repository:")
    print("   https://github.com/abdelrahmanmotazz/aiesec-event-radar/settings/secrets/actions")
    print("2. Click 'New repository secret'")
    print("3. Name: FB_STORAGE_STATE")
    print("4. Value: (Copy the text block below)\n")
    print("-" * 70)
    print(b64_val)
    print("-" * 70)
    print("\nGitHub Actions will now automatically use your Facebook account in the cloud")
    print("every morning at 5:00 AM Cairo time to scrape and update the live website!")

if __name__ == "__main__":
    main()
