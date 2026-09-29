# ĐỊNH NGHĨA AI AGENT — VÀ HỆ THỐNG FACEBOOK ADS CỦA ĐẠI

**Ngày:** 29/09/2026
**Người duyệt:** Đại
**Trạng thái:** Chờ Đại đọc và duyệt — chưa động vào code
**Đây là:** việc #1 trong ba việc Đại đã chốt (làm theo thứ tự 1 → 2 → 3)

---

## 0. TÓM TẮT TRONG NỬA TRANG

**Hệ thống đang chạy của Đại chưa phải AI Agent.** Nó là *tự động hóa có AI viết văn*.
Điều này không phải lỗi — bản thiết kế "Người trực" ngày 28/09 **cố ý** làm như vậy, vì báo cáo
tiền bạc thì không được để AI quyết định con số. Quyết định đó vẫn đúng và nên giữ.

Nhưng nếu Đại muốn một **AI Agent đúng nghĩa** cho Facebook Ads, thì đó là một hệ thống **mới**,
đứng cạnh hệ thống cũ, không phải một bản sửa của hệ thống cũ.

Bốn thứ một AI Agent bắt buộc phải có, và hệ thống hiện tại có/thiếu:

| Đặc tính | Hệ thống hiện tại |
|---|---|
| **Mục tiêu** — biết "tốt" là gì | ❌ Không có. Nó mô tả số, không phán xét số |
| **Vòng lặp** — tự quyết bước kế tiếp | ⚠️ Có, nhưng chỉ trong nhánh hỏi đáp, tối đa 3 lượt |
| **Công cụ** — tác động ra thế giới | ❌ Bốn công cụ đều chỉ **đọc** |
| **Trí nhớ** — nhớ việc mình đã làm | ⚠️ Nhớ **số liệu**, không nhớ **hành động** |

**Một sự thật kỹ thuật phải nói trước:** tôi đã hỏi thẳng Meta bằng token của Đại (ngày 29/09/2026).
Token hiện có quyền `ads_read`, `business_management`, `public_profile` — và **không có**
`ads_management`. Nghĩa là: **với token đang có, không agent nào tắt được camp hay đổi ngân sách.**
Muốn tự hành động thì phải xin lại token, và đó là việc Đại phải làm tay trong giao diện Meta.

**Đề nghị của tôi:** làm theo ba bước, mỗi bước dừng lại cho Đại xem kết quả. Đừng nhảy thẳng
sang "agent tự tắt camp" — vì lúc đó tiền thật đã bị tác động bởi một thứ Đại không đọc được code.

---

## 1. AI AGENT LÀ GÌ — ĐỊNH NGHĨA CHẶT

### 1.1. Định nghĩa một câu

> **AI Agent là một hệ thống trong đó AI tự quyết định hành động kế tiếp, dựa trên kết quả của
> hành động vừa làm, cho tới khi đạt được mục tiêu — và đường đi không được vẽ sẵn từ trước.**

Chữ quan trọng nhất là **"không được vẽ sẵn"**. Nếu người viết code biết trước ở mỗi bước hệ thống
sẽ làm gì, thì đó là script tự động, không phải agent. Trí thông minh nằm ở chỗ hệ thống tự chọn
đường, kể cả khi đường đó không ai lường trước.

### 1.2. Bốn đặc tính bắt buộc — thiếu một là không phải agent

| # | Đặc tính | Nghĩa là gì | Thiếu nó thì sao |
|---|---|---|---|
| 1 | **Mục tiêu** | Biết mình đang cố đạt cái gì, và đo được đã đạt chưa | Hệ thống chỉ mô tả, không bao giờ biết nên làm gì |
| 2 | **Vòng lặp** | Quan sát → suy nghĩ → hành động → quan sát lại, lặp tới khi xong | Hệ thống chỉ chạy một lượt rồi dừng |
| 3 | **Công cụ** | Có khả năng **thay đổi** thế giới bên ngoài, không chỉ sinh chữ | Hệ thống chỉ biết nói, không làm được gì |
| 4 | **Trí nhớ** | Nhớ việc mình đã làm và kết quả ra sao, để lần sau khác lần trước | Hệ thống lặp lại sai lầm cũ mãi mãi |

### 1.3. Phân biệt bốn loại — để không tự lừa mình

| Loại | Ai quyết định bước kế tiếp | Có tác động ra ngoài? | Thí dụ |
|---|---|---|---|
| **Script tự động** | Người viết code | Không | `report.py` chạy lúc 8h |
| **Chatbot** | Người dùng hỏi gì thì đáp nấy | Không | Bot trả lời số liệu (GĐ4) |
| **Workflow** | Người thiết kế, theo sơ đồ cố định | Có, nhưng theo đường đã vẽ | Zapier, n8n |
| **AI Agent** | **Chính AI** | **Có** | Hệ thống tự thấy camp đốt tiền rồi tự tắt |

Ranh giới giữa **workflow** và **agent** là chỗ dễ nhầm nhất. Một workflow có 20 nhánh vẫn là
workflow, vì người thiết kế đã vẽ đủ 20 nhánh. Một agent có thể chỉ có 3 công cụ, nhưng nó
**tự quyết** dùng công cụ nào, theo thứ tự nào, và khi nào dừng.

### 1.4. Ba mức tự hành — dùng thống nhất từ đây về sau

| Mức | Tên | AI được làm gì | Rủi ro |
|---|---|---|---|
| **Mức 1** | Đọc và nói | Đọc số, viết nhận xét, trả lời câu hỏi | Không có — sai thì chỉ sai lời |
| **Mức 2** | Đọc, nói, **đề xuất** | Thêm: đề xuất hành động cụ thể ("tắt camp X vì...") | Thấp — Đại vẫn là người bấm |
| **Mức 3** | **Tự hành có trần** | Thêm: tự làm trong giới hạn Đại đặt ra | **Tiền thật bị tác động** |

Hệ thống hiện tại đang ở **giữa Mức 1 và Mức 2** (nó nhận xét được nhưng không đề xuất hành động).
Đích Đại đã chốt là **Mức 3**. Đường đi đề nghị: Mức 2 trước, Mức 3 sau.

---

## 2. HỆ THỐNG HIỆN TẠI CỦA ĐẠI — SOI THEO ĐỊNH NGHĨA

### 2.1. Những gì đã có (đáng ghi nhận, đừng làm lại)

Đọc kỹ `ai.py`, `cong_cu.py`, `nguoi_truc.py` ngày 29/09/2026:

- **Tiến trình thường trú** `nguoi_truc.py` — chạy suốt khi máy bật, biết rõ lịch của chính nó.
  Đây là hạ tầng đúng, agent sẽ ở lại trong đó.
- **Vòng lặp công cụ** trong `ai.py::tra_loi()` (dòng 514) — AI tự xin gọi công cụ, code chạy
  công cụ, trả kết quả về, AI gọi tiếp. Giới hạn 3 lượt, có ngân sách thời gian 180 giây.
  **Đây chính là mầm mống của một agent** — nó đã đúng về hình dạng.
- **Bốn công cụ**: `lay_mot_ngay`, `lay_khoang`, `xep_hang_camp`, `so_sanh` (`cong_cu.py` dòng 155).
- **Bộ nhớ số liệu**: `logs/lich-su.json`, giữ 180 ngày, ghi **trước** khi gửi báo cáo.
- **Xử lý lỗi chín**: phân biệt lỗi tạm thời / vĩnh viễn, model dự phòng, suy giảm êm.

Nói thẳng: phần hạ tầng này tốt hơn mặt bằng chung. Agent xây trên nền này sẽ không phải làm lại
chuyện mạng, chuyện lỗi, chuyện trần AI.

### 2.2. Những gì còn thiếu — bảng đối chiếu bốn đặc tính

| Đặc tính | Trạng thái | Chi tiết thiếu |
|---|---|---|
| **Mục tiêu** | ❌ Thiếu hẳn | Không có chỗ nào trong code định nghĩa "kết quả tốt". Hệ thống biết `cpr` (chi phí mỗi đơn) là bao nhiêu, nhưng không biết bao nhiêu thì gọi là tốt, và không biết nên làm gì khi nó xấu |
| **Vòng lặp** | ⚠️ Có nhưng hẹp | Vòng lặp chỉ chạy khi **Đại nhắn tin**. Không có vòng lặp nền. AI không bao giờ tự khởi xướng việc gì |
| **Công cụ** | ❌ Toàn đọc | Cả bốn công cụ chỉ đọc `lich-su.json`. **Không một công cụ nào ghi.** AI có thể nói "camp X tệ" nhưng không thể làm gì với nó |
| **Trí nhớ** | ⚠️ Nhớ số, quên việc | `lich-su.json` nhớ số liệu. Không có chỗ nào nhớ "ngày 29/09 tôi đã đề xuất tắt camp X, Đại đã tắt, kết quả ra sao" |

### 2.3. Kết luận trung thực

Hệ thống hiện tại là: **tự động hóa chín + AI viết văn + một công cụ tra cứu thông minh.**

Nó **không phải** agent, và **không nên trở thành** agent bằng cách sửa tại chỗ. Ba lý do:

1. **Xung đột mục tiêu.** Báo cáo cần số **giống hệt nhau ở mọi lần chạy**. Agent cần **tự do
   quyết định**. Nhét hai thứ vào một chỗ là mời tai nạn.
2. **Trần AI.** Gemini miễn phí cho **20 lượt/ngày/model** — đã đo thật. Agent chạy nền liên tục
   sẽ ăn hết lượt của báo cáo, và Đại sẽ mất phần nhận định mà không hiểu vì sao.
3. **Rủi ro tiền.** Hệ thống báo cáo sai thì Đại đọc một con số sai. Agent sai thì Đại **mất tiền
   thật**. Hai mức hậu quả khác nhau, phải tách nhau ra.

⇒ **Agent phải là thư mục riêng, tiến trình riêng, model AI riêng, và có trần riêng.**

---

## 3. ĐÍCH ĐẾN: "TỰ HÀNH CÓ TRẦN" NGHĨA LÀ GÌ CỤ THỂ

### 3.1. Cái trần gồm năm thứ — và cả năm đều phải là CODE, không phải lời dặn AI

Đây là bài học lớn nhất rút từ dự án này. `ai.py` dòng 11–13 ghi:

> *"PHEP SO SANH DO CODE LAM, khong giao cho AI. Ly do: khi AI phai tu doi chieu hai dong so voi
> nhau, no de doc sai ma cau van van troi chay."*

Áp dụng y nguyên cho quyền hạn:

> **GIỚI HẠN QUYỀN DO CODE LÀM, không giao cho AI tự giác.**

Nghĩa là: không viết trong câu lệnh cho AI "đừng tăng ngân sách quá 20%". Mà viết một hàm
`rao_an_toan.py` **chặn đứng** lệnh đó trước khi nó tới Meta. AI có thể xin gì cũng được; rào chặn
là thứ quyết định. Nếu AI bị lừa hoặc hiểu sai, rào vẫn đứng.

| # | Cái trần | Nội dung | Chặn ở đâu |
|---|---|---|---|
| 1 | **Danh sách trắng** | Chỉ được đụng camp có tên chứa `dainq` (khớp bộ lọc báo cáo hiện có). Mọi camp khác: cấm tuyệt đối | Trước khi gửi lệnh lên Meta |
| 2 | **Trần tiền** | Không tăng ngân sách quá X% và không quá Y đồng/ngày cho một camp. Không tăng tổng ngân sách tài khoản quá Z% | Trước khi gửi lệnh |
| 3 | **Cấm đụng camp đang hiệu quả** | Camp có ≥ N đơn trong 3 ngày gần nhất: **cấm tắt**, dù AI nói gì | Trước khi gửi lệnh |
| 4 | **Hạn mức hành động** | Tối đa K hành động/ngày và M hành động/giờ. Vượt: dừng, báo Đại | Bộ đếm trong `ky_uc.py` |
| 5 | **Ghi sổ bắt buộc** | Mọi hành động phải ghi vào `logs/nhat-ky-agent.json` **trước** khi gửi lên Meta, và báo Telegram **ngay sau** khi gửi | Cứng, không tắt được |

### 3.2. Chế độ tập sự — điều kiện bắt buộc trước khi cho phép ghi

Trong **1–2 tuần đầu**, agent chạy ở **chế độ tập sự** (shadow mode):

```
Agent phân tích → viết ra "tôi SẼ tắt camp X, vì lý do Y"
                 → ghi vào nhật ký
                 → gửi Telegram cho Đại đọc
                 → NHƯNG KHÔNG GỬI LỆNH NÀO LÊN META
```

Đại đọc vài ngày, tự đối chiếu: agent đoán đúng bao nhiêu phần trăm? Nếu đúng nhiều thì mở quyền
ghi thật. Nếu sai nhiều thì sửa câu lệnh, chưa mất đồng nào.

**Đây là bước không được bỏ.** Không có nó, lần đầu agent sai là Đại mất tiền thật, và Đại không
có cách nào biết trước.

### 3.3. Điều kiện kỹ thuật bắt buộc — ĐÃ KIỂM CHỨNG, KHÔNG ĐOÁN

**Phép đo ngày 29/09/2026** — gọi thẳng `debug_token` và `me/permissions` của Meta bằng token thật:

| Câu hỏi | Kết quả đo được |
|---|---|
| Token còn sống? | Có, hết hạn  |
| Loại token | `USER` (token người dùng) |
| Quyền được cấp | `ads_read`, `business_management`, `public_profile` |
| Có `ads_management` (quyền ghi)? | **KHÔNG** |

⇒ **Kết luận: phải xin lại token.** Không có đường vòng.

Ba việc Đại phải làm tay (giống hệt quy trình `HUONG-DAN-DIEN-TOKEN.md` đã có):

```
1. Vào developers.facebook.com → Graph API Explorer
2. Ở phần Permissions, tick THÊM quyền  ads_management  (hiện chỉ có ads_read)
3. Generate Access Token → xác nhận → đổi sang token 60 ngày như cũ
```

**⚠️ Ba điều chưa kiểm chứng, phải nói rõ là chưa:**

1. **Chưa chắc Meta cho dùng `ads_management`.** Đây là quyền nâng cao. App của Đại đang ở chế độ
   Development — thường thì chủ app dùng được, nhưng **chưa thử lần nào**. Phải thử trước khi hứa.
2. **Token người dùng 60 ngày là quá ngắn cho một agent.** Agent tự hành mà chết sau 60 ngày thì
   không gọi là tự hành. Hướng đúng là **System User token** trong Business Manager — có tuỳ chọn
   không bao giờ hết hạn. Đã ghi trong `HUONG-DAN-DIEN-TOKEN.md` từ trước, **vẫn chưa ai thử**.
3. **Chưa đo được giới hạn tần suất ghi của Meta.** Meta giới hạn số lệnh ghi mỗi giờ. Chưa biết
   ngưỡng thật của tài khoản Đại. Phải đo bằng cách ghi thử vài lệnh vô hại.

⇒ **Việc đầu tiên của #3 là một phép thử, không phải viết code.** Xin token có `ads_management`,
gọi thử một lệnh ghi **vô hại** (ví dụ đổi tên một camp nháp, hoặc tạm dừng rồi bật lại ngay một
camp trong danh sách trắng), rồi báo kết quả. Chỉ khi phép thử đạt mới tính chuyện xây tiếp.

---

## 4. KIẾN TRÚC ĐỀ XUẤT

### 4.1. Vòng lặp chính

Khác hẳn `nguoi_truc.py` (chỉ thức dậy khi tới mốc giờ), agent có **nhịp riêng**:

```
mỗi 30 phút (cấu hình được, mặc định 30):

  1. QUAN SÁT   đọc số liệu hiện tại (từ lich-su.json, hoặc gọi Meta nếu cần số mới)
  2. SO SÁNH    đối chiếu với ký ức: có gì đổi so với lần trước?
  3. PHÁN XÉT   có gì đáng làm không?  ← ĐÂY là chỗ AI suy nghĩ
  4. QUYẾT ĐỊNH nếu có → xin hành động
  5. RÀO CHẶN   rao_an_toan.py kiểm. Chặn thì thôi, không làm
  6. HÀNH ĐỘNG  gửi lệnh lên Meta (chỉ khi đã qua chế độ tập sự)
  7. GHI KÝ ỨC  ghi việc đã làm + lý do
  8. BÁO ĐẠI    gửi Telegram
  9. THEO DÕI   lần chạy sau, kiểm hậu quả hành động đó
```

Bước 9 quan trọng và dễ quên: agent phải biết hành động của mình có kết quả tốt hay không. Không
có bước này thì nó chỉ là "làm rồi báo", không học được gì.

### 4.2. Các khối — mỗi khối một việc, tách rời được

| File | Việc duy nhất | Phụ thuộc |
|---|---|---|
| `agent.py` | Vòng lặp. Không chứa logic nghiệp vụ | tất cả dưới |
| `muc_tieu.py` | Định nghĩa "tốt" là gì, đo được | đọc `lich-su.json` |
| `ky_uc.py` | Nhật ký hành động: đã làm gì, vì sao, kết quả ra sao | `logs/nhat-ky-agent.json` |
| `cong_cu_ghi.py` | Công cụ ghi: tắt camp, bật camp, đổi ngân sách | Meta API |
| `rao_an_toan.py` | **Cái trần.** Hàm thuần, không gọi mạng, kiểm được bằng unit test | không |
| `theo_doi.py` | Đo hậu quả của hành động đã làm | `ky_uc.py` |

**`rao_an_toan.py` là file quan trọng nhất trong cả hệ thống.** Nó phải là **hàm thuần** — nhận
một đề xuất hành động, trả về "cho phép" hoặc "chặn + lý do". Không gọi mạng, không đọc file,
không phụ thuộc AI. Nhờ vậy nó kiểm thử được từng trường hợp một, và nhờ vậy nó **không thể bị AI
thuyết phục**.

Đây là điểm khác biệt giữa "agent an toàn" và "agent nguy hiểm": ở hệ thống an toàn, thứ quyết định
cuối cùng là một hàm 50 dòng không có AI trong đó.

### 4.3. Bộ nhớ — hai loại, đừng lẫn

| Loại | File | Nội dung | Đã có? |
|---|---|---|---|
| Nhớ **số** | `logs/lich-su.json` | Số liệu từng ngày, từng mốc | ✅ Có sẵn, dùng lại |
| Nhớ **việc** | `logs/nhat-ky-agent.json` | Đã đề xuất/làm gì, vì sao, kết quả | ❌ Phải viết mới |

Nhớ **việc** là thứ biến hệ thống từ "chạy lại y hệt mỗi ngày" thành "biết mình đã thử gì". Ví dụ
một bản ghi:

```json
{
  "luc": "2026-10-02T14:30:00+07:00",
  "che_do": "tap_su",
  "quan_sat": "camp 'dainq-mua-3' chi 480.000d, 0 don, 4 ngay lien tiep",
  "de_xuat": "tam dung camp dainq-mua-3",
  "ly_do": "chi tieu 4 ngay lien tuc khong ra don, CPR khong do duoc",
  "rao_an_toan": "cho phep",
  "da_gui_len_meta": false,
  "dai_phan_hoi": null,
  "ket_qua_sau_24h": null
}
```

`dai_phan_hoi` và `ket_qua_sau_24h` là hai trường để trống, điền sau. Đây là chỗ học.

### 4.4. Về việc dùng AI nào

**Phải dùng model riêng, không dùng chung với báo cáo.** Lý do đã đo được: Gemini miễn phí cho
20 lượt/ngày/**model**. Agent chạy 30 phút một lần là 48 lượt/ngày — vượt trần ngay.

Ba lựa chọn, xếp theo mức tôi khuyến nghị:

1. **Không dùng AI cho vòng lặp nền.** Viết luật bằng code ("camp chi > 0, đơn = 0, 3 ngày liền →
   đề xuất tắt"). AI chỉ dùng khi cần **diễn giải** một tình huống lạ. Rẻ, ổn định, dễ kiểm thử.
   **Đây là lựa chọn tôi khuyến nghị cho giai đoạn đầu.**
2. **AI chạy theo lô.** Gom 1 ngày số liệu, gọi AI **một lần** để phán xét cả ngày. Tốn 1–2 lượt/ngày.
3. **AI chạy mỗi vòng.** Tốn 48 lượt/ngày ⇒ phải trả tiền. Chưa cần.

Nói thẳng: **agent không nhất thiết phải để AI quyết mọi bước.** Một vòng lặp bằng luật code, có
AI tham gia ở đúng một chỗ khó, vẫn là agent đúng nghĩa — vì nó tự chạy, tự quyết, tự nhớ. Và nó
là loại agent Đại kiểm tra được.

---

## 5. BA VIỆC 1–2–3 — ĐƯỜNG ĐI CỤ THỂ

| Việc | Nội dung | Đụng vào đâu | Cần token mới? |
|---|---|---|---|
| **#1** | Bản định nghĩa này | Chỉ tài liệu | Không |
| **#2** | Nâng hệ thống **hiện có** lên Mức 2: AI không chỉ nhận xét mà **đề xuất hành động cụ thể**, có kèm số và lý do, gửi vào Telegram | `ai.py` (thêm mục đề xuất), `report.py` (chỗ ghép báo cáo) | Không |
| **#3** | **Agent mới, tách riêng**, Mức 3, có trần | Thư mục mới, code mới | **Có** |

Chi tiết việc #2 — nó nhỏ hơn vẻ ngoài:

Hiện `viet_nhan_dinh()` chỉ viết 3–5 câu nhận xét. Nâng lên Mức 2 nghĩa là **thêm một mục
"ĐỀ XUẤT"** vào báo cáo, trong đó AI nói rõ: camp nào, làm gì, vì sao, số nào chống lưng. Vẫn giữ
nguyên tắc cũ: **AI chỉ chép số đã tính sẵn**, không tự tính. Không cần token mới, không cần thêm
lượt AI (vẫn một lần gọi, chỉ đổi câu lệnh).

Làm #2 trước #3 có lợi rõ ràng: Đại đọc đề xuất của AI vài ngày, **đối chiếu với việc Đại tự
quyết**, rồi mới biết có nên cho AI cầm quyền. Đây là cách đo độ chính xác mà không mất tiền.

---

## 6. NHỮNG ĐIỀU TÔI KHÔNG KHUYẾN NGHỊ — VÀ VÌ SAO

| Không nên | Vì sao |
|---|---|
| Cho AI tự tính tiền, tự cộng số | Đã chứng minh sai trong dự án này. Code tính, AI chép |
| Cho agent đụng tài khoản ngoài danh sách trắng | Một tài khoản khác của khách, agent tắt camp là Đại mang tiếng |
| Chạy agent không có nhật ký | Khi có chuyện, không ai biết nó đã làm gì lúc nào |
| Nhét agent vào `nguoi_truc.py` | Trần AI 20 lượt/ngày, và xung đột mục tiêu với báo cáo |
| Bật quyền ghi ngay từ đầu | Không có dữ liệu để biết agent đoán đúng bao nhiêu phần trăm |
| Để AI tự đọc `.env` | Quy ước cũ của dự án: `soan_prompt()` không nhận `env`, nên về cấu trúc không thể lộ token. Giữ nguyên |
| Chạy agent khi máy đang ngủ / không có ai xem | Giai đoạn đầu nên chạy lúc Đại có mặt |

---

## 7. CÂU HỎI CẦN ĐẠI CHỐT TRƯỚC KHI VIẾT CODE

Trả lời được năm câu này là đủ để bắt đầu việc #2 và #3:

1. **Mục tiêu tối ưu là gì?** Giảm chi phí mỗi đơn (CPR)? Tăng số đơn? Hay chỉ giữ ổn định và
   cảnh báo khi có bất thường?
2. **Trần tiền cụ thể là bao nhiêu?** Ví dụ: "không tăng ngân sách quá 20% và không quá 500.000đ
   mỗi ngày cho một camp".
3. **Agent được đụng vào camp nào?** Giữ nguyên luật cũ là tên chứa `dainq`, hay mở rộng?
4. **Bao nhiêu hành động mỗi ngày là chấp nhận được?** Ví dụ: tối đa 3 hành động/ngày.
5. **Chế độ tập sự bao lâu?** Đề nghị 1–2 tuần. Đại có muốn tự đặt con số không?

Không cần trả lời hết ngay trong một lần. Câu 1 và câu 2 là hai câu chặn đường.

---

## 8. RỦI RO — NÓI THẲNG

| Rủi ro | Mức | Cách xử lý |
|---|---|---|
| Meta không cấp `ads_management` cho app ở chế độ Development | **Cao** — chặn cả việc #3 | Thử **trước tiên**, trước khi viết dòng code nào. Không được thì việc #3 dừng ở Mức 2 |
| Token 60 ngày chết giữa lúc agent đang chạy | Trung bình | Chuyển sang System User token (không hết hạn). Nếu không được thì nhắc sớm 30 ngày như hiện có |
| Agent tắt nhầm camp đang chạy tốt | **Cao** — mất tiền thật | Danh sách trắng + cấm tắt camp có đơn + chế độ tập sự + nút hoàn tác 24h |
| AI hiểu sai số liệu rồi đề xuất sai | Trung bình | Rào an toàn là code; AI chỉ được chép số đã tính |
| Agent chạy nền ăn hết trần AI của báo cáo | Trung bình | Model riêng, hoặc không dùng AI cho vòng lặp nền |
| Đại không đọc được code nên không biết agent sai lúc nào | **Cao** | Mọi hành động báo Telegram ngay; nhật ký ghi bằng tiếng Việt có dấu, không phải log kỹ thuật |
| Chi phí gọi AI vượt dự tính | Thấp | Bắt đầu bằng luật code; đo trước khi mở rộng |

Rủi ro lớn nhất **không phải kỹ thuật** mà là: Đại giao quyền cho một hệ thống Đại không đọc
được. Cách chống duy nhất là **chế độ tập sự** và **báo cáo mọi hành động**. Hai thứ đó không
phải tính năng phụ — chúng là điều kiện để việc #3 được phép tồn tại.

---

## 9. VIỆC TIẾP THEO NGAY SAU KHI ĐẠI DUYỆT BẢN NÀY

1. Đại trả lời câu 1 và câu 2 ở mục 7 (mục tiêu, trần tiền).
2. Tôi làm **việc #2** — thêm mục ĐỀ XUẤT vào báo cáo. Không cần token mới, làm được ngay.
3. Song song, Đại thử **xin token có `ads_management`** — đây là phép thử quyết định việc #3 có
   khả thi hay không.
4. Chỉ khi cả hai xong mới bàn tới việc #3.
