# Kế hoạch: Thông báo khi agent tự hành + vá lỗ hổng Rào 8

Ngày lập: 03/10/2026
Người duyệt: Đại
Trạng thái: **CHỜ ĐẠI DUYỆT** (chưa sửa code thật)

---

## 1. Bối cảnh — vì sao cần làm

Ngày 03/10/2026, Đại hỏi vì sao chiến dịch `120250389649450509` phải tắt tay và không
thấy thông báo Telegram. Điều tra cho thấy:

- **Agent ĐÃ tự làm** đủ luồng (tắt nhóm → tắt quảng cáo → đổi tên hậu tố → tắt chiến dịch
  TH2 CBO) lúc 10:58–10:59. Đại không biết vì **agent làm im lặng**.
- **Không có thông báo** vì Rào 8 (`HAN_HOI_LAI_PHUT = 24*60`) chặn hỏi lại nhóm Đại đã
  trả lời lúc 10-02 11:45. Đúng thiết kế, nhưng Đại không được báo gì.
- **Hệ quả tâm lý:** Đại tưởng bot chết, tự vào Meta tắt tay. Mất niềm tin vào agent.

Kết luận: thiếu **kênh thông báo một chiều từ agent → Đại**. Mọi tin hiện có đều là
"xin phép" (cần Đại bấm nút). Không có tin nào báo "tôi vừa làm X".

---

## 2. Ba việc Đại đã chốt

| # | Việc | Mục đích |
|---|---|---|
| 1 | **Thông báo khi agent tự hành** tới chiến dịch / nhóm / quảng cáo | Đại luôn biết agent vừa làm gì, dù không bấm nút |
| 2 | **Vá Rào 8** theo đề xuất của tôi | Nhóm đã tắt rồi được BẬT LẠI rồi chạm ngưỡng lần nữa → phải hỏi lại |
| 3 | Giải thích **token App là gì, lấy ở đâu** | Để nhật ký Meta tách bạch người với máy |

Kế hoạch này thi công việc 1 và 2. Việc 3 chỉ là hướng dẫn (không sửa code).

---

## 3. VIỆC 1 — Thông báo khi agent tự hành

### 3.1. Vấn đề cốt lõi: định nghĩa "tự hành" cho đúng

Agent hiện có **hai** đường ghi lên Meta:

| Đường | Đặc điểm | Có phải "tự hành"? |
|---|---|---|
| **A. Theo nút Đại bấm** | `_lam_theo_dong_y` — chỉ chạy sau khi Đại bấm | **KHÔNG** — Đại đã biết, vì chính Đại bấm |
| **B. Tự làm khi phát hiện** | TH2 tắt chiến dịch, chuyển NS nhóm sống | **CÓ** — đây là chỗ Đại bị mù |

⇒ Chỉ báo khi đi đường **B**. Nếu báo cả đường A thì thành spam, vì đường A Đại vừa
bấm xong đã nhận tin "✅ ĐÃ TẮT NHÓM" rồi.

**Điểm móc (hook) duy nhất:** sau khi `xu_ly_th2_cbo()` trả về, trong `_lam_theo_dong_y`,
nhánh `if cbo:` của `agent.py`. Đây là chỗ TH2 tắt chiến dịch.

Nguồn "tự hành" khác cần báo: khi `tat_nhom_cbo` **chuyển ngân sách sang nhóm sống**
(`chuyen_ns_ket_qua`) — Đại cũng không biết việc này.

### 3.2. Nội dung tin nhắn

Một tin ngắn, tiếng Việt, có dấu, không quá 6 dòng:

```
🤖 AGENT TỰ LÀM (không cần Đại bấm)

Vừa tắt CHIẾN DỊCH: 2026 - 09 - 15 - dainq - Scale - Online MUA - LTT X
Mã: 120250389649450509
Lý do: nhóm cuối cùng trong chiến dịch vừa bị tắt, không còn nhóm nào chạy
Ngân sách chiến dịch: hạ về 27.000đ
Lúc: 10:59 ngày 03/10/2026
```

Nếu có chuyển ngân sách, thêm một dòng:

```
Ngân sách chuyển sang nhóm sống: 2026 - ... - dainq - ... A1 → 400.000đ
```

### 3.3. Cách làm

**Thêm hàm thuần mới** `soan_tin_tu_hanh(chi_tiet, bay_gio)` vào `agent_xin_phep.py`
(module chuyên soạn tin — đã có `soan_tin`, `soan_tin_loi`, `dong_doi_tuong`).

- **Hàm THUẦN**: không gọi mạng, không đọc file → kế thừa được cách kiểm thử hiện có.
- Trả về `str`. Danh sách rỗng thì trả `""` (không gửi gì).

**Gọi ở đâu:** trong `agent.py`, nhánh `if cbo:` của `_lam_theo_dong_y`, sau khi
`xu_ly_th2_cbo` chạy xong và `thanh_cong` vẫn đúng:

```python
if cbo:
    ...
    if thanh_cong:
        ok_th2, msg_th2, ct_th2 = agent_cong_cu_ghi.xu_ly_th2_cbo(...)
        ...
        # ← MỚI: báo Đại biết agent vừa tự làm gì
        if ct_th2.get("tat_chien_dich"):
            _bao_tu_hanh(env, thong_bao, ct_th2, chi_tiet, bay_gio)
```

**Hàm `_bao_tu_hanh`** (mới, trong `agent.py`): gọi `agent_xin_phep.soan_tin_tu_hanh`,
nếu chuỗi khác rỗng thì `thong_bao(chuỗi)`.

### 3.4. Chống spam — gửi trùng

Agent quét mỗi `AGENT_NHIP_PHUT` phút. Nếu một nhóm chạm ngưỡng mà Meta từ chối liên tục,
agent có thể lặp. Nhưng TH2 chỉ chạy **một lần** cho mỗi chiến dịch: lần sau
`active_count` đã là 0 và chiến dịch đã PAUSED → `xu_ly_th2_cbo` đọc lại thấy chiến dịch
đã tắt, không ghi lại. ⇒ Không cần thêm cơ chế chống trùng. Ghi rõ điều này trong test.

### 3.5. Ca kiểm thử (viết TRƯỚC khi sửa code)

| # | Tình huống | Mong đợi |
|---|---|---|
| T1 | `chi_tiet` có `tat_chien_dich=True`, đủ dữ liệu | Chuỗi chứa "AGENT TỰ LÀM", tên chiến dịch, mã, lý do |
| T2 | `chi_tiet` không có `tat_chien_dich` (TH1 thường) | Trả chuỗi rỗng → KHÔNG gửi |
| T3 | `chi_tiet` thiếu tên chiến dịch | Vẫn soạn được, dùng mã thay tên |
| T4 | Có `chuyen_ns_ket_qua` | Chuỗi có thêm dòng chuyển ngân sách |
| T5 | Không có dữ liệu giờ | Vẫn soạn được, bỏ dòng "Lúc:" |
| T6 | `chi_tiet` là None / không phải dict | Trả chuỗi rỗng, không ném lỗi |

---

## 4. VIỆC 2 — Vá lỗ hổng Rào 8

### 4.1. Lỗ hổng chính xác là gì

```
10-02 11:45  Đại bấm "tắt" nhóm X          → ghi vào nhom_da_tra_loi[X]
10-02 11:45  agent tắt nhóm X, đổi tên hậu tố
10-03 09:00  Đại BẬT LẠI nhóm X (tình huống MỚI)
10-03 09:15  nhóm X chạm ngưỡng lần nữa
             → Rào 8 chặn: "Đại đã trả lời trong 24 giờ qua"
             → agent IM LẶNG suốt tới 11:45
```

Sai ở chỗ: câu trả lời cũ đã **hết giá trị** vì tình huống đã thay đổi (nhóm được bật
lại và tiêu thêm tiền). Rào 8 đang so sánh "Đại đã trả lời chưa" mà không hỏi
"câu trả lời đó còn đúng không".

### 4.2. Cách vá

Bổ sung **một điều kiện thoát** cho Rào 8: nếu nhóm đó **đã bị tắt rồi được BẬT LẠI
SAU thời điểm Đại trả lời** thì bỏ qua Rào 8 (cho phép hỏi lại).

**Sửa ở đâu:** `agent_rao.py`, Rào 8 (dòng ~279-284):

```python
# --- Rao 8: khong hoi lai nhom da co cau tra loi ---
da_tra_loi = ls.get("nhom_da_tra_loi")
if isinstance(da_tra_loi, dict):
    t_cu = _gio(da_tra_loi.get(ma))
    if t_cu is not None and (goc - t_cu) < timedelta(minutes=HAN_HOI_LAI_PHUT):
        # ⚠️ NGOAI LE (Dai chot 03/10/2026): cau tra loi cu KHONG con gia tri
        # neu nhom da duoc BAT LAI sau do va chay lai phat sinh chi tieu.
        # Xem docs/superpowers/plans/2026-10-03-thong-bao-khi-tu-hanh-va-va-rao-8.md
        t_bat_lai = _gio(ls.get("nhom_bat_lai_gan_nhat", {}).get(ma)
                         if isinstance(ls.get("nhom_bat_lai_gan_nhat"), dict) else None)
        if t_bat_lai is None or t_bat_lai <= t_cu:
            return False, "Nhóm này Đại đã trả lời trong 24 giờ qua"
```

### 4.3. Dữ liệu `nhom_bat_lai_gan_nhat` lấy từ đâu

`agent_ky_uc.py` đã có sẵn đủ dữ liệu trong `logs/nhat-ky-agent.json` — các bản ghi
`hanh_dong == "bat_lai"`. Cần **thêm một hàm mới** cùng dạng với `nhom_da_tra_loi`:

```python
def nhom_bat_lai_gan_nhat(bay_gio=None, duong_dan=None):
    """{id_nhom: thoi_diem_bat_lai_gan_nhat} — de Rao 8 biet cau tra loi cu
    da het gia tri hay chua."""
```

**🔴 LỖI KẾ HOẠCH ĐÃ BỊ DỰNG THỬ BẮT ĐƯỢC (K2):**

Bản đầu tôi viết điều kiện lọc như sau — **SAI**:

```python
if rec.get("da_gui_len_meta") is not True:
    kq = str(rec.get("ket_qua") or "")
    if "da_gui_len_meta" in rec or "thanh cong" not in kq.lower():
        continue          # ← SAI: khi co co True nhung ket_qua bao loi, VAN TINH
```

Dựng thử K2 (bản ghi `da_gui_len_meta=True` nhưng `ket_qua="loi: Meta tu choi"`)
**ĐỎ**: hàm vẫn trả về nhóm đó ⇒ Rào 8 sẽ mở oan cho nhóm **chưa hề được bật lại**,
đúng loại lỗi nguy hiểm nhất (agent hỏi lại nhóm Đại vừa trả lời).

Điều kiện ĐÚNG (đã kiểm chứng): **có cờ `True` VÀ kết quả không báo lỗi**. Bản ghi CŨ
(không có cờ) thì suy từ `ket_qua` chứa "thanh cong", giống `_la_hanh_dong_that`.

Rồi trong `agent.py::_xet_de_xuat` (dòng ~173) nạp thêm:

```python
lich_su["nhom_bat_lai_gan_nhat"] = agent_ky_uc.nhom_bat_lai_gan_nhat(bay_gio)
```

### 4.4. Ca kiểm thử (viết TRƯỚC khi sửa code)

| # | Tình huống | Mong đợi |
|---|---|---|
| R1 | Đại trả lời 2h trước, nhóm CHƯA bật lại | **CHẶN** (giữ nguyên hành vi cũ) |
| R2 | Đại trả lời 2h trước, nhóm bật lại 1h trước | **CHO PHÉP** hỏi lại |
| R3 | Đại trả lời 2h trước, nhóm bật lại 3h trước (bật TRƯỚC khi trả lời) | **CHẶN** |
| R4 | Không có dữ liệu bật lại (thiếu khoá) | **CHẶN** — an toàn, không đổi hành vi |
| R5 | Đại trả lời 25h trước | **CHO PHÉP** (đã quá 24h, hết hạn chặn) |
| R6 | `nhom_bat_lai_gan_nhat` là None / sai kiểu | **CHẶN**, không ném lỗi |
| R7 | Nhóm bật lại ĐÚNG BẰNG thời điểm trả lời | **CHẶN** (biên, ưu tiên an toàn) |
| R8 | Nhóm khác (không nằm trong danh sách trả lời) | **CHO PHÉP** — Rào 8 không liên quan |

### 4.5. Ca kiểm thử cho `nhom_bat_lai_gan_nhat`

| # | Tình huống | Mong đợi |
|---|---|---|
| K1 | Bản ghi CŨ không có cờ `da_gui_len_meta`, `ket_qua` = "thanh cong" | **Tính** (suy từ kết quả) |
| K2 | Có cờ `True` nhưng `ket_qua` báo lỗi | **KHÔNG tính** ← lỗi đã bắt bằng dựng thử |
| K3 | Nhiều lần bật lại | Lấy lần **mới nhất** |
| K4 | Bản ghi `tam_dung` | Không lẫn sang |
| K5 | File hỏng / không tồn tại | Dict rỗng, không ném lỗi |
| K6 | Đọc **sổ thật** của repo | Đọc được, có nhóm `120250506886650509` |
| K7 | Thiếu `id` hoặc thiếu `luc` | Bỏ qua bản ghi đó |

### 4.6. Kết quả dựng thử (03/10/2026)

Dựng thử ngoài repo tại `D:\Buddy Work AI\tt-rao8`, dùng **module thật** chép sang:

| Bộ kiểm thử | Kết quả |
|---|---|
| Rào 8 (R1–R8) trước khi vá | **7/8 xanh, R2 ĐỎ** ← chứng minh lỗ hổng có thật |
| Rào 8 (R1–R8) sau khi vá | **8/8 xanh** |
| Thông báo tự hành (T1–T8) | **8/8 xanh** |
| `nhom_bat_lai_gan_nhat` (K1–K7) sau khi sửa | **7/7 xanh** |
| `nhom_bat_lai_gan_nhat` (K1–K7) bản đầu | **6/7, K2 ĐỎ** ← bắt lỗi kế hoạch |


---

## 5. Rủi ro & ràng buộc

| Rủi ro | Xử lý |
|---|---|
| Vá Rào 8 làm agent hỏi lại nhiều hơn | Chỉ mở cho đúng trường hợp "đã bật lại sau" — hẹp |
| Vá sai → agent hỏi lại nhóm Đại vừa trả lời | R4/R6/R7 bắt buộc phải CHẶN; kiểm thử canh chỗ này |
| Thông báo tự hành thành spam | Chỉ gửi khi TH2 thật sự tắt chiến dịch; không gửi cho đường Đại bấm |
| Tin nhắn Telegram quá dài | Giới hạn 6 dòng, cắt tên dài bằng `ten[:60]` |
| Sửa `agent.py` phải khởi động lại | Nhắc Đại bấm `khoi-dong-lai-agent.bat` |

**Ràng buộc repo:** chỉ thư viện chuẩn + `unittest`, không thư viện ngoài. Chú thích
tiếng Việt không dấu; chuỗi hiện cho Đại có dấu.

---

## 6. Việc KHÔNG làm trong kế hoạch này

- **Không** đổi token sang token App (chỉ hướng dẫn, chờ Đại quyết).
- **Không** làm mẫu báo cáo tóm tắt/cảnh báo (kế hoạch riêng, Đại để sau).
- **Không** mở nấc 3.
- **Không** đổi ngưỡng nào của luật tắt (TH1/TH2/TH3).

---

## 7. Thứ tự thi công

1. Viết kiểm thử cho `soan_tin_tu_hanh` (T1–T6) → chạy, **phải ĐỎ**.
2. Viết kiểm thử cho Rào 8 (R1–R7) → chạy, **phải ĐỎ**.
3. **Dựng thử ngoài repo** toàn bộ code mới, chạy hết kiểm thử → phải XANH.
4. Đại duyệt kết quả dựng thử.
5. Sửa code thật: `agent_xin_phep.py`, `agent_ky_uc.py`, `agent_rao.py`, `agent.py`.
6. Chạy toàn bộ kiểm thử (kỳ vọng 757 + ~13 mới).
7. `git commit`. Đại bấm `khoi-dong-lai-agent.bat`.
