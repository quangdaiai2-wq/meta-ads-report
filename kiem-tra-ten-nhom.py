# -*- coding: utf-8 -*-
"""KIEM TRA TEN NHOM CO DUNG CHUAN KHONG — CHI DOC, KHONG GHI.

Muc dich: tim nhung nhom co hau to SAI (thieu nam), vi du 'X10' thay vi 'X10-26'.
Loi nay xay ra khi agent chay BAN CODE CU (agent chi nap code MOT LAN luc khoi
dong, nen sau khi sua code PHAI khoi dong lai).

Cach chay:  bam file  kiem-tra-ten-nhom.bat  (hoac chay truc tiep bang python)

KHONG GOI LENH GHI NAO LEN META.
"""
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent
sys.path.insert(0, str(GOC))

import agent_doc_meta                                     # noqa: E402

# Hau to CHUAN phai co dang 'X<thang>-<2 chu so nam>', vi du X10-26.
# Hau to SAI la 'X<thang>' khong kem nam, vi du X10.
import re                                                 # noqa: E402

RE_HAU_TO_CHUAN = re.compile(r"\s+\d+\s*/\s*\d+\s+X\d+-\d{2}(\s+[A-Za-zÀ-ỹ]+)*"
                             r"(\s*=>\s*[^\s]+)?\s*$")
RE_CO_Hau_TO = re.compile(r"\s+\d+\s*/\s*\d+(\s+X\d+(-\d+)?)?")

# Trang thai coi nhu "dang anh huong chi tieu"
TRANG_THAI_DANG_CHAY = ("ACTIVE",)


def doc_env():
    env = {}
    p = GOC / ".env"
    if not p.exists():
        return env
    with open(p, encoding="utf-8") as f:
        for dong in f:
            dong = dong.strip()
            if dong and not dong.startswith("#") and "=" in dong:
                k, v = dong.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def main():
    env = doc_env()
    print("=" * 100)
    print("KIEM TRA TEN NHOM — CHI DOC, KHONG GHI GI LEN META")
    print("=" * 100)

    nhom = agent_doc_meta.doc_nhom_dang_chay(env)
    print(f"\nDoc duoc {len(nhom)} nhom dang chay.\n")

    sai_dang_chay = []
    sai_da_tat = []
    for a in nhom:
        ten = a.get("name") or ""
        if not RE_CO_Hau_TO.search(ten):
            continue                       # nhom chua dat ten theo luat => bo qua
        dung = bool(RE_HAU_TO_CHUAN.search(ten))
        if dung:
            continue
        tt = (a.get("effective_status") or "").upper()
        if tt in TRANG_THAI_DANG_CHAY:
            sai_dang_chay.append(a)
        else:
            sai_da_tat.append(a)

    def in_ds(ds, tieu_de):
        print("-" * 100)
        print(f"{tieu_de}: {len(ds)} nhom")
        print("-" * 100)
        if not ds:
            print("  (khong co)")
            return
        for a in ds:
            print(f"\n  ID      : {a.get('id')}")
            print(f"  Trang thai: {a.get('effective_status')}")
            print(f"  Ten hien tai: {a.get('name')}")
            print(f"  >>> THIEU NAM — can la 'X<thang>-<nam>'")

    in_ds(sai_dang_chay, "🔴 NHOM DANG CHAY CO TEN SAI (can sua ngay)")
    print()
    in_ds(sai_da_tat, "⚪ NHOM DA TAT CO TEN SAI (khong anh huong chi tieu)")

    print("\n" + "=" * 100)
    if sai_dang_chay:
        print("CACH SUA: nhung nhom DANG CHAY se tu duoc sua ten o lan tat ke tiep")
        print("(regex cat hau to cu da cat duoc 'X10' nen KHONG bi chong ten).")
        print("Muon sua ngay: tat nhom do qua agent, hoac doi ten tay tren Meta.")
    else:
        print("Khong co nhom DANG CHAY nao bi sai ten.")
    print("=" * 100)
    print("XONG. Khong co lenh nao duoc gui len Meta.")


if __name__ == "__main__":
    main()
