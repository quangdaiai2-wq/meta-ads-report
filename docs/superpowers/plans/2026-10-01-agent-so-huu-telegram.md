# Kế hoạch thi công — Bước 2–4: Agent sở hữu Telegram, người trực chỉ gửi báo cáo

**Ngày:** 01/10/2026 · **Trạng thái:** CHỜ ĐẠI DUYỆT
**Là bước 2–4 của:** `2026-09-30-chuyen-telegram-ve-agent.md`

---

## 1. VÌ SAO — luật Telegram, không phải chuyện thẩm mỹ

`getUpdates` của Telegram **chỉ giao mỗi tin cho MỘT nơi gọi**, và `offset` **xoá vĩnh viễn** mọi
update có mã nhỏ hơn. ⇒ **Chỉ được có MỘT tiến trình đọc tin của một bot.**

Hiện tại **hai** tiến trình cùng đọc ⇒ phải có hàng rào tạm: `nguoi_truc.py` nhận ra lệnh thì
**ghi vào `logs/agent-lenh.json`** cho agent đọc. Hàng rào đó chạy được, nhưng **thừa một mắt xích**
và chính là nguồn của hai lỗi thật đã gặp (mất lệnh khi người trực chết; lệnh bị đọc mất).

⇒ Đích: **agent sở hữu Telegram**, người trực **chỉ gửi báo cáo**.

---

## 2. TRẠNG THÁI SAU KHI XONG (bước 2–4)

```
agent.py  ──►  SỞ HỮU Telegram (getUpdates: message + callback_query)
   │            · tự phát hiện nhóm chạm ngưỡng → gửi tin có 2 nút bấm
   │            · nhận NÚT BẤM + LỆNH GÕ TAY → rào an toàn → ghi lên Meta
   │            · TRẢ LỜI CÂU HỎI của Đại (hỏi đáp chuyển từ người trực sang)
   │            · tự ghi logs/lich-su.json (đã xong ở bước 1)
   └──►  logs/agent-lenh.json KHÔNG CÒN AI GHI (hàng đợi tạm hết việc)

nguoi_truc.py ──► CHỈ canh mốc giờ và gửi báo cáo. KHÔNG đọc tin nữa.
```

⚠️ **Bước 5–6 (tắt báo cáo theo khung giờ, gỡ lịch người trực) KHÔNG làm lần này** — kế hoạch
30/09 mục 4 bắt buộc: **ghi sổ → chạy song song đối chiếu → rồi mới tắt báo cáo**. Bước 1 mới xong
hôm nay, nên chưa đủ thời gian đối chiếu.

---

## 3. THAY ĐỔI CODE

### 3.1. `nguoi_truc.py` — BỎ việc đọc Telegram

| Việc | Chi tiết |
|---|---|
| `NguoiTruc.mot_vong()` | Bỏ dòng gọi `self.nghe_telegram()` |
| Xoá 4 phương thức | `nghe_telegram`, `xu_ly_tin`, `xu_ly_nut_bam`, `doc_va_chuyen_tiep_tin_ton_dong` |
| Xoá thuộc tính | `self.da_xa_tin_ton_dong`, `self.offset` |
| **GIỮ NGUYÊN** | Các hàm thuần về Telegram (`goi_telegram`, `lay_tin_moi`, `offset_moi_tu_ket_qua`, `tin_tu_dai`, `noi_dung_tin`, `gui_tin_nhan`, `tra_loi_nut_bam`, `sua_tin_nhan`, `tin_tu_dai_nut_bam`, `du_lieu_nut_bam`, `ma_tin_nhan_nut_bam`, `ma_lan_bam`, `tra_loi_tin_nhan`) — **agent dùng lại, KHÔNG viết lại** |

### 3.2. `nguoi_truc.tra_loi_tin_nhan` — thêm tham số `nhan`

Câu trả lời sức khỏe hiện mở đầu bằng *"✅ Người trực đang chạy."*. Nay người trả lời là **agent**,
nên thêm tham số `nhan="Người trực"` (giữ nguyên mặc định ⇒ **mọi bài kiểm thử cũ vẫn đạt**).
Agent truyền `nhan="Agent (nấc 2)"`.

### 3.3. `agent.py` — NHẬN Telegram

Thêm **trạng thái** trong `main()`:

```python
    tt_tg = {"offset": None, "da_doc_ton_dong": False,
             "bat_dau": _thoi_diem(), "lan_gui_cuoi": None}
```

Thêm 3 hàm mới:

```python
def _nghe_telegram(env, cau_hinh, bay_gio, thong_bao, tt_tg):
    """Doc tin Telegram moi va xu ly. DAY LA NOI DUY NHAT doc tin cua bot.

    Vi sao agent phai tu doc: getUpdates chi giao moi tin cho MOT noi goi. Truoc
    day nguoi truc doc roi chuyen tiep qua logs/agent-lenh.json — chay duoc
    nhung thua mot mat xich, va chinh no sinh ra 2 loi that (30/09/2026).
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
        except Exception as e:            # mot tin hong khong duoc giet vong lap
            report.log(f"AGENT: loi khi xu ly mot tin Telegram: {e}")


def _doc_tin_ton_dong(env, cau_hinh, bay_gio, thong_bao, tt_tg):
    """Lan dau khoi dong: doc het tin dang cho, XU LY lenh/nut bam, BO cau hoi cu.

    Ly do khong tra loi cau hoi cu: bot se tra loi mot loat tin nhan cu, roi
    loan. Nhung lenh va nut bam thi PHAI xu ly — bo di la mat viec Dai da lam.
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
    """Mot update: nut bam / lenh go tay / cau hoi."""
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
    # vao hang doi" — nay hang doi khong con ai doc nua.
    if lenh_telegram.la_hoan_tac(noi_dung) or lenh_telegram.la_lenh(noi_dung):
        _lam_theo_lenh(env, cau_hinh, bay_gio, thong_bao, noi_dung, None)
        return

    # Cau hoi -> dung lai dung ham cua nguoi truc (ham thuan, da co kiem thu).
    tra_loi = nguoi_truc.tra_loi_tin_nhan(
        cau_hoi=noi_dung,
        env=env,
        danh_sach_moc=report.doc_moc_tu_env(env),
        bat_dau=tt_tg["bat_dau"],
        lan_gui_cuoi=tt_tg["lan_gui_cuoi"],
        da_gui=report.ds_moc_da_gui(bay_gio.strftime("%Y-%m-%d")),
        now=bay_gio,
        nhan="Agent (nấc 2)",
    )
    if nguoi_truc.gui_tin_nhan(env, tra_loi):
        report.log("AGENT: da tra loi mot tin nhan")
```

Và **tách** phần xử lý lệnh ra khỏi `_xu_ly_tra_loi` cũ:

```python
def _lam_theo_lenh(env, cau_hinh, bay_gio, thong_bao, noi_dung, tin_nhan_id):
    """Mot lenh cua Dai: hoan tac / dong y / bo qua. Dung chung cho nut bam va go tay."""
    ... (chinh la than ham _xu_ly_tra_loi cu, bo phan doc hang doi)
```

`_xu_ly_tra_loi` cũ **bị xoá** (không còn hàng đợi để đọc).

**Trong vòng lặp** — thay `_xu_ly_tra_loi(...)` bằng:

```python
                # 1. NGHE Telegram, vong ngan — bam nut la xu ly gan nhu tuc thi
                _nghe_telegram(env, cau_hinh, bay_gio, thong_bao, tt_tg)
```

`chay_mot_vong` (dùng cho `--thu` / `--mot-lan`) **giữ nguyên**: không đọc Telegram (tránh nuốt tin).

### 3.4. Kiểm thử

| # | Bài | Điều phải đúng |
|---|---|---|
| 1 | `test_nguoi_truc_khong_con_doc_telegram` | `mot_vong()` **không** gọi `self.lay_tin` (tiêm hàm đếm) |
| 2 | `test_nut_bam_duoc_xu_ly_va_tra_loi_ngay` | `_xu_ly_mot_tin` gọi `tra_loi_nut_bam` rồi `_lam_theo_lenh` |
| 3 | `test_lenh_go_tay_KHONG_di_vao_AI` | tin "tắt 120..." không gọi `tra_loi_tin_nhan` |
| 4 | `test_cau_hoi_thi_tra_loi_bang_nguoi_truc` | tin "còn sống không?" → gọi `tra_loi_tin_nhan` + `gui_tin_nhan` |
| 5 | `test_tin_tu_nguoi_la_bi_bo_qua` | chat_id khác → không gửi gì |
| 6 | `test_tin_ton_dong_xu_ly_lenh_bo_cau_hoi` | lần đầu: lệnh được xử lý, câu hỏi cũ **không** trả lời |
| 7 | `test_mot_tin_hong_khong_giet_vong_lap` | tin `None`/thiếu khóa → không ném |
| 8 | `test_nhan_mac_dinh_van_la_Nguoi_truc` | `tra_loi_tin_nhan` không truyền `nhan` ⇒ câu cũ giữ nguyên |

---

## 4. RỦI RO

| Rủi ro | Mức | Xử lý |
|---|---|---|
| **Hai tiến trình cùng đọc trong lúc chuyển nhà** ⇒ tin bị nuốt | **Cao** | Thứ tự bắt buộc khi khởi động lại: **người trực TRƯỚC** (nó thôi đọc), **rồi agent** (nó bắt đầu đọc). Khe hở vài giây; tin trong khe hở được agent xử lý lúc khởi động |
| Agent chết ⇒ mất cả hỏi đáp lẫn nút bấm | **Cao** | Agent đã có lịch Windows tự bật lại (`AgentNac2`). Vẫn phải theo dõi vài ngày |
| Trả lời câu hỏi cũ hàng loạt khi khởi động | Trung bình | `_doc_tin_ton_dong` **không** trả lời câu hỏi cũ, chỉ xử lý lệnh/nút bấm |
| Hỏi "còn sống không?" nay do agent trả lời, thông tin về báo cáo vẫn của người trực | Thấp | Chấp nhận; `nhan="Agent (nấc 2)"` nói rõ ai trả lời |
| `--thu` / `--mot-lan` nuốt tin thật | Trung bình | **Không** cho hai chế độ đó đọc Telegram (giữ nguyên như cũ) |

---

## 5. KẾT QUẢ DỰNG THỬ

*(điền sau khi chạy thử — với thay đổi này, bộ kiểm thử chính là phép dựng thử, vì có thể chạy
toàn bộ logic phân loại tin bằng hàm giả, KHÔNG cần mạng)*
