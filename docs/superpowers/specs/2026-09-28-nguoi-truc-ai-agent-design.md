# Thiết kế — Nâng hệ thống báo cáo Meta Ads thành "Người trực" có AI

**Ngày:** 28/09/2026
**Người duyệt:** Đại
**Trạng thái:** Đã duyệt phần định hướng, chờ Đại đọc lại bản viết này

---

## 1. Vì sao làm việc này

Hệ thống hiện tại (xem `HANDOFF.md`) chạy đúng nhưng có ba vấn đề đã kiểm chứng bằng log thật:

### 1.1. Mốc 22h chưa từng chạy một lần nào

Đếm trong toàn bộ `logs/baocao.log`: mốc 8h xuất hiện 51 lần, mốc 12h 37 lần, mốc 17h 27 lần,
**mốc 22h: 0 lần**. Báo cáo "Tổng kết cả ngày" mà `README.md` quảng cáo chưa bao giờ tồn tại.

**Quyết định của Đại:** bỏ mốc 22h trên **máy công ty**. Máy nhà giữ nguyên nếu muốn.
Vì vậy danh sách mốc giờ trở thành cấu hình riêng của từng máy (xem 5.1), không viết cứng trong code.
Kiến trúc mới làm mốc 22h chạy được, nên sau này muốn lấy lại chỉ là sửa một dòng trong `.env`.

### 1.2. Cơ chế chống trùng không hoạt động

Đếm số lần gửi thành công theo ngày: 14/09 = 5 lần, 15/09 = 4, 18/09 = 4, 24/09 = 4, 28/09 = 4.
Bình thường một ngày chỉ nên có 3 lần. Sáng 28/09 lúc 08:26, hệ thống gửi **4 tin trùng + 4 file HTML**.

`HANDOFF.md` dòng 218 ghi cơ chế này "đã kiểm chứng". Nhưng cách kiểm chỉ là **chạy lại tuần tự**,
trong khi lỗi chỉ xuất hiện khi các tiến trình chạy **đồng thời**.

### 1.3. Nguyên nhân gốc của cả hai: lịch Windows không truyền mốc giờ

`cai-dat-lich.bat` dòng 129 tạo lịch bằng:

```
schtasks /Create /TR "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\"" ...
```

Không truyền mốc giờ. Nên `report.py` phải tự đoán (dòng 602):

```python
slot = min(REPORT_SLOTS, key=lambda s: abs(s - now.hour))
```

Khi máy thức dậy sau nhiều mốc bị lỡ, cả bốn lịch cùng chạy bù và cùng đoán ra một mốc gần nhất.
Hệ quả kép: **gửi trùng nhau**, và **mốc 22h bị biến thành mốc 8h** nên không bao giờ báo cáo đúng.

### 1.4. Mục "NHẬN ĐỊNH" không thực sự nhận định

Trong `build_report()`, tiêu đề hứa có phân tích nhưng nội dung chỉ là hai bảng xếp hạng kèm số thô.
Không so sánh với kỳ trước, không có câu kết luận. `determine_period()` chỉ trả về MỘT khoảng thời gian,
nên toàn hệ thống không có dữ liệu kỳ trước để so.

### 1.5. Không lưu lịch sử

`dashboard.html` bị ghi đè mỗi lần chạy, không giữ bản nào. Không có số cũ ⇒ mọi câu so sánh đều bất khả thi.

---

## 2. Mục tiêu

1. Chữa gốc hai lỗi đang hoạt động (gửi trùng, mốc 22h mất tích).
2. Để AI viết phần nhận định thật, có so sánh với kỳ trước.
3. Cho Đại nhắn tin hỏi bot và được trả lời khi máy đang bật.
4. Để hệ thống tự xử lý một số lỗi thay vì chỉ báo lỗi.

## 3. Phi mục tiêu (cố ý KHÔNG làm)

- **Không** để AI quyết định lấy chỉ số nào, tính thế nào, hoặc có gửi hay không.
- **Không** để AI đụng vào phép tính tiền. Số liệu luôn do code tính.
- **Không** đưa bot lên máy chủ đám mây. Bot sống trên máy của Đại.
- **Không** viết lại phần lấy số liệu và tính toán — phần đó đang đúng, giữ nguyên.

Lý do của các phi mục tiêu trên: một báo cáo chi tiêu phải cho ra **cùng một con số ở mọi lần chạy**.
Nếu để AI quyết định ở khâu lấy số, số liệu sẽ thay đổi giữa các lần chạy cùng ngày — tính xấu nghiêm trọng
với một báo cáo tiền bạc, và Đại sẽ khó biết khi nào nó sai.

---

## 4. Kiến trúc

### 4.1. Hiện tại

Bốn lịch Windows rời rạc → bốn tiến trình `report.py` độc lập → mỗi tiến trình tự đoán mốc giờ.

### 4.2. Sau khi làm

Một tiến trình thường trú duy nhất, gọi là **Người trực**, chạy suốt khi máy bật. Nó làm ba việc:
canh mốc giờ và gửi báo cáo; nghe tin nhắn Telegram và trả lời; điều phối hai việc trên.

Ba thứ bên ngoài nó dùng: Meta API (lấy số liệu), `logs/lich-su.json` (số các ngày trước), AI (viết nhận định, trả lời).

### 4.3. Vì sao kiến trúc này chữa được lỗi gốc

Người trực **biết rõ lịch của chính nó**. Nó không đoán mốc giờ, nên:

- Không còn bốn tiến trình chạy cùng lúc ⇒ **hết tranh nhau, hết gửi trùng**.
- Không còn lịch 22h chạy bù lẫn vào mốc 8h ⇒ **mốc 22h báo cáo đúng, nếu máy đó có bật mốc 22h**.
- Chạy bù đúng mốc: bật máy lúc 14h thì nó biết mình lỡ mốc nào và gửi đúng mốc đó.

---

## 5. Thành phần

### 5.1. `nguoi-truc.py` (mới) — tiến trình chính

Vòng lặp chính, kiểm tra đồng hồ mỗi 30 giây:

1. **Canh mốc giờ.** Danh sách mốc đọc từ khoá `REPORT_SLOTS` trong `.env`
   (khoá mới, sẽ thêm vào cả `.env` và `.env.example`; nếu thiếu thì mặc định `8,12,17,22`).
   Khi tới mốc và mốc đó chưa gửi hôm nay → gửi.
2. **Chạy bù khi khởi động.** Lúc khởi động, đối chiếu sổ đã gửi để biết mốc nào bị lỡ, gửi bù **đúng mốc đó**
   (không đoán). **Tối đa một báo cáo bù cho mỗi lần khởi động**: chỉ gửi mốc lỡ gần nhất, các mốc cũ hơn
   ghi nhật ký là "bỏ qua". Lý do: máy tắt hai ngày mà bật lên nhận ba báo cáo cũ là điều khó chịu vô ích,
   và báo cáo mốc 8h vốn đã bao trùm số liệu cả ngày hôm trước.
3. **Nghe Telegram.** Gọi `getUpdates` theo chu kỳ, chỉ nhận tin từ `TELEGRAM_CHAT_ID` của chính Đại.
   Tin từ người lạ bị bỏ qua và ghi nhật ký.
4. **Nhịp tim.** Ghi một dòng nhật ký mỗi vòng để biết tiến trình còn sống.
5. **Trả lời lệnh nhanh.** "còn sống không?" → trả lời kèm tình trạng. Dùng làm phép thử sức khoẻ.

Cờ dòng lệnh:

| Lệnh | Ý nghĩa |
|---|---|
| `python nguoi-truc.py` | Chạy thật (chế độ bình thường) |
| `python nguoi-truc.py --thu` | Chạy toàn bộ luồng, **không gửi gì** — dùng để kiểm chứng |
| `python nguoi-truc.py --gui-ngay 17` | Gửi ngay mốc 17h, bỏ qua canh giờ |

### 5.2. `lich-su.py` (mới) — lịch sử số liệu

Lưu vào `logs/lich-su.json`, giữ 180 ngày. Mỗi bản ghi gồm: ngày, mốc giờ, tổng các chỉ số,
danh sách campaign (id, tên, chi tiêu, lượt mua, CPR).

Giao diện:
- `ghi(ngay, moc, stats)` — ghi lại sau mỗi lần lấy số thành công
- `lay_mot_ngay(ngay)` — số của một ngày
- `lay_khoang(tu, den)` — tổng hợp một khoảng
- `lay_ky_truoc(ngay, so_ngay)` — kỳ trước để so sánh

Ghi **trước khi** gửi Telegram, để nếu gửi lỗi thì số liệu vẫn còn.

### 5.3. `ai.py` (mới) — lớp AI

Hai hàm, dùng chung một chỗ cấu hình nhà cung cấp:

- `viet_nhan_dinh(stats_hom_nay, stats_ky_truoc)` → 3–5 câu tiếng Việt.
  Nhận **số đã tính sẵn**, không tự gọi Meta.
- `tra_loi(cau_hoi)` → câu trả lời. Đây là phần có vòng lặp công cụ, với bốn công cụ giới hạn:
  `lay_mot_ngay`, `lay_khoang`, `xep_hang_camp`, `so_sanh`. Tối đa 5 lượt gọi công cụ rồi buộc trả lời.

Nhà cung cấp: **Gemini** (trường `GEMINI_API_KEY` đã có sẵn trong `.env`, và `test_gemini.py` đã có sẵn
đường kiểm tra chìa khoá).

**Suy giảm êm — điều kiện bắt buộc:** mọi lời gọi AI đều bọc trong `try`. Nếu AI lỗi vì bất kỳ lý do gì
(mất mạng, hết hạn mức, chìa khoá sai), báo cáo **vẫn gửi bình thường**, phần NHẬN ĐỊNH thay bằng
một dòng ghi chú rằng phần đó tạm lỗi. Đại không bao giờ mất báo cáo vì AI.

### 5.4. `report.py` (sửa) — giữ nguyên phần lõi

Thay đổi tối thiểu:
- Thêm tham số `--slot N`: nhận mốc giờ từ ngoài thay vì tự đoán. Đây là chìa khoá chữa lỗi gốc.
- Phần `build_report()` gọi `ai.viet_nhan_dinh()` cho mục NHẬN ĐỊNH; nếu AI lỗi thì rơi về bản mẫu cũ.
- Tách phần gửi (Telegram + file HTML) thành hàm gọi được từ cả `nguoi-truc.py` và dòng lệnh tay.
- Giữ nguyên `--mock`, `--dry`, `--force` như cũ.

**Không đụng tới:** `fetch_insights`, `apply_filter`, `compute_stats`, `get_action_value`, `fmt_money`,
`determine_period`. Toàn bộ phép tính giữ nguyên.

### 5.5. File cài đặt (mới)

- `cai-dat-nguoi-truc.bat` — tạo **một** lịch Windows duy nhất, tên `NguoiTruc`, kích hoạt khi đăng nhập,
  đặt "Restart on failure", không giới hạn thời gian chạy.
- `go-nguoi-truc.bat` — xoá lịch đó, dừng tiến trình.

`go-lich.bat` cũ giữ nguyên để tắt bốn lịch cũ.

---

## 6. Luồng dữ liệu

### 6.1. Luồng gửi báo cáo theo mốc

```
Người trực thấy tới mốc 17h
  → kiểm sổ: mốc 17h hôm nay đã gửi chưa? chưa → đi tiếp
  → compute_stats()  (code tính, như hiện nay)
  → lich-su.ghi()    (lưu số, để lần sau so)
  → ai.viet_nhan_dinh(số hôm nay, số kỳ trước)   ← nếu lỗi thì bỏ qua, dùng bản mẫu
  → build_report()   (ghép chữ, như hiện nay)
  → dashboard.save_dashboard()
  → send_telegram() + send_telegram_document()
  → ghi sổ đã gửi mốc 17h   (chỉ sau khi Telegram báo thành công)
```

### 6.2. Luồng trả lời câu hỏi

```
Đại nhắn "camp nào tệ nhất tuần này?"
  → Người trực đọc getUpdates, thấy tin từ chat_id của Đại
  → ai.tra_loi(câu hỏi)
      → AI chọn công cụ: xep_hang_camp(tuần này, sắp theo lượt mua tăng dần)
      → công cụ đọc từ lich-su.json, trả số về cho AI
      → AI viết câu trả lời tiếng Việt
  → gửi câu trả lời về Telegram
```

Nếu câu hỏi cần số hôm nay (chưa có trong lịch sử), công cụ sẽ gọi Meta API trực tiếp.

---

## 7. Xử lý lỗi — làm được gì và giới hạn ở đâu

| Tình huống | Hành vi mới |
|---|---|
| Meta chặn tạm (mã 17, 80004) | Tự chờ rồi thử lại, lùi dần. Không làm phiền Đại. |
| Meta trả lỗi khác | Gửi cảnh báo Telegram như hiện nay, kèm gợi ý xử lý. |
| Số bất thường | Đối chiếu lịch sử, báo "số này trông sai" thay vì gửi báo cáo gây hiểu lầm. Xem định nghĩa ở 7.3. |
| AI lỗi | Báo cáo vẫn gửi, thiếu phần nhận định, có ghi chú. |
| Tiến trình chết | Windows tự bật lại. Đại nhắn "còn sống không?" để kiểm tra. |
| Token Meta sắp hết hạn | **Thử tự gia hạn** — xem mục 7.1. |
| Token Meta đã chết hẳn | Không tự cứu được. Cảnh báo Đại và hướng dẫn làm tay. |

### 7.1. Tự gia hạn token — CHƯA KIỂM CHỨNG

`.env` của Đại đã có sẵn `META_APP_ID` và `META_APP_SECRET` (đã xác nhận có giá trị). Đó là hai thứ
cần để xin token mới qua `oauth/access_token` với `grant_type=fb_exchange_token`.

Nếu Meta cho phép gia hạn vòng, hệ thống sẽ tự xin token mới mỗi ~50 ngày và Đại không phải làm gì.
Điều này xoá bỏ rủi ro lớn nhất của dự án — lần 14/09 đã có sự cố token chỉ sống 1 giờ 44 phút.

⚠️ **Nhưng chưa thử lần nào.** Nghe hợp lý theo tài liệu, chưa có bằng chứng thực tế.
Đây là **việc thử nghiệm đầu tiên** của kế hoạch, làm trước khi hứa bất cứ điều gì.
Nếu Meta không cho, hệ thống vẫn giữ cảnh báo sớm 7 ngày như hiện nay và Đại vẫn làm tay.

### 7.2. Giới hạn phải nói thẳng

Token đã chết hẳn thì **không máy nào tự cứu được** — Meta bắt người thật đăng nhập mới cấp token.
Không có AI nào vượt được rào đó. Khi rơi vào tình huống này, hệ thống chỉ có thể báo sớm và hướng dẫn.

### 7.3. Định nghĩa "số bất thường" (ba điều kiện cụ thể)

Để tránh mơ hồ, chỉ ba trường hợp sau bị coi là bất thường. Cần ít nhất 7 ngày lịch sử mới bật kiểm tra;
chưa đủ 7 ngày thì bỏ qua, không cảnh báo.

1. **Chi tiêu vọt:** chi tiêu kỳ này lớn hơn **3 lần** mức trung bình cùng kỳ 7 ngày trước đó.
2. **Chi mà không có kết quả:** chi tiêu lớn hơn 0, tổng lượt mua bằng 0, trong khi trung bình 7 ngày
   vẫn có lượt mua.
3. **Tất cả đều bằng 0:** mọi chỉ số bằng 0 trong khi chi tiêu cũng bằng 0, nhưng 7 ngày trước đó
   luôn có chi tiêu — dấu hiệu token hoặc bộ lọc hỏng.

Khi phát hiện, hệ thống **vẫn gửi báo cáo** nhưng thêm một dòng cảnh báo ở đầu:
*"⚠️ Số liệu kỳ này trông bất thường: [lý do]. Nên kiểm tra lại trước khi tin."*
Không tự ý chặn báo cáo — Đại là người quyết định.

---

## 8. Bảo mật

- **Chỉ trả lời đúng `TELEGRAM_CHAT_ID` của Đại.** Tin từ chat_id khác bị bỏ qua và ghi nhật ký.
  Không có hàng rào này, người lạ tìm ra bot có thể hỏi được số liệu quảng cáo.
- Lần chạy đầu tiên phải **xả hết tin nhắn tồn đọng** (dùng `offset=-1`), nếu không bot sẽ trả lời
  một loạt tin cũ.
- `.env` vẫn không lên GitHub. `logs/lich-su.json` nằm trong `logs/` nên cũng không lên GitHub.
- Nội dung gửi cho AI chỉ gồm số liệu tổng hợp và tên campaign — không gửi token, không gửi thông tin đăng nhập.

---

## 9. Kiểm chứng

### 9.1. Bài học từ lần trước

`HANDOFF.md` kết luận cơ chế chống trùng "đã kiểm chứng" vì chỉ thử **chạy lại tuần tự**.
Lỗi thật chỉ hiện khi chạy **đồng thời**. Lần này danh sách thử phải gồm những tình huống khó chịu thật,
không chỉ đường đi thuận lợi.

### 9.2. Danh sách phải thử

| # | Tình huống | Kết quả mong đợi |
|---|---|---|
| 1 | Chạy `--thu` toàn bộ | Chạy hết luồng, không gửi gì, không ghi sổ |
| 2 | Đặt giờ giả tới mốc 17h | Gửi đúng báo cáo mốc 17h, không gửi lần hai |
| 3 | Tắt tiến trình giữa lúc đang chạy, bật lại | Tự phát hiện mốc bị lỡ, gửi bù **đúng mốc đó** |
| 4 | Giả lập mất mạng khi gọi Meta | Thử lại, rồi cảnh báo — không im lặng |
| 5 | Giả lập AI lỗi | Báo cáo vẫn gửi, thiếu phần nhận định, có ghi chú |
| 6 | Giả lập token Meta chết | Cảnh báo đúng nội dung, hướng dẫn đúng |
| 7 | Nhắn tin từ một chat_id lạ | Bị bỏ qua, ghi nhật ký |
| 8 | Nhắn "còn sống không?" | Trả lời kèm tình trạng |
| 9 | Nhắn một câu hỏi cần số liệu | Trả lời đúng số, lấy từ lịch sử |
| 10 | Bật máy sau 2 ngày tắt | Không gửi trùng, không gửi loạt báo cáo cũ |

Bốn tình huống đầu là quan trọng nhất — chúng nhắm thẳng vào hai lỗi đang hoạt động.

---

## 10. Việc Đại phải làm

1. **Lấy chìa khoá AI (Gemini)** — có hướng dẫn từng bước riêng, khoảng 5 phút, có bản miễn phí.
   Dán vào `.env` ở dòng `GEMINI_API_KEY`.
2. Bấm **`cai-dat-nguoi-truc.bat`** (một lần, cần quyền Admin).
3. Bấm **`go-lich.bat`** để tắt bốn lịch cũ.
4. Nhắn thử bot một câu.

Phần code, viết tài liệu, gỡ lỗi — AI làm.

---

## 11. Rủi ro đã biết

| Rủi ro | Mức | Cách xử lý |
|---|---|---|
| Tiến trình thường trú chết im lặng | Trung bình | Windows tự bật lại; nhịp tim trong nhật ký; lệnh "còn sống không?" |
| Tự gia hạn token không khả thi | Trung bình | Thử trước; nếu không được thì giữ cảnh báo sớm 7 ngày |
| Lần cài đầu phức tạp hơn lần trước | Thấp | Cài theo từng giai đoạn, mỗi giai đoạn chạy thử được ngay |
| Chi phí gọi AI | Thấp | 3 lần/ngày + vài câu hỏi; ước tính dưới 1 USD/tháng |
| Trả lời sai câu hỏi | Trung bình | AI chỉ đọc số do công cụ trả về, không tự bịa số; câu trả lời ghi rõ khoảng thời gian |

---

## 12. Thứ tự thi công đề xuất

Mỗi giai đoạn đứng độc lập được và chạy thử được ngay.

| Giai đoạn | Nội dung | Giá trị đem lại |
|---|---|---|
| **0** | Thử nghiệm tự gia hạn token | Biết được có nên hứa tính năng này không |
| **1** | `lich-su.py` + `report.py --slot` | **Chữa cả hai lỗi đang hoạt động.** Chưa cần AI. |
| **2** | `nguoi-truc.py` + hai file `.bat` cài/gỡ | Thay bốn lịch, hết gửi trùng tận gốc |
| **3** | `ai.py` — viết nhận định | Mục NHẬN ĐỊNH có nội dung thật |
| **4** | `ai.py` — trả lời câu hỏi | Đại nhắn hỏi được |
| **5** | Tự xử lý lỗi + tự gia hạn token | Bớt phải làm tay |

**Giai đoạn 1 và 2 đã đủ để chữa hai lỗi đang chạy.** Ba giai đoạn sau mới là phần AI.
Nếu giữa đường Đại muốn dừng, dừng sau giai đoạn 2 vẫn là một hệ thống tốt hơn hiện tại.

**Mỗi giai đoạn nên có kế hoạch thi công riêng**, không gộp sáu giai đoạn vào một kế hoạch lớn.
Lý do: giai đoạn 0 chỉ là thử nghiệm (kết quả là một câu trả lời, không phải code giữ lại);
giai đoạn 1 và 2 chữa lỗi và có thể giao được ngay; giai đoạn 3–5 phụ thuộc vào việc chìa khoá AI
có hoạt động hay không. Gộp lại sẽ khiến một chỗ tắc làm nghẽn toàn bộ.

---

## 13. Tài liệu cần cập nhật khi làm xong

- `README.md` — mục cài đặt, mục "Ba điều cần biết", mục xử lý sự cố
- `HANDOFF.md` — trạng thái mới, cách chạy mới, ghi chú kỹ thuật
- Thêm `HUONG-DAN-LAY-CHIA-KHOA-AI.md` — hướng dẫn Đại lấy chìa khoá Gemini
