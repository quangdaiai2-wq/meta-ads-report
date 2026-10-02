"""
DOC LICH SU THAO TAC QUANG CAO TU META
=======================================
Doc nhat ky hoat dong (activities) cua tai khoan quang cao, loc ra nhung thao
tac DANG KE: tao / tat / bat / doi ngan sach / doi ten.

Muc dich: dung lai CACH DAI CHAY QUANG CAO tu chinh viec Dai da lam, thay vi
bat Dai ngoi nho lai.

Cach dung:
    python doc-lich-su-thao-tac.py                 # 30 ngay gan nhat
    python doc-lich-su-thao-tac.py 2026-09-01 2026-10-01

Ket qua:
    - In thong ke ra man hinh
    - Luu du lieu THO vao logs/lich-su-thao-tac.json (logs/ da bi gitignore)

Script CHI DOC. Khong tao, khong sua, khong xoa gi.
Token khong bao gio bi in day du ra man hinh.
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

GOC = Path(__file__).parent
ENV_PATH = GOC / ".env"
OUT_PATH = GOC / "logs" / "lich-su-thao-tac.json"
API_VERSION = "v26.0"
GRAPH = f"https://graph.facebook.com/{API_VERSION}"
GIO_VN = timezone(timedelta(hours=7))

# Meta dat ten nguoc doi - phai dich lai, neu khong la hieu sai toan bo lich su.
CAP = {
    "CAMPAIGN_GROUP": "chien dich",
    "CAMPAIGN": "nhom quang cao",
    "ADGROUP": "quang cao",
    "ACCOUNT": "tai khoan",
}

# Cac loai thao tac DANG KE (bo qua nhung loai chi tiet ky thuat).
DANG_KE = {
    "create_campaign": "tao chien dich",
    "update_campaign_run_status": "doi trang thai chien dich",
    "update_campaign_name": "doi ten chien dich",
    "update_campaign_budget": "doi ngan sach chien dich",
    "create_ad_set": "tao nhom quang cao",
    "update_ad_set_run_status": "doi trang thai nhom",
    "update_ad_set_name": "doi ten nhom",
    "update_ad_set_budget": "doi ngan sach nhom",
    "update_ad_set_duration": "doi lich chay nhom",
    "create_ad": "tao quang cao",
    "update_ad_run_status": "doi trang thai quang cao",
    "update_ad_name": "doi ten quang cao",
}

FIELDS = ("event_type,translated_event_type,event_time,object_id,object_name,"
          "object_type,actor_name,extra_data")


def load_env(path):
    env = {}
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    except Exception:
        pass
    return env


def goi(url, thu_lai=4):
    """Goi Graph API, tu thu lai khi Meta tra loi tam. Khong bao gio nem loi."""
    for lan in range(thu_lai + 1):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.loads(r.read().decode("utf-8")), None
        except urllib.error.HTTPError as e:
            if e.code in (500, 502, 503, 504) and lan < thu_lai:
                time.sleep(2)
                continue
            return None, f"HTTP {e.code}: {e.read().decode()[:150]}"
        except Exception as e:
            if lan < thu_lai:
                time.sleep(2)
                continue
            return None, str(e)
    return None, "het luot thu lai"


def doc_het(acc, tok, since, until):
    """Doc het activities trong khoang, co phan trang."""
    url = f"{GRAPH}/{acc}/activities?" + urllib.parse.urlencode({
        "access_token": tok, "limit": 300,
        "since": since, "until": until, "fields": FIELDS})
    tat_ca, trang, loi_cuoi = [], 0, None
    while url and trang < 80:
        d, loi = goi(url)
        if loi:
            loi_cuoi = loi
            break
        tat_ca.extend(d.get("data", []))
        trang += 1
        url = (d.get("paging") or {}).get("next")
        print(f"  ... trang {trang}, da doc {len(tat_ca)} muc", end="\r", flush=True)
    print(" " * 60, end="\r")
    return tat_ca, loi_cuoi


def gio_vn(chuoi):
    try:
        return datetime.strptime(chuoi, "%Y-%m-%dT%H:%M:%S%z").astimezone(GIO_VN)
    except Exception:
        return None


def gia_tri_cu_moi(extra):
    """Boc old_value / new_value tu extra_data. Tra ve (cu, moi) da rut gon.

    Meta boc gia tri trong nhieu lop. Da gap that hai dang:
      ngan sach: {"old_value": {"type":"payment_amount","old_value":26135,...},
                  "new_value": {"type":"payment_amount","new_value":400000,...}}
      trang thai: {"old_value": "Ho\u1ea1t \u0111\u1ed9ng", "new_value": "Kh\u00f4ng ho\u1ea1t \u0111\u1ed9ng"}
    Nen phai di theo dung ten khoa, khong doan.
    """
    if not extra:
        return None, None
    try:
        d = json.loads(extra) if isinstance(extra, str) else extra
    except Exception:
        return None, None
    if not isinstance(d, dict):
        return None, None

    def rut(v):
        # Di het cac lop long nhau: uu tien "new_value" roi "old_value" roi "value".
        for _ in range(4):
            if not isinstance(v, dict):
                break
            for k in ("new_value", "old_value", "value"):
                if k in v:
                    v = v[k]
                    break
            else:
                if "content" in v:
                    return v["content"]
                break
        if isinstance(v, dict):
            return json.dumps(v, ensure_ascii=False)[:60]
        return v

    return rut(d.get("old_value")), rut(d.get("new_value"))


def main():
    since = sys.argv[1] if len(sys.argv) > 1 else (
        datetime.now(GIO_VN) - timedelta(days=30)).strftime("%Y-%m-%d")
    until = sys.argv[2] if len(sys.argv) > 2 else (
        datetime.now(GIO_VN) + timedelta(days=1)).strftime("%Y-%m-%d")

    env = load_env(ENV_PATH)
    tok = env.get("META_ADS_ACCESS_TOKEN", "").strip()
    acc = env.get("META_AD_ACCOUNT_ID", "").strip()
    if not tok or not acc:
        print("LOI: thieu META_ADS_ACCESS_TOKEN hoac META_AD_ACCOUNT_ID trong .env")
        sys.exit(1)

    print("=" * 74)
    print(f"DOC LICH SU THAO TAC  ({since} -> {until})")
    print("=" * 74)

    tat_ca, loi = None, None
    if "--tu-file" in sys.argv and OUT_PATH.exists():
        # Doc lai tu du lieu da luu: tranh goi lai hang chuc trang API chi de phan tich lai.
        tat_ca = json.loads(OUT_PATH.read_text(encoding="utf-8"))
        print(f"Doc lai tu file da luu: {len(tat_ca)} muc")
    if tat_ca is None:
        tat_ca, loi = doc_het(acc, tok, since, until)
    print(f"Doc duoc {len(tat_ca)} muc" + (f" | dung som: {loi}" if loi else ""))
    if not tat_ca:
        sys.exit(0)

    if "--tu-file" not in sys.argv:
        OUT_PATH.parent.mkdir(exist_ok=True)
        OUT_PATH.write_text(json.dumps(tat_ca, ensure_ascii=False, indent=1),
                            encoding="utf-8")
        print(f"Da luu du lieu tho: {OUT_PATH}")

    # --- Loc thao tac dang ke ---
    dang_ke = [x for x in tat_ca if x.get("event_type") in DANG_KE]
    print(f"Trong do, thao tac DANG KE (tao/tat/bat/ngan sach/ten): {len(dang_ke)}")
    print()

    # --- 1. Dem theo loai ---
    print("--- 1. THEO LOAI THAO TAC ---")
    dem = Counter(DANG_KE[x["event_type"]] for x in dang_ke)
    for ten, n in dem.most_common():
        print(f"  {n:5}  {ten}")
    print()

    # --- 2. Theo nguoi lam ---
    print("--- 2. AI LAM ---")
    for ten, n in Counter(x.get("actor_name") for x in dang_ke).most_common(10):
        print(f"  {n:5}  {ten}")
    print()

    # --- 3. Theo gio trong ngay / thu trong tuan ---
    print("--- 3. THAO TAC VAO LUC NAO (gio Viet Nam) ---")
    theo_gio = Counter()
    theo_thu = Counter()
    for x in dang_ke:
        t = gio_vn(x.get("event_time") or "")
        if t:
            theo_gio[t.hour] += 1
            theo_thu[t.strftime("%A")] += 1
    for h in range(24):
        n = theo_gio.get(h, 0)
        if n:
            print(f"  {h:02d}h  {'#' * min(n, 60)} {n}")
    print()
    thu_vn = {"Monday": "Thu 2", "Tuesday": "Thu 3", "Wednesday": "Thu 4",
              "Thursday": "Thu 5", "Friday": "Thu 6", "Saturday": "Thu 7",
              "Sunday": "Chu nhat"}
    for t, n in theo_thu.most_common():
        print(f"  {thu_vn.get(t, t):8} {n}")
    print()

    # --- 4. Tat / bat nhom: nhom nao, bao nhieu lan ---
    print("--- 4. NHOM QUANG CAO BI TAT/BAT NHIEU NHAT ---")
    dem_nhom = defaultdict(lambda: {"ten": "", "tat": 0, "bat": 0})
    for x in dang_ke:
        if x.get("event_type") != "update_ad_set_run_status":
            continue
        _, moi = gia_tri_cu_moi(x.get("extra_data"))
        ma = str(x.get("object_id"))
        dem_nhom[ma]["ten"] = x.get("object_name") or dem_nhom[ma]["ten"]
        if moi and "ho\u1ea1t \u0111\u1ed9ng" in str(moi).lower() and "kh\u00f4ng" not in str(moi).lower():
            dem_nhom[ma]["bat"] += 1
        else:
            dem_nhom[ma]["tat"] += 1
    for ma, v in sorted(dem_nhom.items(),
                        key=lambda t: -(t[1]["tat"] + t[1]["bat"]))[:15]:
        print(f"  tat {v['tat']:3} | bat {v['bat']:3} | {v['ten'][:52]!r} ({ma})")
    print()

    # --- 5. Doi ngan sach: huong va do lon ---
    print("--- 5. DOI NGAN SACH NHOM QUANG CAO ---")
    tang = giam = khong_ro = 0
    vi_du = []
    for x in dang_ke:
        if x.get("event_type") != "update_ad_set_budget":
            continue
        cu, moi = gia_tri_cu_moi(x.get("extra_data"))
        try:
            cu_s, moi_s = float(cu), float(moi)
        except (TypeError, ValueError):
            khong_ro += 1
            continue
        if moi_s > cu_s:
            tang += 1
        elif moi_s < cu_s:
            giam += 1
        if len(vi_du) < 15:
            t = gio_vn(x.get("event_time") or "")
            vi_du.append((t, cu_s, moi_s, x.get("object_name")))
    print(f"  tang ngan sach: {tang} lan | giam: {giam} lan | khong doc duoc: {khong_ro}")
    print()
    print("  15 lan doi ngan sach gan nhat:")
    for t, cu, moi, ten in vi_du:
        pt = (moi - cu) / cu * 100 if cu else 0
        chu = t.strftime("%d/%m %H:%M") if t else "?"
        print(f"    {chu} | {cu:>12,.0f} -> {moi:>12,.0f} d ({pt:+6.1f}%) | {str(ten)[:44]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
