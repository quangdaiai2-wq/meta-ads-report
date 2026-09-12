"""
Tim kiem action type lien quan den 'thanh toan' / 'payment'.
Quet ca cac truong actions, conversions, va action_values.
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

    target = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # Quet NHIEU truong khac nhau de tim 'thanh toan'
    params = {
        "access_token": token,
        "level": "campaign",
        "fields": "campaign_id,spend,actions,action_values,conversions,cost_per_action_type",
        "time_range": json.dumps({"since": target, "until": target}),
        "limit": "100",
    }

    url = f"{GRAPH}/{acct}/insights?" + urllib.parse.urlencode(params)
    print(f"Ngay: {target}")
    print("Dang quet cac truong: actions, action_values, conversions")
    print()

    with urllib.request.urlopen(url, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    rows = data.get("data", [])

    # Tim tat ca cac ten co chua tu khoa lien quan
    keywords = ["payment", "thanh_toan", "purchase", "order", "checkout"]
    found = {}

    for field in ["actions", "action_values", "conversions"]:
        for row in rows:
            for item in row.get(field, []) or []:
                t = (item.get("action_type") or "").lower()
                if any(k in t for k in keywords):
                    key = (field, item.get("action_type"))
                    v = float(item.get("value", 0) or 0)
                    found[key] = found.get(key, 0) + v

    print("=" * 70)
    print("CAC ACTION LIEN QUAN DEN THANH TOAN / MUA / DON")
    print("=" * 70)
    if found:
        for (field, atype), v in sorted(found.items(), key=lambda x: -x[1]):
            print(f"[{field:<14}] {int(v):>6}  {atype}")
    else:
        print("KHONG TIM THAY action nao lien quan.")

    # Liet ke TOAN BO ten action de doi chieu
    print()
    print("=" * 70)
    print("TOAN BO ACTION TYPE (chi liet ke ten, khong trung)")
    print("=" * 70)
    all_names = set()
    for row in rows:
        for item in row.get("actions", []) or []:
            all_names.add(item.get("action_type"))
    for n in sorted(all_names):
        print(f"  {n}")


if __name__ == "__main__":
    main()
