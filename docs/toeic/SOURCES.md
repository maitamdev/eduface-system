# Nguồn nghiên cứu cho TOEIC cùng DHV

Đối chiếu ngày 27/10/2026 (giờ Việt Nam). Phân biệt **mã nguồn phần mềm**, **học liệu được xem miễn phí**, và **quyền sao chép/phân phối học liệu**. Một kho code công khai hoặc một trang bài tập miễn phí không tự động cho phép đưa toàn bộ đề/audio vào ứng dụng khác.

## Mã nguồn đã xem xét

| Nguồn | Ghi nhận | Quyết định trong dự án |
|---|---|---|
| [open-spaced-repetition/py-fsrs](https://github.com/open-spaced-repetition/py-fsrs) | Thư viện Python lên lịch ôn cách quãng; MIT. Đã kiểm tra API `Scheduler`, `Card`, `Rating` trên bản 6.3.2 cài thật. | **Tích hợp** vào backend. Một nơi tính lịch, dùng thời gian máy chủ và lưu riêng từng người học. Giữ thông báo bản quyền tại `FSRS-MIT-LICENSE.txt`. |
| [open-spaced-repetition/ts-fsrs](https://github.com/open-spaced-repetition/ts-fsrs) | Triển khai TypeScript của FSRS; MIT. | Phương án phù hợp ứng dụng ôn offline/browser. Không cài vì dự án đã có Python backend và cần đồng bộ tiến độ tài khoản. |
| [moodle/moodle](https://github.com/moodle/moodle) | Nền tảng LMS đầy đủ; repository công bố GPL-3.0. | Tham khảo phạm vi khóa học/hoạt động; không đưa Moodle vào hệ thống React + FastAPI hiện tại vì sẽ cần vận hành thêm một LMS và tích hợp danh tính. Không sao chép code. |
| [HungTabe/TOEIC_VLearningApp](https://github.com/HungTabe/TOEIC_VLearningApp) | Ứng dụng từ vựng TOEIC, Java/Android. README ghi MIT nhưng GitHub API trả `license: null` khi kiểm tra; chưa xác minh được một file cấp phép riêng đầy đủ. | Chỉ tham khảo ý tưởng học từ. Không tái sử dụng code, database hoặc học liệu của repository; stack Android cũng khác frontend hiện tại. |

Lựa chọn thực tế: mở rộng trực tiếp EduFace bằng component React và router FastAPI mới, sử dụng **py-fsrs** cho lịch ôn. Không fork trọn một LMS hay nhập một kho đề không rõ quyền sử dụng.

## Khóa học và học liệu bên ngoài

| Nguồn chính thức | Dùng cho giai đoạn nào | Quyền truy cập / cách dùng |
|---|---|---|
| [British Council — A1–A2 grammar](https://learnenglish.britishcouncil.org/free-resources/grammar/a1-a2) | Người mới: từ loại, câu cơ bản, thì và giới từ | Bài tự học miễn phí trên website. Dẫn link; không sao chép bài tập của họ. |
| [British Council — A1 listening](https://learnenglish.britishcouncil.org/free-resources/listening/a1) | Nền tảng nghe thông tin quen thuộc, số, giờ và tình huống đơn giản | Học nghe miễn phí tại nguồn; bổ sung giọng nói ngoài bộ audio tổng hợp của DHV. |
| [Cambridge English — Activities for learners](https://www.cambridgeenglish.org/learning-english/activities-for-learners/) | Bổ sung ngữ pháp, từ, nghe/đọc từ basic đến proficient | Có bộ lọc trình độ, kỹ năng và thời lượng. Đây là luyện tiếng Anh chung, không phải khóa cam kết TOEIC 900. |
| [ETS — Prepare for TOEIC](https://www.ets.org/toeic/test-takers/prepare.html) | Làm quen bài thi và luyện theo chuẩn nhà tổ chức | Trang chuẩn bị chính thức, có tài liệu mẫu và các sản phẩm luyện thi. Xem điều kiện từng tài nguyên; không gộp tất cả thành “miễn phí”. |
| [IIG Việt Nam — Ôn luyện](https://toeic.iigvietnam.com/on-luyen/) | English Discoveries cho nền tảng; TOEIC OLPC cho luyện thi | Trang IIG giới thiệu các giải pháp học và luyện. Phần mềm/khóa có thể cần mua quyền truy cập. Không mua tài khoản hoặc chép bài trả phí vào DHV. |
| [IIG Academy](https://iigacademy.edu.vn/) | Lớp có hướng dẫn theo kết quả đầu vào và nhu cầu người học | Được dẫn từ nguồn IIG. Công cụ đọc trang trực tiếp nhận HTTP 403 trong lần kiểm tra; vì vậy không xác nhận học phí, lịch khai giảng hoặc một cam kết đầu ra cụ thể. Người học xem/liên hệ trực tiếp. |

Không có bằng chứng rằng chỉ một khóa miễn phí hoặc bộ 268 câu này bảo đảm mọi người đi từ mất gốc đến 900. Mục tiêu cao cần nền ngôn ngữ rộng, tốc độ, luyện nhiều nội dung mới và đánh giá phù hợp. Các mốc chặng trong DHV là thiết kế chương trình nội bộ, không phải bảng quy đổi chính thức giữa TOEIC và CEFR.

## Cấu trúc đề làm căn cứ

[IIBC — TOEIC Listening & Reading test format](https://www.iibc-global.org/english/toeic/test/lr/about/format.html) mô tả bài L&R 200 câu: 100 nghe trong khoảng 45 phút, 100 đọc trong 75 phút. Số câu Parts 1–7 lần lượt là **6, 25, 39, 30, 30, 16, 54**. DHV dùng các số lượng đó để ghép đề luyện và giữ nguyên nhóm hội thoại/bài đọc.

Chế độ luyện của DHV chưa tái tạo đầy đủ điều kiện thi: nghe lại và chuyển câu tự do, đồng hồ tổng 120 phút, audio tổng hợp, Part 1 dùng SVG. Không có bảng chuyển số câu đúng sang điểm TOEIC chuẩn hóa. “0” trong lời gọi lộ trình là cách nói về nền tảng người học; thang điểm L&R chính thức là 10–990.

## Cách phối hợp nguồn trong lộ trình

1. **Nền tảng → 250:** đọc f01–f04; học 10 từ mỗi bài; bổ sung British Council A1 listening và A1–A2 grammar. Tập nghe–ghi số, giờ và tự xác định chủ ngữ/động từ.
2. **250 → 450:** b01–b04; mô tả hình, phản hồi yêu cầu, thì, email. Đối chiếu ảnh/audio mẫu ETS để chuyển từ hình minh họa sang ảnh thật.
3. **450 → 650:** i01–i04; phản hồi gián tiếp, hội thoại, bị động, mạch đoạn. Bổ sung hoạt động nghe/đọc Cambridge theo mức phù hợp.
4. **650 → 800:** u01–u04; suy luận, thông báo, collocation và đọc có bằng chứng. Ghi lại nguyên nhân sai; ưu tiên Part có tỷ lệ đúng thấp trong các lượt gần nhất.
5. **800 → 900:** a01–a04; ý định, liên kết, đối chiếu hai/ba văn bản và tốc độ. Dùng tài liệu/khóa chính thức ETS hoặc IIG theo quyền truy cập để tiếp xúc câu mới và giọng tự nhiên; đề nội bộ dùng để củng cố kỹ năng, không dự đoán điểm.

Một buổi 30 phút có thể chia 5 phút ôn thẻ đến hạn, 10 phút đọc bài, 10 phút làm bài nhỏ và 5 phút ghi lỗi. Đây là gợi ý tự học, điều chỉnh theo sức học; không phải lịch bảo đảm đầu ra.

## Nguồn gốc nội dung đã đóng gói

Toàn bộ 20 bài tiếng Việt, câu ví dụ, 268 câu hỏi, đáp án, lời giải và 200 thẻ được biên soạn mới trong quá trình phát triển tính năng bằng hỗ trợ AI. Không nhập đề ETS, sách thương mại, transcript hoặc audio khóa trả phí. Cần rà soát sư phạm bổ sung khi mở rộng hoặc dùng làm đánh giá chính thức.

Audio được dựng từ chính transcript của bộ này bằng Windows System.Speech, giọng Microsoft English Desktop trên máy phát triển; không sao chép bộ cài giọng nói. SVG được vẽ bằng mã nguồn trong dự án. Thông tin nguồn, dependency và bản quyền được ghi thêm trong [CONTENT_LICENSES.md](CONTENT_LICENSES.md).
