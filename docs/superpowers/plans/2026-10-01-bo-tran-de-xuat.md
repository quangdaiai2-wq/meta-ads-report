# Kế hoạch: Bỏ trần đề xuất — để agent không còn im lặng

**Ngày:** 01/10/2026 · **Người yêu cầu:** Đại · **Trạng thái:** ĐÃ DỰNG THỬ, CHỜ ÁP DỤNG

## Vấn đề Đại gặp (đã kiểm chứng, không phải phỏng đoán)

Sau giờ nghỉ trưa 12h–13h30, Đại phải **tự tắt nhóm thủ công** và **không nhận được thông báo nào**.

### Nguyên nhân 1 — trần 3 đề xuất/ngày hết lúc 12:07, rồi agent im lặng

Hôm nay agent đã hỏi đủ **3 nhóm khác nhau** (07:51 · 08:22 · 11:58) — đúng bằng
`AGENT_TOI_DA_NGAY=3`. Từ 12:07 trở đi, hàm `_xet_de_xuat` trong `agent.py` gặp **ba chỗ
`break` thoát ra mà không ghi một dòng log nào**:

| Dòng | Điều kiện | Ghi log? |
|---|---|---|
| 138 | `con_lai <= 0` (hết trần mỗi vòng) | ❌ im lặng |
| 142 | `len(da_cho) >= AGENT_TOI_DA_CHO` | ❌ im lặng |
| 144 | `dem_de_xuat_hom_nay >= AGENT_TOI_DA_NGAY` | ❌ im lặng |
| 148 | rào an toàn từ chối | ✅ có ghi |

⇒ Agent **vẫn quét, vẫn tìm ra nhóm cần tắt, nhưng không nói gì**. Đo được lúc 13:30: **4 nhóm
đã vượt ngưỡng mà agent không hỏi được**.

### Nguyên nhân 2 — máy tính ngủ trưa 43 phút (ngoài tầm agent)

Nhật ký Windows: **ngủ 12:46:46 → thức 13:30:06**. Trong lúc ngủ không tiến trình nào chạy.
Không sửa được bằng code — thuộc về chế độ nguồn điện của Windows.

## Thay đổi đề xuất

### 1. `agent.py` — bỏ trần, và **không bao giờ im lặng nữa**

```python
MAC_DINH = {
    ...
    "AGENT_TOI_DA_NGAY": 0,             # 0 = KHONG GIOI HAN
    "AGENT_TOI_DA_DE_XUAT_MOI_VONG": 0, # 0 = hoi het trong mot lan quet
    "AGENT_TOI_DA_CHO": 0,              # 0 = khong gioi han so nhom dang cho
}
```

`_xet_de_xuat` viết lại: mọi nhánh đều được đếm, và **cuối hàm LUÔN ghi một dòng tổng kết**:

```
AGENT: 6 nhom cham nguong — hoi 6, bo qua 0 (dang cho Dai tra loi),
       chan 0 (rao an toan), DUNG SOM: <lý do nếu có>
```

### 2. `agent_rao.py` — bỏ trần hành động

```python
TOI_DA_NGAY = 0   # 0 = khong gioi han
TOI_DA_GIO = 0    # 0 = khong gioi han
```

**Vì sao bỏ:** mọi hành động đều **phải có Đại bấm nút** mới chạy. Trần này không ngăn được
agent làm bừa — nó chỉ ngăn **chính Đại** làm việc. Thực tế 01/10: Đại tắt 1 nhóm lúc 12:07 thì
**cả giờ sau không tắt được nhóm nào nữa**, và sau 3 nhóm thì hết cả ngày.

Cơ chế trần **vẫn còn nguyên**, chỉ đổi mặc định. Muốn đặt lại: sửa hai số trên (ví dụ `20` và `5`).

### 3. `.env` và `.env.example`

`AGENT_TOI_DA_NGAY=3` → `AGENT_TOI_DA_NGAY=0`, kèm chú thích `0 = không giới hạn`.

> Lưu ý: `AGENT_*` là nhóm khoá **duy nhất** agent đọc lại mỗi 15 giây ⇒ đổi `.env` ăn ngay.
> Nhưng phần sửa trong `agent.py` / `agent_rao.py` là **code** ⇒ phải khởi động lại agent.

## Kiểm chứng đã chạy (dựng thử NGOÀI repo)

Chép toàn bộ `.py` + `tests/` sang thư mục riêng, sửa ở đó, chạy thật.

**Bộ kiểm thử toàn repo: 637/637 đạt** (630 bài cũ + 7 bài mới).

Bài kiểm chứng trước/sau (`kiem-chung.py`) — 10/10 đạt:

| Phép kiểm | Kết quả |
|---|---|
| Cấu hình cũ (3/ngày, 1/vòng) với 6 nhóm chạm ngưỡng | chỉ hỏi được **1** — đúng như lỗi |
| Cấu hình mới (0 = không giới hạn) | hỏi **hết 6** |
| Sau 5 hành động/ngày + 2 trong giờ | **cho qua** (trước đây bị chặn) |
| Đặt lại trần 3/ngày + 1/giờ | **vẫn chặn** — cơ chế không bị vô hiệu |
| Nhóm đang chờ Đại trả lời | **không hỏi lại** |
| Dòng tổng kết trong log | có, và nói rõ lý do dừng sớm |

**2 bài kiểm thử cũ phải sửa** — chúng khẳng định hành vi cũ (`test_du_3_hanh_dong_hom_nay_thi_chan`,
`test_da_co_hanh_dong_gio_nay_thi_chan`). Đã thay bằng 3 bài mới: mặc định không giới hạn, và đặt
lại trần thì vẫn chặn.

## Việc phải làm sau khi áp dụng

1. Chép `agent.py`, `agent_rao.py`, `tests/test_agent.py` từ thư mục dựng thử về repo.
2. Sửa `.env` và `.env.example`.
3. **Khởi động lại agent** (code mới chỉ nạp lúc khởi động).
4. Kiểm chứng: đọc `logs/baocao.log`, tìm dòng `AGENT: N nhom cham nguong — ...`.

## Điều KHÔNG sửa được bằng code

- **Máy ngủ là mất việc thật.** Muốn theo dõi cả giờ nghỉ trưa phải chỉnh chế độ ngủ của Windows.
- **Tần suất quét 30 phút giữ nguyên** — đã đúng yêu cầu, đo thật là 30,4–30,6 phút/lần.
