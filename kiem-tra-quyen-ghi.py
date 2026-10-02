"""
KIEM TRA QUYEN GHI CUA TOKEN META
==================================
Tra loi cau hoi: token Meta trong .env co quyen TAM DUNG chien dich quang cao
hay khong (quyen `ads_management`).

Vi sao can rieng mot script:
    kiem-tra-token.py chi kiem quyen DOC (ads_read). Mot token doc tot hoan
    toan co the KHONG ghi duoc gi. Do that ngay 29/09/2026: token cua Dai co
    ads_read nhung KHONG co ads_management.

=== BAI HOC QUAN TRONG: KHONG THE KIEM QUYEN GHI BANG LENH VO HAI ===

Da thu that 4 cach ngay 30/09/2026, tren chinh token cua Dai (biet chac la
THIEU quyen ghi), de xem cach nao phan biet duoc. KET QUA: KHONG cach nao.

  1. POST /act_<id>/campaigns voi body rong
     -> (#100) The parameter special_ad_categories is required.
        Meta bao loi THAM SO truoc, khong he nhac toi quyen.
  2. POST /<campaign id khong ton tai> voi status=PAUSED
     -> (#100) Object ... does not exist, cannot be loaded due to missing
        permissions, or does not support this operation.
  3. POST /act_<id> voi name rong
     -> cung mot cau gop nhu tren.
  4. POST /act_<id> voi name = DUNG TEN DANG CO (khong doi gi)
     -> cung mot cau gop nhu tren.

Meta CO Y gop nhieu nguyen nhan vao MOT cau de khong lo thong tin. Nen moi
cach "gui lenh ghi vo hai roi doc ma loi" deu VO GIA TRI: no bao "thieu tham
so" hoac "khong ro", chu khong bao "thieu quyen".

=> VI vay script nay chi dua vao DANH SACH QUYEN Meta cap cho token. Do la
   nguon dang tin duy nhat. Muon chac chan tuyet doi thi phai GHI THAT len mot
   doi tuong that - va viec do chi nen lam khi Dai da dong y, tren mot chien
   dich Dai da muon tat. Xem phan "GIOI HAN" in ra o cuoi script.

Cach dung:
    python kiem-tra-quyen-ghi.py

Script CHI DOC. Khong tao, khong sua, khong xoa gi. Khong gui tin nhan nao.
Token khong bao gio bi in day du ra man hinh (chi hien 4 ky tu dau).
"""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ENV_PATH = Path(__file__).parent / ".env"
API_VERSION = "v26.0"
GRAPH = f"https://graph.facebook.com/{API_VERSION}"

QUYEN_DOC = "ads_read"
QUYEN_GHI = "ads_management"


def load_env(path):
    """Doc .env. Khong bao gio nem loi."""
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


def rut_gon(token):
    """Chi hien 4 ky tu dau. Khong bao gio in token day du."""
    t = str(token or "")
    return (t[:4] + "...") if len(t) > 4 else "(rong)"


def goi_graph(path, params):
    """Goi Graph API (chi doc). Tra ve (du_lieu, loi, ma_http). Khong nem loi."""
    url = f"{GRAPH}/{path}?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.loads(r.read().decode("utf-8")), None, r.status
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            j = json.loads(body)
        except Exception:
            j = {"raw": body[:300]}
        return None, j, e.code
    except Exception as e:
        return None, {"loi_mang": str(e)}, None


def doc_quyen(env):
    """Doc danh sach quyen dang co. Tra ve (dict_quyen, ghi_chu_loi)."""
    token = env.get("META_ADS_ACCESS_TOKEN", "").strip()
    du_lieu, loi, ma = goi_graph("me/permissions", {"access_token": token})
    if du_lieu is None:
        return None, f"HTTP {ma} | {json.dumps(loi, ensure_ascii=False)[:200]}"
    quyen = {}
    for x in du_lieu.get("data", []):
        quyen[x.get("permission")] = x.get("status")
    return quyen, None


def main():
    env = load_env(ENV_PATH)

    print("=" * 64)
    print("KIEM TRA QUYEN GHI CUA TOKEN META")
    print("=" * 64)

    token = env.get("META_ADS_ACCESS_TOKEN", "").strip()
    if not token:
        print()
        print("LOI: Chua co META_ADS_ACCESS_TOKEN trong .env")
        print("Cach xu ly: bam dup mo-file-env.bat roi dien token vao.")
        sys.exit(1)

    print(f"Token dang dung     : {rut_gon(token)} (dai {len(token)} ky tu)")
    print(f"Tai khoan quang cao : {env.get('META_AD_ACCOUNT_ID', '(chua dien)')}")
    print()

    # --- 1. Danh sach quyen Meta da cap ---
    print("[1/2] Danh sach quyen Meta da cap cho token nay...")
    quyen, ghi_chu = doc_quyen(env)
    if quyen is None:
        print(f"  [LOI] Khong doc duoc: {ghi_chu}")
        print()
        print("  => Chua ket luan duoc. Kiem tra mang roi chay lai.")
        print("     Neu van loi: co the token da het han. Chay kiem-tra-token.bat")
        sys.exit(1)

    for ten in sorted(quyen):
        dau = "OK" if quyen[ten] == "granted" else "--"
        print(f"  [{dau}] {ten} = {quyen[ten]}")

    co_doc = quyen.get(QUYEN_DOC) == "granted"
    co_ghi = quyen.get(QUYEN_GHI) == "granted"
    print()
    print(f"  Quyen DOC chien dich  ({QUYEN_DOC}) : {'CO' if co_doc else 'KHONG'}")
    print(f"  Quyen GHI chien dich  ({QUYEN_GHI}) : {'CO' if co_ghi else 'KHONG'}")
    print()

    # --- 2. Tai khoan quang cao co doc duoc khong ---
    print("[2/2] Doc thu tai khoan quang cao...")
    acc = env.get("META_AD_ACCOUNT_ID", "").strip()
    ten_tk, trang_thai = "(khong doc duoc)", None
    if acc:
        # Tai khoan quang cao tren Graph API phai co tien to "act_".
        # Thieu tien to se bao HTTP 400 "object does not exist" du token dung.
        du_lieu, loi, ma = goi_graph("act_" + acc, {
            "access_token": token, "fields": "name,account_status"})
        if du_lieu:
            ten_tk = du_lieu.get("name", "?")
            trang_thai = du_lieu.get("account_status")
        else:
            print(f"  [LOI] HTTP {ma} | "
                  f"{json.dumps(loi, ensure_ascii=False)[:160]}")
    if ten_tk != "(khong doc duoc)":
        # account_status = 1 nghia la dang hoat dong binh thuong.
        nghia = {1: "dang hoat dong binh thuong",
                 2: "bi vo hieu hoa", 3: "bi han che",
                 7: "dang cho xet duyet", 9: "bi dong do chua thanh toan"}
        print(f"  Ten tai khoan : {ten_tk}")
        print(f"  Tinh trang    : {trang_thai} - {nghia.get(trang_thai, 'khong ro')}")
    print()

    # --- Ket luan ---
    print("=" * 64)
    if co_ghi:
        print("KET LUAN: TOKEN DA DUOC CAP QUYEN GHI (ads_management).")
        print()
        print("  Buoc tiep theo: bao tro ly biet. Viec dau tien se lam la kiem")
        print("  chung that - tat thu MOT chien dich ma Dai da dong y tat.")
        print()
        print("  GIOI HAN phai biet: danh sach quyen noi la CO, nhung chua chac")
        print("  lanh nghe da ghi duoc that. Ly do: Meta gop moi loi vao mot cau")
        print("  nen khong the thu truoc bang lenh vo hai. Cach kiem chung duy")
        print("  nhat la lam that mot lan, tren chien dich Dai da muon tat.")
    else:
        print("KET LUAN: TOKEN CHUA CO QUYEN GHI.")
        print()
        print("  Nghia la: he thong CHUA the tam dung chien dich nao.")
        print("  Cach xu ly: lam theo file HUONG-DAN-LAY-TOKEN-QUYEN-GHI.md")
        print("             (lay token moi co tick quyen ads_management).")
    print("=" * 64)

    return 0 if co_ghi else 3


if __name__ == "__main__":
    sys.exit(main())
