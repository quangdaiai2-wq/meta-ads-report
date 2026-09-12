"""
Script kiem tra token Telegram co hoat dong khong.
Chi doc token tu file .env, khong in token ra man hinh.
"""
import os
import sys
import urllib.request
import json
from pathlib import Path


def load_env(path):
    """Doc file .env va tra ve dict cac bien."""
    env = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()
    return env


def mask(value, show=4):
    """Che token, chi hien thi vai ky tu dau."""
    if length := len(value):
        if length <= show:
            return "*" * length
        return value[:show] + "*" * (length - show)
    return "(trong)"


def main():
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        print("LOI: Khong tim thay file .env")
        sys.exit(1)

    env = load_env(env_path)
    token = env.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = env.get("TELEGRAM_CHAT_ID", "").strip()

    print("=" * 50)
    print("KIEM TRA TOKEN TELEGRAM")
    print("=" * 50)
    print(f"Bot token: {mask(token)} ({len(token)} ky tu)")
    print(f"Chat ID  : {mask(chat_id, 3)} ({len(chat_id)} ky tu)")
    print()

    if not token or not chat_id:
        print("KET QUA: THIEU TOKEN - khong the test")
        sys.exit(1)

    # --- Buoc 1: Kiem tra token co hop le khong (goi getMe) ---
    print("[1/2] Dang kiem tra token voi Telegram...")
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if data.get("ok"):
            bot_info = data["result"]
            print(f"    OK - Bot ten: @{bot_info.get('username')}")
            print(f"    Ten hien thi: {bot_info.get('first_name')}")
        else:
            print(f"    LOI: {data.get('description')}")
            sys.exit(1)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        print(f"    LOI HTTP {e.code}: {body[:200]}")
        sys.exit(1)
    except Exception as e:
        print(f"    LOI KET NOI: {e}")
        sys.exit(1)

    # --- Buoc 2: Gui tin nhan test ---
    print()
    print("[2/2] Dang gui tin nhan test...")
    message = (
        "TEST THANH CONG\n\n"
        "He thong bao cao Meta Ads da ket noi duoc Telegram.\n"
        "Neu ban thay tin nhan nay, token da hoat dong dung.\n\n"
        "- Tro ly"
    )
    try:
        payload = json.dumps({
            "chat_id": chat_id,
            "text": message,
        }).encode("utf-8")
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if data.get("ok"):
            print("    OK - Da gui tin nhan thanh cong!")
            print()
            print("=" * 50)
            print("KET QUA: TOKEN HOAT DONG TOT")
            print("Mo Telegram tren dien thoai de xem tin nhan.")
            print("=" * 50)
        else:
            print(f"    LOI: {data.get('description')}")
            print()
            print("Goi y: Kiem tra Chat ID da dung chua.")
            sys.exit(1)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        print(f"    LOI HTTP {e.code}: {body[:200]}")
        sys.exit(1)
    except Exception as e:
        print(f"    LOI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
