"""Export & Auto-Upload Facebook Authenticated Session and Gemini API Key to GitHub Actions Secrets.

1. Encodes data/meta_session/storage_state.json as base64.
2. Automatically uploads FB_STORAGE_STATE (and GEMINI_API_KEY if present) directly
   to GitHub Repository Secrets using your git credentials + PyNaCl sealed-box encryption.
3. Also copies FB_STORAGE_STATE to the Windows clipboard as a backup.
"""

import argparse
import base64
import os
import subprocess
import sys
from typing import Optional

SESSION_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "meta_session"))
STATE_FILE = os.path.join(SESSION_DIR, "storage_state.json")
REPO_SLUG = "abdelrahmanmotazz/aiesec-event-radar"


def get_github_token() -> Optional[str]:
    """Retrieve the authenticated GitHub token from git credential manager."""
    if os.getenv("GITHUB_TOKEN"):
        return os.getenv("GITHUB_TOKEN")
    try:
        proc = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            text=True,
            capture_output=True,
            timeout=5,
        )
        creds = dict(
            line.split("=", 1)
            for line in proc.stdout.splitlines()
            if "=" in line
        )
        return creds.get("password")
    except Exception:
        return None


def upload_github_secret(secret_name: str, secret_value: str, token: str) -> bool:
    """Encrypt and upload a secret directly to GitHub Actions Secrets via REST API."""
    try:
        import requests
        from nacl import encoding, public

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        pk_url = f"https://api.github.com/repos/{REPO_SLUG}/actions/secrets/public-key"
        pk_resp = requests.get(pk_url, headers=headers, timeout=10)
        if pk_resp.status_code != 200:
            return False
        pk_data = pk_resp.json()

        public_key = public.PublicKey(pk_data["key"].encode("utf-8"), encoding.Base64Encoder())
        sealed_box = public.SealedBox(public_key)
        encrypted = base64.b64encode(sealed_box.encrypt(secret_value.encode("utf-8"))).decode("utf-8")

        put_url = f"https://api.github.com/repos/{REPO_SLUG}/actions/secrets/{secret_name}"
        put_resp = requests.put(
            put_url,
            headers=headers,
            json={"encrypted_value": encrypted, "key_id": pk_data["key_id"]},
            timeout=10,
        )
        return put_resp.status_code in (201, 204)
    except Exception as exc:
        print(f"Auto-upload notice for {secret_name}: {exc}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Export and auto-upload GitHub Actions secrets.")
    parser.add_argument("--gemini-key", help="Optional Gemini API Key to upload to GEMINI_API_KEY secret.")
    args = parser.parse_args()

    print("=" * 70)
    print("  AIESEC EVENT RADAR - GITHUB ACTIONS CLOUD SECRET AUTO-UPLOADER")
    print("=" * 70)

    if not os.path.exists(STATE_FILE):
        print("\nStorage state not found on disk. Generating from saved session...")
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=SESSION_DIR,
                    channel="msedge",
                    headless=True,
                )
                context.storage_state(path=STATE_FILE)
                context.close()
        except Exception as e:
            print(f"Error generating storage state: {e}")
            sys.exit(1)

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    b64_val = base64.b64encode(content.encode("utf-8")).decode("ascii")

    # Copy to Windows clipboard
    try:
        subprocess.run("clip", input=b64_val, text=True, check=True)
        print("\n[OK] Copied FB_STORAGE_STATE to Windows clipboard.")
    except Exception:
        pass

    token = get_github_token()
    if token:
        if upload_github_secret("FB_STORAGE_STATE", b64_val, token):
            print(f"[SUCCESS] Automatically uploaded FB_STORAGE_STATE to GitHub Secret ({REPO_SLUG})!")
        else:
            print("[INFO] Could not auto-upload FB_STORAGE_STATE via API; use clipboard paste instead.")

        gemini_key = args.gemini_key or os.getenv("GEMINI_API_KEY")
        if gemini_key:
            if upload_github_secret("GEMINI_API_KEY", gemini_key.strip(), token):
                print(f"[SUCCESS] Automatically uploaded GEMINI_API_KEY to GitHub Secret ({REPO_SLUG})!")
    else:
        print("[INFO] No git token found for auto-upload. Paste from clipboard to GitHub Secrets.")


if __name__ == "__main__":
    main()
