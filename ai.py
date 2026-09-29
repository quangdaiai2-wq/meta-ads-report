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

# Model RIENG cho phan hoi dap. Ly do: tran mien phi cua Gemini tinh rieng cho
# tung model (quotaId: GenerateRequestsPerDayPerProjectPerModel-FreeTier, do
# duoc 20 luot/ngay). Neu dung chung model voi bao cao thi moi cau hoi cua Dai
# se an vao tran cua bao cao, lam bao cao mat phan nhan dinh.
#
# gemini-3.8-flash DA DUOC THU THAT ngay 29/09/2026: goi duoc cong cu.
# gemini-2.5-flash KHONG dung duoc nua (404: no longer available to new users).
MODEL_HOI_DAP_MAC_DINH = "gemini-3.8-flash"

# Model du phong, dung khi model chinh bi 503/404/429. De trong thi khong dung.
# gemini-3.5-flash cung DA THU THAT ngay 29/09/2026: goi duoc cong cu.
MODEL_HOI_DAP_DU_PHONG_MAC_DINH = "gemini-3.5-flash"

# Model DU PHONG cho phan NHAN DINH trong bao cao.
#
# Vi sao can: ngay 29/09/2026, model bao cao `gemini-3.6-flash` tra HTTP 503
# (qua tai) BA LAN LIEN TIEP trong buoi chieu (12:00, 15:48, 15:49) — moi lan
# da thu lai 3 luot theo SO_LAN_THU_LAI ma van hong. Trong khi do do tung model
# mot thi `gemini-3.5-flash` VAN CHAY TOT. Khong co du phong thi bao cao mat
# phan nhan dinh suot nhieu gio, ma Dai khong biet vi sao.
#
# Tran mien phi tinh RIENG cho tung model (20 luot/ngay/model), nen dung du
# phong KHONG an vao luot cua model chinh.
MODEL_BAO_CAO_DU_PHONG_MAC_DINH = "gemini-3.5-flash"

# So luot AI duoc phep xin goi cong cu truoc khi bi buoc phai tra loi.
#
# Vi sao 3: phep thu that ngay 29/09/2026 cho thay AI can DUNG 3 luot cong cu
# (xep_hang_camp -> lay_khoang ky truoc -> lay_khoang ky nay) roi tra loi o luot
# thu 4. Dat 3 la vua du va khop bang chung. Dat 5 nhu ban thiet ke thi mot cau
# hoi ton 6 luot AI => chi 3 cau hoi la het tran 20 luot/ngay.
TOI_DA_LUOT_CONG_CU = 3

# Thoi gian toi da cho mot luot goi AI khi tra loi cau hoi (giay).
# Ngan hon TIMEOUT cua bao cao: nguoi dang cho tin nhan, khong the doi 60 giay.
#
# NANG tu 30 len 45 ngay 29/09/2026: Dai nhan hoi luc 12:00, Gemini dang qua tai,
# va ca hai model deu het thoi gian cho (30 giay khong du). 45 giay van du ngan
# de Dai khong phai cho qua lau.
TIMEOUT_HOI_DAP = 45

# Ngan sach thoi gian cho MOT cau hoi (giay). Het thi BO CUOC va tra loi Dai,
# khong treo Nguoi truc vo han.
#
# Vi sao can: ngay 29/09/2026 luc 12:00, Gemini qua tai toan he thong (bao cao
# 12h cung gap HTTP 503). Neu moi luot AI deu cho het thoi gian roi thu lai thi
# mot cau hoi co the treo Nguoi truc hang chuc phut - trong luc do MOC GIO BI
# CHAN, tuc la bao cao co the bi tre.
THOI_GIAN_TOI_DA_HOI_DAP = 180

# Ma loi HTTP TAM THOI - thu lai duoc. Cac ma khac (400, 403, 404) la loi VINH
# VIEN: thu lai chi ton thoi gian, phai doi model hoac bao loi ngay.
MA_LOI_TAM_THOI = (429, 500, 502, 503, 504)

# Tran token cho mot cau tra loi.
#
# NANG tu 2000 len 4000 ngay 29/09/2026 sau khi DO THAT: model Gemini 3.x tinh
# ca token SUY NGHI (`thoughtsTokenCount`) vao tran nay. Do duoc that:
#   786, 829, 477, 1132, 573 token chi rieng cho phan suy nghi, moi luot.
# Voi tran 2000 thi luot CUOI (luc model viet cau tra loi dai) bi cat giua
# dong - da xay ra that: cau tra loi dung o "...la 20" roi het.
#
# Cach chua khac da can nhac nhung CHUA KIEM CHUNG duoc (het han muc AI trong
# ngay): dat `thinkingConfig.thinkingBudget = 0` de tat suy nghi. Neu sau nay
# muon thu, nho rang gui truong la vao `generationConfig` co the bi loi 400
# voi model khong ho tro.
TOI_DA_TOKEN_TRA_LOI = 4000

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

# Cau lenh nay viet CO DAU, khac voi cac chuoi ky thuat khac trong file.
# Ly do: Gemini bat chuoc giong van cua chinh cau lenh. Khi cau lenh viet
# khong dau thi no cung tra ve khong dau (da gap that ngay 28/09/2026), trong
# khi nguoi doc bao cao can chu co dau cho de doc. Gap khoang 50/50 nen phai
# ghi thanh quy tac ro rang, khong the dua vao may man.
HUONG_DAN = (
    "Bạn là người viết báo cáo quảng cáo cho một chủ shop Việt Nam.\n"
    "Hãy viết 3 đến 5 câu tiếng Việt nhận xét về số liệu trong BẢNG dưới đây.\n"
    "\n"
    "Quy tắc bắt buộc:\n"
    "- Viết tiếng Việt CÓ DẤU đầy đủ, như người Việt đọc hằng ngày. "
    "Tuyệt đối không viết kiểu không dấu.\n"
    "- Mọi con số bạn viết ra PHẢI chép nguyên từ BẢNG. Không tự tính, không "
    "ước lượng, không làm tròn, không suy ra số nào khác.\n"
    "- Cột 'chenh lech' trong bảng đã được tính sẵn. Chép nguyên, đừng tự tính lại.\n"
    "- Nếu bảng ghi 'khong so sanh' thì chỉ mô tả, TUYỆT ĐỐI không so sánh.\n"
    "- Câu ngắn, dễ hiểu, tránh từ chuyên môn. Người đọc không biết kỹ thuật.\n"
    "- Chỉ trả về phần nhận xét, không chào hỏi, không giải thích bạn là ai.\n"
)

# Cau lenh cho phan HOI DAP (khac phan viet bao cao o tren).
#
# Viet CO DAU, cung ly do nhu HUONG_DAN: Gemini bat chuoc giong van cua chinh
# cau lenh. Cau lenh khong dau thi no tra ve khong dau.
HUONG_DAN_HOI_DAP = (
    "Bạn là trợ lý trả lời câu hỏi về số liệu quảng cáo cho một chủ shop Việt Nam.\n"
    "\n"
    "Quy tắc bắt buộc:\n"
    "- Viết tiếng Việt CÓ DẤU đầy đủ. Tuyệt đối không viết kiểu không dấu.\n"
    "- MỌI con số bạn viết ra phải lấy nguyên từ kết quả công cụ. Không tự "
    "tính, không ước lượng, không suy diễn, không làm tròn thành số khác.\n"
    "- SỐ TIỀN phải chép từ trường có chữ 'hien_thi' (ví dụ '20.319.895'). "
    "Các trường số thô chỉ để đối chiếu, KHÔNG viết số thô vào câu trả lời.\n"
    "- Tên chiến dịch phải chép y nguyên từng ký tự. Không thêm khoảng trắng "
    "quanh dấu gạch nối, không viết lại tên theo cách của bạn.\n"
    "- Nếu công cụ báo không có dữ liệu thì nói thẳng là không có. Không bịa.\n"
    "- Dùng đúng khoảng ngày ghi ở phần MỐC THỜI GIAN. Không tự chọn khoảng khác.\n"
    "- Khi nói về số của một phần ngày (day_du_ca_ngay = false) thì phải nói rõ "
    "là số mới tích lũy đến lúc đó, chưa phải cả ngày.\n"
    "- Trả lời ngắn gọn: tối đa 8 câu, viết thành đoạn văn liền mạch.\n"
    "- TUYỆT ĐỐI KHÔNG dùng dấu sao, dấu thăng, gạch đầu dòng hay bảng biểu. "
    "Đây là tin nhắn Telegram, các ký hiệu đó hiện ra rất rối.\n"
    "- Đi thẳng vào câu trả lời. Không chào hỏi, không giới thiệu bản thân.\n"
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
        lines.append(
            "--- TUNG CAMPAIGN (ten | chi tieu | luot mua | chi phi moi don) ---"
        )
        for c in camps[:20]:
            cpr = c.get("cpr")
            # Chi phi moi don duoc code tinh san (report.pack). Chua co don thi
            # ghi ro "chua co don" - KHONG ghi 0, vi 0 trong nhu re nhat.
            gia = f"{fmt_tien(cpr)} d" if cpr else "chua co don"
            lines.append(
                f"- {c.get('name', '?')} | {fmt_tien(c.get('spend', 0))} d "
                f"| {c.get('purchase', 0)} don | chi phi moi don: {gia}"
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


# Dich vai ma loi hay gap sang tieng Viet, de dong ghi chu trong bao cao
# thuc su co ich. Truoc day loi chi ghi "HTTP 429" - Dai doc khong biet
# la het han muc hay sai chia khoa.
Y_NGHIA_LOI = {
    400: "chia khoa AI sai, hoac cau lenh khong hop le",
    403: "chia khoa AI bi tu choi",
    404: "ten model AI khong dung (xem HUONG-DAN-LAY-CHIA-KHOA-AI.md)",
    429: "het han muc goi AI, thu lai sau",
    503: "may chu AI dang qua tai",
}


def _trang_thai_loi(e):
    """Boc truong `error.status` trong phan than loi (vi du RESOURCE_EXHAUSTED).

    Khong bao gio nem loi: doc khong duoc thi tra ve chuoi rong.
    """
    try:
        body = e.read().decode("utf-8", "replace")
    except Exception:
        return ""
    try:
        return str((json.loads(body).get("error") or {}).get("status", "")).strip()
    except Exception:
        return ""


def _goi_mang_that(url, payload, timeout):
    """Goi Gemini that. Tach rieng de kiem thu thay duoc bang ham gia."""
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _goi_gemini_than(env, payload_them, model, timeout, goi_mang_fn):
    """Goi Gemini voi phan payload tuy y. Tra ve (du_lieu_json, loi).

    KHONG BAO GIO nem loi ra ngoai: moi loi deu tra ve qua kenh `loi`.

    Tach rieng khoi goi_gemini() vi phan hoi dap can gui kem `tools` va doc
    nguyen `content` cua model, khong chi doc phan chu.
    """
    env = env or {}
    key = str(env.get("GEMINI_API_KEY", "")).strip()
    if not key:
        return None, "thieu GEMINI_API_KEY trong .env"

    model = str(model or "").strip() or MODEL_MAC_DINH
    url = f"{BASE}/{model}:generateContent?key=" + urllib.parse.quote(key)
    goi = goi_mang_fn or _goi_mang_that

    for lan in range(SO_LAN_THU_LAI + 1):
        try:
            return goi(url, payload_them, timeout or TIMEOUT), None
        except urllib.error.HTTPError as e:
            loi = f"HTTP {e.code}"
            y_nghia = Y_NGHIA_LOI.get(e.code)
            if y_nghia:
                loi += f" - {y_nghia}"
            trang_thai = _trang_thai_loi(e)
            if trang_thai:
                loi += f" [{trang_thai}]"
            if e.code in MA_LOI_TAM_THOI and lan < SO_LAN_THU_LAI:
                time.sleep(CHO_GIUA_HAI_LAN)
                continue
            return None, loi
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            # Het thoi gian cho hoac loi mang: TAM THOI, thu lai duoc.
            #
            # Da gap that ngay 29/09/2026 luc 12:00: Gemini qua tai, Dai nhan
            # hoi, va ca hai model deu tra ve 'The read operation timed out'.
            # Truoc khi sua, nhanh nay roi thang xuong `except Exception` va
            # TRA LOI NGAY, khong thu lai - nen mot lan mang chap chon la Dai
            # mat cau tra loi.
            loi = f"loi mang hoac het thoi gian cho: {e}"
            if lan < SO_LAN_THU_LAI:
                time.sleep(CHO_GIUA_HAI_LAN)
                continue
            return None, loi
        except Exception as e:
            return None, str(e)
    return None, "da thu lai nhieu lan nhung van loi"


def goi_gemini(env, prompt, timeout=None, goi_mang_fn=None, model=None):
    """Goi Gemini mot lan (co thu lai khi qua tai). Tra ve (chu, loi).

    KHONG BAO GIO nem loi ra ngoai: moi loi deu tra ve qua kenh `loi`.
    """
    env = env or {}
    model = str(model or env.get("GEMINI_MODEL", "")).strip() or MODEL_MAC_DINH
    du_lieu, loi = _goi_gemini_than(
        env, {"contents": [{"parts": [{"text": prompt}]}]},
        model, timeout, goi_mang_fn,
    )
    if loi:
        return None, loi
    text = doc_cau_tra_loi(du_lieu)
    if not text:
        return None, "AI tra ve rong hoac sai cau truc"
    return text, None


def chon_model_bao_cao(env):
    """Danh sach model se thu cho phan NHAN DINH, theo thu tu. Chinh truoc, du phong sau."""
    env = env or {}
    chinh = str(env.get("GEMINI_MODEL", "")).strip() or MODEL_MAC_DINH
    du_phong = (str(env.get("GEMINI_MODEL_BAO_CAO_DU_PHONG", "")).strip()
                or MODEL_BAO_CAO_DU_PHONG_MAC_DINH)
    ds = [chinh]
    if du_phong and du_phong != chinh:
        ds.append(du_phong)
    return ds


def viet_nhan_dinh(stats, ky_truoc=None, boi_canh="", env=None, goi_mang_fn=None):
    """Viet 3-5 cau nhan dinh. Tra ve (chu, loi). Khong bao gio nem loi.

    Thu LAN LUOT model chinh roi model du phong. Ly do co du phong: da gap that
    ngay 29/09/2026 - model bao cao tra 503 ba lan lien tiep trong buoi chieu,
    trong khi model khac van chay tot. Khong co du phong thi bao cao mat phan
    nhan dinh suot nhieu gio.

    Du phong nam o DAY chu khong nam trong goi_gemini(): goi_gemini() la ham
    dung chung, nhet vong lap model vao do se lam moi loi goi deu ton gap doi
    va lam hong cac bai kiem thu dem so lan goi.
    """
    try:
        prompt = soan_prompt(stats, ky_truoc, boi_canh)
    except Exception as e:
        return None, f"khong soan duoc cau lenh cho AI: {e}"

    loi_da_gap = []
    for model in chon_model_bao_cao(env):
        chu, loi = goi_gemini(env, prompt, goi_mang_fn=goi_mang_fn, model=model)
        if chu:
            return chu, None
        loi_da_gap.append(f"{model}: {loi}")

    if not loi_da_gap:
        return None, "chua goi duoc AI"
    return None, " | ".join(loi_da_gap)


# ============================================================================
# PHAN HOI DAP (Giai doan 4)
# ============================================================================
# Khac phan viet bao cao o tren: phan nay AI duoc phep XIN GOI CONG CU de lay
# so lieu, thay vi chi doc mot bang co san.
#
# Nguyen tac giong het phan bao cao: CODE tinh, AI chep. Cong cu tra ve so da
# tinh san (chenh lech, phan tram, chi phi moi don, thu hang).


def soan_prompt_hoi_dap(cau_hoi, moc_tg=""):
    """Ghep cau hoi + moc thoi gian thanh cau lenh cho AI.

    KHONG nhan tham so env -> ve cau truc no khong the lam lo token.
    """
    return (
        HUONG_DAN_HOI_DAP
        + "\n--- MỐC THỜI GIAN (do hệ thống cung cấp, không tự suy diễn) ---\n"
        + str(moc_tg or "(không có)")
        + "\n\n--- CÂU HỎI CỦA CHỦ SHOP ---\n"
        + str(cau_hoi or "")
    )


def boc_content(content):
    """Boc mot `content` cua Gemini -> (chu, function_call).

    Uu tien CHU: model co the vua viet chu vua xin goi cong cu; khi do lay chu.
    Khong bao gio nem loi.
    """
    chu = ""
    xin_goi = None
    try:
        for p in (content or {}).get("parts") or []:
            if p.get("text") and str(p["text"]).strip():
                chu += str(p["text"]).strip() + "\n"
            elif p.get("functionCall") and xin_goi is None:
                xin_goi = p["functionCall"]
    except (AttributeError, TypeError):
        pass
    return chu.strip(), xin_goi


def _chon_model_hoi_dap(env):
    """Danh sach model se thu, theo thu tu. Model chinh truoc, du phong sau."""
    env = env or {}
    chinh = str(env.get("GEMINI_MODEL_HOI_DAP", "")).strip() or MODEL_HOI_DAP_MAC_DINH
    du_phong = (str(env.get("GEMINI_MODEL_HOI_DAP_DU_PHONG", "")).strip()
                or MODEL_HOI_DAP_DU_PHONG_MAC_DINH)
    ds = [chinh]
    if du_phong and du_phong != chinh:
        ds.append(du_phong)
    return ds


def goi_gemini_cong_cu(env, noi_dung, khai_bao_cong_cu=None, timeout=None,
                       goi_mang_fn=None):
    """Goi Gemini kem khai bao cong cu. Tra ve (content_cua_model, loi).

    Tra ve NGUYEN `content` (khong phai chuoi chu) vi vong lap cong cu phai gui
    lai nguyen phan do cho luot sau. Trong do co `thoughtSignature` ma Gemini 3.x
    yeu cau giu - da kiem chung ngay 29/09/2026.

    Thu lan luot cac model trong _chon_model_hoi_dap() khi gap loi 503/404/429.
    """
    payload = {"contents": noi_dung,
               "generationConfig": {"maxOutputTokens": TOI_DA_TOKEN_TRA_LOI}}
    if khai_bao_cong_cu:
        payload["tools"] = khai_bao_cong_cu

    loi_da_gap = []
    for model in _chon_model_hoi_dap(env):
        du_lieu, loi = _goi_gemini_than(env, payload, model, timeout or TIMEOUT_HOI_DAP,
                                        goi_mang_fn)
        if loi:
            loi_da_gap.append(f"{model}: {loi}")
            continue
        try:
            ung_vien = du_lieu["candidates"][0]
            # Cau tra loi bi CAT vi het tran token: tra ve LOI chu khong tra ve
            # chuoi cut. Mot cau tra loi cut ("...la 20") con te hon la mot loi
            # ro rang, vi Dai se tuong bot doc sai so.
            if str(ung_vien.get("finishReason", "")).upper() == "MAX_TOKENS":
                loi_da_gap.append(
                    f"{model}: cau tra loi bi cat vi het tran token "
                    f"(maxOutputTokens={TOI_DA_TOKEN_TRA_LOI})")
                continue
            return ung_vien["content"], None
        except (KeyError, IndexError, TypeError):
            loi_da_gap.append(f"{model}: AI tra ve sai cau truc")
            continue

    # Ghi lai loi cua TAT CA cac model da thu, khong chi model cuoi.
    #
    # Da gap that ngay 29/09/2026: model chinh gap HTTP 503 (qua tai) nhung
    # thong bao chi hien loi cua model du phong ('The read operation timed out'),
    # nen Dai doc khong biet la AI dang qua tai ma tuong hong gi do.
    if not loi_da_gap:
        return None, "chua goi duoc AI"
    return None, " | ".join(loi_da_gap)


def tra_loi(cau_hoi, bo_cong_cu, env=None, moc_tg="", goi_mang_fn=None,
            dong_ho_fn=None):
    """Tra loi mot cau hoi cua Dai. Tra ve (chu, loi). KHONG BAO GIO nem loi.

    Vong lap: hoi AI -> AI xin goi cong cu -> CODE chay cong cu -> tra ket qua
    ve -> hoi lai. Toi da TOI_DA_LUOT_CONG_CU luot cong cu, sau do hoi lan cuoi
    KHONG kem cong cu de BUOC AI tra loi bang chu.

    Vi sao phai buoc: da thu that ngay 29/09/2026, AI nhan ket qua roi goi tiep
    cong cu chu khong tu dung. Khong co gioi han cung thi mot cau hoi co the
    ton hang chuc luot goi AI, trong khi tran mien phi chi 20 luot/ngay.

    Ngan sach thoi gian: ca cau hoi chi duoc dung THOI_GIAN_TOI_DA_HOI_DAP giay.
    Het ngan sach thi bo cuoc va bao Dai, de MOC GIO khong bi tre.
    """
    try:
        prompt = soan_prompt_hoi_dap(cau_hoi, moc_tg)
    except Exception as e:
        return None, f"khong soan duoc cau lenh cho AI: {e}"

    khai_bao = None
    if bo_cong_cu is not None:
        try:
            khai_bao = bo_cong_cu.khai_bao()
        except Exception as e:
            return None, f"khong khai bao duoc cong cu: {e}"

    dong_ho = dong_ho_fn or time.monotonic
    bat_dau = dong_ho()

    noi_dung = [{"role": "user", "parts": [{"text": prompt}]}]

    for luot in range(TOI_DA_LUOT_CONG_CU + 1):
        # Con bao nhieu giay trong ngan sach? Het thi bo cuoc.
        da_dung = dong_ho() - bat_dau
        con_lai = THOI_GIAN_TOI_DA_HOI_DAP - da_dung
        if con_lai <= 0:
            return None, (
                f"AI chua tra loi duoc sau {int(da_dung)} giay "
                f"(co the AI dang qua tai)")

        con_cong_cu = khai_bao if luot < TOI_DA_LUOT_CONG_CU else None
        content, loi = goi_gemini_cong_cu(
            env, noi_dung, khai_bao_cong_cu=con_cong_cu,
            timeout=min(TIMEOUT_HOI_DAP, con_lai), goi_mang_fn=goi_mang_fn)
        if loi:
            return None, loi
        if content is None:
            return None, "AI tra ve rong"

        chu, xin_goi = boc_content(content)
        if chu:
            return chu, None
        if not xin_goi:
            return None, "AI tra ve rong, khong co ca cong cu"
        if bo_cong_cu is None:
            return None, "AI xin goi cong cu nhung khong co cong cu nao"

        noi_dung.append(content)
        try:
            kq = bo_cong_cu.thuc_thi(xin_goi.get("name"), xin_goi.get("args") or {})
        except Exception as e:
            kq = {"loi": f"cong cu bi loi: {e}"}
        noi_dung.append({"role": "user", "parts": [{
            "functionResponse": {"name": xin_goi.get("name"), "response": kq}}]})

    return None, "AI xin goi cong cu qua nhieu luot ma chua tra loi"
