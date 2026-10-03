"""Doi chieu SO CUA AGENT voi NHAT KY META. CHI DOC — khong ghi gi len Meta.

VI SAO CO CONG CU NAY (Dai chot 03/10/2026):
  Dai KHONG phai chu tai khoan doanh nghiep Meta. Vai tro la EMPLOYEE nen KHONG
  tao duoc System User => khong co "token App". Moi thao tac gui len Meta deu
  mang ten chu token ca nhan ("Nam Duc Pham"), nen nhat ky Meta KHONG phan biet
  duoc NGUOI va MAY. Cau hoi "viec nay ai lam" khong the tra loi chi bang Meta.

  Cong cu nay lam dung viec ma token App le ra lam duoc: DOI CHIEU hai nguon.
    - So cua agent  : logs/nhat-ky-agent.json  (co `nguon_goc`, gio VN +07:00)
    - Nhat ky Meta  : act_.../activities      (event_time UTC, object_id)
  Khong khop => hien ro. Viec chi co o Meta => DAI TU LAM TAY.

CACH KHOP: theo `object_id` va cua so +-2 phut.
  Vi sao +-2 phut: Meta ghi theo giay nhung co do tre, va mot thao tac
  "tat nhom + tat quang cao + doi ten" sinh NHIEU su kien trong vai giay.
  Cua so nay gom dung chung lai, khong gom nham viec khac.

AN TOAN: file nay TUYET DOI khong ghi gi len Meta, khong gui Telegram.
Co kiem thu canh dieu do (kiem tra ma nguon khong chua ham ghi).
"""
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

GIO_VN = timezone(timedelta(hours=7))
GOC = Path(__file__).parent
SO_AGENT = GOC / "logs" / "nhat-ky-agent.json"

# Cua so khop hai nguon (phut).
CUA_SO_KHOP_PHUT = 2

# Loai su kien Meta la THAO TAC TAT/BAT. Meta tra nhieu ten khac nhau.
SU_KIEN_TAT = {"update_adset_run_status", "update_ad_run_status",
               "update_campaign_run_status", "adset_paused", "ad_paused",
               "campaign_paused"}
SU_KIEN_BAT = {"update_adset_run_status", "update_ad_run_status",
               "update_campaign_run_status", "adset_activated", "ad_activated",
               "campaign_activated"}


def _gio(t):
    """Chuan hoa thoi diem ve co mui gio. Doc khong duoc -> None."""
    if isinstance(t, str):
        try:
            t = datetime.fromisoformat(t)
        except ValueError:
            return None
    if not isinstance(t, datetime):
        return None
    if t.tzinfo is None:
        return t.replace(tzinfo=timezone.utc)
    return t


def doc_so_agent(duong_dan=None):
    """Doc so agent. Tra ve list ban ghi dict. Loi -> [] (khong nem)."""
    return doc_so_agent_co_canh_bao(duong_dan)[0]


def doc_so_agent_co_canh_bao(duong_dan=None):
    """Doc so agent, tra ve (danh_sach_ban_ghi, ly_do).

    VI SAO CAN BAN CO CANH BAO (loi that phat hien 03/10/2026):
      Ban cu LOC BO im lang moi phan tu khong phai dict, va tra [] cho moi loi
      (file khong ton tai, JSON hong, so khong phai list). Ba tinh huong RAT KHAC
      nhau do deu cho ra cung ket qua "so rong":
        - so that su chua gi           -> binh thuong
        - tro sai duong dan            -> DAI GO SAI, khong phai he thong hong
        - so bi hong / co phan tu la   -> MAT DU LIEU AM THAM, nguy hiem nhat
      Nhin bang ket qua khong the phan biet, nen Dai de hieu nham la "Meta khong
      ghi nhan" hoac "agent hong". Phai noi RO tung truong hop.

    Tra ve:
      (danh_sach, "")            — doc duoc, khong co gi bat thuong
      (danh_sach, "ly do ...")   — doc duoc NHUNG co phan tu hong bi bo qua,
                                   hoac khong doc duoc file
    """
    p = Path(duong_dan) if duong_dan else SO_AGENT
    if not p.exists():
        return [], f"khong tim thay file so agent: {p}"
    try:
        tho = json.loads(p.read_text(encoding="utf-8"))
    except OSError as e:
        return [], f"khong doc duoc file so agent ({p}): {e}"
    except ValueError as e:
        return [], f"file so agent hong dinh dang JSON ({p}): {e}"
    if not isinstance(tho, list):
        return [], (f"file so agent khong phai danh sach "
                    f"({type(tho).__name__}) — co the bi ghi de sai")
    ra = [r for r in tho if isinstance(r, dict)]
    so_hong = len(tho) - len(ra)
    if so_hong:
        return ra, (f"so agent co {so_hong} phan tu hong da bi bo qua "
                    f"(khong phai ban ghi) — kiem tra lai file")
    return ra, ""


def _la_mo_coi(rec):
    """Ban ghi DA GUI len Meta nhung KHONG co ket qua => moi coi.

    Xem chu thich o `agent_ky_uc.tim_ban_ghi_mo_coi`. Cac ban ghi nay PHAI bi
    bo qua khi doi chieu: neu khong se bao "agent ghi ma Meta khong nhan" SAI.
    """
    return rec.get("da_gui_len_meta") is True and not rec.get("ket_qua")


def _khoa_doi_tuong(rec):
    return str((rec.get("doi_tuong") or {}).get("id") or "")


def _ban_ghi_that(ds):
    """Loc ra cac ban ghi DUNG de doi chieu.

    Loai: ban ghi chi de HOI Dai (chua gui Meta), ban ghi mo coi, va ban ghi
    thieu du lieu (khong co `luc` hoac khong co id doi tuong) — khong the doi
    chieu cai khong xac dinh duoc.
    Manh: chi con ban ghi mang MOT HANH DONG THAT, du du lieu de so.

    🔴 NGOAI LE DANH CHO SO CU (Dai chot 03/10/2026):
    Truoc khi sua loi "ban ghi mo coi", ket qua bi ghi vao BAN GHI 1 (luc HOI Dai,
    `da_gui_len_meta=False`), con BAN GHI 2 (`da_gui=True`) bi bo trong. Do lai
    tren so that: 0 ban ghi nao vua `da_gui=True` vua co `ket_qua`.

    Neu chi nhan `da_gui=True` thi cong cu doi chieu KHONG BAO GIO khop duoc gi
    — vo dung hoan toan. Nen: nhan THEM ban ghi `da_gui=False` NHUNG co `ket_qua`
    thanh cong. Xem chu thich `_la_ban_ghi_cu_bi_lech`.
    """
    ra = []
    for r in ds:
        if _la_mo_coi(r):
            continue
        if _gio(r.get("luc")) is None:
            continue
        if not _khoa_doi_tuong(r):
            continue
        if r.get("da_gui_len_meta") is True:
            ra.append(r)
            continue
        if _la_ban_ghi_cu_bi_lech(r):
            ra.append(r)
    return ra


def _la_ban_ghi_cu_bi_lech(rec):
    """Ban ghi CU bi lech ket qua: `da_gui=False` NHUNG co ket qua thanh cong.

    VI SAO CAN: day chinh la dau vet cua loi "ban ghi mo coi". Truoc 03/10/2026,
    `cap_nhat_phan_hoi` ghi ket qua vao ban ghi luc HOI Dai, nen BAN GHI MANG
    KET QUA lai co `da_gui_len_meta=False`.

    Cach nhan: `da_gui` khong phai True, NHUNG `ket_qua` bat dau bang "thanh cong"
    (hoac "loi"/"chan") — tuc la da co ket qua thuc thi, khong con la de xuat cho.
    De xuat cho chua duoc Dai tra loi thi `ket_qua` la None.
    """
    if rec.get("da_gui_len_meta") is True:
        return False
    kq = rec.get("ket_qua")
    if not isinstance(kq, str) or not kq.strip():
        return False
    return True


def doc_nhat_ky_meta(env=None, so_ngay=7, bay_gio=None):
    """Doc `act_.../activities` cua Meta. CHI DOC.

    Tra ve (danh_sach, ly_do). Loi mang / thieu quyen -> ([], ly_do), KHONG nem.
    """
    if env is None:
        try:
            import report
            env = report.load_env(os.path.join(os.getcwd(), ".env"))
        except Exception as e:                                  # noqa: BLE001
            return [], f"khong doc duoc .env: {e}"

    ma_tk = (env.get("META_AD_ACCOUNT_ID") or "").strip()
    if not ma_tk:
        return [], "thieu META_AD_ACCOUNT_ID trong .env"
    if not ma_tk.startswith("act_"):
        ma_tk = "act_" + ma_tk

    # ⚠️ `report.api_get` KHONG tu gan token — nguoi goi phai truyen
    # `access_token` trong params. Thieu no thi Meta bao
    # "(#200) Provide valid app ID" (da gap that 03/10/2026).
    token = (env.get("META_ADS_ACCESS_TOKEN") or "").strip()
    if not token:
        return [], "thieu META_ADS_ACCESS_TOKEN trong .env"

    goc = bay_gio or datetime.now(GIO_VN)
    # ⚠️ META: `until` la moc LOAI TRU, khong phai bao gom. Da do that 03/10/2026:
    #    since=03/10 & until=03/10  -> 0 su kien
    #    since=03/10 & until=04/10  -> co su kien
    # Thieu buoc +1 ngay thi hom nay LUON rong, va bao cao mai sai.
    tu = (goc - timedelta(days=so_ngay)).strftime("%Y-%m-%d")
    den = (goc + timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        import report
    except Exception as e:                                      # noqa: BLE001
        return [], f"khong nap duoc report.py: {e}"

    ds, ly_do = _doc_meta_phan_trang(report, ma_tk, tu, den, token)
    return ds, ly_do


# Meta chi tra toi da `limit` su kien moi lan. Thieu phan trang thi MAT DU LIEU
# AM THAM — bao cao van ra, nhung thieu su kien, va nhin nhu "Meta khong nhan".
SO_TRANG_TOI_DA = 10


def _doc_meta_phan_trang(report, ma_tk, tu, den, token):
    """Doc het su kien, di qua nhieu trang. Tra ve (danh_sach, ly_do)."""
    ra = []
    duong_dan = f"{ma_tk}/activities"
    tham_so = {
        "fields": "event_time,event_type,object_id,object_name,"
                  "actor_name,actor_id",
        "since": tu, "until": den, "limit": 200, "access_token": token,
    }
    for _ in range(SO_TRANG_TOI_DA):
        try:
            data, err = report.api_get(duong_dan, tham_so)
        except Exception as e:                                  # noqa: BLE001
            if ra:
                return ra, f"doc duoc {len(ra)} su kien roi loi: {e}"
            return [], f"loi goi Meta: {e}"

        if err:
            if ra:
                return ra, f"doc duoc {len(ra)} su kien roi Meta bao loi: {err}"
            if isinstance(err, dict):
                return [], f"Meta bao loi: {err.get('message', err)}"
            return [], f"Meta bao loi: {err}"
        if not isinstance(data, dict):
            if ra:
                return ra, ""
            return [], f"Meta tra ve du lieu la ({type(data).__name__})"

        ds = data.get("data")
        if isinstance(ds, list):
            ra.extend(x for x in ds if isinstance(x, dict))

        # Con trang sau khong? Meta tra `paging.next` la URL day du.
        after = (((data.get("paging") or {}).get("cursors")) or {}).get("after")
        if not after or not data.get("paging", {}).get("next"):
            break
        tham_so = dict(tham_so)
        tham_so["after"] = after
    return ra, ""


def _khop(su_kien, ban_ghi, cua_so_phut=CUA_SO_KHOP_PHUT):
    """Su kien Meta nay co khop ban ghi agent khong? (cung id, trong cua so)."""
    ma_meta = str(su_kien.get("object_id") or "")
    if not ma_meta:
        return None
    for r in ban_ghi:
        if _khoa_doi_tuong(r) != ma_meta:
            continue
        t_meta = _gio(su_kien.get("event_time"))
        t_so = _gio(r.get("luc"))
        if t_meta is None or t_so is None:
            continue
        if abs((t_meta - t_so).total_seconds()) <= cua_so_phut * 60:
            return r
    return None


def doi_chieu(ds_agent, ds_meta, cua_so_phut=CUA_SO_KHOP_PHUT):
    """Doi chieu hai nguon. Tra ve dict 4 phan. KHONG nem loi.

    Tra ve:
      khop        : [(ban_ghi_agent, su_kien_meta)]  — ca hai nguon deu co
      chi_meta    : [su_kien_meta]                   — DAI TU LAM TAY
      chi_agent   : [ban_ghi_agent]                  — nghi van
      mo_coi      : [ban_ghi_agent]                  — loi ghi so
      trung_so    : [(ma, so_lan)]                   — canh bao so co ban ghi trung
    """
    ds_agent = ds_agent if isinstance(ds_agent, list) else []
    ds_meta = ds_meta if isinstance(ds_meta, list) else []

    that = _ban_ghi_that(ds_agent)
    mo_coi = [r for r in ds_agent if _la_mo_coi(r)]

    # Canh bao trung: cung id, cung phut, cung hanh dong.
    dem = {}
    for r in that:
        t = _gio(r.get("luc"))
        if t is None:
            continue
        k = (_khoa_doi_tuong(r), t.strftime("%Y-%m-%d %H:%M"), r.get("hanh_dong"))
        dem[k] = dem.get(k, 0) + 1
    trung_so = [(f"{k[0]} luc {k[1]} ({k[2]})", v) for k, v in dem.items() if v > 1]

    da_khop = set()
    khop = []
    for sk in ds_meta:
        if not isinstance(sk, dict):
            continue
        r = _khop(sk, that, cua_so_phut)
        if r is not None:
            khop.append((r, sk))
            da_khop.add(id(r))

    chi_meta = [sk for sk in ds_meta if isinstance(sk, dict)
                and _khop(sk, that, cua_so_phut) is None]
    chi_agent = [r for r in that if id(r) not in da_khop]

    return {
        "khop": khop,
        "chi_meta": chi_meta,
        "chi_agent": chi_agent,
        "mo_coi": mo_coi,
        "trung_so": trung_so,
    }


def _gio_hien(t, mui_gio=GIO_VN):
    """Hien thi thoi diem theo gio VN."""
    g = _gio(t)
    if g is None:
        return "?"
    return g.astimezone(mui_gio).strftime("%d/%m %H:%M:%S")


def _nguon_goc(rec):
    """Suy nguon goc. Dung lai logic cua agent_ky_uc de khong lech."""
    try:
        import agent_ky_uc
        return agent_ky_uc.nguon_goc_cua(rec) or "(khong ro)"
    except Exception:                                           # noqa: BLE001
        return rec.get("nguon_goc") or "(khong ro)"


NHAN_NGUON = {
    "agent_tu_hanh": "MAY TU LAM",
    "dai_bam_nut": "Đại bấm nút",
    "dai_go_tay": "Đại gõ tay",
    "cho_duyet": "(chờ duyệt)",
}


def in_bang(kq, ds_meta, ly_do="", ly_do_so=""):
    """In bang doi chieu ra man hinh. Tra ve chuoi de kiem thu doc lai.

    `ly_do_so`: ly do khong doc duoc SO AGENT. Dung de phan biet ro ba tinh huong
    rat khac nhau nhung truoc day deu hien giong nhau (xem `doc_so_agent_co_canh_bao`):
      - so that su chua gi
      - tro sai duong dan (Dai go sai)
      - so bi hong / co phan tu hong (MAT DU LIEU AM THAM)
    """
    ds_meta = ds_meta if isinstance(ds_meta, list) else []
    dong = []
    them = dong.append

    them("=" * 78)
    them("ĐỐI CHIẾU SỔ AGENT VỚI NHẬT KÝ META")
    them("=" * 78)
    if ly_do_so:
        them(f"🔴 KHÔNG ĐỌC ĐƯỢC SỔ AGENT: {ly_do_so}")
        them("    → Mọi con số dưới đây là VÔ NGHĨA. Sửa đường dẫn file sổ rồi chạy lại.")
        them("")
    if ly_do:
        them(f"⚠️  Không đọc được nhật ký Meta: {ly_do}")
        them("    (Phần đối chiếu chỉ còn một nguồn — xem mục 'chỉ có trong sổ'.)")
        them("")

    them(f"Số sự kiện Meta đọc được : {len(ds_meta)}")
    them(f"Khớp hai nguồn            : {len(kq['khop'])}")
    them(f"Chỉ có trên Meta          : {len(kq['chi_meta'])}")
    them(f"Chỉ có trong sổ agent     : {len(kq['chi_agent'])}")
    them(f"Bản ghi mồ côi (lỗi sổ)   : {len(kq['mo_coi'])}")
    them("")

    if kq["khop"]:
        them("── KHỚP (cả sổ và Meta đều có) " + "─" * 44)
        # Gop lai theo (ban ghi agent): mot thao tac "tat nhom + tat quang cao +
        # doi ten" sinh NHIEU su kien Meta trong vai giay. In tung su kien thi
        # mot viec hien 5-6 dong, nhin khong biet bao nhieu viec.
        dem = {}
        for r, _sk_ in kq["khop"]:
            k = id(r)
            dem.setdefault(k, [r, 0])
            dem[k][1] += 1
        for r, n in sorted(dem.values(),
                           key=lambda x: str(x[0].get("luc") or ""), reverse=True):
            them(f"  {_gio_hien(r.get('luc'))}  {(r.get('doi_tuong') or {}).get('id')}"
                 f"  [{NHAN_NGUON.get(_nguon_goc(r), _nguon_goc(r))}]"
                 + (f"  ({n} sự kiện Meta)" if n > 1 else ""))
        them("")

    if kq["chi_meta"]:
        them("── CHỈ CÓ TRÊN META (ĐẠI TỰ LÀM TAY, không qua agent) " + "─" * 24)
        for sk in kq["chi_meta"]:
            ten_nguoi = sk.get("actor_name") or "?"
            them(f"  {_gio_hien(sk.get('event_time'))}  {sk.get('object_id')}"
                 f"  {sk.get('event_type')}  (Meta ghi tên: {ten_nguoi})")
        them("")

    if kq["chi_agent"]:
        them("── CHỈ CÓ TRONG SỔ AGENT (nghi vấn — Meta không nhận) " + "─" * 25)
        for r in kq["chi_agent"]:
            them(f"  {_gio_hien(r.get('luc'))}  {(r.get('doi_tuong') or {}).get('id')}"
                 f"  [{NHAN_NGUON.get(_nguon_goc(r), _nguon_goc(r))}]")
        them("")

    if kq["mo_coi"]:
        them("── BẢN GHI MỒ CÔI (đã gửi Meta nhưng thiếu kết quả — LỖI SỔ) " + "─" * 18)
        them("   (Đây là dấu vết còn lại trước khi sửa lỗi 03/10/2026.)")
        for r in kq["mo_coi"]:
            them(f"  {_gio_hien(r.get('luc'))}  {(r.get('doi_tuong') or {}).get('id')}")
        them("")

    if kq["trung_so"]:
        them("── CẢNH BÁO: SỔ CÓ BẢN GHI TRÙNG " + "─" * 43)
        for nhan, n in kq["trung_so"]:
            them(f"  {nhan} — xuất hiện {n} lần")
        them("")

    if not any(kq[k] for k in ("khop", "chi_meta", "chi_agent", "mo_coi")):
        them("Không có gì để đối chiếu (một hoặc cả hai nguồn rỗng).")
    return "\n".join(dong)


def chay(duong_dan_so=None, env=None, so_ngay=7, bay_gio=None):
    """Chay tron ven: doc -> doi chieu -> in. Tra ve chuoi ket qua."""
    ds_agent, ly_do_so = doc_so_agent_co_canh_bao(duong_dan_so)
    ds_meta, ly_do = doc_nhat_ky_meta(env, so_ngay, bay_gio)
    kq = doi_chieu(ds_agent, ds_meta)
    return in_bang(kq, ds_meta, ly_do, ly_do_so)


def main():
    import argparse
    p = argparse.ArgumentParser(
        description="Đối chiếu sổ agent với nhật ký Meta (CHỈ ĐỌC).")
    p.add_argument("--so", default=None, metavar="DUONG_DAN",
                   help="Đường dẫn FILE SỔ agent (mặc định logs/nhat-ky-agent.json). "
                        "⚠️ Đây là ĐƯỜNG DẪN, không phải số. Muốn đổi số ngày thì "
                        "dùng --ngay.")
    p.add_argument("--ngay", type=int, default=7,
                   help="Số ngày gần đây đọc từ Meta (mặc định 7)")
    p.add_argument("--khong-goi-meta", action="store_true",
                   help="Chỉ đọc sổ agent, không gọi Meta (chạy thử offline)")
    a = p.parse_args()

    if a.khong_goi_meta:
        ds_agent, ly_do_so = doc_so_agent_co_canh_bao(a.so)
        kq = doi_chieu(ds_agent, [])
        print(in_bang(kq, [], "đã tắt gọi Meta theo yêu cầu (--khong-goi-meta)",
                      ly_do_so))
        return 0

    print(chay(a.so, None, a.ngay))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
