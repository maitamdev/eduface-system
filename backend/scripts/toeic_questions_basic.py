def grammar(lid, rows):
    for row in rows:
        prompt, choices, explanation = row
        question(lid, 5, prompt, choices, explanation)


grammar("f02", [
 ("The assistant _____ the visitor's name every morning.", ["checks", "checking", "check", "to check"], "Chủ ngữ the assistant số ít; every morning chỉ thói quen nên dùng checks. Checking cần trợ động từ; to check không tự làm động từ chính."),
 ("Please read the instructions _____.", ["carefully", "careful", "care", "carefulness"], "Chỗ trống bổ nghĩa cách read nên cần trạng từ carefully, không phải tính từ careful."),
 ("The new printer is very _____.", ["efficient", "efficiency", "efficiently", "efficiencies"], "Sau be và very cần tính từ chỉ đặc điểm: efficient. Efficiency là danh từ, efficiently là trạng từ."),
 ("We need an _____ report before the meeting.", ["accurate", "accurately", "accuracy", "accuracies"], "Trước danh từ report cần tính từ accurate. An phù hợp với âm nguyên âm đầu của accurate."),
 ("All employees must _____ their badges.", ["wear", "wears", "wearing", "wore"], "Sau động từ khuyết thiếu must dùng động từ nguyên mẫu không to: wear."),
 ("The manager asked for more _____.", ["information", "inform", "informative", "informatively"], "Sau more ở vị trí tân ngữ cần danh từ information. Đây là danh từ không đếm được, không thêm -s."),
 ("This is _____ office key.", ["an", "a", "many", "some"], "Office bắt đầu bằng âm nguyên âm; key là danh từ đếm được số ít nên dùng an."),
 ("The files are on _____ desk.", ["her", "she", "hers", "herself"], "Trước danh từ desk cần tính từ sở hữu her. Hers dùng độc lập, không đứng trực tiếp trước desk."),
 ("Our team _____ ready for the presentation.", ["is", "be", "being", "to be"], "Trong câu này team được xem là một đơn vị số ít; is là động từ đã chia. Các lựa chọn khác không tạo vị ngữ hoàn chỉnh."),
 ("The receptionist speaks English _____.", ["fluently", "fluent", "fluency", "fluentness"], "Chỗ trống mô tả cách speaks, nên dùng trạng từ fluently."),
 ("Please _____ the documents by date.", ["organize", "organization", "organized", "organizes"], "Câu mệnh lệnh Please + động từ nguyên mẫu: organize. Không chia -s dù người nhận là số ít."),
 ("We bought two new _____ for the office.", ["desks", "desk", "desking", "desk's"], "Sau two cần danh từ đếm được số nhiều desks. Desk's là sở hữu cách, không chỉ số nhiều.")])

grammar("f03", [
 ("Please _____ the receipt to your expense claim.", ["attach", "attend", "arrive", "achieve"], "Attach something to something là đính kèm một thứ vào thứ khác. Attend là tham dự; arrive không nhận tân ngữ trực tiếp như vậy."),
 ("The team worked late to _____ the deadline.", ["meet", "watch", "look", "visit"], "Meet a deadline là hoàn thành đúng hạn. Meet ở đây không mang nghĩa gặp một người."),
 ("The printer is out of _____. Please refill the tray.", ["paper", "meetings", "visitors", "tickets"], "Refill the tray và printer xác định ngữ cảnh hết giấy. Out of paper là cụm thông dụng."),
 ("Could you make an _____ with the dentist?", ["appointment", "equipment", "information", "attendance"], "Make an appointment là đặt lịch hẹn. Ba từ còn lại không phù hợp cụm từ và nghĩa."),
 ("All supervisors will _____ the safety meeting.", ["attend", "attach", "repair", "print"], "Attend a meeting là tham dự cuộc họp; không cần giới từ trước meeting."),
 ("Please keep the _____ as proof of payment.", ["receipt", "schedule", "agenda", "draft"], "Receipt chứng minh đã thanh toán. Agenda và schedule liên quan kế hoạch, không chứng minh trả tiền."),
 ("The company will _____ employees for approved travel expenses.", ["reimburse", "reserve", "recruit", "replace"], "Reimburse someone for expenses là hoàn trả chi phí cho người đó. Recruit là tuyển dụng."),
 ("We ordered pens, envelopes, and other _____.", ["stationery", "stationary", "stations", "stationed"], "Stationery là văn phòng phẩm. Stationary là tính từ nghĩa đứng yên; đây là cặp từ dễ nhầm."),
 ("The supplier sent an _____ requesting payment within thirty days.", ["invoice", "invitation", "interview", "inspection"], "Invoice là hóa đơn yêu cầu thanh toán; requesting payment giúp xác định nghĩa."),
 ("Please _____ these records in the cabinet.", ["file", "attend", "announce", "borrow"], "File records là lưu/sắp xếp hồ sơ. Cabinet là tủ hồ sơ, phù hợp ngữ cảnh.")])

grammar("b03", [
 ("The list of suppliers _____ on the manager's desk.", ["is", "are", "have", "were"], "Chủ ngữ chính là list số ít. Of suppliers chỉ bổ nghĩa và không làm động từ thành số nhiều."),
 ("We _____ the order yesterday afternoon.", ["shipped", "have shipped", "will ship", "ship"], "Yesterday afternoon là thời gian quá khứ đã kết thúc nên dùng quá khứ đơn shipped."),
 ("She has worked at this branch _____ 2022.", ["since", "for", "during", "by"], "Since đi với mốc bắt đầu; 2022 là một mốc. For cần một khoảng thời gian như four years."),
 ("The two printers _____ serviced every month.", ["are", "is", "has", "be"], "Chủ ngữ printers số nhiều và câu bị động hiện tại đơn: are serviced."),
 ("The technician _____ the system right now.", ["is testing", "tested", "tests", "has test"], "Right now nhấn mạnh hành động đang diễn ra; hiện tại tiếp diễn is testing phù hợp."),
 ("By the time the guests arrived, we _____ the room.", ["had prepared", "prepare", "will prepare", "are preparing"], "Việc chuẩn bị xảy ra trước một mốc quá khứ khác, nên dùng quá khứ hoàn thành had prepared."),
 ("Each of the new employees _____ a security badge.", ["receives", "receive", "receiving", "to receive"], "Each là chủ ngữ số ít dù theo sau có employees; động từ hiện tại thêm -s."),
 ("The company has operated here _____ ten years.", ["for", "since", "at", "until"], "Ten years là khoảng thời gian nên dùng for, không dùng since."),
 ("Please call me when the package _____.", ["arrives", "will arrive", "arriving", "to arrive"], "Mệnh đề thời gian với when nói tương lai thường dùng hiện tại đơn, không dùng will ở đây."),
 ("The director _____ the results at tomorrow's briefing.", ["will announce", "announced", "has announcing", "announce"], "Tomorrow's briefing là mốc tương lai; will announce phù hợp và đủ cấu trúc."),
 ("Neither of the two proposals _____ within our budget.", ["is", "are being", "have been", "be"], "Neither of ở cấu trúc chuẩn này lấy động từ số ít; is within our budget diễn tả trạng thái."),
 ("The courier has _____ left, so the parcel must wait until tomorrow.", ["already", "yet", "still", "ever"], "Has already left là đã rời đi. Yet thường ở câu hỏi/phủ định; still ở đây cần cấu trúc khác.")])

grammar("i03", [
 ("All expense forms must _____ by a supervisor.", ["be signed", "sign", "signing", "have sign"], "Forms nhận hành động ký, nên must + be + quá khứ phân từ: be signed."),
 ("The designer _____ joined yesterday will lead the project.", ["who", "whose", "where", "when"], "Đại từ quan hệ thay người và làm chủ ngữ của joined: who. Whose phải đi với danh từ sở hữu."),
 ("_____ the heavy rain, the outdoor tour continued.", ["Despite", "Although", "Because", "While"], "Theo sau là cụm danh từ the heavy rain, cần despite. Although/while/because cần mệnh đề trong cấu trúc này."),
 ("The event was delayed _____ the speaker's flight was canceled.", ["because", "because of", "despite", "during"], "Theo sau là mệnh đề có chủ ngữ và động từ, vì vậy because phù hợp; because of cần cụm danh từ."),
 ("The employee _____ badge was lost reported it to security.", ["whose", "who", "whom", "which"], "Badge thuộc sở hữu của employee, nên dùng whose badge."),
 ("The machines _____ every six months to ensure safety.", ["are inspected", "inspect", "are inspecting", "have inspect"], "Machines được kiểm tra định kỳ: hiện tại đơn bị động are inspected."),
 ("_____ the room is small, it can accommodate the entire team.", ["Although", "Despite", "Because of", "During"], "Có mệnh đề the room is small và ý tương phản, nên although. Despite không đi trực tiếp với mệnh đề đầy đủ ở đây."),
 ("This is the office _____ the interviews will take place.", ["where", "who", "whose", "which"], "Where thay cụm nơi chốn in the office. Which cần giới từ hoặc một cấu trúc khác."),
 ("The application will not be processed _____ all documents are received.", ["until", "despite", "during", "because of"], "Not…until nghĩa là chỉ xử lý sau khi nhận đủ hồ sơ. Ba lựa chọn còn lại không nối được mệnh đề theo nghĩa cần có."),
 ("The new policy, _____ takes effect on Monday, applies to all staff.", ["which", "who", "whose", "where"], "Which mở mệnh đề quan hệ bổ sung về policy, một sự vật. Dấu phẩy không dùng that trong mệnh đề không xác định.")])

grammar("u03", [
 ("Guests receive a _____ breakfast with every overnight stay.", ["complimentary", "complementary", "compliment", "complement"], "Complimentary là miễn phí/được tặng. Complementary nghĩa là bổ trợ lẫn nhau, không phải miễn phí."),
 ("The smaller vehicle is more _____ to operate because it uses less fuel.", ["economical", "economic", "economy", "economically"], "Economical chỉ tiết kiệm chi phí. Economic nói về kinh tế; sau more ở đây cần tính từ."),
 ("The order will remain on hold _____ payment is received.", ["unless", "although", "despite", "during"], "Unless payment is received = nếu không nhận được thanh toán. Điều kiện giải phóng đơn hàng là có tiền."),
 ("You may extend the booking _____ the room is still available.", ["provided that", "in spite of", "because of", "regardless of"], "Provided that + mệnh đề đặt điều kiện. Các cụm còn lại cần cấu trúc/nghĩa khác."),
 ("Had we known about the closure, we _____ another route.", ["would have taken", "will take", "would take", "have taken"], "Had we known là đảo ngữ của if we had known: điều kiện trái quá khứ, dùng would have taken."),
 ("The offer is contingent _____ a satisfactory inspection.", ["on", "at", "for", "with"], "Cụm cố định contingent on = phụ thuộc vào điều kiện nào đó."),
 ("The new process resulted in a _____ reduction in waste.", ["substantial", "substantially", "substance", "substantiate"], "Trước danh từ reduction cần tính từ substantial nghĩa là đáng kể."),
 ("The deadline was tight; _____, the team completed the work on time.", ["nevertheless", "consequently", "therefore", "similarly"], "Hai vế tương phản: khó vì hạn gấp nhưng vẫn hoàn thành. Nevertheless nối tương phản; consequently/therefore nối kết quả."),
 ("Employees are required to comply _____ the updated safety policy.", ["with", "to", "for", "on"], "Comply with là tuân thủ một quy định. Đây là collocation cần nhớ theo cụm."),
 ("No sooner had the presentation started _____ the power went out.", ["than", "when", "that", "then"], "Cấu trúc no sooner…than diễn tả vừa xảy ra việc này thì việc kia xảy ra. Hardly…when là cấu trúc khác.")])


def response(lid, spoken, choices, explanation):
    row = question(lid, 2, "Listen to the question or statement. Choose the best response.", choices, explanation)
    row["audio_id"] = row["id"]
    row["transcript"] = spoken + "\n" + "\n".join(f"{chr(65+i)}. {text}" for i, text in enumerate(row["options"]))


for args in [
 ("What time does the meeting begin?", ["At half past nine.", "In the main office.", "About ten people."], "What time hỏi giờ; half past nine là 9:30. Địa điểm và số người không trả lời câu hỏi."),
 ("How many copies do you need?", ["Thirty, please.", "At three o'clock.", "For half an hour."], "How many hỏi số lượng, đáp án thirty là 30 bản. Hai câu kia là giờ và khoảng thời gian."),
 ("Where is the reception desk?", ["Beside the main entrance.", "It opens at eight.", "Ms. Lee is the receptionist."], "Where hỏi vị trí. Receptionist là người làm tiếp tân, không phải vị trí quầy."),
 ("Who handles the invoices?", ["Mina in accounting.", "On the last day of the month.", "There are three copies."], "Who hỏi người phụ trách; Mina là người ở bộ phận kế toán."),
 ("How long is the factory tour?", ["About two hours.", "At two in the afternoon.", "Two tickets, please."], "How long hỏi thời lượng, about two hours. At two là mốc giờ, không phải thời lượng."),
 ("When will the delivery arrive?", ["On Thursday morning.", "At the loading dock.", "The driver is friendly."], "When hỏi thời điểm; Thursday morning đáp ứng. Loading dock là nơi nhận hàng."),
 ("How much is the visitor pass?", ["Fifteen dollars.", "Fifty visitors.", "In fifteen minutes."], "How much hỏi giá trong ngữ cảnh pass, nên chọn số tiền; không nhầm fifteen với fifty."),
 ("Which floor is the training room on?", ["The fourth floor.", "Four trainees.", "At four thirty."], "Which floor hỏi tầng. Fourth là số thứ tự, còn four trainees là số người."),
 ("Could you tell me your extension number?", ["It's three two six.", "The meeting was extended.", "I'll stay for six days."], "Extension number là số máy lẻ. Extended có âm/từ gần giống nhưng không trả lời yêu cầu."),
 ("What day is the workshop?", ["Next Tuesday.", "At the city library.", "It's about design."], "What day hỏi ngày, không hỏi nơi tổ chức hoặc chủ đề.")]: response("f01", *args)

for args in [
 ("Could you print these forms?", ["Sure. How many copies?", "The form is rectangular.", "I attended the meeting."], "Could you… là lời nhờ; câu hỏi số bản in chấp nhận và làm rõ yêu cầu."),
 ("Would you prefer tea or coffee?", ["Tea, please.", "At the coffee shop.", "I paid yesterday."], "Câu hỏi lựa chọn đồ uống; Tea chọn một phương án. Đừng chọn chỉ vì nghe thấy coffee."),
 ("Why is the meeting room locked?", ["The cleaners are still inside.", "On the second floor.", "Yes, I attended."], "Why cần lý do. Nhân viên vệ sinh đang ở trong giải thích vì sao phòng khóa."),
 ("May I borrow your stapler?", ["Of course. It's on my desk.", "I borrowed the book yesterday.", "Three staples are enough."], "Đây là lời xin mượn; Of course cùng vị trí dụng cụ trả lời tự nhiên."),
 ("Should we meet today or tomorrow?", ["Tomorrow works better for me.", "The meeting room is large.", "I met the new employee."], "Tomorrow lựa chọn thời điểm. Hai câu còn lại lặp meet/meeting nhưng không giải quyết lịch hẹn."),
 ("Can you return the key before six?", ["Yes, I'll bring it back by five.", "There are six keys.", "The key is made of metal."], "By five sớm hơn before six, thể hiện nhận lời và đáp ứng thời hạn."),
 ("Would you like me to reserve a table?", ["That would be helpful, thanks.", "The table is wooden.", "I like reading."], "Lời đề nghị giúp đặt bàn được đáp bằng sự đồng ý cảm ơn. Like ở lựa chọn khác chỉ là bẫy từ lặp."),
 ("How do I get to the station?", ["Take the number eight bus.", "It leaves at eight.", "The station manager called."], "How do I get to hỏi cách đi; tuyến xe buýt là thông tin cần, không phải giờ khởi hành chưa rõ chủ thể."),
 ("Please confirm the number of guests.", ["There will be twelve of us.", "The guest room is upstairs.", "I confirmed the address."], "Number of guests cần số lượng khách; twelve trả lời trực tiếp."),
 ("Can we reschedule the interview?", ["I'll check the manager's calendar.", "I read the interview online.", "The schedule is printed in blue."], "Kiểm tra lịch là bước phù hợp khi được nhờ đổi lịch phỏng vấn; không phải thông tin về màu bản in."),
 ("Which of these two rooms is available?", ["Neither; both are booked.", "The building is tall.", "Two people have arrived."], "Neither; both are booked trả lời rằng không phòng nào rảnh. Câu hỏi which có thể nhận đáp án phủ định cả hai."),
 ("Could you speak a little more slowly?", ["Certainly. Let me repeat that.", "The speaker is on the shelf.", "We were late for lunch."], "Repeat that là phản hồi phù hợp khi người nghe cần nghe rõ hơn. Speaker trong đáp án khác là thiết bị.")]: response("b02", *args)

for args in [
 ("Can we use the large conference room this morning?", ["It's booked until noon.", "The conference was interesting.", "Yes, it's a large company."], "Booked until noon gián tiếp nói phòng chưa dùng được trong buổi sáng. Không cần có từ no."),
 ("Who is driving to the client meeting?", ["I haven't brought my car today.", "The client signed the form.", "The road is being repaired next year."], "Người trả lời gián tiếp cho biết mình không thể là người lái. Các câu còn lại không giải quyết việc đi lại hôm nay."),
 ("Has the courier arrived yet?", ["There's a parcel at reception.", "I prefer email.", "The reception was held last year."], "Có bưu kiện ở quầy là bằng chứng gián tiếp việc giao hàng đã diễn ra."),
 ("Don't we need to submit the budget today?", ["The deadline was extended to Friday.", "Today's lunch was excellent.", "The budget is printed on paper."], "Gia hạn đến thứ Sáu giải thích vì sao không cần nộp hôm nay. Đây là đáp án điều chỉnh giả định của người hỏi."),
 ("Wouldn't the express service be faster?", ["It would, but it costs twice as much.", "Yes, the office is upstairs.", "I always express my opinion."], "Đáp án thừa nhận nhanh hơn nhưng nêu đánh đổi về chi phí; express trong câu khác là nghĩa khác."),
 ("Where did you put the spare cable?", ["Try the drawer under the printer.", "I put the meeting on my calendar.", "It's two meters long."], "Try the drawer đưa nơi cần tìm. Chiều dài dây không trả lời where."),
 ("Is the presentation ready for tomorrow?", ["I'm still waiting for the sales figures.", "Tomorrow is Wednesday.", "The presenter arrived by train."], "Still waiting for sales figures hàm ý bài chưa hoàn thiện vì thiếu dữ liệu."),
 ("Could someone cover my shift on Saturday?", ["I'll ask whether Elena is free.", "The cover is blue.", "Saturday's newspaper is on the table."], "Lời hứa hỏi Elena có rảnh giải quyết việc tìm người thay ca. Cover là bẫy đa nghĩa."),
 ("The chairs haven't arrived, have they?", ["The driver called to say he's five minutes away.", "Yes, the chairs are comfortable.", "I prefer the blue design."], "Tài xế còn cách năm phút cho biết hàng chưa đến nhưng sắp đến. Không chọn mô tả chất lượng ghế."),
 ("Do we have enough time to add another stop?", ["The museum closes in twenty minutes.", "The bus stop is clean.", "I added your name yesterday."], "Giờ đóng cửa sắp tới là lý do gián tiếp cho thấy thời gian hạn chế. Đây là thông tin liên quan đến quyết định có ghé thêm không.")]: response("i01", *args)


def notice(lid, passage, prompt, choices, explanation):
    question(lid, 7, prompt, choices, explanation, passage=passage)


for args in [
 ("NOTICE: The west entrance is closed for repairs. Please use the east entrance until Monday.", "What should visitors do?", ["Use the east entrance.", "Wait outside until Monday.", "Enter through the west door.", "Call the repair company."], "Thông báo chỉ dẫn dùng east entrance. Không yêu cầu chờ đến thứ Hai hay liên hệ đơn vị sửa chữa."),
 ("Library reminder: Please return borrowed laptops by 5 p.m. today. Books may be returned next week.", "What must be returned today?", ["Borrowed laptops", "All books", "Employee badges", "Library chairs"], "Laptops phải trả trước 5 giờ hôm nay; books có thời hạn khác vào tuần sau."),
 ("Visitors must sign in at reception and wear a visitor badge while in the building.", "What is required of visitors?", ["Wearing a visitor badge", "Bringing a passport photo", "Buying a ticket", "Calling the director"], "Wear a visitor badge được nêu rõ. Các yêu cầu khác không xuất hiện."),
 ("Café update: Our kitchen closes at 3 p.m., but drinks are available until 5 p.m.", "What can a customer buy at 4 p.m.?", ["A drink", "A hot lunch", "A cooked dinner", "A kitchen appliance"], "Kitchen đóng lúc 3 giờ nhưng drinks vẫn bán đến 5 giờ, nên 4 giờ còn mua đồ uống."),
 ("Parking Zone B is reserved for delivery vehicles. Employees should use Zone C.", "Who should park in Zone C?", ["Employees", "Delivery drivers", "Tour bus drivers", "Construction workers"], "Employees should use Zone C nêu trực tiếp. Zone B dành cho phương tiện giao hàng."),
 ("Message: Lan, the printer paper arrived. I left it beside your desk, not in the supply cabinet. — Ben", "Where is the paper?", ["Beside Lan's desk", "In the supply cabinet", "At the front gate", "Inside the printer"], "Người gửi sửa lại vị trí thường đoán: beside your desk, not in the supply cabinet."),
 ("Workshop registration closes on Thursday. Participants will receive room details by email on Friday.", "When will room information be sent?", ["On Friday", "On Thursday", "During the workshop", "Next month"], "Thursday là hạn đăng ký; Friday là ngày gửi thông tin phòng. Cần phân biệt hai sự kiện."),
 ("Please keep this receipt. Returns without proof of purchase cannot be accepted.", "Why should customers keep the receipt?", ["To support a return", "To reserve a parking space", "To receive a job offer", "To enter the building"], "Receipt là proof of purchase cần cho việc trả hàng; không có ưu đãi hay mục đích khác được nêu."),
 ("The elevator is temporarily out of service. The stairs are located opposite the restrooms.", "Where are the stairs?", ["Opposite the restrooms", "Inside the elevator", "Next to the loading dock", "Behind the reception desk"], "Located opposite the restrooms là bằng chứng vị trí. Temporarily không có nghĩa thang máy bị tháo bỏ vĩnh viễn."),
 ("Reminder: Bring your employee ID to the training session. Printed invitations are not necessary.", "What should participants bring?", ["Their employee ID", "A printed invitation", "A bank statement", "A laptop charger"], "Employee ID là yêu cầu; printed invitations được nói rõ là không cần."),
 ("Call before visiting the showroom. Staff can arrange appointments between 10 a.m. and 4 p.m.", "What should a visitor do first?", ["Telephone the showroom", "Arrive before 10 a.m.", "Pay an entrance fee", "Send a résumé"], "Call before visiting là hành động đầu tiên được yêu cầu. Khoảng giờ dành cho cuộc hẹn, không phải yêu cầu đến trước 10 giờ."),
 ("Lost property: A blue umbrella was found in Meeting Room 2. Its owner can collect it from security.", "Where can the owner collect the umbrella?", ["From security", "From Meeting Room 2", "From the café", "From the parking office"], "Room 2 là nơi tìm thấy; security mới là nơi nhận lại. Bẫy thường dùng vị trí xuất hiện trước trong bài.")]: notice("f04", *args)

for args in [
 ("Subject: Revised quotation\nDear Ms. Park, Thank you for the quotation. Please send a revised version that includes installation. We do not need the optional maintenance package. Regards, Tom.", "What does Tom request?", ["A quote including installation", "An invoice for maintenance", "A cancellation of the order", "A list of employees"], "Please send a revised version that includes installation là yêu cầu chính. Maintenance được loại ra."),
 ("Subject: Application received\nThank you for applying. We have received your documents and will review them next week. Shortlisted candidates will be contacted by phone.", "What does this email confirm?", ["Receipt of application documents", "A job offer", "An interview time", "A salary increase"], "Have received xác nhận nhận hồ sơ. Review next week và shortlisted mới sẽ được gọi nên chưa có lời mời làm việc."),
 ("Subject: Room change\nTomorrow's training will take place in Room 5 instead of Room 3. The starting time, 9 a.m., remains unchanged.", "What has changed?", ["The training room", "The training date", "The starting time", "The instructor"], "Instead of Room 3 chỉ sự đổi phòng. Starting time remains unchanged loại đáp án đổi giờ."),
 ("Dear team, Please review the attached agenda and send any additional topics by noon Wednesday. I will circulate the final version on Thursday.", "What should team members do by Wednesday noon?", ["Suggest additional topics", "Distribute the final agenda", "Attend the meeting", "Print the annual report"], "Send any additional topics by noon Wednesday là yêu cầu. Circulate Thursday là việc người gửi sẽ làm."),
 ("Subject: Delivery update\nYour order has left our warehouse. It is expected to arrive on Tuesday. You will receive a tracking link later today.", "What has already happened?", ["The order has left the warehouse.", "The customer has received the order.", "The tracking link has been sent.", "The order has been canceled."], "Has left là việc đã xảy ra. Expected to arrive và will receive đều là việc chưa hoàn tất."),
 ("Hello Mira, Could you confirm whether you can attend the client lunch on Friday? Please let me know by tomorrow afternoon so I can finalize the reservation.", "Why does the sender need a reply?", ["To finalize a reservation", "To change a flight", "To approve an expense", "To return an item"], "So I can finalize the reservation nêu lý do cần phản hồi. Không có chuyến bay hay chi phí trong bài."),
 ("Subject: Temporary closure\nOur store will close on May 8 for an inventory check. Online orders will still be accepted and will be dispatched on May 9.", "What can customers do on May 8?", ["Place an online order", "Visit the store", "Collect a dispatched order at the store", "Join the inventory team"], "Online orders will still be accepted là hoạt động còn thực hiện được. Dispatch được dời sang ngày 9."),
 ("Dear customer, We apologize for sending the wrong size. A replacement will be shipped today. Please use the enclosed prepaid label to return the original item.", "How should the customer return the item?", ["Using the enclosed prepaid label", "By paying cash at the warehouse", "By visiting the head office", "By waiting for next month's invoice"], "Use the enclosed prepaid label là hướng dẫn trả hàng. Prepaid cho biết phí nhãn đã được thanh toán."),
 ("Subject: Updated schedule\nPlease ignore the schedule sent yesterday. The attached document includes the correct workshop times. The venue has not changed.", "Which information should recipients use?", ["The newly attached schedule", "Yesterday's schedule", "A new venue address", "An earlier draft"], "Ignore yesterday's schedule và attached correct times khẳng định lịch mới thay lịch cũ, không đổi địa điểm."),
 ("Dear Mr. Cole, Your reservation is confirmed for six guests at 7 p.m. Please notify us in advance if anyone has dietary restrictions.", "What information does the restaurant request?", ["Any dietary restrictions", "The guests' salaries", "A new arrival date", "Payment card numbers by email"], "Notify us…dietary restrictions là yêu cầu. Việc đặt bàn đã xác nhận, không cần thay ngày."),
 ("Subject: Unavailable item\nThe desk you selected is currently unavailable. We can offer the same design in white at the same price, or refund your payment. Please tell us your preference.", "What is the customer asked to do?", ["Choose between a substitute and a refund", "Pay an additional delivery charge", "Design a new desk", "Collect an item immediately"], "Người bán đưa hai phương án: màu trắng cùng giá hoặc hoàn tiền; cần khách chọn."),
 ("Hello everyone, The volunteer orientation has been postponed from June 2 to June 9 because the trainer is unavailable. Please keep the same start time, 10 a.m.", "Why was the orientation postponed?", ["The trainer is unavailable.", "Too few volunteers registered.", "The venue is under repair.", "The start time was incorrect."], "Because the trainer is unavailable là nguyên nhân rõ ràng; các lý do khác không có trong email.")]: notice("b04", *args)

# Part 1 uses original vector illustrations, clearly labeled in the application.
SCENES = [
 ("carrying", ["A worker is carrying a box.", "A worker is painting a wall.", "A worker is riding a bicycle.", "A worker is sleeping on a bench."], "Người trong hình đang cầm hộp bằng hai tay; không có hành động sơn, đạp xe hay ngủ."),
 ("typing", ["A woman is typing at a desk.", "A woman is sweeping the floor.", "A woman is opening an umbrella.", "A woman is serving a meal."], "Hai tay hướng vào bàn phím trước màn hình máy tính; đồ vật và tư thế phù hợp typing."),
 ("watering", ["A gardener is watering a plant.", "A gardener is cutting a tree.", "A gardener is stacking chairs.", "A gardener is repairing a fence."], "Bình tưới và dòng nước hướng vào chậu cây là bằng chứng cho watering."),
 ("bicycle", ["A bicycle is beside a wall.", "A bicycle is hanging from the ceiling.", "A person is riding a bicycle.", "Several bicycles are on a truck."], "Chỉ có một xe đạp đứng cạnh tường; không có người đạp xe hay xe tải."),
 ("shelves", ["Boxes are stacked on shelves.", "Boxes are floating in a pool.", "Workers are unloading a ship.", "The shelves are completely empty."], "Các hộp nằm trên các tầng kệ. Không thấy người đang xếp, nên mô tả trạng thái are stacked phù hợp."),
 ("table", ["Chairs are arranged around a table.", "Chairs are hanging on the wall.", "People are moving the table.", "The table is covered with food."], "Hình cho thấy bàn với các ghế xung quanh, không có người hay thức ăn."),
 ("ladder", ["A ladder is leaning against a wall.", "A ladder is lying under a table.", "A worker is climbing the ladder.", "Several ladders are on the roof."], "Thang nghiêng tựa tường; không có người leo. Against mô tả đúng vị trí."),
 ("walking", ["Two people are walking along a path.", "Two people are swimming in a pool.", "Two people are sitting on a bench.", "Two people are loading a truck."], "Hai người ở tư thế bước đi trên lối đi; không có ghế, hồ nước hoặc xe tải.")]
for scene, choices, explanation in SCENES:
    row = question("b01", 1, "Look at the illustration and listen. Which statement best describes it?", choices, explanation,
                   image=f"/toeic/images/{scene}.svg")
    row["audio_id"] = row["id"]
    row["transcript"] = "\n".join(f"{chr(65+i)}. {text}" for i, text in enumerate(row["options"]))
