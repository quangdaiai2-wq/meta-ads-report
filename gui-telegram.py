#!/usr/bin/env python3
# Gui mot file len Telegram qua Bot API (khong dung thu vien ngoai).
# Doc token tu file .env (khong in ra man hinh).
import os
import sys
import json
import http.client


def read_env(path=".env"):
    env = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def main():
    env = read_env()
    token = env.get("TELEGRAM_BOT_TOKEN")
    chat = env.get("TELEGRAM_CHAT_ID")
    if not token or not chat:
        print("THIEU TELEGRAM_BOT_TOKEN hoac TELEGRAM_CHAT_ID trong file .env")
        sys.exit(1)

    filepath = sys.argv[1] if len(sys.argv) > 1 else "QUY-TRINH-HANG-NGAY.md"
    caption = (
        sys.argv[2]
        if len(sys.argv) > 2
        else "📋 QUY TRINH HANG NGAY (2 may: nha + cong ty). Moi sang chi can chay: git pull"
    )
    if not os.path.exists(filepath):
        print("KHONG TIM THAY FILE:", filepath)
        sys.exit(1)

    boundary = "----workbuddyboundary12345"
    with open(filepath, "rb") as f:
        data = f.read()

    body = b""
    body += ("--%s\r\n" % boundary).encode()
    body += b'Content-Disposition: form-data; name="chat_id"\r\n\r\n'
    body += chat.encode() + b"\r\n"
    body += ("--%s\r\n" % boundary).encode()
    body += b'Content-Disposition: form-data; name="caption"\r\n\r\n'
    body += caption.encode("utf-8") + b"\r\n"
    body += ("--%s\r\n" % boundary).encode()
    body += (
        'Content-Disposition: form-data; name="document"; filename="%s"\r\n'
        % os.path.basename(filepath)
    ).encode()
    body += b"Content-Type: text/markdown\r\n\r\n"
    body += data + b"\r\n"
    body += ("--%s--\r\n" % boundary).encode()

    conn = http.client.HTTPSConnection("api.telegram.org", timeout=30)
    conn.request(
        "POST",
        "/bot%s/sendDocument" % token,
        body,
        {"Content-Type": "multipart/form-data; boundary=%s" % boundary},
    )
    resp = conn.getresponse()
    text = resp.read().decode("utf-8")
    print("HTTP STATUS:", resp.status)
    try:
        j = json.loads(text)
        if j.get("ok"):
            print("OK - da gui file vao Telegram thanh cong")
            print("File:", j["result"]["document"]["file_name"])
        else:
            print("FAIL:", j.get("description", text[:300]))
    except Exception:
        print("RESPONSE:", text[:500])


if __name__ == "__main__":
    main()
