# Nguồn gốc và thông báo thành phần TOEIC

## Code và nội dung mới

Lộ trình 56 buổi và 112 câu tự kiểm tra được biên soạn tại `backend/scripts/toeic_curriculum.py`. Bản v3 có 727 câu chấm điểm: 268 câu DHV ban đầu, 60 câu DHV mới và 399 câu chuyển thể từ TOEIC Question Ocean được cấp MIT. 38 hướng dẫn dạng bài, ví dụ và lời giải tiếng Việt được biên soạn cho DHV bằng hỗ trợ AI; chưa được thẩm định bởi giáo viên độc lập. Câu tự kiểm tra và ví dụ không cộng vào ngân hàng chấm điểm.

Code frontend/backend và script biên soạn TOEIC được viết trực tiếp cho repository này. Điều khoản của dự án tại `LICENSE` vẫn được giữ nguyên; lần nâng cấp không thay giấy phép toàn repository hay xác lập quyền đối với tài liệu của bên thứ ba.

`backend/data/toeic/course.json` và bản metadata xem thử được tạo từ các script `backend/scripts/*toeic*.py`. Phân biệt rõ nội dung DHV với phần MIT có ghi nguồn. Bộ nội dung chưa được kiểm định tương đương đề thi chuẩn hóa; không dùng nhãn “ETS official questions” hoặc “cam kết 900”.

8 SVG trong `frontend/public/toeic/images` là hình minh họa tự vẽ bằng mã. 10 JPG bổ sung là cảnh được nguồn MIT mô tả là tự tạo bằng AI, có ghi nguồn và hash riêng. 188 WAV trong `frontend/public/toeic/audio` được tổng hợp từ transcript DHV hoặc transcript MIT đã chuyển thể; không nhập audio người thật hoặc audio ETS. Script dùng API giọng đọc có sẵn của Windows, không phân phối bản cài hay mô hình giọng của Microsoft. Khi thay công cụ/giọng, kiểm tra điều khoản tương ứng của công cụ đang dùng.

## TOEIC Question Ocean · MIT

- Nguồn: [kdeppaei/toeic-question-ocean](https://github.com/kdeppaei/toeic-question-ocean).
- Copyright (c) 2026 Chun-Hsiung Luo. Giấy phép tại [commit nhập dữ liệu](https://github.com/kdeppaei/toeic-question-ocean/blob/a940bb8b479ef4d06af468015d757041c3d2e457/LICENSE).
- Giữ nguyên thông báo tại [bản backend](../../backend/data/toeic/vendor/OCEAN-MIT-LICENSE.txt) và [bản phân phối frontend](../../frontend/public/toeic/licenses/OCEAN-MIT-LICENSE.txt).
- 399 câu được chọn từ 5 file nguồn đã ghim revision; 15 câu ứng viên và 44 câu Part 6 cũ bị loại. Không khẳng định toàn bộ repository đều đã được kiểm định hoặc nhập vào DHV.
- Thay giải thích bằng tiếng Việt, bổ sung nhãn, đảo lựa chọn ổn định và tạo audio mới. P3-012 và P1-016 có chỉnh cách diễn đạt lựa chọn đúng, được ghi trong `course.json:expansion.adaptations`.
- [Ghi nguồn 10 ảnh và SHA-256](../../frontend/public/toeic/licenses/OCEAN-ATTRIBUTION.md). Không lấy ảnh Pexels trong kho.
- Mỗi câu có `provenance` gồm provider, upstream ID, revision, URL và MIT; snapshot đầy đủ lưu ở `backend/data/toeic/vendor/ocean-snapshot.json`.

Xem [phạm vi, kiểm tra và cách tái tạo](MO_RONG_ON_TAP.md). MIT của phần được nhập không thay thế giấy phép của toàn bộ EduFace hoặc quyền đối với các tài liệu bên ngoài được dẫn link.

## py-fsrs 6.3.2

- Nhà phát triển: Open Spaced Repetition.
- Nguồn: https://github.com/open-spaced-repetition/py-fsrs
- Giấy phép: MIT.
- Bản thông báo đi kèm gói cài đã được giữ nguyên tại [FSRS-MIT-LICENSE.txt](FSRS-MIT-LICENSE.txt).
- Phạm vi sử dụng: lên lịch ôn từ trên backend; `desired_retention=0.9`, tắt fuzzing để lịch có thể kiểm thử nhất quán. Đây không phải tỷ lệ ghi nhớ được bảo đảm cho từng người học.

## Tài nguyên dẫn link

ETS, IIG, British Council, Cambridge và các repository nghiên cứu giữ quyền đối với tài nguyên của họ. DHV dẫn tới trang gốc; không nhúng khóa trả phí, không sao chép đề/audio và không tuyên bố đại diện hay được các tổ chức đó chứng nhận.

Không sử dụng code hoặc dữ liệu của `HungTabe/TOEIC_VLearningApp`, Moodle hay ts-fsrs trong bản triển khai này. Việc liệt kê ở báo cáo nghiên cứu không có nghĩa các nguồn đó đã được tích hợp hoặc toàn bộ nội dung của chúng được phép tái phân phối.
