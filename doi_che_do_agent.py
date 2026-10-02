"""Doi che do chay cua agent trong file .env — TAP SU <-> LAM THAT.

CACH DUNG (khong can mo cua so lenh):
    Bam dup chuot vao  doi-che-do-agent.bat

CACH DUNG BANG LENH:
    python doi_che_do_agent.py              -> chi XEM dang o che do nao
    python doi_che_do_agent.py chay-that    -> doi sang LAM THAT
    python doi_che_do_agent.py tap-su       -> doi sang TAP SU

VI SAO PHAI CO FILE NAY:
    File .env KHONG len GitHub. No chua token Telegram, token Meta, chia khoa AI
    nen .gitignore chan lai. Nghia la moi may phai tu sua .env cua chinh no.

    May o nha va may o cong ty co the dang o HAI CHE DO KHAC NHAU. Dieu do dung,
    khong phai loi: `git pull` khong bao gio dong cham toi che do chay.

    Nhung sua tay bang Notepad thi de nham — trong thu muc co bon file ten gan
    giong nhau (.env / .env.example / .env.bak / .env.bak-truoc-*). File nay sua
    DUNG MOT DONG trong dung file .env, va sao luu truoc khi sua.
"""
import shutil
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent
TEP_ENV = GOC / ".env"
TEP_SAO_LUU = GOC / ".env.bak-truoc-doi-che-do"
KHOA = "AGENT_TAP_SU"

GIA_TRI = {"chay-that": "false", "tap-su": "true"}
NHAN = {
    "false": "LAM THAT — agent duoc gui lenh len Meta",
    "true": "TAP SU — agent chi noi, khong gui lenh nao len Meta",
}


def doc_env():
    """Doc .env dang BYTE roi giai ma, de ghi lai khong lam mat thu gi.

    Dung `utf-8` chu KHONG phai `utf-8-sig`: neu file goc co BOM thi BOM duoc
    giu nguyen nhu mot ky tu va ghi lai van con BOM. Dung `-sig` se lam MAT BOM,
    va mot so trinh doc .env co the hieu sai dong dau tien.
    """
    return TEP_ENV.read_bytes().decode("utf-8")


def tim_dong(lines):
    """Tra ve chi so dong `AGENT_TAP_SU=...` THAT, bo qua dong chu thich.

    Trong .env.example va .env deu co dong chu thich bat dau bang `#` nhac ve
    khoa nay (vd: `#  AGENT_TAP_SU: true = agent CHI NOI...`). Neu khong bo qua
    chu thich thi se sua nham vao dong huong dan.
    """
    for i, d in enumerate(lines):
        if d.lstrip().startswith("#"):
            continue
        if d.strip().startswith(KHOA + "="):
            return i
    return -1


def gia_tri(lines, i):
    return lines[i].split("=", 1)[1].strip()


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    if not TEP_ENV.exists():
        print(f"LOI: khong tim thay file .env trong {GOC}")
        print("Cach xu ly: copy file .env.example thanh .env roi bam lai.")
        return 1

    lines = doc_env().splitlines(keepends=True)
    i = tim_dong(lines)
    if i < 0:
        print(f"LOI: khong tim thay dong {KHOA}=... trong file .env")
        print("Cach xu ly: mo .env bang Notepad, them dong nay vao cuoi file:")
        print(f"    {KHOA}=true")
        return 1

    hien_tai = gia_tri(lines, i)
    print(f"Che do hien tai: {KHOA}={hien_tai}")
    print(f"   {NHAN.get(hien_tai, 'gia tri khong nhan ra duoc')}")

    if len(sys.argv) < 2:
        return 0

    lenh = sys.argv[1].strip().lower()
    if lenh not in GIA_TRI:
        print(f"LOI: tham so '{lenh}' khong hop le. Chi nhan: chay-that | tap-su")
        return 1

    moi = GIA_TRI[lenh]
    if moi == hien_tai:
        print("Khong doi gi — dang da o che do nay roi.")
        return 0

    shutil.copy2(TEP_ENV, TEP_SAO_LUU)
    print(f"Da sao luu .env -> {TEP_SAO_LUU.name}")

    # Giu nguyen kieu xuong dong cua chinh dong do (CRLF hay LF), de lan sua sau
    # khong lam file tron hai kieu xuong dong.
    cu = lines[i]
    if cu.endswith("\r\n"):
        ket = "\r\n"
    elif cu.endswith("\n"):
        ket = "\n"
    else:
        ket = ""
    lines[i] = f"{KHOA}={moi}{ket}"

    TEP_ENV.write_bytes("".join(lines).encode("utf-8"))

    print(f"Da doi sang: {KHOA}={moi}")
    print(f"   {NHAN[moi]}")
    print("Agent tu doc lai .env trong vong 15 giay. Khong can khoi dong lai.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
