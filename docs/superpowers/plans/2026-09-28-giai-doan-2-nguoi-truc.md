# Kế hoạch thi công — Giai đoạn 2: Người trực

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Thay ba lịch Windows rời rạc bằng **một tiến trình chạy suốt** (`nguoi_truc.py`), để hết gửi trùng tận gốc, để mốc giờ trở thành cấu hình riêng của từng máy, và để hệ thống bắt đầu **nghe được** tin nhắn Telegram — điều kiện bắt buộc cho Giai đoạn 4.

**Architecture:** `nguoi_truc.py` là một vòng lặp 30 giây, làm hai việc: (1) canh mốc giờ và gọi `report.py` ở **tiến trình riêng** để gửi báo cáo; (2) gọi `getUpdates` để nghe tin nhắn Telegram, chỉ trả lời tin từ `TELEGRAM_CHAT_ID` của Đại. Nó **không** tính lại số liệu, **không** gửi Telegram trực tiếp cho báo cáo — toàn bộ phần đó vẫn do `report.py` làm. Việc thay lịch Windows bằng một tiến trình là điều duy nhất chữa được lỗi gửi trùng: tiến trình thường trú **biết rõ lịch của chính nó**, nên không đoán mốc, không chạy ba tiến trình cùng lúc, và chỉ gửi **một** báo cáo bù cho mốc gần nhất bị lỡ.

**Tech Stack:** Python 3.13 thuần, chỉ thư viện chuẩn (`argparse`, `json`, `subprocess`, `time`, `urllib`, `unittest`). Không thêm thư viện ngoài. Windows Task Scheduler chỉ dùng để chạy **một** lịch duy nhất tên `NguoiTruc`, tạo bằng PowerShell `Register-ScheduledTask`.

**Spec:** `docs/superpowers/specs/2026-09-28-nguoi-truc-ai-agent-design.md` (mục 4.2, 5.1, 5.4, 5.5, 6.1, 8, 9.2)

---

## Cập nhật khi thi công (28/09/2026) — hai điều khác bản kế hoạch này

**Đã thi công xong 5/5 task, 105/105 kiểm thử đạt.** Hai chỗ dưới đây khác bản kế hoạch viết ở trên:

1. **Máy nhà BỎ mốc 22h, không giữ.** Kế hoạch này (mục Task 1 Step 9, Task 5 Step 4 và Step 11d)
   viết "máy nhà giữ 22h". Khi thi công, Đại chốt lại: **cả hai máy dùng chung `8,12,17`**.
   Đã sửa `README.md`, `.env.example`, `HUONG-DAN-MAY-NHA.md`, `HUONG-DAN-MAY-CONG-TY.md` theo
   đúng quyết định đó. Phần **code** không đổi — `REPORT_SLOTS` vẫn là cấu hình của từng máy,
   chỉ khác giá trị ghi trong `.env`. Kế hoạch vẫn dùng được nguyên vẹn nếu sau này muốn lấy lại
   mốc 22h ở một máy nào đó.
2. **Dòng kiểm tra cuối của `cai-dat-nguoi-truc.bat` in ba thuộc tính khác.** Kế hoạch viết
   `$t.Settings.AllowStartIfOnBatteries` — thuộc tính này **không tồn tại** trên đối tượng lịch,
   luôn trả rỗng, in ra một dòng trống vô nghĩa. Đã đổi thành `Chay khi dung pin`
   (`-not DisallowStartIfOnBatteries`), `Khong tat khi sang pin` (`-not StopIfGoingOnBatteries`)
   và `Chay bu khi lo gio` (`StartWhenAvailable`). Chỉ ảnh hưởng phần in ra, không ảnh hưởng
   việc tạo lịch.
3. **`cai-dat-nguoi-truc.bat` khởi động Người trực ngay** (`Start-ScheduledTask`), không đợi
   lần đăng nhập sau. **Đây là lỗ hổng thật, phát hiện khi Đại cài lần đầu (28/09 ~14:26).**
   Kế hoạch chỉ tạo lịch với trigger `-AtLogOn`. Mà chính file đó lại **xoá ba lịch cũ** ⇒ từ
   lúc bấm file đến lần đăng nhập sau là khoảng trống **không có gì gửi báo cáo**. Đã xảy ra:
   lịch `State=Ready` nhưng `LastRunTime=11/30/1999`, không có tiến trình, Đại nhắn bot lúc
   14:25 không ai trả lời. Phần kiểm tra cũng in thêm `Trang thai` và dòng `Tien trinh: dang chay`.

> **Rút ra:** với mọi `.bat` vừa *xoá* cơ chế cũ vừa *tạo* cơ chế mới, phải bảo đảm cơ chế mới
> **chạy được ngay trong cùng lượt bấm** — không được để nó chờ một sự kiện hệ thống (đăng nhập,
> khởi động lại) mới hoạt động.

---

## Kế hoạch này đã được kiểm chứng trước khi giao

Trước khi giao kế hoạch, tôi đã **dựng thử toàn bộ code của kế hoạch trong một thư mục tạm**
(sao chép `report.py`, `dashboard.py`, `lich_su.py` và bộ kiểm thử ra ngoài, áp đúng các sửa đổi
của Task 1, viết `nguoi_truc.py` và `tests/test_nguoi_truc.py` theo đúng văn bản dưới đây) rồi
chạy. Kết quả:

| Phép kiểm | Kết quả |
|---|---|
| Cú pháp 21 khối Python trong kế hoạch | Hợp lệ cả 21 |
| Tám sửa đổi của Task 1 áp vào `report.py` thật | Khớp **cả tám** vị trí, không chỗ nào lệch |
| Toàn bộ kiểm thử | **105/105 đạt** — đúng bằng con số kế hoạch dự đoán |
| `report.doc_moc_tu_env(report.load_env('.env'))` với `.env` có `REPORT_SLOTS=8,12,17` | `[8, 12, 17]` |
| `nguoi_truc.py --gui-ngay 22` | `LOI: Moc 22h khong nam trong danh sach moc cua may nay: [8, 12, 17]`, thoát mã 1 |
| `report.py --slot 22 --dry` khi `.env` ghi `8,12,17` | `invalid choice: '22'`, thoát mã 2 |
| `report.py --help` khi **chưa có** `.env` | Vẫn chạy, dùng danh sách mặc định `8,12,17,22` |

**Một lỗi của kế hoạch đã bị phép kiểm này bắt được và đã sửa:** bài
`test_thu_qua_so_lan_thi_khong_thu_nua` ban đầu lấy mốc so sánh là `now + 999999 giây`, tức là
**hơn 11 ngày sau** — vượt sang ngày mới, nên bộ đếm được đếm lại từ đầu và bài kiểm thử
**luôn thất bại** dù code đúng. Đã đổi thành `luc(23)` (vẫn trong cùng ngày). Ghi lại đây để
người thi công biết chỗ đó là **cố ý**, không phải lỗi đánh máy.

Thư mục tạm đã được xoá sau khi kiểm chứng. Việc dựng thử **không** thay đổi gì trong repo thật.

---

## Khác với bản thiết kế — đọc trước khi duyệt

Bốn điểm dưới đây tôi cố ý làm khác bản thiết kế. Nếu Đại không đồng ý điểm nào thì nói, tôi sửa kế hoạch trước khi thi công.

| # | Bản thiết kế nói | Kế hoạch này làm | Vì sao |
|---|---|---|---|
| 1 | Mục 5.4: "Tách phần gửi (Telegram + file HTML) thành hàm gọi được từ cả `nguoi_truc.py` và dòng lệnh tay" | `nguoi_truc.py` gọi `report.py` bằng **tiến trình riêng** (`subprocess`), kèm `--slot N`. **Không** sửa phần gửi của `report.py` | Ba lý do: (a) `report.py` lỗi thì Người trực vẫn sống; (b) không phải đụng vào phần tính tiền đang chạy đúng; (c) chính kế hoạch Giai đoạn 1 đã ghi sẵn "tiến trình thường trú cũng sẽ gọi `report.py` kèm mốc giờ". Đây là điểm **quan trọng nhất** cần Đại biết |
| 2 | Mục 5.1 điều 4: "Nhịp tim — ghi một dòng nhật ký **mỗi vòng**" | Ghi nhịp tim **mỗi 30 phút** (mỗi 60 vòng) | Mỗi vòng là 30 giây ⇒ một ngày ~2.880 dòng nhịp tim, làm ngập `logs/baocao.log` — chính file Đại mở đầu tiên khi có sự cố. Phép thử sức khoẻ thật là lệnh "còn sống không?" (mục 5.1 điều 5), vẫn làm đủ |
| 3 | Mục 10: Đại bấm `cai-dat-nguoi-truc.bat`, **rồi** bấm `go-lich.bat` (hai bước) | `cai-dat-nguoi-truc.bat` **tự xoá luôn** ba lịch cũ | Hai lịch cùng sống một ngày là hai nguồn gửi báo cáo. Cơ chế chống trùng cũ đọc-rồi-ghi không có khoá, nên hai tiến trình chạy sát nhau vẫn lọt ⇒ Đại nhận báo cáo trùng. Đại không biết lập trình, quên bước 2 là chuyện thường. `go-lich.bat` vẫn giữ nguyên để tắt toàn bộ |
| 4 | Mục 5.5: lịch `NguoiTruc` "kích hoạt khi đăng nhập" | Vẫn vậy, nhưng đăng ký bằng PowerShell `Register-ScheduledTask` chứ **không** dùng `schtasks /Create` | `schtasks` không đặt được "Restart on failure" và "không giới hạn thời gian chạy". Thêm nữa, Giai đoạn 1 đã tốn một vòng sửa chỉ vì bẫy dấu nháy của `schtasks /TR`; `Register-ScheduledTask` tránh hẳn cái bẫy đó |

---

## Danh sách kiểm chứng của bản thiết kế (mục 9.2) — làm được tới đâu

Bản thiết kế liệt kê 10 tình huống phải thử. Giai đoạn 2 làm được 7, còn 3 thuộc các giai đoạn sau. Ghi rõ ở đây để không ai tưởng đã thử hết.

| # | Tình huống (thiết kế 9.2) | Giai đoạn 2 | Ở đâu |
|---|---|---|---|
| 1 | Chạy `--thu` toàn bộ, không gửi gì | ✅ | Task 3 Step 10 |
| 2 | Tới mốc thì gửi đúng báo cáo mốc đó, không gửi lần hai | ✅ | Task 2 `TestCanhMoc`, `TestChonMocCanGui` |
| 3 | Tắt tiến trình giữa lúc chạy, bật lại → gửi bù **đúng mốc đó** | ✅ | Task 2 `test_thuc_day_luc_12h05_chi_gui_mot_bao_cao` |
| 4 | Mất mạng khi gọi Meta → thử lại, rồi cảnh báo, không im lặng | ➖ | **Đã có sẵn trong `report.py`** (`api_get` thử 3 lần + `send_error_alert`). Giai đoạn 2 **không** sửa phần này, chỉ giới hạn số lần thử lại ở tầng Người trực (3 lần/mốc/ngày) |
| 5 | AI lỗi → báo cáo vẫn gửi, thiếu phần nhận định | ⏳ | Giai đoạn 3 |
| 6 | Token Meta chết → cảnh báo đúng nội dung | ➖ | **Đã có sẵn** trong `report.py` (`canh_bao_han_token`, `send_error_alert`). Giai đoạn 5 mới thêm phần tự gia hạn |
| 7 | Nhắn từ chat_id lạ → bị bỏ qua, ghi nhật ký | ✅ | Task 3 `TestXuLyTin`, `TestTinTuDai` |
| 8 | Nhắn "còn sống không?" → trả lời kèm tình trạng | ✅ | Task 3 `TestTraLoiTinNhan` |
| 9 | Nhắn một câu hỏi cần số liệu → trả lời đúng số | ⏳ | Giai đoạn 4 (cần lớp AI) |
| 10 | Bật máy sau 2 ngày tắt → không gửi trùng, không gửi loạt báo cáo cũ | ✅ | Task 2 `test_bat_may_luc_9h30_sau_hai_ngay_tat_chi_gui_moc_8` |

---

## Global Constraints

- **Không thư viện ngoài.** Chỉ dùng thư viện chuẩn. Kiểm thử bằng `unittest`. Không `requirements.txt`, không `pip install`.
- **Tên file Python dùng gạch dưới.** `nguoi_truc.py`, không phải `nguoi-truc.py`. File `.bat` được dùng gạch ngang (`cai-dat-nguoi-truc.bat`) vì không ai import chúng.
- **Không đụng vào phép tính.** `fetch_insights`, `apply_filter`, `get_action_value`, `fmt_money`, `compute_stats`, `build_report`, `send_telegram`, `send_telegram_document`, `api_get`, `load_env` giữ nguyên tuyệt đối. Trong `report.py`, Giai đoạn 2 chỉ được sửa: hằng số mốc giờ, `chon_moc` (không bắt buộc), `determine_period` (thêm tham số có giá trị mặc định), `da_gui_hom_nay`, `main()`, và **thêm** ba hàm mới.
- **Thao tác phụ không được làm hỏng việc chính.** Mọi lời gọi phụ (ghi lịch sử, nghe Telegram, ghi nhật ký) phải bọc trong `try`. Nguyên tắc: Đại không bao giờ mất báo cáo vì một tính năng phụ lỗi.
- **Chú thích trong code bằng tiếng Việt KHÔNG dấu** (theo đúng lệ repo). **Chuỗi hiện cho người dùng bằng tiếng Việt CÓ dấu.**
- **Không commit `.env`.** `.gitignore` đã chặn. Không sửa `.gitignore`.
- **`logs/` không lên GitHub** — đã bị `.gitignore` chặn ở dòng 16.
- **Python để chạy:** `C:\Users\nguye\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe`
- **Chạy kiểm thử từ thư mục gốc repo:**
  `"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . -v`
- **Lịch Windows chạy ở chế độ `Interactive`** — máy phải đang bật **và đang đăng nhập**. Giới hạn có sẵn, không phải điều giai đoạn này sửa.
- **`schtasks.exe` bị chặn trong môi trường agent.** Muốn kiểm chứng lịch, dùng `Get-ScheduledTask` (đọc). Việc tạo lịch thật là **việc của Đại**, chạy `cai-dat-nguoi-truc.bat`.
- **`bat-danh-thuc-may.bat` không đụng tới lịch** — nó chỉ gọi `powercfg`. Không sửa file này.

---

## Cấu trúc file

| File | Trạng thái | Trách nhiệm |
|---|---|---|
| `nguoi_truc.py` | **Tạo mới** | Vòng lặp thường trú: canh mốc giờ, gọi `report.py`, nghe Telegram, ghi nhịp tim. **Không** tự tính số liệu, **không** tự gửi báo cáo |
| `tests/test_nguoi_truc.py` | **Tạo mới** | Kiểm thử `nguoi_truc.py` |
| `cai-dat-nguoi-truc.bat` | **Tạo mới** | Tạo lịch `NguoiTruc` (một lịch duy nhất), xoá ba lịch cũ |
| `go-nguoi-truc.bat` | **Tạo mới** | Xoá lịch `NguoiTruc`, dừng tiến trình đang chạy |
| `report.py` | **Sửa** | Thêm `doc_moc_tu_env()`, `moc_sang()`, `ds_moc_da_gui()`; `determine_period()` nhận mốc sáng; `main()` đọc danh sách mốc từ `.env` |
| `tests/test_report.py` | **Sửa** | Thêm kiểm thử cho ba hàm mới và cho `determine_period()` |
| `.env.example` | **Sửa** | Ghi lại khoá `REPORT_SLOTS` |
| `.env` (trên máy, KHÔNG lên GitHub) | **Sửa** | Thêm `REPORT_SLOTS=8,12,17` cho máy công ty |
| `README.md` | **Sửa** | Mục cài đặt, cách kiểm tra còn sống, cách gỡ, xử lý sự cố |
| `HANDOFF.md` | **Sửa** | Trạng thái mới, cách chạy mới, ghi chú kỹ thuật |
| `QUY-TRINH-HANG-NGAY.md` | **Sửa** | Quy trình hằng ngày đổi (không còn "lịch Windows chạy 3 mốc") |
| `HUONG-DAN-MAY-CONG-TY.md` | **Sửa** | Bước cài đổi |
| `HUONG-DAN-MAY-NHA.md` | **Sửa** | Bước cập nhật máy nhà đổi |
| `cai-dat-lich.bat` | **Giữ nguyên** | Không xoá — vẫn dùng được làm đường lùi nếu Người trực có sự cố |
| `bat-chay-bu.bat`, `go-lich.bat` | **Giữ nguyên** | `go-lich.bat` là cách tắt toàn bộ; `bat-chay-bu.bat` không còn cần nhưng vô hại |

---

## Task 1: `report.py` trở thành nguồn duy nhất cho danh sách mốc giờ

**Files:**
- Modify: `report.py` (hằng số mốc giờ, thêm ba hàm, sửa `determine_period`, sửa `main()`)
- Modify: `tests/test_report.py` (thêm ba lớp kiểm thử)
- Modify: `.env.example`
- Modify: `.env` (trên máy này; file bị `.gitignore` chặn nên không lên GitHub)

**Interfaces:**
- Consumes: không
- Produces:
  - `doc_moc_tu_env(env) -> list[int]` — danh sách mốc giờ của máy này, đã sắp xếp và bỏ trùng; dữ liệu sai thì trả về `REPORT_SLOTS`
  - `moc_sang(danh_sach_moc) -> int` — mốc gio báo cáo NGÀY HÔM TRƯỚC (mốc nhỏ nhất); danh sách rỗng thì trả `MOC_SANG_MAC_DINH`
  - `ds_moc_da_gui(ngay=None) -> list[int]` — các mốc đã gửi thành công trong một ngày
  - `determine_period(now, slot_hour, moc_sang_bao_cao=None)` — `None` thì dùng 8 như cũ
  - Hằng số mới `MOC_SANG_MAC_DINH = 8`

**Vì sao:** hiện danh sách mốc nằm cứng trong `report.py` (`REPORT_SLOTS = [8, 12, 17, 22]`) và trong `cai-dat-lich.bat`. Bản thiết kế mục 5.1 yêu cầu danh sách này là **cấu hình riêng của từng máy**, đọc từ `.env` — vì máy công ty đã bỏ mốc 22h còn máy nhà thì không. Và `determine_period()` đang viết cứng `if slot_hour == 8`; nếu danh sách mốc đổi mà chỗ đó không đổi theo thì báo cáo mốc đầu tiên sẽ hiểu sai thành "trong ngày" thay vì "hôm qua".

> ⚠️ **Cái bẫy phải nhớ:** nếu `.env` **không có** khoá `REPORT_SLOTS`, hàm `doc_moc_tu_env` trả về mặc định `[8, 12, 17, 22]` — nghĩa là **mốc 22h quay trở lại** trên máy công ty, đúng cái Đại vừa bỏ. Vì vậy Step 6 dưới đây (thêm khoá vào `.env`) là **bắt buộc**, không phải tuỳ chọn.

- [ ] **Step 1: Viết kiểm thử thất bại**

Thêm vào **cuối** `tests/test_report.py`, **trước** khối `if __name__ == "__main__":`:

```python
from datetime import datetime


class TestDocMocTuEnv(unittest.TestCase):
    def test_doc_danh_sach_thuong(self):
        self.assertEqual(
            report.doc_moc_tu_env({"REPORT_SLOTS": "8,12,17"}), [8, 12, 17]
        )

    def test_co_khoang_trang(self):
        self.assertEqual(
            report.doc_moc_tu_env({"REPORT_SLOTS": "8, 12, 17"}), [8, 12, 17]
        )

    def test_sap_xep_lai_va_bo_trung(self):
        self.assertEqual(
            report.doc_moc_tu_env({"REPORT_SLOTS": "17,8,8,12"}), [8, 12, 17]
        )

    def test_thieu_khoa_thi_dung_mac_dinh(self):
        self.assertEqual(report.doc_moc_tu_env({}), report.REPORT_SLOTS)

    def test_rong_thi_dung_mac_dinh(self):
        self.assertEqual(
            report.doc_moc_tu_env({"REPORT_SLOTS": ""}), report.REPORT_SLOTS
        )

    def test_chu_thi_dung_mac_dinh(self):
        self.assertEqual(
            report.doc_moc_tu_env({"REPORT_SLOTS": "tam,muoi"}), report.REPORT_SLOTS
        )

    def test_bo_qua_phan_tu_sai_giu_phan_tu_dung(self):
        self.assertEqual(report.doc_moc_tu_env({"REPORT_SLOTS": "8,abc,17"}), [8, 17])

    def test_so_ngoai_khoang_bi_bo_qua(self):
        self.assertEqual(report.doc_moc_tu_env({"REPORT_SLOTS": "8,99,-1"}), [8])

    def test_dung_dau_cham_phay(self):
        self.assertEqual(report.doc_moc_tu_env({"REPORT_SLOTS": "8;12;17"}), [8, 12, 17])

    def test_None_cung_dung_mac_dinh(self):
        self.assertEqual(report.doc_moc_tu_env(None), report.REPORT_SLOTS)


class TestMocSang(unittest.TestCase):
    def test_lay_moc_nho_nhat(self):
        self.assertEqual(report.moc_sang([8, 12, 17]), 8)

    def test_danh_sach_khac_van_lay_min(self):
        self.assertEqual(report.moc_sang([7, 13, 20]), 7)

    def test_danh_sach_rong_tra_ve_mac_dinh(self):
        self.assertEqual(report.moc_sang([]), report.MOC_SANG_MAC_DINH)


class TestDeterminePeriodTheoMocSang(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 9, 28, 9, 0, 0)

    def test_moc_8_la_bao_cao_hom_qua(self):
        since, until, _ = report.determine_period(self.now, 8, 8)
        self.assertEqual(since, date(2026, 9, 27))
        self.assertEqual(until, date(2026, 9, 27))

    def test_moc_12_la_bao_cao_trong_ngay(self):
        since, _, _ = report.determine_period(self.now, 12, 8)
        self.assertEqual(since, date(2026, 9, 28))

    def test_khong_truyen_moc_sang_thi_mac_dinh_8(self):
        since, _, _ = report.determine_period(self.now, 8)
        self.assertEqual(since, date(2026, 9, 27))

    def test_doi_moc_sang_thanh_7_thi_moc_7_la_hom_qua(self):
        since, _, _ = report.determine_period(self.now, 7, 7)
        self.assertEqual(since, date(2026, 9, 27))

    def test_doi_moc_sang_thanh_7_thi_moc_8_la_trong_ngay(self):
        since, _, _ = report.determine_period(self.now, 8, 7)
        self.assertEqual(since, date(2026, 9, 28))
```

- [ ] **Step 2: Chạy kiểm thử để chắc chắn nó thất bại**

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . -v
```

Kết quả mong đợi: `AttributeError: module 'report' has no attribute 'doc_moc_tu_env'`.

- [ ] **Step 3: Thêm hằng số và ba hàm mới vào `report.py`**

Thay khối hằng số mốc giờ (khoảng dòng 27-28):

```python
# Cac moc gio bao cao (gio Viet Nam)
REPORT_SLOTS = [8, 12, 17, 22]
```

bằng:

```python
# Cac moc gio bao cao MAC DINH (gio Viet Nam).
# Doi duoc bang khoa REPORT_SLOTS trong .env, vi du: REPORT_SLOTS=8,12,17
# (may cong ty bo moc 22h ngay 28/09/2026; may nha giu 22h).
REPORT_SLOTS = [8, 12, 17, 22]

# Moc gio bao cao NGAY HOM TRUOC khi khong xac dinh duoc moc nao khac.
MOC_SANG_MAC_DINH = 8
```

Rồi chèn ba hàm mới ngay **sau** hàm `chon_moc()` (sau dòng `return min(danh_sach_moc, key=lambda s: abs(s - gio_hien_tai))`):

```python
def doc_moc_tu_env(env):
    """Doc danh sach moc gio bao cao tu khoa REPORT_SLOTS trong .env.

    Chap nhan: "8,12,17" hoac "8, 12, 17" hoac "17,8,8" hoac "8;12;17".
    Tra ve danh sach da sap xep tang dan, bo trung.

    Phan tu sai (chu, so ngoai 0-23) bi bo qua tung cai mot. Neu khong doc
    duoc moc nao hop le thi tra ve REPORT_SLOTS.

    Khong bao gio nem loi: mot dong cau hinh go sai khong duoc lam chet
    bao cao.
    """
    raw = (env or {}).get("REPORT_SLOTS", "")
    ds = []
    for phan in str(raw).replace(";", ",").split(","):
        phan = phan.strip()
        if not phan:
            continue
        try:
            moc = int(phan)
        except ValueError:
            continue
        if 0 <= moc <= 23 and moc not in ds:
            ds.append(moc)
    return sorted(ds) if ds else list(REPORT_SLOTS)


def moc_sang(danh_sach_moc):
    """Moc gio bao cao NGAY HOM TRUOC = moc NHO NHAT trong danh sach.

    Truoc day determine_period() viet cung `if slot_hour == 8`. Khi danh sach
    moc doi (vi du bo moc 8h), bao cao moc dau tien se bi hieu sai thanh
    "trong ngay" thay vi "hom qua". Lay min() de doi danh sach moc ma khong
    phai sua code.
    """
    return min(danh_sach_moc) if danh_sach_moc else MOC_SANG_MAC_DINH
```

- [ ] **Step 4: Sửa `determine_period()` để nhận mốc sáng**

Thay toàn bộ hàm `determine_period` (khoảng dòng 311-324) bằng:

```python
def determine_period(now, slot_hour, moc_sang_bao_cao=None):
    """Tra ve (tu_ngay, den_ngay, mo_ta) theo moc gio.

    moc_sang_bao_cao: moc gio bao cao NGAY HOM TRUOC (thuong la moc nho nhat).
                      None thi dung 8 - giu dung hanh vi cu.
    """
    if moc_sang_bao_cao is None:
        moc_sang_bao_cao = MOC_SANG_MAC_DINH

    today = now.date()

    if slot_hour == moc_sang_bao_cao:
        # Bao cao ngay hom truoc
        target = today - timedelta(days=1)
        return target, target, f"{target.strftime('%d/%m/%Y')}"
    else:
        # Bao cao trong ngay, tu 0h den gio hien tai
        return today, today, (
            f"{today.strftime('%d/%m/%Y')} "
            f"(00:00 - {slot_hour:02d}:00)"
        )
```

- [ ] **Step 5: Thêm `ds_moc_da_gui()` và nối vào `da_gui_hom_nay()`**

Thay hàm `da_gui_hom_nay` (khoảng dòng 129-132) bằng hai hàm:

```python
def ds_moc_da_gui(ngay=None):
    """Danh sach cac moc da gui THANH CONG trong mot ngay (mac dinh hom nay).

    Nguoi truc (nguoi_truc.py) doc ham nay de biet moc nao con thieu.
    File hong hoac gia tri sai kieu thi tra ve danh sach rong.
    """
    data = _doc_da_gui()
    ngay = ngay or datetime.now().strftime("%Y-%m-%d")
    ds = data.get(ngay, [])
    return list(ds) if isinstance(ds, list) else []


def da_gui_hom_nay(slot):
    """True neu moc nay da duoc gui thanh cong trong ngay hom nay."""
    return slot in ds_moc_da_gui()
```

- [ ] **Step 6: Sửa `main()` để dùng danh sách mốc của máy**

Trong `main()`, thay đoạn đầu (từ `def main():` tới `args = parser.parse_args()`, khoảng dòng 629-639) bằng:

```python
def main():
    duong_dan_env = Path(__file__).parent / ".env"

    # Doc .env TRUOC argparse: danh sach moc gio la cua TUNG MAY, nen --slot va
    # --mock phai kiem tra theo dung danh sach do. Doc kieu "khong nem loi" de
    # `--help` van chay duoc khi chua co .env.
    env = {}
    try:
        env = load_env(duong_dan_env)
    except Exception:
        pass
    danh_sach_moc = doc_moc_tu_env(env)

    parser = argparse.ArgumentParser(description="Báo cáo Meta Ads → Telegram")
    parser.add_argument("--mock", type=int, choices=danh_sach_moc,
                        help="Chạy thử với mốc giờ này (không gửi Telegram)")
    parser.add_argument("--slot", type=int, choices=danh_sach_moc,
                        help="Mốc giờ do lịch Windows truyền vào (dùng khi gửi thật)")
    parser.add_argument("--dry", action="store_true",
                        help="Chạy thật nhưng không gửi Telegram")
    parser.add_argument("--force", action="store_true",
                        help="Gửi lại dù mốc này đã gửi hôm nay (bỏ qua chống trùng)")
    args = parser.parse_args()

    if not env:
        print(f"LOI: Khong doc duoc file .env tai {duong_dan_env}")
        print("Cach xu ly: copy .env.example thanh .env roi dien token vao.")
        sys.exit(1)

    now = datetime.now()
```

Rồi thay dòng chọn mốc (khoảng dòng 648):

```python
        slot = chon_moc(args.slot, now.hour, REPORT_SLOTS)
```

bằng:

```python
        slot = chon_moc(args.slot, now.hour, danh_sach_moc)
```

Và thay dòng gọi `determine_period` (khoảng dòng 662):

```python
    since, until, period_text = determine_period(now, slot)
```

bằng:

```python
    since, until, period_text = determine_period(now, slot, moc_sang(danh_sach_moc))
```

- [ ] **Step 7: Chạy kiểm thử để chắc chắn nó đạt**

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . -v
```

Kết quả mong đợi: `OK`, **54 bài** đạt (36 bài cũ + 18 bài mới).

- [ ] **Step 8: Kiểm tra hành vi cũ không đổi (tương thích ngược)**

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" report.py --dry
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" report.py --slot 9 --dry
```

Kết quả mong đợi:
- Lệnh 1: vẫn chạy bình thường, vẫn in `Moc gio hien tai: ...`.
- Lệnh 2: bị chặn với `invalid choice: 9` (vì 9 không nằm trong danh sách mốc của máy).

- [ ] **Step 9: Ghi khoá `REPORT_SLOTS` vào `.env.example`**

Trong `.env.example`, trong mục `3. CAU HINH BAO CAO`, thêm **trước** dòng `REPORT_ACCOUNT_NAME=...`:

```
#  Danh sach moc gio bao cao, cach nhau bang dau phay. MOI MAY TU CHON.
#    May cong ty: 8,12,17    (bo moc 22h tu 28/09/2026)
#    May nha    : 8,12,17,22
#  Neu thieu khoa nay, he thong dung mac dinh 8,12,17,22.
REPORT_SLOTS=8,12,17,22
```

- [ ] **Step 10: Ghi khoá `REPORT_SLOTS` vào `.env` thật trên máy này**

**Việc này sửa file bí mật. Phải sao lưu trước.**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
cp .env .env.bak-truoc-gd2
grep -c "^REPORT_SLOTS=" .env
```

Kết quả mong đợi của lệnh `grep`: `0` (chưa có khoá). Nếu ra `1` thì **dừng lại**, báo cho người giao việc — nghĩa là đã có sẵn, phải xem giá trị hiện tại là gì trước khi sửa.

Rồi thêm dòng này vào **cuối** `.env`:

```
REPORT_SLOTS=8,12,17
```

Kiểm chứng:

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" report.py --slot 22 --dry
```

Kết quả mong đợi: **bị chặn** với `invalid choice: 22` — chứng tỏ danh sách mốc của máy này đã thành 8,12,17, mốc 22h không quay lại.

- [ ] **Step 11: Commit**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
git add report.py tests/test_report.py .env.example
git commit -m "report.py: doc danh sach moc gio tu .env (REPORT_SLOTS) va bo viet cung moc 8h"
```

> `.env` và `.env.bak-truoc-gd2` **không** được `git add` — `.gitignore` đã chặn `.env.*`. Kiểm chứng bằng `git status --short` trước khi commit.

---

## Task 2: `nguoi_truc.py` — lõi canh mốc giờ

**Files:**
- Create: `nguoi_truc.py`
- Test: `tests/test_nguoi_truc.py`

**Interfaces:**
- Consumes: `report.doc_moc_tu_env(env)`, `report.ds_moc_da_gui(ngay)`, `report.load_env(path)`, `report.log(msg)`, `report.LOG_DIR`
- Produces:
  - `moc_da_toi(now, danh_sach_moc) -> list[int]` — mốc đã đi qua tính đến `now`
  - `chon_moc_can_gui(now, danh_sach_moc, da_gui, trang_thai) -> (int|None, list[int])` — `(mốc cần gửi, danh sách mốc bị bỏ qua)`
  - `TrangThaiThu` — lớp nhớ số lần thử và lần thử cuối cho từng mốc, tự đếm lại khi sang ngày mới. Phương thức: `duoc_thu(moc, now) -> bool`, `ghi_lan_thu(moc, now)`
  - `gui_bao_cao(moc, che_do_thu=False) -> bool`
  - `NguoiTruc(env, danh_sach_moc, che_do_thu=False, gui_bao_cao_fn=None, gui_tin_fn=None, doc_da_gui_fn=None, dong_ho=None)` — lớp chính, có `mot_vong()`
  - Hằng số: `NHIP_GIAC = 30`, `NHIP_TIM_MOI_VONG = 60`, `MAX_LAN_THU_MOI_MOC = 3`, `KHOANG_NGHI_GIUA_HAI_LAN_THU = 300`, `CHO_REPORT_TOI_DA = 600`, `MOC_MAC_DINH = [8, 12, 17, 22]`

**Vì sao đây là trái tim của giai đoạn:** đây là chỗ chữa nốt chuyện gửi trùng. Quy tắc chỉ có một câu: **mỗi vòng, chỉ gửi MỘT báo cáo cho mốc gần nhất đã đi qua mà chưa gửi; các mốc cũ hơn ghi nhật ký là bỏ qua.** Bật máy lúc 12h05 khi chưa gửi gì ⇒ gửi đúng một báo cáo mốc 12h, không gửi báo cáo 8h. Trước đây ba lịch chạy bù cùng lúc và gửi cả ba.

- [ ] **Step 1: Viết kiểm thử thất bại**

Tạo `tests/test_nguoi_truc.py`:

```python
"""Kiem thu nguoi_truc - tien trinh thuong tru cua bao cao Meta Ads."""
import unittest
from datetime import datetime, timedelta

import nguoi_truc

TrangThaiThu = nguoi_truc.TrangThaiThu


def luc(gio, phut=0, giay=0, ngay=28):
    """Mot thoi diem gia de kiem thu, khong phu thuoc dong ho that."""
    return datetime(2026, 9, ngay, gio, phut, giay)


class TestMocDaToi(unittest.TestCase):
    def test_truoc_moc_thi_chua_toi(self):
        self.assertEqual(nguoi_truc.moc_da_toi(luc(7, 59, 59), [8, 12, 17]), [])

    def test_dung_moc_thi_da_toi(self):
        self.assertEqual(nguoi_truc.moc_da_toi(luc(8, 0, 0), [8, 12, 17]), [8])

    def test_sau_moc_30_giay_van_da_toi(self):
        self.assertEqual(nguoi_truc.moc_da_toi(luc(8, 0, 30), [8, 12, 17]), [8])

    def test_qua_nhieu_moc_thi_tra_ve_het(self):
        self.assertEqual(nguoi_truc.moc_da_toi(luc(13), [8, 12, 17]), [8, 12])


class TestChonMocCanGui(unittest.TestCase):
    def test_chua_toi_moc_nao_thi_khong_gui(self):
        moc, bo_qua = nguoi_truc.chon_moc_can_gui(
            luc(7), [8, 12, 17], set(), TrangThaiThu()
        )
        self.assertIsNone(moc)
        self.assertEqual(bo_qua, [])

    def test_toi_moc_8_thi_gui_moc_8(self):
        moc, bo_qua = nguoi_truc.chon_moc_can_gui(
            luc(8, 0, 5), [8, 12, 17], set(), TrangThaiThu()
        )
        self.assertEqual(moc, 8)
        self.assertEqual(bo_qua, [])

    def test_moc_8_da_gui_roi_thi_toi_moc_12_gui_moc_12(self):
        moc, _ = nguoi_truc.chon_moc_can_gui(
            luc(12, 0, 5), [8, 12, 17], {8}, TrangThaiThu()
        )
        self.assertEqual(moc, 12)

    def test_thuc_day_luc_12h05_khi_chua_gui_gi_chi_gui_MOT_bao_cao_moc_12(self):
        # Bai quan trong nhat cua ca giai doan. Truoc day ba lich chay bu cung
        # luc se gui ca bao cao 8h, 12h, 17h. Nguoi truc chi gui DUNG MOT bao
        # cao, cho moc gan nhat.
        moc, bo_qua = nguoi_truc.chon_moc_can_gui(
            luc(12, 5), [8, 12, 17], set(), TrangThaiThu()
        )
        self.assertEqual(moc, 12)
        self.assertEqual(bo_qua, [8])

    def test_bat_may_luc_9h30_sau_hai_ngay_tat_chi_gui_moc_8(self):
        moc, bo_qua = nguoi_truc.chon_moc_can_gui(
            luc(9, 30), [8, 12, 17], set(), TrangThaiThu()
        )
        self.assertEqual(moc, 8)
        self.assertEqual(bo_qua, [])

    def test_moc_17_con_o_tuong_lai_thi_khong_gui(self):
        moc, _ = nguoi_truc.chon_moc_can_gui(
            luc(14), [8, 12, 17], {8, 12}, TrangThaiThu()
        )
        self.assertIsNone(moc)

    def test_moc_gan_nhat_het_luot_thu_thi_KHONG_gui_moc_cu_hon(self):
        # Moc 12 da thu het luot va that bai -> KHONG duoc gui moc 8, vi bao
        # cao moc 8 la bao cao cu hon.
        tt = TrangThaiThu()
        now = luc(12, 5)
        for _ in range(nguoi_truc.MAX_LAN_THU_MOI_MOC):
            tt.ghi_lan_thu(12, now)
        moc, _ = nguoi_truc.chon_moc_can_gui(now, [8, 12, 17], set(), tt)
        self.assertIsNone(moc)


class TestTrangThaiThu(unittest.TestCase):
    def test_lan_dau_thi_duoc_thu(self):
        self.assertTrue(TrangThaiThu().duoc_thu(12, luc(12)))

    def test_vua_thu_xong_thi_chua_duoc_thu_lai(self):
        tt = TrangThaiThu()
        now = luc(12)
        tt.ghi_lan_thu(12, now)
        self.assertFalse(tt.duoc_thu(12, now + timedelta(seconds=60)))

    def test_qua_khoang_nghi_thi_duoc_thu_lai(self):
        tt = TrangThaiThu()
        now = luc(12)
        tt.ghi_lan_thu(12, now)
        self.assertTrue(
            tt.duoc_thu(12, now + timedelta(seconds=nguoi_truc.KHOANG_NGHI_GIUA_HAI_LAN_THU))
        )

    def test_thu_qua_so_lan_thi_khong_thu_nua(self):
        tt = TrangThaiThu()
        now = luc(12)
        for i in range(nguoi_truc.MAX_LAN_THU_MOI_MOC):
            tt.ghi_lan_thu(12, now + timedelta(seconds=i * 10000))
        # Van trong CUNG NGAY (23h) -> het luot thi khong thu nua.
        # (Neu lui qua ngay hom sau thi dem lai tu dau - do la bai duoi.)
        self.assertFalse(tt.duoc_thu(12, luc(23)))

    def test_sang_ngay_moi_thi_dem_lai_tu_dau(self):
        tt = TrangThaiThu()
        for _ in range(nguoi_truc.MAX_LAN_THU_MOI_MOC):
            tt.ghi_lan_thu(12, luc(12))
        self.assertTrue(tt.duoc_thu(12, luc(12, ngay=29)))

    def test_moc_khac_khong_bi_anh_huong(self):
        tt = TrangThaiThu()
        now = luc(12)
        for _ in range(nguoi_truc.MAX_LAN_THU_MOI_MOC):
            tt.ghi_lan_thu(12, now)
        self.assertTrue(tt.duoc_thu(17, now))


class TrucGia:
    """Mot NguoiTruc voi dong ho va moi thu ben ngoai deu gia - khong goi mang.

    Dung chung cho ca Task 2 va Task 3. Doi gio bang cach gan `tg.now`.
    """

    def __init__(self, now, da_gui=None, che_do_thu=False, ket_qua_gui=True,
                 tin_cho_san=None):
        self.now = now
        self.da_gui = set(da_gui or ())
        self.gui_roi = []
        self.tin_da_gui = []
        self._ket_qua_gui = ket_qua_gui
        self._tin_cho_san = list(tin_cho_san or [])
        self.so_lan_lay_tin = 0
        self.truc = nguoi_truc.NguoiTruc(
            env={"TELEGRAM_CHAT_ID": "123", "REPORT_ACCOUNT_NAME": "Test"},
            danh_sach_moc=[8, 12, 17],
            che_do_thu=che_do_thu,
            gui_bao_cao_fn=self._gui,
            gui_tin_fn=self._gui_tin,
            doc_da_gui_fn=lambda ngay: sorted(self.da_gui),
            dong_ho=lambda: self.now,
            xa_tin_fn=lambda env: (None, None),
            lay_tin_fn=self._lay_tin,
        )

    def _gui(self, moc):
        self.gui_roi.append(moc)
        return self._ket_qua_gui

    def _gui_tin(self, text):
        self.tin_da_gui.append(text)
        return True

    def _lay_tin(self, env, offset):
        """Tra ve tin cho san o lan goi dau, cac lan sau tra ve rong."""
        self.so_lan_lay_tin += 1
        if self.so_lan_lay_tin == 1 and self._tin_cho_san:
            return list(self._tin_cho_san), None
        return [], None


class TestCanhMoc(unittest.TestCase):
    def test_toi_moc_thi_gui_dung_mot_lan(self):
        tg = TrucGia(luc(8, 0, 5))
        tg.truc.canh_moc(luc(8, 0, 5))
        tg.truc.canh_moc(luc(8, 0, 35))
        self.assertEqual(tg.gui_roi, [8])

    def test_chua_toi_moc_thi_khong_gui(self):
        tg = TrucGia(luc(7, 30))
        tg.truc.canh_moc(luc(7, 30))
        self.assertEqual(tg.gui_roi, [])

    def test_moc_da_gui_trong_ngay_thi_khong_gui_lai(self):
        tg = TrucGia(luc(12, 0, 5), da_gui={8, 12})
        tg.truc.canh_moc(luc(12, 0, 5))
        self.assertEqual(tg.gui_roi, [])

    def test_thuc_day_luc_12h05_chi_gui_mot_bao_cao(self):
        tg = TrucGia(luc(12, 5))
        tg.truc.canh_moc(luc(12, 5))
        self.assertEqual(tg.gui_roi, [12])

    def test_gui_that_bai_thi_con_luot_thu_lai(self):
        tg = TrucGia(luc(12, 0, 5), ket_qua_gui=False)
        tg.truc.canh_moc(luc(12, 0, 5))
        self.assertEqual(tg.gui_roi, [12])
        # Chua qua khoang nghi -> khong thu lai ngay lap tuc
        tg.truc.canh_moc(luc(12, 1, 0))
        self.assertEqual(tg.gui_roi, [12])

    def test_qua_khoang_nghi_thi_thu_lai(self):
        tg = TrucGia(luc(12, 0, 5), ket_qua_gui=False)
        tg.truc.canh_moc(luc(12, 0, 5))
        sau = luc(12, 0, 5) + timedelta(seconds=nguoi_truc.KHOANG_NGHI_GIUA_HAI_LAN_THU)
        tg.truc.canh_moc(sau)
        self.assertEqual(tg.gui_roi, [12, 12])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Chạy kiểm thử để chắc chắn nó thất bại**

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . -v
```

Kết quả mong đợi: `ModuleNotFoundError: No module named 'nguoi_truc'`.

- [ ] **Step 3: Viết `nguoi_truc.py` — phần lõi**

Tạo `nguoi_truc.py`:

```python
"""
NGUOI TRUC - tien trinh thuong tru cua bao cao Meta Ads
=======================================================
Thay ba lich Windows roi rac bang MOT tien trinh chay suot khi may bat.

Hai viec:
  1. Canh moc gio, goi report.py o TIEN TRINH RIENG de gui bao cao dung moc.
  2. Nghe tin nhan Telegram, chi tra loi tin tu chat_id cua Dai.

Ly do thay lich Windows: lich khong biet gi ve nhau. Khi may ngu qua nhieu
moc, Windows cho ca ba lich chay bu CUNG LUC va moi lich tu doan moc gan nhat
-> gui ra nhieu bao cao trung nhau. Nguoi truc biet ro lich cua chinh no, nen
chi gui DUNG MOT bao cao bu, cho moc gan nhat bi lo.

Cach dung:
    python nguoi_truc.py                 # chay that
    python nguoi_truc.py --thu           # chay toan bo luong, KHONG gui gi
    python nguoi_truc.py --gui-ngay 17   # gui ngay moc 17h roi thoat
"""
import argparse
import json
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

import report

GOC = Path(__file__).parent

# Vong lap kiem tra dong ho moi 30 giay (theo thiet ke muc 5.1).
NHIP_GIAC = 30

# Ghi mot dong nhip tim moi 60 vong (~30 phut).
# Thiet ke muc 5.1 noi "moi vong", nhung 30 giay mot dong thi mot ngay co
# ~2.880 dong, lam ngap logs/baocao.log - chinh file Dai mo dau tien khi co
# su co. Lenh "con song khong?" moi la phep thu suc khoe chinh.
NHIP_TIM_MOI_VONG = 60

# Mot moc duoc thu toi da 3 lan trong ngay, cach nhau it nhat 5 phut.
# Muc dich: loi mang thoang qua thi van kip gui, nhung token chet han thi
# khong ban tin canh bao moi 30 giay.
MAX_LAN_THU_MOI_MOC = 3
KHOANG_NGHI_GIUA_HAI_LAN_THU = 300

# Thoi gian toi da cho report.py chay xong (giay).
CHO_REPORT_TOI_DA = 600

# Danh sach moc mac dinh khi .env khong ghi gi.
MOC_MAC_DINH = [8, 12, 17, 22]

# Cau tra loi cho cau hoi chua lam duoc (phan AI thuoc Giai doan 4).
TRA_LOI_CHUA_CO_AI = (
    "Tôi đang trực, nhưng chưa trả lời được câu hỏi về số liệu.\n"
    "\n"
    "Phần hỏi số liệu (ví dụ \"camp nào tệ nhất tuần này?\") sẽ có ở "
    "giai đoạn sau, khi nối phần AI vào.\n"
    "\n"
    "Hiện tôi làm được hai việc:\n"
    "- Gửi báo cáo tự động đúng các mốc giờ mỗi ngày.\n"
    "- Trả lời câu \"còn sống không?\" để Đại biết tôi còn chạy."
)
```

- [ ] **Step 4: Thêm phần quyết định mốc giờ (thuần logic, không I/O)**

Nối tiếp vào `nguoi_truc.py`:

```python
def moc_da_toi(now, danh_sach_moc):
    """Cac moc gio da di qua tinh den thoi diem `now`, trong NGAY HOM NAY."""
    return [m for m in danh_sach_moc if now.hour >= m]


class TrangThaiThu:
    """Nho so lan thu va lan thu cuoi cho tung moc, TRONG NGAY hom nay.

    Sang ngay moi thi dem lai tu dau. Khong can luu ra file: tien trinh
    thuong tru chay lien tuc, va khi no khoi dong lai thi thu lai la dung.
    """

    def __init__(self):
        self.ngay = None
        self.so_lan = {}
        self.lan_cuoi = {}

    def _kiem_tra_ngay(self, now):
        ngay = now.strftime("%Y-%m-%d")
        if ngay != self.ngay:
            self.ngay = ngay
            self.so_lan = {}
            self.lan_cuoi = {}

    def duoc_thu(self, moc, now):
        """True neu moc nay con luot thu va da qua khoang nghi."""
        self._kiem_tra_ngay(now)
        if self.so_lan.get(moc, 0) >= MAX_LAN_THU_MOI_MOC:
            return False
        cuoi = self.lan_cuoi.get(moc)
        if cuoi is not None:
            if (now - cuoi).total_seconds() < KHOANG_NGHI_GIUA_HAI_LAN_THU:
                return False
        return True

    def ghi_lan_thu(self, moc, now):
        self._kiem_tra_ngay(now)
        self.so_lan[moc] = self.so_lan.get(moc, 0) + 1
        self.lan_cuoi[moc] = now


def chon_moc_can_gui(now, danh_sach_moc, da_gui, trang_thai):
    """Chon moc gio can gui bao cao trong vong nay.

    Tra ve (moc_can_gui, danh_sach_moc_bo_qua).
    moc_can_gui la None nghia la khong gui gi.

    QUY TAC: chi gui MOT bao cao cho moc GAN NHAT da di qua ma chua gui.
    Cac moc cu hon bi bo qua va ghi nhat ky.

    Day chinh la cho chua loi gui trung: truoc day ba lich Windows chay bu
    cung luc, moi lich tu doan moc, nen gui ra ba bao cao trung nhau.
    """
    chua_gui = [m for m in moc_da_toi(now, danh_sach_moc) if m not in da_gui]
    if not chua_gui:
        return None, []

    can_gui = max(chua_gui)
    bo_qua = [m for m in chua_gui if m != can_gui]

    if not trang_thai.duoc_thu(can_gui, now):
        # Het luot thu cho moc gan nhat thi KHONG lui ve moc cu hon: bao cao
        # cua moc cu hon la bao cao cu, gui di se gay hieu nham.
        return None, bo_qua

    return can_gui, bo_qua
```

- [ ] **Step 5: Thêm phần gọi `report.py` và ghi nhật ký**

Nối tiếp vào `nguoi_truc.py`:

```python
def gui_bao_cao(moc, che_do_thu=False):
    """Goi report.py o TIEN TRINH RIENG de gui bao cao moc `moc`.

    Chay o tien trinh rieng vi: report.py co loi thi Nguoi truc van song, va
    phan tinh tien trong report.py khong bi dung toi.

    Tra ve True neu report.py thoat voi ma 0.
    """
    lenh = [sys.executable, str(GOC / "report.py"), "--slot", str(moc)]
    if che_do_thu:
        lenh.append("--dry")
    try:
        kq = subprocess.run(
            lenh,
            cwd=str(GOC),
            capture_output=True,
            text=True,
            timeout=CHO_REPORT_TOI_DA,
        )
    except subprocess.TimeoutExpired:
        report.log(
            f"NGUOI TRUC: report.py moc {moc}h qua thoi gian cho {CHO_REPORT_TOI_DA} giay"
        )
        return False
    except Exception as e:
        report.log(f"NGUOI TRUC: khong chay duoc report.py moc {moc}h: {e}")
        return False

    if kq.returncode == 0:
        return True
    duoi = (kq.stderr or "")[-300:]
    report.log(f"NGUOI TRUC: report.py moc {moc}h thoat voi ma {kq.returncode}: {duoi}")
    return False
```

- [ ] **Step 6: Thêm lớp `NguoiTruc` — phần canh mốc**

Nối tiếp vào `nguoi_truc.py`:

```python
class NguoiTruc:
    """Tien trinh thuong tru.

    Cac tham so `*_fn` va `dong_ho` de kiem thu thay duoc phan that (dong ho,
    gui bao cao, gui tin, doc so da gui, goi Telegram). Khi chay that thi de
    trong.

    `xa_tin_fn` va `lay_tin_fn` bat buoc phai thay duoc: neu khong thi kiem thu
    `mot_vong()` se goi mang that toi Telegram.
    """

    def __init__(self, env, danh_sach_moc, che_do_thu=False,
                 gui_bao_cao_fn=None, gui_tin_fn=None,
                 doc_da_gui_fn=None, dong_ho=None,
                 xa_tin_fn=None, lay_tin_fn=None):
        self.env = env or {}
        self.danh_sach_moc = list(danh_sach_moc) or list(MOC_MAC_DINH)
        self.che_do_thu = che_do_thu

        if gui_bao_cao_fn is None:
            def gui_bao_cao_fn(moc):
                return gui_bao_cao(moc, che_do_thu)
        if gui_tin_fn is None:
            def gui_tin_fn(text):
                return gui_tin_nhan(self.env, text)
        if doc_da_gui_fn is None:
            doc_da_gui_fn = report.ds_moc_da_gui
        if xa_tin_fn is None:
            def xa_tin_fn(env):
                return xa_tin_ton_dong(env)
        if lay_tin_fn is None:
            def lay_tin_fn(env, offset):
                return lay_tin_moi(env, offset)

        self.gui_bao_cao = gui_bao_cao_fn
        self.gui_tin = gui_tin_fn
        self.doc_da_gui = doc_da_gui_fn
        self.xa_tin = xa_tin_fn
        self.lay_tin = lay_tin_fn
        self.dong_ho = dong_ho or datetime.now

        self.trang_thai = TrangThaiThu()
        self.bat_dau = self.dong_ho()
        self.lan_gui_cuoi = None
        self.so_vong = 0
        # Cac moc da xu ly trong PHIEN nay. Can thiet vi che do --thu khong ghi
        # so gui ra file, va vi mot lan ghi so that bai khong duoc gay gui lap.
        self.da_xu_ly = set()
        self.da_xa_tin_ton_dong = False
        self.offset = None

    def _da_gui_hom_nay(self, now):
        """Tap hop cac moc da gui thanh cong hom nay, theo so tren dia."""
        try:
            return set(self.doc_da_gui(now.strftime("%Y-%m-%d"))) | self.da_xu_ly
        except Exception as e:
            report.log(f"NGUOI TRUC: khong doc duoc so da gui: {e}")
            return set(self.da_xu_ly)

    def canh_moc(self, now):
        """Kiem tra xem co moc nao can gui khong, va gui neu can."""
        moc, bo_qua = chon_moc_can_gui(
            now, self.danh_sach_moc, self._da_gui_hom_nay(now), self.trang_thai
        )
        for m in bo_qua:
            report.log(
                f"NGUOI TRUC: bo qua moc {m}h - da co bao cao moi hon chua gui"
            )
        if moc is None:
            return

        report.log(f"NGUOI TRUC: toi moc {moc}h - bat dau gui")
        self.trang_thai.ghi_lan_thu(moc, now)
        if self.gui_bao_cao(moc):
            self.da_xu_ly.add(moc)
            self.lan_gui_cuoi = now
            report.log(f"NGUOI TRUC: da gui xong moc {moc}h")
        else:
            so_lan = self.trang_thai.so_lan.get(moc, 0)
            report.log(
                f"NGUOI TRUC: gui moc {moc}h THAT BAI (lan thu {so_lan}/{MAX_LAN_THU_MOI_MOC})"
            )
```

> **Ghi chú — đọc trước khi bắt tay:** `nghe_telegram`, `xu_ly_tin`, `gui_tin_nhan`,
> `tra_loi_tin_nhan`, `tin_tu_dai` được viết ở **Task 3**. Bước này **chưa** viết `mot_vong()`.
> Vì vậy Task 2 chỉ kiểm thử được `canh_moc()` — và đó là chủ ý: phần canh mốc là phần chữa
> lỗi gửi trùng, nó phải đứng vững một mình.
>
> Trong `__init__` ở trên có dòng `def gui_tin_fn(text): return gui_tin_nhan(...)`. Hàm
> `gui_tin_nhan` **chưa tồn tại** ở bước này, nhưng điều đó **không sao**: thân hàm chỉ được
> Python đọc tới khi hàm đó được **gọi**, mà kiểm thử của Task 2 luôn truyền `gui_tin_fn` vào
> nên nhánh mặc định không bao giờ chạy. Sang Task 3 nó sẽ có thật.

- [ ] **Step 7: Chạy kiểm thử để chắc chắn Task 2 đạt**

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . -v
```

Kết quả mong đợi: `OK`, **77 bài** đạt (54 bài sau Task 1 + 23 bài mới của Task 2).

- [ ] **Step 8: Commit**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
git add nguoi_truc.py tests/test_nguoi_truc.py
git commit -m "Them nguoi_truc.py: phan canh moc gio (chua nghe Telegram)"
```

---

## Task 3: `nguoi_truc.py` — nghe Telegram

**Files:**
- Modify: `nguoi_truc.py` (thêm phần Telegram và `main()`)
- Test: `tests/test_nguoi_truc.py` (thêm hai lớp kiểm thử)

**Interfaces:**
- Consumes: `NguoiTruc` từ Task 2
- Produces:
  - `goi_telegram(env, method, params) -> (result|None, loi|None)`
  - `tham_so_lay_tin(offset) -> dict` — tham số cho `getUpdates`
  - `offset_moi_tu_ket_qua(ds) -> int|None` — `None` nếu không có tin nào
  - `xa_tin_ton_dong(env) -> (offset|None, loi|None)`
  - `lay_tin_moi(env, offset) -> (ds|None, loi|None)`
  - `tin_tu_dai(tin, chat_id_dai) -> bool`
  - `noi_dung_tin(tin) -> str`
  - `tra_loi_tin_nhan(cau_hoi, env, danh_sach_moc, bat_dau, lan_gui_cuoi, da_gui, now=None) -> str`
  - `gui_tin_nhan(env, text) -> bool`
  - `NguoiTruc.nghe_telegram()`, `NguoiTruc.xu_ly_tin(tin)`
  - `main() -> int`

**Bảo mật (bắt buộc, thiết kế mục 8):** chỉ trả lời đúng `TELEGRAM_CHAT_ID` của Đại; tin từ chat_id khác bị bỏ qua và ghi nhật ký. Lần chạy đầu phải **xả hết tin tồn đọng** bằng `offset=-1`, nếu không bot sẽ trả lời một loạt tin cũ.

- [ ] **Step 1: Viết kiểm thử thất bại**

Thêm vào `tests/test_nguoi_truc.py`, **trước** khối `if __name__ == "__main__":`:

```python
class TestTinTuDai(unittest.TestCase):
    def _tin(self, chat_id, text="hi"):
        return {"update_id": 1, "message": {"chat": {"id": chat_id}, "text": text}}

    def test_dung_chat_id_thi_nhan(self):
        self.assertTrue(nguoi_truc.tin_tu_dai(self._tin(123), "123"))

    def test_chat_id_khac_thi_bo_qua(self):
        self.assertFalse(nguoi_truc.tin_tu_dai(self._tin(999), "123"))

    def test_so_va_chuoi_deu_khop(self):
        self.assertTrue(nguoi_truc.tin_tu_dai(self._tin(123), 123))

    def test_tin_khong_co_message_thi_bo_qua(self):
        self.assertFalse(nguoi_truc.tin_tu_dai({"update_id": 1}, "123"))

    def test_tin_khong_co_chat_thi_bo_qua(self):
        self.assertFalse(nguoi_truc.tin_tu_dai({"update_id": 1, "message": {}}, "123"))


class TestNoiDungTin(unittest.TestCase):
    def test_lay_duoc_chu(self):
        tin = {"message": {"chat": {"id": 1}, "text": "  còn sống không?  "}}
        self.assertEqual(nguoi_truc.noi_dung_tin(tin), "còn sống không?")

    def test_tin_khong_co_chu_tra_ve_rong(self):
        self.assertEqual(nguoi_truc.noi_dung_tin({"message": {"chat": {"id": 1}}}), "")

    def test_tin_hong_tra_ve_rong(self):
        self.assertEqual(nguoi_truc.noi_dung_tin({}), "")


class TestThamSoLayTin(unittest.TestCase):
    def test_co_offset_thi_truyen_offset(self):
        self.assertEqual(nguoi_truc.tham_so_lay_tin(100)["offset"], 100)

    def test_offset_None_thi_khong_truyen(self):
        self.assertNotIn("offset", nguoi_truc.tham_so_lay_tin(None))

    def test_chi_nhan_update_loai_message(self):
        self.assertEqual(
            nguoi_truc.tham_so_lay_tin(None)["allowed_updates"], '["message"]'
        )


class TestOffsetMoi(unittest.TestCase):
    def test_khong_co_tin_thi_None(self):
        self.assertIsNone(nguoi_truc.offset_moi_tu_ket_qua([]))

    def test_lay_tin_cuoi_cong_mot(self):
        self.assertEqual(
            nguoi_truc.offset_moi_tu_ket_qua([{"update_id": 5}, {"update_id": 9}]), 10
        )


class TestTraLoiTinNhan(unittest.TestCase):
    def _tra_loi(self, cau_hoi):
        return nguoi_truc.tra_loi_tin_nhan(
            cau_hoi=cau_hoi,
            env={"REPORT_ACCOUNT_NAME": "Test"},
            danh_sach_moc=[8, 12, 17],
            bat_dau=luc(6),
            lan_gui_cuoi=luc(12, 1),
            da_gui={8, 12},
            now=luc(13),
        )

    def test_hoi_con_song_thi_tra_loi_tinh_trang(self):
        tl = self._tra_loi("còn sống không?")
        self.assertIn("đang chạy", tl)
        self.assertIn("17h", tl)

    def test_hoi_khong_dau_cung_hieu(self):
        self.assertIn("đang chạy", self._tra_loi("con song khong"))

    def test_tinh_trang_liet_ke_moc_da_gui_hom_nay(self):
        tl = self._tra_loi("còn sống không?")
        self.assertIn("8h", tl)
        self.assertIn("12h", tl)

    def test_hoi_cau_khac_thi_noi_ro_chua_co_AI(self):
        tl = self._tra_loi("camp nào tệ nhất tuần này?")
        self.assertIn("giai đoạn sau", tl)
        self.assertNotIn("✅", tl)

    def test_cau_hoi_rong_cung_tra_loi_chua_co_AI(self):
        self.assertIn("giai đoạn sau", self._tra_loi(""))


class TestDinhDangThoiGian(unittest.TestCase):
    def test_duoi_mot_gio_thi_ra_phut(self):
        self.assertEqual(nguoi_truc._thoi_gian_da_chay(90), "1 phút")

    def test_vai_gio_thi_ra_gio_va_phut(self):
        self.assertEqual(nguoi_truc._thoi_gian_da_chay(3 * 3600 + 120), "3 giờ 2 phút")

    def test_qua_mot_ngay_thi_ra_ngay(self):
        self.assertEqual(
            nguoi_truc._thoi_gian_da_chay(86400 + 2 * 3600), "1 ngày 2 giờ"
        )


class TestXuLyTin(unittest.TestCase):
    """Dung lai TrucGia da dinh nghia trong Task 2."""

    def test_tin_tu_nguoi_la_thi_khong_tra_loi(self):
        tg = TrucGia(luc(13))
        tg.truc.xu_ly_tin({
            "update_id": 1,
            "message": {"chat": {"id": 999}, "text": "cho xin so lieu"},
        })
        self.assertEqual(tg.tin_da_gui, [])

    def test_tin_tu_dai_hoi_con_song_thi_tra_loi(self):
        tg = TrucGia(luc(13))
        tg.truc.xu_ly_tin({
            "update_id": 1,
            "message": {"chat": {"id": 123}, "text": "còn sống không?"},
        })
        self.assertEqual(len(tg.tin_da_gui), 1)
        self.assertIn("đang chạy", tg.tin_da_gui[0])

    def test_tin_tu_dai_hoi_so_lieu_thi_bao_chua_co(self):
        tg = TrucGia(luc(13))
        tg.truc.xu_ly_tin({
            "update_id": 1,
            "message": {"chat": {"id": 123}, "text": "camp nào tệ nhất tuần này?"},
        })
        self.assertEqual(len(tg.tin_da_gui), 1)
        self.assertIn("giai đoạn sau", tg.tin_da_gui[0])

    def test_che_do_thu_thi_khong_gui_tin_ra_ngoai(self):
        tg = TrucGia(luc(13), che_do_thu=True)
        tg.truc.xu_ly_tin({
            "update_id": 1,
            "message": {"chat": {"id": 123}, "text": "còn sống không?"},
        })
        self.assertEqual(tg.tin_da_gui, [])


class TestMotVong(unittest.TestCase):
    """Ca mot vong lap. `nghe_telegram` vong dau chi xa tin ton dong."""

    def test_vong_dau_khong_gui_gi_khi_chua_toi_moc(self):
        tg = TrucGia(luc(7, 30))
        tg.truc.mot_vong()
        self.assertEqual(tg.gui_roi, [])

    def test_vong_dau_xa_tin_ton_dong_roi_moi_nghe(self):
        tg = TrucGia(luc(13))
        self.assertFalse(tg.truc.da_xa_tin_ton_dong)
        tg.truc.mot_vong()
        self.assertTrue(tg.truc.da_xa_tin_ton_dong)

    def test_nhip_tim_ghi_sau_dung_so_vong(self):
        tg = TrucGia(luc(13))
        tg.truc.so_vong = nguoi_truc.NHIP_TIM_MOI_VONG - 1
        tg.truc.mot_vong()
        self.assertEqual(tg.truc.so_vong, nguoi_truc.NHIP_TIM_MOI_VONG)
```

- [ ] **Step 2: Chạy kiểm thử để chắc chắn nó thất bại**

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . -v
```

Kết quả mong đợi: `AttributeError: module 'nguoi_truc' has no attribute 'tin_tu_dai'`.

- [ ] **Step 3: Thêm phần gọi Telegram**

Chèn vào `nguoi_truc.py`, **trước** `class NguoiTruc:`:

```python
def goi_telegram(env, method, params):
    """Goi mot API cua Telegram. Tra ve (ket_qua, loi)."""
    token = (env or {}).get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        return None, "thieu TELEGRAM_BOT_TOKEN trong .env"
    url = f"https://api.telegram.org/bot{token}/{method}"
    try:
        data = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=30) as resp:
            j = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}"
    except Exception as e:
        return None, str(e)

    if not j.get("ok"):
        return None, j.get("description", "loi khong ro")
    return j.get("result"), None


def tham_so_lay_tin(offset):
    """Tham so cho getUpdates. offset=None nghia la lay moi tin chua xac nhan."""
    params = {"timeout": 0, "allowed_updates": json.dumps(["message"])}
    if offset is not None:
        params["offset"] = offset
    return params


def offset_moi_tu_ket_qua(ds):
    """Offset cho lan goi tiep theo. Khong co tin nao thi tra ve None."""
    if not ds:
        return None
    return max(u["update_id"] for u in ds) + 1


def lay_tin_moi(env, offset):
    """Lay cac tin nhan moi chua xu ly. Tra ve (danh_sach, loi)."""
    return goi_telegram(env, "getUpdates", tham_so_lay_tin(offset))


def xa_tin_ton_dong(env):
    """Bo qua het tin nhan cu con ton dong. Tra ve (offset_moi, loi).

    Dung offset=-1: Telegram tra ve tin CUOI CUNG va danh dau moi tin cu hon
    la da nhan. Khong lam buoc nay thi lan chay dau tien bot se tra loi mot
    loat tin nhan cu cua Dai.

    Khong co tin nao ton dong thi offset_moi la None - dieu do dung, vi lan
    goi tiep theo khong truyen offset se chi nhan tin moi.
    """
    ket_qua, loi = goi_telegram(env, "getUpdates", {"offset": -1, "timeout": 0})
    if loi:
        return None, loi
    return offset_moi_tu_ket_qua(ket_qua or []), None


def tin_tu_dai(tin, chat_id_dai):
    """True neu tin nhan nay do chinh Dai gui.

    Hang rao bao mat quan trong nhat: nguoi la tim ra bot co the hoi duoc so
    lieu quang cao neu thieu phep kiem tra nay.
    """
    try:
        chat_id = tin["message"]["chat"]["id"]
    except (KeyError, TypeError):
        return False
    return str(chat_id) == str(chat_id_dai).strip()


def noi_dung_tin(tin):
    """Lay phan chu cua tin nhan. Tin hong hoac tin khong phai chu -> ''."""
    try:
        return (tin["message"].get("text") or "").strip()
    except (KeyError, TypeError, AttributeError):
        return ""


def gui_tin_nhan(env, text):
    """Gui mot tin nhan ve Telegram cho Dai. Tra ve True/False."""
    chat_id = (env or {}).get("TELEGRAM_CHAT_ID", "").strip()
    if not chat_id:
        report.log("NGUOI TRUC: thieu TELEGRAM_CHAT_ID, khong gui duoc tin tra loi")
        return False
    _, loi = goi_telegram(env, "sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True,
    })
    if loi:
        report.log(f"NGUOI TRUC: khong gui duoc tin tra loi: {loi}")
        return False
    return True
```

- [ ] **Step 4: Thêm phần soạn câu trả lời**

Nối tiếp vào `nguoi_truc.py`:

```python
def _thoi_gian_da_chay(giay):
    """Doi so giay thanh chu de doc: '3 giờ 2 phút', '1 ngày 2 giờ'."""
    giay = int(giay)
    ngay, du = divmod(giay, 86400)
    gio, du = divmod(du, 3600)
    phut = du // 60
    if ngay:
        return f"{ngay} ngày {gio} giờ"
    if gio:
        return f"{gio} giờ {phut} phút"
    return f"{phut} phút"


def _moc_ke_tiep(now, danh_sach_moc, da_gui):
    """Chu mo ta moc gio ke tiep chua gui."""
    con_lai = [m for m in danh_sach_moc if m > now.hour and m not in da_gui]
    if con_lai:
        return f"{min(con_lai)}h hôm nay"
    return "ngày mai"


def tra_loi_tin_nhan(cau_hoi, env, danh_sach_moc, bat_dau, lan_gui_cuoi, da_gui,
                     now=None):
    """Soan cau tra loi cho mot tin nhan tu Dai.

    Giai doan 2 chi tra loi duoc cau hoi suc khoe. Phan hoi so lieu can lop AI
    (Giai doan 4), nen cac cau hoi khac duoc tra loi that tha la chua co.
    """
    now = now or datetime.now()
    chuan = (cau_hoi or "").lower().strip()

    if any(tu in chuan for tu in (
        "còn sống", "con song", "sống không", "song khong",
        "còn chạy", "con chay", "alive",
    )):
        moc_txt = ", ".join(f"{m}h" for m in danh_sach_moc)
        da_gui_txt = ", ".join(f"{m}h" for m in sorted(da_gui)) or "chưa gửi mốc nào"
        lan_cuoi_txt = (
            lan_gui_cuoi.strftime("%H:%M ngày %d/%m")
            if lan_gui_cuoi else "chưa có trong phiên này"
        )
        return "\n".join([
            "✅ Người trực đang chạy.",
            f"- Máy: {env.get('REPORT_ACCOUNT_NAME', '?')}",
            f"- Đã chạy liên tục: {_thoi_gian_da_chay((now - bat_dau).total_seconds())}",
            f"- Mốc giờ của máy này: {moc_txt}",
            f"- Hôm nay đã gửi: {da_gui_txt}",
            f"- Lần gửi gần nhất: {lan_cuoi_txt}",
            f"- Mốc kế tiếp: {_moc_ke_tiep(now, danh_sach_moc, da_gui)}",
        ])

    return TRA_LOI_CHUA_CO_AI
```

- [ ] **Step 5: Thêm `nghe_telegram()`, `xu_ly_tin()` và `mot_vong()` vào lớp `NguoiTruc`**

Chèn ba phương thức vào `class NguoiTruc`, **ngay sau** `canh_moc()`:

```python
    def nghe_telegram(self):
        """Doc tin nhan Telegram moi va xu ly.

        Vong dau tien chi XA TIN TON DONG, khong tra loi - neu khong bot se
        tra loi mot loat tin nhan cu.

        Goi qua self.xa_tin / self.lay_tin (khong goi thang ham) de kiem thu
        thay duoc, khong phai goi mang that.
        """
        if not self.da_xa_tin_ton_dong:
            self.offset, loi = self.xa_tin(self.env)
            if loi:
                report.log(f"NGUOI TRUC: chua xa duoc tin ton dong: {loi}")
                return
            self.da_xa_tin_ton_dong = True
            report.log("NGUOI TRUC: da xa het tin nhan ton dong")
            return

        ds, loi = self.lay_tin(self.env, self.offset)
        if loi:
            report.log(f"NGUOI TRUC: khong lay duoc tin nhan Telegram: {loi}")
            return
        if not ds:
            return

        self.offset = offset_moi_tu_ket_qua(ds)
        for tin in ds:
            try:
                self.xu_ly_tin(tin)
            except Exception as e:
                report.log(f"NGUOI TRUC: loi khi xu ly mot tin nhan: {e}")

    def xu_ly_tin(self, tin):
        """Xu ly mot tin nhan. Tin tu nguoi la bi bo qua va ghi nhat ky."""
        chat_id_dai = self.env.get("TELEGRAM_CHAT_ID", "")
        if not tin_tu_dai(tin, chat_id_dai):
            try:
                chat_id_la = tin["message"]["chat"]["id"]
            except (KeyError, TypeError):
                chat_id_la = "?"
            report.log(f"NGUOI TRUC: bo qua tin tu chat_id la ({chat_id_la})")
            return

        cau_hoi = noi_dung_tin(tin)
        now = self.dong_ho()
        tra_loi = tra_loi_tin_nhan(
            cau_hoi=cau_hoi,
            env=self.env,
            danh_sach_moc=self.danh_sach_moc,
            bat_dau=self.bat_dau,
            lan_gui_cuoi=self.lan_gui_cuoi,
            da_gui=self._da_gui_hom_nay(now),
            now=now,
        )
        if self.che_do_thu:
            report.log(f"NGUOI TRUC [THU]: se tra loi: {tra_loi.splitlines()[0]}")
            return
        if self.gui_tin(tra_loi):
            report.log("NGUOI TRUC: da tra loi mot tin nhan")

    def mot_vong(self):
        """Mot vong lap: canh moc gio, nghe Telegram, ghi nhip tim."""
        now = self.dong_ho()
        self.canh_moc(now)
        self.nghe_telegram()
        self.so_vong += 1
        if self.so_vong % NHIP_TIM_MOI_VONG == 0:
            report.log(f"NGUOI TRUC: nhip tim - dang song, vong {self.so_vong}")
```

- [ ] **Step 6: Thêm `main()`**

Nối tiếp vào `nguoi_truc.py`:

```python
def main():
    parser = argparse.ArgumentParser(
        description="Người trực — tiến trình chạy suốt của báo cáo Meta Ads"
    )
    parser.add_argument("--thu", action="store_true",
                        help="Chạy toàn bộ luồng nhưng KHÔNG gửi gì (để kiểm chứng)")
    parser.add_argument("--gui-ngay", type=int, default=None, metavar="MOC",
                        help="Gửi ngay mốc này rồi thoát (bỏ qua canh giờ)")
    args = parser.parse_args()

    duong_dan_env = GOC / ".env"
    try:
        env = report.load_env(duong_dan_env)
    except Exception:
        print(f"LOI: Khong doc duoc file .env tai {duong_dan_env}")
        print("Cach xu ly: copy .env.example thanh .env roi dien token vao.")
        report.log("NGUOI TRUC: khong doc duoc .env - dung")
        return 1

    danh_sach_moc = report.doc_moc_tu_env(env)

    if args.gui_ngay is not None:
        if args.gui_ngay not in danh_sach_moc:
            print(
                f"LOI: Moc {args.gui_ngay}h khong nam trong danh sach moc cua may nay: "
                f"{danh_sach_moc}"
            )
            return 1
        ok = gui_bao_cao(args.gui_ngay, che_do_thu=args.thu)
        print("DA GUI" if ok else "GUI THAT BAI")
        return 0 if ok else 1

    truc = NguoiTruc(env, danh_sach_moc, che_do_thu=args.thu)
    print(f"NGUOI TRUC dang chay. Moc gio: {danh_sach_moc}. Che do thu: {args.thu}")
    report.log(
        f"NGUOI TRUC: bat dau - moc gio {danh_sach_moc}, che do thu {args.thu}"
    )

    while True:
        try:
            truc.mot_vong()
        except KeyboardInterrupt:
            report.log("NGUOI TRUC: dung theo yeu cau (Ctrl+C)")
            return 0
        except Exception as e:
            report.log(f"NGUOI TRUC: loi trong vong lap: {e}")
        try:
            time.sleep(NHIP_GIAC)
        except KeyboardInterrupt:
            report.log("NGUOI TRUC: dung theo yeu cau (Ctrl+C)")
            return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 7: Chạy kiểm thử để chắc chắn nó đạt**

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . -v
```

Kết quả mong đợi: `OK`, **105 bài** đạt (77 bài sau Task 2 + 28 bài mới).

- [ ] **Step 8: Kiểm tra `--gui-ngay` với mốc sai bị chặn**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" nguoi_truc.py --gui-ngay 22
```

Kết quả mong đợi: in `LOI: Moc 22h khong nam trong danh sach moc cua may nay: [8, 12, 17]` và thoát với mã 1. Không gửi gì.

- [ ] **Step 9: Kiểm tra `--gui-ngay` với mốc đúng, ở chế độ thử**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" nguoi_truc.py --gui-ngay 17 --thu
```

Kết quả mong đợi: chạy `report.py --slot 17 --dry`, in ra báo cáo, kết thúc bằng `[Khong gui Telegram - che do thu]`, rồi `DA GUI`. **Không** có tin nhắn nào vào Telegram.

- [ ] **Step 10: Kiểm tra `--thu` chạy được một vòng rồi dừng**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
timeout 40 "C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" nguoi_truc.py --thu
```

Kết quả mong đợi: in `NGUOI TRUC dang chay. Moc gio: [8, 12, 17]. Che do thu: True`, chạy im lặng, rồi bị `timeout` dừng. **Không** có báo cáo nào được gửi, **không** có tin nhắn Telegram nào.

Rồi kiểm tra nhật ký:

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
tail -5 logs/baocao.log
```

Kết quả mong đợi: có dòng `NGUOI TRUC: bat dau - moc gio [8, 12, 17], che do thu True` và `NGUOI TRUC: da xa het tin nhan ton dong`.

> ⚠️ **Lưu ý về bước này:** nó gọi thật Telegram `getUpdates` với `offset=-1`, nghĩa là **đánh dấu mọi tin nhắn cũ là đã nhận**. Đó chính là hành vi mong muốn của lần chạy đầu. Nhưng nếu Đại vừa nhắn cho bot một tin chưa xử lý thì tin đó sẽ bị bỏ qua. Không sao — nhắn lại là được.

- [ ] **Step 11: Commit**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
git add nguoi_truc.py tests/test_nguoi_truc.py
git commit -m "Them nguoi_truc.py: tien trinh thuong tru canh moc gio va nghe Telegram"
```

---

## Task 4: Hai file cài và gỡ

**Files:**
- Create: `cai-dat-nguoi-truc.bat`
- Create: `go-nguoi-truc.bat`

**Interfaces:**
- Consumes: `nguoi_truc.py` từ Task 2-3
- Produces: một lịch Windows duy nhất tên `NguoiTruc`, kích hoạt khi đăng nhập, có "Restart on failure", không giới hạn thời gian chạy

**Vì sao dùng PowerShell chứ không `schtasks`:** `schtasks /Create` không đặt được "Restart on failure" và "không giới hạn thời gian chạy". Thêm nữa, Giai đoạn 1 đã tốn một vòng sửa chỉ vì bẫy dấu nháy của `/TR` — `Register-ScheduledTask` tránh hẳn bẫy đó vì đường dẫn được truyền qua **biến môi trường**, không nhúng vào chuỗi lệnh.

**Ba thiết lập quan trọng:**
- `-MultipleInstances IgnoreNew` — không bao giờ có hai Người trực chạy cùng lúc.
- `-ExecutionTimeLimit (New-TimeSpan -Seconds 0)` — tiến trình chạy suốt, Windows không được tự tắt sau 3 ngày (mặc định).
- `-RestartInterval 5 phút -RestartCount 3` — nếu tiến trình chết thì Windows bật lại, tối đa 3 lần. **Cố ý giới hạn 3 lần:** nếu `.env` hỏng thì khởi động lại vô hạn sẽ ghi nhật ký mãi không dừng.

- [ ] **Step 1: Viết `cai-dat-nguoi-truc.bat`**

Tạo file `cai-dat-nguoi-truc.bat`:

```bat
@echo off
REM ============================================
REM CAI DAT NGUOI TRUC - thay 3 lich bang 1 tien trinh chay suot
REM ============================================
REM File nay lam BA viec:
REM   1. Tao MOT lich Windows ten "NguoiTruc", chay khi dang nhap.
REM   2. XOA ba lich cu (BaoCaoMetaAds_08/12/17) - co ly do:
REM      de hai lich cung song la co hai nguon gui bao cao, se bi trung.
REM   3. Kiem tra lai bang cach doc lich vua tao (khong tin dong [OK]).
REM
REM CACH CHAY: bam dup chuot vao file nay
REM Neu bao loi quyen: chuot phai -> Run as administrator
REM
REM Chay lai file nay bao nhieu lan cung duoc - no tu xoa lich cu roi tao lai.
REM ============================================

setlocal

REM --- Tu dong tim Python (giong cai-dat-lich.bat) ---
set PYTHON_EXE=

if exist "C:\Users\%USERNAME%\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe" set PYTHON_EXE=C:\Users\%USERNAME%\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe

if not defined PYTHON_EXE (
    for /f "delims=" %%P in ('where python 2^>nul') do (
        if not defined PYTHON_EXE set PYTHON_EXE=%%P
    )
)

if not defined PYTHON_EXE if exist "C:\Python313\python.exe" set PYTHON_EXE=C:\Python313\python.exe
if not defined PYTHON_EXE if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe
if not defined PYTHON_EXE if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe

set SCRIPT_DIR=%~dp0
set SCRIPT_PATH=%SCRIPT_DIR%nguoi_truc.py
set TASK_NAME=NguoiTruc

echo.
echo ============================================
echo  CAI DAT NGUOI TRUC
echo ============================================
echo.

if not defined PYTHON_EXE (
    echo LOI: Khong tim thay Python tren may nay!
    echo.
    echo Cach xu ly:
    echo   1. Cai Python tu python.org ^(ban 3.12 hoac 3.13^)
    echo   2. Hoac mo file nay bang Notepad, sua dong bat dau bang
    echo      "set PYTHON_EXE=" thanh duong dan Python tren may nay
    echo.
    pause
    exit /b 1
)

if not exist "%SCRIPT_PATH%" (
    echo LOI: Khong tim thay file nguoi_truc.py trong %SCRIPT_DIR%
    pause
    exit /b 1
)

if not exist "%SCRIPT_DIR%.env" (
    echo CANH BAO: Chua co file .env trong thu muc nay!
    echo.
    echo Cach xu ly:
    echo   1. Copy file .env.example thanh .env
    echo   2. Mo .env bang Notepad va dien token vao
    echo   3. Xem huong dan trong HUONG-DAN-DIEN-TOKEN.md
    echo.
    pause
    exit /b 1
)

echo Python : %PYTHON_EXE%
echo Script : %SCRIPT_PATH%
echo.

REM --- Kiem tra .env co khoa REPORT_SLOTS khong ---
REM Neu thieu thi he thong dung mac dinh 8,12,17,22 -> moc 22h quay tro lai
REM tren may cong ty. Canh bao truoc de Dai biet.
findstr /B /C:"REPORT_SLOTS=" "%SCRIPT_DIR%.env" >nul 2>&1
if errorlevel 1 (
    echo [CANH BAO] File .env CHUA co dong REPORT_SLOTS=
    echo   He thong se dung mac dinh 8,12,17,22, tuc la MOC 22H QUAY TRO LAI.
    echo   Cach xu ly: mo .env bang Notepad, them mot dong:
    echo       REPORT_SLOTS=8,12,17
    echo   roi bam lai file nay.
    echo.
)

REM --- Buoc 1: xoa lich NguoiTruc cu neu co ---
schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>&1

REM --- Buoc 2: xoa ba lich cu (BaoCaoMetaAds_08/12/17/22 va dang khong co so 0) ---
echo Dang tat ba lich cu...
for %%H in (08 12 17 22 8) do (
    schtasks /Delete /TN "BaoCaoMetaAds_%%H" /F >nul 2>&1
    if errorlevel 1 (
        echo   [--]  Lich cu BaoCaoMetaAds_%%H khong ton tai
    ) else (
        echo   [XOA] Da xoa lich cu BaoCaoMetaAds_%%H
    )
)
echo.

REM --- Buoc 3: tao lich NguoiTruc bang PowerShell ---
REM Duong dan duoc truyen qua BIEN MOI TRUONG, khong nhung vao chuoi lenh,
REM nen khong dinh bay dau nhay (bai hoc tu cai-dat-lich.bat ngay 28/09/2026).
echo Dang tao lich "%TASK_NAME%"...
powershell -NoProfile -Command "$py=$env:PYTHON_EXE; $sp=$env:SCRIPT_PATH; $wd=$env:SCRIPT_DIR; $a = New-ScheduledTaskAction -Execute $py -Argument ([char]34 + $sp + [char]34) -WorkingDirectory $wd; $t = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME; $s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Seconds 0) -RestartInterval (New-TimeSpan -Minutes 5) -RestartCount 3 -MultipleInstances IgnoreNew; try { Register-ScheduledTask -TaskName 'NguoiTruc' -Action $a -Trigger $t -Settings $s -Force -ErrorAction Stop | Out-Null; Write-Host '  [OK]  Da tao lich NguoiTruc' } catch { Write-Host ('  [LOI] ' + $_.Exception.Message) }"

echo.
echo ============================================
echo  KIEM TRA LAI (doc lai lich, khong tin dong [OK])
echo ============================================
echo.

powershell -NoProfile -Command "$t = Get-ScheduledTask -TaskName 'NguoiTruc' -ErrorAction SilentlyContinue; if (-not $t) { Write-Host '  [LOI] KHONG TIM THAY lich NguoiTruc.'; Write-Host '  Cach xu ly: chuot phai vao file nay, chon Run as administrator, roi bam lai.' } else { Write-Host ('  Ten lich    : ' + $t.TaskName); Write-Host ('  Trang thai  : ' + $t.State); foreach ($a in $t.Actions) { Write-Host ('  Chuong trinh: ' + $a.Execute); Write-Host ('  Tham so     : ' + $a.Arguments); Write-Host ('  Thu muc lam viec: ' + $a.WorkingDirectory) }; Write-Host ('  So trigger  : ' + $t.Triggers.Count); Write-Host ('  Chay khi pin: ' + $t.Settings.AllowStartIfOnBatteries); Write-Host ('  Gioi han thoi gian: ' + $t.Settings.ExecutionTimeLimit); Write-Host ('  So lan tu bat lai: ' + $t.Settings.RestartCount) }"

echo.
echo ============================================
echo  BUOC TIEP THEO
echo ============================================
echo.
echo   1. Kiem tra lich: dong "Tham so" o tren PHAI ket thuc bang nguoi_truc.py"
echo   2. Nhan tin "con song khong?" cho bot Telegram de thu
echo   3. Xem nhat ky: logs\baocao.log
echo.
echo De TAT hoan toan: bam file go-nguoi-truc.bat
echo De quay lai cach cu (3 lich): bam file cai-dat-lich.bat
echo.
pause
exit /b 0
```

- [ ] **Step 2: Viết `go-nguoi-truc.bat`**

Tạo file `go-nguoi-truc.bat`:

```bat
@echo off
REM ============================================
REM TAT NGUOI TRUC
REM ============================================
REM File nay lam hai viec:
REM   1. Xoa lich Windows "NguoiTruc"
REM   2. Dung tien trinh nguoi_truc.py dang chay (neu co)
REM
REM Sau khi chay file nay, he thong NGUNG gui bao cao hoan toan.
REM Muon quay lai cach cu (3 lich): bam cai-dat-lich.bat
REM ============================================

echo.
echo ============================================
echo  TAT NGUOI TRUC
echo ============================================
echo.

REM --- Buoc 1: xoa lich ---
schtasks /Delete /TN "NguoiTruc" /F >nul 2>&1
if errorlevel 1 (
    echo   [--]  Lich NguoiTruc khong ton tai
) else (
    echo   [XOA] Da xoa lich NguoiTruc
)

REM --- Buoc 2: dung tien trinh dang chay ---
REM Tim tien trinh python co dong lenh chua nguoi_truc.py.
REM Chi dung dau nhay DON trong lenh PowerShell nay, de khong dinh bay dau nhay
REM cua cmd (bai hoc tu cai-dat-lich.bat ngay 28/09/2026).
echo Dang dung tien trinh nguoi_truc.py...
powershell -NoProfile -Command "$ds = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -like '*nguoi_truc.py*' }; if (-not $ds) { Write-Host '  [--]  Khong co tien trinh nao dang chay' } else { foreach ($d in $ds) { try { Stop-Process -Id $d.ProcessId -Force -ErrorAction Stop; Write-Host ('  [XOA] Da dung tien trinh PID ' + $d.ProcessId) } catch { Write-Host ('  [LOI] Khong dung duoc PID ' + $d.ProcessId) } } }"

echo.
echo Da tat Nguoi truc.
echo.
echo Neu van thay bao cao gui ve, mo Task Manager (Ctrl+Shift+Esc),
echo tim tien trinh python.exe dang chay nguoi_truc.py va bam End task.
echo.
pause
exit /b 0
```

- [ ] **Step 3: Kiểm chứng phần dựng tham số của lịch (không tạo lịch thật)**

Tạo một file `.bat` tạm để chạy đúng đoạn PowerShell của `cai-dat-nguoi-truc.bat` với đường dẫn giả, xem nó dựng ra tham số gì. Cách này **không** tạo lịch nào.

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
cat > _thu-tham-so.bat << 'EOF'
@echo off
set PYTHON_EXE=C:\Users\nguye\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe
set SCRIPT_PATH=D:\Buddy Work AI\2026-09-14-07-50-57\nguoi_truc.py
set SCRIPT_DIR=D:\Buddy Work AI\2026-09-14-07-50-57\
powershell -NoProfile -Command "$a = New-ScheduledTaskAction -Execute $env:PYTHON_EXE -Argument ([char]34 + $env:SCRIPT_PATH + [char]34) -WorkingDirectory $env:SCRIPT_DIR; Write-Host ('Execute = ' + $a.Execute); Write-Host ('Arguments = ' + $a.Arguments); Write-Host ('WorkingDirectory = ' + $a.WorkingDirectory)"
EOF
cmd //c _thu-tham-so.bat
```

**Điều kiện đạt — cả ba dòng đều phải đúng:**
- `Execute` = `C:\Users\nguye\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe`
- `Arguments` = `"D:\Buddy Work AI\2026-09-14-07-50-57\nguoi_truc.py"` — **có** hai dấu nháy bao quanh, và **không** có phần nào khác dính vào
- `WorkingDirectory` = `D:\Buddy Work AI\2026-09-14-07-50-57\`

Nếu `Arguments` thiếu dấu nháy, đường dẫn có khoảng trắng sẽ bị Windows cắt thành hai ⇒ lịch không chạy được. Đây đúng là loại lỗi đã xảy ra ở Giai đoạn 1.

Xoá file tạm sau khi kiểm xong:

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
rm _thu-tham-so.bat
```

- [ ] **Step 4: Kiểm chứng lệnh tìm tiến trình của `go-nguoi-truc.bat` (chỉ đọc)**

Chạy đúng đoạn PowerShell của `go-nguoi-truc.bat`, nhưng bỏ phần `Stop-Process` — chỉ xem nó tìm được gì:

```bash
powershell -NoProfile -Command "$ds = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -like '*nguoi_truc.py*' }; Write-Host ('So tien trinh tim thay: ' + @($ds).Count)"
```

Kết quả mong đợi: `So tien trinh tim thay: 0` (chưa có tiến trình nào chạy). Điều cần chứng minh là lệnh **chạy được và không báo lỗi cú pháp** — chứng tỏ không dính bẫy dấu nháy.

- [ ] **Step 5: Kiểm chứng chưa có lịch `NguoiTruc` nào tồn tại**

```bash
powershell -NoProfile -Command "$t = Get-ScheduledTask -TaskName 'NguoiTruc' -ErrorAction SilentlyContinue; if ($t) { Write-Host 'DA TON TAI' } else { Write-Host 'CHUA TON TAI (dung nhu mong doi)' }"
```

Kết quả mong đợi: `CHUA TON TAI (dung nhu mong doi)`.

- [ ] **Step 6: Commit**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
git add cai-dat-nguoi-truc.bat go-nguoi-truc.bat
git commit -m "Them cai-dat-nguoi-truc.bat va go-nguoi-truc.bat"
```

> ⚠️ **Việc Đại phải làm, không phải việc agent:** chạy `cai-dat-nguoi-truc.bat`. Bước này **chưa làm** trong kế hoạch, và hai lỗi đang chạy **vẫn chưa được chữa trên máy thật** cho tới khi Đại bấm file đó. Phải bấm **từ thư mục chính** `D:\Buddy Work AI\2026-09-14-07-50-57`, không phải từ bản sao tạm dùng để thi công.

---

## Task 5: Cập nhật tài liệu

**Files:**
- Modify: `README.md`
- Modify: `HANDOFF.md`
- Modify: `QUY-TRINH-HANG-NGAY.md`
- Modify: `HUONG-DAN-MAY-CONG-TY.md`
- Modify: `HUONG-DAN-MAY-NHA.md`

**Interfaces:**
- Consumes: mọi thay đổi của Task 1-4
- Produces: tài liệu khớp với hành vi thật

> **Phương pháp:** các file này đã dài và số dòng đã trôi một lần ở Giai đoạn 1. Vì vậy **đừng dùng số dòng** — dùng `grep` tìm **đúng chuỗi** dưới đây rồi sửa. Sau khi sửa xong, chạy lại chính lệnh `grep` đó: nếu không còn dòng nào khớp thì đã xong.

- [ ] **Step 1: Quét xem còn chỗ nào nói sai**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
grep -n "cai-dat-lich\|go-lich\|bat-chay-bu\|BaoCaoMetaAds\|3 lịch\|ba lịch\|lịch Windows" \
  README.md HANDOFF.md QUY-TRINH-HANG-NGAY.md HUONG-DAN-MAY-CONG-TY.md HUONG-DAN-MAY-NHA.md
```

Đọc hết kết quả. Mỗi dòng rơi vào một trong ba nhóm:

| Nhóm | Xử lý |
|---|---|
| Nói về **trạng thái hiện tại** ("bấm `cai-dat-lich.bat` để bật", "3 lịch tự động", "lịch Windows chạy 3 mốc") | **Phải sửa** theo các bước dưới |
| Là **ghi chép lịch sử** (nhật ký một ngày cụ thể, dòng mốc thời gian) | **Giữ nguyên.** Chỉ thêm chữ "trước đây" nếu đọc ra tưởng là hiện tại |
| Nói về **file vẫn còn dùng được** (`go-lich.bat`, `cai-dat-lich.bat` như đường lùi) | **Giữ nguyên** |

- [ ] **Step 2: Sửa mục cài đặt trong `README.md`**

Tìm chuỗi `### Bước 2: Chuột phải` trong `README.md`. Thay cả mục cài đặt (từ `### Bước 2` tới trước mục tiếp theo) bằng:

```markdown
### Bước 2: Bấm đúp `cai-dat-nguoi-truc.bat`

File này làm **ba** việc, chỉ cần bấm một lần:

1. Tạo **một** lịch Windows duy nhất tên `NguoiTruc`, tự chạy khi Đại đăng nhập máy.
2. **Xoá ba lịch cũ** (`BaoCaoMetaAds_08/12/17`) — để hai lịch cùng sống là có hai nguồn
   gửi báo cáo, sẽ bị trùng.
3. Đọc lại lịch vừa tạo và in ra để kiểm tra.

Nếu báo lỗi quyền: chuột phải vào file → **Run as administrator** → bấm lại.

**Bấm từ đúng thư mục dự án** (`D:\Buddy Work AI\2026-09-14-07-50-57`). File này tự lấy
đường dẫn `nguoi_truc.py` từ chỗ nó đứng — bấm từ bản sao ở nơi khác là trỏ sai chỗ.

Kết quả mong đợi:

```
  [XOA] Da xoa lich cu BaoCaoMetaAds_08
  [XOA] Da xoa lich cu BaoCaoMetaAds_12
  [XOA] Da xoa lich cu BaoCaoMetaAds_17
  [--]  Lich cu BaoCaoMetaAds_22 khong ton tai
  [OK]  Da tao lich NguoiTruc

  Ten lich    : NguoiTruc
  Trang thai  : Ready
  Chuong trinh: C:\...\python.exe
  Tham so     : "D:\Buddy Work AI\2026-09-14-07-50-57\nguoi_truc.py"
```

> ⚠️ **Đừng tin dòng `[OK]`.** Nó chỉ nói Windows không báo lỗi, không nói tham số đã đúng.
> Điều phải nhìn là dòng **`Tham so`**: nó phải **kết thúc bằng `nguoi_truc.py"`** — có dấu
> nháy đóng ở cuối. Thiếu dấu nháy đó thì đường dẫn có khoảng trắng bị cắt làm hai và lịch
> không chạy được.

### Bước 3: Nhắn thử bot

Mở Telegram, nhắn cho bot câu:

```
còn sống không?
```

Bot trả lời kèm tình trạng: đã chạy bao lâu, mốc giờ của máy này, hôm nay đã gửi mốc nào.
Đây là cách kiểm tra nhanh nhất khi nghi ngờ hệ thống có vấn đề.
```

- [ ] **Step 3: Sửa mục tắt hệ thống trong `README.md`**

Tìm chuỗi `Bấm đúp vào file **\`go-lich.bat\`**`. Thay bằng:

```markdown
Bấm đúp vào file **`go-nguoi-truc.bat`** → lịch `NguoiTruc` bị xoá và tiến trình đang chạy
bị dừng, hệ thống ngừng gửi báo cáo hoàn toàn.

Muốn quay lại cách cũ (ba lịch rời rạc, không có Người trực): bấm **`cai-dat-lich.bat`**.
Cách cũ vẫn chạy được, nhưng vẫn còn chuyện gửi gần trùng vào các buổi sáng máy bật lại
sau khi tắt qua nhiều mốc — xem mục "Người trực là gì" bên dưới.
```

- [ ] **Step 4: Thêm mục "Người trực là gì" vào `README.md`**

Chèn **ngay trước** mục `## 🗂️ Lịch sử số liệu`:

```markdown
---

## 🧍 Người trực là gì

Trước 28/09/2026, hệ thống dùng **ba lịch Windows rời rạc**: 8h, 12h, 17h. Mỗi lịch chạy
`report.py` và script tự đoán xem mình là mốc mấy giờ. Cách đó có hai bệnh:

- **Gửi trùng.** Khi máy ngủ qua nhiều mốc, Windows cho **cả ba lịch chạy bù cùng lúc**;
  cả ba cùng đoán ra một mốc và gửi ra nhiều báo cáo giống hệt nhau.
- **Không nghe được tin nhắn.** Lịch chỉ biết *chạy*, không biết *nghe*, nên không thể
  trả lời khi Đại nhắn hỏi.

Từ Giai đoạn 2, cả ba lịch được thay bằng **một tiến trình chạy suốt** tên `NguoiTruc`,
do `nguoi_truc.py` đảm nhiệm. Nó:

| Việc | Cách làm |
|---|---|
| Canh mốc giờ | Kiểm tra đồng hồ mỗi 30 giây. Tới mốc và mốc đó chưa gửi hôm nay → gọi `report.py` kèm `--slot` |
| Gửi bù khi lỡ | Lúc khởi động, đối chiếu sổ đã gửi. Chỉ gửi **MỘT** báo cáo cho mốc gần nhất bị lỡ; các mốc cũ hơn ghi nhật ký là bỏ qua |
| Nghe Telegram | Chỉ trả lời tin từ `TELEGRAM_CHAT_ID` của Đại. Tin từ người lạ bị bỏ qua và ghi nhật ký |
| Nhịp tim | Ghi một dòng nhật ký mỗi 30 phút để biết còn sống |

**Mốc giờ là cấu hình của từng máy**, đọc từ khoá `REPORT_SLOTS` trong `.env`:

```
REPORT_SLOTS=8,12,17        ← máy công ty (đã bỏ mốc 22h)
REPORT_SLOTS=8,12,17,22     ← máy nhà
```

Muốn lấy lại mốc 22h thì sửa một dòng trong `.env` và khởi động lại Người trực. Nếu thiếu
khoá này, hệ thống dùng mặc định `8,12,17,22`.

**Giới hạn phải biết:** Người trực chỉ sống khi máy **đang bật và đang đăng nhập Windows**.
Máy tắt thì không có báo cáo — nhưng khi bật lại, nó gửi bù đúng một báo cáo cho mốc gần
nhất bị lỡ, không gửi một loạt báo cáo cũ.
```

- [ ] **Step 5: Sửa bảng cấu trúc file trong `README.md`**

Tìm khối bắt đầu bằng `├── 📄 cai-dat-lich.bat` trong `README.md`. Thay ba dòng đó bằng:

```
├── 📄 cai-dat-nguoi-truc.bat     ← Bấm để BẬT (tạo Người trực, xoá 3 lịch cũ)
├── 📄 go-nguoi-truc.bat          ← Bấm để TẮT (xoá lịch, dừng tiến trình)
├── 📄 cai-dat-lich.bat           ← Cách cũ (3 lịch rời rạc) — đường lùi nếu Người trực có sự cố
├── 📄 go-lich.bat                ← Xoá 3 lịch cũ
├── 📄 bat-chay-bu.bat            ← Chỉ còn dùng cho cách cũ (cần Admin)
```

- [ ] **Step 6: Sửa mục "Xử lý sự cố" trong `README.md`**

Tìm dòng `| \`logs/baocao.log\` trống hoàn toàn | Lịch chưa được cài → bấm \`cai-dat-lich.bat\` |`. Thay bằng **hai** dòng:

```markdown
| `logs/baocao.log` trống hoàn toàn | Chưa cài gì → bấm `cai-dat-nguoi-truc.bat` |
| Không thấy báo cáo nhưng nhật ký vẫn có dòng nhịp tim | Người trực sống, nhưng việc gửi thất bại → tìm dòng `NGUOI TRUC: gui moc ... THAT BAI` và đọc lý do |
| Nhắn bot không trả lời | Mở Task Manager (Ctrl+Shift+Esc), tìm `python.exe` chạy `nguoi_truc.py`. Không có → bấm `cai-dat-nguoi-truc.bat` lại |
```

- [ ] **Step 7: Sửa mục "Ghi chú kỹ thuật" trong `README.md`**

Tìm chuỗi `- **Task Scheduler**: 3 task tên`. Thay bằng:

```markdown
- **Task Scheduler**: **một** task tên `NguoiTruc`, kích hoạt khi đăng nhập, có "Restart on failure".
  Cách cũ dùng 3 task `BaoCaoMetaAds_08/12/17` — `cai-dat-lich.bat` vẫn tạo được nếu cần.
- **Tiến trình thường trú**: `nguoi_truc.py`, kiểm tra đồng hồ mỗi 30 giây. Gọi `report.py`
  ở **tiến trình riêng** kèm `--slot N`.
- **Mốc giờ**: khoá `REPORT_SLOTS` trong `.env`. Không có khoá thì mặc định `8,12,17,22`.
```

- [ ] **Step 8: Cập nhật `HANDOFF.md`**

Sửa ba chỗ trong `HANDOFF.md`:

**(a)** Tìm dòng `| 2 | 3 lịch tự động | Tên \`BaoCaoMetaAds_08/12/17\` |`. Thay bằng:

```markdown
| 2 | Người trực (từ 28/09/2026) | Một lịch `NguoiTruc` chạy `nguoi_truc.py` khi đăng nhập. Ba lịch `BaoCaoMetaAds_08/12/17` đã bị bỏ |
```

**(b)** Tìm dòng `| \`cai-dat-lich.bat\` | Bật 3 lịch tự động |` trong bảng "CẤU TRÚC FILE QUAN TRỌNG". Thay bằng:

```markdown
| `nguoi_truc.py` | **Tiến trình thường trú** — canh mốc giờ, gọi `report.py`, nghe Telegram |
| `cai-dat-nguoi-truc.bat` | Bật Người trực (tạo lịch `NguoiTruc`, xoá 3 lịch cũ) |
| `go-nguoi-truc.bat` | Tắt Người trực |
| `cai-dat-lich.bat` | Cách cũ: bật 3 lịch rời rạc — đường lùi |
```

**(c)** Chèn một mục mới vào **cuối** phần "🔧 GHI CHÚ KỸ THUẬT CHO TRỢ LÝ AI", ngay **trước** mục `### ⚠️ BẪY QUAN TRỌNG NHẤT`:

```markdown
### BẢN SỬA NGÀY 28/09/2026 (tiếp) — NGƯỜI TRỰC THAY BA LỊCH

**Vấn đề gốc còn lại:** ba lịch Windows rời rạc không biết gì về nhau. `--slot` (Giai đoạn 1)
đã chữa được phần lớn, nhưng khi máy thức dậy buổi sáng, cả ba lịch vẫn chạy bù cùng lúc và
`determine_period()` ánh xạ mốc 12, 17, 22 đều thành "hôm nay" ⇒ hai tin có **số giống hệt
nhau**, chỉ khác dòng tiêu đề. Đếm trong nhật ký: 4 tin trùng giảm còn 3, chưa hết.

**Đã sửa:** thay ba lịch bằng **một** tiến trình thường trú `nguoi_truc.py`, chạy qua lịch
Windows duy nhất `NguoiTruc`. Nó biết rõ lịch của chính nó nên **không đoán mốc**, và khi
khởi động chỉ gửi **một** báo cáo bù cho mốc gần nhất bị lỡ.

**Bốn quyết định kỹ thuật, kèm lý do:**

1. **`nguoi_truc.py` gọi `report.py` bằng tiến trình riêng** (`subprocess`), kèm `--slot N`.
   Không tách phần gửi của `report.py` thành hàm như bản thiết kế mục 5.4 nói. Lý do: lỗi
   trong `report.py` không giết Người trực; và không phải đụng vào phần tính tiền.
2. **Lịch `NguoiTruc` tạo bằng PowerShell `Register-ScheduledTask`**, không dùng
   `schtasks /Create`. Lý do: `schtasks` không đặt được "Restart on failure" và "không giới
   hạn thời gian chạy"; thêm nữa đường dẫn truyền qua **biến môi trường** nên tránh hẳn bẫy
   dấu nháy của `/TR` đã tốn một vòng sửa ngày 28/09.
3. **Mốc giờ chuyển vào `.env`** (khoá `REPORT_SLOTS`). `determine_period()` không còn viết
   cứng `if slot_hour == 8`; nó nhận `moc_sang_bao_cao` với mặc định 8, và `main()` truyền
   `moc_sang(danh_sach_moc)` = mốc nhỏ nhất.
4. **`cai-dat-nguoi-truc.bat` tự xoá ba lịch cũ.** Bản thiết kế mục 10 ghi hai bước riêng,
   nhưng để hai lịch cùng sống là hai nguồn gửi báo cáo, mà cơ chế chống trùng cũ đọc-rồi-ghi
   **không có khoá** nên hai tiến trình chạy sát nhau vẫn lọt.

**Nhịp tim ghi mỗi 30 phút, không phải mỗi vòng.** Bản thiết kế mục 5.1 nói "mỗi vòng"; mỗi
vòng là 30 giây ⇒ ~2.880 dòng/ngày, làm ngập `logs/baocao.log` — chính file mở đầu tiên khi
có sự cố. Phép thử sức khoẻ thật là lệnh "còn sống không?" qua Telegram.

**Đã kiểm chứng (bằng kiểm thử tự động, không phải chạy tay):** thực dậy lúc 12h05 khi chưa
gửi gì ⇒ gửi **đúng một** báo cáo mốc 12h, mốc 8h ghi nhật ký bỏ qua. Đây là bài kiểm thử
quan trọng nhất của giai đoạn.

**Giới hạn đã biết, cố ý không sửa ở giai đoạn này:**

- **Mốc 8h bị bỏ qua khi khởi động muộn.** Máy bật lúc 13h mà chưa gửi gì thì chỉ gửi báo cáo
  mốc 12h; mốc 8h (báo cáo đầy đủ cả ngày hôm trước) bị bỏ. Hệ quả: `logs/lich-su.json` có
  thể thiếu bản ghi **đầy đủ** của ngày hôm trước, chỉ còn bản **một phần** (mốc 17h của ngày
  đó). Giai đoạn 3 cần biết điều này khi so sánh với kỳ trước.
- **Một mốc chỉ được thử tối đa 3 lần trong ngày, cách nhau 5 phút.** Token Meta chết hẳn thì
  Đại nhận tối đa 3 tin cảnh báo cho mỗi mốc. Đây là chủ ý: bản thiết kế mục 7 (tự xử lý lỗi,
  tự gia hạn token) thuộc Giai đoạn 5.
- **`report.py --dry` vẫn ghi vào `logs/lich-su.json`** — hành vi có từ Giai đoạn 1, không đổi.
```

- [ ] **Step 9: Cập nhật `QUY-TRINH-HANG-NGAY.md`**

Tìm hai dòng `**Bước 4 — Tạo lịch tự động:**` và `**Bước 5 — Bật chạy bù:**`. Thay **cả hai** bằng một bước:

```markdown
**Bước 4 — Bật Người trực:** bấm đúp file `cai-dat-nguoi-truc.bat`.

File này tạo **một** lịch Windows duy nhất (`NguoiTruc`) và xoá ba lịch cũ. Từ đó hệ thống
chạy suốt khi máy bật, tự gửi báo cáo đúng 3 mốc (8h, 12h, 17h), và nghe được tin nhắn
Telegram. Không cần bấm `bat-chay-bu.bat` nữa.
```

- [ ] **Step 10: Cập nhật `HUONG-DAN-MAY-CONG-TY.md`**

**(a)** Tìm chuỗi `1. Trong thư mục \`meta-ads-report\`, tìm file **\`cai-dat-lich.bat\`**`. Thay bằng:

```markdown
1. Trong thư mục `meta-ads-report`, tìm file **`cai-dat-nguoi-truc.bat`**
```

**(b)** Tìm dòng `**Chuột phải** vào file **\`bat-chay-bu.bat\`** → **Run as administrator**.`. Thay bằng:

```markdown
Bấm đúp vào file **`cai-dat-nguoi-truc.bat`**. Nếu báo lỗi quyền thì chuột phải → **Run as administrator**.

File này tạo một lịch duy nhất tên `NguoiTruc` và xoá ba lịch cũ. **Không cần chạy
`bat-chay-bu.bat` nữa** — Người trực tự chạy khi đăng nhập, không cần Windows đánh thức máy.
```

**(c)** Tìm chuỗi `**Nếu muốn chỉ nhận 1 bộ:** bấm \`go-lich.bat\``. Thay bằng:

```markdown
**Nếu muốn chỉ nhận 1 bộ:** bấm `go-nguoi-truc.bat` ở máy không muốn chạy.
```

**(d)** Tìm hai dòng `├── Bấm cai-dat-lich.bat` và `└── Bấm bat-chay-bu.bat (Run as administrator)`. Thay bằng:

```
└── Bấm cai-dat-nguoi-truc.bat
```

- [ ] **Step 11: Cập nhật `HUONG-DAN-MAY-NHA.md`**

**(a)** Tìm chuỗi `**Lần này máy nhà PHẢI chạy lại \`cai-dat-lich.bat\`**`. Thay cả câu đó và câu giải thích ngay sau bằng:

```markdown
Bản 28/09 (Giai đoạn 2) thay **cách hệ thống chạy**: không còn ba lịch Windows rời rạc mà
là **một tiến trình thường trú**. Vì vậy máy nhà **PHẢI chạy lại `cai-dat-nguoi-truc.bat`**.
```

**(b)** Tìm dòng `2. **Chuột phải \`cai-dat-lich.bat\` → Run as administrator.** Bắt buộc có quyền Admin.` — thay bằng:

```markdown
2. **Bấm đúp `cai-dat-nguoi-truc.bat`.** Nếu báo lỗi quyền thì chuột phải → Run as administrator.
```

**(c)** Tìm khối kết quả mong đợi có ba dòng `BaoCaoMetaAds_08 : chay bu=True  tu thuc=True` (dòng 27-29) — thay cả khối bằng:

```markdown
   Ten lich    : NguoiTruc
   Trang thai  : Ready
   Tham so     : "D:\...\nguoi_truc.py"
```

**(d)** Tìm dòng `- **Mốc 22h trên máy nhà sẽ bị bỏ — đây là điều Đại ĐÃ ĐỒNG Ý ngày 28/09/2026.** Cả hai máy dùng` — thay bằng:

```markdown
- **Máy nhà GIỮ mốc 22h, máy công ty thì không.** Mốc giờ là cấu hình của từng máy, nằm ở
  khoá `REPORT_SLOTS` trong `.env`. Máy nhà để `REPORT_SLOTS=8,12,17,22`; máy công ty để
  `REPORT_SLOTS=8,12,17`. **Không copy `.env` giữa hai máy mà quên sửa dòng này.**
```

**(e)** Tìm dòng `- **Không mất tính năng chạy bù.** Bản mới của \`cai-dat-lich.bat\` tự đặt lại cả ba thiết lập` — thay bằng:

```markdown
- **Không cần tính năng "tự thức máy" nữa.** Người trực chạy suốt khi máy bật; máy tắt thì
  không có báo cáo, nhưng khi bật lại nó gửi bù đúng **một** báo cáo cho mốc gần nhất bị lỡ.
```

**(f)** Tìm dòng `> Bản 28/09 đổi cách lịch gọi script, nên máy nhà **phải** chạy lại \`cai-dat-lich.bat\` —` và hai dòng bị gạch ngang ngay sau (`~~Không cần chạy lại...~~`, `~~git pull chỉ thay file code...~~`) — thay cả ba bằng:

```markdown
> Bản 28/09 (Giai đoạn 2) đổi **cách hệ thống chạy**, nên máy nhà **phải** bấm
> `cai-dat-nguoi-truc.bat`. Chỉ `git pull` là **chưa đủ**.
```

**(g)** Tìm dòng `├── cai-dat-lich.bat (Run as administrator)   ← PHẢI chạy: tạo lại lịch có --slot` — thay bằng:

```markdown
├── cai-dat-nguoi-truc.bat (Run as administrator)   ← PHẢI chạy: tạo Người trực, xoá 3 lịch cũ
```

- [ ] **Step 12: Kiểm chứng không còn câu nói sai**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
grep -n "cai-dat-lich\|go-lich\|bat-chay-bu\|BaoCaoMetaAds\|3 lịch\|ba lịch\|lịch Windows" \
  README.md HANDOFF.md QUY-TRINH-HANG-NGAY.md HUONG-DAN-MAY-CONG-TY.md HUONG-DAN-MAY-NHA.md
```

Đọc từng dòng còn lại và tự trả lời: *"Dòng này mô tả trạng thái hiện tại hay là ghi chép
lịch sử?"* Mọi dòng mô tả trạng thái hiện tại **phải** đã nói về `NguoiTruc` / `nguoi_truc.py`.
Các dòng còn nhắc `cai-dat-lich.bat` chỉ được nằm ở ba chỗ: (1) nói rõ đó là **cách cũ / đường
lùi**, (2) ghi chép lịch sử ngày cụ thể, (3) bảng cấu trúc file có ghi chú "đường lùi".

- [ ] **Step 13: Chạy lại toàn bộ kiểm thử**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . -v
```

Kết quả mong đợi: `OK`, 105 bài đạt.

- [ ] **Step 14: Commit**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
git add README.md HANDOFF.md QUY-TRINH-HANG-NGAY.md HUONG-DAN-MAY-CONG-TY.md HUONG-DAN-MAY-NHA.md
git commit -m "Cap nhat tai lieu cho Nguoi truc: thay 3 lich bang 1 tien trinh thuong tru"
```

---

## Kiểm chứng cuối cùng

Chạy toàn bộ trước khi báo hoàn thành:

- [ ] **Toàn bộ kiểm thử đạt**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . -v
```

Mong đợi: `OK`, 105 bài đạt, 0 lỗi.

- [ ] **`report.py` chạy tay vẫn hoạt động như cũ** (tương thích ngược)

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" report.py --dry
```

Mong đợi: vẫn tự đoán mốc gần nhất, không lỗi.

- [ ] **Danh sách mốc của máy này đã là 8,12,17**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -c "import report; print(report.doc_moc_tu_env(report.load_env('.env')))"
```

Mong đợi: `[8, 12, 17]`.

- [ ] **Người trực chạy được một vòng ở chế độ thử, không gửi gì**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
timeout 40 "C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" nguoi_truc.py --thu
tail -3 logs/baocao.log
```

Mong đợi: nhật ký có `NGUOI TRUC: bat dau` và `NGUOI TRUC: da xa het tin nhan ton dong`.

- [ ] **Lịch `NguoiTruc` CHƯA tồn tại** (việc tạo lịch là của Đại)

```bash
powershell -NoProfile -Command "$t = Get-ScheduledTask -TaskName 'NguoiTruc' -ErrorAction SilentlyContinue; if ($t) { Write-Host 'DA TON TAI' } else { Write-Host 'CHUA TON TAI (dung)' }"
```

Mong đợi: `CHUA TON TAI (dung)`.

- [ ] **`.env` và bản sao lưu không lọt lên GitHub**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
git check-ignore -v .env .env.bak-truoc-gd2 logs/lich-su.json logs/da_gui.json
git status --short
```

Mong đợi: bốn dòng `check-ignore` đều in ra quy tắc chặn; `git status` không có `.env*` nào.

- [ ] **Hai file `.bat` mới đã được commit và có trong kho**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
git log --oneline -8
git ls-files | grep -E "nguoi_truc|cai-dat-nguoi-truc|go-nguoi-truc"
```

Mong đợi: ba file `nguoi_truc.py`, `cai-dat-nguoi-truc.bat`, `go-nguoi-truc.bat` đều có tên trong danh sách.

---

## Ghi chú chuyển sang Giai đoạn 3

- **`nguoi_truc.py` đã có sẵn chỗ để gắn AI.** `tra_loi_tin_nhan()` hiện trả về `TRA_LOI_CHUA_CO_AI`
  cho mọi câu hỏi không phải câu hỏi sức khoẻ. Giai đoạn 4 sẽ thay nhánh đó bằng `ai.tra_loi(câu_hỏi)`.
- **Việc Đại phải làm ở Giai đoạn 3:** lấy chìa khoá Gemini (khoảng 5 phút, có bản miễn phí) và
  dán vào dòng `GEMINI_API_KEY` trong `.env`. Khoá này **đã có sẵn** trong `.env.example` nhưng
  đang để trống.
- **`report.py` là chỗ gắn phần nhận định.** Bản thiết kế mục 5.4: `build_report()` sẽ gọi
  `ai.viet_nhan_dinh(stats_hom_nay, stats_ky_truoc)`. Dữ liệu kỳ trước lấy từ
  `lich_su.lay_ky_truoc()` — đã có từ Giai đoạn 1.
- **Rủi ro mang sang Giai đoạn 3:** `logs/lich-su.json` có thể thiếu bản ghi **đầy đủ** của ngày
  hôm trước, khi máy bật muộn và mốc 8h bị bỏ qua (xem ghi chú trong `HANDOFF.md`). Giai đoạn 3
  nên chọn kỳ so sánh theo **bản ghi đầy đủ gần nhất có thật**, thay vì giả định ngày hôm qua
  luôn có.
- **Còn tồn đọng từ Giai đoạn 1, chưa xử lý:** `compute_stats()` không loại trừ `good` khỏi `bad`,
  nên khi tài khoản có ít campaign thì báo cáo Telegram có thể liệt kê cùng một campaign ở cả
  "Camp hiệu quả" lẫn "Camp kém hiệu quả". Cần Đại quyết có sửa hay không.
