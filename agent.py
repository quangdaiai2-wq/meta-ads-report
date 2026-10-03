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
import os
import re
import subprocess
import sys
import time
from datetime import date, datetime, timedelta, timezone
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
    # 0 = KHONG GIOI HAN. Doi 01/10/2026 theo yeu cau cua Dai.
    # Truoc day 3/1/3 khien agent hoi duoc 3 nhom roi IM LANG suot ngay.
    "AGENT_TOI_DA_NGAY": 0,
    "AGENT_TOI_DA_DE_XUAT_MOI_VONG": 0,
    "AGENT_TOI_DA_CHO": 0,
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


def doc_moi(duong_dan=None):
    """Doc lai TOAN BO .env. Tra ve (env, cau_hinh).

    LOI THAT da gap 01/10/2026 — vi sao ham nay phai ton tai:
    Ban cu doc .env MOT LAN luc khoi dong, roi trong vong lap chi doc lai phan
    `AGENT_*` (qua `doc_cau_hinh`) va VUT phan con lai. Nghia la:
      - Doi `AGENT_TAP_SU` / `AGENT_NHIP_PHUT`  -> an ngay (dung nhu mong doi).
      - Doi khoa AI, `TELEGRAM_*`, `META_*`     -> KHONG an, phai khoi dong lai.
    Te hon: `khoi-dong-lai-agent.bat` ghi "doi .env khong can bam file nay" —
    cau do SAI voi cac khoa ngoai `AGENT_*`, nen Dai se doi `.env` roi ngoi doi
    mai khong thay gi khac.

    Nay vong lap goi ham nay moi 15 giay => MOI khoa trong .env deu an ngay.
    File .env nho, doc lai 15 giay mot lan khong dang ke.
    """
    env = report.load_env(duong_dan or ENV_PATH)
    return env, doc_cau_hinh(env)


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
            # ID CHIEN DICH: Dai tra tren Meta bang cai nay (chot 02/10/2026).
            "campaign_id": dt.get("campaign_id"),
            "ngan_sach_ngay_vnd": dt.get("ngan_sach_ngay_vnd"),
        },
        "ly_do": de_xuat.get("ly_do"),
        # Truong hop (1/2/3) va ten moi sau khi tat. Luu vao so de luc Dai bam
        # nut thi biet phai dat ten gi — khong tinh lai (so lieu da doi).
        "truong_hop": de_xuat.get("truong_hop"),
        "ten_moi": de_xuat.get("ten_moi"),
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


def _dem_nhom_da_hoi_hom_nay(ban_ghi, bay_gio):
    """So NHOM KHAC NHAU da duoc hoi Dai trong ngay.

    Dem theo NHOM chu KHONG dem theo BAN GHI. Vi sao: MOT lan xin phep sinh HAI
    ban ghi — ban de xuat (luc hoi Dai) va ban luc gui lenh len Meta (luc Dai
    bam nut). Dem theo ban ghi thi tran AGENT_TOI_DA_NGAY bi tieu ton GAP DOI.

    Loi that 01/10/2026: chi 2 nhom duoc hoi nhung dem ra 3 ⇒ agent IM LANG
    suot phan con lai cua ngay, Dai tuong no hong.
    """
    return len({
        str((r.get("doi_tuong") or {}).get("id") or "")
        for r in (ban_ghi or [])
        if isinstance(r, dict) and r.get("che_do") == "xin_phep"
        and (agent_ky_uc._gio(r.get("luc")) or datetime.min.replace(tzinfo=GIO_VN)).date()
        == bay_gio.date()
    })


def _xet_de_xuat(nhom, hom_nay, thang, loai_ten, cau_hinh, bay_gio,
                 ad_hom_nay=None, ad_thang=None):
    """Tra ve danh sach de xuat QUA DUOC rao an toan.

    MOI TRAN DAT 0 = KHONG GIOI HAN.

    VIEC B (Dai chot 02/10/2026): `ad_hom_nay` / `ad_thang` la chi tieu cap
    QUANG CAO. Truyen xuong `agent_muc_tieu.xet` de xet tung quang cao. De mac
    dinh None => ham van chay duoc nhu cu (cac kiem thu cu khong phai sua).

    LOI THAT 01/10/2026 — vi sao ham nay phai GHI LOG moi nhanh:
    Ban cu co ba cho `break` thoat IM LANG (het tran vong / het tran cho / het
    tran ngay). Dai hoi du 3 nhom luc 12:07 roi agent im lang suot buoi chieu:
    no VAN quet, VAN tim ra nhom can tat, nhung khong hoi duoc va cung khong
    bao gi. Dai tuong no hong, phai tu tat tay.
    Nay moi nhanh deu ghi log, va cuoi ham luon co MOT dong tong ket.
    """
    duyet = []
    lich_su = agent_ky_uc.dem_hanh_dong(bay_gio)
    lich_su["nhom_da_tra_loi"] = agent_ky_uc.nhom_da_tra_loi(bay_gio)
    lich_su["nhom_dang_bo_qua"] = agent_ky_uc.nhom_dang_bo_qua(bay_gio)
    # 🔴 MOI 03/10/2026: cho Rao 8 biet nhom nao da duoc BAT LAI sau khi Dai tra
    # loi — cau tra loi cu het gia tri thi phai cho hoi lai. Xem agent_rao.py.
    lich_su["nhom_bat_lai_gan_nhat"] = agent_ky_uc.nhom_bat_lai_gan_nhat(bay_gio)
    da_cho = set(agent_ky_uc.ma_dang_cho(bay_gio))
    nhom_da_hoi_hom_nay = _dem_nhom_da_hoi_hom_nay(agent_ky_uc.doc(), bay_gio)
    dem_de_xuat_hom_nay = nhom_da_hoi_hom_nay

    tran_vong = cau_hinh["AGENT_TOI_DA_DE_XUAT_MOI_VONG"]
    tran_cho = cau_hinh["AGENT_TOI_DA_CHO"]
    tran_ngay = cau_hinh["AGENT_TOI_DA_NGAY"]

    # 🔴 `bay_gio` BAT BUOC phai truyen — thieu no thi ten moi ghi nham thang
    # (va nam) vao ten nhom/quang cao. Truoc 02/10/2026 cho nay bi thieu.
    tat_ca = agent_muc_tieu.xet(nhom, hom_nay, thang, loai_ten,
                                bay_gio=bay_gio,
                                ad_hom_nay=ad_hom_nay, ad_thang=ad_thang)
    bo_qua_dang_cho = 0
    bi_rao_chan = 0
    dung_som = None

    for d in tat_ca:
        ten_ngan = d["doi_tuong"]["ten"][:40]
        ma = str(d["doi_tuong"]["id"])

        if tran_vong > 0 and len(duyet) >= tran_vong:
            dung_som = f"da du {tran_vong} de xuat moi vong"
            break
        if ma in da_cho:
            bo_qua_dang_cho += 1
            continue
        if tran_cho > 0 and len(da_cho) >= tran_cho:
            dung_som = f"da co {tran_cho} nhom dang cho Dai tra loi"
            break
        if tran_ngay > 0 and dem_de_xuat_hom_nay >= tran_ngay:
            dung_som = f"hom nay da hoi du {tran_ngay} nhom"
            break

        ok, ly = agent_rao.kiem(d, lich_su, bay_gio)
        if not ok:
            bi_rao_chan += 1
            report.log(f"AGENT: chan de xuat {ten_ngan!r}: {ly}")
            continue
        duyet.append(d)
        da_cho.add(ma)
        dem_de_xuat_hom_nay += 1

    # Mot dong TONG KET, luon ghi. Day la dong tra loi cau hoi "no co lam gi khong".
    if tat_ca or dung_som:
        report.log(
            f"AGENT: {len(tat_ca)} nhom cham nguong — hoi {len(duyet)}, "
            f"bo qua {bo_qua_dang_cho} (dang cho Dai tra loi), "
            f"chan {bi_rao_chan} (rao an toan)"
            + (f", DUNG SOM: {dung_som}" if dung_som else "")
        )
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


def _lam_theo_lenh(env, cau_hinh, bay_gio, thong_bao, noi_dung, tin_nhan_id):
    """Mot lenh cua Dai: HOAN TAC / DONG Y / BO QUA.

    Dung chung cho ca NUT BAM lan LENH GO TAY — mot duong xu ly duy nhat, nen
    khong the co chuyen nut bam lam duoc ma go tay thi khong.
    Tra ve so viec da lam (0 hoac 1).
    """
    dang_cho = {str((r.get("doi_tuong") or {}).get("id") or ""): r
                for r in agent_ky_uc.hang_cho(bay_gio)}

    # HOAN TAC phai kiem TRUOC: nhom duoc hoan tac KHONG con nam trong danh sach
    # "dang cho", nen neu dua vao doc_tra_loi(dang_cho) se bao khong khop.
    if lenh_telegram.la_hoan_tac(noi_dung):
        ma_hoan = lenh_telegram.ma_trong_lenh(noi_dung)
        if ma_hoan:
            return _lam_hoan_tac(env, cau_hinh, ma_hoan, noi_dung, tin_nhan_id,
                                 bay_gio, thong_bao)
        return 0

    # --- Hai nut tren TIN BAO LOI (Dai chot 02/10/2026) ---
    # Phai kiem TRUOC `dang_cho`: ban ghi loi DA co `dai_phan_hoi` nen khong con
    # nam trong danh sach "dang cho" — dua vao do se bao "khong khop".
    ma_trong = lenh_telegram.ma_trong_lenh(noi_dung)
    if ma_trong:
        kq_loi, _ = agent_xin_phep.doc_tra_loi(noi_dung, {ma_trong})
        if kq_loi == "quet_lai":
            agent_ky_uc.xoa_bo_qua(ma_trong)
            _bao_ket_qua(env, {"tin_nhan_id": tin_nhan_id}, thong_bao, "\n".join([
                "\U0001f501 ĐÃ GHI NHẬN — sẽ quét lại lần sau",
                "",
                f"Nhóm: {ma_trong}",
                "Agent sẽ thử lại ở lần quét kế tiếp.",
            ]))
            report.log(f"AGENT: Dai chon QUET LAI nhom {ma_trong}")
            return 0
        if kq_loi == "bo_qua_24h":
            den = bay_gio + timedelta(hours=24)
            agent_ky_uc.bo_qua_nhom(ma_trong, den)
            _bao_ket_qua(env, {"tin_nhan_id": tin_nhan_id}, thong_bao, "\n".join([
                "\u23f8 ĐÃ BỎ QUA 24 GIỜ",
                "",
                f"Nhóm: {ma_trong}",
                f"Agent sẽ xét lại nhóm này sau {den.strftime('%H:%M ngày %d/%m')}.",
            ]))
            report.log(f"AGENT: Dai chon BO QUA 24h nhom {ma_trong}")
            return 0

    ket_qua, ma = agent_xin_phep.doc_tra_loi(noi_dung, set(dang_cho))
    if ket_qua not in ("dong_y", "dong_y_ha_ngan_sach", "tu_choi") or ma not in dang_cho:
        return 0
    ban_ghi = dang_cho[ma]
    if ket_qua == "tu_choi":
        agent_ky_uc.cap_nhat_phan_hoi(ma, noi_dung, "Đại nói bỏ qua")
        dt_bo = ban_ghi.get("doi_tuong") or {}
        if dt_bo.get("cap") == "ad":
            dong_bo = [
                "\u23ed ĐÃ BỎ QUA — không làm gì",
                "",
                f"Quảng cáo: {dt_bo.get('ten')}",
                f"Thuộc nhóm: {dt_bo.get('ten_nhom')}",
                "",
                "Agent sẽ không đề xuất lại quảng cáo này trong 24 giờ.",
            ]
        else:
            dong_bo = [
                "\u23ed ĐÃ BỎ QUA — không làm gì",
                "",
                f"Nhóm: {dt_bo.get('ten')}",
                "",
                "Agent sẽ không đề xuất lại nhóm này trong 24 giờ.",
            ]
        _bao_ket_qua(env, ban_ghi, thong_bao, "\n".join(dong_bo))
        report.log(f"AGENT: Dai bo qua {ma} (cap={dt_bo.get('cap') or 'ad_set'})")
        return 0
    # ⚠️ PHAI truyen `ket_qua` xuong: `_lam_theo_dong_y` dua vao do de biet Dai
    # chon "tat nhom" hay "tat + ha ngan sach". Thieu no thi nut "tat + ha ngan
    # sach" se im lang khong ha ngan sach.
    return _lam_theo_dong_y(env, cau_hinh, ban_ghi,
                            {"noi_dung": noi_dung, "ket_qua": ket_qua},
                            bay_gio, thong_bao)


def _la_yeu_cau_bao_cao(text):
    """Tin nay la YEU CAU GUI BAO CAO, khong phai cau hoi so lieu.

    Vi sao phai phan biet: "bao cao hom qua" = xin GUI FILE; con
    "bao cao hom qua the nao?" = CAU HOI (de AI tra loi). Phan biet bang
    tu khoa hoi, va bang viec chi cho phep vai tu chi ngay thang theo sau.
    """
    chu = lenh_telegram.bo_dau(text)
    if not chu:
        return False
    if "?" in chu or "bao nhieu" in chu or "the nao" in chu or "ra sao" in chu:
        return False
    phan = chu.split()
    # Cho phep cach noi "gui bao cao ..." / "lay bao cao ..." / "cho toi bao cao ..."
    if (len(phan) >= 3 and phan[0] in ("gui", "lay", "xem", "cho", "muon")
            and phan[1] == "bao" and phan[2] == "cao"):
        phan = phan[1:]
    if len(phan) < 2 or phan[0] != "bao" or phan[1] != "cao":
        return False
    # Sau "bao cao" chi duoc la tu chi ngay thang, mot NGAY CU THE (15/09,
    # 2026-09-15), hoac loi xin. "bao cao thang 9" thi KHONG phai yeu cau gui
    # file -> de AI tra loi.
    for x in phan[2:]:
        if x in {"hom", "qua", "nay", "ngay", "toi", "cho", "cua", "lai", "di", "giup"}:
            continue
        if re.fullmatch(r"\d{1,4}([/\-.]\d{1,4}){1,2}", x):
            continue
        return False
    return True


def _tao_ngay(nam, thang, ngay):
    """date hop le, hoac None."""
    try:
        return date(nam, thang, ngay)
    except ValueError:
        return None


def _ngay_duoc_neu(text, bay_gio):
    """Ngay CU THE, phai DU ngay/thang/nam. Khong co -> None.

    Nhan: 20/09/2026 · 20-09-2026 · 2026-09-20.
    KHONG nhan ngay thieu nam ("20/09") — doan nam rat de sai, nen
    `_co_ngay_thieu_nam()` lo phan nhac Dai ghi ro.
    "hom qua" / "hom nay" cung tra ve None — hai cai do di duong MOC GIO.
    """
    if not isinstance(text, str):
        return None
    m = re.search(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b", text)
    if m:
        return _tao_ngay(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.search(r"\b(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})\b", text)
    if m:
        return _tao_ngay(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    return None


def _co_ngay_thieu_nam(text):
    """Tin co ngay kieu "20/09" (THIEU nam) khong — de nhac Dai ghi ro.

    Phai loai truong hop ngay DU nam truoc: "20/09/2026" cung chua chuoi "20/09"
    ben trong no, neu khong loai thi se nhac nham nguoi da ghi dung.
    """
    if not isinstance(text, str):
        return False
    if re.search(r"\b\d{1,2}[/\-.]\d{1,2}[/\-.]\d{4}\b", text):
        return False
    if re.search(r"\b\d{4}-\d{1,2}-\d{1,2}\b", text):
        return False
    return bool(re.search(r"\b\d{1,2}[/\-.]\d{1,2}\b", text))


def _moc_cho_bao_cao(text, bay_gio, danh_sach_moc):
    """Chon moc gio de gui bao cao.

    Mac dinh = moc NHO NHAT (thuong la 8) — theo dung quy uoc cua report.py:
    moc 8 la "bao cao ve NGAY HOM TRUOC", tuc mot ngay TRON VEN.
    "hom nay" thi lay moc lon nhat DA QUA.
    """
    moc = sorted(danh_sach_moc) or [8]
    if "hom nay" in lenh_telegram.bo_dau(text) or "nay" in lenh_telegram.bo_dau(text).split():
        da_qua = [m for m in moc if m <= bay_gio.hour]
        return max(da_qua) if da_qua else min(moc)
    return min(moc)


def _gui_bao_cao_theo_yeu_cau(env, noi_dung, bay_gio):
    """Dai yeu cau -> chay report.py; CHINH NO gui tin bao cao + file HTML.

    Dung lai report.py chu KHONG tu dung bao cao: nho vay so lieu, bo loc,
    phan nhan dinh AI va file HTML GIONG HET bao cao theo moc gio.

    - Neu tin neu MOT NGAY CU THE ("bao cao 15/09") -> `--ngay YYYY-MM-DD`.
      Cach nay lay so TRUC TIEP tu Meta, KHONG phu thuoc so — nen hoi duoc
      ngay bat ky trong qua khu.
    - Con lai -> `--slot <moc>` nhu bao cao theo moc gio (mac dinh = hom qua).
    - Luon dung `--force`: Dai da yeu cau thi phai gui, du hom nay da gui roi.
    """
    ngay = _ngay_duoc_neu(noi_dung, bay_gio)

    # Ngay THIEU nam ("bao cao 20/09") -> nhac Dai ghi ro, KHONG doan bua.
    if ngay is None and _co_ngay_thieu_nam(noi_dung):
        nguoi_truc.gui_tin_nhan(env, "\u26a0\ufe0f \u0110\u1ea1i ghi r\u00f5 ng\u00e0y/th\u00e1ng/n\u0103m gi\u00fap t\u00f4i nh\u00e9.\n"
                                     "V\u00ed d\u1ee5: b\u00e1o c\u00e1o 20/09/2026")
        report.log("AGENT: yeu cau bao cao thieu nam -> da nhac Dai ghi ro")
        return

    # Ngay o TUONG LAI thi khong co so lieu.
    if ngay is not None and ngay > bay_gio.date():
        nguoi_truc.gui_tin_nhan(
            env, f"\u26a0\ufe0f Ng\u00e0y {ngay.strftime('%d/%m/%Y')} ch\u01b0a t\u1edbi n\u00ean ch\u01b0a c\u00f3 s\u1ed1 li\u1ec7u.")
        return

    if ngay is not None:
        mo_ta = f"ng\u00e0y {ngay.strftime('%d/%m/%Y')}"
        lenh = [sys.executable, str(GOC / "report.py"),
                "--ngay", ngay.isoformat(), "--force"]
    else:
        danh_sach_moc = report.doc_moc_tu_env(env)
        slot = _moc_cho_bao_cao(noi_dung, bay_gio, danh_sach_moc)
        mo_ta = f"m\u1ed1c {slot}h"
        lenh = [sys.executable, str(GOC / "report.py"),
                "--slot", str(slot), "--force"]

    nguoi_truc.gui_tin_nhan(
        env, f"\u23f3 \u0110ang l\u1ea5y b\u00e1o c\u00e1o {mo_ta}... kho\u1ea3ng 20\u201330 gi\u00e2y.")
    moi_truong = dict(os.environ)
    moi_truong["PYTHONIOENCODING"] = "utf-8"
    khong_cua_so = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        kq = subprocess.run(
            lenh, cwd=str(GOC), capture_output=True, text=True,
            encoding="utf-8", errors="replace", env=moi_truong,
            timeout=CHO_BAO_CAO_TOI_DA, creationflags=khong_cua_so,
        )
    except Exception as e:
        nguoi_truc.gui_tin_nhan(env, f"\u26a0\ufe0f Kh\u00f4ng ch\u1ea1y \u0111\u01b0\u1ee3c b\u00e1o c\u00e1o {mo_ta}: {e}")
        report.log(f"AGENT: loi khi gui bao cao theo yeu cau: {type(e).__name__}: {e}")
        return
    if kq.returncode == 0:
        report.log(f"AGENT: da gui bao cao {mo_ta} theo yeu cau cua Dai")
        return
    nguoi_truc.gui_tin_nhan(
        env, f"\u26a0\ufe0f B\u00e1o c\u00e1o {mo_ta} l\u1ed7i (m\u00e3 {kq.returncode}). "
             f"Xem logs\\baocao.log.")
    report.log(f"AGENT: bao cao theo yeu cau THAT BAI {mo_ta}, ma {kq.returncode}")


def _nghe_telegram(env, cau_hinh, bay_gio, thong_bao, tt_tg):
    """Doc tin Telegram moi va xu ly. ĐÂY LÀ NƠI DUY NHẤT đọc tin của bot.

    Vi sao agent phai tu doc: `getUpdates` của Telegram chỉ giao mỗi tin cho MỘT
    nơi gọi. Trước đây `nguoi_truc.py` đọc rồi chuyển tiếp qua
    `logs/agent-lenh.json` — chạy được, nhưng thừa một mắt xích và chính nó sinh ra
    hai lỗi thật ngày 30/09/2026. Từ 01/10/2026 agent đọc trực tiếp.
    """
    if not tt_tg["da_doc_ton_dong"]:
        _doc_tin_ton_dong(env, cau_hinh, bay_gio, thong_bao, tt_tg)
        return
    ds, loi = nguoi_truc.lay_tin_moi(env, tt_tg["offset"])
    if loi:
        report.log(f"AGENT: khong lay duoc tin Telegram: {loi}")
        return
    if not ds:
        return
    tt_tg["offset"] = nguoi_truc.offset_moi_tu_ket_qua(ds)
    for tin in ds:
        try:
            _xu_ly_mot_tin(env, cau_hinh, bay_gio, thong_bao, tt_tg, tin)
        except Exception as e:
            # MOT tin hong KHONG duoc giet ca vong lap (bai hoc that 30/09/2026).
            report.log(f"AGENT: loi khi xu ly mot tin Telegram: {e}")


def _doc_tin_ton_dong(env, cau_hinh, bay_gio, thong_bao, tt_tg):
    """Lan dau khoi dong: doc het tin dang cho, XU LY lenh/nut bam, BO cau hoi cu.

    Vi sao khong tra loi cau hoi cu: bot se tra loi mot loat tin nhan cu mot luc,
    roi loan. Nhung LENH va NUT BAM thi PHAI xu ly — bo di là mất việc Đại đã làm
    (lỗi thật đã gặp 30/09/2026).
    """
    chat_id_dai = env.get("TELEGRAM_CHAT_ID", "")
    ds, loi = nguoi_truc.lay_tin_moi(env, None)
    if loi:
        report.log(f"AGENT: chua doc duoc tin ton dong: {loi}")
        return
    so_viec = 0
    for tin in ds or []:
        try:
            if isinstance(tin, dict) and "callback_query" in tin:
                if nguoi_truc.tin_tu_dai_nut_bam(tin, chat_id_dai):
                    _xu_ly_mot_tin(env, cau_hinh, bay_gio, thong_bao, tt_tg, tin)
                    so_viec += 1
                continue
            if not nguoi_truc.tin_tu_dai(tin, chat_id_dai):
                continue
            noi_dung = nguoi_truc.noi_dung_tin(tin)
            if lenh_telegram.la_hoan_tac(noi_dung) or lenh_telegram.la_lenh(noi_dung):
                _xu_ly_mot_tin(env, cau_hinh, bay_gio, thong_bao, tt_tg, tin)
                so_viec += 1
        except Exception as e:
            report.log(f"AGENT: loi khi doc tin ton dong: {e}")
    tt_tg["offset"] = nguoi_truc.offset_moi_tu_ket_qua(ds or [])
    tt_tg["da_doc_ton_dong"] = True
    report.log(f"AGENT: doc {len(ds or [])} tin ton dong, xu ly {so_viec} lenh/nut bam")


def _xu_ly_mot_tin(env, cau_hinh, bay_gio, thong_bao, tt_tg, tin):
    """Mot update Telegram: nut bam / lenh go tay / cau hoi."""
    chat_id_dai = env.get("TELEGRAM_CHAT_ID", "")

    if isinstance(tin, dict) and "callback_query" in tin:
        if not nguoi_truc.tin_tu_dai_nut_bam(tin, chat_id_dai):
            report.log("AGENT: bo qua nut bam tu nguoi la")
            return
        # Phai tra loi Telegram NGAY, khong thi nut quay mai tren man hinh Dai.
        nguoi_truc.tra_loi_nut_bam(env, nguoi_truc.ma_lan_bam(tin))
        _lam_theo_lenh(env, cau_hinh, bay_gio, thong_bao,
                       nguoi_truc.du_lieu_nut_bam(tin),
                       nguoi_truc.ma_tin_nhan_nut_bam(tin))
        return

    if not nguoi_truc.tin_tu_dai(tin, chat_id_dai):
        try:
            chat_id_la = tin["message"]["chat"]["id"]
        except (KeyError, TypeError):
            chat_id_la = "?"
        report.log(f"AGENT: bo qua tin tu chat_id la ({chat_id_la})")
        return

    noi_dung = nguoi_truc.noi_dung_tin(tin)

    # LENH phai kiem TRUOC khi goi tra_loi_tin_nhan: ham do co nhanh "ghi lenh
    # vao hang doi" — mà hàng đợi này không còn ai đọc nữa.
    if lenh_telegram.la_hoan_tac(noi_dung) or lenh_telegram.la_lenh(noi_dung):
        _lam_theo_lenh(env, cau_hinh, bay_gio, thong_bao, noi_dung, None)
        return

    # YEU CAU GUI BAO CAO -> chay report.py; no tu gui tin + FILE HTML.
    if _la_yeu_cau_bao_cao(noi_dung):
        _gui_bao_cao_theo_yeu_cau(env, noi_dung, bay_gio)
        return

    # Cau hoi -> dung lai DUNG ham cua nguoi truc (ham thuan, da co kiem thu).
    tra_loi = nguoi_truc.tra_loi_tin_nhan(
        cau_hoi=noi_dung,
        env=env,
        danh_sach_moc=report.doc_moc_tu_env(env),
        bat_dau=tt_tg["bat_dau"],
        lan_gui_cuoi=tt_tg["lan_gui_cuoi"],
        lan_gui_cuoi_txt="do tiến trình báo cáo gửi (agent không theo dõi)",
        da_gui=report.ds_moc_da_gui(bay_gio.strftime("%Y-%m-%d")),
        now=bay_gio,
        nhan="Agent (nấc 2)",
    )
    if nguoi_truc.gui_tin_nhan(env, tra_loi):
        report.log("AGENT: da tra loi mot tin nhan")


def _lam_theo_dong_y(env, cau_hinh, ban_ghi, kq, bay_gio, thong_bao):
    """Dai da dong y. Kiem lai rao, ghi so TRUOC, roi moi gui len Meta."""
    doi_tuong = ban_ghi.get("doi_tuong") or {}
    # 🔴 VIEC B (Dai chot 02/10/2026): doi tuong co the la NHOM (cap="ad_set")
    # hoac QUANG CAO (cap="ad"). Rao an toan phan biet hai cap va ap bo rao
    # khac nhau — tat le quang cao KHONG duoc ha ngan sach.
    la_cap_ad = (doi_tuong.get("cap") == "ad")
    de_xuat = {
        "hanh_dong": ban_ghi.get("hanh_dong"),
        "doi_tuong": doi_tuong,
        "ngan_sach_ha": None if la_cap_ad else agent_rao.NGAN_SACH_HA,
        "luot_mua": ban_ghi.get("luot_mua"),
        "chi_phi_moi_luot": ban_ghi.get("chi_phi_moi_luot"),
        "tao_luc": ban_ghi.get("luc"),
    }
    lich_su = agent_ky_uc.dem_hanh_dong(bay_gio)
    ok, ly = agent_rao.kiem(de_xuat, lich_su, bay_gio)
    ma = str(doi_tuong.get("id"))

    if not ok:
        agent_ky_uc.cap_nhat_phan_hoi(ma, kq["noi_dung"], f"chan khi lam lai: {ly}")
        _bao_ket_qua(env, ban_ghi, thong_bao,
                     f"⚠️ Không tắt được {('quảng cáo' if la_cap_ad else 'nhóm')} "
                     f"{ma}\nLý do: {ly}")
        report.log(f"AGENT: chan khi lam lai {ma} (cap="
                   f"{'ad' if la_cap_ad else 'ad_set'}): {ly}")
        return 0

    if cau_hinh["AGENT_TAP_SU"]:
        agent_ky_uc.cap_nhat_phan_hoi(
            ma, kq["noi_dung"], "CHE DO TAP SU — da ghi so, CHUA gui len Meta")
        _bao_ket_qua(env, ban_ghi, thong_bao, "\n".join([
            "\U0001f9ea CHẾ ĐỘ TẬP SỰ — ĐÃ GHI NHẬN",
            "",
            (f"Đại đã đồng ý tắt quảng cáo {ma}." if la_cap_ad
             else f"Đại đã đồng ý tắt nhóm {ma}."),
            "Nhưng agent đang ở chế độ tập sự nên CHƯA gửi lệnh lên Meta.",
            "Muốn agent làm thật: đổi AGENT_TAP_SU=false trong .env.",
        ]))
        report.log(f"AGENT: tap su, khong gui lenh cho {ma}")
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

    if la_cap_ad:
        # ══════════ VIEC B: TAT LE MOT QUANG CAO ══════════
        # Dai chot 02/10/2026: "chi tat quang cao dang chay va chi tieu den
        # nguong thoi". Tat le CHI TAT + DOI TEN — KHONG ha ngan sach.
        # Ham tu doc lai TEN NHOM chua quang cao roi kiem pham vi truoc khi ghi.
        thanh_cong, ket_qua, chi_tiet = agent_cong_cu_ghi.tat_mot_quang_cao(
            env, ma, ten_nhom=doi_tuong.get("ten_nhom"),
            ten_moi=ban_ghi.get("ten_moi"))
    else:
        # DAI CHON KIEU TAT NAO (chot 02/10/2026):
        #   "dong_y"              -> CHI tat nhom, GIU nguyen ngan sach
        #   "dong_y_ha_ngan_sach" -> tat nhom + ha ngan sach ve 27.000d
        ha_ngan_sach = (kq.get("ket_qua") == "dong_y_ha_ngan_sach")
        ngan_sach_dat = agent_rao.NGAN_SACH_HA if ha_ngan_sach else None

        # 🔴 XU LY CBO (Dai chot 09:22 03/10/2026):
        # Nếu nhóm thuộc chiến dịch Advantage+ (daily_budget=None = NS cấp chiến dịch),
        # dùng hàm chuyên biệt: tắt nhóm + đổi tên + CHUYỂN NS cho nhóm còn sống.
        cbo = False
        try:
            truoc, _ = agent_cong_cu_ghi.doc_lai_nhom(env, ma)
            if truoc:
                dg = str(truoc.get("daily_budget") or "").strip()
                cbo = dg in ("", "0", "0.0", "None", "null")
        except Exception:
            pass
        if cbo:
            # Phát hiện CBO → đọc campaign_id từ data đã lưu
            ma_chien_dich = doi_tuong.get("campaign_id", "")
            ten_nhom_truoc = truoc.get("name") or doi_tuong.get("ten", "")
            report.log(f"AGENT: phat hien CBO cho {ma} (camp={ma_chien_dich})")
            # ---- Bước 1: Tắt nhóm + đổi tên + chuyển NS cho nhóm sống ----
            thanh_cong, ket_qua, chi_tiet = agent_cong_cu_ghi.tat_nhom_cbo(
                env, ma, ma_chien_dich, [], ten_nhom_truoc,
                ten_moi=ban_ghi.get("ten_moi"))
            # ---- Bước 2: Kiểm tra TH2 — hết nhóm thì tắt chiến dịch ----
            if thanh_cong:
                ok_th2, msg_th2, ct_th2 = agent_cong_cu_ghi.xu_ly_th2_cbo(
                    env, ma_chien_dich, [])
                chi_tiet["th2_ket_qua"] = msg_th2
                chi_tiet.update(ct_th2)
                if not ok_th2:
                    thanh_cong = False
                    ket_qua = f"tát nhóm thành công nhưng lỗi tắt chiến dịch: {msg_th2}"
                else:
                    # 🔴 MOI 03/10/2026: TH2 TU tat chien dich — Dai KHONG bam nut
                    # nen phai bao rieng. Thieu buoc nay thi Dai tuong bot chet
                    # (dung su co 03/10 voi chien dich 120250389649450509).
                    if ct_th2.get("tat_chien_dich"):
                        chi_tiet["ten_chien_dich"] = _ten_chien_dich(
                            env, ma_chien_dich)
                        _bao_tu_hanh(env, thong_bao, chi_tiet, bay_gio)
        else:
            # Thu tu (Dai doi 02/10/2026): TAT NHOM TRUOC, roi moi tat QUANG CAO.
            # Ban cu lam nguoc: tat quang cao truoc. Neu buoc tat nhom bi Meta tu choi
            # thi quang cao da tat mat roi — nhom con chay ma khong con quang cao, roi
            # vao TRANG THAI NUA VOI. Nay tat nhom xong moi dung toi quang cao.
            # Moi lan ghi len Meta phai cach nhau CHO_GIUA_HAI_LAN_GHI giay — Meta chan
            # "(#613) rate limit" neu ghi qua nhanh (da gap that 01/10/2026).
            thanh_cong, ket_qua, chi_tiet = agent_cong_cu_ghi.tam_dung_va_ha_ngan_sach(
                env, ma, ngan_sach_dat, ten_moi=ban_ghi.get("ten_moi"))

    # ---------- THAT BAI: KHONG TAT GI CA, bao loi + 2 nut ----------
    if not thanh_cong:
        # Danh dau `ghi_meta_that_bai` de nha'c khoi khoa nhom 24 gio — Dai da
        # bam nut nhung viec chua xong, va Dai muon "lan quet sau thu lai".
        agent_ky_uc.cap_nhat_phan_hoi(ma, kq["noi_dung"], ket_qua,
                                      ghi_meta_that_bai=True)
        nguyen_nhan = chi_tiet.get("nguyen_nhan")
        ma_tin_loi = agent_xin_phep.gui_tin_loi(env, ban_ghi, ket_qua, nguyen_nhan)
        if ma_tin_loi is None:
            _bao_ket_qua(env, ban_ghi, thong_bao,
                         agent_xin_phep.soan_tin_loi(ban_ghi, ket_qua, nguyen_nhan))
        report.log(f"AGENT: KHONG tat duoc nhom {ma} — {ket_qua} "
                   f"| nguyen nhan: {nguyen_nhan or 'chua ro'}")
        return 0

    if la_cap_ad:
        # ---------- TAT LE QUANG CAO: xong, khong dung toi nhom ----------
        agent_ky_uc.cap_nhat_phan_hoi(ma, kq["noi_dung"], ket_qua)
        dong = ["✅ ĐÃ TẮT QUẢNG CÁO"]
        dong += agent_xin_phep.dong_doi_tuong(ban_ghi)
        dong += [
            f"Nhóm chứa nó: {doi_tuong.get('ten_nhom')}",
            f"Quảng cáo: {doi_tuong.get('ten')}",
            f"Kết quả: {ket_qua}",
        ]
        if ban_ghi.get("ten_moi"):
            dong.append(f"Tên mới: {ban_ghi.get('ten_moi')}")
        dong.append("Ngân sách nhóm: giữ nguyên (tắt lẻ không đụng ngân sách)")
        dong += ["", "Nhóm vẫn đang chạy với các quảng cáo còn lại."]
        _bao_ket_qua(env, ban_ghi, thong_bao, "\n".join(dong))
        report.log(f"AGENT: tat le quang cao {ma} trong nhom "
                   f"{doi_tuong.get('ten_nhom')!r} — {ket_qua}")
        return 1

    # ---------- THANH CONG: gio moi tat quang cao ben trong ----------
    tat_qc_ok, tat_qc_ly, ct_qc = agent_cong_cu_ghi.tat_quang_cao(
        env, ma, ten_nhom=doi_tuong.get("ten"))
    agent_ky_uc.cap_nhat_phan_hoi(ma, kq["noi_dung"], ket_qua)

    dong = ["✅ ĐÃ TẮT NHÓM"]
    dong += agent_xin_phep.dong_doi_tuong(ban_ghi)
    dong += [
        f"Nhóm: {doi_tuong.get('ten')}",
        f"Kết quả: {ket_qua}",
    ]
    if ban_ghi.get("ten_moi"):
        dong.append(f"Tên mới: {ban_ghi.get('ten_moi')}")
    # Hiển thị thông tin ngân sách khác nhau theo loại
    if cbo and chi_tiet.get("loai") == "CBO":
        # CBO: hiển thị chuyển NS + (nếu có) TH2 tắt chiến dịch
        if chi_tiet.get("chuyen_ns_ket_qua"):
            dong.append(chi_tiet["chuyen_ns_ket_qua"])
        if chi_tiet.get("th2_ket_qua"):
            dong.append(chi_tiet["th2_ket_qua"])
    elif chi_tiet.get("cbo_khong_ha_ngan_sach"):
        dong.append("Ngân sách: KHÔNG hạ được — nhóm thuộc chiến dịch Advantage+ "
                    "(ngân sách cấp chiến dịch), Meta không cho hạ cấp nhóm. "
                    "Đã tắt nhóm + đổi tên. Muốn giảm chi chung, hạ ngân sách "
                    "chiến dịch thủ công trong Trình quản lý quảng cáo.")
    else:
        dong.append("Ngân sách: "
                    + ("đã hạ về 27.000đ" if ha_ngan_sach else "giữ nguyên (theo ý Đại)"))
    dong.append(f"Quảng cáo bên trong: {'đã tắt' if tat_qc_ok else 'LỖI — ' + tat_qc_ly}")
    dong += ["", "Bấm nút bên dưới nếu muốn BẬT LẠI (chỉ trong 24 giờ)."]
    _bao_ket_qua(env, ban_ghi, thong_bao, "\n".join(dong),
                 nut=agent_xin_phep.nut_hoan_tac(ma))
    report.log(f"AGENT: tat nhom {ma} — {ket_qua} | quang cao: {tat_qc_ly} "
               f"| ha ngan sach: {'co' if ha_ngan_sach else 'khong'}")
    return 1


def _tao_thong_bao(env, che_do_thu):
    """Ham gui tin cho Dai. Che do thu thi chi in ra man hinh."""
    def thong_bao(text):
        if che_do_thu:
            print("[THU] se gui Telegram:\n" + text + "\n")
            return
        nguoi_truc.gui_tin_nhan(env, text)
    return thong_bao


def _ten_chien_dich(env, ma_chien_dich):
    """Doc TEN chien dich tu Meta. Khong doc duoc -> chuoi rong (khong nem loi).

    Dung cho tin bao agent tu hanh: co ten thi Dai de nhan ra hon la chi co ma.
    """
    try:
        import agent_cong_cu_ghi
        du, loi = agent_cong_cu_ghi.doc_lai_chien_dich(env, ma_chien_dich)
        if loi or not du:
            return ""
        return str(du.get("name") or "")
    except Exception:
        return ""


def _bao_tu_hanh(env, thong_bao, chi_tiet, bay_gio):
    """Bao Dai biet agent vua TU LAM gi (khong do Dai bam nut).

    🔴 VI SAO CAN (Dai chot 03/10/2026): ngay 03/10 agent tu tat chien dich
    120250389649450509 theo luong TH2 CBO nhung im lang. Dai tuong bot chet
    nen phai tu vao Meta tat tay. Day la kenh MOT CHIEU agent -> Dai.
    Khong bao gio nem loi: bao tin hong khong duoc lam sap agent.
    """
    try:
        tin = agent_xin_phep.soan_tin_tu_hanh(chi_tiet, bay_gio)
        if not tin:
            return
        thong_bao(tin)
        report.log(f"AGENT: da bao Dai viec tu hanh "
                   f"({chi_tiet.get('campaign_id') or ''})")
    except Exception as e:
        report.log(f"AGENT: loi khi bao viec tu hanh: {type(e).__name__}: {e}")


def _quet_va_de_xuat(env, cau_hinh, bay_gio, thong_bao, che_do_thu=False):
    """Phan CHAM: doc so tu Meta roi de xuat. Chay moi AGENT_NHIP_PHUT phut."""
    import agent_doc_meta
    # 🔴 CHU KY DOI 02/10/2026 (Viec B): 3 phan tu -> 5 phan tu.
    #    Them `ad_hom_nay` / `ad_thang` = chi tieu cap QUANG CAO (level=ad).
    nhom, hom_nay, thang, ad_hom_nay, ad_thang = agent_doc_meta.doc_so(env)
    report.log(f"AGENT: {len(nhom)} nhom, {len(hom_nay)} co chi tieu hom nay, "
               f"{len(thang)} co chi tieu thang, {len(ad_hom_nay)} dong quang cao "
               f"hom nay, {len(ad_thang)} dong quang cao thang")

    loai_ten = [x.strip() for x in (env.get("FILTER_EXCLUDE") or "").split(",") if x.strip()]
    duyet = _xet_de_xuat(nhom, hom_nay, thang, loai_ten, cau_hinh, bay_gio,
                         ad_hom_nay=ad_hom_nay, ad_thang=ad_thang)
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
    # KHONG doc Telegram o day. Chi vong lap CHAY LIEN TUC duoc doc tin —
    # vi `getUpdates` chi giao moi tin cho MOT noi goi, doc o day nua la
    # NUOT TIN cua tien trinh chinh dang chay.
    return _quet_va_de_xuat(env, cau_hinh, bay_gio, thong_bao, che_do_thu)


NHIP_NHANH_GIAY = 15

# Ghi lich su: thu moi 1 gio mot lan. Viec nhe (chi doc file), va CHI goi Meta
# khi ngay do THIEU ban ghi tron ngay — nen khong ton gi va khong giẫm chan
# bao cao theo khung gio (bao cao ghi truoc thi agent thoi).
KHOANG_THU_LICH_SU = 60 * 60

# Cho toi da khi chay report.py theo yeu cau cua Dai (giay).
CHO_BAO_CAO_TOI_DA = 600


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

    env, cau_hinh = doc_moi()
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
    # Trang thai doc Telegram: `offset` de Telegram biet da xac nhan toi dau;
    # `da_doc_ton_dong` de lan dau khoi dong biet phai don tin cu truoc.
    tt_tg = {"offset": None, "da_doc_ton_dong": False,
             "bat_dau": _thoi_diem(), "lan_gui_cuoi": None}
    che_do_cu = che_do
    try:
        while True:
            try:
                # DOC LAI TOAN BO .env MOI VONG.
                # Khong chi doc lai phan AGENT_* nhu ban cu: lam vay thi doi
                # khoa AI / TELEGRAM_* / META_* se KHONG co tac dung cho toi khi
                # khoi dong lai, ma `khoi-dong-lai-agent.bat` lai ghi la khong
                # can. Xem docstring cua doc_moi().
                env, cau_hinh = doc_moi()
                nhip = max(1, cau_hinh["AGENT_NHIP_PHUT"])
                che_do_moi = ("TAP SU (chi noi)" if cau_hinh["AGENT_TAP_SU"]
                              else "LAM THAT")
                if che_do_moi != che_do_cu:
                    report.log(f"AGENT: DOI CHE DO -> {che_do_moi}")
                    print(f"Che do da doi -> {che_do_moi}")
                    che_do_cu = che_do_moi

                bay_gio = _thoi_diem()
                thong_bao = _tao_thong_bao(env, False)
                # 1. NGHE Telegram, vong ngan — bam nut la xu ly gan nhu tuc thi
                _nghe_telegram(env, cau_hinh, bay_gio, thong_bao, tt_tg)
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
