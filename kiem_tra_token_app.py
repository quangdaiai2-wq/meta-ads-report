"""KIEM TRA TOKEN META — dung cho Dai sau khi doi sang token App.

Chay: python kiem_tra_token_app.py
Hoac bam dup: kiem-tra-token-app.bat

File nay TRA LOI 3 cau hoi, bang tieng Viet de doc:
  1. Token hien tai la token CA NHAN hay token APP?
  2. Token con han bao lau, het han ngay nao?
  3. Token co du quyen de agent lam viec khong?

KHONG GHI GI LEN META. Chi DOC. Chay bao nhieu lan cung duoc.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import report   # nguon duy nhat cua API_VERSION

GOC = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(GOC, ".env")

QUYEN_CAN = ("ads_management", "ads_read")


def _duong_ke():
    print("-" * 62)


def _doc_env():
    return report.load_env(ENV_PATH)


def _debug_token(tok, app_id, app_secret):
    """Hoi Meta thong tin ve token. Tra ve (data, loi)."""
    if not app_id or not app_secret:
        return None, "thieu META_APP_ID hoac META_APP_SECRET trong .env"
    url = (f"https://graph.facebook.com/{report.API_VERSION}/debug_token?"
           + urllib.parse.urlencode({"input_token": tok,
                                     "access_token": f"{app_id}|{app_secret}"}))
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            d = json.loads(r.read().decode("utf-8"))
        return d.get("data") or {}, None
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode("utf-8")).get("error", {})
        except Exception:
            err = {"message": f"HTTP {e.code}"}
        return None, err.get("message") or str(err)
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def _kiem_quyen_thuc_te(env):
    """Goi Meta doc thu 1 nhom — chung minh token THUC SU dung duoc, khong chi doc mo ta."""
    tok = (env or {}).get("META_ADS_ACCESS_TOKEN", "").strip()
    acc = (env or {}).get("META_AD_ACCOUNT_ID", "").strip()
    if not acc.startswith("act_"):
        acc = "act_" + acc
    du, loi = report.api_get(f"{acc}/adsets", {
        "access_token": tok, "fields": "id,name", "limit": 1})
    if loi:
        return False, report.mo_ta_loi(loi) if hasattr(report, "mo_ta_loi") else str(loi)
    return True, f"doc duoc {len((du or {}).get('data', []) or [])} nhom thu"


def main():
    print()
    _duong_ke()
    print("  KIEM TRA TOKEN META")
    _duong_ke()
    print()

    env = _doc_env()
    tok = (env or {}).get("META_ADS_ACCESS_TOKEN", "").strip()
    if not tok:
        print("[LOI] Khong tim thay META_ADS_ACCESS_TOKEN trong file .env")
        print()
        print("  Cach xu ly: bam dup vao 'mo-file-env.bat' de mo .env,")
        print("  kiem tra dong META_ADS_ACCESS_TOKEN= co token chua.")
        print()
        return 1

    print(f"  File .env .......... {ENV_PATH}")
    print(f"  Token dai .......... {len(tok)} ky tu")
    print(f"  Bat dau bang ....... {tok[:12]}...")
    print()

    data, loi = _debug_token(tok, (env or {}).get("META_APP_ID", ""),
                             (env or {}).get("META_APP_SECRET", ""))
    if loi:
        print("[LOI] Khong hoi duoc Meta ve token nay.")
        print(f"      Chi tiet: {loi}")
        print()
        print("  Cach xu ly: token co the sai hoac bi cat cut khi dan vao .env.")
        print("  Lam lai buoc tao token (Phan C, muc C5) roi dan lai that can than.")
        print()
        return 1

    loai = str(data.get("type") or "?").upper()
    hop_le = data.get("is_valid")
    app_ten = data.get("application") or "(khong ro)"
    app_id_mt = data.get("app_id")
    user_id = data.get("user_id")
    scopes = data.get("scopes") or []
    het_han = data.get("expires_at")

    # ---------- 1. TOKEN CA NHAN HAY TOKEN APP ----------
    _duong_ke()
    print("  1. LOAI TOKEN")
    _duong_ke()
    print(f"  Meta bao ........... type = {loai}")
    print(f"  Ung dung ........... {app_ten} (id {app_id_mt})")
    if user_id:
        print(f"  Thuoc nguoi dung ... id {user_id}  <- day la Tai khoan ca nhan")
    print()

    if loai == "USER":
        print("  ⚠️  VAN LA TOKEN CA NHAN — CHUA DOI DUOC")
        print()
        print("  Nghia la: moi thao tac cua agent VAN bi Meta ghi ten Dai.")
        print()
        print("  Cach xu ly:")
        print("    - Kiem tra lai Phan D1: da dan token MOI vao .env chua?")
        print("    - Chu y .env co 4 file giong nhau (.env, .env.example,")
        print("      .env.bak, .env.bak-truoc-gd2). Chi duoc sua file '.env'.")
    elif loai in ("SYSTEM_USER", "APP", "BUSINESS", "PAGE", "INSTAGRAM"):
        print(f"  ✅ TOKEN APP — DA DUNG (loai {loai})")
        print()
        print("  Nghia la: tu gio Meta ghi ro thao tac nao do HE THONG lam,")
        print("  tach bach han voi Dai. Khong con lan nua.")
    else:
        print(f"  ℹ️  Loai token la '{loai}' — khong nam trong hai loai quen thuoc.")
        print("      Cu chay tiep phan kiem tra quyen ben duoi de biet co dung duoc khong.")
    print()

    # ---------- 2. HAN DUNG ----------
    _duong_ke()
    print("  2. HAN DUNG")
    _duong_ke()
    if not het_han:
        print("  ✅ KHONG BAO GIO HET HAN")
        print("     Day la uu diem lon nhat cua token App — khong phai gia han")
        print("     moi 60 ngay nhu token ca nhan nua.")
    elif isinstance(het_han, (int, float)) and het_han > 0:
        luc = datetime.fromtimestamp(het_han)
        con = (luc - datetime.now()).days
        print(f"  Het han luc ........ {luc.strftime('%H:%M ngay %d/%m/%Y')}")
        if con < 0:
            print(f"  ❌ DA HET HAN {-con} ngay truoc!")
            print()
            print("  Cach xu ly: tao token moi (Phan C) roi dan lai vao .env.")
        elif con <= 7:
            print(f"  ⚠️  CHI CON {con} NGAY — sap het han, nen tao token moi ngay.")
        else:
            print(f"  ✅ Con khoang {con} ngay.")
    print()

    # ---------- 3. QUYEN ----------
    _duong_ke()
    print("  3. QUYEN")
    _duong_ke()
    if scopes:
        for s in scopes:
            can = "  (can thiet)" if s in QUYEN_CAN else ""
            print(f"  - {s}{can}")
    else:
        print("  (Meta khong tra ve danh sach quyen)")
    print()
    thieu = [q for q in QUYEN_CAN if q not in scopes] if scopes else []
    if thieu:
        print(f"  ❌ THIEU QUYEN: {', '.join(thieu)}")
        print()
        print("  Cach xu ly: lam lai buoc C5, nho tick du 3 quyen:")
        print("    ads_management, ads_read, business_management")
    elif scopes:
        print("  ✅ DU QUYEN CAN THIET")
    print()

    # ---------- 4. THU DOC THAT ----------
    _duong_ke()
    print("  4. THU DOC THAT TU META (chung minh token dung duoc)")
    _duong_ke()
    ok, msg = _kiem_quyen_thuc_te(env)
    if ok:
        print(f"  ✅ DOC DUOC — {msg}")
    else:
        print("  ❌ KHONG DOC DUOC")
        print(f"     Chi tiet: {msg}")
        print()
        print("  Cach xu ly thuong gap nhat: chua GAN TAI KHOAN QUANG CAO cho")
        print("  nguoi dung he thong (buoc C4 trong HUONG-DAN-LAY-TOKEN-APP.md).")
        print("  Token tao ra nhung khong gan tai san thi khong co quyen gi.")
    print()

    # ---------- KET LUAN ----------
    _duong_ke()
    print("  KET LUAN")
    _duong_ke()
    if loai != "USER" and ok and not thieu and hop_le:
        print()
        print("  ✅ TOKEN APP — DAT YEU CAU")
        print()
        print("  Buoc cuoi: bam dup vao 'khoi-dong-lai-agent.bat' de nap token moi.")
        print()
        _duong_ke()
        return 0
    if loai == "USER" and ok:
        print()
        print("  ⚠️  VAN LA TOKEN CA NHAN")
        print()
        print("  Token van dung duoc (agent chay binh thuong), NHUNG Meta van ghi")
        print("  ten Dai cho moi thao tac. Muon tach bach thi phai doi sang token App.")
        print()
        _duong_ke()
        return 0
    print()
    print("  ❌ CO VAN DE — xem muc 'Cach xu ly' o tung phan ben tren.")
    print()
    _duong_ke()
    return 1


if __name__ == "__main__":
    sys.exit(main())
