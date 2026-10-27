# Nguồn gốc và thông báo thành phần TOEIC

## Code và nội dung mới

Lộ trình 56 buổi và 112 câu tự kiểm tra được biên soạn tại `backend/scripts/toeic_curriculum.py`. Bản v4 (`dhv-toeic-2026.10-v4`) có **1.376 câu chấm điểm**: 268 câu DHV ban đầu, 60 câu DHV mới và 1.048 câu chuyển thể từ TOEIC Question Ocean được cấp MIT (từ tổng 1.107 câu nguồn đã đối chiếu; loại 59 câu không đạt yêu cầu). 38 hướng dẫn dạng bài, ví dụ và lời giải tiếng Việt được biên soạn cho DHV bằng hỗ trợ AI; chưa được thẩm định bởi giáo viên độc lập. Câu tự kiểm tra và ví dụ không cộng vào ngân hàng chấm điểm.

Code frontend/backend và script biên soạn TOEIC được viết trực tiếp cho repository này. Điều khoản của dự án tại `LICENSE` vẫn được giữ nguyên; lần nâng cấp không thay giấy phép toàn repository hay xác lập quyền đối với tài liệu của bên thứ ba.

`backend/data/toeic/course.json`, `backend/data/toeic/lexicon.json` và bản metadata xem thử được tạo từ các script `backend/scripts/*toeic*.py`. Phân biệt rõ nội dung DHV, phần MIT từ Question Ocean, ảnh Pexels và bộ từ CC BY-SA 4.0. Bộ nội dung chưa được kiểm định tương đương đề thi chuẩn hóa; không dùng nhãn “ETS official questions” hoặc “cam kết 900”.

8 SVG trong `frontend/public/toeic/images` là hình minh họa tự vẽ bằng mã. 25 JPG từ TOEIC Question Ocean gồm **20 cảnh tự tạo bằng AI theo MIT** và **5 ảnh chụp theo Pexels License** (ghi rõ tác giả và giấy phép riêng, không gán nhãn MIT hay AI cho ảnh Pexels). 268 WAV trong `frontend/public/toeic/audio` được tổng hợp từ transcript DHV hoặc transcript MIT đã chuyển thể; không nhập audio người thật hoặc audio ETS. Script dùng API giọng đọc có sẵn của Windows, không phân phối bản cài hay mô hình giọng của Microsoft. Khi thay công cụ/giọng, kiểm tra điều khoản tương ứng của công cụ đang dùng.

## TOEIC Question Ocean · MIT & Pexels License

- Nguồn: [kdeppaei/toeic-question-ocean](https://github.com/kdeppaei/toeic-question-ocean).
- Copyright (c) 2026 Chun-Hsiung Luo. Giấy phép văn bản câu hỏi tại [commit nhập dữ liệu](https://github.com/kdeppaei/toeic-question-ocean/blob/a940bb8b479ef4d06af468015d757041c3d2e457/LICENSE).
- Giữ nguyên thông báo tại [bản backend](../../backend/data/toeic/vendor/OCEAN-MIT-LICENSE.txt) và [bản phân phối frontend](../../frontend/public/toeic/licenses/OCEAN-MIT-LICENSE.txt).
- Đã kiểm tra toàn bộ 12 gói dữ liệu trong `index.html` ở revision ghim cố định (`1.107` câu): nhập **1.048 câu** sau rà soát (399 câu ở v3 + 649 câu ở v4), loại **59 câu** (15 câu ứng viên có vấn đề + 44 câu Part 6 cũ chỉ là các câu đơn lẻ ghép chung group ID).
- Thay giải thích bằng tiếng Việt, bổ sung nhãn chuyên đề, đảo lựa chọn ổn định và tạo audio mới. Các chỉnh sửa câu dẫn/lựa chọn/đoạn văn để khử đa nghĩa hoặc khôi phục chỗ trống bị in lộ đáp án trong nguồn được ghi đầy đủ tại `course.json:expansion.adaptations`, `additional_edits` và `context_edits`.
- [Ghi nguồn 25 ảnh và SHA-256](../../frontend/public/toeic/licenses/OCEAN-ATTRIBUTION.md), tách rõ 20 cảnh AI (MIT) và 5 ảnh Pexels ([Pexels License](https://www.pexels.com/license/)).
- Mỗi câu có `provenance` gồm provider, upstream ID, revision, URL, license và thông tin nguồn ảnh; snapshot đầy đủ lưu ở `backend/data/toeic/vendor/ocean-complete-snapshot.json`.

Xem [phạm vi, kiểm tra và cách tái tạo](MO_RONG_ON_TAP.md). MIT của phần được nhập không thay thế giấy phép của toàn bộ EduFace hoặc quyền đối với các tài liệu bên ngoài được dẫn link.

## Từ điển Anh–Việt 191.864 mục từ · CC BY-SA 4.0 & các giấy phép thành phần

- Thông báo đầy đủ và công bố thay đổi: [DICTIONARY.md](../../frontend/public/toeic/licenses/DICTIONARY.md). Tác giả, revision, URL và SHA-256 nằm trong [dictionary-meta.json](../../backend/data/toeic/dictionary-meta.json).
- Giữ ghi nhận NGSL 1.2 (Charles Browne, Brent Culligan, Joseph Phillips) và TSL 1.2 (Charles Browne, Brent Culligan), CC BY-SA 4.0; thứ hạng từ và các định nghĩa DHV bổ sung vẫn được đánh dấu.
- Dữ liệu từ điển: [Từ điển Anh–Việt thichhoc.com (thichhoc-dict)](https://github.com/thichhoc-org/thichhoc-dict), giấy phép CC BY-SA 4.0. Nguồn gốc: WordNet 3.1 (Princeton), CMUdict (CMU), Wiktionary. **Đã chỉnh sửa dữ liệu.** Giữ mục từ ghi nguồn `thichhoc` và [THICHHOC-LICENSE-DATA.md](../../frontend/public/toeic/licenses/THICHHOC-LICENSE-DATA.md).
- Nghĩa, từ loại, dạng từ và ví dụ song ngữ được mở rộng từ cộng đồng [Wiktionary tiếng Việt](https://vi.wiktionary.org/) qua [Kaikki/Wiktextract](https://kaikki.org/dictionary/rawdata.html), CC BY-SA 4.0. Có URL nguồn theo từng mục để xem người đóng góp/lịch sử.
- Phiên âm có nguồn từ ipa-dict (MIT), CMUdict (BSD 2-clause), Wiktionary và phần biên soạn DHV. Giữ [IPA-MIT-LICENSE.txt](../../frontend/public/toeic/licenses/IPA-MIT-LICENSE.txt) và các thông báo đi kèm. Không gán 100% kho có IPA hoặc toàn bộ IPA thuộc giọng Mỹ.
- Phần DHV bổ sung/chỉnh nghĩa và ví dụ chia sẻ theo CC BY-SA 4.0. Nhãn `edited`, `community`, `machine` phân biệt nguồn nghĩa. Nguồn thichhoc công bố bản dịch máy chưa được con người duyệt; không trình bày dữ liệu này như bản dịch đã được thẩm định.
- Bản đầy đủ tại `backend/data/toeic/dictionary.sqlite3.gz` và `/toeic/dictionary/dictionary.json.gz`; 259.107 nghĩa, 24.576 ví dụ song ngữ, 84.898 mục có IPA. Dữ liệu `lexicon.json`/`lexicon_100k.json.gz` là đầu vào lịch sử để bảo toàn 147.245 ID cũ, không phải kho tra cứu hiện hành.

## py-fsrs 6.3.2

- Nhà phát triển: Open Spaced Repetition.
- Nguồn: https://github.com/open-spaced-repetition/py-fsrs
- Giấy phép: MIT.
- Bản thông báo đi kèm gói cài đã được giữ nguyên tại [FSRS-MIT-LICENSE.txt](FSRS-MIT-LICENSE.txt).
- Phạm vi sử dụng: lên lịch ôn từ trên backend cho cả 200 thẻ tiếng Việt DHV và 191.864 mục từ của từ điển song ngữ; `desired_retention=0.9`, tắt fuzzing để lịch có thể kiểm thử nhất quán. Đây không phải tỷ lệ ghi nhớ được bảo đảm cho từng người học.

## Tài nguyên dẫn link và các nguồn không nhập

ETS, IIG, British Council, Cambridge và các repository nghiên cứu giữ quyền đối với tài nguyên của họ. DHV dẫn tới trang gốc; không nhúng khóa trả phí, không sao chép đề/audio và không tuyên bố đại diện hay được các tổ chức đó chứng nhận.

- `seikaikyo/toeic-practice`: mã nguồn ứng dụng và ngân hàng câu hỏi giữ bản quyền độc quyền (`All Rights Reserved` trong `LICENSE` và `NOTICE`), chỉ dữ liệu từ vựng đi kèm có giấy phép mở riêng. DHV **không** nhập code hay câu hỏi từ repository này; bộ từ NGSL/TSL được lấy trực tiếp từ trang công bố của tác giả.
- `thu-tram/awesome-toeic`: danh mục liên kết tài nguyên luyện TOEIC, được dẫn link tham khảo trong tab Nguồn học; không phải kho câu hỏi được cấp phép tái phân phối.
- `riiid/ednet`: bộ dữ liệu tương tác học tập theo `CC BY-NC 4.0` (phi thương mại, phục vụ nghiên cứu AI/ML, không chứa trọn vẹn văn bản câu hỏi/audio để làm đề thi), chỉ được ghi nhận ở mục Nguồn học tham khảo.
- Không sử dụng code hoặc dữ liệu của `HungTabe/TOEIC_VLearningApp`, Moodle hay ts-fsrs trong bản triển khai này.
