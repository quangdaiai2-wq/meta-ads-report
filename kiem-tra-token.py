"""
KIEM TRA TOKEN — TELEGRAM + META ADS
=====================================
Kiem tra 2 nhom token trong file .env:
  1. Token co HOAT DONG khong (ket noi duoc khong)
  2. Token con SONG BAO LAU  <-- phan quan trong nhat

Vi sao can phan 2:
    Token lay truc tiep tu Graph API Explorer chi song 1-2 GIO.
    Cac bai kiem tra thong thuong (test_meta.py) chi biet token "con song hay khong",
    nen mot token sap chet sau 1 gio van bao DAT binh thuong.
    Script nay hoi thang Meta de biet ngay het han.

Cach dung:
    python kiem-tra-token.py

Script nay CHI DOC, KHONG gui tin nhan nao vao Telegram.
Token khong bao gio bi in day du ra man hinh (chi hien 4 ky tu dau).
"""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ENV_PATH = Path(__file__).parent / ".env"
GRAPH = "https://graph.facebook.com/v26.0"
TELEGRAM = "https://api.telegram.org"

# Token Meta duoi nguong nay coi la NGAN HAN (phai doi sang 60 ngay)
NGUONG_NGAN_HAN_GIO = 24
# Token Meta tren nguong nay coi la dung duoc
NGUONG_DAI_HAN_NGAY = 30

REQUIRED = [
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "META_ADS_ACCESS_TOKEN",
    "META_APP_ID",
    "META_APP_SECRET",
    "META_AD_ACCOUNT_ID",
]

problems = []
warnings = []


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


def mask(value, show=4):
    """Che token, chi de lo vai ky tu dau. Do dai in rieng ben canh."""
    if not value:
        return "(trong)"
    if len(value) <= show:
        return "*" * len(value)
    return value[:show] + "****"


def get_json(url, timeout=30):
    """Tra ve (data, None) hoac (None, thong_bao_loi)."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        try:
            parsed = json.loads(body)
            msg = parsed.get("description") or parsed.get("error", {}).get("message") or body[:200]
        except Exception:
            msg = f"HTTP {e.code}"
        return None, msg
    except Exception as e:
        return None, str(e)


def tieu_de(text):
    print()
    print("=" * 62)
    print(f" {text}")
    print("=" * 62)


# ============================================================
#  1. TELEGRAM
# ============================================================
def kiem_tra_telegram(env):
    tieu_de("1. TELEGRAM")
    token = env.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = env.get("TELEGRAM_CHAT_ID", "")

    print(f"Bot token : {mask(token)} ({len(token)} ky tu)")
    print(f"Chat ID   : {mask(chat_id, 3)} ({len(chat_id)} ky tu)")
    print()

    if not token or not chat_id:
        print("  [LOI] Thieu token hoac chat ID trong .env")
        problems.append("Telegram: thieu token hoac chat ID")
        return

    # --- 1a. Token co hop le khong? ---
    print("[1/2] Token co hop le khong...")
    data, err = get_json(f"{TELEGRAM}/bot{token}/getMe", timeout=15)
    if err:
        print(f"  [LOI] {err}")
        print()
        print("  Nguyen nhan thuong gap:")
        print("   - Token bi thieu nua sau (chi co phan so truoc dau ':')")
        print("     Token Telegram dung phai co dang:  <so> : <35 ky tu>")
        print("   - Token da bi thu hoi (revoke) tren BotFather")
        problems.append("Telegram: token khong hop le")
        return

    if not data.get("ok"):
        print(f"  [LOI] {data.get('description')}")
        problems.append("Telegram: token khong hop le")
        return

    bot = data["result"]
    print(f"  OK - Bot: @{bot.get('username')}")
    print()
    print("  >>> TEN HIEN THI CUA BOT: " + str(bot.get("first_name")))
    print()
    print("  HAY TU KIEM: ten bot nay co dung la bot cua MAY NAY khong?")
    print("  (Vi du may cong ty nen dung bot co ten 'Company', khong phai 'Home'.")
    print("   Token dung dinh dang nhung cua bot khac thi moi bai test van bao DAT,")
    print("   nhung bao cao se chay ve sai cho.)")

    # --- 1b. Chat ID co gui duoc khong? (getChat = chi doc, khong gui tin) ---
    print()
    print("[2/2] Chat ID co hop le khong...")
    data, err = get_json(
        f"{TELEGRAM}/bot{token}/getChat?" + urllib.parse.urlencode({"chat_id": chat_id}),
        timeout=15,
    )
    if err:
        print(f"  [LOI] {err}")
        print()
        print("  Nguyen nhan thuong gap:")
        print("   - Chat ID sai")
        print("   - Chua bam Start voi bot nay (Telegram chan bot nhan tin truoc)")
        problems.append("Telegram: chat ID khong hop le")
        return

    if data.get("ok"):
        chat = data["result"]
        ten = chat.get("title") or chat.get("first_name") or chat.get("username") or "(khong ten)"
        print(f"  OK - Chat: {ten}  (loai: {chat.get('type')})")


# ============================================================
#  2. META ADS
# ============================================================
def kiem_tra_meta(env):
    tieu_de("2. META ADS")
    token = env.get("META_ADS_ACCESS_TOKEN", "")
    app_id = env.get("META_APP_ID", "")
    app_secret = env.get("META_APP_SECRET", "")
    account = env.get("META_AD_ACCOUNT_ID", "")

    print(f"Token     : {mask(token)} ({len(token)} ky tu)")
    print(f"App ID    : {app_id or '(trong)'}")
    print(f"App Secret: {mask(app_secret)} ({len(app_secret)} ky tu)")
    print(f"Tai khoan : {account or '(trong)'}")
    print()

    if not token:
        print("  [LOI] Thieu META_ADS_ACCESS_TOKEN trong .env")
        problems.append("Meta: thieu token")
        return

    # --- 2a. Token co hop le + con song bao lau? ---
    if app_id and app_secret:
        print("[1/3] Token con song bao lau... (hoi thang Meta bang debug_token)")
        data, err = get_json(
            f"{GRAPH}/debug_token?"
            + urllib.parse.urlencode({
                "input_token": token,
                "access_token": f"{app_id}|{app_secret}",
            })
        )
        if err:
            print(f"  [LOI] {err}")
            print("  => Khong doc duoc thong tin token. Kiem tra META_APP_ID / META_APP_SECRET.")
            problems.append("Meta: khong doc duoc thong tin token")
        else:
            d = data.get("data", {})
            if not d.get("is_valid"):
                print("  [LOI] Token KHONG con hieu luc.")
                problems.append("Meta: token het han hoac khong hop le")
            else:
                _in_thong_tin_token(d, app_id)
    else:
        print("[1/3] Thieu App ID / App Secret -> KHONG kiem duoc han token.")
        print("      Se chi kiem duoc token con song hay khong.")
        warnings.append("Meta: thieu App ID/App Secret nen khong kiem duoc han token")

    # --- 2b. Token co quyen doc quang cao khong? ---
    print()
    print("[2/3] Quyen doc quang cao (ads_read)...")
    data, err = get_json(f"{GRAPH}/me/permissions?" + urllib.parse.urlencode({"access_token": token}))
    if err:
        print(f"  [LOI] {err}")
        problems.append("Meta: khong kiem duoc quyen")
    else:
        perms = {p.get("permission"): p.get("status") for p in data.get("data", [])}
        trang_thai = perms.get("ads_read", "khong co")
        if trang_thai == "granted":
            print("  OK - ads_read: granted")
        else:
            print(f"  [LOI] ads_read: {trang_thai}")
            print("  => Khi lay token moi, nho tick quyen ads_read.")
            problems.append("Meta: thieu quyen ads_read")

    # --- 2c. Tai khoan quang cao co truy cap duoc khong? ---
    print()
    print("[3/3] Tai khoan quang cao co truy cap duoc khong...")
    acct = account if account.startswith("act_") else f"act_{account}"
    data, err = get_json(
        f"{GRAPH}/{acct}?" + urllib.parse.urlencode({
            "access_token": token,
            "fields": "name,account_status,currency",
        })
    )
    if err:
        print(f"  [LOI] {err}")
        problems.append("Meta: khong truy cap duoc tai khoan quang cao")
    else:
        trang_thai = {1: "hoat dong", 2: "bi vo hieu hoa", 3: "chua thanh toan",
                      7: "dang xem xet", 9: "grace period", 100: "dang dong",
                      101: "da dong"}.get(data.get("account_status"), "khong ro")
        print(f"  OK - {data.get('name')}  (trang thai: {trang_thai}, tien te: {data.get('currency')})")
        if data.get("account_status") != 1:
            warnings.append(f"Meta: tai khoan quang cao dang o trang thai '{trang_thai}'")


def _in_thong_tin_token(d, app_id):
    """In thong tin token Meta va canh bao neu la token ngan han."""
    expires_at = d.get("expires_at", 0)

    # Token thuoc app nao?
    if str(d.get("app_id")) != str(app_id):
        print(f"  [CANH BAO] Token thuoc app {d.get('app_id')}, nhung .env ghi {app_id}.")
        print("             Co the App ID sai, hoac token lay tu app khac.")
        warnings.append("Meta: App ID trong .env khong khop voi token")

    scopes = d.get("scopes", [])
    print(f"  OK - Token hop le, loai: {d.get('type')}")
    print(f"       Quyen: {', '.join(scopes) if scopes else '(khong co)'}")

    if not expires_at:
        print("       Het han: KHONG BAO GIO het han")
        return

    now = datetime.now(timezone.utc)
    exp_dt = datetime.fromtimestamp(expires_at, tz=timezone.utc)
    con_lai = exp_dt - now
    so_gio = con_lai.total_seconds() / 3600
    so_ngay = con_lai.total_seconds() / 86400

    print(f"       Het han: {exp_dt.astimezone().strftime('%d/%m/%Y %H:%M')} (gio may)")
    print(f"       Con lai: {so_ngay:.1f} ngay ({so_gio:.1f} gio)")
    print()

    if con_lai.total_seconds() <= 0:
        print("  [LOI] TOKEN DA HET HAN!")
        problems.append("Meta: token da het han")
    elif so_gio < NGUONG_NGAN_HAN_GIO:
        print("  [CANH BAO NGHIEM TRONG] Day la token NGAN HAN!")
        print(f"  Chi con song {so_gio:.1f} gio. He thong se chet trong hom nay.")
        print()
        print("  CACH SUA: chay lenh nay NGAY BAY GIO:")
        print("      python doi-token-60-ngay.py")
        problems.append(f"Meta: token ngan han, chi con {so_gio:.1f} gio")
    elif so_ngay < NGUONG_DAI_HAN_NGAY:
        print(f"  [CANH BAO] Token chi con {so_ngay:.0f} ngay. Sap phai gia han.")
        warnings.append(f"Meta: token chi con {so_ngay:.0f} ngay")
    else:
        print(f"  OK - Token DAI HAN, dung duoc (con {so_ngay:.0f} ngay).")


# ============================================================
#  KET LUAN
# ============================================================
def ket_luan():
    tieu_de("KET LUAN")
    if problems:
        print(f"CO {len(problems)} VAN DE CAN XU LY NGAY:")
        for p in problems:
            print(f"  [X] {p}")
        print()
        print("He thong CHUA chay duoc dung. Sua het cac muc [X] o tren.")
    else:
        print("KHONG CO VAN DE NGHIEM TRONG. He thong chay duoc.")

    if warnings:
        print()
        print(f"LUU Y THEM ({len(warnings)} muc, khong chan he thong chay):")
        for w in warnings:
            print(f"  [!] {w}")

    if problems:
        print()
        print("Sau khi sua xong, chay lai: python kiem-tra-token.py")
        return 1
    return 0


def main():
    tieu_de("KIEM TRA TOKEN — TELEGRAM + META ADS")
    print(f"File  : {ENV_PATH}")
    print(f"Luc   : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    if not ENV_PATH.exists():
        print()
        print(f"LOI: Khong tim thay file .env tai {ENV_PATH}")
        print("Cach sua: copy file .env.example thanh .env roi dien token vao.")
        sys.exit(1)

    env = load_env(ENV_PATH)

    # --- Kiem tra du cac muc bat buoc chua ---
    thieu = [k for k in REQUIRED if not env.get(k)]
    con_mau = [k for k in REQUIRED if "your_" in env.get(k, "") or "_here" in env.get(k, "")]
    if thieu or con_mau:
        print()
        if thieu:
            print("LOI: Thieu cac muc sau trong .env:")
            for k in thieu:
                print(f"  - {k}")
        if con_mau:
            print("LOI: Cac muc sau con nguyen chu mau (chua dien token that):")
            for k in con_mau:
                print(f"  - {k}")
        sys.exit(1)

    kiem_tra_telegram(env)
    kiem_tra_meta(env)
    sys.exit(ket_luan())


if __name__ == "__main__":
    main()
