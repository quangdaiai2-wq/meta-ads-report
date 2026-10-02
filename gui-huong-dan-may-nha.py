"""Gui file HUONG-DAN-MAY-NHA.md qua bot Telegram cua MAY CONG TY.

Chay 1 lan, chi DOC file va GUI. Khong dong toi Meta, khong sua gi.

Dung:
    python gui-huong-dan-may-nha.py
"""
import sys

import report

FILE = "HUONG-DAN-MAY-NHA.md"
CAPTION = (
    "HƯỚNG DẪN MÁY NHÀ — bản 02/10/2026\n\n"
    "Máy nhà cần làm 6 bước:\n"
    "1. git pull (phải thấy mốc 16aa0ff)\n"
    "2. sửa REPORT_SLOTS=8,17 trong .env\n"
    "3. sửa AGENT_NHIP_PHUT=15\n"
    "4. kiểm FILTER_INCLUDE=dainq\n"
    "5. chọn chế độ: chuyen-sang-lam-that.bat hoặc chuyen-sang-tap-su.bat\n"
    "6. khởi động lại: khoi-dong-lai-agent.bat\n\n"
    "Đọc file đính kèm để biết chi tiết."
)


def main():
    env = report.load_env(".env")
    if not env.get("TELEGRAM_BOT_TOKEN") or not env.get("TELEGRAM_CHAT_ID"):
        print("THIEU TELEGRAM_BOT_TOKEN hoac TELEGRAM_CHAT_ID trong .env")
        return 1

    # Gui 1 tin ngan truoc, de Dai biet sap co file
    ok, loi = report.send_telegram(env, CAPTION)
    print("Tin ngan :", "OK" if ok else f"LOI: {loi}")

    # Gui file dinh kem
    ok2, loi2 = report.send_telegram_document(env, FILE, FILE)
    print("Gui file :", "OK" if ok2 else f"LOI: {loi2}")

    if ok and ok2:
        print("XONG. Da gui ca tin nhan va file.")
        return 0
    print("CO LOI — kiem lai ket qua phia tren.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
