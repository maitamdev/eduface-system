# Ôn dạng bài, đề thi thử, kho từ mở và sổ câu sai · v4

Phiên bản học liệu `dhv-toeic-2026.10-v4`, ngày 27/10/2026. Lộ trình 56 buổi, 727 câu của bản v3 và 8 mã đề cũ giữ nguyên hoàn toàn nội dung; bổ sung toàn bộ phần câu hỏi đã rà soát còn lại từ TOEIC Question Ocean, mã đề toàn phần thứ ba (`DHV 03`) và kho từ mở NGSL + TOEIC Service List (`4.060` từ).

## Nội dung được đưa vào ứng dụng

| Thành phần | Bản v1/v2 | Bản v3 | Hiện tại (v4) |
|---|---:|---:|---:|
| Bài trong thư viện | 20 | 27 | 27 |
| Câu có chấm điểm | 268 | 727 | 1.376 |
| Chuyên đề nhận diện dạng bài | 0 | 38 | 38 |
| Mã đề cố định | 0 | 8 | 9 |
| Audio WAV có sẵn | 65 | 188 | 268 |
| Hình Part 1 | 8 SVG | 8 SVG + 10 JPG AI | 8 SVG + 20 JPG AI + 5 JPG Pexels |
| Buổi học / câu tự kiểm tra | 56 / 112 | 56 / 112 | 56 / 112 |
| Thẻ từ tiếng Việt DHV (FSRS) | 200 | 200 | 200 |
| Kho từ mở NGSL + TSL (CC BY-SA 4.0, FSRS) | 0 | 0 | 4.060 |

1.108 câu bổ sung so với bản gốc gồm **1.048 câu chuyển thể từ nguồn MIT** (399 câu ở v3 + 649 câu ở v4, từ tổng 1.107 câu của 12 gói dữ liệu nguồn) và **60 câu DHV biên soạn mới**. 112 câu tự kiểm tra trong buổi và 38 ví dụ giải mẫu không cộng vào 1.376 câu chấm điểm.

| Part | Ngân hàng hiện có | Nội dung ôn |
|---|---:|---|
| 1 | 33 | Người, hành động, đồ vật, trạng thái, vị trí |
| 2 | 151 | WH, Yes/No, câu hỏi đuôi, lựa chọn, yêu cầu, phản hồi gián tiếp, phát biểu |
| 3 | 135 | Chủ đề, chi tiết, bước tiếp theo, hàm ý, bảng/lịch kết hợp hội thoại |
| 4 | 117 | Mục đích, điều kiện, hành động, bảng giá/lịch trình kết hợp bài nói |
| 5 | 400 | Từ loại, thì, hòa hợp, bị động, đại từ, giới từ, liên từ, quan hệ, lượng từ, dạng động từ, so sánh, collocation, cấu trúc nâng cao |
| 6 | 96 | Ngữ pháp trong đoạn, từ nối, tham chiếu, điền cả câu |
| 7 | 444 | Mục đích, chi tiết, NOT/EXCEPT, suy luận, nghĩa từ, nhiều văn bản, vị trí chèn câu |

Mỗi chuyên đề có dấu hiệu nhận diện, ít nhất 3 điểm kiến thức, 3 bước xử lý, 2 bẫy, ví dụ phân tích và nguồn đối chiếu. Bộ lọc tìm được tiếng Việt không dấu. Tải sổ tay tại `/toeic/so-tay-dang-bai.md` hoặc xem [bản trong repository](SO_TAY_DANG_BAI.md).

Số “câu trọng tâm” tính câu có nhãn dạng đó. Lượt luyện tối đa 15 câu giữ cả nhóm hội thoại/văn bản, nên có thể có thêm câu thuộc dạng khác. Chuyên đề tổng hợp có ngân hàng lớn lấy tối đa 30 câu mỗi lượt. Khi ngân hàng có các nhóm câu thay thế dùng chung một đoạn hội thoại/bài nói, thuật toán chọn đề chỉ lấy tối đa một nhóm cho mỗi ngữ cảnh nghe trong một lượt.

## Các mã đề

| Mã đề | Số câu | Thời gian | Quan hệ dữ liệu |
|---|---:|---:|---|
| `dhv-full-01-v1` | 200 | 120 phút | Toàn phần DHV 01 |
| `dhv-full-02-v1` | 200 | 120 phút | Không trùng ID câu với DHV 01 |
| `dhv-full-03-v1` | 200 | 120 phút | Không trùng ID câu và ngữ cảnh với DHV 01, DHV 02 |
| `dhv-listening-01-v1` | 100 | 45 phút | Phần nghe trích DHV 01 |
| `dhv-reading-01-v1` | 100 | 75 phút | Phần đọc trích DHV 01 |
| `dhv-mini-01-v1` đến `04-v1` | 50 mỗi đề | 35 phút | Trộn cùng ngân hàng; có thể trùng câu với mã khác |

Đề toàn phần đủ số câu Parts 1–7: **6 / 25 / 39 / 30 / 30 / 16 / 54** theo [IIBC](https://www.iibc-global.org/english/toeic/test/lr/about/format.html). Mini có 2 / 6 / 9 / 9 / 10 / 4 / 10 câu; đây là thiết kế luyện tập nội bộ.

Danh sách ID và thứ tự từng mã được cố định trong `backend/data/toeic/exam-forms.json`. 727 câu cũ và 8 mã đề của bản v3 giữ nguyên fingerprint SHA-256. Đây là **đề luyện có hỗ trợ**, chưa mô phỏng đầy đủ buổi thi thật: audio tổng hợp điều khiển thủ công, nghe lại được; chỉ có đồng hồ tổng, chưa khóa riêng 45 phút nghe và 75 phút đọc. Không quy đổi tỷ lệ đúng thành điểm TOEIC hoặc cam kết đầu ra 900.

## Kho từ mở NGSL + TOEIC Service List

Bên cạnh 200 thẻ từ tiếng Việt DHV, tab **Từ vựng** có thêm chế độ **Kho từ mở (4.060 từ)** tích hợp từ:
- **NGSL 1.2** (Charles Browne, Brent Culligan, Joseph Phillips): 2.809 từ nền tảng xếp theo tần suất SFI.
- **TOEIC Service List 1.2** (Charles Browne, Brent Culligan): 1.250 từ thương mại/công sở xếp hạng, cùng 2 mục trong bảng định nghĩa của tác giả (`born` chưa xếp hạng và `criteria` dùng chung với NGSL).
- Sáu mục xếp hạng TSL thiếu định nghĩa trong bảng XLSX gốc (`by-law`, `café`, `e-book`, `entrée`, `résumé`, `smartphone`) được DHV bổ sung định nghĩa tiếng Anh và gắn nhãn `định nghĩa do DHV bổ sung`.
- Hỗ trợ lọc theo danh sách (`NGSL`, `TSL`, `Tất cả`), trạng thái học (`Đến hạn ôn`, `Chưa học`, `Đã bắt đầu học`), tìm kiếm không phân biệt dấu (`cafe` khớp `café`, `e-mail` khớp `email`), phân trang phía server (`GET /api/toeic/lexicon`) và ôn thẻ FSRS lưu riêng theo tài khoản (`POST /api/toeic/vocabulary/{id}/review`).
- Dữ liệu gốc và bản điều chỉnh được phân phối lại theo **CC BY-SA 4.0** tại `/toeic/lexicon.json` và `/toeic/licenses/NGSL-TSL.md`.

## Sổ câu sai

`GET /api/toeic/review` yêu cầu JWT cá nhân. Đọc tối đa 50 lượt **đã nộp** của đúng tài khoản, từ mới tới cũ. Với mỗi ID câu, kết quả ở lượt mới nhất quyết định: sai hoặc bỏ trống → cần ôn; đúng → rời danh sách. Lượt đang làm chưa tác động sổ câu sai. Không lưu bản sao lịch sử sang một collection mới.

## Nghiên cứu và lựa chọn nguồn theo danh sách đề xuất

- **[TOEIC Question Ocean](https://github.com/kdeppaei/toeic-question-ocean)** (`MIT`, commit `a940bb8b479ef4d06af468015d757041c3d2e457`): đối chiếu toàn bộ 12 gói dữ liệu trong `index.html` (`1.107` câu). Nhập **1.048 câu** sau rà soát (399 câu ở v3 + 649 câu ở v4), loại **59 câu** (15 câu ứng viên có lỗi + 44 câu Part 6 cũ chỉ là câu rời rạc). Nhập 20 cảnh AI theo MIT và 5 ảnh chụp theo [Pexels License](https://www.pexels.com/license/) có ghi nguồn tác giả riêng.
- **[seikaikyo/toeic-practice](https://github.com/seikaikyo/toeic-practice)**: kiểm tra trực tiếp `LICENSE` và `NOTICE` cho thấy mã nguồn ứng dụng và ngân hàng câu hỏi giữ bản quyền độc quyền (`All Rights Reserved`), chỉ thư mục `backend/data/vocabulary` dùng dữ liệu mở. Vì vậy **không nhập mã nguồn hay câu hỏi** từ repo này; thay vào đó lấy trực tiếp bộ từ gốc **NGSL 1.2** và **TSL 1.2** từ công bố của tác giả theo CC BY-SA 4.0.
- **[thu-tram/awesome-toeic](https://github.com/thu-tram/awesome-toeic)**: là danh mục liên kết tài nguyên luyện thi, không phải kho câu hỏi tự thân. Đã tích hợp vào mục **Nguồn học** để người học tra cứu thêm theo điều kiện từng trang đích.
- **[ETS Official Samples](https://www.ets.org/toeic/test-takers/prepare.html)** & **[IIBC format](https://www.iibc-global.org/english/toeic/test/lr/about/format.html)**: đối chiếu cấu trúc đề và dẫn link chính thức; không sao chép hay phân phối lại PDF/audio của ETS.
- **[EdNet Dataset](https://github.com/riiid/ednet)**: bộ dữ liệu tương tác học tập theo `CC BY-NC 4.0` (chỉ cho mục đích nghiên cứu phi thương mại, không cung cấp đầy đủ văn bản câu hỏi/lựa chọn/audio để dựng đề luyện). Đã ghi nhận trong mục **Nguồn học** như tài liệu nghiên cứu hành vi học, không sinh câu hỏi giả lập từ metadata.

Toàn bộ 1.048 câu nguồn đã có lời giải tiếng Việt do DHV biên soạn và nhãn kỹ năng. Không thực thi JavaScript tải từ repository nguồn: `frontend/scripts/extract-toeic-source.mjs` chỉ đọc AST tĩnh và bị kiểm thử đơn vị chặn thực thi lệnh hay getter. Các điều chỉnh ngữ cảnh/lựa chọn để khử phương án đồng thời đúng hoặc khôi phục chỗ trống bị in lộ đáp án (như `P6-G17`, `P6-G18`, `P4-G18`, `P7-R78`, `P7-R79`, `P7-R82` và các câu trong `toeic_ocean_more_vi.py`) đều được lưu vết trong `course.json:expansion`.

## Dữ liệu lưu ở đâu và cách bổ sung

| Đường dẫn từ gốc dự án | Vai trò |
|---|---|
| `backend/data/toeic/course.json` | Học liệu chạy thật (`1.376` câu), chuyên đề, metadata 9 mã đề |
| `backend/data/toeic/exam-forms.json` | Danh sách câu cố định theo 9 mã đề |
| `backend/data/toeic/lexicon.json` | Kho từ mở NGSL + TSL (`4.060` từ, CC BY-SA 4.0) |
| `backend/data/toeic/vendor/` | Snapshot nguồn MIT (`ocean-complete-snapshot.json`), file gốc NGSL/TSL và giấy phép |
| `backend/scripts/toeic_topics.py` | 38 hướng dẫn nhận diện dạng bài |
| `backend/scripts/toeic_ocean_vi.py` & `toeic_ocean_more_vi.py` | Lời giải tiếng Việt, nhãn, danh sách loại bỏ và các chỉnh sửa câu nguồn |
| `backend/scripts/toeic_extra_questions.py` | 60 câu DHV mới, kể cả bảng/lịch nghe và chèn câu |
| `backend/scripts/toeic_expansion.py` & `toeic_source_expansion.py` | Chuyển thể, gắn nhãn, đảo lựa chọn ổn định, ghép dữ liệu và tạo mã đề thứ ba |
| `backend/scripts/import_toeic_sources.py` & `import_toeic_lexicon.py` | Công cụ nhập có kiểm tra hash từ nguồn ghim cố định |
| `frontend/src/features/toeic/previewCatalog.json` | Metadata và nội dung xem thử; không chứa ngân hàng đáp án chấm điểm |
| `frontend/public/toeic/audio/` | 268 WAV tổng hợp, 71,44 phút, 137,17 MB |
| `frontend/public/toeic/images/` | 33 hình cho Part 1 (8 SVG + 20 JPG AI + 5 JPG Pexels) |
| `frontend/public/toeic/lexicon.json` | Bản phân phối công khai của kho từ mở CC BY-SA 4.0 |
| MongoDB | `toeic_profiles`, `toeic_attempts`, `toeic_cards`, `toeic_activity`: dữ liệu học cá nhân |

Sau khi sửa nguồn biên soạn, chạy từ gốc repository:

```powershell
backend/.venv/Scripts/python.exe -X utf8 backend/scripts/import_toeic_lexicon.py
backend/.venv/Scripts/python.exe -X utf8 backend/scripts/build_toeic_content.py
powershell.exe -NoProfile -ExecutionPolicy Bypass -File backend/scripts/build_toeic_audio.ps1
backend/.venv/Scripts/python.exe -X utf8 backend/scripts/validate_toeic.py
npm test --prefix frontend
npm run build --prefix frontend
```
