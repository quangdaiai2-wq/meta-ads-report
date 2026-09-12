"""
Script kiem tra Gemini API key co hoat dong khong.
Chi doc key tu file .env, khong in key ra man hinh.
"""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

MODEL = "gemini-3.6-flash"
BASE = "https://generativelanguage.googleapis.com/v1beta/models"


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
    key = env.get("GEMINI_API_KEY", "")

    print("=" * 60)
    print("KIEM TRA GEMINI API KEY")
    print("=" * 60)
    print(f"Key: {len(key)} ky tu, bat dau '{key[:6]}...'")
    print()

    if not key:
        print("LOI: Chua dien GEMINI_API_KEY")
        sys.exit(1)

    # Test bang 1 cau hoi don gian
    print("[1/1] Dang goi Gemini API...")
    payload = json.dumps({
        "contents": [{
            "parts": [{
                "text": "Tra loi ngan gon bang tieng Viet: 2+2 bang may?"
            }]
        }]
    }).encode("utf-8")

    url = f"{BASE}/{MODEL}:generateContent?key={key}"
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        print(f"    OK - Gemini tra loi: {text}")
        print()
        print("=" * 60)
        print("KET QUA: GEMINI API KEY HOAT DONG TOT")
        print("=" * 60)

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        print(f"    LOI HTTP {e.code}")
        try:
            err = json.loads(body).get("error", {})
            print(f"    Thong bao: {err.get('message')}")
            if e.code == 400:
                print("    => Key sai dinh dang hoac khong hop le")
            elif e.code == 403:
                print("    => Key bi tu choi (het han hoac thieu quyen)")
            elif e.code == 404:
                print(f"    => Model '{MODEL}' khong kha dung voi key nay")
        except Exception:
            print(f"    {body[:300]}")
        sys.exit(1)
    except Exception as e:
        print(f"    LOI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
