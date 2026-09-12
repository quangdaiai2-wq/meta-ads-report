"""
Script kiem tra ket noi Meta Ads API.
Chi doc token tu file .env, khong in token ra man hinh.
"""
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API_VERSION = "v21.0"
BASE = f"https://graph.facebook.com/{API_VERSION}"


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


def call_api(path, params):
    url = f"{BASE}/{path}?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        try:
            return None, json.loads(body).get("error", {})
        except Exception:
            return None, {"message": f"HTTP {e.code}: {body[:200]}"}
    except Exception as e:
        return None, {"message": str(e)}


def main():
    env_path = Path(__file__).parent / ".env"
    env = load_env(env_path)
    token = env.get("META_ADS_ACCESS_TOKEN", "")
    account = env.get("META_AD_ACCOUNT_ID", "")

    print("=" * 60)
    print("KIEM TRA KET NOI META ADS API")
    print("=" * 60)
    print(f"Token    : {len(token)} ky tu, bat dau '{token[:4]}...'")
    print(f"Account  : {account} ({len(account)} ky tu)")
    print()

    if not token:
        print("LOI: Thieu META_ADS_ACCESS_TOKEN")
        sys.exit(1)

    # --- Buoc 1: Kiem tra token co hop le khong ---
    print("[1/3] Kiem tra token con hieu luc...")
    data, err = call_api("me", {"access_token": token, "fields": "id,name"})
    if err:
        print(f"    LOI: {err.get('message')}")
        print(f"    Ma loi: {err.get('code')} / {err.get('error_subcode')}")
        if err.get("code") == 190:
            print("    => Token het han hoac khong hop le. Can lay token moi.")
        sys.exit(1)
    print(f"    OK - Tai khoan: {data.get('name')} (id: {data.get('id')})")

    # --- Buoc 2: Kiem tra quyen ads_read ---
    print()
    print("[2/3] Kiem tra quyen truy cap quang cao...")
    data, err = call_api("me/permissions", {"access_token": token})
    if err:
        print(f"    LOI: {err.get('message')}")
    else:
        perms = {p["permission"]: p["status"] for p in data.get("data", [])}
        ads_perm = perms.get("ads_read", "khong co")
        print(f"    ads_read: {ads_perm}")
        if ads_perm != "granted":
            print("    => THIEU quyen ads_read. Can them trong Graph API Explorer.")

    # --- Buoc 3: Thu lay danh sach campaign ---
    print()
    print("[3/3] Thu lay danh sach campaign...")
    acct = account if account.startswith("act_") else f"act_{account}"
    data, err = call_api(
        f"{acct}/campaigns",
        {"access_token": token, "fields": "id,name,status", "limit": "5"},
    )
    if err:
        print(f"    LOI: {err.get('message')}")
        print(f"    Ma loi: {err.get('code')} / {err.get('error_subcode')}")
        if err.get("code") == 100:
            print("    => ID tai khoan sai, hoac thieu tien to act_")
            print(f"    => Da thu voi: {acct}")
        sys.exit(1)

    campaigns = data.get("data", [])
    print(f"    OK - Lay duoc {len(campaigns)} campaign (mau):")
    for c in campaigns[:5]:
        name = c.get("name", "")[:50]
        print(f"       - {c.get('id')} | {c.get('status')} | {name}")

    print()
    print("=" * 60)
    print("KET QUA: KET NOI META ADS THANH CONG")
    print("=" * 60)


if __name__ == "__main__":
    main()
