# Nguồn nghiên cứu cho TOEIC cùng DHV

## Mở rộng ôn tập và kho từ mở v4 · 27/10/2026

Bản v4 (`dhv-toeic-2026.10-v4`) đã đối chiếu toàn bộ **1.107 câu** trong 12 gói dữ liệu của [TOEIC Question Ocean](https://github.com/kdeppaei/toeic-question-ocean) ở revision `a940bb8b479ef4d06af468015d757041c3d2e457` theo [MIT](https://github.com/kdeppaei/toeic-question-ocean/blob/a940bb8b479ef4d06af468015d757041c3d2e457/LICENSE): đưa vào sử dụng **1.048 câu** có lời giải tiếng Việt (399 câu ở v3 + 649 câu bổ sung ở v4), loại **59 câu** không đạt yêu cầu, giữ **20 cảnh AI theo MIT** và **5 ảnh chụp theo Pexels License** (ghi nguồn tác giả riêng). Thêm 60 câu DHV, 38 hướng dẫn dạng bài, **9 mã đề cố định** (gồm **3 đề toàn phần 200 câu không trùng ID**) và sổ câu sai.

Sau khi kiểm tra các nguồn đề xuất (`seikaikyo/toeic-practice`, `thu-tram/awesome-toeic`, `riiid/ednet`, `ETS Official Samples`), dự án **không nhập** mã nguồn hay câu hỏi độc quyền của `seikaikyo/toeic-practice` và không biến dữ liệu hành vi `EdNet` (`CC BY-NC 4.0`) thành câu hỏi thi; thay vào đó tích hợp trực tiếp **4.060 từ** từ [NGSL 1.2](https://www.newgeneralservicelist.com/new-general-service-list) và [TOEIC Service List 1.2](https://www.newgeneralservicelist.com/toeic-service-list) theo **CC BY-SA 4.0**, đồng thời bổ sung các liên kết tham khảo chính thức vào mục **Nguồn học**. [Báo cáo nguồn, phần loại bỏ, các điều chỉnh và nơi lưu dữ liệu](MO_RONG_ON_TAP.md) mô tả phạm vi hiện tại.

Đã đối chiếu [IIBC format](https://www.iibc-global.org/english/toeic/test/lr/about/format.html), [ETS preparation](https://www.ets.org/toeic/test-takers/prepare.html), [British Council B1–B2](https://learnenglish.britishcouncil.org/free-resources/grammar/b1-b2), [Moodle quiz](https://docs.moodle.org/503/en/Building_Quiz) và [H5P Question Set](https://h5p.org/tutorial-question-set). Moodle/H5P là tham khảo thiết kế, không nhập code. Những nguồn dẫn link không tự động được coi là nguồn cho phép phân phối lại.

Các phần dưới là **lịch sử nghiên cứu của v1/v2**. Các câu “không nhập học liệu/media” trong lịch sử mô tả phiên bản cũ; phạm vi v4 ở trên và CONTENT_LICENSES.md là thông tin hiện hành.

## Bổ sung nghiên cứu cho lộ trình 56 buổi

Đối chiếu lại ngày 27/10/2026 bằng trang nhà cung cấp, README và file cấp phép trên GitHub. Đây là khảo sát **có chọn lọc**, không phải tuyên bố đã đọc hết mọi repository/nền tảng. [Bản thiết kế](THIET_KE_CHUONG_TRINH.md) giải thích cách giữ 24/12 buổi gốc và bổ sung 12/8 buổi nâng cao; [bản chi tiết](LO_TRINH_CHI_TIET.md) chứa toàn bộ buổi, ví dụ và tự kiểm tra.

| Repository được kiểm tra | Giấy phép/ghi nhận tại thời điểm đọc | Áp dụng vào DHV |
|---|---|---|
| [py-fsrs](https://github.com/open-spaced-repetition/py-fsrs) | [MIT](https://github.com/open-spaced-repetition/py-fsrs/blob/main/LICENSE). | Giữ thư viện lên lịch ôn đã tích hợp; không thay thuật toán hoặc nâng dependency trong lần này. |
| [Moodle](https://github.com/moodle/moodle) | [GPL-3.0](https://github.com/moodle/moodle/blob/main/COPYING.txt). | Tham khảo cách tổ chức khóa/hoạt động và tách tiến độ học; không đưa thêm LMS hay chép code. |
| [H5P Interactive Book](https://github.com/h5p/h5p-interactive-book) | [MIT](https://github.com/h5p/h5p-interactive-book/blob/master/LICENSE); component dùng H5P framework. | Tham khảo bố cục nội dung kết hợp tự kiểm tra; tự triển khai component React theo hệ thống sẵn có. |
| [LibreLingo](https://github.com/kantord/LibreLingo) | [AGPL-3.0](https://github.com/kantord/LibreLingo/blob/main/LICENSE); README báo chưa được duy trì và nội dung khóa có thể dùng giấy phép riêng. | Tham khảo nội dung tách khỏi giao diện; không dùng làm dependency vận hành, không nhập học liệu. |
| [Anki](https://github.com/ankitects/anki) | [LICENSE](https://github.com/ankitects/anki/blob/main/LICENSE) ghi AGPL v3 hoặc mới hơn, có các phần dùng giấy phép khác; không chỉ dựa vào giá trị `NOASSERTION` của API. | Tham khảo học bằng truy hồi và lịch ôn; không nhập shared decks không rõ nguồn. |
| [HungTabe/TOEIC_VLearningApp](https://github.com/HungTabe/TOEIC_VLearningApp) | README ghi MIT nhưng API vẫn không tìm được file license riêng. | Giữ mức tham khảo ý tưởng từ vựng theo chủ đề; không sao chép code/database. |
| [toeic-question-ocean](https://github.com/kdeppaei/toeic-question-ocean) | [MIT](https://github.com/kdeppaei/toeic-question-ocean/blob/main/LICENSE); dự án có thông tin attribution cho tài nguyên riêng. | Tham khảo cách công bố nguồn; không coi license code là quyền nhập toàn bộ học liệu. Không nhập đề hoặc media. |
| [seikaikyo/toeic-practice](https://github.com/seikaikyo/toeic-practice) | [LICENSE](https://github.com/seikaikyo/toeic-practice/blob/main/LICENSE) ghi proprietary, không cấp quyền dùng code. Repo công khai không đồng nghĩa mã nguồn mở. | Loại khỏi phương án tái sử dụng code; không clone hay tích hợp. |

Vì EduFace đã có React, FastAPI, JWT và FSRS, lựa chọn triển khai là thêm lớp **buổi học → bài hỗ trợ → nguồn học → mốc đánh giá** vào ứng dụng hiện có. Lần này không nhập thêm dependency từ các repo trên; nội dung và code mới được viết trực tiếp cho dự án.

Nguồn kiến thức được mở/đối chiếu gồm [ETS](https://www.ets.org/toeic/test-takers/prepare.html), [IIBC format](https://www.iibc-global.org/english/toeic/test/lr/about/format.html), [British Council grammar reference](https://learnenglish.britishcouncil.org/free-resources/grammar/english-grammar-reference), [A1–A2](https://learnenglish.britishcouncil.org/free-resources/grammar/a1-a2), [B1–B2](https://learnenglish.britishcouncil.org/free-resources/grammar/b1-b2), [relative clauses](https://learnenglish.britishcouncil.org/free-resources/grammar/b1-b2/relative-clauses-defining-relative-clauses), [participle clauses](https://learnenglish.britishcouncil.org/free-resources/grammar/c1/participle-clauses), [A2 listening](https://learnenglish.britishcouncil.org/free-resources/listening/a2), [B1 listening](https://learnenglish.britishcouncil.org/free-resources/listening/b1), [Cambridge activities](https://www.cambridgeenglish.org/learning-english/activities-for-learners/) và [IIG ôn luyện](https://toeic.iigvietnam.com/on-luyen/). Nội dung bài và ví dụ trong DHV là biên soạn mới dựa trên kiến thức ngôn ngữ, không chép các bài tập ở những trang này.

[Tatoeba](https://en.wiki.tatoeba.org/articles/show/using-the-tatoeba-corpus) có thể hữu ích cho ví dụ câu ở lần mở rộng sau, nhưng quyền văn bản và audio không giống nhau; cần lưu attribution và giấy phép từng tài nguyên nếu nhập. Lần này không nhập dữ liệu Tatoeba. Công cụ đọc web gặp timeout với trang B2 listening và HTTP 403 tại Cambridge Dictionary; các liên kết vẫn là nguồn chính thức để người học mở trực tiếp, không tuyên bố đã kiểm tra mọi bài tập bên trong.

Các tiêu chí 70/75/80%, mốc 350–900, nhịp 2/3/4 buổi và lịch ôn 1/3/7 ngày là thiết kế nội bộ của DHV. Chúng không được trình bày như quy định ETS hay cam kết đầu ra của British Council/Cambridge/IIG.

## Nghiên cứu nền của ngân hàng bài luyện

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
