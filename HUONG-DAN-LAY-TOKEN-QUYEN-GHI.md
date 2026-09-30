# HƯỚNG DẪN LẤY LẠI TOKEN META — BẢN CÓ QUYỀN GHI

Dành cho Đại — người không cần biết code. Khoảng **5 phút**.

---

## Chuyện gì đang xảy ra

Hệ thống hiện **đọc** được số liệu quảng cáo, nhưng **không tắt** được chiến dịch nào.

Tôi đã hỏi thẳng Meta bằng chính token của Đại, ngày 30/09/2026:

| Quyền | Có không | Nghĩa là |
|---|---|---|
| `ads_read` | **CÓ** | Đọc số liệu, gửi báo cáo — đang chạy tốt |
| `ads_management` | **KHÔNG** | Tắt/bật chiến dịch, đổi ngân sách — **chưa làm được** |

Nên nếu bây giờ có cho AI tự tắt camp thì **nó sẽ thất bại ngay ở bước gửi lệnh lên Meta** —
không phải vì code sai, mà vì Meta từ chối. Việc cần làm là lấy token mới có tick thêm một quyền.

---

## Tin tốt: Đại đã làm việc này một lần rồi

Ngày 14/09/2026 Đại đã lấy token theo file `HUONG-DAN-DIEN-TOKEN.md` (Bước A → E). Lần này
**giống hệt lần đó**, chỉ khác **đúng một chỗ**:

> Ở phần chọn quyền, **tick thêm `ads_management`** (lần trước chỉ tick `ads_read`).

Mọi thứ còn lại — lấy token, đổi sang token 60 ngày, kiểm tra — y như cũ.

---

## Việc nào Đại làm, việc nào máy làm

| Bước | Đại làm | Máy làm hộ |
|---|---|---|
| 1. Mở trang lấy token | ✔ | |
| 2. Chọn đúng app **MCP ADS** | ✔ | |
| 3. Tick thêm quyền ghi | ✔ | |
| 4. Bấm lấy token, copy | ✔ | |
| 5. Dán token vào `.env` | ✔ | (có file mở sẵn) |
| 6. Đổi sang token 60 ngày | chỉ **bấm đúp** | ✔ chạy hết |
| 7. Kiểm tra quyền | chỉ **bấm đúp** | ✔ chạy hết |

---

## BƯỚC 1 — Mở trang lấy token

Mở trình duyệt, vào địa chỉ này:

```
https://developers.facebook.com/tools/explorer/
```

Đăng nhập bằng tài khoản Facebook **có quyền quảng cáo** (tài khoản Đại vẫn dùng).

---

## BƯỚC 2 — Chọn ĐÚNG app cũ

⚠️ **Đây là chỗ dễ sai nhất. Sai chỗ này là cả bước 6 sẽ hỏng.**

Nhìn **góc trên bên phải** màn hình, có ô chọn tên app (chữ **"Meta App"**). Bấm vào đó và chọn:

| | |
|---|---|
| **Tên app** | **MCP ADS** |
| **App ID** | `` |

**Nếu không thấy app "MCP ADS" trong danh sách:** dừng lại, đừng làm tiếp — nhắn cho trợ lý.
**Tuyệt đối KHÔNG bấm "Create App"** (tạo app mới). App mới có mã khác, hệ thống sẽ không đổi
được token và sẽ báo lỗi.

---

## BƯỚC 3 — Tick thêm quyền GHI

Ở **cột bên phải** có khung tên **"Permissions"**. Trong đó có danh sách các ô tick.

Cần **đúng 3 ô** được tick:

| Ô cần tick | Trạng thái |
|---|---|
| `ads_read` | đã tick sẵn — giữ nguyên |
| `business_management` | đã tick sẵn — giữ nguyên |
| **`ads_management`** | **tick thêm — đây là ô mới** |

👉 Cách tìm nhanh: trong khung Permissions có ô **tìm kiếm**, gõ `ads_` rồi bấm vào ô
**`ads_management`**.

---

## BƯỚC 4 — Bấm lấy token và copy

1. Bấm nút màu xanh **"Generate Access Token"** (thường ở dưới cùng bên phải).
2. Facebook hiện một hộp thoại hỏi xác nhận → bấm **"Continue"** / **"Tiếp tục"**.
3. Một dãy chữ rất dài hiện ra ở ô phía trên (bắt đầu bằng `EAAZ...`).
4. Bấm nút **copy** bên cạnh dãy đó.

> ⚠️ **Dãy chữ này là mật khẩu quảng cáo của Đại.** Không dán vào chat, không gửi Zalo,
> không chụp màn hình gửi ai. Chỉ dán vào file `.env` ở bước sau.

---

## BƯỚC 5 — Dán token vào file `.env`

1. Trong thư mục dự án, **bấm đúp** vào file **`mo-file-env.bat`** → Notepad mở file `.env`.
2. Tìm dòng bắt đầu bằng **`META_ADS_ACCESS_TOKEN=`**
3. **Xoá token cũ** (phần sau dấu `=`), rồi **dán token mới** vào.
   - Dán **sát dấu `=`**, không có dấu cách. Đúng: `META_ADS_ACCESS_TOKEN=EAAZ...`
4. Bấm **Ctrl + S** để lưu, rồi **đóng** cửa sổ Notepad.

> 💡 Hai dòng `META_APP_ID` và `META_APP_SECRET` **đã có sẵn** — không cần đụng tới.

---

## BƯỚC 6 — Đổi sang token 60 ngày

Token vừa lấy ở bước 4 **chỉ sống 1–2 giờ**. Phải đổi ngay, nếu không mai báo cáo sẽ lỗi.

**Bấm đúp** vào file:

```
doi-token-60-ngay.bat
```

Đợi khoảng 10 giây. Thấy dòng **[OK] DA DOI TOKEN 60 NGAY** là xong.

> ⚠️ Ngày 14/09/2026 đã có sự cố: token chỉ sống **1 giờ 44 phút** mà bài kiểm tra vẫn báo đạt.
> Nên bước này **bắt buộc**, đừng bỏ qua.

---

## BƯỚC 7 — Kiểm tra đã có quyền ghi chưa

**Bấm đúp** vào file:

```
kiem-tra-quyen-ghi.bat
```

Đọc kết quả ở cuối màn hình:

| Kết quả | Nghĩa là | Làm gì |
|---|---|---|
| **[OK] TOKEN DA CO QUYEN GHI** | Xong | Nhắn cho trợ lý biết |
| **[CHUA CO] TOKEN CHUA CO QUYEN GHI** | Chưa tick đúng quyền | Xem mục "Nếu gặp trục trặc" bên dưới |
| **[LOI] KHONG KIEM TRA DUOC** | Chưa kết luận được | Chụp màn hình gửi trợ lý |

---

## Nếu gặp trục trặc

| Hiện tượng | Nguyên nhân thường gặp | Cách xử lý |
|---|---|---|
| Ô chọn app không có **MCP ADS** | Đăng nhập nhầm tài khoản Facebook | Đăng nhập lại bằng tài khoản có quyền quảng cáo |
| Không tìm thấy ô `ads_management` trong Permissions | Đang ở tab khác, hoặc gõ sai tên | Gõ đúng `ads_management` vào ô tìm kiếm |
| Bước 6 báo **thieu META_APP_ID** | File `.env` bị thiếu dòng | Bấm `mo-file-env.bat`, điền lại 2 dòng đó |
| Bước 6 báo lỗi khác | Token ngắn hạn đã hết hạn (quá 2 giờ) | Làm lại từ Bước 1 |
| Bước 7 vẫn báo **CHUA CO QUYEN GHI** | Chưa tick `ads_management`, hoặc tick rồi nhưng bấm Generate trước khi tick | Làm lại từ Bước 3 |
| Meta báo cần **xác minh doanh nghiệp** | Quyền nâng cao yêu cầu xác minh | Chụp màn hình gửi trợ lý — việc này có thể mất vài ngày, cần bàn lại |

---

## Một điều phải nói thẳng trước

**Chưa chắc việc này thành công ngay.** `ads_management` là quyền nâng cao. Thường thì app ở
chế độ thử nghiệm và chính chủ app dùng được ngay, **nhưng chưa ai thử với app này lần nào**.

Và kể cả bước 7 báo **CÓ quyền ghi**, đó vẫn là **Meta nói** — chưa phải đã ghi được thật.
Tôi đã thử 4 cách để kiểm trước bằng một lệnh vô hại, và **cả 4 đều thất bại**: Meta cố ý gộp mọi
loại lỗi vào cùng một câu trả lời nên không thể phân biệt "thiếu quyền" với "sai tham số".

⇒ **Cách kiểm chứng duy nhất là làm thật một lần**, trên **một chiến dịch mà Đại đã muốn tắt**.
Nếu Meta từ chối, ta biết ngay và **không mất gì** — chiến dịch vẫn chạy bình thường.

---

## Sau khi xong

Nhắn cho trợ lý:

> Tôi đã lấy token mới. Kiểm tra giúp tôi đã có quyền ghi chưa.

Trợ lý sẽ tự kiểm lại và báo kết quả. Nếu đã có quyền ghi, bước tiếp theo là bàn cách làm **nấc 2**
(AI xin phép Đại qua Telegram rồi mới tắt) — chưa phải để AI tự tắt.

---

*Liên quan: `HUONG-DAN-DIEN-TOKEN.md` (quy trình gốc) · `HUONG-DAN-LAY-CHIA-KHOA-AI.md` (chìa khoá AI)*
