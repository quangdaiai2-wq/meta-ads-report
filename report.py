"""
BAO CAO META ADS TU DONG -> TELEGRAM
=====================================
Script chay theo lich, lay so lieu Meta Ads, gui bao cao vao Telegram.

Cach dung:
    python report.py            # tu dong nhan biet moc gio hien tai
    python report.py --mock 8   # chay thu voi moc gio 8h (khong gui Telegram)
    python report.py --dry      # chay that nhung khong gui Telegram

Uu tien doc moc gio tu tham so --mock, neu khong co thi lay gio hien tai.
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

from dashboard import save_dashboard

API_VERSION = "v21.0"
GRAPH = f"https://graph.facebook.com/{API_VERSION}"

# Cac moc gio bao cao (gio Viet Nam)
REPORT_SLOTS = [8, 12, 17, 22]

# Ten cac loai action trong Meta API (da kiem chung bang list_actions.py)
# LUU Y: Meta tra ve NHIEU ten cho CUNG mot hanh dong (omni_*, onsite_*, offsite_*).
# Neu cong het se bi dem trung. Chi dung MOT ten duy nhat cho moi chi so.
ACT_PURCHASE = ["onsite_conversion.purchase"]
ACT_PAYMENT = ["onsite_conversion.initiate_checkout"]
ACT_ORDER = ["onsite_conversion.messaging_order_created_v2"]
ACT_MSG = ["onsite_conversion.messaging_conversation_started_7d"]
ACT_CONTACT = ["onsite_conversion.messaging_first_reply"]
ACT_COMMENT = ["onsite_conversion.post_net_comment"]
INSIGHT_FIELDS = [
    "campaign_id",
    "campaign_name",
    "spend",
    "impressions",
    "clicks",
    "actions",
    "cost_per_action_type",
]


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


LOG_DIR = Path(__file__).parent / "logs"


def log(message):
    """Ghi nhat ky moi lan chay vao logs/baocao.log (de biet task co chay hay khong)."""
    try:
        LOG_DIR.mkdir(exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_DIR / "baocao.log", "a", encoding="utf-8") as f:
            f.write(f"[{stamp}] {message}\n")
    except Exception:
        pass


def send_error_alert(env, err):
    """Gui canh bao loi vao Telegram — de loi khong bao gio xay ra im lang."""
    msg = (
        "⚠️ BÁO CÁO META ADS GẶP LỖI\n"
        "\n"
        "Hệ thống không lấy được số liệu.\n"
        f"Lý do Meta trả về:\n{err}\n"
        "\n"
        "Cách xử lý:\n"
    )
    low = str(err).lower()
    if "expired" in low or "session has expired" in low:
        msg += (
            "→ Token Meta đã HẾT HẠN.\n"
            "→ Cần lấy token mới rồi dán lại vào file .env.\n"
            "→ Xem hướng dẫn trong file HUONG-DAN-DIEN-TOKEN.md"
        )
    elif "rate limit" in low or "too many" in low:
        msg += (
            "→ Meta tạm thời chặn (quá nhiều yêu cầu).\n"
            "→ Không cần làm gì. Hệ thống tự thử lại ở mốc giờ sau."
        )
    elif "permission" in low or "ads_read" in low:
        msg += (
            "→ Token thiếu quyền đọc quảng cáo.\n"
            "→ Khi lấy token mới, nhớ tick quyền ads_read."
        )
    else:
        msg += "→ Xem file logs/baocao.log để biết chi tiết."
    try:
        ok, err2 = send_telegram(env, msg)
        if ok:
            log("Da gui canh bao loi vao Telegram")
        else:
            log(f"Khong gui duoc canh bao Telegram: {err2}")
    except Exception as e:
        log(f"Khong gui duoc canh bao Telegram: {e}")


def api_get(path, params):
    url = f"{GRAPH}/{path}?" + urllib.parse.urlencode(params)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8")), None
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            try:
                err = json.loads(body).get("error", {})
            except Exception:
                err = {"message": f"HTTP {e.code}"}
            # Loi rate limit thi thu lai
            if err.get("code") in (17, 80004) and attempt < 2:
                continue
            return None, err
        except Exception as e:
            if attempt < 2:
                continue
            return None, {"message": str(e)}
    return None, {"message": "Khong the ket noi sau 3 lan thu"}


def fmt_money(value):
    """Dinh dang tien kieu Viet Nam: 20.346.476"""
    try:
        return f"{int(round(float(value))):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "0"


def get_action_value(actions, action_type):
    """Lay gia tri cua MOT loai action. action_type co the la str hoac list."""
    if not actions:
        return 0
    types = [action_type] if isinstance(action_type, str) else action_type
    total = 0
    for a in actions:
        if a.get("action_type") in types:
            total += int(float(a.get("value", 0)))
    return total


def determine_period(now, slot_hour):
    """Tra ve (tu_ngay, den_ngay, mo_ta) theo moc gio."""
    today = now.date()

    if slot_hour == 8:
        # Bao cao ngay hom truoc
        target = today - timedelta(days=1)
        return target, target, f"{target.strftime('%d/%m/%Y')}"
    else:
        # Bao cao trong ngay, tu 0h den gio hien tai
        return today, today, (
            f"{today.strftime('%d/%m/%Y')} "
            f"(00:00 - {slot_hour:02d}:00)"
        )


def fetch_insights(env, since, until):
    """Lay insight theo campaign trong khoang thoi gian."""
    token = env["META_ADS_ACCESS_TOKEN"]
    account = env["META_AD_ACCOUNT_ID"]
    acct = account if account.startswith("act_") else f"act_{account}"

    params = {
        "access_token": token,
        "level": "campaign",
        "fields": ",".join(INSIGHT_FIELDS),
        "time_range": json.dumps({
            "since": since.strftime("%Y-%m-%d"),
            "until": until.strftime("%Y-%m-%d"),
        }),
        "limit": "500",
    }

    all_rows = []
    data, err = api_get(f"{acct}/insights", params)
    if err:
        return None, err
    all_rows.extend(data.get("data", []))

    # Lay tiep cac trang sau
    while True:
        paging = data.get("paging", {})
        next_url = paging.get("next")
        if not next_url:
            break
        try:
            with urllib.request.urlopen(next_url, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            all_rows.extend(data.get("data", []))
        except Exception:
            break

    return all_rows, None


def apply_filter(rows, include_kw, exclude_kws):
    """Loc campaign theo tu khoa."""
    include_kw = include_kw.lower().strip()
    exclude_kws = [k.strip().lower() for k in exclude_kws if k.strip()]

    result = []
    for row in rows:
        name = (row.get("campaign_name") or "").lower()

        # Phai chua tu khoa include
        if include_kw and include_kw not in name:
            continue

        # Khong duoc chua tu khoa exclude
        if any(kw in name for kw in exclude_kws):
            continue

        # Chi lay campaign co chi tieu > 0
        try:
            if float(row.get("spend", 0)) <= 0:
                continue
        except (ValueError, TypeError):
            continue

        result.append(row)

    return result


def compute_stats(env, since, until):
    """Tinh toan so lieu, tra ve dict de dung chung cho text va HTML."""
    include_kw = env.get("FILTER_INCLUDE", "")
    exclude_kws = env.get("FILTER_EXCLUDE", "").split(",")
    top_n = int(env.get("TOP_CAMPAIGN_COUNT", "5"))

    rows, err = fetch_insights(env, since, until)
    if err:
        return None, f"Loi lay du lieu Meta: {err.get('message')}"

    filtered = apply_filter(rows, include_kw, exclude_kws)

    def spend_of(r):
        return float(r.get("spend", 0) or 0)

    def purchase_count(r):
        return get_action_value(r.get("actions"), ACT_PURCHASE)

    totals = {
        "spend": sum(spend_of(r) for r in filtered),
        "msg": sum(get_action_value(r.get("actions"), ACT_MSG) for r in filtered),
        "contact": sum(get_action_value(r.get("actions"), ACT_CONTACT) for r in filtered),
        "order": sum(get_action_value(r.get("actions"), ACT_ORDER) for r in filtered),
        "purchase": sum(get_action_value(r.get("actions"), ACT_PURCHASE) for r in filtered),
        "payment": sum(get_action_value(r.get("actions"), ACT_PAYMENT) for r in filtered),
        "comment": sum(get_action_value(r.get("actions"), ACT_COMMENT) for r in filtered),
    }

    # Camp tot: sap theo luot mua giam dan
    good = sorted(filtered, key=purchase_count, reverse=True)[:top_n]
    good = [r for r in good if purchase_count(r) > 0]

    # Camp kem: uu tien chi tieu > 0 ma 0 don
    zero_result = [r for r in filtered if purchase_count(r) == 0]
    zero_result.sort(key=spend_of, reverse=True)
    low_result = [r for r in filtered if purchase_count(r) > 0]
    low_result.sort(key=purchase_count)
    bad = (zero_result + low_result)[:top_n]

    def pack(r, rank):
        pc = purchase_count(r)
        return {
            "rank": rank,
            "id": str(r.get("campaign_id", "")),
            "name": (r.get("campaign_name") or "").strip(),
            "spend": spend_of(r),
            "purchase": pc,
            "payment": get_action_value(r.get("actions"), ACT_PAYMENT),
            "msg": get_action_value(r.get("actions"), ACT_MSG),
            "cpr": (spend_of(r) / pc) if pc > 0 else None,
        }

    return {
        "total_campaigns": len(filtered),
        "totals": totals,
        "good": [pack(r, i + 1) for i, r in enumerate(good)],
        "bad": [pack(r, i + 1) for i, r in enumerate(bad)],
        "include_kw": include_kw,
        "exclude_kw": env.get("FILTER_EXCLUDE", ""),
        "account_name": env.get("REPORT_ACCOUNT_NAME", ""),
    }, None


def build_report(env, stats, period_text):
    """Tao noi dung bao cao dang text tu so lieu DA TINH SAN.

    KHONG goi lai Meta API o day. So lieu duoc tinh dung 1 lan trong main()
    roi dung chung cho ca bao cao text lan dashboard HTML.
    """
    include_kw = env.get("FILTER_INCLUDE", "")
    account_name = env.get("REPORT_ACCOUNT_NAME", "")

    totals = stats["totals"]
    good = stats["good"]
    bad = stats["bad"]

    # --- Soan bao cao ---
    lines = []
    lines.append(f"🔴 BÁO CÁO META ADS — {period_text}")
    lines.append(f"Tài khoản: {account_name}")
    lines.append("")

    lines.append("🔵 BỘ LỌC")
    lines.append(f"- Campaign có tên chứa: {include_kw}")
    lines.append(f"- Loại trừ campaign chứa: {env.get('FILTER_EXCLUDE', '')}")
    lines.append("- Chỉ lấy mục có chi tiêu > 0")
    lines.append("")

    lines.append("🔵 TÓM TẮT")
    lines.append(f"Có {stats['total_campaigns']} campaign đủ điều kiện.")
    lines.append(f"- Số tiền đã chi tiêu: {fmt_money(totals['spend'])} VND")
    lines.append(f"- Lượt bắt đầu cuộc trò chuyện qua tin nhắn: {totals['msg']}")
    lines.append(f"- Người liên hệ nhắn tin mới: {totals['contact']}")
    lines.append(f"- Đơn đặt hàng đã tạo: {totals['order']}")
    lines.append(f"- Lượt mua: {totals['purchase']}")
    lines.append(f"- Lượt thanh toán: {totals['payment']}")
    lines.append(f"- Bình luận về bài viết: {totals['comment']}")
    lines.append("")

    lines.append("🔵 NHẬN ĐỊNH")
    lines.append(f"Camp hiệu quả (top {len(good)}):")
    if good:
        for r in good:
            lines.append(f"- ID chiến dịch: {r['id']}")
            lines.append(
                f"  Lượt mua: {r['purchase']}; "
                f"Số tiền đã chi tiêu: {fmt_money(r['spend'])} VND"
            )
    else:
        lines.append("- Không có camp nào tạo ra lượt mua.")
    lines.append("")

    lines.append(f"Camp kém hiệu quả (top {len(bad)}):")
    if bad:
        for r in bad:
            lines.append(f"- ID chiến dịch: {r['id']}")
            if r["purchase"] == 0:
                lines.append(
                    f"  Không tạo ra kết quả nào; "
                    f"Đã chi tiêu: {fmt_money(r['spend'])} VND"
                )
            else:
                lines.append(
                    f"  Số tiền đã chi tiêu: {fmt_money(r['spend'])} VND; "
                    f"Kết quả tin nhắn mới: {r['msg']}; "
                    f"Lượt mua: {r['purchase']}"
                )
    else:
        lines.append("- Không có camp nào kém hiệu quả.")
    lines.append("")

    return "\n".join(lines)


def send_telegram(env, text):
    token = env["TELEGRAM_BOT_TOKEN"]
    chat_id = env["TELEGRAM_CHAT_ID"]

    # Telegram gioi han 4096 ky tu moi tin
    chunks = []
    while len(text) > 4000:
        split_at = text.rfind("\n", 0, 4000)
        if split_at == -1:
            split_at = 4000
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    chunks.append(text)

    for i, chunk in enumerate(chunks, 1):
        payload = json.dumps({
            "chat_id": chat_id,
            "text": chunk,
            "disable_web_page_preview": True,
        }).encode("utf-8")
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if not data.get("ok"):
                return False, data.get("description")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            return False, f"HTTP {e.code}: {body[:200]}"
        except Exception as e:
            return False, str(e)

    return True, None


def send_telegram_document(env, filepath, filename, caption=""):
    """Gui 1 file (vi du dashboard HTML) len Telegram bang sendDocument."""
    token = env["TELEGRAM_BOT_TOKEN"]
    chat_id = env["TELEGRAM_CHAT_ID"]
    boundary = "----workbuddyboundary" + str(int(datetime.now().timestamp()))
    try:
        with open(filepath, "rb") as f:
            data = f.read()
    except Exception as e:
        return False, f"Khong doc duoc file: {e}"

    body = b""
    body += ("--%s\r\n" % boundary).encode()
    body += b'Content-Disposition: form-data; name="chat_id"\r\n\r\n'
    body += chat_id.encode() + b"\r\n"
    if caption:
        body += ("--%s\r\n" % boundary).encode()
        body += b'Content-Disposition: form-data; name="caption"\r\n\r\n'
        body += caption.encode("utf-8") + b"\r\n"
    body += ("--%s\r\n" % boundary).encode()
    body += (
        'Content-Disposition: form-data; name="document"; filename="%s"\r\n' % filename
    ).encode()
    body += b"Content-Type: text/html; charset=utf-8\r\n\r\n"
    body += data + b"\r\n"
    body += ("--%s--\r\n" % boundary).encode()

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendDocument",
        data=body,
        headers={"Content-Type": "multipart/form-data; boundary=%s" % boundary},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            j = json.loads(resp.read().decode("utf-8"))
        if j.get("ok"):
            return True, None
        return False, j.get("description")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        return False, f"HTTP {e.code}: {err_body[:200]}"
    except Exception as e:
        return False, str(e)


def main():
    parser = argparse.ArgumentParser(description="Bao cao Meta Ads -> Telegram")
    parser.add_argument("--mock", type=int, choices=REPORT_SLOTS,
                        help="Chay thu voi moc gio nay (khong gui Telegram)")
    parser.add_argument("--dry", action="store_true",
                        help="Chay that nhung khong gui Telegram")
    args = parser.parse_args()

    env = load_env(Path(__file__).parent / ".env")
    now = datetime.now()

    if args.mock is not None:
        slot = args.mock
        print(f"[CHE DO THU] Moc gio: {slot}h")
    else:
        # Tim moc gio gan nhat
        slot = min(REPORT_SLOTS, key=lambda s: abs(s - now.hour))
        print(f"Moc gio hien tai: {slot}h (gio may: {now.hour}h)")

    since, until, period_text = determine_period(now, slot)
    print(f"Khoang thoi gian: {since} -> {until}")
    print()
    log(f"BAT DAU - moc {slot}h, khoang {since} -> {until}")

    # --- TINH SO LIEU META API: DUNG 1 LAN DUY NHAT ---
    # Dung chung cho ca bao cao text lan dashboard HTML.
    # (Truoc day cho nay goi compute_stats() 2 lan -> ton gap doi han muc API,
    #  va so lieu tren Telegram co the lech voi file HTML vi goi 2 thoi diem khac nhau.)
    stats, err = compute_stats(env, since, until)
    if err:
        print(f"LOI: {err}")
        log(f"THAT BAI - moc {slot}h: {err}")
        if args.mock is None and not args.dry:
            send_error_alert(env, err)
        sys.exit(1)

    report = build_report(env, stats, period_text)

    print("=" * 60)
    print(report)
    print("=" * 60)

    # --- Tao dashboard HTML (dung lai chinh so lieu vua tinh, khong goi API lan 2) ---
    dashboard_path = None
    try:
        dashboard_path = save_dashboard(stats, since, until, period_text)
        print()
        print(f"DA TAO DASHBOARD: {dashboard_path}")
    except Exception as e:
        print(f"LOI TAO DASHBOARD: {e}")

    if args.mock is not None or args.dry:
        print()
        print("[Khong gui Telegram - che do thu]")
        sys.exit(0)

    print()
    ok, err = send_telegram(env, report)
    if ok:
        print("DA GUI BAO CAO VAO TELEGRAM")
        log(f"THANH CONG - moc {slot}h, da gui Telegram")
    else:
        print(f"LOI GUI TELEGRAM: {err}")
        log(f"THAT BAI GUI TELEGRAM - moc {slot}h: {err}")
        sys.exit(1)

    # --- Gui kem file dashboard HTML vao cung Telegram ---
    if dashboard_path:
        fname = f"baocao_{slot}h_{now.strftime('%d-%m-%Y')}.html"
        caption = (
            f"📊 BÁO CÁO META ADS — {period_text}\n"
            "Bản đầy đủ dạng HTML. Tải về và mở bằng trình duyệt để xem."
        )
        dok, derr = send_telegram_document(env, dashboard_path, fname, caption)
        if dok:
            print("DA GUI FILE HTML VAO TELEGRAM")
            log(f"THANH CONG - moc {slot}h, da gui file HTML")
        else:
            print(f"LOI GUI FILE HTML: {derr}")
            log(f"THAT BAI GUI FILE HTML - moc {slot}h: {derr}")


if __name__ == "__main__":
    main()
