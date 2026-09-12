"""
Liet ke tat ca cac loai action (chuyen doi) ma Meta tra ve.
Dung de tim ten chinh xac cua "Luot mua" va "Luot thanh toan".
"""
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

API_VERSION = "v21.0"
GRAPH = f"https://graph.facebook.com/{API_VERSION}"


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


def main():
    env = load_env(Path(__file__).parent / ".env")
    token = env["META_ADS_ACCESS_TOKEN"]
    account = env["META_AD_ACCOUNT_ID"]
    acct = account if account.startswith("act_") else f"act_{account}"

    # Lay du lieu ngay hom qua
    target = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    params = {
        "access_token": token,
        "level": "campaign",
        "fields": "campaign_id,campaign_name,spend,actions",
        "time_range": json.dumps({"since": target, "until": target}),
        "limit": "100",
    }

    url = f"{GRAPH}/{acct}/insights?" + urllib.parse.urlencode(params)
    print(f"Dang lay du lieu ngay {target}...")
    print()

    with urllib.request.urlopen(url, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    rows = data.get("data", [])
    print(f"Tong so campaign: {len(rows)}")
    print()

    # Thu thap tat ca action type
    all_types = {}
    for row in rows:
        for action in row.get("actions", []):
            t = action.get("action_type", "")
            v = int(float(action.get("value", 0)))
            all_types[t] = all_types.get(t, 0) + v

    print("=" * 70)
    print("TAT CA CAC LOAI ACTION (CHUYEN DOI) CO DU LIEU")
    print("=" * 70)
    for t, v in sorted(all_types.items(), key=lambda x: -x[1]):
        print(f"{v:>8}  {t}")

    print()
    print("=" * 70)
    print("CHI TIET 3 CAMPAIGN DAU (de doi chieu)")
    print("=" * 70)
    for row in rows[:3]:
        print(f"\nCampaign: {row.get('campaign_id')}")
        print(f"  Ten: {row.get('campaign_name')[:60]}")
        print(f"  Chi tieu: {row.get('spend')}")
        for a in row.get("actions", []):
            v = int(float(a.get("value", 0)))
            if v > 0:
                print(f"    {v:>6}  {a.get('action_type')}")


if __name__ == "__main__":
    main()
