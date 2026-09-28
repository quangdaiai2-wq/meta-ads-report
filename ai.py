"""
LOP AI CUA BAO CAO META ADS
============================
Mot viec duy nhat: bien SO LIEU DA TINH SAN thanh 3-5 cau nhan dinh tieng Viet.

Nguyen tac bat buoc:
  - KHONG tu goi Meta. So lieu do report.py tinh roi truyen vao.
  - KHONG bao gio nem loi ra ngoai. AI loi thi bao cao van phai gui duoc.
  - KHONG gui token hay thong tin dang nhap cho AI. Ham soan_prompt() khong
    nhan tham so env, nen ve cau truc no khong the lam lo token.
  - PHEP SO SANH DO CODE LAM, khong giao cho AI. Ly do: khi AI phai tu doi
    chieu hai dong so voi nhau, no de doc sai ma cau van van troi chay. Khi
    code tinh san cot 'chenh lech', AI chi chep lai. Da thu that 28/09/2026.

Nha cung cap: Gemini. Chia khoa doc tu khoa GEMINI_API_KEY trong .env.
"""
import json
import time
import urllib.error
import urllib.parse
import urllib.request

# Ten model mac dinh. Doi duoc bang khoa GEMINI_MODEL trong .env.
# Gia tri nay DA DUOC THU THAT ngay 28/09/2026 voi chia khoa cua Dai.
# Ten model Gemini thay doi theo thoi gian, nen KHONG viet cung trong code.
MODEL_MAC_DINH = "gemini-3.6-flash"

BASE = "https://generativelanguage.googleapis.com/v1beta/models"

# Thoi gian toi da cho mot lan goi AI (giay). Bao cao khong duoc tre vi AI.
TIMEOUT = 60

# Gemini thinh thoang tra 503 (qua tai) - da gap that. Chi thu lai voi 503/429.
#
# SO_LAN_THU_LAI = 2 chu khong phai 1: khi thi cong ngay 28/09/2026, lan goi
# DAU TIEN trong buoc kiem chung tra 503 HAI LAN LIEN TIEP (thu lai 1 lan van
# hong), phai chay lai ca tien trinh moi duoc. Do la mat phan nhan dinh mot
# cach khong dang co.
#
# Chi phi cua viec thu lai: cham nhat 2 lan cho + 3 lan goi. Voi TIMEOUT=60
# thi cham nhat khoang 3*60 + 2*5 = 190 giay. Bao cao chay theo moc gio co
# dinh nen muc tre nay chap nhan duoc - doi lai ti le co duoc phan nhan dinh
# cao hon han.
SO_LAN_THU_LAI = 2
CHO_GIUA_HAI_LAN = 5

# So ngay lay lam ky so sanh (chi dung cho bao cao TRON ngay).
SO_NGAY_KY_TRUOC = 7

# Cac chi so dua vao bang so sanh: (khoa trong stats, ten hien cho AI, kieu)
TEN_CHI_SO = [
    ("spend", "chi tieu (dong)", "tien"),
    ("msg", "tin nhan moi", "so"),
    ("contact", "lien he moi", "so"),
    ("order", "don hang", "so"),
    ("purchase", "luot mua", "so"),
    ("payment", "luot thanh toan", "so"),
    ("comment", "binh luan", "so"),
]

# Cac dau ngoac nay KHONG duoc xuat hien trong HUONG_DAN, neu khong thi khong
# the kiem bang assertNotIn duoc (da bi bat boi buoc dung thu).
KHONG_SO_SANH = "(khong so sanh)"
KY_TRUOC_BANG_0 = "(ky truoc bang 0)"

HUONG_DAN = (
    "Ban la nguoi viet bao cao quang cao cho mot chu shop Viet Nam.\n"
    "Hay viet 3 den 5 cau tieng Viet nhan xet ve so lieu trong BANG duoi day.\n"
    "\n"
    "Quy tac bat buoc:\n"
    "- Moi con so ban viet ra PHAI chep nguyen tu BANG. Khong tu tinh, khong "
    "uoc luong, khong lam tron, khong suy ra so nao khac.\n"
    "- Cot 'chenh lech' trong bang da duoc tinh san. Chep nguyen, dung tu tinh lai.\n"
    "- Neu bang ghi 'khong so sanh' thi chi mo ta, TUYET DOI khong so sanh.\n"
    "- Cau ngan, de hieu, tranh tu chuyen mon. Nguoi doc khong biet ky thuat.\n"
    "- Chi tra ve phan nhan xet, khong chao hoi, khong giai thich ban la ai.\n"
)


def fmt_tien(v):
    """Dinh dang tien kieu Viet Nam: 7034942.0 -> '7.034.942'."""
    try:
        return f"{int(round(float(v))):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "0"


def _fmt_so(v, kieu):
    return fmt_tien(v) if kieu == "tien" else str(int(v or 0))


def bang_so_sanh(stats, ky_truoc):
    """Dung bang so sanh - CODE tinh, AI chi doc.

    Day la cho quan trong nhat cua ai.py. Neu de AI tu doi chieu hai dong so
    thi no de doc sai. Code tinh san cot 'chenh lech' thi AI chi con chep lai.
    """
    hien_tai = (stats or {}).get("totals") or {}
    co_ky_truoc = bool((ky_truoc or {}).get("so_ngay"))
    truoc = (ky_truoc or {}).get("tong") or {}

    lines = ["chi so | ky nay | ky truoc | chenh lech"]
    for khoa, ten, kieu in TEN_CHI_SO:
        nay = _fmt_so(hien_tai.get(khoa, 0), kieu)
        if not co_ky_truoc:
            lines.append(f"{ten} | {nay} | (khong co) | {KHONG_SO_SANH}")
            continue
        cu_so = float(truoc.get(khoa, 0) or 0)
        moi_so = float(hien_tai.get(khoa, 0) or 0)
        cu = _fmt_so(cu_so, kieu)
        chenh = moi_so - cu_so
        if cu_so:
            phan_tram = chenh / cu_so * 100
            dau = "+" if chenh >= 0 else "-"
            lines.append(
                f"{ten} | {nay} | {cu} | {dau}{_fmt_so(abs(chenh), kieu)} "
                f"({dau}{abs(phan_tram):.0f}%)"
            )
        else:
            lines.append(f"{ten} | {nay} | {cu} | {KY_TRUOC_BANG_0}")
    return "\n".join(lines)


def soan_prompt(stats, ky_truoc, boi_canh):
    """Ghep so lieu thanh cau lenh cho AI.

    KHONG nhan env -> khong the lam lo token.
    """
    stats = stats or {}
    lines = [HUONG_DAN, "", "--- BOI CANH ---", str(boi_canh or "")]
    lines.append("")
    lines.append("--- BANG SO LIEU ---")
    lines.append(bang_so_sanh(stats, ky_truoc))

    camps = stats.get("all") or []
    if camps:
        lines.append("")
        lines.append("--- TUNG CAMPAIGN (ten | chi tieu | luot mua) ---")
        for c in camps[:20]:
            lines.append(
                f"- {c.get('name', '?')} | {fmt_tien(c.get('spend', 0))} d "
                f"| {c.get('purchase', 0)}"
            )
    return "\n".join(lines)


def doc_cau_tra_loi(du_lieu_tra_ve):
    """Boc phan chu ra khoi JSON Gemini tra ve. Hong gi -> tra ve chuoi rong.

    Tach rieng vi cau truc JSON cua Gemini co the doi, va vi kiem thu phai
    kiem duoc truong hop JSON la ma khong can goi mang.
    """
    try:
        return du_lieu_tra_ve["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError, TypeError, AttributeError):
        return ""


def _goi_mang_that(url, payload, timeout):
    """Goi Gemini that. Tach rieng de kiem thu thay duoc bang ham gia."""
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def goi_gemini(env, prompt, timeout=None, goi_mang_fn=None):
    """Goi Gemini mot lan (co thu lai khi qua tai). Tra ve (chu, loi).

    KHONG BAO GIO nem loi ra ngoai: moi loi deu tra ve qua kenh `loi`.
    """
    env = env or {}
    key = str(env.get("GEMINI_API_KEY", "")).strip()
    if not key:
        return None, "thieu GEMINI_API_KEY trong .env"
    model = str(env.get("GEMINI_MODEL", "")).strip() or MODEL_MAC_DINH
    url = f"{BASE}/{model}:generateContent?key=" + urllib.parse.quote(key)
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    goi = goi_mang_fn or _goi_mang_that

    du_lieu = None
    for lan in range(SO_LAN_THU_LAI + 1):
        try:
            du_lieu = goi(url, payload, timeout or TIMEOUT)
            break
        except urllib.error.HTTPError as e:
            loi = f"HTTP {e.code}"
            if e.code in (503, 429) and lan < SO_LAN_THU_LAI:
                time.sleep(CHO_GIUA_HAI_LAN)
                continue
            return None, loi
        except Exception as e:
            return None, str(e)

    text = doc_cau_tra_loi(du_lieu)
    if not text:
        return None, "AI tra ve rong hoac sai cau truc"
    return text, None


def viet_nhan_dinh(stats, ky_truoc=None, boi_canh="", env=None, goi_mang_fn=None):
    """Viet 3-5 cau nhan dinh. Tra ve (chu, loi). Khong bao gio nem loi."""
    try:
        prompt = soan_prompt(stats, ky_truoc, boi_canh)
    except Exception as e:
        return None, f"khong soan duoc cau lenh cho AI: {e}"
    return goi_gemini(env, prompt, goi_mang_fn=goi_mang_fn)
