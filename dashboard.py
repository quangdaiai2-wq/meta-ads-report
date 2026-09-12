"""
SINH DASHBOARD HTML TU SO LIEU META ADS
========================================
Tao file dashboard.html — mo bang trinh duyet la xem duoc.
So lieu duoc ghi san vao file, khong can server.
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


def card(label, value, unit="", tone="neutral"):
    return f"""
      <div class="card {tone}">
        <div class="card-label">{esc(label)}</div>
        <div class="card-value">{esc(value)}<span class="card-unit">{esc(unit)}</span></div>
      </div>"""


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


def build_html(stats, since, until, period_text):
    """Tao noi dung HTML dashboard."""
    t = stats["totals"]
    good = stats["good"]
    bad = stats["bad"]

    cpr_total = (t["spend"] / t["purchase"]) if t["purchase"] > 0 else None
    cpr_txt = money(cpr_total) if cpr_total else "—"

    cards = (
        card("Số tiền đã chi tiêu", money(t["spend"]), " VND", "spend")
        + card("Lượt mua", f"{t['purchase']}", "", "purchase")
        + card("CPR (chi phí / lượt mua)", cpr_txt, " VND" if cpr_total else "", "cpr")
        + card("Lượt thanh toán", f"{t['payment']}")
        + card("Bắt đầu trò chuyện", f"{t['msg']}")
        + card("Người liên hệ mới", f"{t['contact']}")
        + card("Đơn đặt hàng", f"{t['order']}")
        + card("Bình luận", f"{t['comment']}")
    )

    generated = datetime.now().strftime("%d/%m/%Y %H:%M")

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Báo cáo Meta Ads — {esc(period_text)}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #f5f5f3;
    color: #2c2c2a;
    line-height: 1.6;
    padding: 32px 24px;
  }}
  .wrap {{ max-width: 1100px; margin: 0 auto; }}

  header {{ margin-bottom: 28px; }}
  h1 {{ font-size: 22px; font-weight: 500; margin-bottom: 6px; }}
  .meta {{ font-size: 13px; color: #888780; }}
  .meta strong {{ color: #5f5e5a; font-weight: 500; }}

  .filters {{
    background: #fff; border: 1px solid #e5e4de; border-radius: 12px;
    padding: 16px 20px; margin-bottom: 28px; font-size: 13px;
  }}
  .filters-title {{
    font-size: 12px; font-weight: 500; color: #888780;
    text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 10px;
  }}
  .filter-row {{ display: flex; gap: 8px; margin-bottom: 4px; }}
  .filter-row span:first-child {{ color: #888780; min-width: 150px; }}
  code {{
    background: #f1efe8; padding: 1px 6px; border-radius: 4px;
    font-family: ui-monospace, "SF Mono", Consolas, monospace; font-size: 12px;
  }}

  .cards {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px; margin-bottom: 32px;
  }}
  .card {{
    background: #fff; border: 1px solid #e5e4de; border-radius: 12px;
    padding: 16px 18px;
  }}
  .card.spend {{ background: #fcebeb; border-color: #f7c1c1; }}
  .card.purchase {{ background: #eaf3de; border-color: #c0dd97; }}
  .card.cpr {{ background: #faeeda; border-color: #fac775; }}
  .card-label {{ font-size: 12px; color: #888780; margin-bottom: 6px; }}
  .card.spend .card-label {{ color: #a32d2d; }}
  .card.purchase .card-label {{ color: #3b6d11; }}
  .card.cpr .card-label {{ color: #854f0b; }}
  .card-value {{ font-size: 24px; font-weight: 500; }}
  .card.spend .card-value {{ color: #791f1f; }}
  .card.purchase .card-value {{ color: #27500a; }}
  .card.cpr .card-value {{ color: #633806; }}
  .card-unit {{ font-size: 13px; font-weight: 400; color: #888780; }}

  section {{ margin-bottom: 32px; }}
  h2 {{
    font-size: 15px; font-weight: 500; margin-bottom: 12px;
    display: flex; align-items: center; gap: 8px;
  }}
  .dot {{ width: 8px; height: 8px; border-radius: 50%; display: inline-block; }}
  .dot-green {{ background: #639922; }}
  .dot-red {{ background: #e24b4a; }}

  .table-wrap {{
    background: #fff; border: 1px solid #e5e4de; border-radius: 12px;
    overflow: hidden;
  }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  thead {{ background: #fafaf8; }}
  th {{
    text-align: left; padding: 11px 16px; font-weight: 500;
    font-size: 12px; color: #888780; border-bottom: 1px solid #e5e4de;
  }}
  th.num, td.num {{ text-align: right; }}
  td {{ padding: 11px 16px; border-bottom: 1px solid #f1efe8; }}
  tbody tr:last-child td {{ border-bottom: none; }}
  tbody tr:hover {{ background: #fafaf8; }}
  .rank {{
    color: #b4b2a9; font-weight: 500; width: 40px;
    font-variant-numeric: tabular-nums;
  }}
  .cid {{
    font-family: ui-monospace, "SF Mono", Consolas, monospace;
    font-size: 12px; color: #5f5e5a;
  }}
  .cname {{
    color: #888780; font-size: 12px; max-width: 340px;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }}
  td.num {{ font-variant-numeric: tabular-nums; }}
  .good {{ color: #3b6d11; font-weight: 500; }}
  .mid {{ color: #854f0b; }}
  .bad {{ color: #a32d2d; font-weight: 500; }}
  .empty {{ text-align: center; color: #b4b2a9; padding: 24px; }}

  footer {{
    margin-top: 40px; padding-top: 16px; border-top: 1px solid #e5e4de;
    font-size: 12px; color: #b4b2a9; text-align: center;
  }}
</style>
</head>
<body>
<div class="wrap">

  <header>
    <h1>Báo cáo Meta Ads</h1>
    <div class="meta">
      <strong>{esc(stats['account_name'])}</strong> ·
      {esc(period_text)} ·
      {stats['total_campaigns']} campaign đủ điều kiện
    </div>
  </header>

  <div class="filters">
    <div class="filters-title">Bộ lọc áp dụng</div>
    <div class="filter-row"><span>Tên chứa</span><code>{esc(stats['include_kw'])}</code></div>
    <div class="filter-row"><span>Loại trừ</span><code>{esc(stats['exclude_kw'])}</code></div>
    <div class="filter-row"><span>Điều kiện</span><code>chi tiêu &gt; 0</code></div>
  </div>

  <div class="cards">{cards}
  </div>

  <section>
    <h2><span class="dot dot-green"></span>Camp hiệu quả — top {len(good)}</h2>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>ID chiến dịch</th>
            <th>Tên chiến dịch</th>
            <th class="num">Chi tiêu (VND)</th>
            <th class="num">CPR (VND)</th>
          </tr>
        </thead>
        <tbody>{campaign_rows(good)}
        </tbody>
      </table>
    </div>
  </section>

  <section>
    <h2><span class="dot dot-red"></span>Camp kém hiệu quả — top {len(bad)}</h2>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>ID chiến dịch</th>
            <th>Tên chiến dịch</th>
            <th class="num">Chi tiêu (VND)</th>
            <th class="num">CPR (VND)</th>
          </tr>
        </thead>
        <tbody>{campaign_rows(bad)}
        </tbody>
      </table>
    </div>
  </section>

  <footer>
    Tạo tự động lúc {generated} · CPR = chi phí / lượt mua (— nghĩa là chưa có lượt mua)
  </footer>

</div>
</body>
</html>"""


def save_dashboard(stats, since, until, period_text, out_path=None):
    """Ghi file dashboard.html."""
    if out_path is None:
        out_path = Path(__file__).parent / "dashboard.html"
    html = build_html(stats, since, until, period_text)
    Path(out_path).write_text(html, encoding="utf-8")
    return out_path
