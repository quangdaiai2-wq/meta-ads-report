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


def doc_chi_tieu_quang_cao(env, date_preset):
    """Chi tieu cap QUANG CAO theo mot moc thoi gian.

    VIEC B (Dai chot 02/10/2026) — xet nguong theo TUNG quang cao.

    DO THAT 02/10/2026 tren act_ — truoc khi viet ham nay:
      - `level=ad` tra ve: ad_id, ad_name, adset_id, adset_name, campaign_id,
        spend, actions  => DU de xet tung quang cao.
      - MOT lenh goi cho CA tai khoan: 46 dong 'today', 55 dong 'this_month',
        KHONG phan trang.
      - `spend` tra dang CHUOI ('29260') — dung bay da ghi trong so.
      - Doi chieu tong: cap ad vs cap adset = 53/53 nhom KHOP, lech 0d
        => xet tung quang cao KHONG lam sai so tien.

    ⚠️ VI SAO KHONG goi /{adset_id}/ads cho tung nhom: tai khoan co >90 nhom dang
    chay => 90 lenh goi. Meta gioi han so lenh goi moi GIAY/PHUT theo tai khoan
    (da bi chan that bang code=17 · subcode 2446079). MOT lenh cho ca tai khoan
    re hon nhieu.

    ⚠️ KHONG co truong trang thai (status/effective_status) o day — insights chi
    tra ve quang cao CO PHA TAT trong ky. Muon biet da tat hay chua phai doc
    rieng tu /{ad_id}.

    ⚠️ Dong THIEU `ad_id` bi bo qua — khong the tat mot quang cao khong co ma.
    ⚠️ Dong thieu `adset_id` VAN GIU (co ad_id la du), nhung se khong gom duoc
    vao nhom nao => `gom_theo_nhom()` ben agent_muc_tieu se bo qua, va do la
    DUNG: khong biet quang cao thuoc nhom nao thi khong kiem duoc pham vi.

    Tra ve {ad_id: dong}.
    """
    acc = _acc(env)
    if not acc:
        return {}
    rows = _doc_het(env, f"{acc}/insights", {
        "date_preset": date_preset,
        "level": "ad",
        "fields": "ad_id,ad_name,adset_id,adset_name,campaign_id,spend,actions",
        "limit": 200,
    })
    return {str(r.get("ad_id")): r for r in rows if r.get("ad_id")}


def doc_so(env):
    """Tra ve (nhom_dang_chay, chi_tieu_hom_nay, chi_tieu_thang,
                chi_tieu_ad_hom_nay, chi_tieu_ad_thang).

    ⚠️ CHU KY DOI 02/10/2026 (Viec B): 3 phan tu -> 5 phan tu.
    Chi co MOT cho goi: `agent.py` trong `_quet_va_de_xuat()`.
    """
    nhom = doc_nhom_dang_chay(env)
    hom_nay = doc_chi_tieu(env, "today")
    thang = doc_chi_tieu(env, "this_month")
    ad_hom_nay = doc_chi_tieu_quang_cao(env, "today")
    ad_thang = doc_chi_tieu_quang_cao(env, "this_month")
    return nhom, hom_nay, thang, ad_hom_nay, ad_thang
