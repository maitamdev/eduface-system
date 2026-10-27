"""Original DHV syllabus. Session IDs stay stable independently of quiz lesson IDs.

The first 36 sessions follow the learner's supplied syllabus. Supplemental sessions
develop the earlier 900-point goal. References are links, not imported courseware.
"""
from math import ceil


def lines(value):
    return [line.strip() for line in value.strip().splitlines() if line.strip()]


CURRICULUM = {
    "version": "dhv-syllabus-2026.10-v1",
    "title": "Từ nền tảng đến mục tiêu 900",
    "reviewed_on": "2026-10-27",
    "description": "24 buổi Level 1 xây nền và 12 buổi Level 2 luyện đủ 7 Part, nối tiếp bằng 20 buổi nâng cao. Học theo năng lực và điều chỉnh nhịp sau mỗi mốc đánh giá.",
    "notice": "Các mốc điểm là mục tiêu định hướng, không phải quy đổi CEFR hay cam kết đầu ra. 56 buổi là kế hoạch học; dùng thêm thư viện chuyên đề, đề luyện và sổ câu sai để củng cố. Bài tự kiểm tra trong từng buổi dùng để hiểu bài, không dùng dự đoán điểm thi.",
    "entry": [
        "Người mới bắt đầu học Level 1 từ buổi 1; trước mỗi buổi dành 10 phút nghe âm, trọng âm, số và giờ.",
        "Đã học tiếng Anh: làm khảo sát 25 câu trong DHV, xem lỗi theo Part, rồi đọc thử mục tiêu và bài tự kiểm tra của level dự định học. Khảo sát ngắn chỉ giúp định hướng.",
        "Nếu cần xếp lớp chính xác hoặc đặt lịch thi, dùng đánh giá đầu vào của đơn vị đào tạo hoặc một đề mới có nguồn hợp lệ; không dùng lại câu đã thuộc đáp án.",
    ],
    "daily_routine": [
        {"minutes": 10, "task": "Ôn thẻ đến hạn bằng cách tự nhớ trước khi lật; học thêm 5–10 từ/cụm nếu còn thời gian."},
        {"minutes": 15, "task": "Nghe một đoạn ngắn: nghe ý chính → nghe chi tiết → mở transcript → đọc theo. Ngày đọc: thay bằng một văn bản mới."},
        {"minutes": 15, "task": "Làm bài theo mục tiêu của buổi, ghi câu bằng chứng và lý do loại đáp án."},
        {"minutes": 5, "task": "Ghi sổ lỗi: nguyên nhân, cách sửa và một ví dụ mới; đặt lịch xem lại sau 1, 3 và 7 ngày."},
    ],
    "levels": [
        {"id": "level-1", "name": "Level 1", "title": "Xây nền từ đầu", "target": "Hướng tới 350–450", "session_count": 24,
         "entry": "Phù hợp người mới hoặc cần học lại cấu trúc câu; bắt đầu từ nhận diện chủ ngữ và động từ.",
         "outcomes": ["Phân tích từ loại, thì, hòa hợp chủ vị và cấu trúc câu cơ bản.", "Hiểu mô tả người/vật và chức năng các dạng câu hỏi Part 2.", "Giải Part 5 bằng cấu trúc rồi kiểm tra nghĩa, có sổ lỗi cá nhân."],
         "exit": "Gợi ý lên Level 2: đạt ít nhất 80% hai lượt ôn ngữ pháp khác câu và 70% nhóm Part 1–2 phù hợp nền tảng; giải thích được lỗi. Đây là tiêu chí nội bộ, không tương đương điểm thi.",
         "checkpoints": [6, 12, 18, 24]},
        {"id": "level-2", "name": "Level 2", "title": "Làm chủ 7 phần thi", "target": "Hướng tới 500–650", "session_count": 12,
         "entry": "Nắm câu đơn, từ loại và thì; nếu còn nhầm nhiều, ôn Level 1 buổi 1–12 trước.",
         "outcomes": ["Xử lý quan hệ, rút gọn và từ chỉ lượng trong Part 5.", "Theo dõi mạch Part 6, đối chiếu hai/ba văn bản Part 7.", "Nghe vấn đề, giải pháp, ý định và bước tiếp theo ở Part 3–4."],
         "exit": "Gợi ý lên Level 3: đạt khoảng 75% từng nhóm kỹ năng trên nội dung mới và giải thích được bằng chứng; nếu một Part dưới 60%, dành thêm 2–3 buổi ôn Part đó.",
         "checkpoints": [4, 8, 12]},
        {"id": "level-3", "name": "Level 3", "title": "Tăng độ chính xác và tốc độ", "target": "Hướng tới 700–800", "session_count": 12,
         "entry": "Đã làm quen đủ 7 Part và có thể hoàn thành nhóm bài nghe/đọc mà không dịch từng từ.",
         "outcomes": ["Phân biệt thông tin nghe rõ, hàm ý và giả định không có bằng chứng.", "Xử lý văn bản có nhiều điều kiện, thay đổi và tham chiếu.", "Giữ nhịp đọc 75 phút và luyện nghe một lượt trên nguồn phù hợp."],
         "exit": "Theo dõi 2 bài mới ở những ngày khác nhau, giảm lỗi lặp lại và hoàn thành đúng thời gian. Ưu tiên độ ổn định từng Part; tỷ lệ đúng nội bộ không quy đổi trực tiếp thành 800.",
         "checkpoints": [4, 8, 12]},
        {"id": "level-4", "name": "Level 4", "title": "Hoàn thiện cho mục tiêu 900", "target": "Hướng tới 850–900+", "session_count": 8,
         "entry": "Có kết quả ổn định trên tài liệu mới, hiểu phần lớn nội dung mà không cần nghe lại; còn lỗi tinh hoặc thiếu tốc độ.",
         "outcomes": ["Kiểm soát bẫy paraphrase, phủ định, mức độ chắc chắn và chi tiết nhỏ.", "Đối chiếu nhiều nguồn nhanh mà vẫn xác định được bằng chứng.", "Có kế hoạch ôn cá nhân từ 2 đề mới và điều kiện làm bài sát thực tế."],
         "exit": "Chỉ đánh giá khả năng sẵn sàng thi bằng nhiều bài mới có nguồn và cách chấm phù hợp, kết hợp tư vấn giáo viên khi cần. Không suy ra 900 từ việc hoàn tất lộ trình hoặc thuộc ngân hàng DHV.",
         "checkpoints": [4, 6, 8]},
    ],
    "sessions": [],
}


def session(level, number, title, skill, *, goals, knowledge, examples, checks,
            practice, homework, lessons, sources, terms, checkpoint=None, minutes=90):
    """Two original comprehension checks per session; separate from scored attempts."""
    CURRICULUM["sessions"].append({
        "id": f"l{level}-s{number:02}", "level_id": f"level-{level}", "number": number,
        "title": title, "skill": skill, "minutes": minutes,
        "objectives": lines(goals), "knowledge": lines(knowledge),
        "examples": [{"text": text, "explanation": explanation} for text, explanation in examples],
        "checks": [{"prompt": prompt, "options": options, "correct": answer, "explanation": why}
                   for prompt, options, answer, why in checks],
        "practice": lines(practice), "homework": lines(homework),
        "lesson_ids": lessons, "source_ids": sources, "vocabulary_focus": terms,
        "checkpoint": checkpoint,
        "agenda": ([{"minutes": 10, "task": "Ôn và kiểm tra đầu buổi"},
                    {"minutes": 20, "task": "Học kiến thức trọng tâm và ví dụ"},
                    {"minutes": 20, "task": "Luyện có hướng dẫn"},
                    {"minutes": 25, "task": "Tự làm bài và tìm bằng chứng"},
                    {"minutes": 10, "task": "Chữa lỗi và giải thích lựa chọn"},
                    {"minutes": 5, "task": "Tự kiểm tra, giao bài ôn"}]
                   if minutes == 90 else [{"minutes": 120, "task": "Luyện đề 200 câu; chữa và phân tích ở buổi sau hoặc phần tự học"}]),
    })


session(1, 1, "Cấu tạo câu · Danh từ", "Grammar", goals="""
Tìm chủ ngữ, động từ chính và tân ngữ trong câu công việc.
Xác định vị trí, chức năng và số ít/số nhiều của danh từ.
Phân biệt danh từ đếm được với danh từ không đếm được thông dụng.
""", knowledge="""
Câu đơn thường có chủ ngữ + động từ chia thì; phần sau có thể là tân ngữ, bổ ngữ hoặc trạng ngữ. Câu mệnh lệnh có thể lược chủ ngữ you, nên không máy móc đếm số từ trước động từ.
Danh từ/cụm danh từ có thể làm chủ ngữ, tân ngữ của động từ, tân ngữ của giới từ hoặc bổ ngữ sau be. Tìm từ trung tâm của cụm thay vì chọn danh từ đứng sát động từ.
Danh từ đếm được số ít thường cần từ hạn định. Information, equipment và advice thường không đếm được: dùng some information, a piece of advice; không thêm -s theo thói quen tiếng Việt.
""", examples=[("The receptionist checks each reservation.", "Receptionist là chủ ngữ; checks là động từ; reservation là tân ngữ trong cụm each reservation."), ("The equipment in these rooms is new.", "Equipment không đếm được và là chủ ngữ chính, nên dùng is dù rooms là số nhiều.")], checks=[("The company needs more ____ for the office.", ["equipment", "equipments", "equipping"], 0, "Equipment là danh từ không đếm được; không thêm -s."), ("Trong 'The list of applicants is ready', chủ ngữ trung tâm là gì?", ["applicants", "list", "ready"], 1, "List là trung tâm; of applicants chỉ bổ nghĩa cho list.")], practice="""
Tách S–V–O/C trong 8 câu văn phòng; chỉ ra danh từ trung tâm của mỗi cụm.
Phân loại 12 từ thành đếm được/không đếm được, rồi làm bài “Dựng câu: chủ ngữ, động từ, từ loại” và giải thích 3 lỗi.
""", homework="""
Viết 6 câu giới thiệu lớp hoặc nơi làm việc; khoanh danh từ và gạch chân động từ.
Ôn 8 cụm từ chủ đề văn phòng, kiểm tra lại sau 1 ngày và 3 ngày.
""", lessons=["f02", "f03"], sources=["bc-reference", "bc-grammar"], terms=["employee", "department", "equipment", "information", "application", "schedule"])

session(1, 2, "Đại từ · Vị trí và chức năng", "Grammar", goals="""
Chọn đại từ chủ ngữ, tân ngữ và sở hữu theo vị trí.
Phân biệt tính từ sở hữu với đại từ sở hữu.
Tìm danh từ mà đại từ thay thế trong câu và đoạn ngắn.
""", knowledge="""
I/you/he/she/it/we/they thường đứng ở vị trí chủ ngữ; me/him/her/us/them làm tân ngữ sau động từ hoặc giới từ. Đừng chọn theo tiếng Việt mà bỏ qua chức năng trong câu.
My/your/his/her/its/our/their phải đi trước danh từ. Mine/yours/his/hers/ours/theirs thay cả cụm danh từ, không thêm danh từ ngay sau.
Đại từ phản thân dùng khi chủ thể và đối tượng là cùng người/vật hoặc để nhấn mạnh. Phân biệt its (sở hữu) với it's (it is/it has).
""", examples=[("Please send them the revised agenda.", "Them nhận hành động gửi; the revised agenda là thứ được gửi."), ("This badge is hers; our badges are blue.", "Hers đứng độc lập, còn our đi trước badges.")], checks=[("Mr. Park will call ____ after lunch.", ["we", "our", "us"], 2, "Sau call cần tân ngữ: us."), ("This laptop is ____. Mine is at home.", ["your", "yours", "yourself"], 1, "Yours thay cho your laptop; your không đứng một mình ở đây.")], practice="""
Lập bảng 7 nhóm đại từ; điền 12 câu theo vị trí trước khi dịch nghĩa.
Đọc một email ngắn, nối it/they/them với danh từ gốc và giải thích cách chọn.
""", homework="""
Viết 8 cặp câu có cùng danh từ rồi thay danh từ lặp bằng đại từ phù hợp.
Tạo 5 thẻ lỗi phân biệt their/theirs/them/themselves và ôn theo lịch.
""", lessons=["f02", "b04"], sources=["bc-reference"], terms=["badge", "colleague", "supervisor", "recipient", "owner", "laptop"])

session(1, 3, "Phrase – Clause – Sentence · Tính từ", "Grammar", goals="""
Phân biệt cụm từ, mệnh đề và câu hoàn chỉnh ở mức cơ bản.
Đặt tính từ trước danh từ hoặc sau động từ nối phù hợp.
Nhận biết danh từ trung tâm trong cụm dài.
""", knowledge="""
Ở mức nhập môn, clause hữu hạn có chủ ngữ và động từ chia thì; phrase như in the main office không có cấu trúc đó. Một mệnh đề phụ như because the office is closed cần gắn với mệnh đề chính để tạo câu hoàn chỉnh.
Tính từ thường bổ nghĩa danh từ (a reliable supplier) hoặc làm bổ ngữ sau be/seem/become. Không phải từ đứng sau be đều là tính từ: be còn tham gia cấu trúc tiếp diễn và bị động.
Xác định phạm vi bổ nghĩa: trong a new employee training program, program là danh từ trung tâm. Đọc cả cụm trước khi quyết định từ loại còn thiếu.
""", examples=[("The supplier seems reliable.", "Reliable mô tả supplier sau động từ nối seems."), ("Because the lift is broken, visitors use the stairs.", "Mệnh đề because nêu lý do; visitors use the stairs là mệnh đề chính.")], checks=[("The revised timetable is ____.", ["conveniently", "convenience", "convenient"], 2, "Sau is cần tính từ mô tả timetable."), ("Nhóm nào là câu hoàn chỉnh?", ["In the meeting room.", "The meeting ended early.", "Because the manager arrived."], 1, "The meeting ended early có mệnh đề chính hoàn chỉnh; hai nhóm còn lại là cụm hoặc mệnh đề phụ.")], practice="""
Phân loại 10 nhóm từ thành phrase/clause/sentence; sửa 4 câu thiếu mệnh đề chính.
Mở rộng 6 cụm danh từ bằng tính từ, rồi dùng chúng trong email công việc ngắn.
""", homework="""
Viết 6 câu có be/seem/become + adjective, ghi danh từ được mô tả.
Tìm 5 cụm danh từ trong bài “Email: mục đích, người nhận và việc cần làm” và xác định từ trung tâm.
""", lessons=["f02", "b04"], sources=["bc-reference", "bc-grammar"], terms=["reliable", "available", "convenient", "annual", "revised", "confidential"])

session(1, 4, "Trạng từ · Vị trí và chức năng", "Grammar", goals="""
Nhận ra trạng từ bổ nghĩa động từ, tính từ, trạng từ hoặc cả câu.
Đặt trạng từ tần suất và cách thức ở vị trí tự nhiên.
Tránh áp dụng máy móc quy tắc đuôi -ly.
""", knowledge="""
Trạng từ trả lời các câu hỏi như làm thế nào, mức độ bao nhiêu, khi nào hoặc thường xuyên ra sao. Carefully có thể bổ nghĩa động từ; extremely có thể bổ nghĩa tính từ trong extremely useful.
Trạng từ tần suất thường đứng trước động từ thường nhưng sau be: usually arrives, is usually early. Với cụm động từ, vị trí tùy phạm vi nghĩa; không đặt trạng từ giữa động từ và tân ngữ một cách máy móc.
Friendly là tính từ dù có -ly; fast/hard có thể là trạng từ không thêm -ly. Hardly thường mang nghĩa gần như không, khác hard là chăm chỉ/mạnh.
""", examples=[("The assistant checked the figures carefully.", "Carefully mô tả cách kiểm tra, đứng sau tân ngữ the figures."), ("The new process is remarkably efficient.", "Remarkably bổ nghĩa tính từ efficient, không bổ nghĩa trực tiếp danh từ process.")], checks=[("Please read the safety notice ____.", ["careful", "carefully", "carefulness"], 1, "Cần trạng từ mô tả cách đọc."), ("'She hardly knows the new system' có nghĩa gì?", ["Cô ấy hiểu hệ thống rất kỹ.", "Cô ấy học hệ thống chăm chỉ.", "Cô ấy gần như không biết hệ thống mới."], 2, "Hardly nghĩa gần như không; không đồng nghĩa hard.")], practice="""
Đánh dấu từ được bổ nghĩa trong 12 câu có trạng từ.
Sửa 6 lỗi adjective/adverb và đọc lại câu để kiểm tra nghĩa.
""", homework="""
Viết 5 câu về lịch học với always/usually/often/sometimes/never.
Ghi 4 cặp dễ nhầm: hard/hardly, late/lately, good/well, friendly/friend.
""", lessons=["f02", "f03"], sources=["bc-reference"], terms=["carefully", "promptly", "regularly", "recently", "highly", "nearly"])

session(1, 5, "Động từ · Hiện tại đơn và hiện tại tiếp diễn", "Grammar", goals="""
Tìm động từ chính và trợ động từ trong câu.
Chọn hiện tại đơn cho thói quen/sự thật và tiếp diễn cho việc đang diễn ra.
Hòa hợp chủ ngữ với động từ và tạo câu hỏi/phủ định cơ bản.
""", knowledge="""
Động từ chính biểu đạt hành động hoặc trạng thái. Trợ động từ do/does tạo câu hỏi và phủ định ở hiện tại đơn; be tham gia hiện tại tiếp diễn.
Hiện tại đơn dùng V/V-s/es theo chủ ngữ: The office opens at eight. Sau does/doesn't, động từ chính trở về nguyên mẫu: doesn't open.
Hiện tại tiếp diễn dùng am/is/are + V-ing cho hoạt động đang diễn ra hoặc tình huống tạm thời. Know/own/belong thường dùng dạng đơn trong nghĩa trạng thái; dấu hiệu now không thay thế việc hiểu nghĩa.
""", examples=[("Our team meets every Monday.", "Every Monday chỉ thói quen; team được dùng như đơn vị số ít trong câu này."), ("The technician is replacing the cable now.", "Hành động đang diễn ra, dùng is replacing.")], checks=[("Ms. Tran usually ____ the office at six.", ["leaves", "is leave", "leaving"], 0, "Usually chỉ thói quen; chủ ngữ số ít dùng leaves."), ("Look! Two workers ____ the sign.", ["installs", "are installing", "is installing"], 1, "Hoạt động đang diễn ra; two workers số nhiều đi với are.")], practice="""
So sánh 6 cặp câu về công việc thường ngày và việc đang làm.
Đổi 8 câu khẳng định sang phủ định/câu hỏi, giữ đúng dạng động từ chính.
""", homework="""
Viết 5 câu lịch thường ngày và 5 câu mô tả hành động đang quan sát.
Làm bài “Thì, hòa hợp chủ vị và dấu hiệu thời gian”, ghi lỗi về chủ ngữ thật và dấu hiệu thời gian.
""", lessons=["b03", "b01"], sources=["bc-reference", "bc-grammar"], terms=["operate", "maintain", "replace", "deliver", "attend", "usually"])

session(1, 6, "Quá khứ đơn · Hiện tại hoàn thành · There is/are", "Grammar", goals="""
Phân biệt thời điểm đã kết thúc với trải nghiệm/kết quả liên quan hiện tại.
Dùng since/for và các dạng động từ bất quy tắc thông dụng.
Chọn there is/are theo danh từ giới thiệu.
""", knowledge="""
Quá khứ đơn dùng V-ed/V2 khi nói việc đã kết thúc: yesterday, last month. Sau did/didn't dùng động từ nguyên mẫu.
Hiện tại hoàn thành dùng have/has + V3 cho trải nghiệm, kết quả hiện tại hoặc việc kéo dài đến hiện tại; không gắn máy móc với mốc quá khứ đã đóng như yesterday. Since chỉ điểm bắt đầu; for chỉ khoảng thời gian.
There is giới thiệu danh từ số ít/không đếm được; there are giới thiệu số nhiều trong cách dùng chuẩn cần luyện. Phân biệt there với their, và phân biệt câu tồn tại với câu nói vị trí của một vật đã biết.
""", examples=[("We sent the invoice yesterday; the client has not replied yet.", "Sent gắn mốc đã qua; has not replied diễn tả trạng thái chưa có phản hồi đến hiện tại."), ("There are three messages on your desk.", "Danh từ giới thiệu là three messages, nên dùng are.")], checks=[("The branch ____ in 2021.", ["has opened", "opening", "opened"], 2, "In 2021 là thời điểm quá khứ đã kết thúc; dùng opened."), ("There ____ some useful information in the guide.", ["is", "are", "have"], 0, "Information không đếm được, dùng there is.")], practice="""
Làm 12 câu phân biệt quá khứ đơn/hoàn thành và giải thích mốc thời gian.
Ôn xen kẽ buổi 1–6: 12 câu cấu trúc/từ loại, tự sửa mà không xem đáp án trước.
""", homework="""
Viết 6 cặp câu việc đã làm và kết quả đến nay; dùng since/for ở hai câu.
Nếu dưới 80% bài ôn cấu trúc, học lại buổi tương ứng trước khi thêm nhiều thì mới.
""", lessons=["b03", "f02"], sources=["bc-reference", "bc-b1"], terms=["already", "yet", "since", "recently", "invoice", "branch"], checkpoint="Mốc 1: rà lại cấu trúc câu và từ loại của buổi 1–6; lưu 3 lỗi cần ôn trong tuần.")

session(1, 7, "Động từ khiếm khuyết · Tương lai đơn", "Grammar", goals="""
Dùng modal + động từ nguyên mẫu và phân biệt khả năng/nghĩa vụ/lời khuyên.
Nhận biết lời hứa, dự đoán và quyết định với will.
Phân biệt mustn't với don't have to.
""", knowledge="""
Can/could/may/might/must/should + động từ nguyên mẫu không to; không thêm -s theo chủ ngữ. Have to là cấu trúc khác, có biến đổi has to/had to.
Mustn't là không được phép; don't have to là không cần thiết. Should nêu lời khuyên, không có độ bắt buộc như must trong quy định.
Will + V thường dùng cho lời hứa, dự đoán hoặc quyết định lúc nói. Mệnh đề thời gian/điều kiện nói tương lai thường dùng hiện tại đơn: when the parcel arrives, we will call.
""", examples=[("You must wear a badge, but you don't have to wear a tie.", "Thẻ là bắt buộc; cà vạt không bắt buộc, không phải bị cấm."), ("I'll email the file when I get back.", "Will ở mệnh đề chính; get ở mệnh đề when chỉ thời gian tương lai.")], checks=[("Employees must ____ the form today.", ["submits", "submit", "to submit"], 1, "Sau must dùng nguyên mẫu không to."), ("'You don't have to print it' nghĩa là gì?", ["Bạn bị cấm in.", "Bạn bắt buộc phải in.", "Bạn không cần in."], 2, "Không cần thiết khác với cấm; cấm là mustn't.")], practice="""
Phân loại 10 câu modal thành cho phép, khả năng, lời khuyên và nghĩa vụ.
Viết 6 phản hồi ngắn cho lời nhờ/đề nghị; nghe bài “Part 2 · Yêu cầu, đề nghị và câu hỏi lựa chọn” để nhận chức năng giao tiếp.
""", homework="""
Viết 5 quy định lớp học với must/mustn't và 3 lời khuyên với should.
Ghi 5 câu hứa hoặc kế hoạch có will, kiểm tra lại sau modal không có -s/to.
""", lessons=["b02", "b03"], sources=["bc-reference"], terms=["permission", "requirement", "mandatory", "optional", "promise", "confirm"])

session(1, 8, "Giới từ · Thời gian, vị trí và cụm cố định", "Grammar", goals="""
Nhận ra giới từ + cụm danh từ/đại từ/V-ing.
Phân biệt at/on/in, by/until và for/during trong ngữ cảnh.
Học giới từ cùng động từ/tính từ thay vì dịch từng từ.
""", knowledge="""
Giới từ tạo cụm bổ nghĩa cho danh từ, động từ hoặc cả câu; sau giới từ thường là cụm danh từ, đại từ tân ngữ hoặc V-ing. To có thể là giới từ trong look forward to, không luôn là dấu hiệu nguyên mẫu.
At thường đi với giờ, on với ngày, in với tháng/năm. By nêu hạn chót; until nêu sự tiếp diễn đến một mốc. During + danh từ chỉ sự kiện/khoảng thời gian; for + khoảng kéo dài.
Cụm cố định như responsible for, interested in, apply for phải học theo nghĩa toàn cụm. Một giới từ có thể mang nhiều nghĩa, nên kiểm tra cả cấu trúc lẫn tình huống.
""", examples=[("Please submit the request by Friday; the office is open until six.", "By Friday là hạn nộp; until six là kéo dài giờ mở cửa."), ("We look forward to meeting you.", "To là giới từ trong cụm look forward to nên sau đó dùng meeting.")], checks=[("The seminar starts ____ 9 a.m. on Monday.", ["at", "in", "on"], 0, "At dùng trước một giờ cụ thể."), ("Ms. Lee is responsible ____ ordering supplies.", ["to", "for", "with"], 1, "Cụm responsible for + danh từ/V-ing.")], practice="""
Lập trục thời gian để giải thích 6 cặp by/until; điền 10 câu giới từ.
Mô tả 5 vị trí đồ vật bằng next to/between/behind/in front of/against.
""", homework="""
Viết một email lịch hẹn có 6 cụm thời gian và địa điểm.
Ôn 8 cụm adjective/verb + preposition, đặt câu riêng thay vì chỉ chép nghĩa.
""", lessons=["b01", "f03"], sources=["bc-reference", "bc-grammar"], terms=["by Friday", "until noon", "during the meeting", "responsible for", "interested in", "next to"])

session(1, 9, "Thể bị động · Passive voice", "Grammar", goals="""
Xác định chủ ngữ làm hay nhận hành động.
Tạo bị động be + V3 theo thì và modal.
Phân biệt trạng thái với hành động đang bị thực hiện.
""", knowledge="""
Bị động đưa đối tượng nhận hành động lên làm chủ ngữ; dạng cơ bản là be + V3. Thì và số nằm ở be: is delivered, was delivered, has been delivered.
Với modal dùng modal + be + V3; với tiếp diễn dùng be + being + V3. By + tác nhân có thể bỏ khi không cần nêu; by Friday chỉ hạn chót, không phải tác nhân.
Không phải mọi động từ đều có bị động thông thường; arrive/happen không lấy tân ngữ trực tiếp. Trong hình, are stacked mô tả trạng thái, are being stacked cần hành động đang xếp.
""", examples=[("The invoices were checked by the accountant.", "Invoices nhận hành động kiểm tra; were checked là bị động quá khứ."), ("The boxes are being loaded onto a truck.", "Being loaded diễn tả đang được chất lên xe, cần ngữ cảnh có hoạt động.")], checks=[("All visitors must ____ at reception.", ["registering", "be registered", "been registered"], 1, "Modal + be + V3; khách được đăng ký tại lễ tân."), ("The parcel ____ yesterday.", ["was delivered", "is delivering", "has deliver"], 0, "Parcel nhận hành động; yesterday yêu cầu quá khứ: was delivered.")], practice="""
Đổi 8 câu chủ động có tân ngữ sang bị động và giữ nguyên thì.
So sánh mô tả đồ vật ở bài “Part 1 · Hành động và vị trí trong hình”: trạng thái/đang được thực hiện, nêu bằng chứng.
""", homework="""
Viết quy trình xử lý đơn hàng bằng 6 câu bị động.
Chọn 5 câu sai của bài “Bị động, mệnh đề quan hệ và liên từ”, giải thích vai trò chủ ngữ và dạng be.
""", lessons=["i03", "b01"], sources=["bc-b1", "bc-reference"], terms=["be delivered", "be approved", "be installed", "be repaired", "be arranged", "be required"])

session(1, 10, "Phân từ V-ing / V-ed", "Grammar", goals="""
Phân biệt phân từ với động từ chia thì.
Chọn tính từ -ing/-ed theo nghĩa gây ra/cảm nhận.
Nhận biết cụm phân từ bổ nghĩa danh từ.
""", knowledge="""
V-ing và V3 có thể tham gia cụm động từ (is working, was repaired) hoặc bổ nghĩa danh từ (a waiting customer, a printed form). Chỉ thấy V-ing chưa đủ kết luận câu đã có động từ chính chia thì.
Với tính từ cảm xúc, -ing thường mô tả điều gây cảm giác; -ed mô tả trạng thái cảm nhận. Không dùng mẹo người luôn -ed, vật luôn -ing: a boring speaker là người gây chán.
Cụm phân từ sau danh từ có thể mang nghĩa chủ động hoặc bị động: people waiting outside, documents attached to the email. Phải xác định danh từ được bổ nghĩa trước khi chọn dạng.
""", examples=[("The training was interesting, but the trainees were tired.", "Interesting mô tả khóa học gây hứng thú; tired là trạng thái của học viên."), ("The documents attached to this message are confidential.", "Attached bổ nghĩa documents theo nghĩa bị động; are là động từ chính.")], checks=[("The instructions were very ____.", ["confused", "confusing", "confuse"], 1, "Instructions gây bối rối, dùng confusing."), ("Customers ____ outside will be served first.", ["waited", "wait", "waiting"], 2, "Customers tự thực hiện hành động chờ; waiting bổ nghĩa cho customers.")], practice="""
Tìm động từ chia thì trong 10 câu chứa V-ing/V3.
Viết 6 cặp câu cảm xúc và giải thích chủ thể gây/cảm nhận.
""", homework="""
Mô tả 5 người/vật bằng cụm phân từ sau danh từ.
Ôn 6 cặp tính từ cảm xúc trong câu hoàn chỉnh, không học mỗi hậu tố.
""", lessons=["i03", "f02"], sources=["bc-grammar", "bc-participles"], terms=["interested", "interesting", "satisfied", "satisfying", "attached", "remaining"])

session(1, 11, "Mệnh đề trạng ngữ · Quan hệ giữa các ý", "Grammar", goals="""
Phân biệt mệnh đề chỉ thời gian, nguyên nhân, điều kiện và tương phản.
Chọn liên từ hay giới từ dựa trên cấu trúc phía sau.
Dùng thì phù hợp trong mệnh đề thời gian tương lai.
""", knowledge="""
Because/although/if/when nối mệnh đề; because of/despite thường đi với cụm danh từ hoặc V-ing. Cùng gần nghĩa không có nghĩa thay thế được ở mọi vị trí.
Xác định logic trước: nguyên nhân, kết quả, tương phản hay điều kiện. Không dùng đồng thời although và but để nối cùng một cặp mệnh đề theo cấu trúc đang luyện.
Mệnh đề thời gian nói tương lai thường dùng hiện tại: when the meeting ends, we will leave. Unless nghĩa là if not, cần đọc lại cả câu để tránh phủ định hai lần.
""", examples=[("Although it rained, the delivery arrived on time.", "Although + mệnh đề chỉ tương phản; không cần thêm but."), ("Because of the roadworks, the bus took another route.", "Because of theo sau bởi cụm danh từ the roadworks.")], checks=[("____ the heavy traffic, Ms. Kim arrived on time.", ["Although", "Because", "Despite"], 2, "Sau chỗ trống là cụm danh từ; Despite phù hợp cấu trúc và tương phản."), ("We will contact you when the documents ____.", ["arrive", "will arrive", "arriving"], 0, "Mệnh đề when chỉ thời gian tương lai dùng hiện tại đơn.")], practice="""
Nối 8 cặp câu bằng liên từ đúng nghĩa; chuyển 4 câu sang cụm giới từ tương đương.
Giải thích vì sao một đáp án đúng nghĩa nhưng sai cấu trúc vẫn phải loại.
""", homework="""
Viết 8 câu công việc với because/although/if/when và 2 câu với despite.
Tự kiểm tra lại sự có mặt của chủ ngữ + động từ sau từng liên từ.
""", lessons=["i03", "i04"], sources=["bc-b1", "bc-reference"], terms=["although", "despite", "because of", "unless", "as soon as", "whereas"])

session(1, 12, "So sánh · Ôn nền tảng ngữ pháp", "Grammar", goals="""
Dùng so sánh hơn, nhất và ngang bằng với tính từ/trạng từ.
Nhận biết dạng bất quy tắc và từ nhấn mạnh mức độ.
Tổng hợp cách chọn từ loại, thì và cấu trúc trước khi luyện đề.
""", knowledge="""
Tính từ ngắn thường thêm -er/-est; từ dài thường dùng more/most. Good/well → better/best; bad → worse/worst. Không kết hợp more với một dạng đã có -er trong cấu trúc chuẩn đang học.
As + adjective/adverb + as diễn tả ngang bằng; less/least diễn tả mức ít hơn. Xác định đang so sánh phẩm chất hay cách làm để chọn adjective/adverb.
Much/far/a little có thể bổ nghĩa so sánh hơn; very không đứng ngay trước comparative theo cách dùng này. So sánh phải cùng đối tượng và đủ ngữ cảnh, không chọn chỉ dựa vào than.
""", examples=[("This route is much shorter than the old one.", "Much nhấn mạnh mức chênh lệch; không dùng more shorter."), ("Lan completes reports as carefully as Minh does.", "Carefully bổ nghĩa completes nên dùng trạng từ trong cấu trúc ngang bằng.")], checks=[("The new printer is ____ than the previous model.", ["more faster", "fastest", "faster"], 2, "Fast có so sánh hơn faster; không thêm more."), ("Of the three proposals, this one is the ____.", ["most practical", "more practical", "practically"], 0, "Chọn một trong ba: dùng so sánh nhất the most practical.")], practice="""
Làm 12 câu so sánh, giải thích cách xác định đối tượng và mức độ.
Ôn hỗn hợp buổi 1–12 trong 20 phút; phân nhóm lỗi thay vì chỉ cộng điểm.
""", homework="""
Viết bảng so sánh 3 sản phẩm với 6 câu đúng cấu trúc.
Nếu còn dưới 80% một nhóm ngữ pháp, dành thêm một lượt ôn nhóm đó trước buổi 13.
""", lessons=["f02", "b03", "i03"], sources=["bc-grammar", "bc-reference"], terms=["efficient", "affordable", "reliable", "better", "the least", "as carefully as"], checkpoint="Mốc 2: kiểm tra nền tảng buổi 1–12; biết giải thích vị trí, chức năng và nghĩa của đáp án.")

session(1, 13, "Part 5 · Dạng 1: Biến thể từ loại", "Reading", goals="""
Nhận diện nhóm đáp án cùng gốc từ.
Dự đoán từ loại cần điền từ cấu trúc hai phía.
Kiểm tra nghĩa sau khi lọc đúng chức năng.
""", knowledge="""
Với apply/application/applicable/applicant, trước hết hỏi chỗ trống làm nhiệm vụ gì: chủ ngữ, tân ngữ, bổ nghĩa danh từ hay động từ. Hậu tố chỉ hỗ trợ, không thay thế phân tích câu.
Một vị trí danh từ có thể nhận nhiều danh từ khác nghĩa: applicant là người ứng tuyển, application là đơn/quá trình ứng tuyển. Vì vậy chọn đúng từ loại chưa đủ để chọn đáp án.
Đọc tối thiểu cả cụm chứa chỗ trống và động từ chính. Tập phân tích đúng trước, rồi mới giới hạn khoảng 30–40 giây cho câu đơn giản; không hy sinh độ hiểu để chạy đồng hồ.
""", examples=[("The successful applicant will start next month.", "Vị trí danh từ chỉ người thực hiện start, nên applicant phù hợp hơn application."), ("Please review the contract thoroughly.", "Thoroughly là trạng từ mô tả review; thorough là tính từ.")], checks=[("The committee praised the ____ of the presentation.", ["clear", "clearly", "clarity"], 2, "Sau the và trước of cần danh từ: clarity."), ("The new policy is ____ to all branches.", ["applicable", "application", "applicant"], 0, "Applicable là tính từ có nghĩa áp dụng được, đi với to.")], practice="""
Luyện 15 câu biến thể từ loại; ghi loại từ trước khi xem đáp án.
Chọn 5 câu sai, viết cả lý do cấu trúc và lý do nghĩa.
""", homework="""
Tạo 8 họ từ gồm danh từ/động từ/tính từ/trạng từ có thật, mỗi họ kèm một câu.
Làm lại 5 lỗi sau 48 giờ bằng câu tự viết mới.
""", lessons=["f02", "f03"], sources=["bc-reference", "cambridge"], terms=["apply", "application", "applicant", "applicable", "clarity", "thoroughly"])

session(1, 14, "Part 1: Một người · Part 2: WHERE / WHEN", "Listening", goals="""
Mô tả chủ thể, hành động và vị trí trong hình một người.
Phân biệt câu hỏi nơi chốn với thời điểm.
Nghe số, giờ và giới từ trong cụm thay vì từng từ riêng.
""", knowledge="""
Part 1 có bốn mô tả nghe; quan sát hành động thật sự nhìn thấy, không tự thêm nghề nghiệp hay mục đích. Chú ý holding khác reaching for, wearing khác putting on.
Where thường cần nơi chốn hoặc chỉ dẫn tới nơi biết thông tin. When cần thời điểm, khoảng mốc hoặc lời nói chưa biết lịch. Câu đúng có thể gián tiếp nhưng vẫn giải quyết nhu cầu người hỏi.
Part 2 có ba phản hồi nghe. Loại theo ý nghĩa trước; từ trùng âm hoặc trùng từ trong câu hỏi không phải bằng chứng đúng. Lần đầu nghe không mở transcript.
""", examples=[("Where can I collect my badge? — At the front desk.", "Câu đáp cung cấp đúng địa điểm nhận thẻ."), ("When will the technician arrive? — Shortly after lunch.", "Sau bữa trưa là thông tin thời gian, không nhất thiết phải có con số.")], checks=[("Phản hồi phù hợp: 'Where is the training room?'", ["At ten o'clock.", "On the second floor.", "For two hours."], 1, "On the second floor trả lời nơi chốn."), ("Trong ảnh một người đang cầm ô đã mở, mô tả nào bám đúng thông tin đó?", ["He is buying an umbrella.", "He is repairing an umbrella.", "He is holding an umbrella."], 2, "Chỉ hành động holding được cung cấp; buying/repairing là suy diễn.")], practice="""
Luyện 6 hình một người từ bài hỗ trợ/nguồn mẫu; nói trước một mô tả rồi nghe.
Luyện 10 câu WHERE/WHEN, ghi dấu hiệu quyết định sau lượt nghe đầu.
""", homework="""
Nghe và chép 10 mốc số/giờ; so transcript sau khi tự ghi.
Đọc theo 5 câu đáp trong bài “Nghe số, giờ và từ để hỏi”; giữ trọng âm của từ mang thông tin.
""", lessons=["b01", "f01"], sources=["bc-listening", "ets"], terms=["holding", "reaching for", "reception", "upstairs", "shortly", "half past"])

session(1, 15, "Part 5 · Biến thể động từ: Thì và chủ ngữ", "Reading", goals="""
Tìm chủ ngữ thật khi có cụm giới từ/mệnh đề chen vào.
Chọn thì bằng mốc thời gian và trình tự sự kiện.
Kiểm tra động từ chia thì và dạng nguyên mẫu sau trợ động từ.
""", knowledge="""
Gạch phần bổ nghĩa để thấy chủ ngữ trung tâm: The cost of the repairs has increased. Repairs đứng gần động từ nhưng không quyết định số của has.
Đọc toàn câu tìm mốc thời gian rõ, quan hệ trước/sau và trạng thái còn tiếp diễn. Since/for không phải dấu hiệu duy nhất; phải xét nghĩa cùng các thành phần còn lại.
Mỗi mệnh đề hữu hạn cần động từ chia thì; tránh chọn V-ing chỉ vì nó trông giống động từ. Sau modal/do/does/did, kiểm tra dạng động từ theo cấu trúc tương ứng.
""", examples=[("The manager, along with two assistants, is attending the seminar.", "Along with không biến chủ ngữ manager thành số nhiều."), ("Our supplier has served this region for ten years.", "Công việc bắt đầu trước và còn liên quan hiện tại, dùng has served.")], checks=[("The price of these tickets ____ taxes.", ["includes", "include", "including"], 0, "Price là danh từ trung tâm số ít: includes."), ("The team ____ the report last Friday.", ["has completed", "completed", "completing"], 1, "Last Friday là mốc quá khứ đóng, dùng completed.")], practice="""
Luyện 15 câu động từ; ghi S, V và dấu thời gian trên mỗi câu.
So sánh 5 câu có chủ ngữ bị ngăn cách với động từ; giải thích bẫy danh từ gần nhất.
""", homework="""
Viết 6 câu có of/with/along with ở giữa chủ ngữ và động từ.
Ôn dạng quá khứ và V3 của 10 động từ gặp trong bài, dùng trong câu riêng.
""", lessons=["b03", "f02"], sources=["bc-reference", "bc-b1"], terms=["cost", "price", "along with", "recently", "last quarter", "so far"])

session(1, 16, "Part 1: Nhiều người · Part 2: WHO / WHICH", "Listening", goals="""
Theo dõi từng người và hoạt động chung trong hình.
Hiểu câu hỏi người chịu trách nhiệm và câu hỏi lựa chọn.
Nhận biết phản hồi bằng chức vụ, bộ phận hoặc chỉ dẫn.
""", knowledge="""
Với nhiều người, kiểm tra all/some/one of: câu nói mọi người cùng làm một việc có thể sai nếu chỉ một người làm. Không gán hành động của một người cho cả nhóm.
Who hỏi danh tính, chức năng hoặc người làm việc; câu đáp có thể nêu bộ phận thay tên riêng. Which hỏi chọn một trong những khả năng ngữ cảnh đã giới hạn.
Lắng nghe thì và vai trò: who approved khác who will approve. Đáp án nhắc đúng người nhưng sai thời điểm/hành động vẫn có thể sai.
""", examples=[("Who handles room bookings? — The reception team does.", "Tên bộ phận trả lời được câu hỏi về trách nhiệm."), ("Which entrance should we use? — The one beside the car park.", "The one thay entrance, cung cấp cách xác định lựa chọn.")], checks=[("'Who will lead tomorrow's tour?' — chọn câu đáp hợp lý.", ["At the main gate.", "Ms. Lin from reception.", "It lasted two hours."], 1, "Ms. Lin là người sẽ dẫn đoàn."), ("Ảnh có ba người ngồi, một người đứng. Mô tả nào không phù hợp?", ["Some people are seated.", "One person is standing.", "All the people are standing."], 2, "All là phạm vi quá rộng, trái thông tin đã cho.")], practice="""
Luyện 6 hình nhóm người; lập bảng ai–đang làm gì trước khi chữa.
Luyện 10 câu WHO/WHICH, diễn đạt lại câu đáp bằng một câu rõ nghĩa.
""", homework="""
Tạo 8 cặp câu hỏi WHO/WHICH về lớp học hoặc cơ quan.
Nghe lại 3 câu đã sai vì tên người/chức vụ, chép đúng cụm quyết định.
""", lessons=["b01", "f01", "b02"], sources=["bc-listening", "ets"], terms=["lead", "handle", "department", "entrance", "seated", "gathered"])

session(1, 17, "Part 5 · Biến thể động từ: Bị động", "Reading", goals="""
Kết hợp lựa chọn thì, số và thể chủ động/bị động.
Nhận biết bị động với modal và hoàn thành.
Loại dạng sai cấu trúc trước khi kiểm tra nghĩa.
""", knowledge="""
Quy trình ba bước: tìm chủ ngữ → xem chủ ngữ làm hay nhận hành động → xác định thời gian. Đừng chọn bị động chỉ vì câu có by hoặc một dạng V3.
Is/are + V3, was/were + V3, has/have been + V3, modal + be + V3 phải được giữ đúng thành phần. Being và been không thay thế tùy ý.
Một số V3 dùng như tính từ trạng thái; khi có nhiều đáp án đều đúng cấu trúc, ngữ cảnh thời gian và nghĩa giúp quyết định. Kiểm tra tân ngữ và bản chất động từ.
""", examples=[("The budget must be approved before purchases are made.", "Hai chủ ngữ đều nhận hành động; modal + be approved và are made."), ("The files have already been uploaded.", "Hiện tại hoàn thành bị động cần have + been + V3.")], checks=[("The new schedule will ____ tomorrow.", ["be announced", "been announced", "announcing"], 0, "Will + be + V3."), ("All damaged items ____ by the supplier last week.", ["are replacing", "have replace", "were replaced"], 2, "Items nhận hành động; last week và chủ ngữ số nhiều yêu cầu were replaced.")], practice="""
Luyện 15 câu động từ trộn chủ động/bị động, nêu ba bước suy luận cho mỗi câu.
Sửa 5 lỗi thiếu be/been hoặc nhầm being, không chỉ ghi đáp án đúng.
""", homework="""
Viết 6 câu thông báo theo ba dạng: hiện tại, quá khứ, modal bị động.
Ôn lại các câu sai ở “Bị động, mệnh đề quan hệ và liên từ” sau 2 ngày, không xem lời giải trước.
""", lessons=["i03", "b03"], sources=["bc-b1", "bc-reference"], terms=["approve", "announce", "replace", "upload", "process", "notify"])

session(1, 18, "Part 1: Đồ vật · Part 2: Yes/No và Tag questions", "Listening", goals="""
Phân biệt trạng thái đồ vật với hành động đang diễn ra.
Hiểu câu hỏi Yes/No và câu hỏi đuôi theo ý nghĩa.
Chấp nhận phản hồi gián tiếp khi nó giải quyết đúng câu hỏi.
""", knowledge="""
Khi không thấy người thực hiện, tránh chọn are being moved chỉ từ vị trí đồ vật. Mô tả trạng thái thường dùng be + V3 hoặc giới từ vị trí.
Yes/No không bắt buộc đáp bằng yes/no; The room is already booked trả lời gián tiếp cho Can we use the room? Phải xét tình huống, không chỉ hình thức câu.
Câu hỏi đuôi thường tìm xác nhận. Hiểu nội dung được xác nhận và nghe cả câu đáp; không dịch yes/no máy móc từ cách phản hồi tiếng Việt.
""", examples=[("The chairs are arranged in rows.", "Mô tả bố trí; không khẳng định đang có người xếp."), ("The meeting isn't cancelled, is it? — No, it's still on.", "It's still on xác nhận cuộc họp vẫn diễn ra; nghĩa toàn câu quyết định.")], checks=[("'Have you sent the invoice?' — 'I'm waiting for the final amount.' Hàm ý gì?", ["Đã gửi xong.", "Chưa gửi vì đang đợi số tiền cuối.", "Không có hóa đơn."], 1, "Đang chờ thông tin cần cho hóa đơn, nên chưa gửi; không suy ra không tồn tại."), ("Mô tả trạng thái hộp đã xếp trên kệ là gì?", ["The boxes are stacked on shelves.", "The boxes are being sold.", "The boxes are arriving."], 0, "Are stacked nói trạng thái xếp; hai câu còn lại thêm hành động không có bằng chứng.")], practice="""
Luyện 6 hình vật và 10 câu Yes/No/Tag; ghi nguyên nhân từng lựa chọn sai.
Ôn buổi 14/16/18: tự phân nhóm câu hỏi trước khi chọn phản hồi.
""", homework="""
Viết 6 câu Yes/No và 3 câu đuôi kèm phản hồi có nội dung rõ.
Lập sổ bẫy: trạng thái/hành động, từ lặp, âm gần giống, sai chức năng.
""", lessons=["b01", "b02", "i01"], sources=["ets", "bc-listening"], terms=["stacked", "arranged", "leaning", "booked", "cancelled", "still on"], checkpoint="Mốc 3: rà khả năng nghe ý chính Part 1–2 và giải thích bẫy; luyện lại câu mới nếu còn nhầm chức năng câu hỏi.")

session(1, 19, "Part 5 · Dạng 3: Biến thể đại từ", "Reading", goals="""
Chọn đại từ theo vị trí và đối tượng tham chiếu.
Phân biệt sở hữu, phản thân và đại từ tân ngữ trong câu dài.
Kiểm tra số và tính nhất quán của đại từ.
""", knowledge="""
Trước danh từ thường cần tính từ sở hữu; sau động từ/giới từ có thể cần đại từ tân ngữ. Đại từ sở hữu thay cả cụm danh từ, nên xem có danh từ ngay sau không.
Reflexive như themselves dùng khi đối tượng trùng chủ thể hoặc để nhấn mạnh; không dùng như một cách làm cho me/us nghe trang trọng hơn trong mọi câu.
Trong câu dài, tìm antecedent trước; it/they cần khớp đối tượng nói đến. Each/every + danh từ số ít đòi hỏi chú ý hòa hợp, nhưng lựa chọn đại từ còn phụ thuộc ngữ cảnh và cách dùng hiện đại.
""", examples=[("All applicants must bring their identification.", "Their bổ nghĩa identification; they/theirs không dùng trực tiếp trước danh từ này."), ("The engineers installed the system themselves.", "Themselves nhấn mạnh chính các kỹ sư thực hiện.")], checks=[("Please send the receipt to ____.", ["I", "my", "me"], 2, "Sau giới từ to cần tân ngữ me."), ("The team completed the inspection by ____.", ["itself", "its", "it"], 0, "By itself diễn tả tự thực hiện; team ở đây là đơn vị số ít.")], practice="""
Luyện 15 câu đại từ, ghi đối tượng mà mỗi đại từ thay thế.
Tạo 5 cặp our/ours và their/theirs rồi giải thích sự khác nhau.
""", homework="""
Viết email 80 từ có đại từ thay danh từ để tránh lặp, kiểm tra tham chiếu rõ.
Ôn lại 5 câu sai sau 48 giờ và giải thích bằng tiếng Việt.
""", lessons=["f02", "b04"], sources=["bc-reference", "cambridge"], terms=["identification", "applicant", "receipt", "by itself", "on their own", "recipient"])

session(1, 20, "Part 1: Người và vật · Part 2: HOW / WHY", "Listening", goals="""
Kết nối người, động tác và đồ vật trong hình.
Phân biệt how/how long/how often/how much/how many.
Hiểu lý do trực tiếp hoặc gián tiếp của câu WHY.
""", knowledge="""
Mô tả đúng cần khớp chủ thể, hành động và vật liên quan. Một từ đúng với hình không cứu được mệnh đề còn lại sai.
How hỏi cách thức/trạng thái; how long hỏi thời lượng, how often hỏi tần suất, how much/how many hỏi lượng. Nghe trọn cụm mở đầu chứ không dừng ở how.
Why có thể được trả lời bằng because, to + V chỉ mục đích hoặc một câu nêu nguyên nhân. Why don't we… thường là đề nghị, không đơn thuần hỏi lý do.
""", examples=[("How often is the filter replaced? — Every three months.", "Every three months là tần suất, không phải thời gian thao tác mất bao lâu."), ("Why don't we meet online? — That would save time.", "Đây là đề nghị họp trực tuyến, phản hồi đồng ý hợp lý.")], checks=[("'How long will the repair take?' — chọn câu đáp.", ["Every Tuesday.", "About two hours.", "By the side entrance."], 1, "How long hỏi thời lượng."), ("'Why was the shipment delayed?' — chọn câu đáp.", ["Because of the storm.", "At the warehouse.", "Two packages."], 0, "Because of the storm cung cấp nguyên nhân.")], practice="""
Luyện 6 hình người–vật và 12 câu HOW/WHY; phân loại từng how trước khi nghe đáp án.
Đổi 4 câu Why don't we… thành lời đề nghị tương đương.
""", homework="""
Ghi âm 8 cặp HOW/WHY với câu đáp; nghe lại xem thời lượng/tần suất có bị nhầm.
Đọc theo một đoạn A1/A2 tại nguồn đã dẫn, ghi 5 cụm hỏi đáp mới.
""", lessons=["b01", "f01", "b02"], sources=["bc-listening", "ets"], terms=["how often", "how long", "frequency", "duration", "delay", "purpose"])

session(1, 21, "Part 5 · Dạng 4: Cụm từ · Dạng 5: Giới từ", "Reading", goals="""
Chọn collocation trong ngữ cảnh công việc.
Phân biệt giới từ theo nghĩa và cấu trúc bổ ngữ.
Lưu từ theo cụm có ví dụ và đối chiếu với từ điển.
""", knowledge="""
Collocation cần được học như một đơn vị có ngữ cảnh: meet a deadline, make a reservation, place an order. Dịch từng từ có thể tạo cụm không tự nhiên.
Phân biệt interested in, responsible for, eligible for và apply for/apply to theo nghĩa. Sau giới từ chọn dạng danh từ hoặc V-ing khi cần.
Thời gian by/until/within/throughout khác nhau: within two days là trong vòng hai ngày; throughout nhấn toàn bộ thời gian. Luôn kiểm tra logic của câu hoàn chỉnh.
""", examples=[("Please place your order by noon.", "Place an order là đặt hàng; by noon là hạn chót."), ("You will receive a reply within two business days.", "Within giới hạn thời gian từ bây giờ, không nói phản hồi kéo dài hai ngày.")], checks=[("The team worked late to ____ the deadline.", ["catch", "meet", "take"], 1, "Cụm tự nhiên là meet a deadline."), ("The warranty is valid ____ one year.", ["during", "within", "for"], 2, "For + khoảng thời gian thể hiện thời hạn hiệu lực một năm.")], practice="""
Luyện 15 câu collocation/giới từ, đánh dấu cả cụm thay vì riêng đáp án.
Tra 5 cụm khó trong từ điển Cambridge, ghi ví dụ do mình viết.
""", homework="""
Tạo 10 thẻ cụm công việc và đặt câu với 5 cụm yếu nhất.
Ôn xen kẽ với buổi 8 để tránh chỉ nhớ vị trí câu trong bài.
""", lessons=["f03", "u03"], sources=["cambridge-dictionary", "bc-reference"], terms=["meet a deadline", "place an order", "make a reservation", "eligible for", "within", "throughout"])

session(1, 22, "Part 1: Mini test · Part 2: A OR B / Statement", "Listening", goals="""
Làm nhóm Part 1 liên tục, hạn chế dừng để dịch.
Hiểu phản hồi either/neither/both/khác lựa chọn cho câu hỏi A or B.
Chọn phản hồi tự nhiên cho câu phát biểu.
""", knowledge="""
Câu hỏi lựa chọn không luôn cần lặp đúng A hoặc B; either, neither hoặc lời giải thích chưa quyết định có thể phù hợp. Yes/no đơn lẻ thường không giải quyết rõ câu lựa chọn.
Statement có thể thông báo vấn đề, bày tỏ ý kiến hoặc báo việc đã làm. Phản hồi có thể đề nghị giúp, hỏi thêm hoặc ghi nhận thông tin, tùy mục đích.
Mini test dùng để quan sát lỗi sau lượt nghe đầu. Chỉ mở transcript khi đã chốt câu trả lời; điểm tăng sau khi thuộc audio không phải bằng chứng tiến bộ trên nội dung mới.
""", examples=[("Should we send it by mail or courier? — Courier would be faster.", "Chọn phương án và nêu lý do."), ("The printer has run out of paper. — I'll get some from storage.", "Phản hồi đề nghị giải quyết vấn đề được nêu.")], checks=[("'Would you prefer Monday or Tuesday?' — 'Either is fine.' nghĩa gì?", ["Chỉ thứ Hai phù hợp.", "Cả hai đều không phù hợp.", "Ngày nào trong hai ngày cũng được."], 2, "Either is fine chấp nhận một trong hai phương án."), ("'I can't find the visitor list.' — câu đáp phù hợp?", ["Have you checked the front desk?", "There are five visitors.", "It was a pleasant visit."], 0, "Gợi ý nơi tìm giúp giải quyết vấn đề; hai đáp án còn lại chỉ gần chủ đề.")], practice="""
Làm Part 1 trong DHV: 6 câu, lần đầu chỉ nghe một lượt; ghi kết quả trước khi chữa.
Luyện 10 câu lựa chọn/statement và phân loại chức năng phản hồi.
""", homework="""
Viết 5 statement kèm lời đáp hữu ích, 5 câu lựa chọn có either/neither.
Ghi ba bẫy đã gặp và cách nhận ra chúng trên một câu mới.
""", lessons=["b01", "b02", "i01"], sources=["ets", "bc-listening"], terms=["either", "neither", "courier", "run out of", "storage", "prefer"])

session(1, 23, "Part 5 · Khoảng trống đầu câu và chọn nghĩa", "Reading", goals="""
Xác định thành phần còn thiếu ở đầu câu thay vì dùng mẹo vị trí.
Chọn từ nối theo cấu trúc và quan hệ logic.
Đọc ngữ cảnh để chọn nghĩa phù hợp khi mọi đáp án cùng từ loại.
""", knowledge="""
Khoảng trống đầu câu có thể là chủ ngữ, liên từ, giới từ hoặc trạng từ nối. Dấu phẩy và cấu trúc phía sau giúp xác định, nhưng không có quy tắc cứ đầu câu là liên từ.
Because + clause khác because of + noun phrase; however là trạng từ nối và cần dấu câu phù hợp. Kiểm tra cả số mệnh đề chính lẫn quan hệ nguyên nhân/tương phản.
Với câu từ vựng, đọc toàn câu tìm người/vật, hành động, sắc thái và collocation. Tránh chọn từ có nghĩa tiếng Việt gần nhất mà bỏ điều kiện cụ thể.
""", examples=[("Despite a short delay, the workshop finished on time.", "Cụm danh từ sau chỗ trống và quan hệ tương phản phù hợp Despite."), ("The hotel will waive the cancellation fee.", "Waive là miễn khoản phí, không phải hoãn thanh toán hay tăng phí.")], checks=[("____ the system was offline, staff used paper forms.", ["Because", "Because of", "During"], 0, "Sau chỗ trống là mệnh đề system was offline, dùng Because."), ("Customers can ____ a full refund if the item is faulty.", ["attend", "request", "arrive"], 1, "Request a refund là yêu cầu hoàn tiền, phù hợp chủ thể và tân ngữ.")], practice="""
Luyện 15 câu trộn từ nối và từ vựng; viết cấu trúc phía sau chỗ trống.
Tạo sơ đồ xử lý Part 5 cá nhân: từ loại → động từ/đại từ → cụm từ → nghĩa.
""", homework="""
Ôn các nhóm lỗi còn lại của Level 1, chọn 3 nhóm ưu tiên cho buổi tổng kết.
Viết 8 câu dùng từ mới trong ngữ cảnh hoàn tiền, lịch hẹn và công việc.
""", lessons=["i03", "u03", "f03"], sources=["bc-b1", "cambridge-dictionary"], terms=["despite", "however", "therefore", "waive", "refund", "faulty"])

session(1, 24, "Final test Level 1 · Chẩn đoán và kế hoạch ôn", "Assessment", goals="""
Đánh giá lại cấu trúc cơ bản và khả năng nghe/đọc lần đầu.
Phân biệt lỗi kiến thức, nghe âm, suy luận và quản lý thời gian.
Quyết định học tiếp hay bổ sung buổi ôn theo bằng chứng.
""", knowledge="""
Dùng khảo sát 25 câu của DHV như bài rà soát nội bộ, không gọi là đề TOEIC rút gọn chuẩn hóa. Bài có cả Part 3–7 để giúp nhìn thấy phần sắp học; người mới không cần hiểu hết các phần đó.
Sau khi nộp, xem riêng nhóm Part 1, 2, 5 và lỗi ngữ pháp đã học. Nếu gặp lại câu cũ, ghi rõ đã quen và bổ sung bài mới ở nguồn hợp lệ trước khi quyết định xếp level.
Mỗi lỗi phải có nguyên nhân và hành động: không biết từ → học cụm; nghe sai → đối chiếu âm; sai cấu trúc → ôn đúng buổi; suy diễn → tìm câu bằng chứng. Có thể học lại từng phần, không phải làm lại mọi buổi.
""", examples=[("Tôi chọn sai vì không nghe được thirteen, không phải vì không biết cách hỏi giờ.", "Kế hoạch sửa là luyện cặp âm/số và cụm thời gian, không chỉ đọc thêm ngữ pháp."), ("Tôi đúng câu này vì đã nhớ đáp án từ tuần trước.", "Ghi là câu đã quen; không dùng nó làm bằng chứng độc lập cho năng lực hiện tại.")], checks=[("Khảo sát nội bộ đạt 80% có nghĩa gì?", ["Đã chắc chắn đạt 800 TOEIC.", "Đúng 80% trên bộ câu đã làm; cần xem kỹ năng và độ mới của đề.", "Không cần học thêm."], 1, "Phần trăm nội bộ không phải điểm TOEIC chuẩn hóa."), ("Sau một câu sai, hành động nào hữu ích nhất?", ["Chép riêng chữ cái đáp án.", "Bỏ qua vì đề khó.", "Ghi nguyên nhân, bằng chứng đúng và bài ôn tương ứng."], 2, "Nhật ký lỗi có hành động giúp sửa kiến thức và thói quen cụ thể.")], practice="""
Làm khảo sát 25 câu/25 phút tại Góc luyện tập; không mở tài liệu trong lượt đầu.
Dùng 45 phút chữa bài và 20 phút lập kế hoạch ôn; nếu cần, dùng bài mới tại nguồn chính thức để kiểm tra lại.
""", homework="""
Ôn ba nhóm yếu trong tuần, làm lại câu tự viết khác sau 3–7 ngày.
Trước Level 2, giải thích được các lỗi cơ bản về từ loại, chủ ngữ và thể động từ.
""", lessons=["f02", "b01", "b02", "b03"], sources=["ets", "format", "cambridge"], terms=["accuracy", "evidence", "review", "weakness", "timing", "progress"], checkpoint="Final Level 1: tổng hợp sổ lỗi, kiểm tra tiêu chí chuyển level; cho phép thêm buổi ôn theo nhu cầu.")

session(2, 1, "Part 5 · Mệnh đề quan hệ và cụm giới từ", "Reading", goals="""
Chọn who/which/that/whose/where theo chức năng trong mệnh đề.
Phân biệt mệnh đề quan hệ với cụm giới từ bổ nghĩa danh từ.
Tìm động từ chính trong câu có nhiều cụm bổ nghĩa.
""", knowledge="""
Mệnh đề quan hệ bổ sung thông tin cho danh từ: who thường thay người, which thay vật, whose chỉ sở hữu. Xác định đại từ làm chủ ngữ hay tân ngữ trong mệnh đề, không chỉ nhìn danh từ đứng trước.
Where biểu đạt quan hệ nơi chốn, còn which có thể làm chủ ngữ/tân ngữ: the office where we work khác the office which we rent. Không chọn where chỉ vì danh từ là địa điểm.
Cụm giới từ như in charge of sales không có động từ chia thì và có thể chen giữa chủ ngữ với động từ chính. Mệnh đề không xác định được ngăn bởi dấu phẩy; không dùng that theo cách đang luyện trong mệnh đề này.
""", examples=[("The assistant who manages bookings is on leave.", "Who làm chủ ngữ của manages; is là động từ chính của cả câu."), ("The room which we reserved is beside reception.", "Which là tân ngữ của reserved, không dùng where để thay tân ngữ này.")], checks=[("The employee ____ desk is near the window handles returns.", ["who", "whose", "whom"], 1, "Whose + desk diễn tả sở hữu."), ("The warehouse ____ we store supplies is being renovated.", ["where", "which", "whose"], 0, "We store supplies có đủ tân ngữ; cần quan hệ nơi chốn where.")], practice="""
Luyện 15 câu quan hệ/cụm giới từ; gạch động từ chính và động từ mệnh đề phụ.
Viết lại 6 cặp câu thành mệnh đề quan hệ, chỉ ra vai trò đại từ.
""", homework="""
Tìm 5 mệnh đề quan hệ trong nguồn B1–B2, tự viết câu tương tự về công việc.
Ôn Level 1 buổi 3/8/11 nếu còn nhầm clause với noun phrase.
""", lessons=["i03", "f02"], sources=["bc-relative", "bc-reference"], terms=["whose", "in charge of", "on leave", "located in", "responsible for", "reservation"])

session(2, 2, "Part 6–7 · Cấu trúc bài và kỹ năng tìm từ khóa", "Reading", goals="""
Nhận biết dạng văn bản, người gửi/người nhận và mục đích.
Tìm từ khóa kèm paraphrase, không chỉ dò từ trùng.
Đọc câu trước/sau bằng chứng để tránh chọn sai phạm vi.
""", knowledge="""
Part 6 có các đoạn với chỗ trống về ngữ pháp, từ vựng và câu nối. Part 7 gồm văn bản đơn và nhóm văn bản; xác định dạng tài liệu trước khi đọc chi tiết.
Từ khóa tốt thường là tên riêng, ngày, số, hành động yêu cầu. Đáp án có thể đổi cách diễn đạt: postpone → move to a later date; không trùng từ vẫn đúng nếu cùng nghĩa.
Scan giúp đến vùng thông tin, nhưng quyết định cần đọc cả câu và ngữ cảnh lân cận. Với NOT/EXCEPT, tìm bằng chứng cho ba lựa chọn được nêu, không đoán từ cảm giác.
""", examples=[("Email: 'The workshop has moved from 8 May to 15 May. The venue is unchanged.'", "Ngày thay đổi, địa điểm giữ nguyên; không tự suy ra mọi thông tin đều đổi."), ("Question: 'Why was this email sent?' Answer: 'To announce a revised date.'", "Revised date là paraphrase của moved from…to…; mục đích khác chi tiết về địa điểm.")], checks=[("Thông báo nói 'The deadline has been extended to Friday.' Cách diễn đạt tương đương?", ["The deadline was cancelled.", "The work must start on Friday.", "There is more time to submit the work."], 2, "Extended deadline là có thêm thời gian nộp."), ("Sau khi tìm được từ khóa trùng đáp án, nên làm gì?", ["Chọn ngay.", "Đọc cả câu và ngữ cảnh để kiểm tra nghĩa/phạm vi.", "Bỏ qua câu hỏi."], 1, "Từ trùng chỉ là dấu định vị, không tự chứng minh đáp án.")], practice="""
Làm một đoạn Part 6 (4 câu) và hai văn bản đơn Part 7; ghi bằng chứng từng câu.
Lập 8 cặp paraphrase từ lời giải và dùng chúng trong câu mới.
""", homework="""
Đọc hai email công việc ngắn từ bài hỗ trợ, tóm tắt ai–việc gì–khi nào.
Làm lại một văn bản đã chữa bằng cách giải thích vì sao ba lựa chọn sai.
""", lessons=["i04", "b04", "u04"], sources=["format", "ets", "cambridge"], terms=["postpone", "extend", "revised", "venue", "purpose", "deadline"])

session(2, 3, "Part 1–2 · Loại trừ và dạng WHAT", "Listening", goals="""
Loại một phương án vì chi tiết cụ thể sai, không vì cảm giác.
Phân biệt what time, what kind, what…for và câu hỏi ý kiến.
Hiểu phản hồi gián tiếp cho câu hỏi WHAT.
""", knowledge="""
Với Part 1, kiểm tra chủ thể–động tác–vị trí; chỉ một chi tiết không khớp cũng đủ loại. Đừng loại một từ chưa biết nếu chưa hiểu toàn mô tả.
What time hỏi giờ, what kind hỏi loại, what…for có thể hỏi mục đích. What do you think of…? hỏi ý kiến; đáp án cần đánh giá chứ không chỉ lặp danh từ.
Loại trừ cần đi cùng bằng chứng nghe được. Nếu không chắc, chọn phương án giải quyết câu hỏi tốt nhất rồi tiếp tục, tránh bỏ lỡ câu sau vì cố nhớ lại câu trước.
""", examples=[("What is this form for? — To request travel expenses.", "Câu hỏi mục đích, đáp án nguyên mẫu to request phù hợp."), ("What do you think of the revised logo? — It's easier to read.", "Ý kiến đánh giá thiết kế, không phải thông tin về giờ hay người vẽ.")], checks=[("'What time does the reception open?' — đáp án phù hợp?", ["At eight thirty.", "The main reception.", "A new receptionist."], 0, "What time yêu cầu giờ."), ("'What kind of accommodation do you need?' hỏi gì?", ["Ngày nhận phòng.", "Loại chỗ ở cần tìm.", "Tên người đặt phòng."], 1, "What kind of hỏi loại, không hỏi thời gian hoặc danh tính.")], practice="""
Luyện 6 hình và 12 câu WHAT, ghi một lý do loại cho từng phương án sai.
Nghe lại 5 câu khó theo cụm, phân biệt sai vì âm và sai vì chức năng.
""", homework="""
Viết 8 câu WHAT thuộc bốn dạng khác nhau kèm câu đáp tự nhiên.
Nghe một đoạn A2 tại British Council, ghi ba câu hỏi phù hợp nội dung.
""", lessons=["b01", "b02", "i01"], sources=["bc-a2-listening", "ets"], terms=["what kind", "what for", "expense", "accommodation", "opinion", "readable"])

session(2, 4, "Part 3–4 · Cấu trúc bài và nghe từ khóa", "Listening", goals="""
Đọc trước ba câu hỏi để biết thông tin cần nghe.
Theo dõi người nói, vấn đề, giải pháp và bước tiếp theo.
Phân biệt từ khóa với nghĩa được diễn đạt lại.
""", knowledge="""
Part 3 là hội thoại; Part 4 là bài nói một người. Mỗi nhóm có ba câu hỏi trong cấu trúc hiện hành; giữ cả nhóm khi luyện để hiểu mạch.
Trước audio, đọc nhanh câu hỏi và dự đoán cần nơi chốn, lý do, ý định hay hành động. Trong audio, theo dõi chuyển ý và thông tin sửa lại: actually, instead, however.
Không cần ghi tất cả từ nghe được. Sơ đồ ai → vấn đề → cách xử lý → bước tiếp theo giúp nhớ ý và tránh chọn đề xuất đã bị bác bỏ.
""", examples=[("A: The delivery is late. B: I'll call the supplier. A: Please ask for the new arrival time.", "B sẽ gọi nhà cung cấp để hỏi giờ đến; chưa có bằng chứng hàng đã được gửi lại."), ("'The meeting has moved upstairs. Please use the lift on the left.'", "Thông báo thay địa điểm và hướng dẫn hành động, không nói cuộc họp bị hủy.")], checks=[("Người nói: 'Nine won't work. Let's meet at ten instead.' Giờ được chốt?", ["9 giờ.", "Chưa có giờ nào.", "10 giờ."], 2, "Instead đánh dấu lựa chọn thay thế được đề nghị/chốt trong câu."), ("Trước khi nghe nhóm Part 3, việc hữu ích nhất là gì?", ["Đọc trước ba câu hỏi và xác định loại thông tin cần tìm.", "Dịch toàn bộ đáp án từng từ.", "Đoán đáp án theo độ dài."], 0, "Đọc có mục tiêu giúp theo dõi mạch và chi tiết cần thiết.")], practice="""
Luyện hai nhóm Part 3 và hai nhóm Part 4, lần đầu nghe một lượt không dừng.
Sau khi chữa, vẽ sơ đồ vấn đề–giải pháp–hành động và ghi 6 cặp paraphrase.
""", homework="""
Chép 20–30 giây khó nhất của một audio; đối chiếu transcript rồi đọc theo.
Ôn các lỗi của buổi 1–4 và chọn một kỹ năng ưu tiên cho tuần sau.
""", lessons=["i02", "u02"], sources=["format", "bc-b1-listening", "ets"], terms=["instead", "actually", "supplier", "arrival", "reschedule", "next step"], checkpoint="Mốc Level 2 buổi 4: nhận đúng cấu trúc và tìm bằng chứng ở cả đọc/nghe, chưa ép tốc độ cao.")

session(2, 5, "Part 5 · Rút gọn mệnh đề quan hệ và trạng ngữ", "Reading", goals="""
Rút gọn quan hệ theo nghĩa chủ động hoặc bị động khi phù hợp.
Kiểm tra chủ thể chung trước khi rút gọn mệnh đề trạng ngữ.
Nhận ra lỗi phân từ không có chủ thể phù hợp.
""", knowledge="""
Với quan hệ chủ động có thể dùng V-ing khi ngữ cảnh phù hợp: employees who work remotely → employees working remotely. Quan hệ bị động có thể dùng V3: forms that are attached → forms attached.
Không phải cứ thấy who/which là xóa và thêm -ing: khi đại từ làm tân ngữ, có quy tắc lược đại từ khác. Phải giữ nghĩa, quan hệ thời gian và vai trò danh từ.
Phần thường gọi 'rút gọn chủ ngữ' ở đây là rút gọn mệnh đề trạng ngữ: chủ thể ngầm của cụm phân từ phải phù hợp chủ ngữ mệnh đề chính. 'Walking to work, the rain started' sai ý vì rain không đi bộ. Having + V3 có thể nhấn việc hoàn tất trước hành động chính.
""", examples=[("The files stored on this drive are encrypted.", "Stored rút gọn bị động từ files that are stored; are encrypted vẫn là động từ chính."), ("After checking the figures, Lan sent the report.", "Lan vừa kiểm tra vừa gửi; chủ thể của hai hành động thống nhất.")], checks=[("The customers ____ near the entrance need assistance.", ["waited", "waiting", "were waited"], 1, "Customers chủ động chờ, dùng waiting bổ nghĩa."), ("Câu rút gọn nào có chủ thể hợp lý?", ["Driving to the office, the rain became heavy.", "Reviewing the form, a mistake appeared.", "After reviewing the form, Mai corrected a mistake."], 2, "Mai là người review và correct; hai câu kia gán hành động cho rain/mistake.")], practice="""
Rút gọn 8 câu quan hệ, viết lại dạng đầy đủ để kiểm tra nghĩa.
Sửa 5 câu có cụm phân từ sai chủ thể, giải thích ai thực hiện từng hành động.
""", homework="""
Viết 4 câu quan hệ rút gọn và 4 mệnh đề trạng ngữ rút gọn với chủ thể rõ.
Đọc phần participle clauses tại nguồn, tự làm ví dụ mới thay vì chép câu mẫu.
""", lessons=["i03", "u03"], sources=["bc-relative", "bc-participles"], terms=["attached", "stored", "working remotely", "having completed", "encrypted", "assistance"])

session(2, 6, "Part 6: Điền câu · Part 7: Double passage", "Reading", goals="""
Chọn câu nối phù hợp cả câu trước và câu sau.
Xác định vai trò và ngày của hai văn bản.
Ghép hai bằng chứng để giải câu hỏi đối chiếu.
""", knowledge="""
Câu điền phải đúng chủ đề, tham chiếu và quan hệ logic. This change/these items/therefore cần thông tin phù hợp ở trước; câu cùng chủ đề nhưng không nối mạch vẫn sai.
Với hai văn bản, ghi nhanh văn bản A đặt quy định/đề nghị, văn bản B xác nhận hoặc cập nhật. Chỉ thay thông tin được nói rõ, không hủy mọi điều kiện cũ.
Câu hỏi cross-reference cần bằng chứng từ cả hai nguồn. Đọc kỹ ngày hiệu lực, đối tượng và điều kiện trước khi suy luận hoặc tính tiền.
""", examples=[("A: 'Orders placed before 10 June receive free delivery.' B: 'I placed my order on 8 June.'", "Đơn đặt trước hạn nên thỏa điều kiện ngày cho miễn phí giao; không cần biết ngày nhận để trả lời điều kiện này."), ("'The entrance will move to the east side. [Gap] These signs will remain for one week.'", "Câu chèn cần giới thiệu signs, ví dụ 'We will put up signs to guide visitors.'")], checks=[("Thông báo giảm 10% cho đơn trước 12/6. Email đặt hàng ngày 14/6. Kết luận có căn cứ?", ["Không đủ điều kiện ngày cho ưu đãi này.", "Chắc chắn được giảm.", "Đơn hàng đã bị hủy."], 0, "14/6 sau hạn; chỉ kết luận không thỏa điều kiện, không suy ra bị hủy."), ("Câu sau chỗ trống là 'This option is available at no extra cost.' Câu trước phù hợp nhất?", ["The office closes at six.", "Customers can choose electronic receipts.", "Thank you for last year's order."], 1, "Electronic receipts giới thiệu một option mà this option có thể tham chiếu.")], practice="""
Làm hai đoạn Part 6 và một nhóm hai văn bản; ghi nguồn A/B cho từng đáp án.
Với câu điền, đọc lại toàn đoạn sau khi chọn để kiểm tra tham chiếu.
""", homework="""
Tự viết cặp thông báo–email 120 từ có một cập nhật; đặt ba câu hỏi và đáp án có bằng chứng.
Ôn 6 từ nối/tham chiếu trong câu, không học riêng bản dịch.
""", lessons=["i04", "a02", "a03"], sources=["ets", "bc-b1", "cambridge"], terms=["this change", "these items", "therefore", "eligible", "confirmation", "updated"])

session(2, 7, "Part 1–2 · Tả người/vật và các bẫy nghe", "Listening", goals="""
Phân loại lỗi mô tả chủ thể, hành động, vị trí và trạng thái.
Nhận ra bẫy âm gần giống, từ lặp và sai chức năng đáp lời.
Hiểu phản hồi gián tiếp mà không suy diễn quá mức.
""", knowledge="""
Một lựa chọn có thể chứa đúng danh từ trong hình nhưng sai động từ. So cả quan hệ không gian và số người/vật; are being repaired cần hành động sửa đang diễn ra.
Trong Part 2, âm gần giống và lặp từ chỉ đánh lạc hướng nếu ý đáp không phù hợp. Phản hồi 'Ask the supervisor' có thể hợp câu hỏi thông tin mà người nói không biết.
Khi câu hỏi là lời nhờ/đề nghị, chọn phản hồi giải quyết chức năng đó. Ghi lỗi theo nguyên nhân để chọn bài ôn âm hoặc bài ôn nghĩa thích hợp.
""", examples=[("'Who approved the budget?' — 'The director did.'", "Did thay cho approved the budget; câu đáp không cần lặp đầy đủ động từ."), ("'Could you unlock the cabinet?' — 'I'll get the key.'", "Đáp gián tiếp thể hiện chuẩn bị thực hiện lời nhờ.")], checks=[("'Where can I get a parking permit?' — đáp nào giải quyết câu hỏi?", ["The park is beautiful.", "It was permitted yesterday.", "Ask the security office."], 2, "Chỉ dẫn đúng nơi hỗ trợ; park/permitted chỉ giống âm hoặc gốc từ."), ("Thấy các xe đạp tựa vào tường, không có người. Mô tả phù hợp?", ["Bicycles are leaning against a wall.", "People are riding bicycles.", "Bicycles are being loaded onto a truck."], 0, "Leaning against mô tả trạng thái quan sát; các hành động khác không có bằng chứng.")], practice="""
Luyện 6 câu Part 1 và 15 câu Part 2 trộn dạng; không chia sẵn nhóm câu hỏi.
Với mỗi lỗi, viết nhãn âm/ý/chức năng/phạm vi và câu đáp tương đương đúng.
""", homework="""
Nghe lại 5 lỗi âm với transcript, sau đó nghe một bài mới để kiểm tra chuyển giao.
Ôn 10 cụm động từ mô tả người và đồ vật.
""", lessons=["b01", "b02", "i01"], sources=["ets", "bc-a2-listening"], terms=["permit", "security office", "unlock", "cabinet", "lean against", "approve"])

session(2, 8, "Part 3–4 · Shopping, Office, Advertisement", "Listening", goals="""
Nhận biết đổi trả, lịch công việc và lời quảng cáo.
Theo dõi điều kiện ưu đãi, lý do liên hệ và hành động yêu cầu.
Ghi cặp paraphrase theo chủ đề thay vì chỉ danh sách từ.
""", knowledge="""
Shopping thường có hàng lỗi, biên lai, tồn kho, đổi trả. Phân biệt refund với exchange và điều kiện áp dụng; việc khách yêu cầu chưa có nghĩa cửa hàng đã đồng ý.
Office thường xoay quanh lịch họp, nhân sự, thiết bị hoặc công việc đang chậm. Tách nguyên nhân khỏi giải pháp và xác định ai nhận trách nhiệm cuối.
Advertisement thường nêu đối tượng, lợi ích, điều kiện và cách đăng ký. Chú ý limited to, while supplies last, members only: quảng cáo không có nghĩa ai cũng nhận mọi ưu đãi.
""", examples=[("'Members who order online by Friday receive free installation.'", "Ba điều kiện cần theo dõi: là thành viên, đặt online và đúng hạn."), ("'The copier is broken, so send the handouts by email instead.'", "Nguyên nhân là máy hỏng; hành động được yêu cầu là gửi email.")], checks=[("'I'd like an exchange, not a refund.' Người nói muốn gì?", ["Đổi sang sản phẩm khác.", "Lấy lại tiền.", "Hủy mọi giao dịch."], 0, "Exchange là đổi hàng; refund là hoàn tiền."), ("'The offer is for members only.' Ai được hưởng?", ["Mọi khách tới cửa hàng.", "Khách có tư cách thành viên.", "Chỉ nhân viên cửa hàng."], 1, "Only giới hạn đối tượng vào members.")], practice="""
Luyện ba nhóm hội thoại/bài nói thuộc shopping, office và quảng cáo; mỗi nhóm ba câu.
Tóm tắt mỗi audio bằng bốn ô: người, vấn đề, điều kiện, hành động.
""", homework="""
Học 12 cụm theo ba chủ đề, mỗi cụm kèm paraphrase và câu ví dụ.
Nghe một bài B1 mới, ghi kết quả lượt đầu và lỗi cần ôn.
""", lessons=["i02", "u02", "a01"], sources=["bc-b1-listening", "ets"], terms=["exchange", "refund", "receipt", "in stock", "handout", "members only"], checkpoint="Mốc Level 2 buổi 8: kiểm tra điều kiện và hành động ở cả nghe/đọc; không chỉ nhận ra chủ đề chung.")

session(2, 9, "Part 5 · Từ chỉ số lượng và ôn hỗn hợp", "Reading", goals="""
Chọn quantifier theo danh từ đếm được/không đếm được.
Phân biệt few/a few và little/a little về sắc thái.
Giải bài hỗn hợp mà không biết trước dạng ngữ pháp.
""", knowledge="""
Many/few/several đi với danh từ đếm được số nhiều; much/little đi với danh từ không đếm được. Some/any/a lot of có phạm vi rộng hơn nhưng vẫn cần xét câu và nghĩa.
Few/little thường nhấn ít đến mức thiếu; a few/a little nhấn có một ít. A number of + plural noun thường đi với động từ số nhiều; the number of chỉ một con số nên thường đi với động từ số ít.
Each/every + danh từ số ít; all/both có thể dùng với số nhiều. Đọc danh từ trung tâm và ý nghĩa, đừng chọn chỉ vì nhìn thấy từ of.
""", examples=[("A few seats are still available, so we can accept more bookings.", "Có một ít ghế, sắc thái đủ để tiếp tục nhận khách."), ("The number of complaints has fallen.", "Chủ ngữ là number số ít, dù complaints số nhiều.")], checks=[("We have ____ time left, so we must hurry.", ["many", "little", "a few"], 1, "Time không đếm được; little phù hợp ý gần hết thời gian."), ("A number of employees ____ requested new uniforms.", ["has", "is", "have"], 2, "A number of employees mang nghĩa nhiều nhân viên, đi với have.")], practice="""
Luyện 12 câu lượng từ, rồi 18 câu trộn từ loại/động từ/đại từ/liên từ.
Phân loại câu trước khi chữa, so sánh loại lỗi với kết quả Level 1.
""", homework="""
Viết 8 câu phân biệt few/a few/little/a little và number of.
Ôn ba nhóm lỗi phổ biến nhất, đặt ví dụ mới khác ngữ cảnh bài đã làm.
""", lessons=["f02", "b03", "u03"], sources=["bc-reference", "bc-grammar"], terms=["several", "a few", "little", "a number of", "the number of", "remaining"])

session(2, 10, "Part 7 · Triple passage", "Reading", goals="""
Tóm tắt chức năng và thời điểm của ba văn bản.
Đối chiếu yêu cầu, xác nhận và cập nhật cuối.
Phân biệt thay thế với bổ sung trước khi tính số lượng.
""", knowledge="""
Đọc tiêu đề/người gửi/ngày để tạo bản đồ: A quảng cáo/quy định; B yêu cầu/đơn đặt; C xác nhận/cập nhật. Không cần dịch toàn bộ trước khi xem câu hỏi.
Với thay đổi, hỏi thay mục nào, áp dụng từ khi nào, điều nào vẫn giữ. Add two khác replace two; requested khác confirmed.
Mỗi câu hỏi kết hợp cần ít nhất hai bằng chứng rõ. Với số tiền hoặc lượng, ghi phép tính và điều kiện; nếu dữ kiện chưa đủ thì không tự cộng.
""", examples=[("A: Lunch costs $12 per person. B: Book lunch for 20 people. C: Please add 2 guests; all will have the same lunch.", "Số cuối là 22; nếu không có phí khác được nêu, chi phí phần ăn là 22 × 12 = $264."), ("B: We ordered 20 lunches, including 4 vegetarian. C: Replace 2 regular lunches with vegetarian ones.", "Tổng vẫn 20; chay thành 6, không tăng tổng lên 22.")], checks=[("Đặt 30 ghế, email cuối yêu cầu 'add five more chairs'. Tổng là bao nhiêu?", ["25", "30", "35"], 2, "Add nghĩa bổ sung: 30 + 5 = 35."), ("Văn bản cuối chỉ đổi địa điểm; không nói đổi giờ. Xử lý giờ cũ thế nào?", ["Giữ giờ cũ nếu không có bằng chứng khác.", "Tự đổi sang giờ ở tiêu đề email.", "Cho rằng sự kiện bị hủy."], 0, "Chỉ cập nhật trường thông tin được nêu rõ.")], practice="""
Làm hai nhóm ba văn bản; đặt ngân sách thời gian rồi ghi A/B/C cạnh bằng chứng.
Kiểm tra lại 3 câu cần nối nguồn, nhất là các từ add/replace/confirm/request.
""", homework="""
Tạo bảng ai–việc–ngày–điều kiện cho một nhóm văn bản đã học.
Viết 5 paraphrase từ câu hỏi sang bằng chứng và ôn sau 3 ngày.
""", lessons=["a03", "a04"], sources=["ets", "format"], terms=["add", "replace", "confirm", "request", "including", "additional"])

session(2, 11, "Part 1–2 · Ôn tích hợp và đáp lời gián tiếp", "Listening", goals="""
Giữ nhịp nghe qua nhiều dạng câu hỏi liên tiếp.
Hiểu câu đáp gián tiếp theo nhu cầu giao tiếp.
Phân tích lỗi theo nhóm âm, cấu trúc và ý nghĩa.
""", knowledge="""
Luân phiên các dạng WHERE/WHEN/WHO/WHICH/WHAT/HOW/WHY, Yes/No, lựa chọn và statement để tránh đoán theo nhãn bài. Trong lúc làm chỉ nghe audio, không dựa vào bản chữ.
Phản hồi gián tiếp có thể chỉ nơi tìm thông tin, nêu lý do chưa làm, đưa phương án khác hoặc sửa giả định. Chỉ suy ra điều được tình huống hỗ trợ.
Nếu lỡ một câu, chốt lựa chọn rồi quay lại nghe câu mới; giữ sự chú ý quan trọng hơn cố giải lại bằng trí nhớ khi audio tiếp tục.
""", examples=[("'Can we meet in Room 3?' — 'A training session is using it all morning.'", "Phòng chưa sẵn trong sáng nay; không đủ căn cứ nói phòng vĩnh viễn đóng."), ("'Who will collect the visitor?' — 'I've already arranged a taxi.'", "Câu đáp đưa cách xử lý thay vì tên người; chưa chỉ ra ai trong công ty sẽ đón.")], checks=[("'Why hasn't the report been sent?' — 'We're waiting for approval.' Hàm ý?", ["Báo cáo đã gửi.", "Chưa gửi vì chưa có phê duyệt.", "Báo cáo không tồn tại."], 1, "Lý do trì hoãn được nêu trực tiếp; không suy ra tài liệu chưa được viết."), ("Khi lỡ một câu và câu tiếp theo bắt đầu, nên làm gì?", ["Tiếp tục nghĩ câu cũ đến khi nhớ ra.", "Bỏ luôn vài câu để nghỉ.", "Chốt lựa chọn, tập trung vào câu mới."], 2, "Giữ nhịp tránh một lỗi kéo theo chuỗi lỗi mất tập trung.")], practice="""
Làm 6 câu Part 1 và hai lượt Part 2 trộn dạng; đánh dấu câu đã gặp để phân biệt với câu mới.
Sau chữa, chọn 5 lỗi nghe âm để đọc theo và 5 lỗi ý nghĩa để diễn giải.
""", homework="""
Nghe bài A2/B1 mới 10–15 phút, tóm tắt bằng tiếng Việt rồi đối chiếu transcript.
Tự kiểm tra lại năm nhóm câu hỏi còn yếu trước buổi 12.
""", lessons=["b01", "b02", "i01"], sources=["ets", "bc-b1-listening"], terms=["approval", "arrange", "alternative", "available", "already", "not yet"])

session(2, 12, "Part 3–4 · Announcement, Lease và tổng kết", "Listening", goals="""
Hiểu thông báo thay đổi, yêu cầu và điều kiện thuê.
Phân biệt phí cọc, tiền thuê, gia hạn và nghĩa vụ thông báo.
Tổng kết Level 2 bằng kế hoạch luyện và ôn theo Part.
""", knowledge="""
Announcement thường có mục đích, thay đổi và việc người nghe cần làm. Chú ý until/from/effective, địa điểm cũ/mới và nhóm người áp dụng.
Lease/rental liên quan deposit, monthly rent, maintenance, renewal và notice. Deposit không tự động là khoản phí không hoàn lại; điều kiện hoàn trả phải có trong bài.
Buổi này giữ trọng tâm nghe của khung gốc. Bài 200 câu/120 phút là hoạt động tổng kết riêng sau buổi, kèm một lượt chữa; chế độ DHV cho nghe lại nên cần tự tuân thủ một lượt nghe nếu muốn luyện sức bền.
""", examples=[("'The lift will be unavailable until Friday. Please use the west staircase.'", "Nghe thời gian hạn chế và tuyến đi thay thế; không hiểu là tòa nhà đóng cửa."), ("'The deposit is refundable if the apartment is returned undamaged.'", "Hoàn cọc có điều kiện; không suy ra ai cũng mất cọc hoặc ai cũng được hoàn ngay.")], checks=[("'Please give thirty days' notice before moving out.' Yêu cầu là gì?", ["Báo trước 30 ngày khi chuyển đi.", "Chỉ được ở 30 ngày.", "Trả tiền thuê mỗi 30 giờ."], 0, "Notice là thông báo trước, không phải thời hạn thuê tối đa."), ("Một thông báo nói 'Only residents of Building B are affected.' Ai bị ảnh hưởng?", ["Tất cả cư dân.", "Cư dân tòa B.", "Chỉ khách vãng lai."], 1, "Only giới hạn phạm vi cụ thể vào Building B.")], practice="""
Luyện hai bài thông báo và hai hội thoại thuê; ghi ai–thay đổi–điều kiện–hành động.
Dành cuối buổi tổng hợp lỗi của 12 buổi, chọn Part cần ưu tiên ở Level 3.
""", homework="""
Làm bài 200 câu/120 phút vào một buổi riêng nếu đã sẵn sàng; chữa theo từng Part vào ngày sau.
Nếu một Part còn dưới 60% trên câu mới, bổ sung 2–3 buổi ôn mục tiêu trước khi tăng tốc.
""", lessons=["i02", "u02", "a01"], sources=["ets", "bc-b1-listening", "iig"], terms=["lease", "deposit", "monthly rent", "renewal", "notice", "maintenance"], checkpoint="Tổng kết Level 2: đủ 7 Part, có sổ lỗi và đề luyện riêng; không quy đổi tỷ lệ đúng của ngân hàng DHV thành điểm thi.")

session(3, 1, "Part 2 · Ý ngầm, phủ định và đề nghị", "Listening", goals="""
Giải thích ý ngầm bằng tình huống và câu bằng chứng.
Phân biệt câu hỏi thật với lời đề nghị/yêu cầu.
Không nhầm chưa biết với phủ nhận một sự việc.
""", knowledge="""
I haven't heard yet cho biết người nói chưa có thông tin, không chứng minh sự kiện bị hủy. Đáp án đúng phải giữ mức độ chắc chắn như audio.
Câu hỏi phủ định, câu hỏi đuôi và lời đề nghị đòi hỏi nghe toàn câu đáp. Could you…/Would you mind… thường kiểm tra chức năng giao tiếp hơn là khả năng thể chất.
""", examples=[("'Has the contract been signed?' — 'The director is still reviewing it.'", "Có căn cứ hiểu việc ký còn chờ duyệt, không suy ra hợp đồng bị hủy."), ("'Would you mind closing the window?' — 'Not at all.'", "Not at all thể hiện không phiền, nhận lời nhờ trong tình huống này.")], checks=[("'Do you know when the new branch opens?' — 'They're still choosing a location.' Điều hợp lý nhất?", ["Đã mở hôm qua.", "Ngày mở chưa được xác định trong câu đáp.", "Chi nhánh chắc chắn bị hủy."], 1, "Chưa có địa điểm chốt; không có ngày mở được xác nhận."), ("'Why don't we take a taxi?' chủ yếu là gì?", ["Đề nghị đi taxi.", "Câu hỏi ai lái taxi.", "Lệnh cấm đi taxi."], 0, "Why don't we… thường đưa đề xuất.")], practice="""
Luyện 20 câu Part 2 trộn dạng, ghi điều nghe rõ và điều suy ra ở hai cột.
Chữa 5 phản hồi gián tiếp bằng một câu đáp trực tiếp tương đương.
""", homework="""
Nghe B1 trong 15 phút và ghi 5 cách từ chối/đề nghị lịch sự.
Ôn lỗi của “Part 2 · Câu đáp gián tiếp và ý ngầm” sau 3 ngày, dùng câu mới để kiểm tra lại.
""", lessons=["i01", "b02"], sources=["bc-b1-listening", "ets"], terms=["still reviewing", "not at all", "not yet", "would you mind", "suggest", "confirm"])

session(3, 2, "Part 3 · Nhiều người nói và theo dõi thay đổi", "Listening", goals="""
Theo dõi vai trò người nói thay vì chỉ tên riêng.
Phân biệt đề xuất ban đầu với quyết định cuối.
Nhận ra người chịu trách nhiệm cho bước tiếp theo.
""", knowledge="""
Hội thoại có thể có nhiều người; ghi vai trò như người báo lỗi, người xử lý, người phê duyệt. Dùng đại từ và lời gọi tên để theo dõi lượt nói.
Actually/instead/how about thường báo sửa ý hoặc đề xuất khác. Ý cuối không tự động đúng cho mọi câu hỏi: nếu hỏi đề xuất đầu tiên thì vẫn phải dùng thông tin đầu.
""", examples=[("A suggests Monday; B is away; C offers Tuesday; A agrees.", "Cuộc hẹn chốt Tuesday, còn đề xuất ban đầu vẫn là Monday nếu câu hỏi hỏi original suggestion."), ("'I'll ask Minh to send the file.'", "Người nói sẽ nhờ Minh; không khẳng định chính người nói sẽ gửi file.")], checks=[("'I'll ask the receptionist to book a taxi.' Người nói sẽ làm gì trước?", ["Tự lái taxi.", "Đã đặt xe xong.", "Nhờ lễ tân đặt xe."], 2, "Ask someone to do là nhờ, chưa xác nhận việc đã hoàn thành."), ("Nếu hỏi 'What was originally proposed?', nên tìm gì?", ["Đề xuất ban đầu.", "Chỉ câu cuối audio.", "Bất kỳ tên người nào."], 0, "Originally chỉ giai đoạn đầu, khác quyết định cuối.")], practice="""
Luyện 4 nhóm hội thoại; ghi bảng người–đề xuất–quyết định–trách nhiệm.
Chép một đoạn chuyển ý 20 giây, xác định từ làm thay đổi kế hoạch.
""", homework="""
Tóm tắt hai hội thoại mới trong 3 câu, giữ đúng ai làm gì.
Ôn 8 cụm giao việc, đề nghị và xác nhận.
""", lessons=["i02", "u01"], sources=["ets", "bc-b1-listening"], terms=["originally", "instead", "delegate", "confirm", "arrange for", "follow up"])

session(3, 3, "Part 4 · Mục đích, ý định và paraphrase", "Listening", goals="""
Phân biệt mục đích toàn bài với một chi tiết phụ.
Giải câu trích dẫn bằng ngữ cảnh trước/sau.
Nhận diện cách diễn đạt tương đương trong môi trường công việc.
""", knowledge="""
Câu hỏi Why does the speaker say…? cần chức năng của lời nói trong tình huống, không chỉ nghĩa đen. Đọc câu trước và sau trong giai đoạn chữa để tìm ngữ cảnh.
Paraphrase có thể đổi từ loại hoặc cấu trúc: we won't charge extra → no additional fee. Giữ điều kiện, phủ định và mức độ, không coi gần nghĩa là luôn tương đương.
""", examples=[("'We only have ten minutes before closing.'", "Trong ngữ cảnh chọn hàng, có thể nhắc cần quyết định sớm; không tự suy ra cửa hàng sẽ đóng vĩnh viễn."), ("'Your installation fee will be waived.'", "Phí lắp đặt được miễn, không phải lùi ngày nộp.")], checks=[("'At no additional cost' tương đương gì?", ["Có phụ phí nhỏ.", "Không có phí thêm.", "Chưa xác định giá."], 1, "No additional cost nghĩa không thu thêm khoản đó."), ("Để hiểu một câu trích dẫn, nên xem gì?", ["Chỉ từng từ trong câu.", "Chỉ độ dài đáp án.", "Tình huống và câu trước/sau."], 2, "Ý định phụ thuộc ngữ cảnh giao tiếp.")], practice="""
Luyện 4 bài nói, phân biệt mục đích chung/chi tiết/ý định trong từng nhóm.
Ghi 10 cặp paraphrase từ audio và đáp án rồi kiểm tra chúng còn giữ điều kiện không.
""", homework="""
Nghe một bài B2 phù hợp, tóm tắt mục đích và hai chi tiết có bằng chứng.
Đọc theo 30 giây, chú ý trọng âm và các từ chức năng dễ bỏ sót.
""", lessons=["u02", "a01"], sources=["bc-b2-listening", "ets"], terms=["waive", "additional fee", "reminder", "provisional", "imply", "urge"])

session(3, 4, "Part 5 · Điều kiện, lượng từ và collocation nâng cao", "Reading", goals="""
Phân biệt điều kiện, ngoại lệ và nguyên nhân.
Chọn collocation theo nghĩa chính xác.
Kiểm tra lỗi nhỏ về lượng từ và phạm vi.
""", knowledge="""
Unless mang nghĩa if not; provided that đặt điều kiện. Với tương lai thực tế, mệnh đề if thường dùng hiện tại, không chọn will theo mốc tương lai một cách máy móc.
Các từ complimentary/complementary, economic/economical khác nghĩa. Đọc danh từ được bổ nghĩa và cả tình huống để chọn; học ví dụ thay vì chỉ bản dịch rời.
""", examples=[("The order will ship provided that payment arrives today.", "Gửi hàng phụ thuộc điều kiện thanh toán trong hôm nay."), ("The hotel offers complimentary breakfast.", "Complimentary ở đây là miễn phí, không phải complementary = bổ sung cho nhau.")], checks=[("The trip will proceed ____ the weather becomes dangerous.", ["unless", "despite", "because of"], 0, "Unless + mệnh đề nêu ngoại lệ: trừ khi thời tiết nguy hiểm."), ("A car that uses little fuel is ____.", ["economic", "economical", "economy"], 1, "Economical diễn tả tiết kiệm trong sử dụng.")], practice="""
Làm 30 câu Part 5 theo ba lượt 10 câu, ghi thời gian và độ đúng từng lượt.
Phân loại lỗi của buổi 1–4 thành âm/nghĩa/cấu trúc/suy diễn để đặt ưu tiên.
""", homework="""
Viết 8 câu điều kiện công việc, gồm unless và provided that.
Ôn 10 cụm nâng cao với câu mới; nếu nghĩa chưa vững, giảm tốc độ luyện.
""", lessons=["u03", "i03"], sources=["bc-b1", "cambridge-dictionary"], terms=["unless", "provided that", "complimentary", "complementary", "economical", "exception"], checkpoint="Mốc Level 3 buổi 4: xem lỗi theo kỹ năng và độ mới của câu; không chỉ so tổng điểm.")

session(3, 5, "Part 6 · Liên kết, tham chiếu và trình tự", "Reading", goals="""
Theo dõi this/these/such và danh từ được nhắc lại.
Chọn từ nối đúng quan hệ và văn phong.
Đặt câu vào mạch thông tin với bằng chứng hai phía.
""", knowledge="""
Tham chiếu không nhất thiết là một danh từ đơn: this decision có thể thay cả quyết định trong câu trước. Đọc nghĩa toàn cụm thay vì tìm một từ giống hệt.
Câu chèn có thể giới thiệu thông tin mới, giải thích hoặc chuyển ý. Một câu đúng ngữ pháp nhưng không nối được câu sau phải bị loại.
""", examples=[("'We will extend the trial by a month. This decision will allow more users to participate.'", "This decision chỉ việc gia hạn, không phải một người hay tháng cụ thể."), ("'Demand increased. Consequently, production was expanded.'", "Consequently nêu kết quả, không phải ý tương phản.")], checks=[("Sau 'Sales fell sharply', câu nối nào thể hiện hệ quả?", ["Nevertheless, the products are blue.", "For example, the office is upstairs.", "Consequently, the company reduced production."], 2, "Giảm sản xuất là hệ quả hợp logic của doanh số giảm trong ví dụ."), ("'Both options are available online' cần trước đó có gì?", ["Hai phương án được giới thiệu rõ.", "Bất kỳ một ngày nào.", "Tên của một nhân viên."], 0, "Both options phải có hai lựa chọn làm tham chiếu.")], practice="""
Làm bốn đoạn Part 6, giữ nhóm 4 câu và đọc lại đoạn hoàn chỉnh sau khi chữa.
Vẽ mạch thông tin mỗi đoạn bằng 3–4 nhãn ngắn.
""", homework="""
Viết đoạn 100 từ có this change/however/therefore, kiểm tra tham chiếu rõ.
Ôn các câu chèn sai bằng cách giải thích vì sao không nối được cả hai phía.
""", lessons=["i04", "a02"], sources=["bc-b1", "ets"], terms=["consequently", "nevertheless", "this decision", "both options", "in addition", "such an arrangement"])

session(3, 6, "Part 7 · Single passage, suy luận và câu NOT", "Reading", goals="""
Tìm thông tin chi tiết mà không bỏ điều kiện/ngoại lệ.
Phân biệt suy luận được hỗ trợ với giả định hợp lý nhưng không có căn cứ.
Giải câu NOT/EXCEPT bằng đối chiếu có hệ thống.
""", knowledge="""
Only, except, at least, no later than thay đổi phạm vi đáp án. Đọc nguyên câu chứa bằng chứng và kiểm tra đối tượng/ngày áp dụng.
Với NOT/EXCEPT, ba lựa chọn thường có căn cứ; tìm lựa chọn không được hỗ trợ theo câu hỏi. Không coi không được nhắc là chắc chắn sai trong đời thực.
""", examples=[("'Members may bring one guest on weekdays.'", "Giới hạn một khách và ngày trong tuần; không áp dụng mặc nhiên vào cuối tuần."), ("'Late applications will be reviewed next month.'", "Vẫn được xem xét muộn hơn, không có nghĩa bị loại vĩnh viễn.")], checks=[("'At least three days' nghĩa là gì?", ["Không quá ba ngày.", "Tối thiểu ba ngày.", "Chính xác một ngày."], 1, "At least đặt mức tối thiểu."), ("Bài không nhắc bãi đỗ xe. Kết luận an toàn?", ["Không có bãi đỗ xe.", "Bãi đỗ xe miễn phí.", "Chưa đủ thông tin về bãi đỗ xe."], 2, "Thiếu thông tin không chứng minh có hoặc không.")], practice="""
Làm 3 văn bản đơn dài hơn, đặt 4–5 phút mỗi nhóm phù hợp độ dài rồi điều chỉnh.
Gạch câu bằng chứng cho từng lựa chọn của hai câu NOT/EXCEPT.
""", homework="""
Đọc một thông báo mới và ghi ba điều kiện có thể làm đổi đáp án.
Viết 5 câu suy luận, nối mỗi câu với bằng chứng cụ thể.
""", lessons=["u04", "b04"], sources=["ets", "cambridge"], terms=["at least", "no later than", "except", "eligible", "restricted", "subject to"])

session(3, 7, "Part 7 · Double passage và đối chiếu giao dịch", "Reading", goals="""
Nối quảng cáo/quy định với email/đơn hàng.
Xử lý ngày, số tiền và điều kiện ưu đãi.
Phân biệt đã yêu cầu với đã được xác nhận.
""", knowledge="""
Lập bảng điều kiện ở nguồn A, dữ kiện khách hàng ở nguồn B. Chỉ áp dụng ưu đãi khi đủ mọi điều kiện được nêu, không chỉ một từ khóa.
Requested/approved/issued/received biểu đạt giai đoạn khác nhau. Yêu cầu hoàn tiền chưa đồng nghĩa tiền đã được chuyển.
""", examples=[("A: 'Free delivery for orders over $100.' B: 'Order total: $95.'", "Không đạt điều kiện giá trị; không được tự cộng khoản không nêu để đạt $100."), ("'Your refund request has been approved; payment will follow next week.'", "Đã duyệt, nhưng chưa trả ngay tại thời điểm thông báo.")], checks=[("Ưu đãi cho đơn 'over $100'. Đơn đúng $100 có đáp ứng điều kiện này không?", ["Không; over nghĩa lớn hơn, không phải bằng.", "Có, luôn luôn.", "Không thể hiểu nghĩa over."], 0, "Over $100 là lớn hơn $100; phân biệt at least $100."), ("'A refund has been requested' cho biết gì?", ["Tiền đã vào tài khoản.", "Đã có yêu cầu hoàn tiền.", "Yêu cầu chắc chắn bị từ chối."], 1, "Requested chỉ giai đoạn yêu cầu, không bảo đảm kết quả.")], practice="""
Làm hai nhóm hai văn bản, ghi nguồn của từng điều kiện và dữ kiện.
Kiểm tra lại mọi câu liên quan con số bằng phép tính ngắn.
""", homework="""
Tự viết một chính sách và email 150 từ có điều kiện ngày/giá, đặt bốn câu hỏi.
Ôn cụm giao dịch và các trạng thái xử lý yêu cầu.
""", lessons=["a03", "u04"], sources=["ets", "cambridge-dictionary"], terms=["over", "at least", "requested", "approved", "issued", "received"])

session(3, 8, "Part 3–4 · Kết hợp audio với bảng và sơ đồ", "Listening", goals="""
Đọc tiêu đề, cột, đơn vị và nhãn trước khi nghe.
Ghép dữ kiện audio với thông tin nhìn thấy.
Tránh chọn chỉ từ bảng hoặc chỉ từ audio khi cần cả hai.
""", knowledge="""
Một số câu nghe có yếu tố đồ họa. Đọc nhanh tên hàng/cột/ngày/đơn vị; trong audio nghe điều kiện để chọn dòng hoặc địa điểm phù hợp.
Ngân hàng DHV hiện chưa có nhóm nghe kèm bảng/sơ đồ đầy đủ. Buổi này dùng mẫu chính thức ETS/IIBC ở liên kết nguồn; phần tự kiểm tra bên dưới là bài đọc hiểu cơ chế ghép thông tin, không giả làm bài nghe.
""", examples=[("Bảng: Room A = 20 seats; Room B = 40 seats. Audio: 'We expect thirty people.'", "B có đủ chỗ, A không đủ, nếu không có điều kiện khác."), ("Bảng giờ: Express 09:10; Local 09:25. Audio: 'Take the later service.'", "Later service ứng với 09:25; phải nối cách nói với dữ kiện bảng.")], checks=[("Bảng có gói A 5 kg, gói B 10 kg. Yêu cầu chứa 8 kg. Chọn gói đủ sức chứa?", ["A", "Không gói nào.", "B"], 2, "8 kg vượt 5 kg và nằm trong mức 10 kg."), ("Trước audio có bảng giá, điều nào cần nhìn nhanh?", ["Tên cột, đơn vị, loại sản phẩm và điều kiện.", "Chỉ màu chữ.", "Bỏ qua bảng hoàn toàn."], 0, "Đây là dữ kiện giúp liên kết thông tin nghe với bảng.")], practice="""
Mở mẫu nghe có graphic ở ETS/IIBC, xem hướng dẫn và luyện nhóm tương ứng tại nguồn.
Ghi rõ điều lấy từ audio và điều lấy từ hình/bảng cho từng đáp án.
""", homework="""
Tạo một bảng giờ/giá đơn giản và ba câu mô tả để tự luyện ghép dữ kiện.
Tổng hợp lỗi buổi 5–8, chọn một nhóm đọc và một nhóm nghe cần ôn.
""", lessons=["i02", "a01"], sources=["ets", "format"], terms=["capacity", "departure", "platform", "rate", "column", "available"], checkpoint="Mốc Level 3 buổi 8: bổ sung dạng graphic bằng nguồn chính thức; ghi rõ phần nào còn thiếu luyện thực tế.")

session(3, 9, "Part 7 · Triple passage và thông tin cập nhật", "Reading", goals="""
Giữ bản đồ ba nguồn trong khi trả lời nhiều câu.
Theo dõi điều kiện giữ nguyên và điều kiện đã đổi.
Kiểm tra tính nhất quán của câu trả lời trong cùng nhóm.
""", knowledge="""
Tạo bảng phiên bản: yêu cầu ban đầu, xác nhận, cập nhật. Ngày mới hơn chỉ ưu tiên cho thông tin nó thực sự sửa; vẫn giữ các điều kiện không đổi.
Một đáp án có thể đúng theo nguồn đầu nhưng sai sau cập nhật. Đọc câu hỏi để biết đang hỏi thời điểm/nguồn nào trước khi chọn.
""", examples=[("A: 30 tickets at $8. B: Booking confirmed. C: Cancel 5 tickets; the rest remain unchanged.", "Còn 25 vé, giá đơn vị vẫn $8; tiền vé còn lại $200 nếu không có phí khác."), ("'Only the delivery address has changed.'", "Chỉ địa chỉ đổi; không tự đổi số lượng, giá hoặc lịch nếu không được nêu.")], checks=[("Đặt 12 phòng, hủy 2 và thêm 1. Tổng cuối?", ["11", "12", "15"], 0, "12 − 2 + 1 = 11."), ("Nguồn mới chỉ đổi người liên hệ. Điều nào có căn cứ?", ["Mọi điều khoản cũ bị hủy.", "Cập nhật người liên hệ, giữ các trường không được nói là thay đổi.", "Tự sửa cả giờ hẹn."], 1, "Chỉ cập nhật thông tin có bằng chứng.")], practice="""
Làm hai nhóm ba văn bản; ghi thời gian và số lần phải quay lại từng nguồn.
Chữa câu sai bằng cách chỉ ra phiên bản thông tin đã dùng nhầm.
""", homework="""
Viết lại bảng phiên bản cho một nhóm bằng tối đa 6 dòng.
Ôn 8 cụm cập nhật/hủy/thay thế và đặt câu riêng.
""", lessons=["a04", "a03"], sources=["ets", "format"], terms=["revised", "remaining", "unchanged", "cancel", "replace", "latest"])

session(3, 10, "Reading · Quản lý 75 phút", "Reading", goals="""
Đặt ngân sách thời gian theo độ chính xác thực tế.
Biết đánh dấu và đi tiếp ở câu khó.
Đo hiệu quả theo cả số đúng và câu chưa kịp làm.
""", knowledge="""
Gợi ý ban đầu: Part 5 khoảng 12 phút, Part 6 khoảng 10 phút, Part 7 khoảng 53 phút; tổng 75. Đây là phương án thử, phải điều chỉnh theo tốc độ và lỗi của từng người.
Không bỏ nhiều câu dễ phía sau để cố giải một câu khó. Sau bài, tách sai vì không biết với sai vì không đủ thời gian; phương án ôn của hai loại khác nhau.
""", examples=[("Dùng 18 phút cho Part 5 và 12 phút cho Part 6.", "Chỉ còn 45 phút cho Part 7; cần xem phần nào có thể giảm thời gian mà vẫn giữ độ đúng."), ("Một câu mất 3 phút nhưng vẫn đoán.", "Đánh dấu đi tiếp sớm hơn có thể giúp có thời gian cho câu khác; xem lại ở lượt chữa.")], checks=[("Part 5 dùng 12 phút, Part 6 dùng 10 phút. Còn bao nhiêu trong 75 phút?", ["43", "50", "53"], 2, "75 − 12 − 10 = 53 phút."), ("Sau bài nhiều câu chưa kịp làm, nên ghi gì?", ["Thời gian từng phần và số câu bỏ dở, cùng nguyên nhân lỗi.", "Chỉ tổng điểm.", "Chỉ câu khó nhất."], 0, "Cần dữ kiện về tốc độ và kiến thức để chỉnh cách luyện.")], practice="""
Luyện một phần Reading 100 câu mới có nguồn hợp lệ trong 75 phút, tự ghi ba mốc thời gian.
Nếu dùng bộ DHV, ghi rõ câu đã gặp; ngân hàng lặp không dùng để suy điểm thi.
""", homework="""
Chữa các câu bỏ dở trước, xem làm không giờ có đúng không.
Điều chỉnh ngân sách lần sau dựa trên hai lỗi lớn nhất.
""", lessons=["u03", "a02", "a04"], sources=["format", "ets", "iig"], terms=["time budget", "accuracy", "pace", "skip", "review", "remaining"])

session(3, 11, "Listening · Nghe một lượt và giữ sức tập trung", "Listening", goals="""
Luyện nghe liền mạch và chuyển chú ý giữa các nhóm.
Bổ sung giọng người thật và nhiều cách phát âm.
Tách kỹ năng nghe mới khỏi trí nhớ transcript.
""", knowledge="""
Luyện khoảng 45 phút nghe theo cấu trúc thật cần nguồn audio phù hợp. DHV dùng audio tổng hợp và cho điều khiển lại; nguồn chính thức giúp bổ sung điều kiện nghe và giọng tự nhiên.
Ở lượt kiểm tra, nghe một lần rồi chốt; ở lượt học, nghe lại, chép đoạn khó và đọc theo. Hai chế độ có mục đích khác nhau, cần ghi rõ kết quả của lượt đầu.
""", examples=[("Lượt đầu đúng 6/10; sau đọc transcript đúng 10/10.", "6/10 phản ánh lượt đầu trên đoạn này; 10/10 sau học cho thấy hiểu nội dung đã chữa, không phải bài đo độc lập."), ("Một câu lỡ nghe, nhóm tiếp theo bắt đầu.", "Chuyển chú ý sang nhóm mới; không để một lỗi kéo dài qua nhiều câu.")], checks=[("Kết quả nào dùng để theo dõi nghe lần đầu?", ["Sau lần nghe thứ năm.", "Lượt chưa mở transcript và chưa biết đáp án.", "Lượt đọc lời giải trước."], 1, "Theo dõi nhất quán điều kiện lượt đầu giúp đánh giá thực tế hơn."), ("Nguồn nào bổ sung điều ngân hàng giọng tổng hợp còn hạn chế?", ["Chỉ đọc phụ đề tiếng Việt.", "Chỉ xem bảng đáp án.", "Audio người thật có nguồn hợp lệ và mẫu chính thức."], 2, "Giọng người thật và điều kiện phù hợp giúp luyện nghe ngoài một giọng tổng hợp.")], practice="""
Luyện một lượt nghe liên tục trên nguồn phù hợp; ghi câu mất tập trung và câu nghe sai âm.
Chữa 3 đoạn khó theo nghe–chép–đối chiếu–đọc theo.
""", homework="""
Nghe B1/B2 15 phút/ngày, luân phiên chủ đề và người nói.
Chuẩn bị một đề chưa làm cho buổi 12, kiểm tra audio và thời gian trước khi bắt đầu.
""", lessons=["i01", "u01", "a01"], sources=["ets", "bc-b2-listening", "cambridge"], terms=["connected speech", "stress", "intonation", "distraction", "first attempt", "transcript"])

session(3, 12, "Đề tổng hợp · Đánh giá trước chặng 900", "Assessment", goals="""
Hoàn thành 200 câu trong điều kiện đã ghi rõ.
Phân tích độ ổn định theo Part và loại lỗi.
Chọn nội dung Level 4 theo nhu cầu cá nhân.
""", knowledge="""
Bài L&R có 100 nghe khoảng 45 phút và 100 đọc trong 75 phút; tổng 200 câu. Chọn đề mới có quyền truy cập để tránh việc nhớ đáp án làm tăng kết quả giả.
Bộ DHV 200 câu dùng cùng ngân hàng đang học, audio điều khiển thủ công và đồng hồ tổng 120 phút. Có thể dùng luyện sức bền, nhưng đánh giá độc lập cần nguồn mới và điều kiện phù hợp.
""", examples=[("Part 7 có nhiều câu bỏ trống, Part 5 đúng nhưng mất quá lâu.", "Ưu tiên quản lý thời gian đọc và bài nhiều văn bản thay vì học lại toàn bộ ngữ pháp."), ("Part 2 sai chủ yếu câu gián tiếp; các câu WH cơ bản ổn.", "Ôn ý định và phản hồi gián tiếp ở “Part 2 · Câu đáp gián tiếp và ý ngầm”/Level 3 buổi 1.")], checks=[("Một đề dùng nhiều câu đã học nên được xem là gì?", ["Luyện củng cố, không phải đánh giá độc lập.", "Chắc chắn dự đoán điểm thi.", "Chứng chỉ TOEIC."], 0, "Độ quen câu làm sai lệch việc đo năng lực trên câu mới."), ("Cấu trúc thời gian nghe/đọc phổ biến của TOEIC L&R là gì?", ["75 phút nghe, 45 phút đọc.", "Khoảng 45 phút nghe, 75 phút đọc.", "30 phút cho mỗi phần."], 1, "Theo cấu trúc L&R chính thức đang được dẫn nguồn.")], practice="""
Làm 200 câu trong 120 phút; ghi rõ nguồn, đề mới/cũ và có nghe lại hay không.
Không mở lời giải trong lượt làm; dành việc chữa cho hôm sau để giữ điều kiện rõ ràng.
""", homework="""
Dành một buổi chữa riêng, ghi tỷ lệ từng Part và 10 lỗi cần sửa đầu tiên.
Nếu kết quả chưa ổn định, bổ sung 2–4 buổi mục tiêu trước khi tăng độ khó.
""", lessons=["u01", "u03", "a04"], sources=["ets", "format", "iig"], terms=["baseline", "section", "accuracy", "consistency", "independent", "review"], checkpoint="Tổng kết Level 3: cần dữ liệu từ nội dung mới và thời gian thực tế; hoàn tất buổi không đồng nghĩa đạt 800.", minutes=120)

session(4, 1, "Listening · Paraphrase tinh và mức độ chắc chắn", "Listening", goals="""
Giữ đúng điều kiện, phủ định và mức độ khi diễn giải.
Hiểu ý định trong câu trích dẫn khó.
Loại đáp án khẳng định mạnh hơn audio.
""", knowledge="""
May/might có mức chắc chắn khác will/definitely. We are considering khác we have decided; tentative khác confirmed. Đáp án đổi mức độ có thể sai dù cùng chủ đề.
Luyện paraphrase theo mệnh đề đầy đủ, giữ các từ only/unless/before. Nghe từ nhấn mạnh và diễn biến trước câu trích dẫn để hiểu mục đích.
""", examples=[("'We are considering extending the opening hours.'", "Mới cân nhắc, chưa chốt giờ mới."), ("'The launch date is provisional.'", "Lịch có thể thay đổi; không nên chọn đáp án xác nhận tuyệt đối.")], checks=[("'The plan may change' cho biết gì?", ["Chắc chắn đã đổi.", "Không bao giờ thay đổi.", "Có khả năng thay đổi."], 2, "May giữ mức khả năng, không phải chắc chắn."), ("'We have decided to renew' khác 'We are considering renewal' ở đâu?", ["Một câu đã quyết định, một câu còn cân nhắc.", "Hai câu luôn đồng nghĩa.", "Cả hai đều là từ chối."], 0, "Giai đoạn quyết định và độ chắc chắn khác nhau.")], practice="""
Luyện 4 nhóm nghe khó; đánh dấu từ chỉ mức độ và điều kiện quyết định.
Viết 8 cặp paraphrase, kiểm tra không làm mạnh thêm lời gốc.
""", homework="""
Nghe B2/nguồn chính thức 20 phút, ghi 5 cách diễn đạt dự kiến/chắc chắn.
Ôn câu sai sau 3 ngày bằng audio mới tương tự chủ đề.
""", lessons=["u01", "a01"], sources=["ets", "bc-b2-listening"], terms=["tentative", "provisional", "consider", "confirm", "provided that", "definitely"])

session(4, 2, "Part 5–6 · Từ vựng chính xác và văn phong", "Reading", goals="""
Chọn nghĩa tinh theo collocation và văn phong.
Phân biệt các từ cùng gốc nhưng khác chức năng/nghĩa.
Giảm lỗi bất cẩn ở câu đã nắm kiến thức.
""", knowledge="""
Ở mức cao, tập trung từ đi cùng nhau và sắc thái: comply with regulations, be eligible for reimbursement. Câu đúng từ loại vẫn có thể sai kết hợp từ.
Part 6 yêu cầu mạch thông tin và giọng văn nhất quán. Đọc lại câu hoàn chỉnh giúp phát hiện phủ định, tham chiếu hoặc thì bị bỏ sót lúc chạy nhanh.
""", examples=[("'Employees must comply with the revised regulations.'", "Comply with là tuân thủ; không dùng comply to theo cấu trúc này."), ("'Travel expenses are eligible for reimbursement.'", "Reimbursement là hoàn trả chi phí đã chi, khác salary là lương.")], checks=[("All contractors must comply ____ safety rules.", ["with", "to", "at"], 0, "Cụm chuẩn đang dùng là comply with."), ("'Reimbursement of travel expenses' là gì?", ["Tăng lương hằng tháng.", "Hoàn trả chi phí đi lại.", "Phí phạt đi muộn."], 1, "Reimbursement là hoàn trả khoản đã chi theo điều kiện.")], practice="""
Luyện 30 câu Part 5 và bốn đoạn Part 6 trên nội dung chưa làm nếu có.
Tách lỗi bất cẩn khỏi lỗi chưa biết; ghi quy tắc rà soát 10 giây cho lỗi lặp lại.
""", homework="""
Học 12 collocation theo công việc, mỗi cụm một ví dụ có ngữ cảnh.
Đọc lại sổ lỗi, loại bỏ mẹo không còn giải thích được bằng cấu trúc/nghĩa.
""", lessons=["u03", "a02"], sources=["cambridge-dictionary", "bc-b1", "ets"], terms=["comply with", "eligible for", "reimbursement", "in accordance with", "substantial", "retain"])

session(4, 3, "Part 7 · Suy luận nhiều nguồn và ý định người viết", "Reading", goals="""
Giải suy luận bằng chuỗi bằng chứng ngắn.
Phân biệt thái độ, mục đích và chi tiết sự kiện.
Theo dõi thay đổi ở nhóm hai/ba văn bản với tốc độ ổn định.
""", knowledge="""
Một suy luận tốt không thêm nghề nghiệp, nguyên nhân hoặc kết quả chưa được nêu. Dùng 'bằng chứng A + bằng chứng B → kết luận có giới hạn' để tự kiểm tra.
Ý định người viết nằm ở việc muốn người nhận làm/hiểu gì; thái độ nằm ở cách đánh giá. Câu có cảm ơn không nhất thiết mang mục đích chính là cảm ơn nếu phần còn lại yêu cầu xử lý vấn đề.
""", examples=[("A: Members receive a 10% discount. B: Lin paid the member price.", "Có dấu hiệu Lin được áp dụng mức thành viên; không tự suy ra Lin là nhân viên cửa hàng."), ("'Thank you for your help. Could you send the missing attachment today?'", "Hành động yêu cầu là gửi tệp còn thiếu; lời cảm ơn là mở đầu lịch sự.")], checks=[("Email nói 'Please confirm by noon'. Người nhận cần làm gì?", ["Hủy mọi kế hoạch.", "Gửi xác nhận trước/trong hạn trưa.", "Đến trực tiếp lúc nửa đêm."], 1, "Confirm by noon là yêu cầu phản hồi xác nhận theo hạn."), ("Kết luận nào nên loại?", ["Kết luận nối được hai bằng chứng.", "Kết luận giữ nguyên điều kiện.", "Kết luận thêm nguyên nhân không được văn bản hỗ trợ."], 2, "Không đưa suy đoán ngoài bài thành đáp án.")], practice="""
Luyện ba nhóm nhiều văn bản, ghi thời gian và câu cần đối chiếu nhiều nhất.
Chọn 5 câu suy luận và viết chuỗi bằng chứng trong tối đa hai dòng.
""", homework="""
Ôn các từ giới hạn phạm vi và các trạng thái requested/approved/issued.
Chuẩn bị một đề mới hợp lệ cho buổi mô phỏng tiếp theo.
""", lessons=["u04", "a03", "a04"], sources=["ets", "cambridge"], terms=["infer", "imply", "confirm", "attachment", "scope", "evidence"])

session(4, 4, "Mô phỏng A · Đề mới và điều kiện làm bài", "Assessment", goals="""
Thực hiện một đề mới với điều kiện nghe/đọc đã xác định.
Ghi dữ kiện thời gian và mức độ tự tin.
Tạo danh sách lỗi để chữa ở buổi 5.
""", knowledge="""
Dùng đề mới được phép truy cập từ nguồn chính thức hoặc đơn vị đào tạo; không tải đề trôi nổi. Chỉ dùng cách quy đổi do nguồn của chính đề hướng dẫn, không dùng bảng số đúng tùy ý.
Nếu chỉ có ngân hàng DHV, dùng để luyện sức bền và ghi là câu có thể đã gặp. Không dùng kết quả đó để xác nhận đạt 900.
""", examples=[("Một đề mới, audio nghe một lượt, Reading 75 phút.", "Ghi nguồn và điều kiện để so sánh được với lần mô phỏng B."), ("Internet gián đoạn khiến nghe lại nhiều lần.", "Ghi nhận sự gián đoạn; không coi kết quả tương đương lượt thi không gián đoạn.")], checks=[("Để so sánh hai lần mô phỏng, cần giữ gì?", ["Cùng đáp án đã thuộc.", "Cùng màu giao diện.", "Nguồn/độ mới và điều kiện làm bài được ghi rõ, tương đối nhất quán."], 2, "Khác điều kiện có thể làm thay đổi điểm mà không phản ánh tiến bộ."), ("Có nên tự lấy phần trăm đúng nhân 990 để suy điểm TOEIC?", ["Không; không có quy đổi chuẩn bằng phép nhân đó.", "Có, luôn đúng.", "Chỉ cần làm tròn."], 0, "Điểm chuẩn hóa không bằng tỷ lệ đúng nhân điểm tối đa.")], practice="""
Làm 200 câu, khoảng 45 phút nghe và 75 phút đọc theo nguồn đề.
Ghi mốc thời gian, câu bỏ dở và câu đoán; không chữa trong 120 phút làm bài.
""", homework="""
Lưu kết quả lượt đầu và chọn 10 lỗi cần phân tích trong buổi 5.
Nghỉ hợp lý, không làm lại ngay đề vừa thuộc đáp án để báo tăng điểm.
""", lessons=["a01", "a02", "a04"], sources=["ets", "format", "iig"], terms=["simulation", "unseen", "conditions", "raw score", "scaled score", "consistency"], checkpoint="Mô phỏng A: tạo số liệu nền từ đề mới; không có đề mới thì ghi rõ chỉ là luyện củng cố.", minutes=120)

session(4, 5, "Chữa sâu · Kế hoạch sửa lỗi cá nhân", "Review", goals="""
Phân loại lỗi nghe âm, từ vựng, cấu trúc, suy luận và tốc độ.
Biến mỗi lỗi thành một hành động ôn cụ thể.
Kiểm tra sửa lỗi trên câu khác.
""", knowledge="""
Đáp án đúng không đủ giải thích. Với câu sai, ghi bằng chứng, lý do chọn nhầm, và điều cần học; với câu đoán đúng, vẫn xem là cần kiểm tra lại kiến thức.
Chọn hai nhóm gây mất nhiều câu nhất để ôn trước. Bài sửa nên dùng ví dụ khác nhưng cùng kỹ năng, tránh học thuộc vị trí đáp án.
""", examples=[("Sai vì 'by Friday' bị hiểu thành 'on Friday'.", "Ôn nghĩa thời hạn, viết ba câu mới với by/until/on và kiểm tra lại bằng ngữ cảnh khác."), ("Đúng do đoán nhưng không biết nghĩa từ.", "Vẫn đưa từ/cụm vào danh sách ôn; không xem là đã làm chủ.")], checks=[("Câu đoán đúng nhưng không giải thích được nên xử lý thế nào?", ["Đánh dấu cần ôn và kiểm tra lại trên câu mới.", "Bỏ qua vì đã đúng.", "Xóa câu khỏi sổ lỗi."], 0, "Kết quả đúng do đoán chưa chứng minh kiến thức chắc."), ("Ưu tiên ôn nào hiệu quả hơn sau đề?", ["Học lại mọi thứ theo thứ tự cũ.", "Chọn nhóm lỗi lặp/gây mất nhiều câu và có hành động cụ thể.", "Chỉ xem tổng điểm."], 1, "Ưu tiên theo bằng chứng giúp tập trung vào điểm yếu thực tế.")], practice="""
Chữa ít nhất 10 lỗi và 5 câu đoán đúng của mô phỏng A.
Luyện hai nhóm yếu bằng bài hỗ trợ phù hợp, tự viết thêm câu khác để kiểm tra chuyển giao.
""", homework="""
Ôn trong 3–7 ngày trước mô phỏng B; ghi mỗi ngày đã sửa kỹ năng nào.
Chuẩn bị đề B chưa làm, điều kiện tương đương đề A.
""", lessons=["i01", "u03", "a04"], sources=["cambridge", "bc-b2-listening", "ets"], terms=["error log", "root cause", "evidence", "guess", "retest", "priority"])

session(4, 6, "Mô phỏng B · Kiểm tra độ ổn định", "Assessment", goals="""
Làm một đề khác sau giai đoạn sửa lỗi.
So sánh lỗi và tốc độ theo từng phần.
Nhận ra tiến bộ thật trên nội dung mới.
""", knowledge="""
Chọn đề khác, không đổi điều kiện chỉ để tăng điểm. So tỷ lệ đúng, số câu bỏ dở, thời gian và loại lỗi; độ khó hai đề có thể khác nên không giải thích mọi chênh lệch là tiến bộ.
Nếu một nhóm vẫn yếu, quay lại bài mục tiêu. Lộ trình linh hoạt cho phép thêm buổi; hoàn thành số buổi không bắt buộc phải đăng ký thi ngay.
""", examples=[("Đề B ít câu bỏ dở hơn nhưng sai từ vựng nhiều hơn.", "Có cải thiện tốc độ, còn cần xem độ khó và vốn từ; không chỉ kết luận tốt hơn từ một con số."), ("Sai câu gián tiếp Part 2 giảm trên audio mới.", "Đây là dấu hiệu kỹ năng mục tiêu được cải thiện, cần thêm dữ liệu để xem ổn định.")], checks=[("Đề B dùng lại đề A đã chữa có phù hợp đo ổn định không?", ["Có vì điểm chắc cao hơn.", "Không; độ quen đáp án làm sai lệch việc đánh giá độc lập.", "Chỉ cần đổi thứ tự đáp án là đủ."], 1, "Đổi thứ tự không làm nội dung trở thành mới."), ("Nếu điểm giảm nhẹ nhưng đề B khó hơn, kết luận hợp lý?", ["Chắc chắn mất toàn bộ kiến thức.", "Chắc chắn phải thi ngay.", "Cần xem từng kỹ năng, độ khó và điều kiện trước khi kết luận."], 2, "Một chênh lệch đơn lẻ không đủ mô tả xu hướng.")], practice="""
Làm đề B 200 câu/120 phút với nguồn hợp lệ, ghi điều kiện như lần A.
Không mở transcript/lời giải trong lượt làm; giữ kết quả để chữa ngày sau.
""", homework="""
So bảng A/B theo từng Part, ghi ba tiến bộ và ba việc còn cần sửa.
Nếu chưa ổn định, dành thêm một chu kỳ học–luyện–kiểm tra mới.
""", lessons=["a01", "a02", "a04"], sources=["ets", "format", "iig"], terms=["stability", "comparison", "unseen material", "trend", "timing", "retention"], checkpoint="Mô phỏng B: đối chiếu bằng chứng qua hai đề khác nhau; không dùng một điểm cao duy nhất để cam kết đầu ra.", minutes=120)

session(4, 7, "Hoàn thiện · Bẫy cuối và nhịp làm bài", "Review", goals="""
Giảm các lỗi lặp còn lại từ hai đề mô phỏng.
Giữ chiến lược đọc/nghe đã kiểm chứng.
Lập checklist ngắn cho từng nhóm lỗi cá nhân.
""", knowledge="""
Tập trung lỗi còn lặp: số ít/số nhiều, từ phủ định, điều kiện giảm giá, who does what, ngày đã cập nhật. Checklist chỉ hữu ích khi gắn lỗi thật của bản thân.
Không thay toàn bộ chiến lược sát ngày thi nếu chưa luyện. Thử thay đổi nhỏ trên nhóm câu mới và xem cả tốc độ lẫn độ chính xác.
""", examples=[("Hay nhầm 'no later than' với 'after'.", "Thêm bước kiểm tra hướng thời gian ở câu deadline, luyện ba ví dụ mới."), ("Hay bỏ lỡ next action do vẫn nghĩ câu trước.", "Tập chuyển chú ý sang nhóm tiếp theo theo nhịp audio, không kéo dài suy nghĩ câu cũ.")], checks=[("Một checklist cá nhân tốt nên dựa vào gì?", ["Lỗi lặp đã quan sát và cách kiểm tra cụ thể.", "Mẹo đoán đáp án không có bằng chứng.", "Tất cả quy tắc ngữ pháp từng biết."], 0, "Checklist ngắn gắn lỗi thật dễ dùng hơn danh sách quá tải."), ("Trước khi thay chiến lược làm bài, nên làm gì?", ["Áp dụng ngay trong thi thật.", "Thử trên nhóm câu mới và đo kết quả.", "Chỉ hỏi xem người khác có thích không."], 1, "Kiểm chứng trên bài mới giúp biết thay đổi có phù hợp mình.")], practice="""
Luyện hai nhóm lỗi cuối từ đề A/B, ưu tiên câu chưa gặp.
Thử một lượt ngắn theo chiến lược đã chọn, ghi độ đúng và mức tập trung.
""", homework="""
Soạn checklist một trang: nhịp từng phần, lỗi cần tránh và cách chuyển câu.
Ôn thẻ đến hạn, nghe nhẹ và duy trì lịch ngủ phù hợp.
""", lessons=["i01", "u03", "a04"], sources=["ets", "cambridge"], terms=["checklist", "exception", "negation", "updated", "next action", "focus"])

session(4, 8, "Tổng kết lộ trình · Kế hoạch thi và duy trì", "Assessment", goals="""
Đối chiếu mục tiêu với bằng chứng học tập thực tế.
Chọn học thêm, nhờ đánh giá hoặc đăng ký thi khi sẵn sàng.
Duy trì kỹ năng sau khi kết thúc lộ trình.
""", knowledge="""
Hoàn tất 56 buổi thể hiện đã đi qua kế hoạch, không phải chứng nhận đạt 900. Quyết định thi nên dựa vào nhiều bài mới, điều kiện làm bài, mức ổn định và tư vấn chuyên môn khi cần.
Quy định thi, giấy tờ, lịch và lệ phí có thể thay đổi; xem trực tiếp thông tin của đơn vị tổ chức tại thời điểm đăng ký. Sau lộ trình, giữ nghe/đọc đều và ôn thẻ đến hạn.
""", examples=[("Kết quả còn thiếu thời gian ở Part 7.", "Thêm chu kỳ đọc nhiều văn bản và đo 75 phút trước khi đặt lịch thi."), ("Đã đạt mục tiêu qua đánh giá phù hợp.", "Duy trì nghe/đọc 20–30 phút mỗi ngày và dùng tiếng Anh trong tình huống thật.")], checks=[("Đánh dấu hoàn tất lộ trình có đồng nghĩa được chứng nhận 900 không?", ["Có, tự động.", "Có nếu học đủ ngày.", "Không; cần kết quả đánh giá/thi phù hợp."], 2, "Số buổi đã học và điểm thi là hai thông tin khác nhau."), ("Nên xem lịch, lệ phí và giấy tờ thi ở đâu?", ["Nguồn chính thức của đơn vị tổ chức tại thời điểm đăng ký.", "Một ảnh cũ không rõ ngày.", "Suy từ điểm luyện trong ứng dụng."], 0, "Thông tin đăng ký cần cập nhật từ đơn vị tổ chức.")], practice="""
Rà bảng kết quả, sổ lỗi và tiêu chí từng level; ghi phần đã chắc và phần cần bổ sung.
Lập kế hoạch 2–4 tuần tiếp theo theo tình trạng thật, không theo số buổi đã đánh dấu.
""", homework="""
Duy trì ôn cách quãng, nghe người thật và đọc văn bản công việc mới.
Nếu cần thi, kiểm tra hướng dẫn hiện hành tại ETS/IIG và làm theo quy trình của nhà tổ chức.
""", lessons=["a01", "a03", "a04"], sources=["ets", "iig", "format"], terms=["readiness", "maintenance", "registration", "requirements", "goal", "continuity"], checkpoint="Tổng kết: học viên có hồ sơ tiến bộ và kế hoạch tiếp theo; không hứa đầu ra từ số buổi hoặc điểm nội bộ.")


def curriculum():
    return CURRICULUM


def guide_markdown(sources):
    """Export the same content shown in the app so the guide cannot drift."""
    lookup = {s["id"]: s for s in sources}
    out = ["# Lộ trình TOEIC cùng DHV — 56 buổi", "", CURRICULUM["description"], "",
           "Đối chiếu nguồn ngày 27/10/2026. Các mục tiêu, thời lượng, bài tập và tiêu chí chuyển level dưới đây là thiết kế của DHV, không phải cam kết của ETS hay nguồn tham khảo.", "",
           CURRICULUM["notice"], "", "## Chọn nhịp học", "",
           "| Nhịp | Số tuần dự kiến | Tự học |", "|---|---:|---|",
           *[f"| {n} buổi/tuần | {sum(ceil(l['session_count']/n) for l in CURRICULUM['levels'])} | 45 phút/ngày, điều chỉnh theo nền tảng |" for n in (2, 3, 4)], "",
           "Đây là số tuần xếp lịch, không phải thời gian bảo đảm đạt điểm. Cộng thêm tuần ôn khi chưa đạt tiêu chí và thời gian làm/chữa đề ngoài buổi học.", "",
           "## Đầu vào và cách học", "", *[f"- {x}" for x in CURRICULUM["entry"]], "",
           *[f"- {x['minutes']} phút: {x['task']}" for x in CURRICULUM["daily_routine"]], "",
           "Buổi thường 90 phút: 10 ôn + 20 kiến thức + 20 luyện có hướng dẫn + 25 tự làm + 10 chữa + 5 tự kiểm tra. Ba buổi mô phỏng riêng dài 120 phút; chữa vào phần tự học hoặc buổi tiếp theo.", "",
           "Số bài/câu trong nhiệm vụ là khối lượng luyện đề xuất, dùng bài hỗ trợ trong DHV hoặc nguồn liên kết. Không phải mỗi buổi đều có một đề riêng tương ứng đã được đóng gói. Bài nghe phải dùng audio; các câu tự kiểm tra dạng chữ kiểm tra kiến thức và chiến lược, không thay thế phép đo nghe.", ""]
    for level in CURRICULUM["levels"]:
        out += [f"## {level['name']} — {level['title']}", "", f"**{level['target']} · {level['session_count']} buổi**", "", level["entry"], "",
                *[f"- {x}" for x in level["outcomes"]], "", f"**Tiêu chí chuyển chặng:** {level['exit']}", "",
                "| Buổi | Trọng tâm | Kỹ năng | Thời lượng |", "|---:|---|---|---:|"]
        rows = [s for s in CURRICULUM["sessions"] if s["level_id"] == level["id"]]
        out += [f"| {s['number']} | {s['title']} | {s['skill']} | {s['minutes']} phút |" for s in rows]
        out.append("")
        for s in rows:
            out += [f"### Buổi {s['number']}: {s['title']}", "", "**Đầu ra**", "", *[f"- {x}" for x in s["objectives"]], "",
                    "**Kiến thức trọng tâm**", "", *[f"- {x}" for x in s["knowledge"]], "", "**Ví dụ tự biên soạn**", ""]
            for e in s["examples"]:
                out += [f"- {e['text']} — {e['explanation']}"]
            out += ["", "**Luyện trong buổi**", "", *[f"- {x}" for x in s["practice"]], "", "**Tự kiểm tra kiến thức**", ""]
            for i, q in enumerate(s["checks"], 1):
                options = "; ".join(f"{chr(65+j)}. {x}" for j, x in enumerate(q["options"]))
                out += [f"{i}. {q['prompt']} ({options})", f"   - Đáp án {chr(65+q['correct'])}: {q['explanation']}"]
            out += ["", "**Bài tập về nhà**", "", *[f"- {x}" for x in s["homework"]], "",
                    f"**Cụm từ trọng tâm:** {', '.join(s['vocabulary_focus'])}.", "",
                    f"**Bài hỗ trợ trong DHV:** {', '.join(s['lesson_ids'])}. Đây là bài dùng chung để ôn kỹ năng, không phải đề mới riêng cho buổi.", "",
                    "**Nguồn bổ trợ:** " + "; ".join(f"[{lookup[k]['title']}]({lookup[k]['url']})" for k in s["source_ids"]), ""]
            if s["checkpoint"]:
                out += [f"**Mốc đánh giá:** {s['checkpoint']}", ""]
    out += ["## Nguồn gốc và sử dụng", "",
            "Nội dung, ví dụ và 112 câu tự kiểm tra được biên soạn mới cho DHV với hỗ trợ AI, cần giáo viên rà soát nếu dùng để đánh giá chính thức. Không nhập ngân hàng đề/audio thương mại. Các liên kết dẫn người học tới nhà cung cấp để học theo điều kiện của nguồn.", "",
            "Xem [nghiên cứu nguồn](SOURCES.md), [thiết kế và phạm vi](THIET_KE_CHUONG_TRINH.md) và [hướng dẫn chạy](README.md).", ""]
    return "\n".join(out)
