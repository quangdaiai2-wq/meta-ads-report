# -*- coding: utf-8 -*-
"""Kiem chung: giu khoa bang MOT tien trinh gia de chan agent khoi dong lai.

Y tuong: agent goi `agent_ky_uc.giu_khoa(nhip)` luc khoi dong. Neu khoa con
"song" (PID trong khoa van song, hoac moi cap nhat trong 2*nhip phut) thi agent
TU CHOI khoi dong. Vay chi can mot tien trinh nho giu khoa -> lich 5 phut co
chay cung khong the khoi dong agent.

Cach nay KHONG xoa lich nen khong dung vao quyen Admin, va GO RA rat de.
"""
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

GIO_VN = timezone(timedelta(hours=7))
GOC = Path(r"D:\Buddy Work AI\2026-09-14-07-50-57")
KHOA = GOC / "logs" / "agent-dang-chay.lock"
CO_TAM_NGAT = GOC / "logs" / "TAM-NGAT-AGENT.txt"

# Cap nhat khoa moi 60 giay. Nguong "con song" = max(10, nhip*2) phut, nhip=15
# => 30 phut. Cap nhat moi 60 giay thi du an toan.
CHU_KY_GIU = 60


def _doc_ly_do():
    try:
        return CO_TAM_NGAT.read_text(encoding="utf-8").strip()
    except OSError:
        return "(khong co file ly do)"


def main():
    if not CO_TAM_NGAT.exists():
        print("KHONG co file tam ngat — thoat de khong giu khoa vo co.")
        return 2
    print("GIU KHOA de chan agent khoi dong lai.")
    print("Ly do:", _doc_ly_do())
    print("Khoa:", KHOA)
    print("Thoat: xoa file", CO_TAM_NGAT.name, "roi dung tien trinh nay.")
    while True:
        if not CO_TAM_NGAT.exists():
            print("Da xoa file tam ngat — nha khoa va thoat.")
            try:
                KHOA.unlink()
            except OSError:
                pass
            return 0
        noi_dung = datetime.now(GIO_VN).isoformat(timespec="seconds")
        try:
            KHOA.write_text(f"{noi_dung}\n{os.getpid()}\n", encoding="utf-8")
        except OSError as e:
            print("LOI ghi khoa:", e)
            return 1
        time.sleep(CHU_KY_GIU)


if __name__ == "__main__":
    sys.exit(main())
