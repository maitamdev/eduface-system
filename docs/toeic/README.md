# TOEIC cùng DHV — chạy và sử dụng

Tính năng nằm trong ứng dụng EduFace hiện có, tại `/toeic`. Tài khoản student, operator và admin đều học và lưu tiến độ riêng. Không cần hoàn thành đăng ký khuôn mặt để mở tab TOEIC.

## Chạy cùng dự án

1. Cập nhật dependency backend: `python -m pip install -r backend/requirements.txt` trong môi trường Python 3.11 của dự án. Dependency mới là `fsrs==6.3.2`.
2. Cấu hình backend theo `backend/.env.example`. MongoDB cần replica set hoặc Atlas để nộp bài/ôn từ bằng transaction. Giữ nguyên tài khoản và database đang dùng; không chạy lệnh xóa hoặc seed đè dữ liệu.
3. Mở backend: `cd backend`, rồi `python -m uvicorn main:app --host 127.0.0.1 --port 8000`.
4. Mở terminal khác: `cd frontend`, `npm ci`, rồi `npm run dev`. Trong môi trường dev không có cấu hình khác, frontend gọi `http://localhost:8000`. Nếu API ở địa chỉ khác, cấu hình `VITE_API_URL` theo `.env.example` trước khi chạy/build.
5. Đăng nhập bằng tài khoản hiện có và chọn **TOEIC cùng DHV** ở menu. Bản xem thử không cần database nằm tại `/design-preview/toeic` khi chạy Vite dev; bản này chỉ đọc học liệu, không làm bài hay lưu tiến độ.

**Học liệu đã có sẵn:** `backend/data/toeic/course.json`, `frontend/public/toeic/audio/*.wav` và `frontend/public/toeic/images/*.svg`. Không cần lấy API key, tải đề bên ngoài hoặc chạy script tạo audio để sử dụng. Docker backend đã sao chép thư mục `data`; Vite tự đưa `public/toeic` vào bản build frontend.

## Các luồng chính

- **Lộ trình theo buổi:** 4 level, 24 + 12 + 12 + 8 = 56 buổi, giữ khung Level 1–2 của người dùng và nối tới mục tiêu 900. Mỗi buổi có kiến thức, ví dụ, 2 câu tự kiểm tra, nhiệm vụ luyện, bài tập về nhà và nguồn học. Chọn nhịp 2/3/4 buổi mỗi tuần để xem lịch dự kiến; dùng **Tải lộ trình (.md)** để tải bản đầy đủ.
- **Buổi đã học:** học viên tự đánh dấu, lưu theo tài khoản và có thể bỏ đánh dấu. Đây không phải điểm kiểm tra, không tự tăng streak hay cấp chứng chỉ. Bài tự kiểm tra 2 câu không lưu kết quả lên server; đổi buổi sẽ bắt đầu lại.
- **Thư viện 27 bài luyện & 38 chuyên đề dạng bài:** giữ nguyên 5 chặng kỹ năng (20 bài nền) và thêm 7 bài luyện theo Part cùng 38 hướng dẫn nhận diện dạng bài. Làm bài đạt ít nhất 70% để đánh dấu bài luyện hoàn thành; hệ thống giữ tỷ lệ đúng tốt nhất. Nhiều buổi có thể dùng chung một bài hỗ trợ.
- **Luyện tập & 9 mã đề cố định:** khảo sát 25 câu/25 phút, bài theo từng Part, luyện theo dạng bài, sổ câu sai (từ 50 lượt nộp gần nhất) và 9 mã đề cố định (gồm **3 đề toàn phần 200 câu/120 phút không trùng ID câu**, 4 đề mini 50 câu/35 phút, 1 đề Listening 100 câu/45 phút, 1 đề Reading 100 câu/75 phút). Part 1–2 chỉ hiện nhãn A/B/C/D trước khi nộp để luyện nghe; Part 3–4 dùng audio chung theo nhóm. Đáp án, giải thích và transcript được mở sau khi nộp.
- **Tiếp tục bài:** dùng “Lưu & về góc học tập”, vào **Tiến độ → Bài đang làm → Tiếp tục**. Thời gian vẫn chạy khi rời trang. Bài hết hạn được chấm từ đáp án đã lưu trên máy chủ; không chấp nhận thay đáp án sau hạn (có 3 giây đệm cho yêu cầu nộp).
- **Lưu lỗi:** đáp án trên màn hình vẫn giữ để thử lại. Không đóng tab khi đang báo “Chưa lưu được”. Nếu hai cửa sổ cùng sửa một bài, server chặn bản ghi cũ; nút lấy bản đã lưu sẽ thay bản chưa lưu hiện tại bằng bản trên server.
- **Từ vựng (200 thẻ DHV + Sổ tra từ song ngữ 4.060 từ NGSL/TSL):** hỗ trợ 2 chế độ xem (**Thẻ lật FSRS** và **Sổ tra từ song ngữ 30 từ/trang**), tra cứu hai chiều Anh–Việt (có/không dấu), lọc theo bảng chữ cái A–Z và từ loại (`Danh từ`, `Động từ`, `Tính từ`, `Trạng từ`, `Từ chức năng`), kèm phiên âm IPA chuẩn Mỹ (`open-dict-data/ipa-dict`, MIT), nghĩa tiếng Việt (`Vietnamese Wiktionary / Kaikki.org` & biên tập DHV, CC BY-SA 4.0) và định nghĩa tiếng Anh gốc (`NGSL 1.2 + TSL 1.2`, CC BY-SA 4.0). Có thể tải trọn bộ [Sổ tay từ vựng song ngữ (.md)](SO_TAY_TU_VUNG.md) hoặc JSON.
- **Tiến độ:** mục tiêu 350/550/650/750/900, 15/30/45/60 phút mỗi ngày, chuỗi ngày học theo giờ Việt Nam, 20 lượt gần nhất, 90 ngày có hoạt động gần nhất và gợi ý Part cần củng cố.
- **Nguồn học:** link ETS, IIG, British Council, Cambridge, TOEIC Question Ocean (MIT), NGSL/TSL (CC BY-SA 4.0), Awesome TOEIC, EdNet và mã nguồn FSRS, có phân biệt nguồn tái sử dụng, nguồn tham khảo và khóa có phí.

## Phạm vi dữ liệu

| Thành phần | Số lượng |
|---|---:|
| Phiên bản học liệu | `dhv-toeic-2026.10-v4` |
| Level / kế hoạch buổi | 4 / 56 |
| Câu tự kiểm tra kiến thức (khác ngân hàng chấm điểm) | 112 |
| Ví dụ và phân tích trong lộ trình | 112 |
| Thời lượng trong buổi (chưa tính tự học) | 85,5 giờ |
| Chặng / bài trong thư viện / chuyên đề dạng bài | 5 / 27 / 38 |
| Câu hỏi có chấm điểm và lời giải tiếng Việt | 1.376 |
| Part 1 / 2 / 3 / 4 / 5 / 6 / 7 | 33 / 151 / 135 / 117 / 400 / 96 / 444 |
| Mã đề cố định (3 đề toàn phần 200 câu không trùng ID) | 9 |
| Thẻ từ vựng tiếng Việt DHV có câu ví dụ, IPA & từ loại | 200 |
| Sổ tra từ song ngữ NGSL 1.2 + TSL 1.2 (Anh–Việt + IPA + từ loại, CC BY-SA 4.0 & MIT) | 4.060 |
| Audio tổng hợp dựng sẵn | 268 WAV, khoảng 71,44 phút, 137,17 MB |
| Hình Part 1 | 33 (8 SVG + 20 JPG AI theo MIT + 5 JPG Pexels) |

Đề 200 câu giữ nguyên nhóm hội thoại/bài đọc và đúng số lượng 6/25/39/30/30/16/54. Đây là **chế độ luyện có hỗ trợ**: audio điều khiển thủ công, nghe lại được, chưa ép 45 phút nghe riêng và 75 phút đọc riêng. Các đề lấy từ cùng ngân hàng nên có thể trùng câu. Bộ học liệu chưa được chuẩn hóa độ khó hoặc hiệu chỉnh thống kê để quy đổi điểm; ứng dụng chỉ báo số câu đúng và tỷ lệ phần trăm.

“Từ 0” nghĩa là người mới học; điểm thi TOEIC L&R chính thức không bắt đầu từ 0. Mốc chặng, thời lượng gợi ý và bài khảo sát nội bộ không chứng nhận trình độ hay bảo đảm đạt 900. Hai mươi bài ngắn và 200 từ là bộ khởi đầu; cần bổ sung luyện nghe tự nhiên, vốn từ rộng và đề chính thức cho mục tiêu cao.

## Tạo lại / thêm học liệu

Lộ trình được biên soạn tại `backend/scripts/toeic_curriculum.py`. Builder tạo dữ liệu chung, [bản 56 buổi](LO_TRINH_CHI_TIET.md) và file tải tại `frontend/public/toeic/lo-trinh-dhv.md`. Không sửa riêng các bản sinh ra. Xem [thiết kế và phạm vi](THIET_KE_CHUONG_TRINH.md) để phân biệt kế hoạch buổi, bài hỗ trợ, tự kiểm tra và đánh giá chính thức.

Các script dùng đường dẫn dự án, không cần database:

```powershell
.\backend\.venv\Scripts\python.exe -X utf8 backend/scripts/import_toeic_lexicon.py
.\backend\.venv\Scripts\python.exe -X utf8 backend/scripts/build_toeic_content.py
.\backend\.venv\Scripts\python.exe -X utf8 backend/scripts/build_toeic_images.py
powershell -NoProfile -ExecutionPolicy Bypass -File backend/scripts/build_toeic_audio.ps1
.\backend\.venv\Scripts\python.exe -X utf8 backend/scripts/validate_toeic.py
```

Tạo audio chỉ cần khi chỉnh transcript: script dùng Windows `System.Speech` với giọng English Desktop và không gọi dịch vụ bên ngoài. Bản audio dựng sẵn chạy trên frontend ở mọi hệ điều hành. Thiết bị không có giọng English Desktop cần cài giọng phù hợp hoặc dùng bản WAV đã có. Nút “Nghe từ” dùng giọng trình duyệt nếu có; bài nghe chính không phụ thuộc chức năng này.

Nguồn biên soạn nằm trong `backend/scripts/build_toeic_content.py`, `toeic_vocabulary.py`, `toeic_questions_basic.py`, `toeic_questions_context.py`, `toeic_topics.py`, `toeic_extra_questions.py`, `toeic_ocean_vi.py`, `toeic_ocean_more_vi.py`, `toeic_expansion.py`, `toeic_source_expansion.py` và `import_toeic_lexicon.py`. Chỉnh ở các file nguồn rồi chạy build, không sửa riêng JSON sinh ra. Giữ ID bài/từ ổn định khi nội dung còn cùng ý nghĩa; tăng version khi thay đổi đáng kể. Khi thay transcript, dùng audio ID mới nếu cần giữ nguyên lượt luyện cũ: attempt lưu snapshot câu hỏi nhưng file audio là tài nguyên tĩnh theo ID.

Mỗi câu có một đáp án đúng; lời giải nên giải thích bằng chứng và bẫy. Part 1–2 phải khớp thứ tự A/B/C/D trong audio. Part 3–4 có nhóm 3 câu; Part 6 có nhóm 4 câu. Mọi phần phải đủ số câu để chọn đề đầy đủ. Script validate kiểm tra nội dung, nhóm, đủ audio/hình, âm thanh không rỗng, kho từ mở và 30 cách ghép đề.

## Kiểm thử

```powershell
# Từ thư mục backend; chỉ trỏ URI kiểm thử tới replica set localhost riêng.
$env:APP_ENV='test'
$env:MONGODB_INTEGRATION_URI='mongodb://127.0.0.1:27028/?replicaSet=eduface-test'
.\.venv\Scripts\python.exe -m pytest -q

# Từ thư mục frontend
npm test
npm run build
```

Các integration test tự tạo database tên ngẫu nhiên `eduface_integration_*`, kiểm tra chỉ kết nối localhost và chỉ dọn database do chính test tạo. Khi không đặt `MONGODB_INTEGRATION_URI`, integration test sẽ skip; cần chạy có replica set trước khi bàn giao thay đổi server. CI đã bổ sung kiểm tra học liệu/audio và các transaction TOEIC.

## Lưu trữ và API

Trạng thái buổi nằm tại `toeic_profiles.curriculum_completed`. `PUT /api/toeic/curriculum/sessions/{id}` nhận `{ "completed": true/false }`, chỉ ghi theo JWT của người gọi; GET progress trả danh sách ID đã học. Không cần seed hay migration dữ liệu. Catalog bổ sung `curriculum`, `topics`, `exams`, `lexicon_count`; frontend có nhánh dự phòng nếu nhận catalog cũ trong lúc triển khai.

Nội dung versioned ở JSON; tiến độ MongoDB nằm trong `toeic_profiles`, `toeic_attempts`, `toeic_cards`, `toeic_activity`. Attempt lưu snapshot câu hỏi để kết quả cũ không bị thay bởi cập nhật nội dung. Mọi truy vấn tiến độ lọc theo JWT user ID; API key dùng chung không được ghi tiến độ cá nhân. Nộp bài và ghi lịch FSRS dùng transaction để tránh ghi dở dang.

API dưới `/api/toeic`: `GET catalog`, `GET lessons/{id}`, `GET progress`, `PUT preferences`, `PUT curriculum/sessions/{id}`, `GET review`, `POST attempts`, `GET attempts/{id}`, `PUT attempts/{id}/answers`, `POST attempts/{id}/submit`, `GET vocabulary`, `GET lexicon`, `POST vocabulary/{id}/review`. Lưu đáp án dùng revision để chặn ghi đè; tạo bài/ôn từ có UUID chống ghi lặp khi thử lại. Không có endpoint trả đáp án bài chưa nộp. Đây là công cụ tự học, không phải hệ thống coi thi chống gian lận.
