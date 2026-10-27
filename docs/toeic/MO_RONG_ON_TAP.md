# Ôn dạng bài, đề thi thử và sổ câu sai · v3

Phiên bản học liệu `dhv-toeic-2026.10-v3`, ngày 27/10/2026. Lộ trình 56 buổi giữ nguyên nội dung; bổ sung thư viện ôn tập có chấm điểm, lời giải và audio dùng ngay.

## Nội dung được đưa vào ứng dụng

| Thành phần | Trước | Hiện tại |
|---|---:|---:|
| Bài trong thư viện | 20 | 27 |
| Câu có chấm điểm | 268 | 727 |
| Chuyên đề nhận diện dạng bài | 0 | 38 |
| Mã đề cố định | 0 | 8 |
| Audio WAV có sẵn | 65 | 188 |
| Hình Part 1 | 8 SVG | 8 SVG + 10 JPG mô phỏng AI |
| Buổi học / câu tự kiểm tra | 56 / 112 | 56 / 112 |
| Thẻ từ có lịch ôn FSRS | 200 | 200 |

459 câu bổ sung gồm **399 câu chuyển thể từ nguồn MIT** và **60 câu DHV biên soạn mới**. 112 câu tự kiểm tra trong buổi và 38 ví dụ giải mẫu không cộng vào 727 câu chấm điểm.

| Part | Ngân hàng hiện có | Nội dung ôn |
|---|---:|---|
| 1 | 18 | Người, hành động, đồ vật, trạng thái, vị trí |
| 2 | 110 | WH, Yes/No, câu hỏi đuôi, lựa chọn, yêu cầu, phản hồi gián tiếp, phát biểu |
| 3 | 96 | Chủ đề, chi tiết, bước tiếp theo, hàm ý, bảng/lịch kết hợp hội thoại |
| 4 | 84 | Mục đích, điều kiện, hành động, bảng giá/lịch trình kết hợp bài nói |
| 5 | 196 | Từ loại, thì, hòa hợp, bị động, đại từ, giới từ, liên từ, quan hệ, lượng từ, dạng động từ, so sánh, collocation, cấu trúc nâng cao |
| 6 | 40 | Ngữ pháp trong đoạn, từ nối, tham chiếu, điền cả câu |
| 7 | 183 | Mục đích, chi tiết, NOT/EXCEPT, suy luận, nghĩa từ, nhiều văn bản, vị trí chèn câu |

Mỗi chuyên đề có dấu hiệu nhận diện, ít nhất 3 điểm kiến thức, 3 bước xử lý, 2 bẫy, ví dụ phân tích và nguồn đối chiếu. Bộ lọc tìm được tiếng Việt không dấu. Tải sổ tay tại `/toeic/so-tay-dang-bai.md` hoặc xem [bản trong repository](SO_TAY_DANG_BAI.md).

Số “câu trọng tâm” tính câu có nhãn dạng đó. Lượt luyện tối đa 15 câu giữ cả nhóm hội thoại/văn bản, nên có thể có thêm câu thuộc dạng khác. Chuyên đề tổng hợp có ngân hàng lớn lấy tối đa 30 câu mỗi lượt. Các lượt có thể lặp câu; không quảng cáo ngân hàng vô hạn.

## Các mã đề

| Mã đề | Số câu | Thời gian | Quan hệ dữ liệu |
|---|---:|---:|---|
| `dhv-full-01-v1` | 200 | 120 phút | Toàn phần DHV 01 |
| `dhv-full-02-v1` | 200 | 120 phút | Không trùng ID câu với DHV 01 |
| `dhv-listening-01-v1` | 100 | 45 phút | Phần nghe trích DHV 01 |
| `dhv-reading-01-v1` | 100 | 75 phút | Phần đọc trích DHV 01 |
| `dhv-mini-01-v1` đến `04-v1` | 50 mỗi đề | 35 phút | Trộn cùng ngân hàng; có thể trùng câu với mã khác |

Đề toàn phần đủ số câu Parts 1–7: **6 / 25 / 39 / 30 / 30 / 16 / 54** theo [IIBC](https://www.iibc-global.org/english/toeic/test/lr/about/format.html). Mini có 2 / 6 / 9 / 9 / 10 / 4 / 10 câu; đây là thiết kế luyện tập nội bộ.

Danh sách ID và thứ tự từng mã được cố định trong `backend/data/toeic/exam-forms.json`. Thêm câu vào ngân hàng không tự thay đề đã có. Khi thay đáng kể đề, tạo mã phiên bản mới và kiểm tra lại quan hệ không trùng; không tái sử dụng mã cũ cho một đề khác.

Đây là **đề luyện có hỗ trợ**, chưa mô phỏng đầy đủ buổi thi thật: audio tổng hợp điều khiển thủ công, nghe lại được; chỉ có đồng hồ tổng, chưa khóa riêng 45 phút nghe và 75 phút đọc. Số lượng từng Part đúng nhưng chưa áp đặt toàn bộ cơ cấu dạng con của Part 7 như đề ETS. Không quy đổi tỷ lệ đúng thành điểm TOEIC hoặc cam kết đầu ra 900. Hai bộ câu khác nhau vẫn có thể chứa câu người học đã gặp trong luyện dạng.

## Sổ câu sai

`GET /api/toeic/review` yêu cầu JWT cá nhân. Đọc tối đa 50 lượt **đã nộp** của đúng tài khoản, từ mới tới cũ. Với mỗi ID câu, kết quả ở lượt mới nhất quyết định: sai hoặc bỏ trống → cần ôn; đúng → rời danh sách. Lượt đang làm chưa tác động sổ câu sai. Không lưu bản sao lịch sử sang một collection mới.

Lọc theo Part, mở lượt ôn tối đa 30 câu và giữ nguyên các câu cùng nhóm. Các câu đi kèm ngữ cảnh cũng được chấm bình thường. Nếu toàn bộ nhóm không thể vừa giới hạn, bỏ nhóm đó ở lượt này thay vì cắt đoạn. Lịch sử ngoài cửa sổ 50 lượt không được gọi là toàn bộ lỗi tích lũy của tài khoản.

Lượt luyện lưu snapshot câu hỏi vào `toeic_attempts`; cập nhật học liệu không đổi đáp án của lượt đang làm. Bắt đầu bài có request ID chống tạo trùng; kiểm tra xung đột bao gồm dạng bài và mã đề. Tiếp tục bài trong Tiến độ. Điểm, transcript, giải thích và trích dẫn bằng chứng chỉ được trả về sau khi nộp.

## Nghiên cứu và lựa chọn nguồn

- [ETS preparation](https://www.ets.org/toeic/test-takers/prepare.html), [IIBC format](https://www.iibc-global.org/english/toeic/test/lr/about/format.html): đối chiếu cấu trúc và hướng dẫn; dẫn link, không nhập đề thương mại.
- [British Council grammar reference](https://learnenglish.britishcouncil.org/free-resources/grammar/english-grammar-reference), [B1–B2](https://learnenglish.britishcouncil.org/free-resources/grammar/b1-b2): đối chiếu kiến thức; phần giải thích, ví dụ DHV được viết mới.
- [TOEIC Question Ocean](https://github.com/kdeppaei/toeic-question-ocean): chọn nội dung mô phỏng do nguồn tự biên soạn, được cấp MIT, tại commit `a940bb8b479ef4d06af468015d757041c3d2e457`. Có câu hỏi, passage, key và 10 cảnh AI phù hợp.
- [Moodle quiz](https://docs.moodle.org/503/en/Building_Quiz): tham khảo phân loại ngân hàng, chọn nhóm và đề cố định.
- [H5P Question Set](https://h5p.org/tutorial-question-set): tham khảo phản hồi và tổng kết; không thêm code/dependency H5P.
- [HuyDao224/TOEIC-test-website](https://github.com/HuyDao224/TOEIC-test-website), [hide0123/toeicgpt](https://github.com/hide0123/toeicgpt): nghiên cứu nguồn code. Không nhập SQL, ảnh hoặc tài liệu không xác minh được quyền phân phối; không thêm phụ thuộc AI tạo đề khi chạy.

399 câu nguồn đã có lời giải tiếng Việt do DHV viết và nhãn kỹ năng. Không tự động sao chép giải thích ngoại ngữ; không thực thi JavaScript tải từ repository. Script đọc JSON hoặc AST literal, ghi revision và SHA-256. Bản nhập có thể dựng offline sau lần lấy nguồn đầu.

Kiểm tra nội dung đã loại **15 câu ứng viên**: 6 Part 5, 2 Part 2, cả nhóm 3 câu Part 3 và cả nhóm 4 câu Part 7. Ngoài ra không dùng 44 câu Part 6 cũ vì group ID gom các đoạn một chỗ trống độc lập; thay bằng nhóm 4 câu cùng văn bản ở v47/v50. Chi tiết ID/lý do nằm trong `toeic_ocean_vi.py:EXCLUDED` và `course.json:expansion`.

Hai điều chỉnh tiếng Anh được ghi nhận: P3-012 làm rõ việc cập nhật đặt phòng đã có; P1-016 mô tả hai người nhìn bản đồ thay vì suy ra mục đích đi lại hoặc việc so sánh bản đồ trên tường. Đã đối chiếu trực quan cả 10 hình với lựa chọn. Đây là rà soát có hỗ trợ AI, chưa phải chứng nhận thẩm định bởi giáo viên TOEIC độc lập.

Giữ nguyên thông báo MIT tại `backend/data/toeic/vendor/OCEAN-MIT-LICENSE.txt` và bản public tương ứng; mỗi câu chuyển thể có nguồn, revision và upstream ID. Danh sách 10 ảnh và SHA-256 nằm trong `frontend/public/toeic/licenses/OCEAN-ATTRIBUTION.md`. Các cảnh này được nguồn mô tả là ảnh AI nguyên gốc; không nhập ảnh Pexels, audio ETS hoặc khóa trả phí.

## Dữ liệu lưu ở đâu và cách bổ sung

| Đường dẫn từ gốc dự án | Vai trò |
|---|---|
| `backend/data/toeic/course.json` | Học liệu chạy thật, câu hỏi/đáp án, chuyên đề, metadata mã đề |
| `backend/data/toeic/exam-forms.json` | Danh sách câu cố định theo mã đề |
| `backend/data/toeic/vendor/` | Snapshot nguồn MIT và thông báo giấy phép |
| `backend/scripts/toeic_topics.py` | 38 hướng dẫn nhận diện dạng bài |
| `backend/scripts/toeic_ocean_vi.py` | Lời giải, nhãn và danh sách loại câu nguồn |
| `backend/scripts/toeic_extra_questions.py` | 60 câu mới, kể cả bảng/lịch nghe và chèn câu |
| `backend/scripts/toeic_expansion.py` | Chuyển thể, gắn nhãn, đảo lựa chọn ổn định, ghép dữ liệu |
| `frontend/src/features/toeic/previewCatalog.json` | Metadata và nội dung xem thử; không chứa ngân hàng đáp án chấm điểm |
| `frontend/public/toeic/audio/` | 188 WAV tổng hợp, 47,57 phút, 91,34 MB; tải khi cần |
| `frontend/public/toeic/images/` | 18 hình cho Part 1 |
| MongoDB | `toeic_profiles`, `toeic_attempts`, `toeic_cards`, `toeic_activity`: dữ liệu học cá nhân |

Sau khi sửa nguồn biên soạn, chạy từ gốc repository:

```powershell
backend/.venv/Scripts/python.exe -X utf8 backend/scripts/build_toeic_content.py
powershell.exe -NoProfile -ExecutionPolicy Bypass -File backend/scripts/build_toeic_audio.ps1
backend/.venv/Scripts/python.exe -X utf8 backend/scripts/validate_toeic.py
npm run build --prefix frontend
```

Script audio chỉ tạo lại transcript có hash thay đổi hoặc file thiếu; `-Force` tạo lại toàn bộ. Chạy PowerShell Windows có giọng tiếng Anh cài sẵn. Không cần chạy script audio trên Render vì WAV đã nằm trong frontend.

Chỉ khi chủ động cập nhật snapshot, sau khi xem lại nguồn/giấy phép, mới chạy `backend/scripts/import_toeic_ocean.py` (cần mạng, Node và dependencies frontend đã cài). Không có job tải nguồn bên ngoài trong runtime, CI hoặc deploy bình thường. Không cần migration, seed Mongo học liệu hay API AI để sinh câu lúc người học mở bài.

Kiểm tra tự động bao gồm nhóm ngữ cảnh, mã đề, lời giải, nhãn, nguồn, ảnh/hash, WAV không im lặng, transcript khớp audio manifest, metadata xem thử và sổ tay đồng bộ. Bài nghe dùng giọng tổng hợp, chưa thay cho luyện nghe đa giọng với tài liệu thật được cấp phép.
