"""Doc so tu Meta o CAP NHOM QUANG CAO.

Vi sao khong dung logs/lich-su.json: file do chi co cap chien dich. Ngan sach va
nguong cua Dai nam o cap nhom.

Gioi han da cham that: tai khoan co HON 3.000 nhom. Doc het roi moi loc la cham,
nen phai dung tham so `filtering` de chi lay nhom dang ACTIVE.

CHI DOC. Khong gui lenh nao len Meta o file nay.
"""
import json
import urllib.parse

import report

ACC_MAC_DINH = ""


def _acc(env):
    return ((env or {}).get("META_AD_ACCOUNT_ID", "") or ACC_MAC_DINH).strip()


def _doc_het(env, path, params):
    """Doc het co phan trang. Tra ve danh sach (rong neu loi).

    LOI THAT da gap (30/09/2026): ban dau ham nay ghep san chuoi truy van roi
    goi report.api_get(f"{path}?{...}", {}). Nhung api_get LAI tu them "?" vao
    cuoi => URL thanh "...&access_token=TOKEN?" => Meta bao
    "Malformed access token ...FO?" va agent doc ve 0 nhom.
    Phai de api_get tu ghep: truyen path va params RIENG.
    """
    tok = (env or {}).get("META_ADS_ACCESS_TOKEN", "").strip()
    if not tok:
        report.log("AGENT: thieu META_ADS_ACCESS_TOKEN trong .env")
        return []
    p = dict(params)
    p["access_token"] = tok
    ra = []
    d, loi = report.api_get(path, p)
    if loi:
        report.log(f"AGENT: loi doc Meta: {loi.get('message') if isinstance(loi, dict) else loi}")
        return ra
    ra.extend(d.get("data", []))
    url = (d.get("paging") or {}).get("next")
    while url and len(ra) <= 5000:
        d, loi = _goi_url(url)
        if loi:
            report.log(f"AGENT: loi khi doc tiep trang: "
                       f"{loi.get('message') if isinstance(loi, dict) else loi}")
            break
        ra.extend(d.get("data", []))
        url = (d.get("paging") or {}).get("next")
    return ra


def _goi_url(url):
    """Goi thang mot URL do Meta tra ve (da kem access_token)."""
    import urllib.error
    import urllib.request
    for _ in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8")), None
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="ignore")
            try:
                return None, json.loads(raw).get("error", {"message": f"HTTP {e.code}"})
            except ValueError:
                return None, {"message": f"HTTP {e.code}"}
        except Exception as e:
            return None, {"message": str(e)}
    return None, {"message": "Khong the ket noi"}


def doc_nhom_dang_chay(env):
    """Danh sach nhom co effective_status = ACTIVE. Loc ngay tu phia Meta."""
    acc = _acc(env)
    if not acc:
        return []
    loc = json.dumps([{"field": "effective_status", "operator": "IN",
                       "value": ["ACTIVE"]}])
    return _doc_het(env, f"{acc}/adsets", {
        "fields": "id,name,effective_status,daily_budget,campaign_id",
        "filtering": loc,
        "limit": 200,
    })


def doc_chi_tieu(env, date_preset):
    """Chi tieu cap nhom theo mot moc thoi gian ('today' hoac 'this_month')."""
    acc = _acc(env)
    if not acc:
        return {}
    rows = _doc_het(env, f"{acc}/insights", {
        "date_preset": date_preset,
        "level": "adset",
        "fields": "adset_id,adset_name,spend,actions",
        "limit": 200,
    })
    return {str(r.get("adset_id")): r for r in rows if r.get("adset_id")}


def doc_so(env):
    """Tra ve (nhom_dang_chay, chi_tieu_hom_nay, chi_tieu_thang)."""
    nhom = doc_nhom_dang_chay(env)
    hom_nay = doc_chi_tieu(env, "today")
    thang = doc_chi_tieu(env, "this_month")
    return nhom, hom_nay, thang
