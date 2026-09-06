"""Arkose-Safe Interactive Session Initializer for Meta (Facebook & Instagram).
Launches genuine Microsoft Edge directly without automation flags or CDP hooks.
This prevents Arkose Labs MatchKey / 2FA from detecting automation and freezing on a white screen.
"""

import os
import subprocess
import sys

SESSION_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "meta_session"))
os.makedirs(SESSION_DIR, exist_ok=True)

EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

def get_edge_path():
    for p in EDGE_PATHS:
        if os.path.exists(p):
            return p
    return "msedge.exe"

def main():
    edge_exe = get_edge_path()
    print("=" * 70)
    print("  AIESEC EVENT RADAR - GENUINE EDGE FACEBOOK LOGIN (ARKOSE-SAFE)")
    print("=" * 70)
    print(f"\nTarget Session Directory: {SESSION_DIR}")
    print(f"Edge Binary: {edge_exe}")
    print("\nLaunching genuine Microsoft Edge natively (Zero automation flags)...")
    print("1. Log in to Facebook in the Edge window that opens.")
    print("2. Complete any two-step verification / security checks normally.")
    print("3. Once your Facebook Events feed loads, come back here and press ENTER.\n")

    cmd = [
        edge_exe,
        f"--user-data-dir={SESSION_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
        "https://www.facebook.com/events/"
    ]

    try:
        proc = subprocess.Popen(cmd)
        print("Edge is open. Waiting for you to complete login...")
        print("Press ENTER in this terminal when finished logging in:")
        try:
            input()
        except (KeyboardInterrupt, EOFError):
            pass

        print("\nSession saved securely in data/meta_session! Headless scraping is now ready.")
    except Exception as e:
        print(f"Error launching Edge: {e}")

if __name__ == "__main__":
    main()
