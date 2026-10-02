"""Gui file HUONG-DAN-MAY-NHA.md qua bot Telegram cua MAY CONG TY.

Chay 1 lan, chi DOC file va GUI. Khong dong toi Meta, khong sua gi.

Dung:
    python gui-huong-dan-may-nha.py
"""
import sys

import report

FILE = "HUONG-DAN-MAY-NHA.md"
CAPTION = (
    "HƯỚNG DẪN MÁY NHÀ — bản 02/10/2026 (viết cho TRỢ LÝ AI ở nhà)\n\n"
    "File này viết để WorkBuddy ở nhà ĐỌC VÀ TỰ LÀM giúp, không phải để Đại tự đọc.\n\n"
    "6 bước:\n"
    "1. git pull  → phải thấy mốc 19f05ce\n"
    "2. sửa .env: REPORT_SLOTS=8,17\n"
    "3. sửa .env: AGENT_NHIP_PHUT=15\n"
    "4. sửa .env: FILTER_INCLUDE=dainq\n"
    "5. hỏi Đại chọn chế độ → chuyen-sang-lam-that.bat hoặc tap-su\n"
    "6. khoi-dong-lai-agent.bat  ← BẮT BUỘC\n\n"
    "3 điều không được quên:\n"
    "· .env KHÔNG đi theo git pull — phải sửa tay\n"
    "· git pull là sửa CODE ⇒ phải khởi động lại agent\n"
    "· đo giờ khởi động bằng logs/baocao.log, KHÔNG bằng agent-dang-chay.lock\n\n"
    "Đọc file đính kèm để biết chi tiết và các bẫy đã gặp thật."
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
