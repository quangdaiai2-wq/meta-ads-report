"""
CONG CU TRA LOI CAU HOI
========================
Bon cong cu ma AI duoc phep goi de lay so lieu. CODE chay cong cu, AI chi doc
ket qua tra ve.

Nguyen tac quan trong nhat (bai hoc tu Giai doan 3, lap lai o day):
  PHEP TINH DO CODE LAM. Cong cu tra ve so DA TINH SAN (chenh lech, phan tram,
  chi phi moi don, thu hang). AI khong tu tinh, chi chep lai.

Vi sao tach rieng khoi ai.py: file nay KHONG cham mang, KHONG biet Gemini la gi.
Nho vay kiem thu duoc toan bo ma khong can gia lap mang, va doi nha cung cap AI
sau nay khong phai sua file nay.
"""
from datetime import date, datetime
from pathlib import Path

import lich_su

DUONG_DAN_MAC_DINH = Path(__file__).parent / "logs" / "lich-su.json"

# So camp toi da tra ve trong mot lan xep hang. Nhieu hon thi cau lenh gui cho
# AI dai vo ich, va AI cung khong doc het.
TOI_DA_CAMP = 15

# Cac chi so dung khi so sanh hai ky. Ten viet CO DAU vi day la chu gui cho AI
# doc va AI se chep lai -> phai co dau ngay tu day.
#
# KHAC voi ai.TEN_CHI_SO (viet khong dau): bang do la bang nam trong bao cao
# Telegram, da kiem chung va da chot, khong dung vao.
CHI_SO_SO_SANH = [
    ("spend", "chi tieu", "tien"),
    ("msg", "tin nhan moi", "so"),
    ("contact", "lien he moi", "so"),
    ("order", "don hang", "so"),
    ("purchase", "luot mua", "so"),
    ("payment", "luot thanh toan", "so"),
    ("comment", "binh luan", "so"),
]

# Chi so duoc phep dung khi xep hang chien dich.
CHI_SO_XEP_HANG = ("spend", "purchase", "payment", "msg", "cpr")

THU_TRONG_TUAN = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu",
                  "Thứ Bảy", "Chủ Nhật"]


def _thanh_ngay(s):
    """'2026-09-28' -> date. Sai dinh dang -> None (khong nem loi)."""
    try:
        return datetime.strptime(str(s), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _hien_thi_ngay(s):
    """'2026-09-28' -> '28/09/2026'. Sai dinh dang -> nguyen chuoi cu."""
    d = _thanh_ngay(s)
    return d.strftime("%d/%m/%Y") if d else str(s)


def _lam_tron(v, kieu):
    """Lam tron theo kieu chi so. 'tien' thi ve so nguyen dong."""
    try:
        return int(round(float(v or 0)))
    except (ValueError, TypeError):
        return 0


def _tien(v):
    """20319895 -> '20.319.895'. Kieu Viet Nam (dau cham ngan nghin)."""
    return f"{_lam_tron(v, 'tien'):,}".replace(",", ".")


def _chuoi_so(v):
    """Moi chi so thanh CHUOI da dinh dang san.

    Vi sao tra ve CHUOI chu khong phai so: da thu that ngay 29/09/2026, AI chep
    so tho tu JSON nen viet ra '20319895 dong' - thieu dau phan cach, doc rat
    met (bao cao cua Dai van ghi '20.319.895'). Neu de AI tu them dau phan cach
    thi tuc la de AI SUA SO, dung rai ro da tranh o Giai doan 3.
    Cach dung: CODE dinh dang san, AI chep nguyen chuoi.
    """
    ra = {}
    for khoa, ten, kieu in CHI_SO_SO_SANH:
        ra[ten] = _tien(v.get(khoa, 0)) if kieu == "tien" else str(int(v.get(khoa, 0) or 0))
    return ra


def moc_thoi_gian(duong_dan=None, hom_nay=None):
    """Chu mo ta MOC THOI GIAN, do CODE tinh. Dua vao cau lenh cho AI.

    Ly do phai co: khi thu nghiem ngay 29/09/2026, AI tu hieu "tuan nay" thanh
    28/09 -> 29/09 (hai ngay) va tu chon "tuan truoc" la 21/09 -> 27/09. Ca hai
    deu khong dung y nguoi hoi, va luc do lich su chi co so toi 28/09.

    Pham vi thoi gian la mot PHEP TINH. Phai do code lam.
    """
    duong_dan = Path(duong_dan or DUONG_DAN_MAC_DINH)
    hom_nay = hom_nay or date.today()

    dong = [f"Hôm nay: {hom_nay.strftime('%d/%m/%Y')} "
            f"({THU_TRONG_TUAN[hom_nay.weekday()]})"]

    try:
        data = lich_su.doc(duong_dan)
        ds_ngay = sorted(k for k in data if data[k].get("tong"))
    except Exception:
        ds_ngay = []

    if not ds_ngay:
        dong.append("Lịch sử CHƯA CÓ ngày nào. Không trả lời được câu hỏi "
                    "cần số liệu. Nếu được hỏi, hãy nói thật là chưa có số.")
        return "\n".join(dong)

    dong.append(f"Ngày cuối cùng CÓ số liệu: {_hien_thi_ngay(ds_ngay[-1])}")
    dong.append(f"Số liệu có từ ngày: {_hien_thi_ngay(ds_ngay[0])} "
                f"(tổng cộng {len(ds_ngay)} ngày)")

    bay_ngay = ds_ngay[-7:]
    dong.append(f"7 ngày có số gần nhất: {_hien_thi_ngay(bay_ngay[0])} "
                f"đến {_hien_thi_ngay(bay_ngay[-1])}")

    truoc_do = ds_ngay[-14:-7]
    if truoc_do:
        dong.append(f"7 ngày liền trước đó: {_hien_thi_ngay(truoc_do[0])} "
                    f"đến {_hien_thi_ngay(truoc_do[-1])}")
    else:
        dong.append("7 ngày liền trước đó: CHƯA CÓ số liệu, không so sánh được.")

    dong.append("Khi trả lời, phải nói rõ bạn dùng khoảng ngày nào. "
                "Không tự chọn khoảng khác ngoài các khoảng ở trên.")
    return "\n".join(dong)


class BoCongCu:
    """Bon cong cu AI duoc phep goi. Mot doi tuong song trong MOT cau hoi.

    lay_so_hom_nay_fn(ngay) -> dict stats hoac None.
        None (mac dinh) nghia la KHONG goi Meta. Day la che do an toan, dung
        trong kiem thu va trong truong hop chua cau hinh token.
    """

    def __init__(self, duong_dan=None, lay_so_hom_nay_fn=None, hom_nay=None):
        self.duong_dan = Path(duong_dan or DUONG_DAN_MAC_DINH)
        self.lay_so_hom_nay_fn = lay_so_hom_nay_fn
        self.hom_nay = hom_nay or date.today()
        # Moi cau hoi toi da MOT lan goi Meta: goi Meta mat 15-30 giay, ma AI
        # co the xin goi cong cu nhieu lan lien tiep.
        self.da_goi_meta = False
        self.cache_meta = None

    # ---------- khai bao cho AI ----------

    def khai_bao(self):
        """Danh sach khai bao cong cu, dung lam truong `tools` gui cho Gemini."""
        return [{"functionDeclarations": [
            {
                "name": "lay_mot_ngay",
                "description": ("Lay so lieu tong hop cua MOT ngay. Dung khi cau hoi "
                                "chi ve mot ngay cu the. Neu ngay do chua co trong "
                                "lich su va la hom nay thi he thong tu lay tu Meta."),
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "ngay": {"type": "STRING",
                                 "description": "Ngay can lay, dang YYYY-MM-DD"},
                    },
                    "required": ["ngay"],
                },
            },
            {
                "name": "lay_khoang",
                "description": ("Cong don so lieu trong mot khoang ngay, bao gom ca hai "
                                "dau mut. Dung khi cau hoi noi ve nhieu ngay."),
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "tu": {"type": "STRING", "description": "Tu ngay, YYYY-MM-DD"},
                        "den": {"type": "STRING", "description": "Den ngay, YYYY-MM-DD"},
                    },
                    "required": ["tu", "den"],
                },
            },
            {
                "name": "xep_hang_camp",
                "description": ("Xep hang cac chien dich theo mot chi so trong mot khoang "
                                "ngay. Ket qua da duoc sap san. Chi so hop le: "
                                "spend (chi tieu), purchase (luot mua), payment (luot "
                                "thanh toan), msg (tin nhan moi), cpr (chi phi moi don)."),
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "tu": {"type": "STRING", "description": "Tu ngay, YYYY-MM-DD"},
                        "den": {"type": "STRING", "description": "Den ngay, YYYY-MM-DD"},
                        "sap_theo": {"type": "STRING",
                                     "description": "Chi so de sap xep"},
                        "tang_dan": {"type": "BOOLEAN",
                                     "description": ("true = nho nhat len dau "
                                                     "(muon tim cai te nhat thi dung true)")},
                    },
                    "required": ["tu", "den", "sap_theo"],
                },
            },
            {
                "name": "so_sanh",
                "description": ("So sanh hai khoang ngay voi nhau. He thong da tinh san "
                                "chenh lech va phan tram. Dung khi cau hoi co y so sanh."),
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "ky_nay_tu": {"type": "STRING", "description": "Ky nay, tu ngay"},
                        "ky_nay_den": {"type": "STRING", "description": "Ky nay, den ngay"},
                        "ky_truoc_tu": {"type": "STRING", "description": "Ky truoc, tu ngay"},
                        "ky_truoc_den": {"type": "STRING", "description": "Ky truoc, den ngay"},
                    },
                    "required": ["ky_nay_tu", "ky_nay_den", "ky_truoc_tu", "ky_truoc_den"],
                },
            },
        ]}]

    # ---------- phan phoi ----------

    def thuc_thi(self, ten, args):
        """Chay mot cong cu theo ten. KHONG BAO GIO nem loi ra ngoai.

        Moi loi deu tra ve qua khoa "loi", de AI doc duoc va noi that voi Dai
        thay vi im lang.
        """
        args = args or {}
        try:
            if ten == "lay_mot_ngay":
                return self.lay_mot_ngay(args.get("ngay"))
            if ten == "lay_khoang":
                return self.lay_khoang(args.get("tu"), args.get("den"))
            if ten == "xep_hang_camp":
                return self.xep_hang_camp(
                    args.get("tu"), args.get("den"),
                    args.get("sap_theo"), args.get("tang_dan"))
            if ten == "so_sanh":
                return self.so_sanh(
                    args.get("ky_nay_tu"), args.get("ky_nay_den"),
                    args.get("ky_truoc_tu"), args.get("ky_truoc_den"))
        except Exception as e:
            return {"loi": f"Cong cu '{ten}' bi loi khi chay: {e}"}
        return {"loi": f"Khong co cong cu nao ten '{ten}'. "
                       f"Chi dung: lay_mot_ngay, lay_khoang, xep_hang_camp, so_sanh."}

    # ---------- bon cong cu ----------

    def lay_mot_ngay(self, ngay):
        if _thanh_ngay(ngay) is None:
            return {"loi": f"Ngay '{ngay}' sai dinh dang. Phai la YYYY-MM-DD."}

        ban_ghi = lich_su.lay_mot_ngay(self.duong_dan, ngay)
        if ban_ghi:
            tong = ban_ghi.get("tong") or {}
            return {
                "ngay": str(ngay),
                "nguon": "so da luu trong lich su",
                "moc_gio_bao_cao": ban_ghi.get("moc"),
                "day_du_ca_ngay": bool(ban_ghi.get("day_du")),
                "ghi_chu": ("day_du_ca_ngay = false nghia la so nay moi tich luy "
                            "den mot moc gio trong ngay, chua phai ca ngay."),
                "tong": tong,
                "tong_hien_thi": _chuoi_so(tong),
                "so_camp": ban_ghi.get("so_camp", 0),
            }

        # Chua co trong lich su. Chi goi Meta khi la HOM NAY va duoc phep.
        d = _thanh_ngay(ngay)
        if d == self.hom_nay and self.lay_so_hom_nay_fn is not None:
            stats = self._lay_meta_mot_lan()
            if stats:
                tong = stats.get("totals") or {}
                return {
                    "ngay": str(ngay),
                    "nguon": "vua lay truc tiep tu Meta",
                    "day_du_ca_ngay": False,
                    "ghi_chu": ("So tich luy tu 0h den luc nay, CHUA het ngay. "
                                "Phai noi ro dieu nay khi tra loi."),
                    "tong": tong,
                    "tong_hien_thi": _chuoi_so(tong),
                    "so_camp": stats.get("total_campaigns", 0),
                }

        return {"loi": (f"Lich su chua co so ngay {ngay}. "
                        f"Ngay cuoi cung co so la {self._ngay_cuoi() or 'khong co'}.")}

    def lay_khoang(self, tu, den):
        if _thanh_ngay(tu) is None or _thanh_ngay(den) is None:
            return {"loi": "Ngay phai co dinh dang YYYY-MM-DD."}
        r = lich_su.lay_khoang(self.duong_dan, tu, den)
        if not r.get("so_ngay"):
            return {"loi": (f"Khong co ngay nao co so lieu trong khoang "
                            f"{tu} den {den}. Ngay cuoi cung co so la "
                            f"{self._ngay_cuoi() or 'khong co'}.")}
        return {"tu": str(tu), "den": str(den), "so_ngay": r["so_ngay"],
                "tong": r.get("tong") or {},
                "tong_hien_thi": _chuoi_so(r.get("tong") or {})}

    def xep_hang_camp(self, tu, den, sap_theo="spend", tang_dan=False):
        if _thanh_ngay(tu) is None or _thanh_ngay(den) is None:
            return {"loi": "Ngay phai co dinh dang YYYY-MM-DD."}
        sap_theo = str(sap_theo or "spend").strip().lower()
        if sap_theo not in CHI_SO_XEP_HANG:
            return {"loi": f"Chi so '{sap_theo}' khong hop le. "
                           f"Chi dung: {list(CHI_SO_XEP_HANG)}"}

        gop = self._gop_camp(tu, den)
        if not gop:
            return {"loi": (f"Khong co du lieu chien dich nao trong khoang "
                            f"{tu} den {den}.")}

        ds = list(gop.values())
        if sap_theo == "cpr":
            # Camp CHUA CO don thi cpr la None -> day xuong cuoi cung, KHONG
            # coi la 0. So 0 trong nhu re nhat, da biet la sai.
            co_don = [c for c in ds if c.get("cpr")]
            khong_don = [c for c in ds if not c.get("cpr")]
            co_don.sort(key=lambda c: c["cpr"], reverse=not tang_dan)
            ds = co_don + khong_don
        else:
            ds.sort(key=lambda c: float(c.get(sap_theo, 0) or 0),
                    reverse=not tang_dan)

        return {"tu": str(tu), "den": str(den), "so_camp": len(ds),
                "sap_theo": sap_theo, "tang_dan": bool(tang_dan),
                "danh_sach": ds[:TOI_DA_CAMP]}

    def so_sanh(self, ky_nay_tu, ky_nay_den, ky_truoc_tu, ky_truoc_den):
        for v in (ky_nay_tu, ky_nay_den, ky_truoc_tu, ky_truoc_den):
            if _thanh_ngay(v) is None:
                return {"loi": "Ngay phai co dinh dang YYYY-MM-DD."}

        nay = lich_su.lay_khoang(self.duong_dan, ky_nay_tu, ky_nay_den)
        truoc = lich_su.lay_khoang(self.duong_dan, ky_truoc_tu, ky_truoc_den)
        if not nay.get("so_ngay"):
            return {"loi": (f"Ky nay ({ky_nay_tu} den {ky_nay_den}) khong co so lieu, "
                            f"khong so sanh duoc.")}

        co_ky_truoc = bool(truoc.get("so_ngay"))
        bang = []
        for khoa, ten, kieu in CHI_SO_SO_SANH:
            moi = _lam_tron((nay.get("tong") or {}).get(khoa, 0), kieu)
            moi_chu = _tien(moi) if kieu == "tien" else str(moi)
            if not co_ky_truoc:
                bang.append({"ten": ten, "ky_nay": moi, "ky_truoc": None,
                             "chenh_lech": None, "phan_tram": None,
                             "ky_nay_hien_thi": moi_chu,
                             "ky_truoc_hien_thi": None,
                             "chenh_lech_hien_thi": None})
                continue
            cu = _lam_tron((truoc.get("tong") or {}).get(khoa, 0), kieu)
            chenh = moi - cu
            cu_chu = _tien(cu) if kieu == "tien" else str(cu)
            chenh_chu = ("+" if chenh >= 0 else "-") + (
                _tien(abs(chenh)) if kieu == "tien" else str(abs(chenh)))
            bang.append({
                "ten": ten, "ky_nay": moi, "ky_truoc": cu, "chenh_lech": chenh,
                "phan_tram": (round(chenh / cu * 100) if cu else None),
                "ky_nay_hien_thi": moi_chu, "ky_truoc_hien_thi": cu_chu,
                "chenh_lech_hien_thi": chenh_chu,
            })

        return {
            "ky_nay": f"{ky_nay_tu} den {ky_nay_den}",
            "so_ngay_ky_nay": nay.get("so_ngay", 0),
            "ky_truoc": (f"{ky_truoc_tu} den {ky_truoc_den}" if co_ky_truoc else None),
            "so_ngay_ky_truoc": truoc.get("so_ngay", 0),
            "bang": bang,
            "ghi_chu": ("Cot 'chenh_lech' va 'phan_tram' do he thong tinh san. "
                        "Chep nguyen, khong tu tinh lai. Neu 'ky_truoc' la null thi "
                        "noi ro la khong co so ky truoc, dung so sanh."),
        }

    # ---------- phu tro ----------

    def _gop_camp(self, tu, den):
        """Cong don tung chien dich qua cac ngay trong khoang.

        Khoa la id; id rong thi dung ten. Id khong doi khi camp doi ten.
        """
        data = lich_su.doc(self.duong_dan)
        gop = {}
        for ngay in sorted(data):
            if not (tu <= ngay <= den):
                continue
            for c in (data[ngay].get("camp") or []):
                khoa = str(c.get("id") or "").strip() or str(c.get("name") or "").strip()
                if not khoa:
                    continue
                if khoa not in gop:
                    gop[khoa] = {"id": str(c.get("id") or ""),
                                 "name": c.get("name") or "",
                                 "spend": 0.0, "purchase": 0, "payment": 0, "msg": 0,
                                 "so_ngay_xuat_hien": 0}
                g = gop[khoa]
                g["spend"] += float(c.get("spend", 0) or 0)
                for k in ("purchase", "payment", "msg"):
                    g[k] += int(c.get(k, 0) or 0)
                g["so_ngay_xuat_hien"] += 1
                if not g["name"] and c.get("name"):
                    g["name"] = c["name"]

        for g in gop.values():
            g["spend"] = int(round(g["spend"]))
            g["cpr"] = (int(round(g["spend"] / g["purchase"]))
                        if g["purchase"] > 0 else None)
            # Ten thu hai cho cung mot so, de AI khong phai doan 'cpr' la gi.
            g["chi_phi_moi_don"] = g["cpr"]
            # Cac truong CHUOI da dinh dang san. AI phai chep tu day, khong
            # chep tu truong so tho (xem _chuoi_so de biet ly do).
            g["chi_tieu_hien_thi"] = _tien(g["spend"])
            g["chi_phi_moi_don_hien_thi"] = (
                f"{_tien(g['cpr'])} d" if g["cpr"] else "chua co don")
            g["tin_nhan_moi"] = str(g["msg"])
            g["luot_mua"] = str(g["purchase"])
        return gop

    def _lay_meta_mot_lan(self):
        """Goi Meta lay so hom nay. Toi da MOT lan cho moi cau hoi."""
        if self.da_goi_meta:
            return self.cache_meta
        self.da_goi_meta = True
        try:
            self.cache_meta = self.lay_so_hom_nay_fn(self.hom_nay)
        except Exception:
            self.cache_meta = None
        return self.cache_meta

    def _ngay_cuoi(self):
        try:
            data = lich_su.doc(self.duong_dan)
        except Exception:
            return None
        ds = sorted(k for k in data if data[k].get("tong"))
        return ds[-1] if ds else None
