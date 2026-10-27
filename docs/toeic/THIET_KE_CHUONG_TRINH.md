# Thiết kế chương trình TOEIC cùng DHV

Ngày đối chiếu: 27/10/2026. Yêu cầu đầu vào là bảng 24 buổi Level 1, 12 buổi Level 2 của người dùng, trong bối cảnh tính năng học từ nền tảng đến mục tiêu 900.

## Kết quả thiết kế

| Chặng | Buổi | Nội dung và đầu ra | Mốc điểm định hướng |
|---|---:|---|---|
| Level 1 | 24 | Buổi 1–12: cấu trúc, từ loại, thì, bị động, phân từ, mệnh đề, so sánh. Buổi 13–23: luân phiên Part 5 và Part 1–2 đúng khung đã cung cấp. Buổi 24: khảo sát và chữa lỗi. | 350–450 |
| Level 2 | 12 | Giữ thứ tự Reading 5, Reading 6–7, Listening 1–2, Listening 3–4; bao gồm relative clauses, rút gọn, quantifiers, double/triple passage, shopping, office, advertisement, announcement, lease. | 500–650 |
| Level 3 | 12 | Đáp lời gián tiếp, nhiều người nói, ý định, điều kiện, liên kết đoạn, suy luận, đọc nhiều nguồn, graphic, tốc độ và đề tổng hợp. | 700–800 |
| Level 4 | 8 | Paraphrase tinh, từ vựng chính xác, suy luận, hai đề mới, chữa sâu, kiểm tra ổn định và kế hoạch thi. | 850–900+ |

56 buổi gồm **53 buổi 90 phút và 3 buổi 120 phút**, tổng **85,5 giờ trong buổi**. Tự học gợi ý 45 phút/ngày; thêm thời gian chữa đề và tuần ôn khi cần. Lịch 2/3/4 buổi mỗi tuần tương ứng 28/19/14 tuần khi xếp từng level trọn tuần. Đây là tính lịch, không phải dự báo thời gian để mọi học viên đạt một điểm số.

Mỗi buổi có 3 mục tiêu, 2–3 điểm kiến thức, 2 ví dụ có giải thích, 2 câu tự kiểm tra, nhiệm vụ luyện, bài tập về nhà, 6 từ/cụm trọng tâm, bài hỗ trợ trong DHV, nguồn bổ trợ và phân bổ thời gian. Toàn bộ bảng và nội dung từng buổi nằm trong [LO_TRINH_CHI_TIET.md](LO_TRINH_CHI_TIET.md), được sinh từ cùng dữ liệu dùng trong ứng dụng.

## Điều chỉnh sư phạm so với bảng đầu vào

- Giữ nguyên số buổi và trục nội dung của Level 1–2. Sửa cách viết “Sentence Structure”; bỏ các ký tự điều khiển bị lẫn trong bản dán.
- “Rút gọn chủ ngữ” được giải thích thành rút gọn mệnh đề trạng ngữ với chủ thể phù hợp, không hướng dẫn xóa chủ ngữ vô điều kiện. Tham khảo [British Council — Participle clauses](https://learnenglish.britishcouncil.org/free-resources/grammar/c1/participle-clauses).
- Bổ sung nghe số/giờ, trọng âm, học cụm từ, truy hồi trước khi xem đáp án và sổ lỗi xuyên suốt, không đợi đến cuối khóa mới luyện.
- Level 1 final dùng khảo sát nội bộ 25 câu và chữa bài; không gọi đây là đề TOEIC chính thức. Level 2 buổi 12 giữ chủ đề Announcement/Lease, đề tổng kết 200 câu là hoạt động riêng ngoài buổi.
- Thêm graphic và nghe người thật ở chặng nâng cao. Ngân hàng hiện có chưa bao phủ đầy đủ dạng nghe có bảng/sơ đồ, nên dẫn tới mẫu chính thức thay vì ghi là đã có bài tương ứng trong DHV.
- Không gắn nhãn CEFR A1/B1/C1 thành mức điểm TOEIC tương đương. Mức CEFR của nguồn chỉ giúp chọn tài liệu tiếng Anh bổ trợ.

## Nguồn làm căn cứ

| Nguồn | Vai trò trong thiết kế |
|---|---|
| [ETS — Preparation materials](https://www.ets.org/toeic/test-takers/prepare.html) | Mẫu chính thức, handbooks và sản phẩm luyện; dùng đề mới theo quyền truy cập. |
| [IIBC — Test format](https://www.iibc-global.org/english/toeic/test/lr/about/format.html) | Đối chiếu 7 Part, số câu 6/25/39/30/30/16/54; 100 nghe khoảng 45 phút, 100 đọc 75 phút. |
| [British Council — Grammar reference](https://learnenglish.britishcouncil.org/free-resources/grammar/english-grammar-reference) | Tra từ loại, đại từ, lượng từ, động từ và cấu trúc câu. |
| [British Council — A1–A2](https://learnenglish.britishcouncil.org/free-resources/grammar/a1-a2), [B1–B2](https://learnenglish.britishcouncil.org/free-resources/grammar/b1-b2) | Chọn điểm ngữ pháp bổ trợ cho từng buổi; học và làm bài tại nguồn. |
| [British Council — Listening](https://learnenglish.britishcouncil.org/free-resources/listening) | Bổ sung audio người thật ở mức phù hợp; chọn A1/A2/B1/B2 theo năng lực thực tế. |
| [Cambridge — Activities](https://www.cambridgeenglish.org/learning-english/activities-for-learners/) | Hoạt động theo kỹ năng, mức độ và thời lượng; không phải ngân hàng TOEIC. |
| [IIG — Ôn luyện](https://toeic.iigvietnam.com/on-luyen/) | English Discoveries và TOEIC OLPC khi cần khóa có hướng dẫn/quyền truy cập phù hợp. Không mua tài khoản tự động. |

Danh sách kho code, giấy phép, lựa chọn tích hợp và giới hạn truy cập đã kiểm tra nằm trong [SOURCES.md](SOURCES.md). Nghiên cứu là khảo sát có chọn lọc các nguồn phù hợp, không tuyên bố kiểm kê hết mọi nền tảng trên Internet.

## Cách dùng trong sản phẩm

1. Mở **TOEIC cùng DHV → Lộ trình → Học theo buổi**. Chọn nhịp học và level; có thể mở buổi bất kỳ để ôn.
2. Học mục tiêu, kiến thức và ví dụ; làm hai câu tự kiểm tra trước khi mở giải thích. Có thể làm lại; điểm tự kiểm tra chỉ tồn tại trong buổi đang mở.
3. Mở bài hỗ trợ để làm bài được chấm bằng API hoặc mở tài nguyên bên ngoài theo điều kiện của nguồn.
4. Tự bấm **Đánh dấu đã học buổi này** khi hoàn thành công việc đã đề ra. Có thể bỏ đánh dấu. Tài khoản lưu trạng thái trên server; lựa chọn nhịp 2/3/4 buổi chỉ là bộ xem kế hoạch, chưa lưu như lịch học cá nhân.
5. **Thư viện 20 bài luyện**, từ vựng FSRS, khảo sát và đề 200 câu vẫn sử dụng tiến độ bài luyện đã có. Mark buổi không tặng điểm bài luyện, không tự tăng streak và không tạo chứng chỉ.
6. **Tải lộ trình (.md)** tải bản đủ 56 buổi, gồm cả đáp án tự kiểm tra và nguồn tham khảo.

## Dữ liệu đã đóng gói và giới hạn

| Nội dung | Trạng thái |
|---|---|
| 56 kế hoạch buổi, 112 ví dụ và 112 câu tự kiểm tra | Đã biên soạn và có trong ứng dụng; hỗ trợ AI, chưa được giáo viên kiểm định như đề chuẩn hóa. |
| 20 bài hỗ trợ, 268 câu chấm server, 200 thẻ FSRS | Giữ nguyên nội dung/ID để không mất tiến độ cũ. Một bài hỗ trợ có thể dùng cho nhiều buổi. |
| 65 WAV và 8 SVG | Giữ bộ audio tổng hợp/hình tự tạo hiện có; lần này không bổ sung một bộ audio mới cho từng buổi. |
| Nhiệm vụ “luyện 15/30 câu”, đề mới, nghe graphic | Khối lượng tự học đề xuất, thực hiện qua ngân hàng hỗ trợ và nguồn liên kết; không có nghĩa đã thêm từng ấy câu mới riêng cho mỗi buổi. |
| 900 TOEIC | Mục tiêu của người học, không suy từ dấu hoàn tất hoặc % đúng nội bộ. |

## Triển khai và bảo toàn tiến độ

- Nguồn biên soạn: `backend/scripts/toeic_curriculum.py`; builder ghép vào `course.json` và metadata xem thử. Bản Markdown được tạo từ cùng nguồn, hạn chế lệch giữa tài liệu và UI.
- `GET /api/toeic/catalog` bổ sung `curriculum`. Các API và ID bài luyện cũ giữ nguyên. Frontend còn hỗ trợ catalog cũ trong lúc backend đang triển khai.
- `PUT /api/toeic/curriculum/sessions/{id}` nhận `{ "completed": true/false }`, yêu cầu JWT cá nhân, kiểm tra ID buổi và boolean, giới hạn tần suất, cập nhật `$addToSet`/`$pull` theo user ID. Thử lại không nhân đôi buổi.
- `GET /api/toeic/progress` thêm `curriculum_completed`. Trường mới trong `toeic_profiles`; không cần seed hay migration xóa dữ liệu.
- Các đáp án trong `curriculum.checks` là học liệu tự kiểm tra công khai trong tài khoản. Chúng tách biệt với ngân hàng câu hỏi có chấm điểm; đáp án bài đang làm vẫn chỉ mở sau nộp.
- Preview cho đọc và tự kiểm tra tại chỗ; không gọi API ghi tiến độ hay tạo lượt làm bài.

## Kiểm chứng

Kiểm thử gồm đủ 24/12/12/8 buổi, tổng thời lượng, tham chiếu nguồn/bài, tính hợp lệ câu tự kiểm tra, UI chọn level/nhịp học, reset bài tự kiểm tra, trở về đúng buổi từ bài hỗ trợ, lưu lỗi và tương thích catalog cũ. Integration kiểm tra JWT, tách tài khoản, thử lại idempotent, ghi đồng thời và bảo toàn mục tiêu/điểm cũ. Kiểm tra ảnh giao diện trên desktop/mobile trước bàn giao; kết quả chạy cụ thể được ghi trong báo cáo triển khai của ngày.
