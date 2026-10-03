"""CONG TAC TAM NGAT — chan agent khoi dong bang MOT FILE, khong can tien trinh nao.

Vi sao can module nay (03/10/2026):

Cach chan cu la mot tien trinh nho giu khoa `logs/agent-dang-chay.lock`. Cach do
CO LO HONG CHET NGUOI: tien trinh giu khoa chet khi may tat / dang xuat. May bat
lai (hoac Windows tu chay lai lich -AtLogOn) thi lich AgentNac2 chay, khong con ai
giu khoa, agent TU KHOI DONG LAI nhu chua he bi tam ngat. Dai phat hien ra:

    "Nhu nay neu toi tat may nay va t2 quay tro lai cong ty no tu bat lai thi con
     noi chuyen gi nua?"

Cach moi KHONG phu thuoc tien trinh nao:

  - Cong tac la SU TON TAI cua file `logs/TAM-NGAT-AGENT.txt`.
  - Khong co gi phai chay nen khong co gi chet theo.
  - Tat may, dang xuat, khoi dong lai Windows - file van con nguyen tren dia.
  - Lich AgentNac2 co chay thi cung doc phai cong tac va TU CHOI ngay.

Cong tac nam o `logs/TAM-NGAT-AGENT.txt`. File nay KHONG duoc ghi boi bat ky
tien trinh nao khac (logs/ duoc .gitignore bo qua nen khong len GitHub).
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

GIO_VN = timezone(timedelta(hours=7))
GOC = Path(__file__).parent
CONG_TAC = GOC / "logs" / "TAM-NGAT-AGENT.txt"


def dang_tam_ngat(duong_dan=None):
    """True neu cong tac tam ngat dang BAT (file con ton tai).

    Chi kiem su ton tai cua file. KHONG doc noi dung, KHONG kiem han dung.
    Ly do: noi dung file chi de NGUOI doc; may chi can biet co/khong. Nho vay
    khong the co chuyen "file hong dinh dang nen tuong la chua tam ngat".
    """
    p = Path(duong_dan) if duong_dan else CONG_TAC
    try:
        return p.is_file()
    except OSError:
        # Doc khong duoc (quyen, dia loi) => coi nhu DANG tam ngat.
        # Tha chan nham con hon de agent tac dong Meta ngoai y muon.
        return True


def ly_do(duong_dan=None):
    """Doc phan dau file cong tac de bao cho nguoi dung biet vi sao bi chan.

    Tra ve chuoi rong neu khong doc duoc (khong nem loi).
    """
    p = Path(duong_dan) if duong_dan else CONG_TAC
    try:
        tho = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    # Lay 3 dong dau, du de biet ai dat va den khi nao.
    dong = [d.strip() for d in tho.splitlines() if d.strip()][:3]
    return " | ".join(dong)


def thong_diep_chan(duong_dan=None):
    """Cau thong bao day du de ghi vao nhat ky / in ra man hinh."""
    p = Path(duong_dan) if duong_dan else CONG_TAC
    ra = f"CONG TAC TAM NGAT dang BAT ({p}) — agent khong duoc chay"
    tom_tat = ly_do(duong_dan)
    if tom_tat:
        ra += f" — {tom_tat}"
    ra += f" — muon bat lai: xoa file {p}"
    return ra


def bat_tam_ngat(noi_dung, duong_dan=None):
    """Bat cong tac tam ngat. Tra ve (thanh_cong: bool, ly_do: str).

    `noi_dung` la phan chu giai thich cho NGUOI doc (ai dat, den khi nao,
    cach mo lai). Luon tu them moc thoi gian o dau neu chua co.
    """
    p = Path(duong_dan) if duong_dan else CONG_TAC
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        return False, f"khong tao duoc thu muc {p.parent}: {e}"
    try:
        dau = datetime.now(GIO_VN).strftime("%d/%m/%Y %H:%M")
        p.write_text(f"TAM NGAT AGENT — bat luc {dau}\n\n{noi_dung}",
                     encoding="utf-8")
        return True, f"da bat cong tac tam ngat: {p}"
    except OSError as e:
        return False, f"khong ghi duoc file cong tac {p}: {e}"


def tat_tam_ngat(duong_dan=None):
    """Tat cong tac tam ngat (xoa file). Tra ve (thanh_cong: bool, ly_do: str)."""
    p = Path(duong_dan) if duong_dan else CONG_TAC
    try:
        p.unlink()
        return True, f"da tat cong tac tam ngat (xoa {p})"
    except FileNotFoundError:
        return True, "cong tac von da tat (file khong ton tai)"
    except OSError as e:
        return False, f"khong xoa duoc file cong tac {p}: {e}"
