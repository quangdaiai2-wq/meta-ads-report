"""
SINH BAO CAO HTML TU SO LIEU META ADS
======================================
Tao file dashboard.html — mo bang trinh duyet la xem duoc.
So lieu duoc ghi san vao file, khong can server, khong can internet.

Giao dien lam lai ngay 29/09/2026 theo yeu cau cua Dai:
  - Kieu khac han ban cu: nen TOI lam mac dinh, co nut doi sang nen sang.
  - Phan NHAN DINH do AI viet nay nam TRONG FILE NAY (truoc day nam trong tin
    nhan Telegram). Tin nhan Telegram chi con tieu de + TOM TAT.
  - Hai bang xep hang camp va khung bo loc cung nam o day.

Vi sao tach CSS ra thanh chuoi rieng (khong nhet vao f-string): CSS co rat nhieu
dau ngoac nho. Nhet vao f-string thi moi dau ngoac phai viet doi ({{ }}) — vua
kho doc vua de sai. De rieng mot chuoi thuong roi ghep vao thi khong phai doi.
"""
from datetime import datetime
from html import escape
from pathlib import Path


def money(v):
    return f"{int(round(float(v))):,}".replace(",", ".")


def esc(s):
    return escape(str(s or ""))


def cpr_class(cpr, avg_cpr):
    """Tra ve class mau theo CPR so voi trung binh."""
    if cpr is None:
        return "bad"
    if avg_cpr and cpr <= avg_cpr * 0.8:
        return "good"
    if avg_cpr and cpr >= avg_cpr * 1.2:
        return "bad"
    return "mid"


def doan_van(text):
    """Chu do AI viet -> cac doan HTML.

    AI viet tin nhan Telegram nen xuong dong la ranh gioi doan. Phai ESCAPE:
    chu do AI sinh ra thi khong duoc tin tuyet doi.
    """
    if not text:
        return ""
    return "".join(
        f"<p>{esc(p)}</p>"
        for p in str(text).splitlines() if p.strip()
    )


def the_so(nhan, gia_tri):
    """Mot o so lieu nho trong luoi chi so phu."""
    return (
        f'<div class="stat">'
        f'<div class="stat-label">{esc(nhan)}</div>'
        f'<div class="stat-value">{esc(gia_tri)}</div>'
        f"</div>"
    )


def campaign_rows(items, show_cpr=True):
    if not items:
        return '<tr><td colspan="5" class="empty">Không có dữ liệu</td></tr>'

    avg = None
    if show_cpr:
        vals = [i["cpr"] for i in items if i["cpr"]]
        if vals:
            avg = sum(vals) / len(vals)

    out = []
    for it in items:
        cpr_txt = money(it["cpr"]) if it["cpr"] else "—"
        cls = cpr_class(it["cpr"], avg) if show_cpr else ""
        out.append(f"""
          <tr>
            <td class="rank">{it['rank']}</td>
            <td class="cid">{esc(it['id'])}</td>
            <td class="cname" title="{esc(it['name'])}">{esc(it['name']) or '—'}</td>
            <td class="num">{money(it['spend'])}</td>
            <td class="num {cls}">{cpr_txt}</td>
          </tr>""")
    return "".join(out)


# --- Bang mau. Hai bo, doi qua lai bang nut tren goc phai. ---
_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }

:root, html[data-theme="dark"] {
  --bg: #0a0d13;
  --bg-soft: #111722;
  --panel: #151c28;
  --panel-2: #1b2432;
  --border: #26313f;
  --text: #e9edf4;
  --muted: #8794a8;
  --faint: #5d6a7d;
  --spend: #f5b544;
  --purchase: #4ade80;
  --cpr: #60a5fa;
  --good: #4ade80;
  --mid: #fbbf24;
  --bad: #f87171;
  --shadow: 0 1px 2px rgba(0,0,0,.4);
}
html[data-theme="light"] {
  --bg: #f4f6f9;
  --bg-soft: #eaeef4;
  --panel: #ffffff;
  --panel-2: #f7f9fc;
  --border: #dfe5ee;
  --text: #17202e;
  --muted: #5f6b7d;
  --faint: #97a1b0;
  --spend: #b45309;
  --purchase: #15803d;
  --cpr: #1d4ed8;
  --good: #15803d;
  --mid: #a16207;
  --bad: #b91c1c;
  --shadow: 0 1px 2px rgba(16,24,40,.06);
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
               "Helvetica Neue", Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  padding: 20px 16px 40px;
  -webkit-font-smoothing: antialiased;
}
.wrap { max-width: 1080px; margin: 0 auto; }

/* --- Thanh tren: thuong hieu + nut doi mau --- */
.topbar {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px; margin-bottom: 18px;
}
.brand {
  font-size: 11px; letter-spacing: .14em; text-transform: uppercase;
  color: var(--faint); font-weight: 600;
}
.toggle {
  background: var(--panel); border: 1px solid var(--border); color: var(--muted);
  border-radius: 999px; padding: 6px 14px; font-size: 12px; cursor: pointer;
  font-family: inherit;
}
.toggle:hover { color: var(--text); border-color: var(--muted); }

/* --- Khoi tieu de --- */
.hero {
  background: linear-gradient(160deg, var(--panel-2), var(--panel));
  border: 1px solid var(--border); border-radius: 18px;
  padding: 24px 26px; margin-bottom: 16px; box-shadow: var(--shadow);
}
.hero h1 { font-size: 25px; font-weight: 650; letter-spacing: -.01em; }
.hero-sub { color: var(--muted); font-size: 14px; margin-top: 8px; }
.chip {
  display: inline-block; background: var(--bg-soft); border: 1px solid var(--border);
  color: var(--muted); border-radius: 999px; padding: 3px 11px; font-size: 12px;
  margin-right: 6px; margin-top: 8px;
}

/* --- Ba so lon nhat --- */
.hero-grid {
  display: grid; grid-template-columns: 1.6fr 1fr 1fr; gap: 12px;
  margin-bottom: 16px;
}
.big {
  background: var(--panel); border: 1px solid var(--border); border-radius: 16px;
  padding: 18px 20px; box-shadow: var(--shadow);
}
.big-label {
  font-size: 11px; letter-spacing: .08em; text-transform: uppercase;
  color: var(--muted); font-weight: 600; margin-bottom: 8px;
}
.big-value {
  font-size: 34px; font-weight: 680; letter-spacing: -.02em; line-height: 1.15;
  font-variant-numeric: tabular-nums;
}
.big-value.small { font-size: 26px; }
.big-unit { font-size: 14px; font-weight: 500; color: var(--muted); margin-left: 6px; }
.big.spend .big-value { color: var(--spend); }
.big.purchase .big-value { color: var(--purchase); }
.big.cpr .big-value { color: var(--cpr); }

/* --- Khoi nhan dinh do AI viet --- */
.analysis {
  background: var(--panel); border: 1px solid var(--border);
  border-left: 3px solid var(--cpr); border-radius: 14px;
  padding: 20px 24px; margin-bottom: 16px; box-shadow: var(--shadow);
}
.analysis-label {
  font-size: 11px; letter-spacing: .12em; text-transform: uppercase;
  color: var(--cpr); font-weight: 700; margin-bottom: 10px;
}
.analysis p { font-size: 15.5px; margin-bottom: 9px; }
.analysis p:last-child { margin-bottom: 0; }
.analysis.warn { border-left-color: var(--mid); }
.analysis.warn .analysis-label { color: var(--mid); }
.analysis.warn p { font-size: 14px; color: var(--muted); }

/* --- Luoi chi so phu --- */
.stats {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px; margin-bottom: 26px;
}
.stat {
  background: var(--panel); border: 1px solid var(--border); border-radius: 12px;
  padding: 14px 16px; box-shadow: var(--shadow);
}
.stat-label { font-size: 12px; color: var(--muted); margin-bottom: 5px; }
.stat-value {
  font-size: 21px; font-weight: 620; font-variant-numeric: tabular-nums;
}

/* --- Bang --- */
section { margin-bottom: 26px; }
h2 {
  font-size: 15px; font-weight: 620; margin-bottom: 4px;
  display: flex; align-items: center; gap: 9px;
}
.dot { width: 9px; height: 9px; border-radius: 50%; flex: none; }
.dot-good { background: var(--good); }
.dot-bad { background: var(--bad); }
.note { font-size: 12px; color: var(--faint); margin-bottom: 11px; }

.table-wrap {
  background: var(--panel); border: 1px solid var(--border);
  border-radius: 14px; box-shadow: var(--shadow); overflow-x: auto;
}
table { width: 100%; border-collapse: collapse; font-size: 13px; min-width: 620px; }
thead { background: var(--panel-2); }
th {
  text-align: left; padding: 12px 16px; font-weight: 600; font-size: 11px;
  color: var(--muted); text-transform: uppercase; letter-spacing: .06em;
  border-bottom: 1px solid var(--border); white-space: nowrap;
}
th.num, td.num { text-align: right; }
td { padding: 12px 16px; border-bottom: 1px solid var(--border); }
tbody tr:last-child td { border-bottom: none; }
tbody tr:hover { background: var(--panel-2); }
.rank {
  color: var(--faint); font-weight: 600; width: 44px;
  font-variant-numeric: tabular-nums;
}
.cid {
  font-family: ui-monospace, "SF Mono", Consolas, monospace;
  font-size: 12px; color: var(--muted);
}
.cname {
  color: var(--muted); font-size: 12px; max-width: 320px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
td.num { font-variant-numeric: tabular-nums; }
.good { color: var(--good); font-weight: 620; }
.mid { color: var(--mid); }
.bad { color: var(--bad); font-weight: 620; }
.empty { text-align: center; color: var(--faint); padding: 26px; }

/* --- Chan trang --- */
footer {
  margin-top: 34px; padding-top: 18px; border-top: 1px solid var(--border);
  font-size: 12px; color: var(--faint); line-height: 1.9;
}
footer .frow { display: flex; gap: 8px; flex-wrap: wrap; }
footer .flabel { min-width: 128px; color: var(--faint); }
footer code {
  background: var(--bg-soft); border: 1px solid var(--border);
  padding: 1px 7px; border-radius: 5px;
  font-family: ui-monospace, "SF Mono", Consolas, monospace; font-size: 11.5px;
  color: var(--muted);
}

@media (max-width: 640px) {
  body { padding: 14px 11px 30px; }
  .hero { padding: 18px; border-radius: 15px; }
  .hero h1 { font-size: 20px; }
  .hero-grid { grid-template-columns: 1fr 1fr; }
  .hero-grid .big:first-child { grid-column: 1 / -1; }
  .big-value { font-size: 28px; }
  .big-value.small { font-size: 22px; }
  .analysis { padding: 16px 17px; }
  .analysis p { font-size: 14.5px; }
  td, th { padding: 10px 12px; }
  footer .flabel { min-width: 100%; }
}
"""

# Nut doi sang/toi. Nho lua chon bang localStorage de lan sau mo lai khong phai bam lai.
_JS = """
(function () {
  var goc = document.documentElement;
  var nut = document.getElementById('doi-mau');
  function dat(t) {
    goc.setAttribute('data-theme', t);
    if (nut) { nut.textContent = (t === 'light') ? '\\u{1F319} N\\u1ec1n t\\u1ed1i' : '\\u2600\\uFE0F N\\u1ec1n s\\u00e1ng'; }
  }
  var luu = null;
  try { luu = localStorage.getItem('mau-bao-cao'); } catch (e) { luu = null; }
  dat(luu === 'light' ? 'light' : 'dark');
  if (nut) {
    nut.addEventListener('click', function () {
      var moi = goc.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
      dat(moi);
      try { localStorage.setItem('mau-bao-cao', moi); } catch (e) {}
    });
  }
})();
"""


def build_html(stats, since, until, period_text, nhan_dinh=None, loi_ai=None):
    """Tao noi dung bao cao HTML.

    nhan_dinh: chu do AI viet (main() goi AI roi truyen vao). Nam trong file nay
               vi tu 29/09/2026 tin nhan Telegram chi con phan TOM TAT.
    loi_ai:    ly do AI khong viet duoc. Hien mot khoi ghi chu thay cho phan
               nhan dinh, de nguoi doc biet vi sao thieu.
    """
    t = stats["totals"]
    good = stats["good"]
    bad = stats["bad"]

    cpr_total = (t["spend"] / t["purchase"]) if t["purchase"] > 0 else None
    cpr_txt = money(cpr_total) if cpr_total else "—"
    cpr_dv = "VND" if cpr_total else ""

    # --- Khoi nhan dinh ---
    if nhan_dinh:
        phan_nhan_dinh = (
            '<div class="analysis">'
            '<div class="analysis-label">Nhận định</div>'
            + doan_van(nhan_dinh)
            + "</div>"
        )
    elif loi_ai:
        phan_nhan_dinh = (
            '<div class="analysis warn">'
            '<div class="analysis-label">Nhận định</div>'
            f"<p>Phần nhận định do AI viết tạm không có (lý do: {esc(loi_ai)}).</p>"
            "<p>Số liệu trong báo cáo này vẫn đầy đủ — báo cáo không bị ảnh hưởng.</p>"
            "</div>"
        )
    else:
        phan_nhan_dinh = ""

    chi_so_phu = "".join([
        the_so("Bắt đầu trò chuyện", f"{t['msg']}"),
        the_so("Người liên hệ mới", f"{t['contact']}"),
        the_so("Đơn đặt hàng", f"{t['order']}"),
        the_so("Lượt thanh toán", f"{t['payment']}"),
        the_so("Bình luận", f"{t['comment']}"),
    ])

    generated = datetime.now().strftime("%d/%m/%Y %H:%M")

    return f"""<!DOCTYPE html>
<html lang="vi" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Báo cáo Meta Ads — {esc(period_text)}</title>
<style>{_CSS}</style>
</head>
<body>
<div class="wrap">

  <div class="topbar">
    <div class="brand">Báo cáo quảng cáo</div>
    <button class="toggle" id="doi-mau" type="button">&#127769; Nền tối</button>
  </div>

  <div class="hero">
    <h1>Báo cáo Meta Ads</h1>
    <div class="hero-sub">{esc(stats['account_name'])}</div>
    <div>
      <span class="chip">{esc(period_text)}</span>
      <span class="chip">{stats['total_campaigns']} campaign đủ điều kiện</span>
    </div>
  </div>

  <div class="hero-grid">
    <div class="big spend">
      <div class="big-label">Số tiền đã chi tiêu</div>
      <div class="big-value">{money(t['spend'])}<span class="big-unit">VND</span></div>
    </div>
    <div class="big purchase">
      <div class="big-label">Lượt mua</div>
      <div class="big-value small">{t['purchase']}</div>
    </div>
    <div class="big cpr">
      <div class="big-label">Chi phí mỗi đơn</div>
      <div class="big-value small">{cpr_txt}<span class="big-unit">{cpr_dv}</span></div>
    </div>
  </div>

  {phan_nhan_dinh}

  <div class="stats">{chi_so_phu}</div>

  <section>
    <h2><span class="dot dot-good"></span>Camp hiệu quả — top {len(good)}</h2>
    <div class="note">Xếp theo chi phí mỗi đơn, rẻ nhất trước — không phải theo số đơn.
      Camp chỉ có 1 đơn được xếp xuống sau những camp đã có từ 2 đơn trở lên.</div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>ID chiến dịch</th>
            <th>Tên chiến dịch</th>
            <th class="num">Chi tiêu (VND)</th>
            <th class="num">Chi phí / đơn</th>
          </tr>
        </thead>
        <tbody>{campaign_rows(good)}
        </tbody>
      </table>
    </div>
  </section>

  <section>
    <h2><span class="dot dot-bad"></span>Camp kém hiệu quả — top {len(bad)}</h2>
    <div class="note">Ưu tiên camp đã chi tiền mà không ra đơn nào (chi nhiều nhất trước).
      Một camp chỉ nằm ở MỘT trong hai bảng — nên bảng này có thể ngắn hoặc trống.</div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>ID chiến dịch</th>
            <th>Tên chiến dịch</th>
            <th class="num">Chi tiêu (VND)</th>
            <th class="num">Chi phí / đơn</th>
          </tr>
        </thead>
        <tbody>{campaign_rows(bad)}
        </tbody>
      </table>
    </div>
  </section>

  <footer>
    <div class="frow"><span class="flabel">Tên chứa</span><code>{esc(stats['include_kw'])}</code></div>
    <div class="frow"><span class="flabel">Loại trừ</span><code>{esc(stats['exclude_kw'])}</code></div>
    <div class="frow"><span class="flabel">Điều kiện</span><code>chi tiêu &gt; 0</code></div>
    <div style="margin-top:10px">
      Tạo tự động lúc {generated} · Chi phí / đơn = chi tiêu ÷ lượt mua
      (— nghĩa là chưa có lượt mua)
    </div>
  </footer>

</div>
<script>{_JS}</script>
</body>
</html>"""


def save_dashboard(stats, since, until, period_text, nhan_dinh=None, loi_ai=None,
                   out_path=None):
    """Ghi file bao cao HTML."""
    if out_path is None:
        out_path = Path(__file__).parent / "dashboard.html"
    html = build_html(stats, since, until, period_text, nhan_dinh, loi_ai)
    Path(out_path).write_text(html, encoding="utf-8")
    return out_path
