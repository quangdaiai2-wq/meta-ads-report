# Kế hoạch: Đối chiếu sổ agent với nhật ký Meta (Đường 2)

Ngày lập: 03/10/2026 · Người duyệt: Đại
Trạng thái: **CHỜ ĐẠI DUYỆT** (chưa sửa code thật)

---

## 0. Kế hoạch này đã được VIẾT LẠI — đọc mục này trước

Bản kế hoạch đầu tiên của tôi (cùng ngày) nói *`cap_nhat_phan_hoi` ghi thêm bản ghi mới,
đẻ ra bản ghi rác*. **Sai.** Tôi đã dựng thử bằng số thật và tìm ra sự thật khác,
nghiêm trọng hơn. Ba phát hiện:

### Phát hiện 1 — "Ghi trùng" KHÔNG phải lỗi ghi trùng

Tôi đã soi **cả 40 bản ghi** trong `logs/nhat-ky-agent.json`. Có **17 nhóm** xuất hiện
2 lần. Nhưng **4 khẳng định dưới đây đều ĐÚNG** (đã chạy máy kiểm):

| Khẳng định | Kết quả đo |
|---|---|
| Bản ghi thứ 2 **luôn** có `da_gui_len_meta = True` | **ĐÚNG** |
| Bản ghi thứ 2 **luôn** thiếu `ket_qua` (None) | **ĐÚNG** |
| Bản ghi thứ 1 **luôn** có `che_do = "xin_phep"` | **ĐÚNG** |
| Bản ghi thứ 1 **luôn** khác vai với bản ghi thứ 2 | **ĐÚNG** |

⇒ Hai bản ghi đó **không phải bản sao của nhau**. Chúng là **hai vai khác nhau** trong
vòng đời một việc:

```
  BẢN GHI 1  (luc = 11:45:09)   ← lúc HỎI Đại        → che_do="xin_phep", da_gui=False
  BẢN GHI 2  (luc = 11:46:55)   ← lúc GHI TRƯỚC KHI GỬI META → da_gui=True
```

Đây không phải lỗi thiết kế: luật của dự án là **"ghi sổ TRƯỚC khi gửi lên Meta —
bắt buộc, không tắt được"**. Bản ghi 2 chính là bản ghi đó.

### Phát hiện 2 — Lỗi THẬT: "bản ghi mồ côi", kết quả ghi nhầm chỗ

`cap_nhat_phan_hoi` đi tìm bản ghi để chốt kết quả bằng điều kiện:

```python
if rec.get("che_do") != "xin_phep" or rec.get("dai_phan_hoi"):
    continue        # tìm bản ghi CHƯA có dai_phan_hoi
```

Nó tìm **từ dưới lên** (`reversed`), nên gặp **bản ghi 2** trước — và bản ghi 2 lúc đó
**chưa có `dai_phan_hoi`** (vì `_lam_theo_dong_y` mới gán `dai_phan_hoi` **vào biến trong
bộ nhớ**, chưa ghi ra file). Kết quả: nó tưởng bản ghi 2 là đích... nhưng theo số thật
thì kết quả lại **rơi vào bản ghi 1**.

Đã dựng thử, in ra từng bước:

```
TRƯỚC:  bg1  da_gui=False  dai_phan_hoi=None                        ket_qua=None
        bg2  da_gui=True   dai_phan_hoi='tat:120250389649480509'    ket_qua=None

SAU:    bg1  da_gui=False  dai_phan_hoi='tat:120250389649480509'    ket_qua='thanh cong (...)'
        bg2  da_gui=True   dai_phan_hoi='tat:120250389649480509'    ket_qua=None  ← MỒ CÔI
```

**Hậu quả:** bản ghi **thực sự đã gửi lệnh lên Meta** (`da_gui=True`) **mãi mãi trống
kết quả**. Còn bản ghi chỉ để hỏi Đại (`da_gui=False`) lại mang kết quả. Nội dung bị **lệch vai**.

### Phát hiện 3 — Tôi ĐÃ SAI: bộ đếm trần KHÔNG hề bị sai

Tôi tưởng lỗi Phát hiện 2 làm bộ đếm trần sai, vì `_la_hanh_dong_that()` cộng **cả hai**
bản ghi của cùng một nhóm. Tôi viết kiểm thử N15 cho giả thuyết đó. **Kiểm thử XANH
ngay từ đầu ⇒ giả thuyết SAI.**

Lý do thật: `_la_hanh_dong_that()` đòi `da_gui_len_meta is True`, mà bản ghi 1 (lúc hỏi
Đại) có `da_gui=False` ⇒ **bị loại**. Nên mỗi việc chỉ còn **1 bản ghi** được đếm.

Đo lại trên sổ thật, hai con số khớp nhau:

| Ngày | Hành động thật | Nhóm khác nhau |
|---|---|---|
| 01/10 | 2 | 2 |
| 02/10 | 10 | 10 |
| 03/10 | 5 | 5 |

⇒ **Không có lỗi trần giờ. Không sửa `dem_hanh_dong`.** Các bài kiểm thử về bộ đếm được
giữ lại **để canh**, không phải để sửa. Mục 2(c) trong bản kế hoạch trước **bị bỏ hoàn toàn**.

> Bài học ghi lại: tôi đã hai lần suy đoán sai về sổ này. Lần nào cũng phải **dựng thử
> bằng số thật** mới biết đúng sai — đọc code suông là chưa đủ.

---

## 1. Vì sao chọn Đường 2

Đại xác nhận **không phải chủ tài khoản doanh nghiệp** và **không xin được** Admin.
Meta xác nhận bằng dữ liệu cứng:

```
Business: Langmaster Business ()
  → Người dùng: "" — role: EMPLOYEE
  → Tài khoản QC: act_ = "" (tài sản công ty)
  → system_users: rỗng (0 mục)
```

Vai trò `EMPLOYEE` **không đủ quyền** tạo System User ⇒ Đường 1 và Đường 3 đều bị chặn.

⇒ Chọn **Đường 2**: giữ token cá nhân (mọi thao tác trên Meta sẽ hiện tên
**** — chủ token, KHÔNG phải Đại), nhưng bù lại bằng cách **ghi rõ nguồn gốc
trong sổ của agent** và làm **công cụ đối chiếu** để trả lời câu "việc này ai làm".

---

## 2. Ba việc sẽ làm

### Việc 1 — Đánh dấu rõ NGUỒN GỐC trong mỗi bản ghi

Thêm **trường `nguon_goc`** vào mọi bản ghi mới:

| `nguon_goc` | Nghĩa |
|---|---|
| `agent_tu_hanh` | Agent tự quyết, **không ai bấm nút** (TH2 tắt chiến dịch, chuyển NS) |
| `dai_bam_nut` | Agent làm **sau khi Đại bấm nút** |
| `dai_go_tay` | Đại gõ lệnh bằng tay qua Telegram |

Thêm **trường `nhac_meta`** ghi chú: *"Trên Meta sẽ hiện tên **** — đó là
token cá nhân, KHÔNG phải Đại thao tác."*

> Vì sao cần: mở sổ ra là biết ngay việc nào máy làm, việc nào Đại làm — **không cần**
> mở Meta.

### Việc 2 — Sửa lỗi "bản ghi mồ côi" (Phát hiện 2)

Đây là **sửa gốc**, làm đúng hai việc:

**(a) `_lam_theo_dong_y`** — gán luôn `nguon_goc` cho bản ghi trước khi ghi:
* Bấm nút → `"dai_bam_nut"`
* Gõ tay → `"dai_go_tay"`
(nhận qua tham số mới của `_lam_theo_lenh`, mặc định `"dai_bam_nut"` để kiểm thử cũ không vỡ)

**(b) `cap_nhat_phan_hoi`** — chốt kết quả vào **đúng bản ghi đã gửi Meta**.
Điều kiện mới: tìm bản ghi có `da_gui_len_meta is True` + `ket_qua is None`;
nếu không có thì mới lùi về hành vi cũ (tương thích bản ghi cũ).

**KHÔNG sửa `dem_hanh_dong`.** Xem Phát hiện 3 — giả thuyết "đếm gấp đôi" đã bị bác bỏ
bằng kiểm thử.

> ⚠️ `cap_nhat_phan_hoi` có tham số `ghi_meta_that_bai` mà `nhom_da_tra_loi` đang dựa vào.
> Sửa xong phải chạy hết kiểm thử hiện có để không phá Rào 8.

### Việc 3 — Công cụ `doi-chieu-meta.py` (trái tim của Đường 2)

Một công cụ **CHỈ ĐỌC**, làm đúng việc mà token App lẽ ra làm được:

```
Đầu vào : logs/nhat-ky-agent.json  +  nhật ký Meta (act_.../activities)
Ra      : Bảng đối chiếu

  Việc                          | Sổ agent nói    | Meta nói      | Khớp? | Ai làm
  ------------------------------|-----------------|---------------|-------|--------
  Tắt nhóm 120250389649480509   | 02/10 11:46     | 02/10 11:46   | ✅    | agent
  Tắt chiến dịch 120250...509   | 03/10 10:59     | 03/10 10:59   | ✅    | agent tự
  Bật lại nhóm 120250506886650509 | 30/09 09:58   | 30/09 09:58   | ✅    | Đại bấm

  Việc CHỈ có trên Meta (không có trong sổ agent) — ĐẠI TỰ LÀM TAY:
  - 03/10 10:00  tạo chiến dịch mới ...
```

Cách khớp: mỗi bản ghi agent có `luc` (giờ VN) + `doi_tuong.id` + `hanh_dong`.
Meta trả `event_time` (UTC) + `object_id` + `event_type`. Quy đổi giờ, khớp theo
`(object_id, trong khoảng ±2 phút)`.

> Vì sao ±2 phút: Meta ghi theo giây nhưng có độ trễ; và một thao tác "tắt nhóm + tắt ad +
> đổi tên" sinh **nhiều** sự kiện trong vài giây. Cửa sổ ±2 phút gom đúng chúng lại.

> ⚠️ Khi đối chiếu **phải bỏ qua bản ghi mồ côi** (`da_gui=True` mà `ket_qua=None`) —
> nếu không sẽ báo "agent ghi mà Meta không nhận" sai. Chỉ lấy bản ghi **có kết quả**.

---

## 3. Ca kiểm thử (viết TRƯỚC khi sửa code)

| # | Tình huống | Mong đợi |
|---|---|---|
| N1 | Bản ghi agent có `luc` + `id`, Meta có sự kiện cùng id, cùng phút | **KHỚP** |
| N2 | Meta có sự kiện lệch 3 phút | **KHÔNG khớp** (ngoài cửa sổ ±2) |
| N3 | Meta ghi tên "" cho việc của agent | Vẫn **KHỚP** — không phụ thuộc tên |
| N4 | Meta có sự kiện không có trong sổ agent | Xếp vào nhóm **"Đại tự làm tay"** |
| N5 | Sổ agent có việc, Meta không có | **"nghi vấn — agent ghi mà Meta không nhận"** |
| N6 | Danh sách Meta rỗng / lỗi mạng | Trả bảng rỗng + nêu lý do, **không ném lỗi** |
| N7 | Hai bản ghi agent cùng id, cùng phút | **KHÔNG** báo lỗi trùng — nhận diện là 2 VAI (hỏi / gửi) |
| N8 | Bản ghi agent thiếu `luc` hoặc thiếu `id` | Bỏ qua, không làm sập |
| N9 | Công cụ chỉ ĐỌC | Không `api_post`, không gửi Telegram |
| N10 | Bản ghi mới có `nguon_goc` | Đọc được, hiện đúng trong bảng |
| N11 | Bản ghi CŨ không có `nguon_goc` | Suy từ `da_gui_len_meta` + `dai_phan_hoi`, không để trống |
| N12 | **Chốt kết quả** cho một nhóm có 2 bản ghi | Kết quả vào bản ghi **`da_gui=True`**; bản ghi `da_gui=False` **không** mang kết quả |
| N13 | Bản ghi **mồ côi** (`da_gui=True`, `ket_qua=None`) | **Phát hiện và liệt kê riêng** — đây là lỗi, phải thấy được |
| N14 | Công cụ đối chiếu gặp bản ghi mồ côi | **Bỏ qua**, không báo "Meta không nhận" sai |
| N15 | ~~`dem_hanh_dong` với 1 nhóm có 2 bản ghi~~ | **BỎ** — kiểm thử xanh ngay, giả thuyết sai |

---

## 4. Rủi ro

| Rủi ro | Xử lý |
|---|---|
| Sửa `cap_nhat_phan_hoi` phá Rào 8 | Chạy hết 795 kiểm thử; có 17 bài canh Rào 8 |
| Sửa sổ làm mất dữ liệu cũ | Chỉ **THÊM** trường, không xoá. Dựng thử trước |
| Công cụ đối chiếu lỡ GHI lên Meta | Kiểm thử N9 canh `api_post` không được xuất hiện |
| Khớp sai vì lệch múi giờ | Meta trả UTC, sổ ghi +07:00. Phải quy đổi, có kiểm thử riêng |
| Sửa hỏng sổ thật (40 bản ghi) | Dựng thử trên **bản sao**; sổ thật chỉ đọc |
| **Suy đoán sai về sổ** | **Đã xảy ra 2 lần trong phiên này.** Bắt buộc dựng thử bằng số thật |

**Ràng buộc repo:** chỉ thư viện chuẩn + `unittest`. Chú thích Việt không dấu, chuỗi hiện Đại có dấu.

---

## 5. Thứ tự thi công

1. Viết kiểm thử → chạy, **phải ĐỎ**. ✅ **XONG** — `tests/test_doi_chieu_meta.py`,
   13 bài, kết quả `FAILED (failures=4, errors=4)`.
2. **Dựng thử ngoài repo** trên bản sao sổ thật → phải XANH.
3. Đại duyệt.
4. Sửa code thật: `agent_ky_uc.py`, `agent.py`, thêm `doi_chieu_meta.py` + `doi-chieu-meta.bat`.
5. Chạy toàn bộ kiểm thử (795 bài cũ + bài mới).
6. Commit. Đại bấm `khoi-dong-lai-agent.bat`.
7. Sửa lại `HUONG-DAN-LAY-TOKEN-APP.md` cho đúng tiền đề (Đại là EMPLOYEE).

---

## 6. Bằng chứng đã thu (để Đại kiểm lại)

Thư mục `D:\Buddy Work AI\_kiem-chung-03-10\`:
* `chung_minh.py` — in bảng 17 nhóm + 4 khẳng định. Kết quả: **4/4 ĐÚNG**.
* `thu_cap_nhat.py` — dựng thử `cap_nhat_phan_hoi` bằng số thật. Kết quả: **xác nhận
  bản ghi 2 mồ côi**.
