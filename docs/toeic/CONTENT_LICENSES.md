# Nguồn gốc và thông báo thành phần TOEIC

## Code và nội dung mới

Code frontend/backend và script biên soạn TOEIC được viết trực tiếp cho repository này. Điều khoản của dự án tại `LICENSE` vẫn được giữ nguyên; lần nâng cấp không thay giấy phép toàn repository hay xác lập quyền đối với tài liệu của bên thứ ba.

`backend/data/toeic/course.json` và bản metadata xem thử được tạo từ các script `backend/scripts/*toeic*.py`. Nội dung được biên soạn bằng hỗ trợ AI cho dự án, không trích ngân hàng câu hỏi thương mại. Bộ nội dung chưa được kiểm định tương đương đề thi chuẩn hóa; không dùng nhãn “ETS official questions” hoặc “cam kết 900”.

Các SVG trong `frontend/public/toeic/images` là hình minh họa tự vẽ bằng mã, không phải ảnh lấy từ sách/website. Các WAV trong `frontend/public/toeic/audio` được tổng hợp từ transcript của dự án; chúng không phải bản ghi người thật hoặc audio ETS. Script dùng API giọng đọc có sẵn của Windows, không phân phối bản cài hay mô hình giọng của Microsoft. Khi thay công cụ/giọng hoặc phân phối thương mại, kiểm tra điều khoản tương ứng của công cụ đang dùng.

## py-fsrs 6.3.2

- Nhà phát triển: Open Spaced Repetition.
- Nguồn: https://github.com/open-spaced-repetition/py-fsrs
- Giấy phép: MIT.
- Bản thông báo đi kèm gói cài đã được giữ nguyên tại [FSRS-MIT-LICENSE.txt](FSRS-MIT-LICENSE.txt).
- Phạm vi sử dụng: lên lịch ôn từ trên backend; `desired_retention=0.9`, tắt fuzzing để lịch có thể kiểm thử nhất quán. Đây không phải tỷ lệ ghi nhớ được bảo đảm cho từng người học.

## Tài nguyên dẫn link

ETS, IIG, British Council, Cambridge và các repository nghiên cứu giữ quyền đối với tài nguyên của họ. DHV dẫn tới trang gốc; không nhúng khóa trả phí, không sao chép đề/audio và không tuyên bố đại diện hay được các tổ chức đó chứng nhận.

Không sử dụng code hoặc dữ liệu của `HungTabe/TOEIC_VLearningApp`, Moodle hay ts-fsrs trong bản triển khai này. Việc liệt kê ở báo cáo nghiên cứu không có nghĩa các nguồn đó đã được tích hợp hoặc toàn bộ nội dung của chúng được phép tái phân phối.
