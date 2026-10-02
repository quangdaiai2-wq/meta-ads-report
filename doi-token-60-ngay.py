"""
DOI TOKEN META NGAN HAN -> DAI HAN (60 NGAY)
=============================================
Token lay tu Graph API Explorer chi song 1-2 gio.
Script nay doi thanh token song 60 ngay.

CACH DUNG:
  1. Dan token ngan han vao file .env (dong META_ADS_ACCESS_TOKEN=...)
  2. Them 2 dong nay vao .env:
         META_APP_ID=...
         META_APP_SECRET=...
  3. Chay: python doi-token-60-ngay.py

Script se tu dong ghi token dai han tro lai vao .env (co backup).
"""
import json
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

API_VERSION = "v26.0"
ENV_PATH = Path(__file__).parent / ".env"


def load_env(path):
    env = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()
    return env


def update_env(path, updates):
    """Ghi de gia tri cua mot so key trong .env, giu nguyen cac dong khac."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    out = []
    done = set()
    for line in lines:
        stripped = line.strip()
        if "=" in stripped and not stripped.startswith("#"):
            key = stripped.partition("=")[0].strip()
            if key in updates:
                out.append(f"{key}={updates[key]}")
                done.add(key)
                continue
        out.append(line)
    # Key nao chua co thi them vao cuoi
    for key, value in updates.items():
        if key not in done:
            out.append(f"{key}={value}")
    Path(path).write_text("\n".join(out) + "\n", encoding="utf-8")


def main():
    if not ENV_PATH.exists():
        print("LOI: Khong tim thay file .env")
        sys.exit(1)

    env = load_env(ENV_PATH)
    short_token = env.get("META_ADS_ACCESS_TOKEN", "").strip()
    app_id = env.get("META_APP_ID", "").strip()
    app_secret = env.get("META_APP_SECRET", "").strip()

    # --- Kiem tra du thong tin chua ---
    missing = []
    if not short_token:
        missing.append("META_ADS_ACCESS_TOKEN (token ngan han vua lay)")
    if not app_id:
        missing.append("META_APP_ID")
    if not app_secret:
        missing.append("META_APP_SECRET")

    if missing:
        print("LOI: File .env con thieu cac muc sau:")
        for m in missing:
            print(f"  - {m}")
        print()
        print("Xem huong dan trong file HUONG-DAN-DIEN-TOKEN.md")
        sys.exit(1)

    print("Dang doi token...")
    print(f"  App ID    : {app_id}")
    print(f"  App Secret: {app_secret[:4]}...{app_secret[-4:]}")
    print(f"  Token cu  : {short_token[:12]}... ({len(short_token)} ky tu)")
    print()

    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_token,
    }
    url = f"https://graph.facebook.com/{API_VERSION}/oauth/access_token?" + urllib.parse.urlencode(params)

    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        try:
            err = json.loads(body).get("error", {})
            msg = err.get("message", body[:200])
        except Exception:
            msg = f"HTTP {e.code}"
        print(f"LOI: {msg}")
        print()
        print("Goi y kiem tra:")
        print("  - Token ngan han con hieu luc khong? (token chi song 1-2 gio)")
        print("  - META_APP_ID va META_APP_SECRET da dung chua?")
        print("  - App da bat che do Live chua? (Settings > Basic > App Mode)")
        sys.exit(1)
    except Exception as e:
        print(f"LOI ket noi: {e}")
        sys.exit(1)

    new_token = data.get("access_token")
    expires_in = data.get("expires_in")

    if not new_token:
        print("LOI: Meta khong tra ve token moi.")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        sys.exit(1)

    # --- Backup .env truoc khi ghi ---
    backup = ENV_PATH.parent / (ENV_PATH.name + ".bak")
    try:
        shutil.copy2(ENV_PATH, backup)
        print(f"Da sao luu file cu -> {backup.name}")
    except Exception as e:
        print(f"Canh bao: khong sao luu duoc ({e})")

    update_env(ENV_PATH, {"META_ADS_ACCESS_TOKEN": new_token})

    print()
    print("=" * 60)
    print("THANH CONG - DA DOI TOKEN DAI HAN")
    print("=" * 60)
    print(f"Token moi: {new_token[:12]}... ({len(new_token)} ky tu)")
    if expires_in:
        days = int(expires_in) // 86400
        het_han = datetime.now() + timedelta(seconds=int(expires_in))
        print(f"Song duoc : {days} ngay")
        print(f"Het han   : {het_han.strftime('%d/%m/%Y %H:%M')}")
    print()
    print("Token da duoc ghi tu dong vao file .env")
    print("Tu gio he thong chay bao cao binh thuong.")


if __name__ == "__main__":
    main()
