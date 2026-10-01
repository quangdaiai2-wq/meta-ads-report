# HƯỚNG DẪN MÁY NHÀ — CẬP NHẬT NGÀY 01/10/2026 (luật tắt nhóm mới)

**Dành cho:** Đại (người không cần biết code) **và** trợ lý AI trên máy nhà.

> **Nếu bạn là trợ lý AI đang đọc file này:** máy công ty vừa đẩy một bản cập nhật **thay đổi luật
> tắt nhóm hoàn toàn**. Đọc hết trước khi làm. Máy nhà chạy code cũ sẽ **tắt oan rất nhiều nhóm**.

**Ngày máy công ty cài đặt:** 14/09/2026. Kho GitHub: `meta-ads-report`, nhánh `main`.
**Mốc mới nhất đã đẩy:** **`bca174c`** (01/10/2026).

---

## 🆕 CẬP NHẬT NGÀY 01/10/2026 — ĐỌC PHẦN NÀY TRƯỚC

### ⚠️ Vì sao bản này QUAN TRỌNG hơn các bản trước

Luật tắt nhóm **đã đổi hoàn toàn**. Nếu máy nhà còn chạy code cũ:

| | Code cũ (đang có ở máy nhà) | Luật mới |
|---|---|---|
| Nhóm có tin nhắn, chưa ra đơn | tắt khi chi **70.000đ** | tắt khi chi **290.000đ** |
| Nhóm không có tin nhắn | tắt khi chi **80.000đ** | tắt khi chi **70.000đ** |
| Nhóm đã có đơn | giá mỗi đơn ≥ **400.000đ** | giá mỗi đơn ≥ **390.000đ** |
| Đếm tin nhắn | **chỉ 1** chỉ số | **cả 2** chỉ số |
| Khi tắt | tắt nhóm + hạ ngân sách | tắt **quảng cáo** + tắt nhóm + hạ ngân sách + **đổi tên** |

⇒ **Code cũ sẽ tắt oan** những nhóm mới chi 70.000đ mà đã có tin nhắn. Phải cập nhật.

### Máy nhà cần làm — 4 bước

**Bước 1 — Kéo code mới:**
```
git pull
```
Phải thấy mốc **`bca174c`**. Nếu chưa thấy, gõ `git log --oneline -1` để kiểm.

**Bước 2 — Sửa `.env` (`.env` KHÔNG đi theo `git pull`):**
Bấm `mo-file-env.bat`, tìm dòng `AGENT_TOI_DA_NGAY=3` và đổi thành:
```
AGENT_TOI_DA_NGAY=0
```
`0` nghĩa là **KHÔNG GIỚI HẠN** — agent được hỏi Đại về mọi nhóm chạm ngưỡng, không bị im lặng
sau 3 nhóm như trước. Nếu máy nhà **chưa có** dòng này thì thêm vào, thiếu cũng chạy.

**Bước 3 — Khởi động lại agent** (bắt buộc — đây là **đổi code**, không phải chỉ đổi `.env`):
Bấm `khoi-dong-lai-agent.bat`.

**Bước 4 — Kiểm chứng:**
Mở `logs\baocao.log`, tìm dòng mới nhất có dạng:
```
AGENT: N nhom cham nguong — hoi X, bo qua Y (dang cho Dai tra loi), chan Z (rao an toan)
```
Dòng này **mới có từ hôm nay**. Thấy nó là code mới đã chạy. Từ nay **mỗi lần quét đều ghi dòng này**,
nên nhìn vào là biết agent có làm việc hay không — không còn cảnh im lặng mà không rõ vì sao.

### Những gì đã sửa trong bản này

1. **Luật tắt nhóm mới** — ba trường hợp TH1/TH2/TH3 (bảng trên).
2. **Tắt quảng cáo + đổi tên nhóm** — agent nay làm đủ 4 việc như Đại vẫn làm tay.
3. **Bỏ trần đề xuất** — trước đây hết 3 nhóm/ngày là agent **im lặng hoàn toàn**, kể cả khi tìm ra
   nhóm cần tắt. Nay không giới hạn, và mọi lý do dừng đều được ghi log.
4. **Sửa phép so sánh của báo cáo** — trước đây so 1 ngày với 7 ngày nên cột chênh lệch luôn ra −80%.
   Nay so **ngày hôm qua với ngày hôm trước**.
5. **Thêm dòng "chi phí mỗi đơn" vào bảng so sánh** — đây là thủ phạm chính làm phần nhận định luôn
   viết tiêu cực. Trước đây mọi dòng khác đều giảm nên AI kết luận "kém hiệu quả", trong khi chi phí
   mỗi đơn lại rẻ đi.
6. **Chờ lâu hơn khi Meta chặn** — Meta giới hạn ghi ~1 lần/30 giây; code cũ chờ 5–15 giây, không đủ.

### ⚠️ Một điều máy nhà cần biết về token

Token Meta của máy nhà hết hạn **10/11/2026** (máy công ty **** — hai máy khác ngày).
Và từ 30/09/2026 token **đã có quyền GHI** (`ads_management`), nên agent **tắt nhóm thật** được.
Kiểm tra token còn sống hay không: nhắn bot chữ `token`.

---

## 📅 CẬP NHẬT NGÀY 29/09/2026 — nếu máy nhà CHƯA làm bản này

Nếu máy nhà đã làm xong bản 28/09 (Giai đoạn 2) thì chỉ còn **BA bước nhỏ**:

1. **`git pull`** → nhận Giai đoạn 3 + 4 + 5.
2. **Thêm `GEMINI_API_KEY` vào `.env`** — chìa khoá AI, lấy theo `HUONG-DAN-LAY-CHIA-KHOA-AI.md`
   (khoảng 5 phút, có bản miễn phí). **Không có chìa khoá thì báo cáo vẫn gửi đầy đủ**, chỉ thiếu
   mục NHẬN ĐỊNH và bot không trả lời được câu hỏi về số liệu.
3. **Nhắn thử bot một chữ `token`** để xác nhận (xem mục "Hai lệnh nhanh" bên dưới).

**Không phải bấm lại `cai-dat-nguoi-truc.bat`**, không phải sửa gì khác.

### Có gì mới kể từ bản 28/09

| Giai đoạn | Có gì mới |
|---|---|
| **3** | Mục `🔵 NHẬN ĐỊNH` trong báo cáo nay do AI viết 3–5 câu, có so sánh với kỳ trước (chỉ ở mốc 8h) |
| **4** | **Nhắn bot hỏi được số liệu** bằng tiếng Việt: *"camp nào tệ nhất tuần này?"* → bot trả lời có số thật |
| **5** | **Tự xử lý lỗi**: Meta chặn tạm thì tự chờ rồi thử lại; token chết thì không thử lại vô ích; số liệu trông sai thì cảnh báo; cùng một lỗi chỉ nhắn **một tin** thay vì 9 tin mỗi ngày |

### Hai lệnh nhanh mới — **không tốn lượt AI**

| Nhắn cho bot | Bot trả lời |
|---|---|
| `còn sống không?` | Máy nào, đã chạy bao lâu, hôm nay đã gửi mốc nào |
| `token` | Token Meta còn sống bao nhiêu ngày, hết hạn ngày nào, cần làm gì |

### ⛔ Điều quan trọng nhất về token — đã kiểm chứng

**Hệ thống KHÔNG tự gia hạn token được. Meta không cho.** Máy công ty đã thử thật ngày 29/09/2026:
Meta trả về token mới nhưng **giữ nguyên ngày hết hạn cũ** (lệch **+0 giây**, thử hai lần đều vậy).

⇒ **Vẫn phải làm tay mỗi 60 ngày.** Nhưng hệ thống nay nhắc **hai mức** cho bạn:
- Còn dưới **30 ngày** → nhắc nhẹ một lần mỗi ngày ở báo cáo buổi sáng
- Còn dưới **7 ngày** → nhắc ở **mọi** báo cáo

Và bạn chủ động kiểm được bất cứ lúc nào bằng cách nhắn chữ `token`.

> 🔎 Có **một hướng chưa thử**: token "System User" trong Business Manager có tuỳ chọn không hết hạn.
> **Chưa ai thử, chưa hứa gì.** Ghi lại đây để lúc nào rảnh thì nghiên cứu.

### Token máy nhà hết hạn ngày nào?

| Máy | Token hết hạn |
|---|---|
| **Máy nhà** | **10/11/2026** |
| Máy công ty |  |

---

## ⚠️ CẬP NHẬT NGÀY 28/09/2026 — nếu máy nhà CHƯA làm bản này

Bản 28/09 sửa hai lỗi đang chạy thật. Bản 28/09 (Giai đoạn 2) thay **cách hệ thống chạy**:
không còn ba lịch Windows rời rạc mà là **một tiến trình thường trú**. Vì vậy máy nhà **PHẢI
chạy lại `cai-dat-nguoi-truc.bat`**.

**BỐN bước, theo đúng thứ tự:**

1. **`git pull`** tại thư mục dự án → nhận code mới.
2. **Thêm một dòng vào `.env`** (làm ở bước 2b bên dưới). **Đây là bước MỚI, bắt buộc** — bỏ qua
   thì mốc 22h quay trở lại máy nhà.
3. **Bấm đúp `cai-dat-nguoi-truc.bat`.** Nếu báo lỗi quyền thì chuột phải → Run as administrator.
   File này tạo **một** lịch duy nhất tên `NguoiTruc`, **xoá ba lịch cũ**, và **khởi động
   Người trực ngay**. Phải chạy bước này, vì lịch cũ không biết gì về nhau nên vẫn còn hai lỗi:
   báo cáo trùng, và mốc 8h chạy bù sai.
4. **Kiểm tra kết quả.** File in ra phần đọc lại lịch:

   ```
   Ten lich    : NguoiTruc
   Trang thai  : Running
   Tham so     : "D:\...\nguoi_truc.py"
   So trigger  : 2
   Tien trinh   : dang chay (PID ...)
   ```

   **Ba dòng phải đúng:**
   - `Tham so` phải **kết thúc bằng `nguoi_truc.py"`** (có dấu nháy đóng). Thiếu dấu nháy đó thì
     đường dẫn có khoảng trắng bị Windows cắt làm hai, lịch không chạy được.
   - `So trigger` phải là **`2`** — một cái chạy khi đăng nhập, một cái lặp mỗi 5 phút để tự bật
     lại nếu tiến trình chết.
   - `Trang thai` phải là `Running` và có dòng `Tien trinh: dang chay`.

### Bước 2b — Thêm dòng `REPORT_SLOTS` vào `.env` (BẮT BUỘC)

`.env` là file riêng của từng máy, **không** nằm trên GitHub, nên `git pull` **không** mang dòng
này sang máy nhà. Phải tự thêm.

**Cách làm:**

1. Mở **Notepad**
2. Kéo file `.env` trong thư mục dự án thả vào cửa sổ Notepad (hoặc File → Open → chọn `.env`)
3. Xuống **cuối file**, thêm một dòng mới:

```
REPORT_SLOTS=8,12,17
```

4. Bấm **Ctrl + S**, rồi đóng Notepad

**Kiểm tra lại** — mở cửa sổ lệnh tại thư mục dự án, dán dòng này:

```powershell
python -c "import report; print(report.doc_moc_tu_env(report.load_env('.env')))"
```

Nếu báo lỗi `python is not recognized`, dùng đường dẫn đầy đủ (đường dẫn Python trên máy nhà
có thể khác máy công ty — xem lại mục cài Python ở đầu file này):

```powershell
& "C:\Users\nguye\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe" -c "import report; print(report.doc_moc_tu_env(report.load_env('.env')))"
```

Kết quả phải in ra **`[8, 12, 17]`**. Nếu in ra `[8, 12, 17, 22]` thì dòng vừa thêm bị sai chính tả
(phải đúng `REPORT_SLOTS`, chữ in hoa, không có dấu cách quanh dấu `=`).

**Một điều cần biết trước khi bấm bước 3:**

- **Cả hai máy dùng chung ba mốc 8h, 12h, 17h.** Đại đã chốt bỏ mốc 22h ở cả hai máy ngày
  28/09/2026. Nếu thiếu dòng `REPORT_SLOTS` trong `.env`, hệ thống dùng mặc định `8,12,17,22`
  — tức **mốc 22h quay trở lại**.
- **Không cần tính năng "tự thức máy" nữa.** Người trực chạy suốt khi máy bật; máy tắt thì
  không có báo cáo, nhưng khi bật lại nó gửi bù đúng **một** báo cáo cho mốc gần nhất bị lỡ.
- **Sau khi bấm file xong hãy nhắn thử bot** câu `còn sống không?`. Phải nhắn **sau**, vì Người
  trực bỏ qua mọi tin nhắn đến trước lúc nó khởi động — nhắn trước là mất tin, không phải lỗi.

---

## PHẦN 1 — VIỆC MÁY NHÀ CẦN LÀM (bản 14/09 — nay đã cũ)

### Bước 1: Cập nhật code

Mở cửa sổ lệnh **tại đúng thư mục dự án** rồi chạy:

```powershell
git pull
```

**Kết quả mong đợi:** thấy danh sách file thay đổi, trong đó có `report.py`, `nguoi_truc.py`,
`cai-dat-nguoi-truc.bat` và `tests/test_nguoi_truc.py`.

> ⚠️ **Câu dưới đây đúng cho bản 14/09, KHÔNG đúng cho bản 28/09.**
> Bản 28/09 (Giai đoạn 2) đổi **cách hệ thống chạy**, nên máy nhà **phải** bấm
> `cai-dat-nguoi-truc.bat`. Chỉ `git pull` là **chưa đủ** — xem mục "CẬP NHẬT NGÀY 28/09/2026"
> ở đầu file.

### Bước 2: Kiểm tra token của máy nhà

```powershell
python kiem-tra-token.py
```

Lệnh này cho biết token máy nhà **còn sống bao lâu** — điều mà `test_meta.py` không làm được.

> ⚠️ **Quan trọng:** nếu nó báo token chỉ còn **vài giờ**, nghĩa là token máy nhà cũng đang là
> loại ngắn hạn. Phải chạy ngay `python doi-token-60-ngay.py` rồi kiểm lại.
>
> Ngày 14/09, token máy công ty đã suýt chết vì đúng lý do này: nó chỉ còn sống 1 giờ 44 phút
> mà mọi bài kiểm tra đều báo ĐẠT.

---

## PHẦN 2 — CÓ GÌ MỚI TRONG 3 BẢN CẬP NHẬT

| # | Thay đổi | Vì sao |
|---|---|---|
| 1 | `report.py` chỉ gọi Meta API **1 lần** thay vì 2 | Trước đây mỗi lần chạy tốn gấp đôi hạn mức gọi Meta, và số liệu trên tin nhắn Telegram có thể **lệch** với file HTML đính kèm. Nay hai đầu ra luôn khớp nhau. |
| 2 | Thêm file **`kiem-tra-token.py`** | Kiểm cả 2 nhóm token và cho biết token Meta còn sống bao lâu. Chạy sau mỗi lần lấy token mới. |
| 3 | **Cảnh báo trước khi token hết hạn** | Trước đây hệ thống chỉ báo **sau khi** token đã chết. Nay nếu token còn dưới **7 ngày**, mỗi báo cáo sẽ kèm một dòng cảnh báo vàng ở đầu tin nhắn. |

Xem chi tiết từng bản: `git log --oneline -5`

---

## PHẦN 3 — TOKEN CỦA MÁY NHÀ

### Ngày hết hạn: 10/11/2026

Từ 14/09/2026, **hai máy dùng hai token khác nhau và hết hạn khác ngày**:

| Máy | Token hết hạn |
|---|---|
| **Máy nhà** | **10/11/2026** |
| Máy công ty |  |

⇒ **Không còn chuyện "cả hai máy cùng ngừng hoạt động"** như tài liệu cũ ghi. Máy nhà sẽ
hết hạn trước 3 ngày — thực ra tốt hơn, vì bạn còn thời gian xử lý trước khi máy kia cũng tới hạn.

---

## PHẦN 4 — THÔNG BÁO TOKEN HẾT HẠN ĐI ĐÂU?

### Mỗi máy gửi qua bot Telegram riêng của máy đó

`report.py` đọc `TELEGRAM_BOT_TOKEN` trong file `.env` **của chính máy đang chạy**. Nên:

- Máy **nhà** → cảnh báo nằm trong khung chat với **bot Home**
- Máy **công ty** → cảnh báo nằm trong khung chat với **bot Company**

Hai máy không lẫn vào nhau. Mở đúng khung chat của bot là thấy.

### Có 2 loại cảnh báo

| Loại | Khi nào | Nội dung |
|---|---|---|
| 🟡 **Cảnh báo sớm** | Token còn dưới **7 ngày** | Nằm ở **đầu** mỗi báo cáo, kèm hướng dẫn lấy token mới |
| 🔴 **Báo lỗi** | Token **đã chết**, lần chạy thất bại | Tin nhắn riêng, nội dung tuỳ lỗi Meta trả về |

### ⚠️ Giới hạn phải biết

**Cả hai loại cảnh báo đều chỉ gửi được khi có một lần chạy báo cáo.** Nghĩa là:

- Máy **tắt** hoặc **đăng xuất Windows** đúng lúc đó ⇒ **không có cảnh báo nào**.
- Nếu máy tắt nhiều ngày, bạn chỉ biết khi tự để ý là báo cáo không về.

⇒ **Đừng phụ thuộc hoàn toàn vào cảnh báo.** Thỉnh thoảng mở Telegram xem báo cáo có về đều không.

---

## PHẦN 5 — KHI CẦN LẤY TOKEN META MỚI

1. Làm theo `HUONG-DAN-DIEN-TOKEN.md` — **chỉ làm ở MỘT máy**
2. Chạy `python kiem-tra-token.py` để xác nhận token mới sống được 60 ngày
3. **Copy file `.env` sang máy kia bằng USB**

> ❌ **Đừng** gửi file `.env` qua Telegram / Zalo / email / chat AI.
> Đó là gửi mật khẩu tài khoản quảng cáo qua mạng.
>
> ✅ Sau khi copy sang máy kia, chạy `python kiem-tra-token.py` ở máy đó để chắc chắn.

---

## PHẦN 6 — MỐC THỜI GIAN

| Thời điểm | Việc |
|---|---|
| **Tối 14/09/2026** | Chạy `git pull` + `python kiem-tra-token.py` ở máy nhà |
| **10/11/2026** | ⚠️ Token Meta **máy nhà** hết hạn |
| **** | ⚠️ Token Meta **máy công ty** hết hạn |

Hệ thống sẽ **tự nhắn cảnh báo trước 7 ngày** — bạn không cần tự nhớ ngày.

---

## TÓM TẮT NHANH

```
MÁY NHÀ — BẢN 28/09 (mới nhất, làm theo mục đầu file)
├── git pull                                        ← nhận code mới
├── thêm dòng REPORT_SLOTS=8,12,17 vào cuối .env     ← BẮT BUỘC, git pull không mang dòng này sang
├── cai-dat-nguoi-truc.bat (Run as administrator)   ← PHẢI chạy: tạo Người trực, xoá 3 lịch cũ
├── nhìn "Tham so": phải kết thúc bằng nguoi_truc.py"
└── nhìn "Trang thai": phải là Running + có dòng "Tien trinh: dang chay"

KIỂM TRA NHANH (dán vào cửa sổ lệnh tại thư mục dự án):
   python -c "import report; print(report.doc_moc_tu_env(report.load_env('.env')))"
   → phải in ra [8, 12, 17]

KHÔNG cần: bat-chay-bu.bat, bat-danh-thuc-may.bat (Người trực chạy suốt, không cần đánh thức máy)
KHÔNG cần: sửa token trong .env (token máy nhà không đổi)
```

**Xong.**
