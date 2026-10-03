# HƯỚNG DẪN VỀ TOKEN APP (TOKEN TÀI KHOẢN HỆ THỐNG)

Dành cho Đại — người không cần biết code.

> 🔴 **ĐỌC MỤC NÀY TRƯỚC — TÀI LIỆU NÀY ĐÃ ĐƯỢC VIẾT LẠI.**
>
> Bản đầu tiên của tôi (cùng ngày 03/10/2026) hướng dẫn Đại cách **tự tạo token App**
> trong Business Manager. **Hướng dẫn đó SAI** — vì nó giả định Đại là **Admin** của
> tài khoản doanh nghiệp.
>
> Đại đã nói rõ: *"tôi không chủ của tài khoản doanh nghiệp của meta"* và
> *"tôi không xin được"*. Tôi đã tra trực tiếp trên Meta để kiểm chứng:
>
> ```
> Business: Langmaster Business ()
>   → Người dùng "" — vai trò: EMPLOYEE   ← KHÔNG phải ADMIN
>   → system_users: rỗng (0 mục)                   ← chưa có token App nào
> ```
>
> **Vai trò `EMPLOYEE` KHÔNG đủ quyền tạo tài khoản hệ thống.** Nên Đại **không thể**
> tự làm việc này, dù có làm theo hướng dẫn cũ cũng sẽ bị Meta chặn ở bước cuối.
>
> ✅ **Vậy nên: KHÔNG cần token App nữa.** Tôi đã làm **Đường 2** thay thế — xem Phần G
> ở cuối tài liệu. Đường 2 chạy được ngay, không cần xin ai.

---

## Phần A — Hiểu nhanh trước khi làm

### Token hiện tại là gì

Tôi đã tra trực tiếp trên Meta bằng công cụ chính thức `debug_token`. Đây là sự thật đo được:

| Thông số | Giá trị thật |
|---|---|
| Loại token | **`USER`** — token cá nhân |
| Thuộc về |  (id ``) |
| Ứng dụng | MCP ADS (id ``) |
| Hết hạn |
| Quyền đang có | `ads_management`, `ads_read`, `business_management` |
| Tài khoản quảng cáo |
| Business |
| **Vai trò của Đại** | **`EMPLOYEE`** — không phải Admin |

### Token App khác gì

| | Token cá nhân (đang dùng) | Token App (sẽ đổi sang) |
|---|---|---|
| Thuộc về | Tài khoản Facebook của Đại | Một "tài khoản hệ thống" giả, do Đại tạo |
| Meta ghi ai làm | **""** | **Ứng dụng / tài khoản hệ thống** |
| Phân biệt người với máy | ❌ Không thể | ✅ Rõ ràng |
| Hết hạn |
| Nếu Đại đổi mật khẩu Facebook | Token **có thể chết** | **Không ảnh hưởng** |

### "Tài khoản hệ thống" là gì

Nó **không phải** người thật. Đại tạo một cái tên (ví dụ `Agent Ads`) trong Business Manager.
Tên đó chỉ tồn tại để giữ token và được cấp quyền trên tài khoản quảng cáo. Nó không có mật khẩu,
không đăng nhập được, không ai dùng nó để chat.

---

> ⛔ **CÁC PHẦN B, C, D, E, F DƯỚI ĐÂY KHÔNG DÙNG ĐƯỢC NỮA.**
>
> Chúng hướng dẫn Đại vào Business Manager tự tạo tài khoản hệ thống. Việc đó **đòi hỏi
> vai trò Admin**, mà Đại là `EMPLOYEE`. Làm theo sẽ **bị Meta chặn ở bước cuối** (không
> thấy mục "Người dùng hệ thống", hoặc bấm tạo mà không được).
>
> Tôi giữ lại để tham khảo — **nếu sau này Đại được cấp quyền Admin**, lúc đó làm theo là được.
> Còn bây giờ xin **bỏ qua xuống thẳng Phần G**.
>
> Lý do tôi không xoá: nếu một ngày Admin đổi ý và cấp quyền, tài liệu này vẫn dùng được ngay.

---

## Phần B — Chuẩn bị (KHÔNG DÙNG — xem ghi chú trên)

### B1. Kiểm tra `.env` đã có đủ 3 dòng

Mở file `.env` bằng cách **bấm đúp vào `mo-file-env.bat`** (file này có sẵn trong thư mục dự án,
nó tự mở đúng file `.env` bằng Notepad).

Trong file phải có **đủ 3 dòng** này:

```
META_ADS_ACCESS_TOKEN=EAA...
META_APP_ID=
META_APP_SECRET=...
```

✅ Tôi đã kiểm tra: **`.env` hiện tại đã có đủ cả 3 dòng**. Đại không cần làm gì ở bước này.

> ⚠️ **Đừng đóng file `.env` vội** — chút nữa Đại sẽ dán token mới vào chính dòng
> `META_ADS_ACCESS_TOKEN` này.

### B2. Ghi lại thông tin cần thiết

Đại sẽ cần những con số này khi làm (đã tra sẵn cho Đại):

- **Tài khoản quảng cáo:**
- **Business ID:**
- **App ID:**

---

## Phần C — Lấy token App (làm từng bước)

> ⚠️ **Quan trọng:** Đại phải **tự làm phần này** — tôi không thể làm thay, vì nó yêu cầu đăng
> nhập Facebook của Đại.

### C1. Mở Business Manager

1. Mở trình duyệt (Chrome / Edge).
2. Vào địa chỉ: **business.facebook.com/settings**
3. Nếu được hỏi chọn tài khoản doanh nghiệp → chọn business ``
   (tên có thể là tên công ty của Đại).

### C2. Vào mục Người dùng hệ thống

Ở menu **bên trái**, tìm và bấm:

```
Người dùng  →  Người dùng hệ thống
```

(Tiếng Anh: `Users` → `System Users`)

> 📌 Nếu không thấy mục "Người dùng hệ thống", xem **Phần E — Xử lý sự cố** ở cuối tài liệu.

### C3. Tạo người dùng hệ thống mới

1. Bấm nút **Thêm** (góc trên bên phải).
2. Đặt tên: **`Agent Ads`** (tên gì cũng được, nhưng đặt vậy để dễ nhớ).
3. Vai trò: chọn **Người quản lý** (`Admin`).
   > ⚠️ Phải chọn **Admin**, không phải `Employee`. Chọn `Employee` thì không gán được tài sản.
4. Bấm **Tạo người dùng hệ thống**.

**→ Tôi đã viết sẵn file ảnh minh hoạ các bước:** xem `HUONG-DAN-TOKEN-APP-HINH-ANH.md` (nếu có).

### C4. Gán tài khoản quảng cáo cho người dùng hệ thống

1. Sau khi tạo xong, bấm vào tên **`Agent Ads`** vừa tạo.
2. Bấm nút **Thêm tài sản** (`Add Assets`).
3. Chọn tab **Tài khoản quảng cáo** (`Ad Accounts`).
4. Tick vào tài khoản quảng cáo đã được cấp quyền.
5. Ở cột quyền bên phải, tick **"Quản lý chiến dịch"** (`Manage campaigns`).
6. Bấm **Lưu thay đổi** (`Save Changes`).

> ⚠️ **Đây là bước hay bị bỏ sót nhất.** Không gán tài sản thì token tạo ra sẽ không có quyền gì,
> và hệ thống sẽ báo lỗi khi đọc số.

### C5. Tạo token

1. Vẫn trong trang `Agent Ads`, bấm nút **Tạo token mới** (`Generate New Token`).
2. Chọn ứng dụng: **`MCP ADS`** (id ``).
   > 📌 Chọn **đúng ứng dụng này**, không chọn ứng dụng khác — vì `META_APP_ID` trong `.env`
   > đang là app này.
3. Hạn dùng (`Token Expiration`): chọn **Không bao giờ** (`Never`).
   > ✅ Đây là lợi ích lớn nhất — khỏi phải gia hạn mỗi 60 ngày như hiện tại.
4. Tick **đủ 3 quyền** này:
   - ☑ `ads_management` (Quản lý quảng cáo)
   - ☑ `ads_read` (Đọc dữ liệu quảng cáo)
   - ☑ `business_management` (Quản lý doanh nghiệp)
5. Bấm **Tạo token**.
6. Một dãy ký tự dài hiện ra — bấm **Copy**.

> 🔴 **CẢNH BÁO:** token chỉ hiện **MỘT LẦN DUY NHẤT**. Đóng cửa sổ là mất, phải tạo lại từ đầu.
> **Đừng đóng cửa sổ vội** — cứ để nguyên đó, làm tiếp Phần D rồi hãy đóng.

---

## Phần D — Đưa token vào hệ thống

### D1. Dán token vào `.env`

1. Quay lại cửa sổ **Notepad** đang mở file `.env` (mở từ bước B1).
   > Nếu đã lỡ đóng: bấm đúp vào **`mo-file-env.bat`** để mở lại.
2. Tìm dòng bắt đầu bằng `META_ADS_ACCESS_TOKEN=`.
3. **Xoá token cũ** (phần sau dấu `=`) và **dán token mới** vào.
   > ⚠️ Dán **sát** dấu `=`, **không có dấu cách**, **không xuống dòng** giữa chừng.
4. Bấm **Ctrl + S** để lưu.
5. Đóng cửa sổ Notepad.

### D2. Kiểm tra token mới

Bấm đúp vào file **`kiem-tra-token-app.bat`** (tôi đã viết sẵn trong thư mục dự án).

File này sẽ tự kiểm tra và cho Đại biết kết quả. **Đọc kỹ phần chữ hiện ra**, có 3 khả năng:

| Kết quả hiện ra | Nghĩa là | Đại làm gì |
|---|---|---|
| ✅ `TOKEN APP — ĐÃ ĐÚNG` | Thành công | Sang bước D3 |
| ⚠️ `VẪN LÀ TOKEN CÁ NHÂN` | Chưa đổi được | Kiểm lại bước D1, có thể dán nhầm ô |
| ❌ `TOKEN KHÔNG HỢP LỆ` | Token sai / thiếu quyền | Làm lại Phần C từ bước C5 |

### D3. Khởi động lại agent

Bấm đúp vào **`khoi-dong-lai-agent.bat`**.

> 📌 **Bắt buộc phải làm bước này.** Lý do: Python chỉ đọc `.env` một lần lúc khởi động đối với
> phần cấu hình, nên đổi token xong phải khởi động lại mới ăn.

### D4. Xác nhận lần cuối

Sau khoảng 2 phút, mở file `logs\baocao.log` (bấm đúp vào nó, chọn Notepad).

Tìm dòng mới nhất có chữ `AGENT:`. Nếu thấy dòng dạng:

```
AGENT: 99 nhom, 41 co chi tieu hom nay, ...
```

→ **Thành công.** Agent đang đọc số bình thường bằng token mới.

Nếu thấy dòng `AGENT: loi doc Meta: ...` → chụp màn hình gửi tôi.

---

## Phần E — Xử lý sự cố

### "Không thấy mục Người dùng hệ thống"

Nguyên nhân: tài khoản của Đại chưa có quyền quản trị đầy đủ trên business đó.

Cách xử lý:
1. Vào **business.facebook.com/settings** → **Người dùng** → **Yêu cầu**.
2. Kiểm tra xem Đại có vai trò **Quản trị viên** (`Admin`) trên business `` không.
3. Nếu không phải Admin → nhờ người đang là Admin cấp quyền, hoặc tự làm theo hướng dẫn của Meta
   tại `developers.facebook.com/docs/business-manager`.

### "Tạo token mới" bị mờ, không bấm được

Nguyên nhân: chưa gán tài sản ở bước C4.
Cách xử lý: quay lại **C4**, gán tài khoản quảng cáo đã được cấp quyền.
"Quản lý chiến dịch", rồi bấm lại.

### Token tạo ra nhưng hệ thống báo "thieu META_ADS_ACCESS_TOKEN"

Nguyên nhân: dán nhầm ô trong `.env`, hoặc dán kèm dấu cách / dấu xuống dòng.
Cách xử lý: mở lại `.env`, kiểm tra dòng `META_ADS_ACCESS_TOKEN=` — token phải nằm **ngay sau**
dấu `=`, **trên cùng một dòng**, **không có dấu cách** ở hai đầu.

### Muốn quay về token cũ

Đại vẫn giữ token cũ trong file `.env.bak` (được sao lưu tự động).
Cách quay về: mở `.env.bak`, copy dòng `META_ADS_ACCESS_TOKEN=` cũ, dán lại vào `.env`,
rồi bấm `khoi-dong-lai-agent.bat`.

> 📌 Token cũ còn hạn tới ****, nên vẫn quay về được nếu cần.

---

## Phần F — Sau khi đổi xong, có gì khác

### Điều tốt lên

1. **Nhật ký Meta tách bạch.** Khi agent tự tắt nhóm, Meta ghi là do ứng dụng hệ thống làm —
   không còn lẫn với Đại.
2. **Hết lo token chết.** Đặt "Không bao giờ" thì không phải gia hạn 60 ngày một lần nữa.
3. **Đổi mật khẩu Facebook không ảnh hưởng.** Token App không phụ thuộc mật khẩu cá nhân.

### Lưu ý

- Token App này **không dùng** để đăng nhập Facebook được — nó chỉ là chìa khoá cho hệ thống.
- Nếu Đại muốn **thu hồi** token (ví dụ nghi bị lộ): vào `Agent Ads` → **Tạo token mới** →
  xoá token cũ đi, rồi làm lại Phần D với token mới.

---

## Phần G — ĐƯỜNG 2: CÁCH TÔI ĐÃ LÀM THAY (ĐỌC PHẦN NÀY)

Đại không lấy được token App ⇒ tôi **bù lại bằng cách khác**, chạy được ngay, không cần xin ai.

### G1. Ghi rõ NGUỒN GỐC trong sổ của agent

Từ nay mỗi bản ghi trong `logs/nhat-ky-agent.json` có thêm trường `nguon_goc`:

| Giá trị | Nghĩa |
|---|---|
| `agent_tu_hanh` | **Máy tự quyết**, không ai bấm nút (ví dụ: TH2 tự tắt chiến dịch) |
| `dai_bam_nut` | Đại **bấm nút** trên Telegram |
| `dai_go_tay` | Đại **gõ lệnh** bằng tay |
| `cho_duyet` | Mới là đề xuất, chưa gửi gì lên Meta |

⇒ Mở sổ ra là biết **việc nào máy làm, việc nào Đại làm** — **không cần mở Meta**.

### G2. Sửa lỗi "bản ghi mồ côi" (lỗi thật, đã tồn tại trên sổ)

Tôi đã dựng thử và đo được: **17 trong 40 bản ghi** bị **mồ côi** — tức là *đã gửi lệnh lên
Meta* nhưng **thiếu kết quả**. Nguyên nhân: `cap_nhat_phan_hoi` chốt kết quả vào **nhầm bản ghi**.

Hậu quả nặng nhất: **không bản ghi nào** vừa "đã gửi Meta" vừa "có kết quả", nên **không thể
đối chiếu với Meta được** — công cụ ở G3 lọc ra rỗng.

**Đã sửa.** Từ nay kết quả chốt đúng vào bản ghi đã gửi Meta.

> 📌 17 bản ghi cũ vẫn còn dấu vết mồ côi — **không sửa được quá khứ**, nhưng công cụ G3
> **nhận diện và bỏ qua** chúng, đồng thời liệt kê riêng để Đại thấy.

### G3. Công cụ đối chiếu — việc mà token App lẽ ra làm được

Bấm đúp vào **`doi-chieu-meta.bat`**. Nó in ra bảng:

```
Số sự kiện Meta đọc được : 1061
Khớp hai nguồn            : 30
Chỉ có trên Meta          : 1031
Chỉ có trong sổ agent     : 9
Bản ghi mồ côi (lỗi sổ)   : 17

── KHỚP (cả sổ và Meta đều có) ───────────────────────────────────────
  03/10 09:50:25  120250698465560509  [Đại bấm nút]  (3 sự kiện Meta)
  02/10 11:45:08  120250204184200509  [Đại bấm nút]  (3 sự kiện Meta)
  ...

── CHỈ CÓ TRÊN META (ĐẠI TỰ LÀM TAY, không qua agent) ─────────────────
  03/10 13:59:59  120250719073350509  update_ad_run_status  (Meta ghi tên: )
  ...
```

**Đọc bảng này thế nào:**

| Mục | Nghĩa |
|---|---|
| **KHỚP** | Việc có ở **cả** sổ agent **và** Meta → agent làm, đã kiểm chứng được |
| **CHỈ CÓ TRÊN META** | Đại (hoặc người khác) **tự làm tay**, agent không biết |
| **CHỈ CÓ TRONG SỔ** | Nghi vấn — agent ghi mà Meta không nhận. Nhờ AI xem |
| **MỒ CÔI** | Dấu vết lỗi cũ. Nhờ AI xem |

> ✅ **Công cụ này TUYỆT ĐỐI CHỈ ĐỌC.** Không tắt, không sửa, không tạo gì trên Meta.
> Không gửi Telegram. Không sửa file sổ. **Bấm bao nhiêu lần cũng được.**

**Bằng chứng nó chạy thật** — tôi đã đối chiếu đúng việc Đại hỏi hôm 03/10:

| Nguồn | Ghi gì |
|---|---|
| Sổ agent | tắt chiến dịch `120250389649450509` |
| Meta | `03:59:10 UTC` = **10:59:10 giờ VN** — `update_campaign_run_status` |

⇒ **Khớp.** Và Meta ghi tên người thực hiện là **""** — đúng như tôi đã nói:
token cá nhân nên Meta không phân biệt được người và máy. **Đó chính là lý do phải có công cụ này.**

### G4. Còn token App thì sao?

**Để sau.** Khi nào Đại được cấp quyền Admin (hoặc xin được), làm theo Phần B–F ở trên —
không cần sửa code, chỉ dán token mới vào `.env` rồi bấm `khoi-dong-lai-agent.bat`.

Còn hiện tại, Đường 2 đã đủ để trả lời câu **"việc này ai làm"**.

---

## Tóm tắt một câu

**Hiện tại (Đường 2 — đang dùng):** token cá nhân vẫn giữ, nhưng sổ agent nay ghi rõ nguồn gốc,
và bấm **`doi-chieu-meta.bat`** là biết ngay việc nào máy làm, việc nào Đại làm tay.

**Sau này (nếu được cấp Admin):** vào **Business Manager → Người dùng → Người dùng hệ thống →
tạo `Agent Ads` → gán tài khoản quảng cáo quyền "Quản lý chiến dịch" → tạo token (không bao giờ
hết hạn, tick 3 quyền) → dán vào `.env` → bấm `kiem-tra-token-app.bat` → bấm
`khoi-dong-lai-agent.bat`.
