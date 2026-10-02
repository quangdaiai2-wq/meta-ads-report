# Kế hoạch — Tên kèm năm + Xét ngưỡng theo TỪNG QUẢNG CÁO

**Ngày:** 02/10/2026 · **Người chốt:** Đại · **Trạng thái:** ✅ **Việc A ĐÃ VÀO REPO** (commit `0147c3d`) — ⏳ Việc B đang dựng thử

> 📌 **File này là BẢN DUY NHẤT.** Bản `2026-10-02-hau-to-kem-thang-nam-va-tat-theo-tung-quang-cao.md`
> là bản viết trước đó trong ngày, **nay đã gộp vào đây** (đổi đuôi thành
> `.gop-vao-file-chinh`) vì nó còn ghi hai điều nay đã sai: *"TH1 không ghi năm"* và
> *"lượt này chưa làm tắt lẻ quảng cáo"*.

**Bằng chứng gốc:** Đại phản hồi trực tiếp sáng 02/10/2026:
> *"1. Các nhóm đổi tên hiện nay đang bị thiếu năm đằng sau X10. Đúng thì phải là X10 26."*
> *"2. Nếu 1 nhóm quảng cáo chạy 2 quảng cáo thì quảng cáo nào đạt ngưỡng đã quy định thì phải tắt
> quảng cáo đó đi trước, quảng cáo còn lại giữ nguyên để chạy tiếp đến ngưỡng. Tuy nhiên trong
> trường hợp ví dụ như 2 quảng cáo chạy đều song song sẽ có trường hợp qc1 chi tiêu 200.000 có
> 1 tin nhắn, qc2 chi tiêu 90.000 đồng có 1 tin nhắn thì phải tắt cả vì lúc này sẽ chuyển sang
> quan tâm đến chi tiêu tổng thể cả nhóm."*

**Và bổ sung chiều 02/10/2026 — Đại giải mã:**
> *"X9-26 nghĩa là tắt vào tháng 9 năm 2026 đó"*
> *"Được. bạn cứ làm theo đúng những gì ta đã trao đổi từ trước đến nay và theo quy chuẩn đã thống nhất"*

---

## 0. BA SAI LẦM CŨ ĐÃ ĐƯỢC ĐÍNH CHÍNH

### 0.1. `X<n>` là **THÁNG ĐẶT TÊN**, không phải "lần thứ n", không phải tháng tạo nhóm

Đại giải mã: **`X9-26` = tắt vào tháng 9 năm 2026**.

Kiểm chứng bằng dữ liệu thật (đọc `/activities`, không gọi thêm Meta) — **14/14 ca KHỚP**:

| Lúc đặt tên | Tháng đặt | `X` trong tên | Khớp? |
|---|---|---|---|
| 2026-09-20 03:42 | 09/2026 | `X9-26` | ✅ |
| 2026-09-25 01:16 | 09/2026 | `X9` | ✅ |
| 2026-09-30 01:17 | 09/2026 | `X9` | ✅ |
| 2026-10-01 03:19 | 10/2026 | `X10` | ✅ |
| 2026-10-01 06:35 | 10/2026 | `X10` | ✅ |
| 2026-10-01 07:49 | 10/2026 | `X10` | ✅ |

🔑 **Hai ca QUYẾT ĐỊNH:**
- `2026 - 09 - 05 - ... 0/150 X10` — tên nhóm ghi *ngày tạo 09*, nhưng hậu tố là `X10`
  (vì **đặt tên lúc tháng 10**).
- `2025 - 07 - 02 - ... 0/180 X10` — tên nhóm ghi *ngày tạo 07/2025*, hậu tố là `X10`.

⇒ Nếu `X` là tháng **TẠO** thì phải ra `X9` và `X7`. Đại ghi `X10` cả hai.
⇒ `X<n>` **ăn theo THÁNG ĐANG ĐẶT TÊN**, hoàn toàn độc lập với ngày tạo nhóm.

⚠️ **Ghi chú cũ trong repo SAI.** `TONG-HOP-CACH-CHAY-QUANG-CAO.md` mục 3.4b mô tả `y` là
"trần CPR riêng nhóm" — không phải. Và mọi tài liệu hiểu `X<n>` là "lần thứ n" cũng không phải.

### 0.2. Định dạng năm: **GẠCH NỐI** `X10-26`, KHÔNG phải khoảng trắng `X10 26`

Tôi đã từng ghi vào kế hoạch buổi chiều: *"`X10` → `X10 26`"* — **SAI**. Đo trên tài khoản:

| Kiểu | Số tên nhóm |
|---|---|
| `X9-26` / `X10-26` (**gạch nối**) | **396** |
| `X10 26` (**khoảng trắng**) | **0** |

⇒ Mẫu khoảng trắng **không tồn tại** trên tài khoản. Nếu code theo mẫu đó, mỗi lần tắt sẽ đẻ ra
một định dạng chưa từng có, và `RE_HAU_TO` có thể không cắt được ⇒ **tắt lần hai chồng tên**.

✅ **Đại chốt cuối ngày 02/10/2026:** dùng **gạch nối**, và **CẢ BA** trường hợp đều ghi năm.

### 0.3. Luật cũ *"TH1 không ghi năm"* — **ĐÃ BỎ**

`TONG-HOP-CACH-CHAY-QUANG-CAO.md` mục 5.1 ghi: *"`X9-26` chỉ dùng cho nhóm có từ 1 tin nhắn trở lên;
nhóm không có tin nhắn chỉ ghi `X9`"*. **Luật đó nay bị thay** — Đại muốn **mọi trường hợp đều ghi năm**.

### 🔴 0.4. PHẠM VI — Đại phát hiện 15:1x 02/10/2026, đây là điều PHẢI KHẮC CỐT

**Đại nói:**
> *"'Quảng cáo Mức độ nhận biết mới' → '... 0/350 X10-26 TN'
> Cái này là bạn động vào qc của truong rồi à. Chỉ được áp dụng đối với dainq thôi mà"*

**Đọc thật từ Meta — không suy đoán:**

| | |
|---|---|
| Tổng số nhóm đọc được (đọc hết, có phân trang) | **1800** |
| Nhóm **KHÔNG** chứa `dainq` | **64 — đều là nhóm của Truong** |
| Ví dụ | `2026 - 8 - 27 - Truong - Online - Target sinh viên - Bản sao 2` |
| Quảng cáo bên trong nhóm Truong | `Quảng cáo Lượt tương tác mới` · `... - Bản sao` |
| Quảng cáo đó có `dainq` không? | ❌ **KHÔNG** — Meta tự sinh tên |

⇒ **KHÔNG THỂ lọc theo tên quảng cáo.** Tên quảng cáo của Truong không hề giống của Đại.

### 🔴 QUY TẮC SẮT — áp cho TOÀN BỘ Việc B

```
PHẠM VI LUÔN LUÔN KIỂM THEO *TÊN NHÓM* (adset chứa quảng cáo).
TUYỆT ĐỐI KHÔNG kiểm theo TÊN QUẢNG CÁO.
```

| Nếu kiểm theo tên QUẢNG CÁO thì… | Hậu quả |
|---|---|
| `thuoc_pham_vi(ten_ad)` với ad của **Đại** | Tên Meta tự sinh, không có `dainq` ⇒ **False** ⇒ ad của Đại **bị bỏ qua** ⇒ agent **vô dụng** |
| `thuoc_pham_vi(ten_ad)` với ad của **Truong** | Cũng False — **nhưng** nếu ai viết ngược lại (coi tên ad là đủ) ⇒ **đụng tài sản của Truong** |

**CẢ HAI CHIỀU ĐỀU SAI.** Chỉ có một cách đúng: mỗi lần cần biết một quảng cáo có thuộc phạm vi
không, **đọc lại TÊN NHÓM chứa nó** rồi kiểm tên nhóm đó.

**Đã kiểm chứng rào hiện tại chặn đúng:** gọi `tat_quang_cao` với nhóm Truong
`120250116467270509` (đang ACTIVE) ⇒ `thanh_cong = False`, **POST lên Meta = 0**.

**Ba lớp đều kiểm TÊN NHÓM (giữ nguyên, không được nới):**

| Lớp | File · dòng |
|---|---|
| Không sinh đề xuất | `agent_muc_tieu.py:147` — `thuoc_pham_vi(ten)` với `ten` là **tên nhóm** |
| Rào trung tâm từ chối | `agent_rao.py:140` |
| Đọc lại trước khi ghi | `agent_cong_cu_ghi.py:190` (adset) và `:287` (ad) |

**Đã khóa bằng kiểm thử:**
- `kiem_thu_pham_vi.py` — 5 bài: tên quảng cáo **luôn** ngoài phạm vi; 7 kiểu tên nhóm Truong thật
  (kể cả **sau khi gắn hậu tố**) **luôn** ngoài phạm vi; nhóm của Đại **không bị chặn quá tay**
- `kiem_thu_ghi.py` lớp **D** — 4 bài: `tat_quang_cao` trên nhóm Truong (cả tắt-hết lẫn
  tắt-chọn-lọc) **phải bị chặn và POST = 0**

⚠️ **Khi làm B3 (`tat_mot_quang_cao`) phải theo đúng quy tắc này.** Đó là lý do mục 5.10 dưới đây
ghi rõ: *"KHÔNG kiểm tên quảng cáo (Meta tự sinh, không có `dainq`)"*.

---

## 1. Vì sao có kế hoạch này

### Việc 1 — Tên nhóm thiếu năm

Đại tự tay đặt tên nhóm **521 lần trong 30 ngày**. Tên nhóm với Đại là **bảng thông tin vận hành**:
nhìn tên là biết nhóm đã tắt chưa, tắt tháng nào, có tin nhắn hay không.

Sáng nay thấy tên sinh ra là `... X10` — **thiếu năm**. Đại muốn `X10-26`.

### Việc 2 — Xét ngưỡng theo từng quảng cáo

Bảng lịch sử thao tác cho thấy Đại **can thiệp ở cấp QUẢNG CÁO 1.541 lần**, gấp đôi cấp nhóm
(797 lần). Nhưng agent hiện tại **chỉ biết tắt cả nhóm** — nó bỏ qua hoàn toàn cấp quảng cáo.

Đại muốn: nhóm chạy nhiều quảng cáo thì **quảng cáo nào chạm ngưỡng thì tắt riêng nó**, để quảng
cáo còn lại chạy tiếp. **Nhưng** nếu tổng chi tiêu cả nhóm chạm ngưỡng thì **tắt cả nhóm**.

---

## 2. LUẬT ĐẠI CHỐT — ghi lại nguyên văn, có ví dụ số

### 2.1. Thứ tự xét — phụ thuộc vào việc quảng cáo ĐÃ CÓ KẾT QUẢ hay CHƯA

> *"khi quảng cáo chưa có bất kỳ 1 kết quả nào thì xét ở quảng cáo rồi đến nhóm /
> khi quảng cáo đã có kết quả rồi thì xét từ nhóm rồi quảng cáo"*

```
BƯỚC 1: Trong nhóm có quảng cáo nào CHƯA có kết quả không?
        │
        ├── CÓ   →  xét QUẢNG CÁO trước  →  rồi mới tới NHÓM
        │
        └── KHÔNG →  xét NHÓM trước      →  rồi mới tới QUẢNG CÁO
```

### 2.2. Mỗi quảng cáo tự chọn mốc của chính nó

Đại chốt **"chọn a"** — quảng cáo **không mượn mốc của nhóm**, mà dùng **cùng bộ quy tắc** áp cho
chính số liệu của nó:

| Quảng cáo | Mốc áp dụng |
|---|---|
| **Chưa có kết quả** (0 tin nhắn, 0 lượt mua) | **70.000đ** hôm nay (giống TH1) |
| Đã có tin nhắn nhưng chưa ra lượt mua | **290.000đ** hôm nay (giống TH2) |
| Đã có lượt mua trong tháng | giá mỗi lượt mua **tháng** ≥ **390.000đ** (giống TH3) |

Xét theo thứ tự **TH3 → TH2 → TH1**, y hệt cấp nhóm.

### 2.3. Tắt riêng quảng cáo = chỉ TẮT + ĐỔI TÊN. KHÔNG hạ ngân sách.

> *"Không nhé. Chỉ tắt quảng cáo đang chạy và chi tiêu đến ngưỡng thôi"*

**Hạ ngân sách chỉ dành cho cả nhóm**, và chỉ khi Đại bấm nút `💰 TẮT NHÓM + HẠ NGÂN SÁCH`.

### 2.4. Luật ưu tiên — 🔴 ĐẠI CHỐT LẦN CUỐI 15:5x 02/10/2026

Mục này đã **sửa hai lần** trong ngày 02/10/2026. Ghi lại cả hai để không lặp lại sai lầm.

#### Lần 1 (16:0x) — Đại phát hiện mâu thuẫn

```
nhóm chi 100.000đ, 0 tin nhắn   →  TỔNG NHÓM đã chạm 70.000đ
  ad1 chi  80.000đ  → chạm 70.000đ
  ad2 chi  20.000đ  → chưa chạm
```

| Cách đọc | Kết quả |
|---|---|
| *"quảng cáo chưa có kết quả ⇒ xét QUẢNG CÁO trước"* | tắt lẻ **ad1** |
| *"tổng nhóm chạm ngưỡng ⇒ tắt cả nhóm"* | tắt **cả nhóm** |

⚠️ **Hai luật cho HAI kết quả khác nhau.** Đại phân xử: *"Chỉ tắt lẻ quảng cáo"* — để giữ
lại **ad2** đang còn cơ hội.

#### 🔴 Lần 2 (15:5x) — dựng thử ĐO THẬT và phát hiện luật lần 1 bị VỠ

Tôi cài luật lần 1 vào bản dựng thử, rồi **đo tài khoản thật**:

```
82 nhóm ACTIVE thuộc phạm vi Đại
├── 66 nhóm  không có quảng cáo nào
├── 16 nhóm  có ĐÚNG 1 quảng cáo      ← 19,5%
└──  0 nhóm  có từ 2 quảng cáo trở lên
```

**Cả 16 nhóm một-quảng-cáo đều có: chi tiêu quảng cáo = chi tiêu nhóm, đúng 100,0%.**

| Nhóm | Chi tiêu nhóm | Chi tiêu ad | ad/nhóm |
|---|---|---|---|
| `120250213748540509` | 779.615đ | 779.615đ | 100,0% |
| `120250080111780509` | 648.122đ | 648.122đ | 100,0% |
| `120249911752740509` | 575.700đ | 575.700đ | 100,0% |
| `120250263934130509` | 560.416đ | 560.416đ | 100,0% |
| … 12 nhóm còn lại | | | 100,0% |

**Vì sao luật lần 1 vỡ ở nhóm một quảng cáo:** "tắt lẻ, lần sau tắt nhóm" **không bao giờ
thoát ra**, vì giữa hai lần quét **không có gì thay đổi**:

```
Quét lần 1  →  tắt lẻ ad1
Quét lần 2  →  tắt lẻ ad1     (số KHÔNG đổi)
Quét lần 3  →  tắt lẻ ad1     (số KHÔNG đổi)
```

Số không đổi vì **hai lý do cộng lại**:
1. Quảng cáo chiếm 100% chi tiêu nhóm ⇒ tắt ad thì nhóm ngừng chi tiêu ⇒ số dừng luôn.
2. Insights **THÁNG** vẫn giữ dòng lịch sử của quảng cáo **đã tắt** ⇒ ad vẫn nằm trong
   `ds_ad` và vẫn bị đề xuất tắt lại.

Hậu quả thật: nhóm giữ **ACTIVE** mãi, ngân sách vẫn 400.000đ mãi, **không bao giờ hạ
27.000đ**, và cứ **15 phút agent nhắc lại một lần — nhắc mãi mãi**.

Đã **mô phỏng ba lần quét liên tiếp**, cả ba ra y hệt nhau — xác nhận lặp vô tận.

#### ✅ LUẬT CHỐT CUỐI CÙNG — Đại nguyên văn 15:5x 02/10/2026

> *"Bao giờ có từ 02 quảng cáo trở lên trong nhóm thì tự động chuyển sang xét duyệt như vậy."*

| Nhóm có | Hành động |
|---|---|
| **Từ 2 quảng cáo**, có quảng cáo chạm ngưỡng | **Tắt LẺ** quảng cáo đó, **giữ nhóm** chạy tiếp |
| **Chỉ 1 quảng cáo**, nó chạm ngưỡng | **TẮT CẢ NHÓM** + hạ ngân sách 27.000đ + đổi tên |
| **0 quảng cáo**, nhóm chạm ngưỡng | **TẮT CẢ NHÓM** + hạ ngân sách 27.000đ + đổi tên |

**Vì sao "tắt lẻ" phải phụ thuộc số quảng cáo:** tắt lẻ chỉ có nghĩa khi **có thứ để bảo
vệ** — một quảng cáo khác đang còn cơ hội. Nhóm một quảng cáo thì không có gì để bảo vệ:
tắt lẻ cũng làm nhóm ngừng chi tiêu y như tắt nhóm, chỉ khác là nhóm vẫn mang tiếng
ACTIVE và ngân sách không được hạ.

⚠️ **Tắt lẻ quảng cáo KHÔNG hạ ngân sách** (`ngan_sach_ha = None`). Hạ ngân sách là việc
của cả nhóm.

⚠️ **Số quảng cáo tính theo `ds_ad`** — tức theo dòng `level=ad` insights **tháng**. Nhóm
có 0 dòng ⇒ tắt nhóm; 1 dòng ⇒ tắt nhóm; ≥2 dòng ⇒ xét lẻ.

#### Ví dụ số áp luật chốt

```
VÍ DỤ A — nhóm 0 quảng cáo (66/82 nhóm của Đại)
  nhóm chi 100.000đ, 0 tin nhắn  →  chạm TH1
  → TẮT CẢ NHÓM, hạ ngân sách, đổi tên: "<gốc> 0/200 X10-26"

VÍ DỤ B — nhóm 1 quảng cáo (16/82 nhóm của Đại)
  nhóm chi 100.000đ  →  chạm TH1
  ad1  chi 100.000đ  →  chạm TH1     (ad = 100% nhóm, luôn bằng nhau)
  → TẮT CẢ NHÓM (KHÔNG tắt lẻ), hạ ngân sách, đổi tên

VÍ DỤ C — nhóm 2 quảng cáo (0/82 nhóm hiện có, nhưng luật phải sẵn)
  nhóm chi 100.000đ  →  chạm TH1
  ad1  chi  80.000đ  →  chạm TH1
  ad2  chi  20.000đ  →  chưa chạm, còn cơ hội
  → TẮT LẺ ad1 (giữ ad2), KHÔNG hạ ngân sách, KHÔNG đổi tên nhóm

VÍ DỤ D — nhóm 2 quảng cáo, KHÔNG ad nào chạm riêng
  qc1 200.000đ/1 tin  →  chạm TH2 (290k)? KHÔNG
  qc2  90.000đ/1 tin  →  chạm TH2?        KHÔNG
  tổng nhóm 290.000đ/2 tin  →  chạm TH2
  → KHÔNG có quảng cáo nào để tắt lẻ ⇒ TẮT CẢ NHÓM
  ⚠️ Bản kế hoạch 16:0x từng ghi ca này "KHÔNG đề xuất gì" — SAI. Nếu vậy thì nhóm
     chạm ngưỡng mà KHÔNG BAO GIỜ bị tắt. Đã sửa.
```

#### ⚠️ CẢNH BÁO cho lần sau — "lần quét sau" chỉ đúng khi có gì đó ĐỔI

Cả **hai** lỗi thật của mục này đều cùng một loại: **hoãn sang lần quét sau trong khi
không có gì thay đổi giữa hai lần quét.**

⇒ Khi thiết kế bất kỳ luật nào có chữ **"lần sau"**, phải hỏi ngay:
**"cái gì sẽ khác đi để lần sau khác lần này?"** Không trả lời được ⇒ luật đó sẽ lặp vô tận.

---

## 3. Đối chiếu với code đang chạy

| | Đang chạy | Luật mới |
|---|---|---|
| Tên nhóm | `0/140 X10` | **`0/140 X10-26`** |
| Cấp xét | chỉ **adset** | **adset + ad** |
| Thứ tự xét | luôn nhóm trước | **tuỳ số quảng cáo:** ≥2 ⇒ xét ad trước; <2 ⇒ xét nhóm |
| Tắt quảng cáo | **tắt HẾT** ad trong nhóm (khi tắt nhóm) | **tắt CHỌN LỌC** ad chạm ngưỡng (chỉ khi nhóm ≥2 ad) |
| Đổi tên quảng cáo | không | **có** (dùng hậu tố của nhóm) |
| Hạ ngân sách quảng cáo | không | **không** (giữ nguyên) |
| Đọc `level=ad` | **không có** | **phải thêm** |

### 🔴 Ranh giới quyết định — SỐ QUẢNG CÁO TRONG NHÓM

| Nhóm có | Nhóm chạm ngưỡng | Hành động |
|---|---|---|
| **0 quảng cáo** | có | TẮT CẢ NHÓM + hạ 27.000đ + đổi tên |
| **1 quảng cáo** | có | TẮT CẢ NHÓM + hạ 27.000đ + đổi tên |
| **≥2 quảng cáo**, có ad chạm | có | **TẮT LẺ ad đó** — KHÔNG hạ ngân sách, KHÔNG đổi tên nhóm |
| **≥2 quảng cáo**, không ad nào chạm | có | TẮT CẢ NHÓM + hạ 27.000đ + đổi tên |
| bất kỳ | không | không làm gì (trừ ad lẻ chạm khi nhóm ≥2 ad) |

---

## 4. Việc A — Tên nhóm kèm năm

### 4.1. Sửa `ten_moi()` trong `agent_muc_tieu.py`

```
TH1: <tên gốc> 0/<2×chi tiêu> X<tháng>-<năm 2 số>          →  0/140 X10-26
TH2: <tên gốc> 0/350 X<tháng>-<năm 2 số> TN                →  0/350 X10-26 TN
TH3: <tên gốc> <lượt mua>/450 X<tháng>-<năm 2 số>          →  1/450 X10-26
```

⚠️ **CẢ BA** trường hợp đều ghi năm — luật cũ *"TH1 không ghi năm"* **đã bỏ**.

⚠️ Dùng **GẠCH NỐI** (`X10-26`), **KHÔNG** dùng khoảng trắng (`X10 26`).
**Đo thật trên tài khoản 02/10/2026: 396 tên nhóm dùng `X9-26`, 0 tên dùng `X9 26`.**

⚠️ Vị trí ` TN` phải ở **cuối cùng**, sau năm.

⚠️ Năm tính **động** (`t.year % 100:02d`) — sang 2027 phải ra `-27`, không được viết cứng `26`.

### 4.2. Sửa `RE_HAU_TO` — QUAN TRỌNG NHẤT

Regex cũ:
```python
RE_HAU_TO = re.compile(r"\s+\d+\s*/\s*\d+(\s+X\d+(-\d+)?)?(\s+[A-Za-zÀ-ỹ]+)*\s*$")
```

Regex mới (rút ra từ dựng thử 02/10/2026 — **đã chạy trên 237 tên nhóm thật, đạt 237/237**):
```python
RE_HAU_TO = re.compile(
    r"\s+\d+\s*/\s*\d+(\s+X\d+(-\d+)?)?(\s+[A-Za-zÀ-ỹ]+)*(\s*=>\s*[^\s]+)?\s*$")
```

**Vì sao thêm nhánh `(\s*=>\s*[^\s]+)?`** — thêm nhánh riêng thay vì nới nhánh cũ:
- Nhánh cũ chỉ nhận **chữ cái** ⇒ tên `... 0/160 X9 => Lỗi` **KHÔNG cắt được** ⇒ tắt lần hai
  **chồng tên**. **Tên này CÓ THẬT trên tài khoản** (đo được 2 nhóm `... X11 => Lỗi`).
- Nếu nới nhánh cũ cho nhận **số** thì sẽ **nuốt mất mã content** ở đuôi tên
  (`... Online 120825 1/450 X10-26` → mất `120825`).
- ⇒ Thêm **nhánh riêng** cho đuôi `=>`, không đụng nhánh nào khác ⇒ **không thể cắt quá tay**.

⚠️ Vẫn phải giữ khả năng cắt định dạng **CŨ** — tài khoản còn **rất nhiều** nhóm mang hậu tố
`X8-26`, `X9`, `X1/400 X4` do Đại tự đặt tay qua nhiều tháng. Không cắt được chúng thì cũng
chồng tên y như trên.

⇒ Regex mới cắt được **cả năm** dạng:

| Dạng | Ví dụ có thật trong tài khoản |
|---|---|
| `x/y X<m>` | `0/120 X7` |
| `x/y X<m>-<năm>` | `0/300 X8-26 TN` |
| `x/y X<m>-<năm> TN` ⬅ **MỚI** | `0/350 X10-26 TN` |
| `x/y X<m>-<năm>` ⬅ **MỚI** | `0/140 X10-26` |
| `x/y X<m> => Lỗi` ⬅ **MỚI** | `0/360 X11 => Lỗi` |

### 4.3. Thêm rào `truong_hop` hợp lệ — ĐÃ KIỂM AN TOÀN

Trong `ten_moi()`, thay `return` không điều kiện ở cuối bằng:
```python
    if truong_hop == 3:
        return f"{goc} {int(mua_thang or 0)}/{MOC_CHAN_TH3 // 1000} {duoi}"
    raise ValueError(f"truong_hop khong hop le: {truong_hop!r} (chi nhan 1/2/3)")
```

**Vì sao:** trước đây `truong_hop = 0` hoặc `9` **âm thầm** rơi vào TH3 ⇒ ra `0/450` mà không
báo gì. Đúng kiểu **lỗi im lặng**.

✅ **Đã kiểm điều kiện tiên quyết 02/10/2026:** rà 5 file (`agent_muc_tieu.py`, `agent_rao.py`,
`agent.py`, `agent_xin_phep.py`, `agent_ky_uc.py`) — `truong_hop` chỉ được gán ở **đúng 3 chỗ**
trong `agent_muc_tieu.py` (dòng 165 = 3, 173 = 2, 181 = 1). **Không nơi nào truyền giá trị lạ**
⇒ thêm `raise` **không làm sập agent**.

### 4.4. Hệ quả

`agent_rao.py` **không cần sửa** — nó chỉ kiểm `ten_moi` có phải chuỗi thật, không phân tích định dạng.

---

## 5. Việc B — Xét ngưỡng theo từng quảng cáo

### 5.1. Đọc `level=ad` — ĐÃ ĐO THẬT, xong

**Đo ngày 02/10/2026** trên `act_`:

| | |
|---|---|
| `level=ad` trả về | `ad_id`, `ad_name`, `adset_id`, `adset_name`, `spend`, `actions` ✅ |
| Số dòng `today` | 46 dòng, **không phân trang** |
| Số dòng `this_month` | 55 dòng, **không phân trang** |
| **Tốn hạn mức** | **1 lệnh gọi** cho cả tài khoản — `call_count: 1` |
| **Đối chiếu tổng tiền** | adset `12.165.690đ` = ad `12.165.690đ` — **lệch 0đ** ✅ |

⇒ **Đọc cấp quảng cáo tốn thêm 2 lệnh gọi mỗi vòng quét** (today + this_month), cộng vào 3 lệnh
hiện có ⇒ **5 lệnh/vòng**. Ở nhịp 15 phút: 480 lệnh/ngày ≈ **0,7% hạn mức/giờ**. Không đáng kể.

⚠️ **Điểm quan trọng về chi phí:** gọi **MỘT** lệnh `level=ad` cho **CẢ tài khoản** rẻ hơn nhiều so
với gọi `/{adset_id}/ads` cho từng nhóm (79 nhóm ⇒ 79 lệnh). Đúng như bài học 02/10: **đừng quét
từng nhóm một**.

### 5.2. Số liệu thật hôm nay — có bao nhiêu nhóm nhiều quảng cáo?

Đo lúc 14:xx ngày 02/10/2026:

| | |
|---|---|
| Nhóm đang ACTIVE | **90** |
| Trong phạm vi của Đại | **79** |
| Nhóm **có** ad phát sinh chi tiêu hôm nay | **14** |
| **Nhóm có ≥2 ad** phát sinh chi tiêu | **0** |

⇒ **Hôm nay việc B chưa đổi hành vi gì cả** — mọi nhóm đang chạy chỉ có **1 ad chi tiêu**. Luật mới
được viết để **sẵn sàng** cho khi có nhóm nhiều ad, chứ không phải để sửa ca đang cháy.

⚠️ **Nhưng luật này vẫn phải làm**, vì: (a) Đại yêu cầu, (b) tài khoản **có** nhóm 2 ad thật
(hai nhóm `Truong - Online` — xem dưới), chỉ là chưa rơi vào phạm vi Đại.

**Bằng chứng có nhóm 2 ad thật** (đo `this_month`):

| Nhóm | Số ad | Chi tiêu từng ad |
|---|---|---|
| `2026 - 8 - 14 - Truong - Online - Ads mess - Bản sao 2` | **2** | 342.332đ · 68.469đ |
| `2026 - 5 - 28 - Truong - Online - Chạy tệp mới - Bản sao 2` | **2** | 741.556đ · 45.950đ |

### 5.3. Đọc thêm `level=ad` trong `agent_doc_meta.py`

Thêm hàm mới (giữ nguyên `doc_chi_tieu` cũ để không vỡ chỗ gọi):

```python
def doc_chi_tieu_quang_cao(env, date_preset):
    """Chi tieu cap QUANG CAO. Tra ve {ad_id: dong insights}."""
    ...  level="ad", fields="ad_id,ad_name,adset_id,adset_name,spend,actions"
```

Sửa `doc_so` trả về **5** phần tử thay vì 3:
```python
return nhom, hom_nay, thang, hom_nay_ad, thang_ad
```

⚠️ `doc_so` đang được gọi ở `agent.py` và **trong kịch bản dựng thử**. Đổi chữ ký trả về phải
**cập nhật hết chỗ gọi** — dễ sót nhất là `tests/`.

### 5.4. Gom quảng cáo về theo nhóm

```python
def gom_theo_nhom(ds_dong_ad):
    """{adset_id: [dong ad, ...]} — sap xep chi tieu giam dan."""
```

Sắp xếp giảm dần để quảng cáo chi nhiều nhất được xét trước (đề xuất đáng chú ý nhất lên đầu).

### 5.5. Luật trong `agent_muc_tieu.py`

Thêm hàm thuần **`xet_mot_quang_cao(dong_ad, bay_gio)`** — trả về `(truong_hop, ly_do, uu_tien)`
hoặc `None` nếu chưa chạm ngưỡng. **Dùng CHUNG một hàm** cho cả nhóm lẫn quảng cáo:

```python
def _xet_nguong(chi_hom_nay, chi_thang, mua_thang, tin_nhan):
    """Dung CHUNG cho cap nhom va cap quang cao.
    Tra ve (truong_hop, ly_do, uu_tien, chi_phi_moi_luot) hoac None."""
```

Điều này bảo đảm **quảng cáo không thể lệch luật so với nhóm** — cùng một đoạn code.

### 5.6. Sửa `xet()` — thêm tham số quảng cáo

```python
def xet(nhom, chi_tieu_hom_nay=None, chi_tieu_thang=None, loai_ten=None,
        bay_gio=None, ad_hom_nay=None, ad_thang=None):
```

Luồng trong `xet()` cho mỗi nhóm:

```
1. Tính so NHÓM (như hiện nay)            -> ket_qua_nhom
2. Lay danh sach AD cua nhom, tinh so AD  -> danh_sach_ket_qua_ad
3. co_ad_chua_ket_qua = co ad nao luot_mua==0 VA tin_nhan==0 khong?

4. NEU co_ad_chua_ket_qua:
       A. Duyet tung AD truoc -> ad nao cham nguong thi TAT RIENG ad do
       B. Roi xet NHOM -> cham nguong thi TAT CA NHOM (keo theo tat het ad)
   NGUOC LAI:
       A. Xet NHOM truoc -> cham nguong thi TAT CA NHOM
       B. Neu nhom CHUA cham -> duyet tung AD -> cham thi TAT RIENG

5. NEU TONG chi tieu ca nhom cham nguong (theo luat nhom)
       -> LUON TAT CA NHOM, huy moi de xuat tat le ad
```

⚠️ **Bước 5 là điều kiện Đại nêu nguyên văn** (qc1 200k + qc2 90k = 290k ⇒ tắt cả nhóm). Phải kiểm
**TRƯỚC** khi trả về đề xuất tắt lẻ, vì nhóm "đã có kết quả" mới tính tổng — và tổng có thể chạm
ngưỡng dù từng ad chưa chạm.

### 5.7. Định dạng đề xuất tắt lẻ quảng cáo

Giữ **nguyên cấu trúc** của đề xuất cấp nhóm, chỉ đổi `cap`:

```python
{
    "hanh_dong": "tam_dung",
    "cap": "ad",                          # <-- DIEM KHAC BIET
    "truong_hop": 2,
    "doi_tuong": {
        "cap": "ad",
        "id": <ad_id>,
        "ten": <ad_name>,
        "adset_id": <nhóm chứa nó>,        # <-- can de biet nhom nao
        "campaign_id": ...,
    },
    "ten_moi": <ten_ad_moi>,              # dung hau to cua NHOM
    "ngan_sach_ha": None,                 # <-- KHONG ha ngan sach
    ...
}
```

⚠️ `ngan_sach_ha = None` là **cách nói "không hạ ngân sách"**. Nhưng `agent_rao.kiem` hiện đang
**BẮT BUỘC** `ngan_sach_ha == 27000` ⇒ **phải sửa rào** (xem 5.9).

### 5.8. Tên quảng cáo mới

Quảng cáo **dùng chung hậu tố với nhóm chứa nó**. Ví dụ nhóm bị tắt ở TH2 ⇒ tên nhóm
`... Online 0/350 X10 26 TN` ⇒ quảng cáo tắt riêng trong nhóm đó cũng mang hậu tố
`... 0/350 X10 26 TN`.

⚠️ **Rủi ro:** tên quảng cáo do Meta tự sinh, **không nhất quán** (nhiều cái tên
`Quảng cáo Mức độ nhận biết mới`, hoặc tên rỗng). Đổi tên quảng cáo là **thay đổi mới hoàn toàn**
— chưa từng chạy thật. Phải thử ở chế độ tập sự trước.

### 5.9. Sửa `agent_rao.py` — rào an toàn

Đây là **file quan trọng nhất**, không được nới lỏng bừa:

| Rào | Hiện tại | Cần sửa thành |
|---|---|---|
| Rào 2 — hành động cho phép | `("tam_dung", "bat_lai")` | giữ nguyên |
| Rào danh sách | `thuoc_pham_vi(ten)` | **adset rỗng tên** ⇒ phải kiểm theo **TÊN NHÓM** chứa nó |
| Rào 4 — `ngan_sach_ha` | **bắt buộc == 27.000** | **nếu `cap == "ad"` thì `ngan_sach_ha` PHẢI là `None`**; nếu `cap == "ad_set"` thì giữ nguyên == 27.000 |
| Rào 3 — nhóm đang hiệu quả | kiểm `MOC_CPR` | giữ nguyên, áp cho cả hai cấp |
| Rào 8/`bo_qua` | khoá theo `doi_tuong.id` | **giữ nguyên** — quảng cáo có id riêng |

⚠️ **Rào "quảng cáo không hạ ngân sách" viết theo chiều NGƯỢC** (cấp `ad` ⇒ **bắt buộc** `None`) —
để một đề xuất tắt ad lỡ mang `ngan_sach_ha=27000` thì **bị chặn**, chứ không âm thầm hạ ngân sách
quảng cáo.

### 5.10. Sửa `agent_cong_cu_ghi.py` — tắt CHỌN LỌC

`tat_quang_cao(env, ma_nhom, ten_nhom=None)` hiện **tắt HẾT** ad. Viết thêm hàm mới, **giữ hàm cũ**
để không vỡ chỗ gọi:

```python
def tat_mot_quang_cao(env, ma_ad, ten_nhom=None, ten_moi=None, ngu_fn=None):
    """Tat MOT quang cao + (tuy chon) doi ten. KHONG dung ngan sach."""
```

⚠️ **Rào phạm vi:** giống `tat_quang_cao` — đọc lại **tên NHÓM chứa ad** rồi kiểm `thuoc_pham_vi`.
**KHÔNG** kiểm tên quảng cáo (Meta tự sinh, không có `dainq`).

⚠️ **Mỗi lần ghi cách nhau `CHO_GIUA_HAI_LAN_GHI` = 20 giây.** Tắt 5 quảng cáo = 100 giây. Phải
tính vào thời gian chạy.

⚠️ **Gộp `status` + `name` vào MỘT lệnh gọi** — đã kiểm chứng Meta nhận cả hai cùng lúc.

### 5.11. Sửa `agent.py`

`_lam_theo_dong_y` hiện giả định **mọi** đề xuất là cấp nhóm. Cần phân nhánh theo
`ban_ghi["doi_tuong"]["cap"]`:

```python
cap = (ban_ghi.get("doi_tuong") or {}).get("cap")
if cap == "ad":
    -> tat_mot_quang_cao(...)         # KHONG ha ngan sach, khong dung toi adset
else:
    -> tam_dung_va_ha_ngan_sach(...)  # nhu hien nay
```

⚠️ Phần **tắt nhóm xong thì tắt hết quảng cáo bên trong** phải **GIỮ NGUYÊN** — đó là ý Đại
(*"khi tắt nhóm thì tắt luôn quảng cáo bên trong"*, 01/10). Chỉ **thêm** nhánh cấp quảng cáo.

### 5.12. Nút Telegram cho đề xuất cấp quảng cáo

Đại chốt: tắt quảng cáo **không hạ ngân sách** ⇒ tin xin phép cho cấp quảng cáo **chỉ có 2 nút**:

```
[ ⏸ TẮT QUẢNG CÁO NÀY ]
[ ⏭ Bỏ qua ]
```

⚠️ **Không có nút "hạ ngân sách"** — vì hạ ngân sách quảng cáo là việc **không tồn tại** theo luật Đại.
Hiện một nút không làm gì được chỉ gây bấm nhầm.

⚠️ `callback_data` dùng `tat:<ad_id>` / `boqua:<ad_id>` — **giống hệt cấp nhóm**, vì mã quảng cáo và
mã nhóm đều là dãy số dài. `doc_tra_loi` không cần sửa.

⚠️ Vẫn cần hàm `soan_tin` riêng biết nói **"XIN PHÉP TẮT QUẢNG CÁO"** thay vì **"XIN PHÉP TẮT NHÓM"**,
và hiện **tên nhóm chứa nó** để Đại biết nó nằm đâu.

---

## 6. Kiểm thử phải có

| Việc | Bài kiểm thử |
|---|---|
| A | `ten_moi` TH1/TH2/TH3 đều **kèm năm**: `0/140 X10-26`, `0/350 X10-26 TN`, `1/450 X10-26` |
| A | ` TN` đứng **SAU** năm, không phải trước |
| A | `RE_HAU_TO` cắt được **cả 5 dạng**: `X10`, `X8-26 TN`, `X10-26`, `X10-26 TN`, `X11 => Lỗi` |
| A | **KHÔNG** dùng khoảng trắng trước năm (`X10 26` là SAI) |
| A | Năm **động** — sang 2027 ra `-27`, không viết cứng `26` |
| A | **Tắt lần hai KHÔNG chồng tên** — chạy `ten_moi` hai lần ra **cùng một chuỗi** |
| A | Đổi trường hợp (TH1→TH2, TH3→TH2) vẫn cắt sạch hậu tố cũ |
| A | `RE_HAU_TO` mới cắt **237/237** tên nhóm thật đọc từ Meta |
| A | `truong_hop` ngoài 1/2/3 ⇒ **NÉM LỖI**, không âm thầm ra TH3 |
| A | `KHÔNG` cắt quá tay — mã content `120825` / `160825` ở đuôi tên phải giữ nguyên |
| **Phạm vi** | **Tên QUẢNG CÁO luôn NGOÀI phạm vi** — kể cả sau khi gắn hậu tố |
| **Phạm vi** | **7 kiểu tên nhóm Truong thật** (đọc từ Meta) **luôn ngoài phạm vi** |
| **Phạm vi** | Nhóm của Đại **không bị chặn quá tay** (kiểm cả `dainq`, `new - dainq`, mã content) |
| **Phạm vi** | `tat_quang_cao` trên nhóm Truong ⇒ **POST lên Meta = 0** (cả tắt-hết lẫn tắt-chọn-lọc) |
| **Phạm vi** | Tắt chọn lọc ad của Truong ⇒ **KHÔNG được đổi tên** ad đó |
| B | `doc_chi_tieu_quang_cao` trả `{ad_id: dong}`, bỏ dòng thiếu `ad_id` |
| B | `gom_theo_nhom` gom đúng + sắp chi tiêu **giảm dần** |
| B | Quảng cáo **chưa có kết quả** + chi 70.000đ ⇒ **chạm ngưỡng** |
| B | Quảng cáo **chưa có kết quả** + chi 69.999đ ⇒ **chưa chạm** |
| B | Quảng cáo có tin nhắn + chi 290.000đ ⇒ chạm; 289.999đ ⇒ chưa |
| B | Quảng cáo CPR tháng 390.000đ ⇒ chạm; 389.999đ ⇒ chưa |
| B | **qc2 chưa có kết quả** ⇒ xét ad TRƯỚC, qc1 chạm ngưỡng ⇒ tắt riêng qc1 |
| B | Mọi ad **đã có kết quả** ⇒ xét NHÓM trước |
| B | **Ca của Đại:** qc1 200.000đ/1 tin + qc2 90.000đ/1 tin = **290.000đ** ⇒ **tắt CẢ NHÓM**, **KHÔNG** có đề xuất tắt lẻ |
| B | Tắt lẻ ad ⇒ `ngan_sach_ha` là **None** |
| B | 🔴 **Ad của nhóm Truong KHÔNG BAO GIỜ được sinh đề xuất** — xét cả nhóm lẫn ad |
| Rao | Đề xuất cấp `ad` mà `ngan_sach_ha == 27000` ⇒ **BỊ CHẶN** |
| Rao | Đề xuất cấp `ad_set` mà `ngan_sach_ha == None` ⇒ **BỊ CHẶN** |
| Rao | Nhóm ngoài phạm vi ⇒ **không** tắt quảng cáo bên trong |
| Ghi | `tat_mot_quang_cao` gửi **ĐÚNG MỘT** lệnh, có cả `status` lẫn `name` |
| Ghi | `tat_mot_quang_cao` **KHÔNG** gửi `daily_budget` |
| Ghi | 🔴 `tat_mot_quang_cao` **đọc lại TÊN NHÓM chứa ad** rồi kiểm phạm vi — **KHÔNG** kiểm tên ad |
| Ghi | `chi_tat=[id]` ⇒ chỉ tắt **đúng ad đó**, ad còn lại **giữ nguyên ACTIVE** |
| Ghi | `chi_tat=None` ⇒ tắt **hết** (giữ hành vi cũ khi tắt cả nhóm) |
| Ghi | `chi_tat=[]` ⇒ **không tắt gì** |
| Ghi | Tên mới rỗng ⇒ **KHÔNG gửi trường `name`**, nhưng **vẫn tắt được** |
| Ghi | Có **nghỉ 20 giây** giữa hai lần ghi Meta |
| Ghi | Ad đã `PAUSED` sẵn ⇒ **không POST lại** |
| Agent | `cap == "ad"` ⇒ gọi `tat_mot_quang_cao`, **KHÔNG** gọi `tam_dung_va_ha_ngan_sach` |
| Nút | Tin cấp quảng cáo có **2 nút** (không có nút hạ ngân sách) |

---

## 7. Thứ tự thi công

1. **Việc A trước** — nhỏ, độc lập, đang gây lỗi thật (tên thiếu năm). Sửa + chạy toàn bộ kiểm thử.
2. **Việc B** — lớn hơn, chia làm 3 chặng:
   - B1: đọc `level=ad` (chỉ ĐỌC, không đổi hành vi) → chạy tập sự vài ngày xem số có khớp không.
   - B2: luật xét + rào an toàn (vẫn tập sự).
   - B3: ghi Meta (`tat_mot_quang_cao`) + nút Telegram.
3. **Dựng thử toàn bộ ngoài repo trước khi sửa code thật** — theo quy trình đã chốt.

### 7.1. Tiến độ thực tế (cập nhật 02/10/2026, 15:5x)

| Bước | Trạng thái |
|---|---|
| Đọc bản thiết kế + code thật | ✅ xong |
| Viết kế hoạch riêng (file này) | ✅ xong |
| **Dựng thử Việc A ở `.workbuddy-ai/dung-thu/hau-to-thang-nam/`** | ✅ **xong — 63/63 đạt** |
| **Tấn công tìm lỗi** | ✅ **xong — bắt 3 lỗi thật, đã sửa** |
| **Kiểm điều kiện tiên quyết** (`truong_hop`, `RE_HAU_TO` trên tên thật) | ✅ **xong — 237/237 tên cắt đúng** |
| **Kiểm rào PHẠM VI trên 4200 nhóm thật (phát hiện của Đại)** | ✅ **xong — siết về đúng `dainq`** |
| **Đại duyệt** | ✅ **duyệt 15:3x 02/10/2026** |
| **Chép Việc A vào repo thật** | ✅ **xong — commit `0147c3d`** |
| **Chạy toàn bộ kiểm thử repo** | ✅ **xong — 726/726 đạt** |
| **`git commit` Việc A** | ✅ **xong** |
| **Dựng thử Việc B (B1+B2+B3)** | ✅ **xong 46/46 đạt — bắt 2 lỗi thật** |
| **Đại duyệt luật chốt cuối (15:5x)** | ✅ **duyệt: ≥2 quảng cáo mới tắt lẻ** |
| Chép Việc B vào repo thật | ⬜ |
| Chạy tập sự ≥3 ngày rồi mới bật thật | ⬜ |

**Bằng chứng dựng thử Việc A:** `.workbuddy-ai/dung-thu/hau-to-thang-nam/LOI-DA-BAT-DUOC.md`
**Bằng chứng dựng thử Việc B:** `.workbuddy-ai/dung-thu/xet-tung-quang-cao/LOI-DA-BAT-DUOC.md`

### 7.2. 🔴 ĐO LẠI CẤU TRÚC QUẢNG CÁO THẬT — 15:5x 02/10/2026

Đo để biết **có ca thật nào để kiểm chứng Việc B không** — và phát hiện luật bị vỡ:

| | |
|---|---|
| Nhóm đang ACTIVE | **93** |
| Trong phạm vi của Đại (có `dainq`) | **82** |
| — có **0** quảng cáo | **66** |
| — có **1** quảng cáo | **16** |
| — có **≥2** quảng cáo | **0** |

⚠️ **Cả 16 nhóm một-quảng-cáo đều có: chi tiêu ad = chi tiêu nhóm, ĐÚNG 100,0%.**

| Nhóm | Chi nhóm | Chi ad | ad/nhóm | Lượt mua | Tin nhắn |
|---|---|---|---|---|---|
| `120250213748540509` | 779.615đ | 779.615đ | 100,0% | 5 | 19 |
| `120250080111780509` | 648.122đ | 648.122đ | 100,0% | 3 | 14 |
| `120249911752740509` | 575.700đ | 575.700đ | 100,0% | 3 | 14 |
| `120250263934130509` | 560.416đ | 560.416đ | 100,0% | 2 | 17 |
| `120250574692000509` | 442.375đ | 442.375đ | 100,0% | 2 | 8 |
| … 11 nhóm còn lại | | | 100,0% | | |

Số này **buộc phải đúng**: nhóm có một quảng cáo thì tổng của nó bằng chính nó.
⇒ Đây là **bằng chứng** cho thấy luật "tắt lẻ rồi lần sau tắt nhóm" **không hoạt động được**
ở nhóm một quảng cáo (xem mục 2.4).

⚠️ **HỆ QUẢ — phải nói rõ:** Việc B **hôm nay chưa có ca thật nào của Đại để kiểm chứng**
nhánh "tắt lẻ". Luật được viết để **sẵn sàng**, không phải để sửa ca đang cháy.
Đại chốt vẫn làm luôn: *"Cứ làm luôn như đã thống nhất để còn theo dõi trong những ngày tới"*.

⇒ Vì không có ca thật, **kiểm thử phải dựng bằng số liệu GIẢ**, và **2 nhóm Truong ở trên dùng làm
mẫu cấu trúc** (đúng 2 ad, 1 ad có kết quả + 1 ad chưa) — **chỉ dùng để kiểm rằng hệ thống CHẶN,
tuyệt đối không dùng làm ca hợp lệ**.

### 7.3. ✅ KIỂM CHỨNG THÊM QUY TẮC SẮT — bằng số thật

| Câu hỏi | Kết quả đo |
|---|---|
| Tên **quảng cáo** có `dainq` không? | **44/55 có** — 11 cái KHÔNG (vd `Quảng cáo Mức độ nhận biết mới`) |
| Ad thuộc nhóm **của Đại** mà tên **không** có `dainq` | **0** |

⇒ Chứng minh **tên quảng cáo KHÔNG đáng tin** (11/55 sai) ⇒ **bắt buộc** kiểm theo tên nhóm.
Và may là trong nhóm của Đại hiện tên ad đều có `dainq` — nhưng **không được dựa vào đó**, vì Truong
đổi tên lúc nào không biết.

### 7.4. Đo `level=ad` — bổ sung 15:4x 02/10/2026

| | |
|---|---|
| Trường trả về | `ad_id`, `ad_name`, `adset_id`, `adset_name`, `campaign_id`, `spend`, `actions` ✅ |
| Một lệnh cho **cả tài khoản** | ✅ — 46 dòng `today`, 55 dòng `this_month`, **không phân trang** |
| `spend` kiểu dữ liệu | **CHUỖI** (`'29260'`) — đúng như bẫy đã ghi |
| Tổng tiền cấp ad vs cấp adset | **53/53 nhóm KHỚP, lệch 0đ** ✅ |
| Nhóm có >1 ad | 2 — **đều của Truong, đều ngoài phạm vi** |

---

## 8. Rủi ro

| Rủi ro | Mức | Xử lý |
|---|---|---|
| `RE_HAU_TO` mới cắt **quá tay** tên thật (mất chữ cuối tên) | **Cao** | ✅ **Đã đo thật: 237/237 tên nhóm cắt đúng.** Cộng bài hồi quy trên tên thật |
| Hậu tố `X10-26` **bị chồng** khi tắt lần hai | **Cao** | ✅ Có bài "tắt hai lần không chồng" cho **cả 3** trường hợp + đổi trường hợp |
| Tên có đuôi `=> Lỗi` **không cắt được** | **Cao** | ✅ **Đã bắt được ở dựng thử** — có 2 nhóm thật; đã sửa + có bài hồi quy |
| Sửa lỗi `=> Lỗi` xong lại **nuốt mất mã content** | **Cao** | ✅ Có bài hai chiều: cắt được `=> Lỗi` **và** giữ được `120825` |
| `truong_hop` lạ **âm thầm** ra TH3 | Trung bình | ✅ Đã kiểm: không nơi nào truyền giá trị lạ ⇒ an toàn thêm `raise` |
| Đổi chữ ký trả về `doc_so` (3→5 phần tử) làm vỡ chỗ gọi | Trung bình | Chạy **toàn bộ** bộ kiểm thử; grep hết chỗ gọi `doc_so` |
| Đọc thêm `level=ad` ⇒ thêm 2 lệnh gọi/vòng | Thấp | Đã đo: 1 lệnh cho cả tài khoản; 15 phút ⇒ 0,7% hạn mức/giờ |
| Tắt nhiều ad ⇒ **chạm mã 613** (1 ghi/30 giây) | **Cao** | Giữ `CHO_GIUA_HAI_LAN_GHI` = 20 giây; tắt 5 ad = 100 giây |
| Đổi tên quảng cáo — **chưa từng chạy thật** | **Cao** | Chạy tập sự trước; nếu Meta từ chối thì báo lỗi chứ không tắt nửa vời |
| Tên quảng cáo rỗng / trùng nhau | Trung bình | `bo_hau_to_cu` trả `""` ⇒ **không gửi trường `name`** nếu tên gốc rỗng |
| **Tên quảng cáo Meta tự sinh vẫn bị ghép hậu tố** (vd `Quảng cáo Mức độ nhận biết mới 0/350 X10-26 TN`) | Trung bình | Đúng thiết kế — tên gốc còn nguyên. Nhưng dài/dễ lẫn ⇒ **Đại xem ở chế độ tập sự rồi quyết** |
| 🔴 **Kiểm phạm vi nhầm theo TÊN QUẢNG CÁO** | **Rất cao** | Đại phát hiện 15:1x 02/10. Tài khoản **CÓ 64 nhóm của Truong**, ad tên Meta tự sinh **không có `dainq`**. ⇒ **Quy tắc sắt ở mục 0.4**: luôn kiểm theo **TÊN NHÓM**. Đã khóa bằng `kiem_thu_pham_vi.py` (5 bài) + `kiem_thu_ghi.py` lớp D (4 bài) |
| Tên nhóm Truong **vô tình thuộc phạm vi** (chứa `dainq`/mã content) | Thấp | Đo thật: 0/64 nhóm Truong lọt. Nhưng vẫn nên rà lại mỗi khi thêm luật phạm vi |
| Nhóm nhiều ad nhưng **chỉ 1 ad có chi tiêu** | Thấp | Ad không có dòng insights ⇒ **không xét** (không có số) |

---

## 9. Điều CHƯA biết — phải thử mới biết

1. **Meta có cho đổi TÊN quảng cáo không?** Chưa từng gọi. Khoá Meta có thể chỉ đủ quyền `status`.
   ⇒ Thử ở chế độ tập sự, **không** thử thẳng trên tài khoản thật đang chạy.
2. **`level=ad` lúc 8h sáng** — số dòng có thể nhiều hơn 46 (đo lúc 14h). Cần đo lại giờ cao điểm
   xem có phân trang không.
3. ~~Đại muốn tên quảng cáo mới thế nào?~~ ✅ **ĐÃ CHỐT 02/10/2026:** quảng cáo **dùng chung hậu tố
   với nhóm chứa nó** (`... 0/350 X10-26 TN`).
4. **MỚI — tên quảng cáo Meta tự sinh nên ghép hậu tố ra tên rất dài.** Ví dụ
   `Quảng cáo Mức độ nhận biết mới 0/350 X10-26 TN`. Cần Đại xem thực tế và quyết có giữ cách này
   không, hay chỉ tắt mà **không đổi tên** quảng cáo.
