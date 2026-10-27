"""Original DHV questions that fill gaps in the licensed bank: graphics, inference,
sentence placement, indirect responses and grammar. Not official ETS questions.
"""
EXTRA = []


def question(qid, part, prompt, options, explanation, topic, **extra):
    EXTRA.append({"id": "dhv-x-" + qid, "lesson_id": f"lab-p{part}", "part": part,
        "prompt": prompt, "options": options, "correct": 0, "explanation": explanation,
        "topic_ids": [topic], "provenance": {"provider": "DHV", "kind": "original", "version": "2026.10-v3"}, **extra})


def group(gid, part, text, rows, graphic=None):
    context = {"group_id": "dhv-x-" + gid}
    if part <= 4:
        context.update(transcript=text, audio_id="dhv-x-" + gid)
    else:
        context["passage"] = text
    if graphic:
        context["graphic"] = graphic
    for n, (prompt, options, explanation, topic) in enumerate(rows, 1):
        question(f"{gid}-{n}", part, prompt, options, explanation, topic, **context)


for n, (heard, choices, why, topic) in enumerate([
 ("The meeting link in my invitation has expired.", ["I'll send you the updated one.", "The meeting lasted an hour.", "I invited six people yesterday."], "Người nghe gặp link hết hạn; gửi link mới là hành động khắc phục, không phải nói thời lượng họp.", "p2-indirect"),
 ("There's no space left on the display shelf.", ["Could we move the older samples to storage?", "The display opens at nine.", "I left the office early."], "Đề nghị chuyển mẫu cũ tạo thêm chỗ trống, đáp lại vấn đề bằng giải pháp gián tiếp.", "p2-indirect"),
 ("Our train won't arrive until after the interview starts.", ["Let's ask whether a video interview is possible.", "I bought the ticket last week.", "The platform was very clean."], "Đến muộn có thể giải quyết bằng hỏi phỏng vấn video; hai phương án khác không xử lý xung đột giờ.", "p2-indirect"),
 ("I haven't received the revised floor plan.", ["Would you like me to forward the architect's email?", "The floor was polished yesterday.", "It's a five-year plan."], "Forward email của kiến trúc sư là cách cung cấp sơ đồ; floor và plan trong hai đáp án khác là bẫy nghĩa.", "p2-indirect"),
 ("The visitor says her access code isn't working.", ["Has she tried the code in today's confirmation?", "The visitors arrived in a group.", "I work in accounting."], "Câu hỏi ngược kiểm tra đúng mã hiện tại giúp xử lý sự cố; không cần bắt buộc một câu trần thuật.", "p2-indirect"),
 ("We promised the client a response this afternoon.", ["Then we should finalize the estimate now.", "The client has two offices.", "Afternoons are usually sunny."], "Lời nhắc hạn phản hồi được đáp bằng hành động hoàn tất dự toán ngay; hai thông tin còn lại không giải quyết lời nhắc.", "p2-indirect"),
 ("The new supplier hasn't confirmed the price, has it?", ["We're still waiting for its quotation.", "Yes, the supplies are heavy.", "The confirmation number is on the train ticket."], "Still waiting for its quotation xác nhận đang chờ báo giá, trả lời đúng sự việc trong câu hỏi đuôi.", "p2-yesno"),
 ("You can attend the morning briefing, can't you?", ["Only if my appointment finishes early.", "The briefcase belongs to Mia.", "I attended a concert last night."], "Người đáp nêu điều kiện có thể tham dự; briefing và briefcase là hai từ khác nghĩa.", "p2-yesno"),
 ("The delivery fee is included, isn't it?", ["No, it's listed separately on the invoice.", "The driver included a map.", "The fee was discussed at a workshop."], "Listed separately phủ nhận phí đã gộp. Câu đuôi không có nghĩa người đáp buộc phải đồng ý.", "p2-yesno"),
 ("Would you prefer a call or a written update?", ["A written update would be easier to share.", "I wrote the address incorrectly.", "The phone was repaired yesterday."], "Chọn cập nhật bằng văn bản và giải thích lợi ích chia sẻ, đúng hai phương án được hỏi.", "p2-choice"),
 ("Should we book Room Elm or Room Cedar?", ["Neither is large enough for our group.", "The booking reference has six digits.", "Cedar trees grow behind the building."], "Neither từ chối cả hai phương án vì thiếu sức chứa, là câu trả lời hợp lệ cho A or B.", "p2-choice"),
 ("Would Monday or Thursday work for the equipment check?", ["Either day is fine; the lab is free on both.", "The equipment arrived by truck.", "I checked the figures twice."], "Either cùng both cho biết cả hai ngày đều được. Không cần bắt buộc chọn đúng một ngày.", "p2-choice"),
], 1):
    question(f"p2-{n:02}", 2, "Choose the best response.", choices, why, topic,
        transcript=heard, audio_id=f"dhv-x-p2-{n:02}")

group("graphic-conversation-1", 3,
 "Woman: We need a room for twenty-eight guests, and our workshop starts at ten. The screen is essential for the demonstrations.\nMan: Cedar is too small. Elm has a screen, but it is not available until eleven.\nWoman: Then let's book the remaining room that meets all three requirements.\nMan: I'll reserve it now and send the room name to the trainer.", [
 ("What are the speakers planning?", ["A workshop", "A product shipment", "A staff interview", "A building inspection"], "Người nữ nêu our workshop và các yêu cầu cho phần minh họa, nên đang chuẩn bị workshop.", "p3-overview"),
 ("Look at the graphic. Which room will they book?", ["Maple", "Cedar", "Elm", "Pine"], "Cần ≥28 ghế, màn hình và trống lúc 10 giờ. Chỉ Maple thỏa cả ba; Pine đủ ghế nhưng không có màn hình.", "p3-graphic"),
 ("What will the man do after making the reservation?", ["Notify the trainer", "Buy a screen", "Reduce the guest list", "Delay the workshop"], "Người nam sẽ gửi tên phòng cho trainer sau khi đặt, theo câu cuối.", "p3-next"),
 ], {"title": "Meeting rooms", "columns": ["Room", "Seats", "Screen", "Available from"], "rows": [["Cedar","20","Yes","09:00"],["Elm","35","Yes","11:00"],["Maple","30","Yes","09:00"],["Pine","40","No","09:00"]]})
group("graphic-conversation-2", 3,
 "Man: Our opening event is on Friday, so the sample display needs to reach us by Thursday.\nWoman: The supplier recommends the tracked option that takes two business days. Express is faster, but we don't need it if the samples leave on Tuesday as planned.\nMan: Good. That gives us some breathing room. Please confirm the pickup today.\nWoman: I'll email the supplier now and ask for the tracking number after collection.", [
 ("Look at the graphic. How much does the recommended shipping option cost?", ["$18", "$9", "$30", "$45"], "Phương án có theo dõi và mất hai ngày làm việc là Priority, giá 18 đô la. Không chọn Express chỉ vì nhanh hơn.", "p3-graphic"),
 ("What does the man mean by 'That gives us some breathing room'?", ["They have some time before the event", "They need a larger room", "The package contains medical equipment", "The delivery should be canceled"], "Sự kiện thứ Sáu, dự kiến hàng đến thứ Năm nên còn thời gian chuẩn bị. Breathing room là thời gian dự phòng trong ngữ cảnh này.", "p3-intent"),
 ("What will the woman do next?", ["Contact the supplier", "Visit the exhibition venue", "Pay an express surcharge", "Print new display panels"], "I'll email the supplier now là hành động được nói rõ; tracking number sẽ xin sau khi lấy hàng.", "p3-next"),
 ], {"title": "Shipping options", "columns": ["Service", "Business days", "Tracking", "Fee"], "rows": [["Economy","4","No","$9"],["Priority","2","Yes","$18"],["Express","1","Yes","$30"],["Same day","0","Yes","$45"]]})
group("graphic-talk-1", 4,
 "Passengers for West Park, please note a change to today's timetable. The eight twenty shuttle has been canceled because of a mechanical problem. Your tickets will be accepted on the next departure to the same destination. Please stay at platform three; no change of platform is required. The service desk will provide a written confirmation of the delay if you need one for your employer.", [
 ("Why has one shuttle been canceled?", ["A vehicle has a mechanical problem", "The platform is closed", "Too few tickets were sold", "Roads are flooded"], "Because of a mechanical problem nêu nguyên nhân phương tiện bị sự cố.", "p4-detail"),
 ("Look at the graphic. When can affected passengers travel to West Park?", ["08:50", "08:30", "08:40", "09:10"], "Tìm chuyến tiếp theo đến cùng điểm West Park sau 08:20: 08:50. Chuyến 08:30 và 08:40 đi nơi khác.", "p4-graphic"),
 ("What can passengers obtain at the service desk?", ["Written confirmation of the delay", "A new employee badge", "A hotel reservation", "A free meal voucher"], "Quầy có thể cấp xác nhận bằng văn bản về việc chậm để người đi trình cơ quan; không có cam kết phiếu ăn.", "p4-action"),
 ], {"title": "Morning shuttles", "columns": ["Departure", "Destination", "Platform"], "rows": [["08:20","West Park","3"],["08:30","North Gate","2"],["08:40","Harbor","1"],["08:50","West Park","3"],["09:10","Airport","4"]]})
group("graphic-talk-2", 4,
 "Thank you for your interest in our business-writing classes. The short course is intended for learners who want to focus only on email. For staff who also prepare proposals, we recommend the course that includes individual feedback but does not include a live presentation. The listed prices already include materials. If you register by Friday, enter your employee number to receive a ten-dollar reduction. Do not deduct any further materials charge when calculating the fee.", [
 ("What is the main purpose of the message?", ["To help learners select a course", "To announce an office closure", "To recruit writing instructors", "To request overdue payment"], "Người nói đối chiếu mục tiêu và tính năng các khóa, nên đang hướng dẫn chọn khóa.", "p4-purpose"),
 ("Look at the graphic. How much will the recommended course cost with the reduction?", ["$80", "$50", "$90", "$120"], "Khóa Plus có feedback, không presentation: 90 đô la. Giảm 10 còn 80; tài liệu đã gồm trong giá nên không trừ thêm.", "p4-graphic"),
 ("What should employees enter to obtain the reduction?", ["Their employee number", "A materials code", "An instructor's email address", "A previous certificate number"], "Enter your employee number là thao tác nhận ưu đãi khi đăng ký đúng hạn.", "p4-action"),
 ], {"title": "Writing courses", "columns": ["Course", "Focus", "Individual feedback", "Live presentation", "Price"], "rows": [["Short","Email","No","No","$60"],["Plus","Email and proposals","Yes","No","$90"],["Complete","Email and proposals","Yes","Yes","$130"]]})

for n, (prompt, choices, why, topic) in enumerate([
 ("All obsolete access cards must ____ before employees leave.", ["be returned","return","returning","have returning"], "Cards nhận hành động; modal must cần be + V3: be returned.", "p5-passive"),
 ("Yesterday, the laboratory samples ____ by an independent inspector.", ["were examined","examines","have examining","examining"], "Yesterday xác lập quá khứ; samples số nhiều nhận hành động examined nên were examined.", "p5-passive"),
 ("The room is unavailable because it ____ at the moment.", ["is being cleaned","cleans","has cleaning","will cleaning"], "At the moment và phòng không dùng được cho thấy đang được dọn: hiện tại tiếp diễn bị động.", "p5-passive"),
 ("Every visitor badge ____ at reception before it is issued.", ["is checked","checks","checking","has checking"], "Mỗi thẻ được kiểm tra, chủ ngữ số ít: is checked. Checks sẽ là chủ động và thiếu đối tượng phù hợp.", "p5-passive"),
 ("The shipment cannot ____ until customs releases the documents.", ["be delivered","deliver","delivering","have delivering"], "Lô hàng được giao, nên sau cannot cần be delivered. Until nêu điều kiện thời gian chờ giấy tờ.", "p5-passive"),
 ("Several errors have ____ in the draft report.", ["been found","found","been finding","being found"], "Các lỗi đã được phát hiện: have been found, hiện tại hoàn thành bị động.", "p5-passive"),
 ("Please send the signed contract to ____ before noon.", ["her","she","hers","herself"], "Sau giới từ to cần đại từ tân ngữ her; she là chủ ngữ, hers thay cụm sở hữu.", "p5-pronouns"),
 ("These lockers belong to our team; the ones by the window are ____.", ["ours","our","us","we"], "Ours là đại từ sở hữu đứng độc lập sau are, thay our lockers. Our cần danh từ theo sau.", "p5-pronouns"),
 ("Because no assistant was available, Mr. Hall completed the inventory ____.", ["himself","his","he","him"], "Himself nhấn mạnh chính ông Hall tự làm vì không có trợ lý. His cần danh từ trong vai trò tính từ sở hữu.", "p5-pronouns"),
 ("The director asked Nina and ____ to review the contract.", ["me","I","my","mine"], "Ask nhận tân ngữ Nina and me. Không dùng I chỉ vì có and; thử bỏ Nina and sẽ thấy asked me.", "p5-pronouns"),
 ("We received ____ complaints this month than last month.", ["fewer","less","much","little"], "Complaints đếm được số nhiều, có than nên fewer là so sánh ít hơn phù hợp.", "p5-quantity"),
 ("Only ____ advice was needed before the team could proceed.", ["a little","a few","many","several"], "Advice không đếm được; a little advice là một ít lời khuyên. Không dùng a few/many/several trực tiếp với advice.", "p5-quantity"),
 ("How ____ spare keyboards are stored in this cabinet?", ["many","much","little","every"], "Keyboards đếm được số nhiều nên hỏi how many. How much dùng cho lượng không đếm được.", "p5-quantity"),
 ("Each branch has received ____ copy of the revised handbook.", ["one","many","several","both"], "Copy ở số ít nên one copy. Các từ many/several/both cần danh từ số nhiều copies.", "p5-quantity"),
 ("It is essential that every submitted form ____ complete.", ["be","been","being","to be"], "Cấu trúc giả định sau it is essential that dùng nguyên mẫu be, dù chủ ngữ every form là số ít.", "p5-advanced"),
 ("Had the supplier notified us earlier, we ____ the shipment.", ["would have postponed","will postpone","had postponing","would postponing"], "Had…the supplier notified là điều kiện quá khứ đảo ngữ; kết quả giả định dùng would have + V3.", "p5-advanced"),
 ("Only after the repairs were finished ____ reopen.", ["did the store","the store did","the store was","was the store"], "Only after ở đầu làm đảo trợ động từ mệnh đề chính: did the store reopen. Reopen là nguyên mẫu sau did.", "p5-advanced"),
 ("Never before ____ such a detailed proposal.", ["have we received","we have received","we received","received we"], "Never before đứng đầu cần đảo have và chủ ngữ: have we received.", "p5-advanced"),
 ("The number of requests ____ increased since Monday.", ["has","have","are","were"], "The number là chủ ngữ số ít, dùng has increased. Of requests không quyết định số của động từ.", "p5-agreement"),
 ("One of the storage rooms ____ reserved for medical supplies.", ["is","are","have","being"], "One là trung tâm số ít, nên is reserved. Rooms chỉ nằm trong cụm of the storage rooms.", "p5-agreement"),
 ("Both the accountant and the supervisor ____ available now.", ["are","is","was","has"], "Both…and tạo chủ ngữ ghép số nhiều; available cần be, nên are.", "p5-agreement"),
 ("The revised instructions seem ____ to new employees.", ["clear","clearly","clarity","clarify"], "Seem là động từ nối, theo sau bằng tính từ clear mô tả instructions. Không dùng clearly như sau động từ hành động.", "p5-word-form"),
 ("The software automatically checks the ____ of each address.", ["accuracy","accurate","accurately","inaccurate"], "Sau the và trước of cần danh từ accuracy, độ chính xác. Accurate/accurately là tính từ/trạng từ.", "p5-word-form"),
 ("The presentation was ____ organized despite the short preparation time.", ["carefully","careful","care","cares"], "Carefully bổ nghĩa phân từ organized, diễn tả được tổ chức cẩn thận. Careful là tính từ.", "p5-word-form"),
], 1):
    question(f"p5-{n:02}", 5, prompt, choices, why, topic)

group("insertion-1", 7,
 "TRAINING REGISTRATION\n\nThe safety office is offering induction training next week. [1] There will be two sessions, on Tuesday morning and Wednesday afternoon. [2] The first group must bring a contractor ID; the second should bring an employee badge. Registration closes on Monday at noon. [3] The usual registration fee will be waived for anyone who signs up before that deadline. [4] Confirmation emails will include a link to the training materials.", [
 ("Where does this sentence best belong? 'These two sessions serve different audiences: contractors on Tuesday and employees on Wednesday.'", ["Position [2]","Position [1]","Position [3]","Position [4]"], "These two sessions cần đứng sau câu giới thiệu hai buổi; the first group/the second ngay sau cần biết hai nhóm người. Chỉ [2] nối đủ hai phía.", "p7-insertion"),
 ("The word 'waived' is closest in meaning to", ["not charged","paid twice","postponed indefinitely","increased"], "Phí được waived nghĩa là được miễn, không bị tính; không phải chỉ hoãn trả hoặc tăng phí.", "p7-vocabulary"),
 ("What is suggested about someone registering on Monday morning?", ["The usual registration fee will not apply","They must attend both sessions","They will receive a contractor ID","They can register without a confirmation email"], "Sáng thứ Hai trước hạn trưa nên đáp ứng điều kiện miễn phí; không có bằng chứng phải dự cả hai buổi.", "p7-inference"),
])
group("insertion-2", 7,
 "LIBRARY COLLECTIONS\n\nOur reference collection is moving to the east wing. [1] The old reading room will close on Friday for the move. Visitors who need reference books during the closure may request them through the online catalog. [2] They will receive a collection message when the requested items are ready. [3] Please retain this message until you have collected all of your items. [4] The east-wing reading room opens on Monday.", [
 ("Where does this sentence best belong? 'Those who choose this online option should allow one working day for staff to retrieve the books.'", ["Position [2]","Position [1]","Position [3]","Position [4]"], "This online option tham chiếu câu đặt sách qua catalog; They ở câu sau tiếp tục nói về nhóm này. [2] giữ chuỗi yêu cầu → xử lý → thông báo, trước khi chuyển sang hướng dẫn giữ tin.", "p7-insertion"),
 ("The word 'retain' is closest in meaning to", ["keep","delete","rewrite","publish"], "Retain this message until collection yêu cầu giữ tin nhắn để nhận đủ đồ; không phải xóa hay công khai nó.", "p7-vocabulary"),
 ("What can visitors do while the old reading room is closed?", ["Request reference books online","Enter the old room after hours","Collect any book without notice","Use the east wing on Friday"], "Văn bản cho phép đặt sách qua catalog trong thời gian đóng; phòng đông chỉ mở thứ Hai.", "p7-detail"),
])
group("insertion-3", 7,
 "SERVICE UPDATE\n\nOur appointment website is undergoing maintenance this morning. [1] Customers cannot create or change appointments online until noon. The support team has set up a temporary telephone booking line. [2] It will use the same appointment database as the website, so existing reservations remain valid. [3] Once online service has resumed, callers will receive written confirmation of any changes made by phone. [4] We appreciate your patience.", [
 ("Where does this sentence best belong? 'This alternative service can be reached at the number printed on your membership card.'", ["Position [2]","Position [1]","Position [3]","Position [4]"], "This alternative service cần tiền đề telephone booking line, rồi It tiếp tục mô tả cùng dịch vụ. [2] đưa cách liên hệ trước phần giải thích dữ liệu và xác nhận.", "p7-insertion"),
 ("The word 'resumed' is closest in meaning to", ["started again","been removed permanently","been paid for","slowed down"], "Resumed nghĩa là hoạt động trở lại sau bảo trì, không phải xóa vĩnh viễn hoặc chỉ giảm tốc độ.", "p7-vocabulary"),
 ("What is indicated about existing reservations?", ["They will remain valid during maintenance","They must all be canceled","They are stored in a separate paper system","They will move automatically to noon"], "Cùng database và existing reservations remain valid xác nhận không cần đặt lại mọi lịch cũ.", "p7-inference"),
])
group("insertion-4", 7,
 "PROFESSIONAL DEVELOPMENT FUND\n\nThe company has opened applications for its annual learning fund. [1] Both permanent employees and fixed-term staff may apply. [2] They must have completed six months of service by the course start date. Applicants should explain how the course supports their current role. [3] Eligible applicants will be contacted for a short discussion before any payment is approved. [4] Approval is required before enrolling on a paid course.", [
 ("Where does this sentence best belong? 'Members of these two staff groups are subject to the same service-length requirement.'", ["Position [2]","Position [1]","Position [3]","Position [4]"], "These two staff groups cần đứng sau hai loại nhân viên; câu kế tiếp giải thích service-length requirement là sáu tháng. [2] tạo chuỗi tham chiếu rõ nhất.", "p7-insertion"),
 ("The word 'eligible' is closest in meaning to", ["qualified to apply","already reimbursed","unable to attend","required to resign"], "Eligible là đáp ứng điều kiện. Đủ điều kiện chưa đồng nghĩa đã được thanh toán hay phê duyệt.", "p7-vocabulary"),
 ("What should an applicant do before enrolling on a paid course?", ["Obtain approval","Pay the fee personally","Complete twelve months of service","Resign from a fixed-term position"], "Câu cuối yêu cầu approval trước khi đăng ký khóa có phí; không phải cứ eligible là tự động được hoàn tiền.", "p7-detail"),
])
