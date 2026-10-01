"""NAC 2 — AGENT XIN PHEP DAI QUA TELEGRAM ROI MOI TAT NHOM.

Tien trinh RIENG, model RIENG, tran RIENG. Khong dung chung voi bao cao.
Khong sua report.py / ai.py / dashboard.py.

Cach chay:
    python agent.py --mot-lan        # chay dung mot vong roi thoat
    python agent.py --thu            # chay thu: khong gui Telegram, khong ghi Meta
    python agent.py                  # chay lien tuc theo nhip AGENT_NHIP_PHUT

Mac dinh la CHE DO TAP SU (AGENT_TAP_SU=true): agent CHI NOI, khong gui lenh
nao len Meta. Dai doc vai ngay, doi chieu, roi moi tat tap su.
"""
import argparse
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import report
import lenh_telegram
import nguoi_truc
import agent_ky_uc
import agent_lich_su
import agent_muc_tieu
import agent_rao
import agent_xin_phep

GIO_VN = timezone(timedelta(hours=7))
GOC = Path(__file__).parent
ENV_PATH = GOC / ".env"

MAC_DINH = {
    "AGENT_MUC": 2,
    "AGENT_TAP_SU": True,
    "AGENT_NHIP_PHUT": 30,
    "AGENT_TOI_DA_NGAY": 3,
    "AGENT_TOI_DA_DE_XUAT_MOI_VONG": 1,
    "AGENT_TOI_DA_CHO": 3,
}


def doc_cau_hinh(env):
    """Doc cau hinh tu .env. Thieu khoa nao thi dung mac dinh trong code."""
    ra = dict(MAC_DINH)
    for k, mac_dinh in MAC_DINH.items():
        v = (env or {}).get(k, "").strip()
        if not v:
            continue
        if isinstance(mac_dinh, bool):
            ra[k] = v.lower() in ("1", "true", "yes", "co", "có")
        else:
            try:
                ra[k] = int(float(v))
            except ValueError:
                pass
    return ra


def _thoi_diem():
    return datetime.now(GIO_VN)


def _soan_ban_ghi(de_xuat, che_do, rao_an_toan, da_gui=False, tin_nhan_id=None):
    """Ban ghi so theo dung dinh dang hai ban ghi cu (30/09/2026).

    `tin_nhan_id`: ma tin nhan Telegram chua 2 nut bam — de sau khi Dai bam
    thi SUA chinh tin do thanh ket qua.
    """
    dt = de_xuat.get("doi_tuong") or {}
    return {
        "luc": _thoi_diem().isoformat(timespec="seconds"),
        "che_do": che_do,
        "ai_lam": "agent nac 2",
        "hanh_dong": de_xuat.get("hanh_dong"),
        "doi_tuong": {
            "cap": dt.get("cap", "ad_set"),
            "id": dt.get("id"),
            "ten": dt.get("ten"),
            "ngan_sach_ngay_vnd": dt.get("ngan_sach_ngay_vnd"),
        },
        "ly_do": de_xuat.get("ly_do"),
        "rao_an_toan": rao_an_toan,
        "da_gui_len_meta": bool(da_gui),
        "tin_nhan_id": tin_nhan_id,
        "dai_phan_hoi": None,
        "ket_qua": None,
        "ket_qua_sau_24h": None,
    }


def _bao_ket_qua(env, ban_ghi, thong_bao, text, nut=None):
    """Dai BAM NUT thi sua tin cu thanh ket qua; GO TAY thi gui tin moi.

    Dai chon cach nay ngay 30/09/2026: nhin vao tin nhan la biet da xu ly,
    va nut bam bi xoa nen khong bam lai duoc.
    `nut`: ban phim moi de gan vao tin (vd nut HOAN TAC sau khi da tat nhom).
    """
    ma_tin = (ban_ghi or {}).get("tin_nhan_id")
    if ma_tin is not None and agent_xin_phep.sua_ket_qua(env, ma_tin, text, nut):
        return
    thong_bao(text)


def _xet_de_xuat(nhom, hom_nay, thang, loai_ten, cau_hinh, bay_gio):
    """Tra ve danh sach de xuat QUA DUOC rao an toan."""
    duyet = []
    lich_su = agent_ky_uc.dem_hanh_dong(bay_gio)
    lich_su["nhom_da_tra_loi"] = agent_ky_uc.nhom_da_tra_loi(bay_gio)
    da_cho = set(agent_ky_uc.ma_dang_cho(bay_gio))
    dem_de_xuat_hom_nay = sum(
        1 for r in agent_ky_uc.doc()
        if isinstance(r, dict) and r.get("che_do") == "xin_phep"
        and (agent_ky_uc._gio(r.get("luc")) or datetime.min.replace(tzinfo=GIO_VN)).date()
        == bay_gio.date())
    con_lai = cau_hinh["AGENT_TOI_DA_DE_XUAT_MOI_VONG"]

    for d in agent_muc_tieu.xet(nhom, hom_nay, thang, loai_ten):
        if con_lai <= 0:
            break
        if str(d["doi_tuong"]["id"]) in da_cho:
            continue
        if len(da_cho) >= cau_hinh["AGENT_TOI_DA_CHO"]:
            break
        if dem_de_xuat_hom_nay >= cau_hinh["AGENT_TOI_DA_NGAY"]:
            break
        ok, ly = agent_rao.kiem(d, lich_su, bay_gio)
        if not ok:
            report.log(f"AGENT: chan de xuat {d['doi_tuong']['ten'][:40]!r}: {ly}")
            continue
        duyet.append(d)
        da_cho.add(str(d["doi_tuong"]["id"]))
        dem_de_xuat_hom_nay += 1
        con_lai -= 1
    return duyet


def _lam_hoan_tac(env, cau_hinh, ma, noi_dung, tin_nhan_id, bay_gio, thong_bao):
    """Dai bam nut HOAN TAC: BAT LAI nhom + dat ngan sach ve muc cu.

    Vi sao can: tat nham thi cai mat khong phai tien, ma la GIAI DOAN HOC cua
    Meta — nhom bi tat roi bat lai se hoc lai tu dau, mat vai ngay hieu suat.
    Nen hoan tac phai la MOT LAN BAM, khong phai mo Trinh quan ly quang cao.
    """
    ban_ghi_cu = agent_ky_uc.lan_tat_gan_nhat(ma, bay_gio)
    if not ban_ghi_cu:
        _bao_ket_qua(env, {"tin_nhan_id": tin_nhan_id}, thong_bao, "\n".join([
            f"⚠️ Không hoàn tác được nhóm {ma}",
            "",
            "Không tìm thấy lần tắt nào trong 24 giờ qua.",
        ]))
        report.log(f"AGENT: khong tim thay lan tat nao cua nhom {ma} de hoan tac")
        return 0

    dt = ban_ghi_cu.get("doi_tuong") or {}
    ngan_sach = agent_rao._so(dt.get("ngan_sach_ngay_vnd")) or 400000
    de_xuat = {
        "hanh_dong": "bat_lai",
        "doi_tuong": {"cap": "ad_set", "id": ma, "ten": dt.get("ten")},
        "ngan_sach_khoi_phuc": ngan_sach,
        "tao_luc": ban_ghi_cu.get("luc"),
    }
    ok, ly = agent_rao.kiem(de_xuat, agent_ky_uc.dem_hanh_dong(bay_gio), bay_gio)

    ban_ghi_moi = {
        "luc": _thoi_diem().isoformat(timespec="seconds"),
        "che_do": "hoan_tac",
        "ai_lam": "agent nac 2",
        "hanh_dong": "bat_lai",
        "doi_tuong": {"cap": "ad_set", "id": ma, "ten": dt.get("ten"),
                      "ngan_sach_ngay_vnd": int(ngan_sach)},
        "ly_do": f"Đại bấm HOÀN TÁC nhóm {ma}",
        "rao_an_toan": ly,
        "da_gui_len_meta": False,
        "tin_nhan_id": tin_nhan_id,
        "dai_phan_hoi": None,
        "ket_qua": None,
        "ket_qua_sau_24h": None,
    }

    if not ok:
        agent_ky_uc.ghi(ban_ghi_moi)
        agent_ky_uc.cap_nhat_phan_hoi(ma, noi_dung, f"chan khi hoan tac: {ly}")
        _bao_ket_qua(env, ban_ghi_moi, thong_bao,
                     f"⚠️ Không bật lại được nhóm {ma}\nLý do: {ly}")
        report.log(f"AGENT: chan hoan tac nhom {ma}: {ly}")
        return 0

    if cau_hinh["AGENT_TAP_SU"]:
        agent_ky_uc.ghi(ban_ghi_moi)
        agent_ky_uc.cap_nhat_phan_hoi(
            ma, noi_dung, "CHE DO TAP SU — da ghi so, CHUA gui len Meta")
        _bao_ket_qua(env, ban_ghi_moi, thong_bao, "\n".join([
            "\U0001f9ea CHẾ ĐỘ TẬP SỰ — ĐÃ GHI NHẬN",
            "",
            f"Đại muốn bật lại nhóm {ma}.",
            "Nhưng agent đang ở chế độ tập sự nên CHƯA gửi lệnh lên Meta.",
        ]))
        return 0

    # Ghi so TRUOC khi gui len Meta — bat buoc, khong tat duoc.
    agent_ky_uc.ghi(ban_ghi_moi)
    import agent_cong_cu_ghi
    thanh_cong, ket_qua, _ = agent_cong_cu_ghi.bat_lai_va_dat_ngan_sach(
        env, ma, int(ngan_sach))
    agent_ky_uc.cap_nhat_phan_hoi(ma, noi_dung, ket_qua)

    dau = "✅" if thanh_cong else "❌"
    _bao_ket_qua(env, ban_ghi_moi, thong_bao, "\n".join([
        f"{dau} ĐÃ BẬT LẠI NHÓM {ma}",
        "",
        f"Nhóm: {dt.get('ten')}",
        f"Ngân sách đặt lại: {agent_rao.tien(ngan_sach)}",
        f"Kết quả: {ket_qua}",
    ]))
    report.log(f"AGENT: bat lai nhom {ma} — {ket_qua}")
    return 1


def _xu_ly_tra_loi(env, cau_hinh, bay_gio, thong_bao):
    """Doc lenh Dai da gui (tien trinh bao cao chuyen tiep) va lam theo.

    KHONG tu goi getUpdates. Ly do: tien trinh bao cao (`nguoi_truc.py`) va
    agent dung CHUNG mot bot Telegram, ma `getUpdates` chi giao moi tin cho MOT
    nguoi goi — ai xac nhan truoc thi nguoi kia khong bao gio thay tin do nua.
    Nen `nguoi_truc.py` nhan tin cua Dai, thay lenh "tat <ma>" thi ghi vao
    `logs/agent-lenh.json`; agent doc file do o vong chay ke tiep.
    """
    ds_lenh = agent_ky_uc.doc_lenh()
    if not ds_lenh:
        return 0
    dang_cho = {str((r.get("doi_tuong") or {}).get("id") or ""): r
                for r in agent_ky_uc.hang_cho(bay_gio)}
    da_lam = 0
    for lenh in ds_lenh:
        noi_dung = lenh.get("noi_dung") if isinstance(lenh, dict) else None
        ma_tin = lenh.get("tin_nhan_id") if isinstance(lenh, dict) else None

        # HOAN TAC phai kiem TRUOC: nhom duoc hoan tac KHONG con nam trong danh
        # sach "dang cho", nen neu dua vao doc_tra_loi(dang_cho) se bao khong khop.
        if lenh_telegram.la_hoan_tac(noi_dung):
            ma_hoan = lenh_telegram.ma_trong_lenh(noi_dung)
            if ma_hoan:
                da_lam += _lam_hoan_tac(env, cau_hinh, ma_hoan, noi_dung, ma_tin,
                                        bay_gio, thong_bao)
            continue

        ket_qua, ma = agent_xin_phep.doc_tra_loi(noi_dung, set(dang_cho))
        if ket_qua not in ("dong_y", "tu_choi") or ma not in dang_cho:
            continue
        ban_ghi = dang_cho[ma]
        if ket_qua == "tu_choi":
            agent_ky_uc.cap_nhat_phan_hoi(ma, noi_dung, "Đại nói bỏ qua")
            _bao_ket_qua(env, ban_ghi, thong_bao, "\n".join([
                "\u23ed ĐÃ BỎ QUA — không làm gì",
                "",
                f"Nhóm: {(ban_ghi.get('doi_tuong') or {}).get('ten')}",
                "",
                "Agent sẽ không đề xuất lại nhóm này trong 24 giờ.",
            ]))
            report.log(f"AGENT: Dai bo qua nhom {ma}")
            continue
        da_lam += _lam_theo_dong_y(env, cau_hinh, ban_ghi, {"noi_dung": noi_dung},
                                   bay_gio, thong_bao)
    agent_ky_uc.xoa_lenh()
    return da_lam


def _lam_theo_dong_y(env, cau_hinh, ban_ghi, kq, bay_gio, thong_bao):
    """Dai da dong y. Kiem lai rao, ghi so TRUOC, roi moi gui len Meta."""
    de_xuat = {
        "hanh_dong": ban_ghi.get("hanh_dong"),
        "doi_tuong": ban_ghi.get("doi_tuong") or {},
        "ngan_sach_ha": agent_rao.NGAN_SACH_HA,
        "luot_mua": ban_ghi.get("luot_mua"),
        "chi_phi_moi_luot": ban_ghi.get("chi_phi_moi_luot"),
        "tao_luc": ban_ghi.get("luc"),
    }
    lich_su = agent_ky_uc.dem_hanh_dong(bay_gio)
    ok, ly = agent_rao.kiem(de_xuat, lich_su, bay_gio)
    ma = str((ban_ghi.get("doi_tuong") or {}).get("id"))

    if not ok:
        agent_ky_uc.cap_nhat_phan_hoi(ma, kq["noi_dung"], f"chan khi lam lai: {ly}")
        _bao_ket_qua(env, ban_ghi, thong_bao,
                     f"⚠️ Không tắt được nhóm {ma}\nLý do: {ly}")
        report.log(f"AGENT: chan khi lam lai nhom {ma}: {ly}")
        return 0

    if cau_hinh["AGENT_TAP_SU"]:
        agent_ky_uc.cap_nhat_phan_hoi(
            ma, kq["noi_dung"], "CHE DO TAP SU — da ghi so, CHUA gui len Meta")
        _bao_ket_qua(env, ban_ghi, thong_bao, "\n".join([
            "\U0001f9ea CHẾ ĐỘ TẬP SỰ — ĐÃ GHI NHẬN",
            "",
            f"Đại đã đồng ý tắt nhóm {ma}.",
            "Nhưng agent đang ở chế độ tập sự nên CHƯA gửi lệnh lên Meta.",
            "Muốn agent làm thật: đổi AGENT_TAP_SU=false trong .env.",
        ]))
        report.log(f"AGENT: tap su, khong gui lenh cho nhom {ma}")
        return 0

    # GHI SO TRUOC khi gui len Meta — bat buoc, khong tat duoc.
    ban_ghi_moi = dict(ban_ghi)
    ban_ghi_moi.update({
        "luc": _thoi_diem().isoformat(timespec="seconds"),
        "dai_phan_hoi": kq["noi_dung"],
        "da_gui_len_meta": True,
    })
    agent_ky_uc.ghi(ban_ghi_moi)

    import agent_cong_cu_ghi
    thanh_cong, ket_qua, chi_tiet = agent_cong_cu_ghi.tam_dung_va_ha_ngan_sach(
        env, ma, agent_rao.NGAN_SACH_HA)
    agent_ky_uc.cap_nhat_phan_hoi(ma, kq["noi_dung"], ket_qua)

    dau = "✅" if thanh_cong else "❌"
    _bao_ket_qua(env, ban_ghi, thong_bao, "\n".join([
        f"{dau} ĐÃ TẮT NHÓM {ma}",
        "",
        f"Nhóm: {(ban_ghi.get('doi_tuong') or {}).get('ten')}",
        f"Kết quả: {ket_qua}",
        "",
        "Bấm nút bên dưới nếu muốn BẬT LẠI (chỉ trong 24 giờ).",
    ]), nut=agent_xin_phep.nut_hoan_tac(ma) if thanh_cong else None)
    report.log(f"AGENT: tat nhom {ma} — {ket_qua}")
    return 1


def _tao_thong_bao(env, che_do_thu):
    """Ham gui tin cho Dai. Che do thu thi chi in ra man hinh."""
    def thong_bao(text):
        if che_do_thu:
            print("[THU] se gui Telegram:\n" + text + "\n")
            return
        nguoi_truc.gui_tin_nhan(env, text)
    return thong_bao


def _quet_va_de_xuat(env, cau_hinh, bay_gio, thong_bao, che_do_thu=False):
    """Phan CHAM: doc so tu Meta roi de xuat. Chay moi AGENT_NHIP_PHUT phut."""
    import agent_doc_meta
    nhom, hom_nay, thang = agent_doc_meta.doc_so(env)
    report.log(f"AGENT: {len(nhom)} nhom, {len(hom_nay)} co chi tieu hom nay, "
               f"{len(thang)} co chi tieu thang")

    loai_ten = [x.strip() for x in (env.get("FILTER_EXCLUDE") or "").split(",") if x.strip()]
    duyet = _xet_de_xuat(nhom, hom_nay, thang, loai_ten, cau_hinh, bay_gio)
    ghi_chu = ("(Đang ở CHẾ ĐỘ TẬP SỰ — agent chỉ nói, chưa gửi lệnh nào lên Meta. "
               "Muốn agent làm thật: đổi AGENT_TAP_SU=false trong .env.)"
               if cau_hinh["AGENT_TAP_SU"] else None)
    for d in duyet:
        if che_do_thu:
            print("[THU] se ghi so va gui:\n"
                  + agent_xin_phep.soan_tin(d, ghi_chu) + "\n")
            continue
        # Gui tin co 2 NUT BAM truoc, lay message_id, roi moi ghi so.
        # Ghi so sau khi gui (khong phai truoc): can message_id de sau nay sua
        # chinh tin do. Con luat "ghi so TRUOC khi gui len Meta" van giu nguyen —
        # no ap cho buoc GUI LENH LEN META, khong phai buoc hoi Dai.
        ma_tin = agent_xin_phep.gui_xin_phep(env, d, ghi_chu)
        if ma_tin is None:
            report.log(f"AGENT: KHONG gui duoc tin xin phep cho "
                       f"{d['doi_tuong']['ten'][:40]!r} — khong ghi so")
            continue
        agent_ky_uc.ghi(_soan_ban_ghi(d, "xin_phep", "cho phep", da_gui=False,
                                      tin_nhan_id=ma_tin))
        report.log(f"AGENT: xin phep tat {d['doi_tuong']['ten'][:40]!r} "
                   f"(tin nhan {ma_tin})")
    return len(duyet)


def chay_mot_vong(env, cau_hinh, che_do_thu=False):
    """Mot vong DAY DU: doc tra loi -> quet -> de xuat. Dung cho --mot-lan."""
    bay_gio = _thoi_diem()
    if cau_hinh["AGENT_MUC"] != 2:
        report.log(f"AGENT: AGENT_MUC={cau_hinh['AGENT_MUC']} — nac 3 chua mo, dung o nac 2")
    thong_bao = _tao_thong_bao(env, che_do_thu)
    if not che_do_thu:
        _xu_ly_tra_loi(env, cau_hinh, bay_gio, thong_bao)
    return _quet_va_de_xuat(env, cau_hinh, bay_gio, thong_bao, che_do_thu)


NHIP_NHANH_GIAY = 15

# Ghi lich su: thu moi 1 gio mot lan. Viec nhe (chi doc file), va CHI goi Meta
# khi ngay do THIEU ban ghi tron ngay — nen khong ton gi va khong giẫm chan
# bao cao theo khung gio (bao cao ghi truoc thi agent thoi).
KHOANG_THU_LICH_SU = 60 * 60


def _an_toan_stdout():
    """Chay NEN (pythonw) thi khong co console => sys.stdout / sys.stderr la None.

    Khi do MOI lenh print se nem loi, va tien trinh chet ngay. Doi chieu vao
    file logs/console.log de khong bao gio vo, va van con dau vet de doc khi can.
    """
    for ten in ("stdout", "stderr"):
        if getattr(sys, ten, None) is not None:
            continue
        try:
            (GOC / "logs").mkdir(exist_ok=True)
            setattr(sys, ten, open(GOC / "logs" / "console.log", "a",
                                   encoding="utf-8", buffering=1))
        except OSError:
            pass


def main():
    _an_toan_stdout()
    parser = argparse.ArgumentParser(description="Agent nac 2 — xin phep roi moi tat")
    parser.add_argument("--mot-lan", action="store_true", help="chay mot vong roi thoat")
    parser.add_argument("--thu", action="store_true", help="chay thu, khong gui gi")
    args = parser.parse_args()

    env = report.load_env(ENV_PATH)
    cau_hinh = doc_cau_hinh(env)
    nhip = max(1, cau_hinh["AGENT_NHIP_PHUT"])
    che_do = "TAP SU (chi noi)" if cau_hinh["AGENT_TAP_SU"] else "LAM THAT"

    # --- Chay thu: khong gui gi, khong giu khoa ---
    if args.thu:
        print(f"Agent nac 2 — muc {cau_hinh['AGENT_MUC']} — {che_do} — CHAY THU")
        chay_mot_vong(env, cau_hinh, che_do_thu=True)
        return 0

    # --- Mot vong: khong giu khoa, nhung TU CHOI neu co agent khac dang chay ---
    if args.mot_lan:
        co, ly = agent_ky_uc.co_agent_khac_dang_chay(nhip)
        if co:
            print(f"KHONG CHAY: {ly}.")
            print("Tat agent kia truoc, hoac dung --thu neu chi muon xem thu.")
            report.log(f"AGENT: tu choi --mot-lan vi {ly}")
            return 2
        print(f"Agent nac 2 — muc {cau_hinh['AGENT_MUC']} — {che_do} — mot vong")
        chay_mot_vong(env, cau_hinh)
        return 0

    # --- Chay lien tuc: GIU KHOA de khong the co hai agent cung chay ---
    # Ngay 30/09/2026 nhat ky ghi agent khoi dong HAI LAN cach nhau 15 giay.
    # Hai agent cung chay thi de xuat trung, xu ly trung, so loan.
    giu, ly = agent_ky_uc.giu_khoa(nhip)
    if not giu:
        print(f"KHONG KHOI DONG: {ly}.")
        print("Cua so kia dang chay agent roi — chi mo MOT cua so thoi.")
        report.log(f"AGENT: tu choi khoi dong vi {ly}")
        return 2

    print(f"Agent nac 2 — muc {cau_hinh['AGENT_MUC']} — {che_do}")
    print(f"Quet Meta moi {nhip} phut · nghe nut bam moi {NHIP_NHANH_GIAY} giay")
    print("De cua so nay MO. Tat bang Ctrl + C.")
    report.log(f"AGENT: khoi dong — muc {cau_hinh['AGENT_MUC']} — {che_do} — {ly}")

    lan_quet_ke = 0.0
    lan_thu_lich_su_ke = 0.0
    che_do_cu = che_do
    try:
        while True:
            try:
                # DOC LAI .env MOI VONG.
                # Truoc day chi doc MOT LAN luc khoi dong, nen Dai doi
                # AGENT_TAP_SU xong agent van chay theo gia tri cu — dung kieu
                # "da doi ma khong thay gi khac", rat de tuong la hong.
                # File .env nho, doc lai moi 15 giay khong dang ke.
                cau_hinh = doc_cau_hinh(report.load_env(ENV_PATH))
                nhip = max(1, cau_hinh["AGENT_NHIP_PHUT"])
                che_do_moi = ("TAP SU (chi noi)" if cau_hinh["AGENT_TAP_SU"]
                              else "LAM THAT")
                if che_do_moi != che_do_cu:
                    report.log(f"AGENT: DOI CHE DO -> {che_do_moi}")
                    print(f"Che do da doi -> {che_do_moi}")
                    che_do_cu = che_do_moi

                bay_gio = _thoi_diem()
                thong_bao = _tao_thong_bao(env, False)
                # 1. NGHE TRUOC, vong ngan — bam nut la xu ly gan nhu tuc thi
                _xu_ly_tra_loi(env, cau_hinh, bay_gio, thong_bao)
                # 2. GHI LICH SU cho ngay hom qua — 1 gio mot lan.
                #    Chi goi Meta khi ngay do THIEU ban ghi tron ngay, nen chay
                #    song song voi bao cao khong giẫm chan nhau. Sau nay khi bo
                #    bao cao theo khung gio thi day chinh la nguon ghi so.
                if time.time() >= lan_thu_lich_su_ke:
                    lan_thu_lich_su_ke = time.time() + KHOANG_THU_LICH_SU
                    da_ghi, ly = agent_lich_su.ghi_neu_can(env, bay_gio)
                    if da_ghi:
                        report.log(f"AGENT: tu ghi lich su — {ly}")
                    elif ly.startswith("khong lay duoc") or ly.startswith("loi"):
                        report.log(f"AGENT: ghi lich su that bai — {ly}")
                # 3. QUET Meta, vong dai
                if time.time() >= lan_quet_ke:
                    _quet_va_de_xuat(env, cau_hinh, bay_gio, thong_bao)
                    lan_quet_ke = time.time() + nhip * 60
                    agent_ky_uc.cap_nhat_khoa(bay_gio)
            except Exception as e:              # vong lap khong duoc chet
                report.log(f"AGENT: loi trong vong lap: {type(e).__name__}: {e}")
            time.sleep(NHIP_NHANH_GIAY)
    except KeyboardInterrupt:
        print("\nDa bam Ctrl + C — agent dung.")
    finally:
        agent_ky_uc.nha_khoa()
        report.log("AGENT: da dung")
    return 0


if __name__ == "__main__":
    sys.exit(main())
