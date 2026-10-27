"""Build the original DHV learning pack. No scraped exercises or third-party answer banks.

The educational text is authored for this project. Deterministic IDs allow progress
to survive rebuilds. Review factual/pedagogical changes before increasing version.
"""
import json
import hashlib
from pathlib import Path
from toeic_curriculum import curriculum, guide_markdown

ROOT = Path(__file__).resolve().parents[2]
DATA = {"version": "dhv-toeic-2026.10-v1", "notice": "Học liệu tự biên soạn, không phải đề ETS. Mục tiêu 900 là định hướng học, không bảo đảm kết quả. ‘Từ 0’ nghĩa là bắt đầu từ nền tảng; điểm TOEIC L&R chính thức là 10–990. Âm thanh là giọng tổng hợp; Part 1 dùng hình minh họa.", "stages": [
    {"id": 0, "title": "Bắt đầu từ nền tảng", "range": "Nền tảng → 250", "focus": "Âm, từ loại, cấu trúc câu và thông tin ngắn", "weeks": "4–8 tuần gợi ý"},
    {"id": 1, "title": "Xây nền vững", "range": "250 → 450", "focus": "Mô tả hình, câu hỏi thường gặp, thì và email", "weeks": "4–6 tuần gợi ý"},
    {"id": 2, "title": "Kết nối ý nghĩa", "range": "450 → 650", "focus": "Paraphrase, hội thoại, bị động và đoạn văn", "weeks": "4–6 tuần gợi ý"},
    {"id": 3, "title": "Đọc sâu · nghe chắc", "range": "650 → 800", "focus": "Suy luận, mục đích người nói, từ vựng ngữ cảnh", "weeks": "4–8 tuần gợi ý"},
    {"id": 4, "title": "Hướng đến 900", "range": "800 → 900", "focus": "Nối nhiều văn bản, ý ngầm, độ chính xác và tốc độ", "weeks": "6–10 tuần gợi ý"}],
    "sources": [
        {"id": "ets", "title": "ETS · Preparation materials", "url": "https://www.ets.org/toeic/test-takers/prepare.html", "provider": "ETS", "access": "Mẫu miễn phí / khóa học có phí", "stage": "Mọi chặng", "usage": "Dẫn link chính thức; không tái phân phối đề hoặc audio ETS."},
        {"id": "iig", "title": "IIG · English Discoveries & TOEIC OLPC", "url": "https://toeic.iigvietnam.com/on-luyen/", "provider": "IIG Việt Nam", "access": "Có phí; xem giá tại nhà cung cấp", "stage": "Nền tảng đến luyện thi", "usage": "Tham khảo khóa học chính thống. Không mua hay tích hợp tài khoản trả phí tự động."},
        {"id": "iig-academy", "title": "IIG Academy · Các chương trình đào tạo", "url": "https://iigacademy.edu.vn/", "provider": "IIG Academy", "access": "Khóa đào tạo có phí", "stage": "Theo đánh giá đầu vào", "usage": "Liên hệ nhà cung cấp để chọn lớp; không cam kết đầu ra thay họ."},
        {"id": "bc-grammar", "title": "British Council · A1–A2 grammar", "url": "https://learnenglish.britishcouncil.org/free-resources/grammar/a1-a2", "provider": "British Council", "access": "Bài học công khai", "stage": "Nền tảng / 250–450", "usage": "Học bổ trợ trên trang gốc; nội dung không được chép vào ứng dụng."},
        {"id": "bc-listening", "title": "British Council · A1 listening", "url": "https://learnenglish.britishcouncil.org/free-resources/listening/a1", "provider": "British Council", "access": "Bài học công khai", "stage": "Nền tảng", "usage": "Bổ sung giọng người thật. Học trên trang của nhà cung cấp."},
        {"id": "cambridge", "title": "Cambridge English · Learning activities", "url": "https://www.cambridgeenglish.org/learning-english/activities-for-learners/", "provider": "Cambridge English", "access": "Hoạt động miễn phí", "stage": "Lọc theo trình độ", "usage": "Luyện kỹ năng tiếng Anh tổng quát, không phải ngân hàng TOEIC."},
        {"id": "format", "title": "IIBC · Cấu trúc TOEIC L&R", "url": "https://www.iibc-global.org/english/toeic/test/lr/about/format.html", "provider": "IIBC", "access": "Thông tin chính thức", "stage": "Làm quen bài thi", "usage": "200 câu, nghe khoảng 45 phút và đọc 75 phút; xem nguồn khi có thay đổi."},
        {"id": "fsrs", "title": "Py-FSRS · Lịch ôn cách quãng", "url": "https://github.com/open-spaced-repetition/py-fsrs", "provider": "Open Spaced Repetition", "access": "Mã nguồn MIT", "stage": "Ôn từ mỗi ngày", "usage": "Thư viện được tích hợp ở server để lên lịch ôn riêng từng người."}],
    "lessons": [], "questions": [], "vocabulary": []}


def lesson(lid, stage, title, part, objectives, rules, examples, strategy):
    DATA["lessons"].append({"id": lid, "stage": stage, "title": title, "part": part,
        "minutes": 25 if stage < 2 else 35, "objectives": objectives,
        "sections": [{"title": "Hiểu bản chất", "body": rules},
                     {"title": "Ví dụ có phân tích", "body": examples},
                     {"title": "Cách luyện hôm nay", "body": strategy}],
        "practice_rule": "Đọc bài → ôn từ → làm bài không xem lời giải → ghi lại lý do sai. Từ 70% được đánh dấu hoàn thành; có thể luyện lại mọi lúc."})


def vocab(lid, rows):
    for i, row in enumerate(rows.strip().splitlines(), 1):
        term, meaning, example = row.split("|", 2)
        DATA["vocabulary"].append({"id": f"{lid}-v{i:02}", "lesson_id": lid,
            "term": term, "meaning": meaning, "example": example.strip()})


def question(lid, part, prompt, options, explanation, correct=0, **extra):
    number = sum(q["lesson_id"] == lid for q in DATA["questions"]) + 1
    # Stable per-question placement without a predictable A/B/C cycle.
    rotation = hashlib.sha256(f"{lid}:{number}".encode()).digest()[0] % len(options)
    rotated = options[rotation:] + options[:rotation]
    row = {"id": f"{lid}-q{number:02}", "lesson_id": lid, "part": part,
           "prompt": prompt, "options": rotated, "correct": (correct - rotation) % len(options),
           "explanation": explanation, **extra}
    DATA["questions"].append(row)
    return row


lesson("f01", 0, "Nghe số, giờ và từ để hỏi", 2,
 ["Phân biệt thirteen/thirty và các mốc giờ", "Xác định câu hỏi hỏi ai, ở đâu hay khi nào"],
 "Nghe từ để hỏi trước khi cố hiểu mọi từ. Who hỏi người, where hỏi nơi chốn, when hỏi thời điểm; how long hỏi khoảng thời gian. Mười ba (thirteen) thường nhấn âm cuối, ba mươi (thirty) nhấn âm đầu. Nghe thêm danh từ đi sau để hiểu số tiền, số lượng hay giờ.",
 "When does the meeting start? — At half past nine. Half past nine là 9:30.\nHow long is the tour? — About two hours. Đây là khoảng thời gian, không phải một giờ trên đồng hồ.\nWho handles invoices? — Mina in accounting. Phòng kế toán là ngữ cảnh; Mina mới là người được hỏi.",
 "Nghe lần 1 và chọn ý chính. Nghe lần 2 để ghi số hoặc cụm từ khóa. Sau khi nộp mới mở transcript, gạch chân thông tin quyết định. Đọc theo từng cụm 3–5 từ, không đọc từng chữ.")
lesson("f02", 0, "Dựng câu: chủ ngữ, động từ, từ loại", 5,
 ["Nhìn ra động từ chính của câu", "Chọn danh từ, tính từ, trạng từ theo vị trí"],
 "Một câu đơn thường có chủ ngữ + động từ + phần bổ sung. Danh từ làm chủ ngữ/tân ngữ; tính từ bổ nghĩa danh từ; trạng từ bổ nghĩa động từ hoặc tính từ. Sau a/an/the thường cần một cụm danh từ. Sau can/must/should dùng động từ nguyên mẫu không to.",
 "The assistant checks the schedule. Assistant là chủ ngữ, checks là động từ.\nPlease read the instructions carefully. Carefully mô tả cách đọc nên là trạng từ.\nThe report is accurate. Sau be có thể là tính từ chỉ đặc điểm.",
 "Trước khi nhìn đáp án, ghi loại từ cần điền. Loại các đáp án sai chức năng rồi mới kiểm tra nghĩa. Không chọn chỉ vì nhìn thấy hậu tố quen thuộc: position và ngữ cảnh quyết định.")
lesson("f03", 0, "Từ vựng văn phòng và cụm từ tự nhiên", 5,
 ["Nhận biết các vật dụng và việc văn phòng", "Học cụm từ thay vì dịch từng từ"],
 "Collocation là những từ thường đi cùng nhau: make an appointment, meet a deadline, attend a meeting. Một từ có thể có nhiều nghĩa: file có thể là hồ sơ hoặc động từ lưu hồ sơ. Hãy đọc cả câu để xác định vai trò và nghĩa.",
 "Please attach the receipt to your claim. Attach là đính kèm; receipt là biên lai.\nWe need to meet the deadline. Không dịch meet thành gặp người trong cụm này.\nThe printer is out of paper. Out of nghĩa là hết, không phải ở ngoài.",
 "Mỗi thẻ học theo ba bước: đọc từ, tự nhớ nghĩa, rồi đặt câu tương tự với công việc của mình. Chỉ bấm Dễ khi nhớ được cả nghĩa lẫn cách dùng; quên thì chọn Học lại để FSRS lên lịch gần hơn.")
lesson("f04", 0, "Đọc biển báo và tin nhắn ngắn", 7,
 ["Tìm người nhận, hành động và thời hạn", "Phân biệt thông tin có trong bài với suy đoán"],
 "Đọc tiêu đề và các từ khóa như closed, until, before, available trước. Câu hỏi What/When/Where thường cần một chi tiết rõ ràng. Before Friday không tự động đồng nghĩa on Friday. Khi thông tin không được nêu, đừng chọn một đáp án chỉ vì nó có vẻ hợp lý.",
 "Closed for repairs until Monday: cửa hàng chưa mở trong thời gian sửa chữa, không phải đóng cửa vĩnh viễn.\nBring your employee ID: yêu cầu mang thẻ nhân viên, không phải danh thiếp.\nCall before visiting: cần gọi trước, không có nghĩa chỉ được liên hệ bằng điện thoại.",
 "Giới hạn 45–60 giây cho một tin ngắn. Gạch chân một câu bằng chứng cho đáp án. Sau bài, viết lại thông báo bằng một câu tiếng Việt để kiểm tra mình hiểu đúng yêu cầu.")
lesson("b01", 1, "Part 1 · Hành động và vị trí trong hình", 1,
 ["Phân biệt hành động đang diễn ra và trạng thái", "Dùng giới từ vị trí chính xác"],
 "Với người, chú ý động từ đang diễn ra: is carrying, is typing. Với đồ vật, phân biệt trạng thái với hành động: are stacked khác are being stacked. Kiểm tra chủ thể, động từ và vị trí; chỉ một chi tiết sai cũng đủ loại đáp án. Bài này dùng hình minh họa tự tạo để luyện mô tả, không phải ảnh đề thi.",
 "A woman is carrying a box: có người đang mang hộp.\nChairs are arranged around a table: mô tả cách xếp ghế, không nói ai đang xếp.\nA bicycle is leaning against a wall: xe đạp tựa vào tường, không phải nằm dưới bàn.",
 "Nhìn hình 5 giây và tự nói một câu trước khi nghe. Sau khi nộp, so sánh động từ và giới từ ở từng lựa chọn. Với đề thật, tiếp tục luyện trên ảnh và audio mẫu ở nguồn ETS.")
lesson("b02", 1, "Part 2 · Yêu cầu, đề nghị và câu hỏi lựa chọn", 2,
 ["Trả lời đúng chức năng giao tiếp", "Không mắc bẫy từ lặp và âm gần giống"],
 "Could you…? thường là lời nhờ, nên câu trả lời có thể nhận lời hoặc giải thích vì sao chưa làm được. Would you like…? là đề nghị. Câu hỏi A or B có thể được trả lời bằng Neither/Either hoặc một lựa chọn. Đáp án đúng không nhất thiết lặp từ khóa trong câu hỏi.",
 "Could you print this? — Certainly, how many copies?\nWould you prefer tea or coffee? — Tea, please.\nWhy is the room locked? — The cleaning team is still inside. Câu trả lời là lý do chứ không phải Yes/No.",
 "Tự phân loại từng câu thành hỏi thông tin / nhờ / đề nghị / lựa chọn. Nếu sai vì nghe âm, nghe lại cả cụm. Nếu sai vì nghĩa, viết một câu đáp tương đương bằng từ khác.")
lesson("b03", 1, "Thì, hòa hợp chủ vị và dấu hiệu thời gian", 5,
 ["Chọn thì từ mốc thời gian", "Nhận ra chủ ngữ thật giữa các cụm bổ nghĩa"],
 "Hiện tại đơn diễn tả thói quen; quá khứ đơn gắn với mốc đã kết thúc; hiện tại hoàn thành nối quá khứ với hiện tại. Since đi với mốc bắt đầu, for đi với khoảng thời gian. Đừng để danh từ gần động từ trong cụm of/with đánh lạc hướng hòa hợp chủ vị.",
 "The list of suppliers is on my desk. Chủ ngữ là list, không phải suppliers.\nWe shipped the order yesterday. Yesterday là mốc đã kết thúc.\nShe has worked here since 2022. Trạng thái bắt đầu trước và vẫn còn hiện nay.",
 "Khoanh chủ ngữ và gạch chân mốc thời gian trước. Giải thích vì sao ba dạng còn lại không phù hợp. Khi gặp hiện tại hoàn thành và quá khứ đơn, hỏi: mốc thời gian có đóng lại không?")
lesson("b04", 1, "Email: mục đích, người nhận và việc cần làm", 7,
 ["Đọc nhanh subject, opening và closing", "Nhận ra yêu cầu được diễn đạt gián tiếp"],
 "Email thường có mục đích chính: xác nhận, yêu cầu, xin lỗi, thông báo hoặc mời. Subject gợi chủ đề nhưng câu hành động mới cho biết người nhận phải làm gì. Please let me know by… yêu cầu phản hồi trước hạn. Thank you for… thường nhắc một việc đã xảy ra.",
 "Could you send the revised quote? là yêu cầu báo giá đã sửa, không phải hóa đơn.\nWe have received your application xác nhận nhận hồ sơ, chưa phải tuyển dụng.\nPlease ignore the earlier schedule: lịch cũ bị thay thế.",
 "Đọc câu hỏi trước, tìm bằng chứng trong email, rồi đối chiếu paraphrase. Luôn kiểm tra thì: has been sent khác will be sent. Không tự suy ra một cuộc hẹn đã được xác nhận nếu email chỉ đề xuất.")
lesson("i01", 2, "Part 2 · Câu đáp gián tiếp và ý ngầm", 2,
 ["Hiểu câu trả lời không dùng yes/no", "Theo dõi thay đổi kế hoạch và trách nhiệm"],
 "Câu đáp gián tiếp vẫn giải quyết mục đích câu hỏi: Do you have the key? — Try the front desk. Đáp án này gợi nơi lấy chìa khóa. Trong câu hỏi phủ định và tag question, đừng chỉ đếm yes/no; phải hiểu mệnh đề mà người nói xác nhận.",
 "Can we use the large room? — It's booked until noon. Hàm ý chưa dùng được trước trưa.\nWho is driving? — I haven't brought my car. Hàm ý người này không lái.\nHas the courier arrived? — There's a parcel at reception. Có bằng chứng gián tiếp việc giao hàng.",
 "Với mỗi lựa chọn, hỏi: câu này giúp giải quyết việc người hỏi đang cần không? Tránh chọn chỉ vì có từ cùng chủ đề. Sau bài, viết nghĩa hàm ý bằng tiếng Việt rồi diễn đạt lại bằng một câu ngắn tiếng Anh.")
lesson("i02", 2, "Part 3 · Theo dõi hội thoại công việc", 3,
 ["Xác định vấn đề, giải pháp và bước tiếp theo", "Phân biệt người nói và thông tin được sửa lại"],
 "Một hội thoại có thể đổi hướng: đề xuất đầu tiên bị từ chối, giải pháp sau mới là kết luận. Đọc ba câu hỏi trước để biết cần nghe địa điểm, lý do hay hành động. Giữ mốc tên người và vai trò; thông tin cuối thường chốt trách nhiệm.",
 "We could meet at nine. — I have a call then. How about ten? Cuộc gặp chuyển sang 10 giờ.\nI'll ask the technician: người nói hứa liên hệ kỹ thuật viên, chưa hứa sửa được ngay.\nBecause the supplier is late nêu nguyên nhân, không phải đề xuất.",
 "Nghe một lượt không dừng, trả lời cả nhóm câu hỏi rồi mới nghe lại. Vẽ chuỗi vấn đề → giải pháp → ai làm gì. Các câu trong cùng hội thoại phải dựa trên cùng đoạn, không cộng thông tin từ hội thoại khác.")
lesson("i03", 2, "Bị động, mệnh đề quan hệ và liên từ", 5,
 ["Nhận ra đối tượng nhận hành động", "Phân biệt liên từ và giới từ theo cấu trúc"],
 "Bị động dùng be + quá khứ phân từ khi chủ ngữ nhận hành động. Which/that thay vật, who thay người, whose chỉ sở hữu. Because đi với mệnh đề; because of đi với cụm danh từ. Although và despite cùng diễn tả tương phản nhưng không dùng cùng cấu trúc.",
 "The forms must be signed today: mẫu đơn được ký.\nThe designer who joined yesterday is in Room 2: who làm chủ ngữ mệnh đề quan hệ.\nDespite the rain, the tour continued; although it rained, the tour continued.",
 "Đánh dấu chỗ trống cần một mệnh đề hay cụm danh từ. Với bị động, tìm người/vật thực hiện hành động nếu có by. Không cứ thấy by là chọn bị động: by Friday có thể chỉ thời hạn.")
lesson("i04", 2, "Part 6 · Mạch đoạn văn và câu nối", 6,
 ["Giải chỗ trống bằng cả ngữ pháp lẫn ngữ cảnh", "Dùng từ chỉ ngược để chọn câu nối"],
 "Trong Part 6, câu kế tiếp có thể quyết định đáp án câu trước. This change, these items, therefore và however cần một ý được nhắc phù hợp. Đọc lướt toàn đoạn để xác định văn phong và thời gian trước khi điền. Một câu đúng ngữ pháp vẫn có thể sai mạch ý.",
 "The entrance will move to the east side. Signs will direct visitors there. There chỉ east side.\nDemand has risen. Therefore, we will extend opening hours. Therefore nối kết quả.\nThe service is free. However, registration is required: điều kiện bổ sung trái với kỳ vọng miễn phí là không cần thủ tục.",
 "Làm cả bốn câu trong một đoạn. Sau khi điền, đọc lại đoạn liền mạch; kiểm tra đại từ và từ nối có đối tượng tham chiếu rõ không. Giữ khoảng 30–45 giây cho câu ngữ pháp, thêm thời gian cho câu chèn.")
lesson("u01", 3, "Part 3 · Suy luận có bằng chứng", 3,
 ["Hiểu lời đề nghị gián tiếp", "Suy luận đúng mức, không thêm chi tiết"],
 "Câu What does the speaker imply? cần suy luận từ câu nói và tình huống liền trước. Không chọn một ý khẳng định mạnh hơn bằng chứng. Có thể suy ra cần thêm thời gian từ We still have fifty packages to label, nhưng không suy ra chắc chắn sẽ trễ nếu chưa biết thời hạn.",
 "The store closes in ten minutes thường ngụ ý cần quyết định nhanh.\nWe have already paid the deposit có thể là lý do nên giữ đặt chỗ, không có nghĩa đã thanh toán toàn bộ.\nI'll check whether… là lời hứa kiểm tra, chưa xác nhận kết quả.",
 "Viết riêng hai cột: điều nghe rõ và điều suy ra. Với đáp án suy luận, nối nó với một câu bằng chứng cụ thể. Tập nhận biết mức độ chắc chắn: might, should, will, definitely.")
lesson("u02", 3, "Part 4 · Thông báo và tin nhắn thoại", 4,
 ["Theo dõi mục đích và trình tự của bài nói", "Tách lý do, chi tiết và lời kêu gọi hành động"],
 "Bài nói một người thường có mở đầu xác định ngữ cảnh, thân bài nêu thay đổi và kết thúc bằng hành động. Với thông báo địa điểm, nghe old/new và các từ instead, now, relocated. Với voicemail, chú ý người gọi muốn được gọi lại hay muốn người nhận làm việc khác.",
 "This is a reminder… báo nhắc lại, không phải lời mời mới.\nDue to maintenance… đưa nguyên nhân thay đổi.\nYou do not need to reply… loại đáp án yêu cầu gọi lại dù cuối bài có số điện thoại.",
 "Xem trước câu hỏi và dự đoán dạng thông tin. Nghe một lượt rồi nộp nhóm câu. Sau đó chép 20–30 giây khó nhất; so transcript để tìm nối âm hoặc từ chức năng bị bỏ sót.")
lesson("u03", 3, "Từ vựng nâng cao, điều kiện và sắc thái", 5,
 ["Chọn từ theo logic và cụm cố định", "Phân biệt điều kiện thật, giả định và ngoại lệ"],
 "Unless tương đương if not; provided that đặt điều kiện. Câu điều kiện về tương lai thường dùng hiện tại đơn ở mệnh đề if. Cẩn thận với nearly, hardly, still và already vì chúng thay đổi sắc thái. Những cặp từ như economic/economical hay complimentary/complementary khác nghĩa.",
 "Unless payment arrives, the order will remain on hold: chưa thanh toán thì chưa xử lý.\nThe hotel offers complimentary breakfast: bữa sáng miễn phí, không phải bổ sung lẫn nhau.\nHad we known earlier, we would have acted: đảo ngữ điều kiện trái quá khứ.",
 "Sau khi xác định cấu trúc, đọc toàn câu để kiểm tra logic. Ghi sổ lỗi theo nguyên nhân: từ loại, collocation, điều kiện, hoặc sắc thái. Dùng lại từ sai trong một câu do mình viết.")
lesson("u04", 3, "Part 7 · Đọc đơn văn bản có chiều sâu", 7,
 ["Tìm mục đích và thái độ trong bài dài hơn", "Xử lý điều kiện, ngoại lệ và mốc thời gian"],
 "Skim để xác định loại văn bản, rồi scan theo câu hỏi. Các từ only, except, at least, no later than giới hạn phạm vi thông tin. Đọc kỹ câu trước/sau vị trí tìm được; một từ trùng đáp án không đủ làm bằng chứng.",
 "Applications received after Friday will be considered next month: vẫn xét, nhưng ở tháng sau.\nMembers may bring one guest: chỉ một khách, không phải cả gia đình.\nA trial has been extended: chương trình đang tiếp tục thử nghiệm, chưa chắc đã áp dụng vĩnh viễn.",
 "Làm nhóm câu trong 4–5 phút. Tìm câu bằng chứng cho mỗi đáp án, nhất là câu NOT/EXCEPT. Nếu chưa chắc, đánh dấu và đi tiếp; quay lại sau khi hoàn thành các câu chi tiết.")
lesson("a01", 4, "Part 4 · Ý định, paraphrase và chi tiết nhỏ", 4,
 ["Nhận ra cách nói khác của cùng một ý", "Phân biệt ưu tiên, điều kiện và thông tin nền"],
 "Ở mức nâng cao, đáp án có thể dùng nghĩa tương đương thay vì từ nghe được: get in touch = contact, at no additional cost = free of extra charge. Một chi tiết nhỏ như unless, only hoặc before có thể đảo nghĩa toàn lựa chọn. Giọng tổng hợp trong bộ này hỗ trợ luyện cấu trúc; hãy bổ sung giọng người thật ở nguồn chính thức.",
 "The opening is provisional: lịch khai trương chưa chốt.\nWe can accommodate the request provided that…: có thể đáp ứng nếu đủ điều kiện.\nThe fee will be waived: được miễn phí đó, không phải hoãn đóng.",
 "Nghe không dừng để ghi ba ý: mục đích, thay đổi quan trọng, hành động. Sau lời giải, liệt kê một cặp paraphrase cho mỗi đáp án. Đừng coi việc nhớ transcript sau nhiều lần nghe là năng lực thi lần đầu.")
lesson("a02", 4, "Part 6 · Liên kết và lựa chọn câu chính xác", 6,
 ["Theo dõi tham chiếu qua nhiều câu", "Chọn câu bổ sung đúng lập luận"],
 "Câu chèn đúng phải nối được cả câu trước và câu sau. Tìm cụm tham chiếu such an arrangement, this exception, both options. Mỗi lựa chọn cần đúng ngữ pháp, đúng chủ đề và không mâu thuẫn với chi tiết còn lại. Ý cùng chủ đề nhưng sai vai trò không phải đáp án.",
 "Một câu nêu cách đăng ký phải xuất hiện trước This registration is required.\nNếu đoạn đang nói về hoàn tiền, câu về quà tặng không tự nhiên chỉ vì cùng có customers.\nNevertheless giữ ý đối lập; consequently nêu hệ quả.",
 "Đọc đoạn hoàn chỉnh sau khi làm. Diễn giải mạch: thông tin → điều kiện → hệ quả → hướng dẫn. Tập trả lời lý do ba câu còn lại không nối được đại từ hoặc quan hệ logic.")
lesson("a03", 4, "Part 7 · Nối hai văn bản", 7,
 ["Đối chiếu hai nguồn có thời điểm khác nhau", "Tìm đáp án cần kết hợp nhiều chi tiết"],
 "Xác định vai trò từng văn bản: quảng cáo đặt điều kiện, email xác nhận giao dịch; lịch nêu kế hoạch, tin nhắn nêu thay đổi. Nếu hai mốc khác nhau, nguồn cập nhật sau thường giải thích thay đổi nhưng chỉ áp dụng cho nội dung nó nói. Không tự cho mọi điều kiện cũ đều bị hủy.",
 "Thông báo ghi giảm 10% cho đơn trước ngày 12; email đặt ngày 10 → có thể áp dụng nếu đủ các điều kiện khác.\nEmail nói chỉ đổi địa điểm → thời gian cũ vẫn giữ.\nCâu According to both documents yêu cầu kiểm tra thật sự cả hai nguồn.",
 "Tạo bảng nhỏ ai / việc gì / ngày nào / điều kiện. Với câu cross-reference, chỉ ra một bằng chứng ở mỗi văn bản. Giới hạn khoảng 6 phút cho nhóm năm câu rồi phân tích lỗi sau.")
lesson("a04", 4, "Part 7 · Ba văn bản và chiến lược 900", 7,
 ["Liên kết yêu cầu, xác nhận và cập nhật cuối", "Giữ độ chính xác khi quản lý 75 phút đọc"],
 "Với ba văn bản, ghi nhanh chức năng và ngày của từng nguồn. Theo dõi những điều được giữ lại và được thay đổi. Mục tiêu 900 cần hiệu suất ổn định ở cả nghe lẫn đọc; kết quả một bài luyện nội bộ không dự đoán chắc điểm thi. Đề 200 câu của ứng dụng có thể tái sử dụng câu đã học nên không dùng làm đánh giá độc lập.",
 "Yêu cầu đặt 40 phần ăn; xác nhận gồm 5 phần chay; cập nhật cuối tăng 2 phần chay → kiểm tra đó là tăng tổng hay thay thế trước khi cộng.\nRefund issued khác refund requested.\nMột văn bản nói closed on Monday không loại trừ phục vụ trực tuyến nếu nguồn khác nêu rõ.",
 "Luyện theo đợt: làm có giờ → thống kê lỗi → học lại nhóm yếu → làm một đề mới có nguồn hợp lệ. Chia ngân sách đọc gợi ý 10–12 phút Part5, 8–10 phút Part6, còn lại Part7; điều chỉnh theo kết quả của mình. Giữ thời gian điền mọi đáp án.")

# Question and vocabulary builders are kept in companion source files for review.
for name in ("toeic_vocabulary.py", "toeic_questions_basic.py", "toeic_questions_context.py"):
    exec(compile((Path(__file__).parent / name).read_text(encoding="utf-8"), name, "exec"))

DATA["version"] = "dhv-toeic-2026.10-v2"
DATA["sources"].extend([
    {"id": "bc-reference", "title": "British Council · English grammar reference", "url": "https://learnenglish.britishcouncil.org/free-resources/grammar/english-grammar-reference", "provider": "British Council", "access": "Bài học công khai", "stage": "Level 1–2", "usage": "Tra cấu trúc câu, từ loại, đại từ, thì và giới từ trên trang gốc."},
    {"id": "bc-b1", "title": "British Council · B1–B2 grammar", "url": "https://learnenglish.britishcouncil.org/free-resources/grammar/b1-b2", "provider": "British Council", "access": "Bài học công khai", "stage": "Level 2–4", "usage": "Bổ trợ bị động, điều kiện và liên kết ý; chọn bài theo nhu cầu, không quy đổi CEFR thành điểm TOEIC."},
    {"id": "bc-relative", "title": "British Council · Defining relative clauses", "url": "https://learnenglish.britishcouncil.org/free-resources/grammar/b1-b2/relative-clauses-defining-relative-clauses", "provider": "British Council", "access": "Bài học công khai", "stage": "Level 2 · buổi 1, 5", "usage": "Đối chiếu chức năng đại từ quan hệ trước khi học rút gọn."},
    {"id": "bc-participles", "title": "British Council · Participle clauses", "url": "https://learnenglish.britishcouncil.org/free-resources/grammar/c1/participle-clauses", "provider": "British Council", "access": "Bài học công khai", "stage": "Bổ trợ rút gọn mệnh đề", "usage": "Tham khảo điều kiện chủ thể phù hợp của cụm phân từ; không yêu cầu học hết C1 để bắt đầu TOEIC."},
    {"id": "bc-a2-listening", "title": "British Council · A2 listening", "url": "https://learnenglish.britishcouncil.org/free-resources/listening/a2", "provider": "British Council", "access": "Audio và bài tập tại nguồn", "stage": "Nền tảng / Level 2", "usage": "Bổ sung nghe tình huống quen thuộc bằng giọng người thật."},
    {"id": "bc-b1-listening", "title": "British Council · B1 listening", "url": "https://learnenglish.britishcouncil.org/free-resources/listening/b1", "provider": "British Council", "access": "Audio và bài tập tại nguồn", "stage": "Level 2–3", "usage": "Nghe tình huống công việc và đời sống; không nhập audio vào DHV."},
    {"id": "bc-b2-listening", "title": "British Council · B2 listening", "url": "https://learnenglish.britishcouncil.org/free-resources/listening/b2", "provider": "British Council", "access": "Audio và bài tập tại nguồn", "stage": "Level 3–4", "usage": "Luyện bài nói dài, ý định và nhiều cách diễn đạt; chọn độ khó phù hợp."},
    {"id": "cambridge-dictionary", "title": "Cambridge Dictionary · Tra nghĩa và cách dùng", "url": "https://dictionary.cambridge.org/", "provider": "Cambridge", "access": "Tra cứu tại nguồn", "stage": "Mọi level", "usage": "Kiểm tra nghĩa, phát âm và cụm từ; tự viết ví dụ để kiểm tra hiểu."},
])
DATA["curriculum"] = curriculum()

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(ROOT / "backend"))
    from core.toeic_content import validate_content
    validate_content(DATA)
    target = ROOT / "backend/data/toeic/course.json"
    target.write_text(json.dumps(DATA, ensure_ascii=False, indent=2), encoding="utf-8")
    preview = {k: v for k, v in DATA.items() if k != "questions"}
    preview["question_count"] = len(DATA["questions"])
    preview["vocabulary_count"] = len(DATA["vocabulary"])
    for row in preview["lessons"]:
        row["question_count"] = sum(q["lesson_id"] == row["id"] for q in DATA["questions"])
    (ROOT / "frontend/src/features/toeic/previewCatalog.json").write_text(json.dumps(preview, ensure_ascii=False, indent=2), encoding="utf-8")
    guide = guide_markdown(DATA["sources"])
    (ROOT / "docs/toeic/LO_TRINH_CHI_TIET.md").write_text(guide, encoding="utf-8")
    public_guide = guide
    for filename in ("SOURCES.md", "THIET_KE_CHUONG_TRINH.md", "README.md"):
        public_guide = public_guide.replace(f"]({filename})", f"](https://github.com/maitamdev/eduface-system/blob/main/docs/toeic/{filename})")
    (ROOT / "frontend/public/toeic/lo-trinh-dhv.md").write_text(public_guide, encoding="utf-8")
    print(f"Built {len(DATA['lessons'])} lessons, {len(DATA['questions'])} questions, {len(DATA['vocabulary'])} vocabulary cards")
