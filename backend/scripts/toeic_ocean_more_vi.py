"""DHV explanations and editorial decisions for the remaining pinned MIT items."""
REVIEWS = {}
EXCLUDED = {}
GROUP_EDITS = {
    "P4-G18": {"replace_audio": ["returns on Monday", "returns later on Sunday"], "reason": "The announced Sunday 1–4 A.M. outage must not imply the app stays unavailable until Monday."},
    "P6-G16": {"replace_text": [["creates _____ summaries", "creates more _____ summaries"]], "reason": "Explicit more rules out the also-valid comparative conciser."},
    "P6-G17": {"replace_text": [["ready for wider use", "ready for _____ use"]], "reason": "Restore the missing fourth blank; its answer was printed in the source passage."},
    "P6-G18": {"replace_text": [["results in October", "results in _____"]], "reason": "Restore the missing fourth blank instead of exposing October."},
    "P7-R82": {"replace_text": [["left our warehouse on Tuesday", "were packed on Tuesday and are ready for dispatch"]], "reason": "Items cannot already have shipped if the company is holding the whole order to avoid a partial shipment."},
    "P7-R78": {"replace_text": [["Their chargers are connected to the regular building meter, not the trial meter.", "Their chargers are connected to the trial meter, so their electricity is included in the trial total."]], "reason": "An inflated energy-per-kilometer concern requires included energy but omitted distance, rather than consistently excluding both."},
    "P7-R79": {"replace_text": [["will be closed from August 12 through August 16", "will close at 6:00 P.M. each day from August 12 through August 16"]], "reason": "Make the evening-only closure consistent with the retained 5–6 P.M. desk reservation."},
}
EDITS = {
    "P1-007": {"answer_text": "A man is handling a box at the back of a van.", "reason": "Describe visible handling without inferring loading versus unloading."},
    "P1-023": {"answer_text": "A man is fastening a bicycle to a rack.", "reason": "Do not infer commuting from the image."},
    "P1-024": {"answer_text": "A woman is placing a book on a rolling cart.", "reason": "Do not infer employment from the image."},
    "P1-025": {"answer_text": "A man is coiling an electrical cable.", "reason": "Describe the action without asserting a profession."},
    "P5-133": {"prompt": "Yesterday, the announcement that the plant would reopen next month _____ many suppliers by surprise.", "reason": "Add an explicit past-time anchor to distinguish took from takes."},
    "P5-146": {"options": {3: "will considering"}, "reason": "Remove a defensible future-simple alternative to the intended future-perfect answer."},
    "P5-156": {"prompt": "Please contact the facilities department if you notice one or more _____ in the conference room equipment.", "reason": "Require a plural count noun; any malfunction was also grammatical."},
    "P5-170": {"prompt": "By the end of the pilot program next month, the engineering team _____ the battery-monitoring sensors on all delivery vehicles.", "reason": "Anchor the completion deadline explicitly in the future."},
    "P5-182": {"options": {3: "completes"}, "reason": "The original participial alternative also allowed an activity reading."},
    "P5-190": {"prompt": "By the time the audit begins next Monday, the finance department _____ the new expense-tracking system.", "reason": "Make the future deadline explicit."},
    "P5-181": {"options": {1: "been"}, "reason": "Avoid an indicative mandative alternative used in some varieties of English."},
    "P5-197": {"options": {1: "been"}, "reason": "Avoid an indicative mandative alternative used in some varieties of English."},
    "P5-214": {"options": {1: "explain"}, "reason": "Remove the defensible participial modifier of meeting."},
    "P5-220": {"prompt": "Participants who purchased two seats should scan both of their _____ at the kiosk.", "reason": "Both requires a plural noun; distributive their ticket was also valid in the original."},
    "P5-230": {"prompt": "By the time the regional director arrives next Monday, the finance team _____ the forecast.", "reason": "Distinguish a future completion from a habitual present reading."},
    "P5-246": {"options": {1: "Because of"}, "reason": "Longer instructions can also cause fewer errors; remove that competing causal clause."},
    "P5-248": {"prompt": "_____ on feedback from test users, the updated design replaced the swipe gesture with a button.", "reason": "The design, rather than the team, is based on feedback; remove a dangling modifier."},
    "P5-266": {"prompt": "These days, seldom _____ employees need to contact support after completing the guided installation.", "reason": "Anchor the generalization in the present, excluding the otherwise possible past did."},
    "P5-268": {"options": {3: "does"}, "reason": "Remove a defensible past-event reading with did."},
    "P5-276": {"options": {3: "does"}, "reason": "Remove a defensible past-event reading with did."},
    "P5-281": {"options": {0: "were"}, "reason": "Avoid competing passive-state ellipsis with is."},
    "P5-294": {"options": {0: "to review", 1: "been reviewed"}, "reason": "Avoid indicative mandative alternatives; focus on the bare verb."},
    "P5-295": {"options": {0: "been stored"}, "reason": "Avoid an indicative mandative alternative."},
    "P5-296": {"options": {0: "revising", 1: "to revise", 3: "to revising"}, "reason": "Avoid indicative mandative alternatives; focus on the bare verb."},
    "P5-298": {"options": {2: "been postponed"}, "reason": "Avoid an indicative mandative alternative."},
    "P5-299": {"options": {0: "to remain", 2: "to remaining"}, "reason": "Avoid indicative mandative alternatives."},
    "P5-301": {"options": {2: "been destroyed"}, "reason": "Avoid an indicative mandative alternative."},
    "P5-303": {"prompt": "_____ reviewed the revised budget, the committee approved the project without further discussion.", "options": {1: "Having"}, "reason": "Make the perfect-participle form explicit; reviewing was also defensible in the original."},
    "P5-307": {"options": {3: "To using"}, "reason": "Remove a defensible prior-use interpretation with having used."},
    "P5-311": {"prompt": "_____ completed all required safety checks, the engineers authorized the system restart.", "options": {2: "Having"}, "reason": "Explicitly test the auxiliary of the perfect participle rather than an ambiguous ordering inference."},
    "P5-314": {"options": {3: "easiness"}, "reason": "Easy and easier could both coordinate with accurate when a comparison was implicit."},
    "P5-328": {"options": {0: "been retained"}, "reason": "Avoid an indicative mandative alternative."},
    "P6-030": {"options": {2: "between", 3: "onto"}, "reason": "During/from Wednesday evening allowed different defensible removal schedules."},
    "P6-031": {"options": {1: "Although"}, "reason": "Despite the closure was also a defensible concession."},
    "P6-039": {"options": {2: "at"}, "reason": "Avoid an alternative completion-window reading with through."},
    "P6-048": {"options": {1: "activate"}, "reason": "Has been active was also grammatical; test passive completion unambiguously."},
    "P6-049": {"options": {2: "materializes"}, "reason": "Packaging material and packaging materials are both valid nouns."},
    "P6-055": {"options": {3: "to record"}, "reason": "Their professional development record permits a distributive singular reading."},
    "P6-063": {"options": {3: "to request"}, "reason": "A past request could also provide an exception to future deletion."},
    "P6-G32-Q3": {"options": {2: "Instead"}, "reason": "For example could also introduce a concrete way of building understanding."},
    "P7-R69-Q4": {"prompt": "Which information does the FAQ explicitly say the system does not collect?", "reason": "Distinguish explicit privacy exclusions from output estimates that were not described as input data."},
    "P7-R100-Q3": {"prompt": "What does the manager identify as a reason for the rise in Q4 request volume?", "options": {0: "The holiday product launch"}, "reason": "Avoid inferring greater agent volume: 10% of 1800 is less than 12% of 1650. The note explicitly attributes total request growth to the launch."},
}


def add(text):
    for line in text.strip().splitlines():
        qid, topic, explanation = line.split("|", 2)
        assert qid not in REVIEWS, qid
        REVIEWS[qid] = {"topic":topic, "explanation":explanation}


add("""
P1-001|p1-actions|Những người trong ảnh ngồi quanh bàn họp với giấy tờ và máy tính. Không có người viết bảng, xếp chồng ghế hay sửa máy tính.
P1-002|p1-scene|Các nhân viên ở giữa những kệ có nhiều thùng hàng. Không thấy xe tải hoặc thang; từ completely empty trái với hình.
P1-003|p1-scene|Hành khách và hành lý xuất hiện trong nhà ga sân bay. Không có cảnh lên xe buýt ngoài trời hoặc kiểm tra động cơ máy bay.
P1-004|p1-scene|Những người đội mũ bảo hộ đứng phía sau rào chắn công trường ven đường. Biển cửa hàng phía sau không có nghĩa họ đang mua sắm.
P1-005|p1-actions|Người phục vụ đang cầm khay có đồ ăn. Hành động quan sát được là carrying a tray, không phải quét phòng hay rửa bát.
P1-006|p1-actions|Người đàn ông đưa tay vào bảng điều khiển máy in. Operating mô tả thao tác này; máy không được di chuyển qua cửa.
P1-007|p1-actions|Người đàn ông đang cầm và xử lý một thùng ở cửa sau xe tải nhỏ. Mô tả không suy đoán chiều chuyển hàng vào hay ra khỏi xe.
P1-008|p1-scene|Có hành khách trên sân ga. Every platform is completely empty sai vì khẳng định tất cả đều vắng; không có cảnh sửa đường ray.
P1-019|p1-actions|Người phụ nữ đưa thẻ tới đầu đọc của cổng kiểm soát. Vị trí tay và thẻ xác nhận tapping an access card.
P1-020|p1-actions|Người đàn ông dùng dụng cụ dán băng keo để đóng thùng. Đây là sealing a package, không phải quét mã hay lấy vật liệu ra.
P1-021|p1-actions|Người đàn ông thao tác thiết bị điều chỉnh nhiệt độ trên tường. Không có sơn, khung tranh hoặc dây đang tháo khỏi trần.
P1-022|p1-scene|Ghế được xếp thành các hàng hướng về màn chiếu. Không có người xem thuyết trình; ghế không được xếp chồng.
P1-023|p1-actions|Người đàn ông đang cố định xe đạp vào giá bằng khóa. Hình không chứng minh mục đích đi lại hoặc nghề nghiệp của người đó.
P1-024|p1-actions|Người phụ nữ đặt sách lên xe đẩy có bánh. Mô tả hành động nhìn thấy; không cần suy ra người đó là nhân viên thư viện.
P1-025|p1-actions|Người đàn ông đang cuộn dây điện thành các vòng. Dây không được cắm vào ổ; không có người mang loa lên sân khấu.
P2-069|p2-wh|When hỏi thời điểm giao cảm biến; by Friday trả lời hạn giao. Vị trí phòng họp và thói quen đi tàu không liên quan.
P2-070|p2-yesno|Câu hỏi xác nhận còn cần sửa báo cáo không. Đã gửi bản sửa giải thích vì sao không cần thực hiện yêu cầu nữa.
P2-071|p2-wh|Why hỏi nguyên nhân trì hoãn. Kiểm thử mã hóa kéo dài hơn dự kiến là lý do; vị trí máy quét không trả lời câu hỏi.
P2-072|p2-wh|Who hỏi người phụ trách hội thảo. Câu đáp giới thiệu Mia, người quản lý lịch đào tạo, là đầu mối phù hợp.
P2-073|p2-yesno|Câu hỏi hỏi có ai khởi động lại máy tính bảng chưa. I reset the tablet this morning xác nhận hành động và thời điểm.
P2-074|p2-wh|When hỏi lúc bắt đầu diễn tập. Not until the consultant arrives nghĩa là phải chờ chuyên gia đến rồi mới bắt đầu.
P2-075|p2-yesno|Câu hỏi dùng all drafts; câu đáp giới hạn nghĩa vụ vào only the final version. Phải nghe phạm vi thay vì chỉ tìm yes/no.
P2-076|p2-request|Could you send là lời nhờ gửi mẫu hóa đơn. Sure, I can send it now nhận lời và nêu hành động cụ thể.
P2-077|p2-request|Người nói nhờ chuyển tiếp chương trình họp. Certainly cùng lời hứa gửi chiều nay đáp ứng đúng yêu cầu.
P2-078|p2-wh|When hỏi khi nào mở lại phòng. After the safety inspection is complete nêu điều kiện thời gian phù hợp.
P2-079|p2-wh|Where hỏi nơi lưu hợp đồng đã ký. In the secure archive room là địa điểm; lý do sửa hợp đồng không phù hợp.
P2-080|p2-wh|Who has hỏi ai giữ số liệu. I think Mr. Alvarez has the latest figures nêu người có thể cung cấp chúng.
P2-081|p2-yesno|Yes xác nhận được tham dự nhưng only for registered attendees giới hạn ở người đã đăng ký; không hiểu là ai cũng được vào.
P2-082|p2-request|Should we book là đề xuất đặt phòng lớn hơn. Good idea thể hiện đồng ý và lời hứa đặt phòng tiếp nối đề xuất.
P2-083|p2-wh|Why hỏi nguyên nhân hệ thống ngoại tuyến. Because several sensors are being replaced giải thích đúng tình trạng đó.
P2-084|p2-yesno|Have the results arrived hỏi kết quả đã tới chưa. Not yet phủ định ở hiện tại, còn before noon là dự kiến nhận.
P2-085|p2-choice|Do you prefer A or B yêu cầu chọn loại tài liệu. Nhận xét bản điện tử dễ cập nhật thể hiện ưu tiên bản đó.
P2-086|p2-yesno|Câu hỏi phủ định xác nhận hạn ngày mai. No và extended to Friday sửa lại giả định về hạn nộp.
P2-087|p2-wh|Who hỏi người phê duyệt. Câu về Ms. Delgado nhắc người đã nhận việc; said she would chưa khẳng định việc đã hoàn tất.
P2-088|p2-wh|Đường cao tốc đóng để sửa chữa là lý do hợp lý khiến người chuyển phát chưa tới. Không cần câu đáp bắt đầu bằng because.
P2-089|p2-wh|Where hỏi vị trí cất bộ lọc. On the shelf beside the maintenance office chỉ rõ nơi cất.
P2-090|p2-request|Could you send là lời nhờ. I'll attach it to an email now nhận lời gửi sơ đồ dưới dạng tệp đính kèm.
P2-091|p2-yesno|Isn't ... still valid xác nhận bảo hành còn hiệu lực. No, it expired last month trực tiếp sửa giả định này.
P2-092|p2-wh|How often hỏi tần suất. Every six months là chu kỳ sáu tháng; người thực hiện và tủ thiết bị không trả lời tần suất.
P2-093|p2-wh|Which loading dock hỏi bến nào. The one behind Warehouse B xác định đúng địa điểm được chọn.
P2-094|p2-wh|When hỏi thời gian gặp kiểm toán viên. Right after lunch trả lời lúc gặp; văn phòng là câu trả lời cho where.
P2-095|p2-indirect|Thông báo cửa phía đông đóng dẫn tới quyết định dùng cửa từ nhà để xe. Then liên kết hành động với tình huống vừa nghe.
P2-096|p2-request|Would you mind checking là lời nhờ lịch sự. Sure cùng câu hỏi bắt đầu từ quý nào thể hiện nhận việc và làm rõ phạm vi.
P2-097|p2-request|Should we postpone hỏi quyết định có hoãn không. Chờ khách phản hồi trước là cách đáp gián tiếp hợp tình huống.
P2-098|p2-wh|How long hỏi phòng được giữ đến khi nào. Until four thirty cung cấp mốc kết thúc; không phải người sử dụng hoặc tầng.
P2-099|p2-wh|What time hỏi giờ xe chạy. A quarter past six là 6 giờ 15; không nhầm với sức chứa hoặc điểm đón.
P2-100|p2-wh|Who hỏi người hướng dẫn thực tập sinh. Daniel from human resources is dùng is thay cho phần is giving the orientation.
P2-101|p2-request|Why don't we là lời đề xuất chuyển học trực tuyến. That would solve the room shortage đồng ý bằng cách nêu lợi ích.
P2-102|p2-indirect|Hóa đơn vẫn chờ chữ ký giám đốc nên chưa được gửi. Câu đáp gián tiếp giải thích trạng thái mà không cần nói no.
P2-103|p2-wh|Where hỏi vị trí biểu mẫu. In the top drawer of the filing cabinet chỉ ngăn trên cùng của tủ hồ sơ.
P2-104|p2-request|Can I borrow là lời xin mượn. As soon as I finish đặt điều kiện có thể mượn sau khi kiểm kê xong.
P2-105|p2-indirect|Việc chuyển dữ liệu lâu thêm hai giờ có thể ảnh hưởng ca tối. Đề nghị báo nhân viên ca tối đáp ứng thông tin mới.
P2-106|p2-wh|How many hỏi số người xác nhận. Six have confirmed so far cung cấp số lượng sáu người tính đến hiện tại.
P2-107|p2-yesno|Câu hỏi xác nhận nhà cung cấp chịu phí gấp. Only if we ordered before noon bổ sung điều kiện của cam kết đó.
P2-108|p2-wh|Who's taking minutes hỏi ai ghi biên bản. I can nhận việc; unless Martin has already volunteered nêu ngoại lệ.
P2-109|p2-indirect|Máy chủ dự phòng chưa đồng bộ nên hoãn chuyển hệ thống là phản ứng phù hợp. Then đánh dấu quyết định dựa trên tình trạng vừa nêu.
P5-125|p5-advanced|Had + chủ ngữ + V3 là đảo ngữ điều kiện trái quá khứ. Kết quả bị động tương ứng dùng would have been processed.
P5-126|p5-relative|Many of which thay cho nhiều chính sách trong several policies. Sau giới từ of không dùng that trong cấu trúc quan hệ này.
P5-127|p5-advanced|Đưa so detailed lên đầu để nhấn mạnh làm đảo be lên trước chủ ngữ: So detailed is the manual that…
P5-128|p5-passive|Nhóm tiếp thị được phản hồi tích cực khích lệ. Encouraged là phân từ bị động; encouraging sẽ đổi vai trò thành chủ thể gây khích lệ.
P5-129|p5-conjunction|Determine whether + mệnh đề diễn đạt xác định liệu văn phòng còn mở hay không. Các lựa chọn khác không diễn đạt câu hỏi gián tiếp này.
P5-130|p5-word-form|Chỗ trống bổ nghĩa cho operate nên cần trạng từ erratically, nghĩa là hoạt động thất thường.
P5-131|p5-conjunction|Even though nối hai mệnh đề có ý nhượng bộ: dù ước tính thấp, chi phí cuối vẫn trong ngân sách. Because of cần cụm danh từ.
P5-132|p5-preposition|Cụm cố định be consistent with nghĩa là phù hợp, nhất quán với tiêu chuẩn được nêu.
P5-133|p5-tense|Yesterday xác định sự kiện đã xảy ra; took là động từ chính của chủ ngữ the announcement. That… chỉ bổ sung nội dung thông báo.
P5-134|p5-comparison|Cấu trúc so sánh tương quan là the more… the better…: khách dùng thường xuyên hơn thì cá nhân hóa tốt hơn.
P5-135|p5-infinitive|Nhân viên tự đọc hướng dẫn trước khi làm đánh giá. Having reviewed diễn đạt hành động chủ động đã hoàn thành trước đó.
P5-136|p5-conjunction|Be confident that + mệnh đề có chủ ngữ và động từ diễn đạt tin chắc vào kết quả. Các giới từ không nối trực tiếp mệnh đề này.
P5-137|p5-conjunction|Phòng nhỏ hơn dự kiến nhưng vẫn đủ chỗ là quan hệ nhượng bộ. Nevertheless phù hợp; therefore sẽ biến thành quan hệ kết quả.
P5-138|p5-passive|Yêu cầu bảo hành cần được kèm bản sao hóa đơn: modal + be + V3, tức must be accompanied by.
P5-139|p5-advanced|Rarely đứng đầu yêu cầu đảo trợ động từ: do we receive. Động từ chính receive trở về dạng nguyên mẫu.
P5-140|p5-infinitive|Recommend + V-ing diễn đạt đề nghị thực hiện hành động; reviewing làm bổ ngữ của recommended.
P5-141|p5-agreement|What the auditors requested là một mệnh đề danh từ chỉ yêu cầu. Bổ ngữ a complete record phù hợp với was số ít.
P5-142|p5-word-form|Minimize cần tân ngữ; disruption là danh từ chỉ sự gián đoạn. Disruptive là tính từ và disrupt là động từ.
P5-143|p5-conjunction|In spite of đi với cụm danh từ the restrictions, diễn đạt hoàn thành công việc bất chấp các hạn chế.
P5-144|p5-relative|Sau district, mệnh đề đã có chủ ngữ firms và tân ngữ offices; where bổ sung nơi các công ty mở văn phòng.
P5-145|p5-comparison|Than báo hiệu so sánh hơn; far nhấn mạnh mức độ. Dùng far easier, không dùng trạng từ easily.
P5-146|p5-tense|By the time đặt mốc tương lai và xét việc hoàn tất trước mốc đó. Will have considered là tương lai hoàn thành.
P5-147|p5-advanced|Ask that khi đưa yêu cầu dùng động từ nguyên mẫu trong mệnh đề giả định: all suppliers submit.
P5-148|p5-conjunction|Postpone… until nghĩa là hoãn đến khi máy quét thay thế tới. Until nối với mệnh đề thời gian có đủ chủ ngữ và động từ.
P5-149|p5-word-form|Handling là hành động được mô tả; so efficiently dùng trạng từ để nói cách xử lý yêu cầu.
P5-150|p5-passive|Hợp đồng nhận hành động ký nên dùng it is signed. Signed là quá khứ phân từ sau be.
P5-151|p5-word-form|Register cần trạng từ bổ nghĩa cách thực hiện. Promptly nghĩa là nhanh chóng, phù hợp khi số chỗ có hạn.
P5-152|p5-word-form|Information là danh từ; comprehensive là tính từ đứng trước để mô tả thông tin đầy đủ, toàn diện.
P5-153|p5-word-form|Correctly là trạng từ bổ nghĩa had been installed, cho biết máy được lắp đúng cách.
P5-154|p5-conjunction|Once diễn đạt điều kiện thời gian: báo cáo được phát hành sau khi hội đồng phê duyệt. Các từ còn lại đổi quan hệ giữa hai việc.
P5-155|p5-word-form|Price cần tính từ competitive đứng trước; competitive price nghĩa là giá cạnh tranh.
P5-156|p5-quantity|One or more yêu cầu danh từ đếm được số nhiều. Malfunctions chỉ những sự cố của thiết bị.
P5-157|p5-word-form|A more detailed explanation dùng tính từ detailed để bổ nghĩa explanation; detail là danh từ hoặc động từ.
P5-158|p5-infinitive|After reviewing diễn đạt khách đặt câu hỏi sau khi đọc hợp đồng. Khách là chủ thể thực hiện cả hai hành động.
P5-159|p5-preposition|By noon là hạn chót không muộn hơn trưa. Các lựa chọn along, between, except không chỉ hạn nộp trong câu này.
P5-160|p5-conjunction|Hàng đến trễ dẫn đến đổi lịch lắp đặt. Therefore nối nguyên nhân với hệ quả sau dấu chấm phẩy.
P5-161|p5-vocabulary|Sau will cần động từ nguyên mẫu; notify someone of something là thông báo cho ai về việc gì.
P5-162|p5-word-form|Estimate là danh từ; accurate là tính từ mô tả một ước tính chính xác hơn.
P5-163|p5-word-form|Electronically bổ nghĩa cho submitted, chỉ cách nộp qua cổng trực tuyến. Electronic là tính từ.
P5-164|p5-tense|Next Monday là mốc tương lai. Will have finalized nhấn mạnh báo cáo sẽ hoàn tất trước khi kiểm toán viên tới.
P5-165|p5-preposition|Apply to chỉ phạm vi áp dụng: các hướng dẫn áp dụng cho toàn bộ nhân viên làm trong kho.
P5-166|p5-conjunction|Unless + mệnh đề nêu ngoại lệ: không thể xong trước thứ sáu trừ khi linh kiện tới hôm nay. Các giới từ không đi trực tiếp với mệnh đề này.
P5-167|p5-relative|Recommendations thuộc về consultant, nên dùng whose + danh từ. Who không thể đứng trực tiếp trước recommendations theo nghĩa sở hữu.
P5-168|p5-infinitive|Ask someone to + động từ nguyên mẫu: asked staff members to report any delays.
P5-169|p5-word-form|Review là danh từ nên cần tính từ thorough. More thorough diễn đạt việc rà soát kỹ hơn.
P5-170|p5-tense|Next month đặt hạn hoàn tất trong tương lai. Will have installed diễn đạt sẽ lắp xong cảm biến trước khi chương trình kết thúc.
P5-171|p5-infinitive|Sau will dùng nguyên mẫu review. Reviewing, reviewed và reviewer không phù hợp vị trí động từ sau modal.
P5-172|p5-preposition|Have/give control over something diễn đạt quyền kiểm soát đối với việc đó; how… nêu cách thông tin được chia sẻ.
P5-173|p5-word-form|Hourly có thể là trạng từ, nghĩa là mỗi giờ. Ở đây nó bổ nghĩa cho backs up để chỉ chu kỳ sao lưu.
P5-174|p5-conjunction|Concerns about server capacity là cụm danh từ. Despite đi với cụm này; although cần một mệnh đề đầy đủ.
P5-175|p5-relative|Technician chỉ người và mệnh đề thiếu chủ ngữ trước configured, nên dùng who.
P5-176|p5-vocabulary|A small-scale trial là một cuộc thử nghiệm quy mô nhỏ. Trail là đường mòn, không phù hợp nghĩa phát triển sản phẩm.
P5-177|p5-conjunction|Whether… or… diễn đạt hai lựa chọn đang cân nhắc trong câu hỏi gián tiếp sau decided.
P5-178|p5-conjunction|Nguyên mẫu giảm điện năng dẫn đến quyết định thử lớn hơn. Therefore nối kết quả; however diễn đạt tương phản.
P5-179|p5-word-form|Privacy policy là cụm danh từ cần tính từ transparent bổ nghĩa. Most transparent diễn đạt mức minh bạch cao nhất.
P5-180|p5-conjunction|As soon as nối thời điểm thông báo với lúc linh kiện có sẵn: ngay khi có linh kiện thì báo kỹ thuật viên.
P5-181|p5-advanced|Với lời đề nghị trong cấu trúc giả định recommended that, dùng động từ nguyên mẫu be; dashboard nhận hành động nên be updated.
P5-182|p5-infinitive|To complete nêu mục đích ở lại phòng thí nghiệm sau giờ làm. Các lựa chọn còn lại không tạo cụm chỉ mục đích phù hợp.
P5-183|p5-relative|Which thay the report và làm chủ ngữ cho includes trong mệnh đề quan hệ bổ sung giữa hai dấu phẩy.
P5-184|p5-word-form|Hastily là trạng từ mô tả cách lắp ráp vội vàng, giải thích vì sao nhóm chất lượng yêu cầu kiểm tra lại.
P5-185|p5-word-form|Sau chủ ngữ they cần động từ disrupt. Các lựa chọn danh từ, tính từ, trạng từ không tạo được mệnh đề đầy đủ.
P5-186|p5-preposition|Accessible to someone là cách diễn đạt quyền tiếp cận dành cho ai. Câu giới hạn ở nhân viên đã hoàn thành hướng dẫn bảo mật.
P5-187|p5-word-form|Operate là động từ cần trạng từ safely để chỉ vận hành an toàn trong vùng thiếu sáng.
P5-188|p5-word-form|Significantly là trạng từ bổ nghĩa decreased, chỉ thời gian chờ giảm đáng kể.
P5-189|p5-word-form|Method cần tính từ reliable; a more reliable method là phương pháp đáng tin cậy hơn.
P5-190|p5-tense|By the time… next Monday nêu hạn tương lai. Will have implemented diễn đạt triển khai xong hệ thống trước mốc đó.
""")

add("""
P5-191|p5-preposition|Be responsible for + V-ing diễn đạt trách nhiệm thực hiện việc gì. Reporting đứng sau giới từ for.
P5-192|p5-conjunction|Unless nêu ngoại lệ của việc tự gia hạn: chỉ không gia hạn nếu nhóm mua hàng hủy đúng hạn.
P5-193|p5-word-form|Substantially là trạng từ bổ nghĩa reduced, cho biết mức giảm nhiên liệu đáng kể.
P5-194|p5-infinitive|After reviewing diễn đạt nhóm sản phẩm hoãn phát hành sau khi xem phản hồi thử nghiệm; chủ thể hai hành động là một.
P5-195|p5-word-form|A detailed cần danh từ số ít phía sau. Assessment là sự đánh giá các rủi ro.
P5-196|p5-relative|Technician chỉ người và mệnh đề thiếu chủ ngữ trước repaired; dùng who.
P5-197|p5-advanced|Requires that diễn đạt yêu cầu; dùng nguyên mẫu be trong mệnh đề giả định. Reports nhận hành động nên be reviewed.
P5-198|p5-conjunction|Thiếu chế độ ngoại tuyến giải thích việc nhân viên thích ứng dụng cũ hơn. Therefore biểu thị hệ quả đó.
P5-199|p5-conjunction|Decide whether + mệnh đề diễn đạt quyết định liệu có cung cấp chatbot ngoài giờ hay không.
P5-200|p5-infinitive|Sau will cần nguyên mẫu calibrate, nghĩa là hiệu chuẩn cảm biến. Calibration là danh từ.
P5-201|p5-word-form|Explanation cần tính từ specific; more specific là cụ thể hơn. Specifically không trực tiếp bổ nghĩa danh từ này.
P5-202|p5-preposition|Coverage for something là phạm vi bảo hành đối với vấn đề đó. For nối coverage với software defects.
P5-203|p5-word-form|Automatically bổ nghĩa updates, mô tả cập nhật tự động mỗi khi có dữ liệu mới.
P5-204|p5-conjunction|Not… until diễn đạt chỉ kích hoạt sau khi điều kiện hoàn thành. Until đi với mệnh đề có chủ ngữ all employees.
P5-205|p5-quantity|Several yêu cầu danh từ đếm được số nhiều. Adjustments là các điều chỉnh thiết kế pin.
P5-206|p5-tense|Since… went live nối thời điểm quá khứ với hiện tại. Has processed là hiện tại hoàn thành, phù hợp số yêu cầu đã xử lý đến nay.
P5-207|p5-infinitive|Can + động từ nguyên mẫu: identify. Các từ identification, identifiable, identifiably thuộc từ loại khác.
P5-208|p5-relative|Uses thiếu tân ngữ chỉ office; that làm tân ngữ trong mệnh đề quan hệ. Where chỉ nơi chốn, không thay tân ngữ của uses.
P5-209|p5-conjunction|In case nêu tình huống dự phòng: lưu bản cục bộ phòng khi Wi-Fi không ổn định.
P5-210|p5-passive|Data là thứ được thu thập nên dùng phân từ collected. Cụm này rút gọn nghĩa data that are collected.
P5-211|p5-word-form|Answers là hành động; more accurately diễn đạt trả lời chính xác hơn bằng trạng từ.
P5-212|p5-conjunction|When nối việc hiển thị các mục lưu trữ với lúc người dùng chọn bộ lọc lịch sử.
P5-213|p5-word-form|Additional cần danh từ phía sau và purchased cần tân ngữ. Equipment là danh từ không đếm được chỉ thiết bị.
P5-214|p5-infinitive|To explain nêu mục đích của việc lên lịch họp: giải thích các quy tắc mới.
P5-215|p5-word-form|Automatically là trạng từ bổ nghĩa updates. Automatic là tính từ, automation là danh từ.
P5-216|p5-preposition|Before closing đặt việc lưu trữ trước khi hoàn tất báo cáo. Sau giới từ before có thể dùng V-ing.
P5-217|p5-infinitive|Require someone to do something: requires all vendors to sign. Động từ sau to ở dạng nguyên mẫu.
P5-218|p5-conjunction|After nêu đúng thứ tự: đặt lại mật khẩu trước, hiển thị xác nhận sau. Các giới từ còn lại không nối mệnh đề này.
P5-219|p5-word-form|Sau was cần tính từ mô tả ảnh. Too dark giải thích vì sao người trình bày cần máy chiếu dự phòng.
P5-220|p5-quantity|Both of their yêu cầu danh từ số nhiều chỉ hai vé. Tickets đáp ứng cấu trúc; ticket số ít không phù hợp.
P5-221|p5-word-form|Accurately bổ nghĩa cho recorded, diễn đạt ghi nhận chính xác các số đo qua đêm.
P5-222|p5-conjunction|Before + mệnh đề chỉ việc xem xét phải diễn ra trước khi hợp đồng được tải lên cổng khách hàng.
P5-223|p5-word-form|More efficiently dùng trạng từ để mô tả tạo báo cáo hiệu quả hơn. Efficiency là danh từ.
P5-224|p5-word-form|Make + tân ngữ + tính từ: make the webinar accessible. Accessible mô tả khả năng tiếp cận của hội thảo.
P5-225|p5-word-form|Carefully bổ nghĩa cho was reviewed, cho biết báo cáo được kiểm tra cẩn thận.
P5-226|p5-conjunction|Linh kiện chưa tới là nguyên nhân hoãn kiểm tra. Because nối mệnh đề nguyên nhân đầy đủ.
P5-227|p5-vocabulary|Photo identification là giấy tờ nhận dạng có ảnh. Sau photo ở cụm này cần danh từ identification.
P5-228|p5-infinitive|Recommend + V-ing dùng để đề nghị hành động. Testing là kiểm thử cổng khách hàng trước nâng cấp.
P5-229|p5-preposition|Apply to diễn đạt áp dụng cho những nhóm người được liệt kê.
P5-230|p5-tense|Next Monday đặt mốc tương lai. Will have revised nghĩa là sẽ sửa xong dự báo trước khi giám đốc tới.
P5-231|p5-word-form|Detailed là tính từ bổ nghĩa information, diễn đạt thông tin chi tiết về bảo hành.
P5-232|p5-conjunction|Despite đi với danh từ the shipping delay; still nhấn mạnh vẫn dự kiến đáp ứng hạn dù có chậm giao.
P5-233|p5-pronouns|Download cần đại từ tân ngữ them để thay training materials. They là chủ ngữ, their cần danh từ phía sau.
P5-234|p5-comparison|Than báo hiệu so sánh hơn; much nhấn mạnh faster. Fastest là so sánh nhất nên không phù hợp.
P5-235|p5-relative|Who thay engineer và làm chủ ngữ cho designed. Whom là dạng tân ngữ.
P5-236|p5-word-form|Quarterly dùng như trạng từ nghĩa là mỗi quý một lần, mô tả tần suất khảo sát.
P5-237|p5-quantity|Several + danh từ đếm được số nhiều. Representatives chỉ nhiều đại diện từ phòng tiếp thị.
P5-238|p5-passive|Illustrated instructions là hướng dẫn có hình minh họa: instructions nhận sự minh họa nên dùng phân từ quá khứ.
P5-239|p5-infinitive|Be encouraged to + động từ nguyên mẫu diễn đạt được khuyến khích thực hiện: to ask questions.
P5-240|p5-vocabulary|Ahead of schedule là cụm chỉ sớm hơn lịch dự kiến. Các cụm còn lại không mang nghĩa này.
P5-241|p5-conjunction|When mở đầu câu hỏi gián tiếp về thời điểm chính sách có hiệu lực sau explained.
P5-242|p5-vocabulary|Provide service là cung cấp dịch vụ. Produce, prevent và predict không diễn đạt việc khách sạn cung cấp xe đưa đón.
P5-243|p5-pronouns|Expense receipts là danh từ cần từ chỉ sở hữu your đứng trước. Yours không đứng trực tiếp trước danh từ.
P5-244|p5-advanced|Should you need… là đảo ngữ điều kiện tương đương If you should need…; should đi với need nguyên mẫu.
P5-245|p5-word-form|Gradually bổ nghĩa collect, chỉ thu phản hồi từng bước trước khi đầu tư phát hành toàn diện.
P5-246|p5-conjunction|Although diễn đạt nhượng bộ: hướng dẫn dài hơn nhưng người dùng mắc ít lỗi hơn. Because of không đi trực tiếp với mệnh đề đầy đủ.
P5-247|p5-word-form|A clearer cần danh từ số ít explanation, nghĩa là lời giải thích rõ hơn về cách lưu dữ liệu.
P5-248|p5-passive|The updated design được xây dựng dựa trên phản hồi nên dùng Based on. Chủ thể của cụm phân từ phải khớp chủ ngữ design.
P5-249|p5-conjunction|Unless nêu điều kiện ngoại lệ: không xử lý yêu cầu nếu khách chưa cung cấp số sê-ri.
P5-250|p5-word-form|Make + tân ngữ + tính từ. Meaningful mô tả kết quả có ý nghĩa hơn khi tách dữ liệu trong nhà và ngoài trời.
P5-251|p5-pronouns|Library là danh từ số ít; its bổ nghĩa hours để chỉ giờ mở cửa của thư viện.
P5-252|p5-relative|Employees chỉ người và trước completed cần chủ ngữ của mệnh đề quan hệ, nên dùng who.
P5-253|p5-conjunction|So that nêu mục đích nộp danh sách: để bộ phận tuân thủ có thể cập nhật hồ sơ.
P5-254|p5-comparison|Than và slightly phù hợp với so sánh hơn farther, chỉ khoảng cách xa hơn một chút.
P5-255|p5-infinitive|Allow someone to do something: allows residents to report. Reporting không theo sau tân ngữ trong cấu trúc này.
P5-256|p5-preposition|Returned for correction nghĩa là trả lại để sửa. For nêu mục đích trả lại các yêu cầu thiếu mã dự án.
P5-257|p5-word-form|Periodically là trạng từ bổ nghĩa reviews, diễn đạt việc rà soát theo định kỳ.
P5-258|p5-conjunction|Asked whether + mệnh đề dùng cho câu hỏi gián tiếp có/không, ở đây hỏi có cần đặt trước buổi học không.
P5-259|p5-passive|Button được gắn nhãn nên dùng labeled; clearly bổ nghĩa cho phân từ này: một nút được ghi nhãn rõ ràng.
P5-260|p5-relative|Employees tự làm việc từ xa nên dùng cụm phân từ chủ động working remotely, rút gọn employees who are working remotely.
""")

add("""
P5-261|p5-advanced|Visible là tính từ nên cần be. Đảo ngữ sau Not until dùng was the discrepancy visible; không thêm it vì đã có chủ ngữ discrepancy.
P5-262|p5-advanced|Not until đưa lên đầu làm đảo trợ động từ. Sự kiện compared ở quá khứ nên dùng did they discover, với discover nguyên mẫu.
P5-263|p5-advanced|Only after đứng đầu yêu cầu đảo ngữ ở mệnh đề chính: did the machine resume. Resume là động từ nguyên mẫu sau did.
P5-264|p5-advanced|Cấu trúc gốc là the team was able to restore. Sau Only when, đảo was lên trước the team; không dùng did với able.
P5-265|p5-advanced|Received là phân từ trong thì hiện tại hoàn thành. Never before đứng đầu làm đảo has lên trước the committee.
P5-266|p5-advanced|These days xác định nhận xét hiện tại. Sau seldom dùng do employees need; need giữ nguyên mẫu sau do.
P5-267|p5-advanced|Quiet là tính từ bổ ngữ nên dùng is. Rarely đứng đầu tạo is the loading area this quiet.
P5-268|p5-advanced|Under no circumstances là cụm phủ định đứng đầu; đảo modal may lên trước visitors. Sau modal dùng enter nguyên mẫu.
P5-269|p5-advanced|Little mang nghĩa hầu như không biết; đảo did lên trước chủ ngữ và dùng know nguyên mẫu cho sự kiện quá khứ.
P5-270|p5-advanced|No sooner had + chủ ngữ + V3 + than diễn đạt vừa xong việc này thì việc khác xảy ra. Been signed là bị động hoàn thành.
P5-271|p5-advanced|Hardly had + chủ ngữ + V3 + when… là cấu trúc diễn đạt vừa bắt đầu thì có sự cố. Begun là phân từ của begin.
P5-272|p5-advanced|Not only đứng đầu làm đảo trợ động từ. Reduced ở vế sau xác định quá khứ, nên dùng did the update improve.
P5-273|p5-advanced|Accessible là tính từ; customer records số nhiều cần were. At no time đứng đầu tạo đảo ngữ were customer records accessible.
P5-274|p5-advanced|Only then đứng đầu yêu cầu đảo trợ động từ did. Understand dùng nguyên mẫu, phù hợp câu chuyện quá khứ.
P5-275|p5-advanced|On no account nêu điều cấm. Should đảo lên trước files và đi với be sent nguyên mẫu bị động.
P5-276|p5-advanced|Nowhere else đứng đầu yêu cầu đảo ngữ: can customers obtain. Can đi với obtain nguyên mẫu.
P5-277|p5-advanced|So + tính từ đặt đầu câu nhấn mạnh dẫn đến was the revised schedule. Mốc were completed ở sau xác nhận quá khứ.
P5-278|p5-advanced|Such was the demand that… diễn đạt nhu cầu lớn đến mức phải thêm buổi. Be đứng trước chủ ngữ trong cấu trúc nhấn mạnh.
P5-279|p5-advanced|Neither đứng đầu cần đảo did trước supplier. Nor did ở vế sau cho thấy hai hành động phủ định cùng ở quá khứ.
P5-280|p5-advanced|Neither did the revised quotation thay cho did not include installation. Dùng did tương ứng với động từ quá khứ ở vế trước.
P5-281|p5-advanced|Nor has the revised budget lược bỏ been approved đã có ở vế trước. Has giữ thì hiện tại hoàn thành của câu gốc.
P5-282|p5-advanced|Should you require tương đương If you should require, dùng trong điều kiện trang trọng. Require giữ dạng nguyên mẫu.
P5-283|p5-advanced|Were + chủ ngữ + to V là đảo ngữ điều kiện giả định: Were the supplier to miss… tương ứng If… were to miss…
P5-284|p5-advanced|Had + chủ ngữ + V3 thay If + chủ ngữ + had + V3 trong điều kiện trái quá khứ. Known là phân từ đi với had.
P5-285|p5-relative|Employees tự làm việc ở công trường nên dùng working, rút gọn who work/are working. Must complete là động từ chính.
P5-286|p5-passive|Ứng dụng được ra mắt vào tháng ba; launched rút gọn which was launched. Now supports là động từ chính.
P5-287|p5-passive|Once approved rút gọn Once it is approved. Agreement là đối tượng được bộ phận pháp lý phê duyệt.
P5-288|p5-passive|Located within walking distance mô tả vị trí khách sạn, từ cấu trúc be located. Locating sẽ chuyển sang nghĩa chủ động xác định vị trí.
P5-289|p5-relative|Customers được mời tham gia nên dùng invited, rút gọn who are invited. Will receive là động từ chính của câu.
P5-290|p5-infinitive|Kỹ thuật viên tự lắp pin nên While installing rút gọn While the technician was installing, với cùng chủ thể.
P5-291|p5-passive|Unless stated otherwise là cụm bị động rút gọn thường gặp trong văn bản: trừ khi có quy định khác bằng văn bản.
P5-292|p5-relative|Files là đối tượng được lưu nên dùng stored, rút gọn that are stored. Can be accessed là vị ngữ chính.
P5-293|p5-passive|Dashboard được xem trên máy tính bảng nên When viewed rút gọn When it is viewed. Không dùng viewing với chủ thể dashboard.
P5-294|p5-advanced|Recommended that đưa đề nghị; động từ giả định dùng review nguyên mẫu dù chủ ngữ each branch số ít.
P5-295|p5-advanced|It is essential that diễn đạt điều thiết yếu. Backup copies nhận hành động lưu, nên dùng nguyên mẫu bị động be stored.
P5-296|p5-advanced|Requested that diễn đạt yêu cầu. Dùng revise nguyên mẫu trong mệnh đề giả định, không thêm to hoặc đuôi -s.
P5-297|p5-advanced|It is vital that diễn đạt yêu cầu quan trọng; access request nhận hành động nên be approved.
P5-298|p5-advanced|Suggested that đưa đề xuất hoãn ngày ra mắt. Dùng be postponed, nguyên mẫu bị động trong mệnh đề giả định.
P5-299|p5-advanced|Requires that diễn đạt quy định. Động từ giả định remain giữ nguyên mẫu ngay cả sau no visitor số ít.
P5-300|p5-advanced|Would demonstrate ở mệnh đề chính đi với giả định không thực ở hiện tại. Were là dạng be trang trọng trong mệnh đề if.
P5-301|p5-advanced|Asked that đưa yêu cầu hủy bản nháp. Draft nhận hành động, nên dùng be destroyed.
P5-302|p5-advanced|It was proposed that đưa đề xuất cải tạo văn phòng. Office nhận hành động chuyển đổi, nên dùng be converted.
P5-303|p5-infinitive|Having + V3 tạo cụm phân từ hoàn thành. Having reviewed cho biết ủy ban đã xem ngân sách trước khi phê duyệt.
P5-304|p5-infinitive|Người chuyển phát là chủ thể biết hoặc không biết mã. Not knowing là cụm phân từ chủ động phủ định, nêu lý do gọi lễ tân.
P5-305|p5-passive|Hệ thống được thiết kế cho khối lượng giao dịch lớn, nên dùng Designed. Having designed sẽ yêu cầu hệ thống tự thiết kế thứ khác.
P5-306|p5-passive|Compared with là cụm phân từ bị động để so sánh máy mới với mẫu trước. Chủ ngữ scanner là đối tượng được so sánh.
P5-307|p5-infinitive|Using the encrypted portal nêu phương tiện nhân viên sử dụng để gửi tài liệu. Chủ thể của using là employees.
P5-308|p5-passive|Having been notified kết hợp nghĩa bị động và hoàn thành: tài xế được báo trước rồi mới tránh cây cầu đóng.
P5-309|p5-passive|Be faced with là cụm cố định chỉ đối mặt với vấn đề. Lược be trong cụm đầu câu thành Faced with.
P5-310|p5-passive|Forecast được xây dựng dựa trên dữ liệu nên dùng Based on, từ cấu trúc be based on.
P5-311|p5-infinitive|Having completed diễn đạt hoàn tất kiểm tra an toàn trước khi cho khởi động lại. Having là trợ thành phần của cụm phân từ hoàn thành.
P5-312|p5-comparison|Not only reduce… but also improve… nối hai động từ nguyên mẫu cùng phụ thuộc will; cần cấu trúc song song.
P5-313|p5-comparison|Sau responsible for, ba công việc giữ cùng dạng V-ing: scheduling, monitoring và preparing.
P5-314|p5-comparison|Both accurate and easy nối hai tính từ cùng mô tả dashboard. Easily là trạng từ, ease/easiness là danh từ.
P5-315|p5-comparison|Either upload… or submit… nối hai nguyên mẫu sau may. Submitting và submission không song song với upload.
P5-316|p5-comparison|Aims to nối ba nguyên mẫu shorten, reduce và improve. Không chia -s ở mục cuối danh sách.
P5-317|p5-comparison|Faster và easier là hai tính từ so sánh hơn song song mô tả quy trình mới so với quy trình trước.
P5-318|p5-agreement|Hai động từ cùng chủ ngữ the company: renews hoặc relocates. Relocates giữ ngôi thứ ba số ít và song song về thì.
P5-319|p5-comparison|Danh sách nhiệm vụ sau requires gồm preparing, negotiating và evaluating, cùng dạng V-ing.
P5-320|p5-word-form|Recommendations là danh từ cần tính từ practical. Ba cụm clear organization, concise language, practical recommendations có cấu trúc tương ứng.
P5-321|p5-conjunction|Provided that + mệnh đề nêu điều kiện được truy cập: hoàn thành đào tạo bảo mật. Despite cần cụm danh từ hoặc V-ing.
P5-322|p5-passive|Các văn phòng được thông báo trước khi sửa mẫu. Having been informed diễn đạt cả tính bị động và thứ tự trước sau.
P5-323|p5-word-form|Independently là trạng từ bổ nghĩa reviewed, mô tả cách từng đề xuất được xem xét độc lập.
P5-324|p5-agreement|Trong neither… nor…, động từ theo chủ ngữ gần nhất ở đây là the summary số ít, nên dùng is.
P5-325|p5-advanced|Had the vendor disclosed… là đảo ngữ điều kiện trái quá khứ, tương ứng If the vendor had disclosed…
P5-326|p5-comparison|Not only to identify… but also to verify… giữ cấu trúc nguyên mẫu song song. Sau to cần verify.
P5-327|p5-agreement|Together with… là phần bổ sung, không đổi chủ ngữ chính policy số ít. Vì vậy dùng is available.
P5-328|p5-advanced|Recommended that đưa đề nghị; a copy nhận hành động lưu giữ. Dùng be retained, nguyên mẫu bị động trong mệnh đề giả định.
""")

add("""
P3-052-Q1|p3-overview|Hai người nói bản cập nhật bảo mật chưa hoàn tất vì vấn đề tương thích trên máy cũ; chủ đề là cập nhật bị chậm.
P3-052-Q2|p3-detail|Người đàn ông nói visitors arriving at nine tomorrow: khách tới lúc chín giờ ngày mai, không phải chiều nay.
P3-052-Q3|p3-next|Người phụ nữ sẽ nhờ nhóm kiểm tra lại trang đăng nhập dự phòng vào chiều nay; không có yêu cầu đổi lịch khách.
P3-052-Q4|p3-intent|Compatibility issue with the older models cho biết một số máy tính bảng tiếp tân thuộc dòng cũ; không nói máy bị mất hay mất mạng.
P3-G18-Q2|p3-next|Can we use the backup login page? đề xuất dùng trang đăng nhập dự phòng trong lúc bản cập nhật chưa xong.
P3-G18-Q3|p3-detail|Khách sẽ tới lúc chín giờ sáng mai, nên hệ thống tiếp đón phải dùng được trước thời điểm đó.
P3-053-Q1|p3-overview|Vấn đề là phụ đề không khớp âm thanh của video an toàn; các lượt nói sau bàn cách dùng tệp đã sửa.
P3-053-Q2|p3-detail|The vendor sent a corrected file this morning: nhà cung cấp gửi tệp đã sửa, không phải thiết bị hay tài liệu in.
P3-053-Q3|p3-next|Người đàn ông hỏi có tải tệp lên learning portal ngay không; câu Please do xác nhận bước tiếp theo là tải lên.
P4-046-Q1|p4-purpose|Thông báo hướng dẫn dùng ứng dụng công ty để làm thủ tục tại máy ở sảnh; đây là tính năng check-in mới.
P4-046-Q2|p4-action|Scan the code displayed on the kiosk screen yêu cầu quét mã trên màn hình máy tự phục vụ, không phải giấy tờ khác.
P4-046-Q3|p4-detail|A printed badge will still be required xác nhận vẫn cần thẻ in trước khi vào khu họp, dù đã check-in bằng ứng dụng.
P3-054-Q1|p3-detail|Phụ đề xuất hiện muộn khoảng năm giây. Người trình bày và địa điểm không phải vấn đề được nêu.
P3-054-Q2|p3-next|Người phụ nữ sẽ chỉnh sync setting của nền tảng phát trực tiếp để đồng bộ phụ đề và âm thanh.
P3-054-Q3|p3-detail|Run another test in ten minutes chỉ một lần kiểm tra lại sau mười phút, không phải thời điểm đóng văn phòng.
P4-047-Q1|p4-purpose|Công trình ở cửa chính khiến điểm đón xe sân bay chuyển sang cửa bắc; đây là nội dung chính của thông báo.
P4-047-Q2|p4-action|Khách cần đi theo biển xanh tới north entrance, nơi đón xe thay thế bắt đầu từ tối nay.
P4-047-Q3|p4-detail|Assist guests with luggage cho biết nhân viên sẽ giúp hành lý. Không có thông tin về in thẻ lên máy bay.
P3-055-Q1|p3-detail|Ba phiếu hỗ trợ bị thiếu tên khách hàng. Đây là lỗi dữ liệu biểu mẫu, không phải website tải chậm.
P3-055-Q2|p3-next|Người phụ nữ yêu cầu required-field warning; người đàn ông đồng ý thêm cảnh báo đó rồi kiểm thử.
P3-055-Q3|p3-detail|Within the hour nghĩa là trong vòng một giờ, khác với giờ đóng quầy hay ngày mai.
P3-056-Q1|p3-overview|Bàn, màn hình và trạm kết nối đều phục vụ đội phân tích chuyển lên tầng bốn; chủ đề là chuẩn bị chỗ làm.
P3-056-Q2|p3-detail|Cần mười hai màn hình nhưng mới nhận tám: còn thiếu bốn. Bốn chiếc sẽ mượn từ phòng đào tạo.
P3-056-Q3|p3-next|Người phụ nữ sẽ nhờ facilities lắp các trạm kết nối, nên bước tiếp theo phù hợp là liên hệ bộ phận cơ sở vật chất.
P3-057-Q1|p3-overview|Người đàn ông không mở được tệp trình chiếu đã nhận; cuộc gọi nhằm xử lý vấn đề với tệp đó.
P3-057-Q2|p3-next|Could you upload it to the vendor portal instead? yêu cầu chuyển tệp lên cổng nhà cung cấp thay vì gửi email.
P3-057-Q3|p3-detail|Người phụ nữ hứa gửi temporary password, tức mật khẩu tạm để truy cập tệp.
P4-048-Q1|p4-purpose|Máy check-in ngừng hoạt động để cài bản vá; khách tạm làm thủ tục tại bàn bảo vệ. Đó là thay đổi chính.
P4-048-Q2|p4-action|Visitors should check in at the security desk xác định nơi khách đến làm thủ tục ngày mai.
P4-048-Q3|p4-action|Nhân viên có khách cần gửi danh sách cho lễ tân trước 5 giờ chiều nay, không phải tự cài bản vá.
P4-049-Q1|p4-purpose|Máy in màu đã sửa xong và có thể đến lấy. Người gọi báo tình trạng sửa chữa, không nhắc nợ thanh toán.
P4-049-Q2|p4-detail|Kỹ thuật viên thay paper tray, tức khay giấy, và không thu thêm phí.
P4-049-Q3|p4-action|Please bring your service receipt yêu cầu mang biên nhận dịch vụ khi tới lấy máy.
P4-050-Q1|p4-purpose|Đây là quảng cáo buổi đào tạo Managing Remote Project Teams với bài tập thực hành và ưu đãi đăng ký.
P4-050-Q2|p4-detail|Designed for new project managers xác định đối tượng là những quản lý dự án mới.
P4-050-Q3|p4-detail|Đăng ký trước thứ sáu nhận giảm 15 phần trăm và sách bài tập điện tử; không có phòng khách sạn miễn phí.
P3-G19-Q1|p3-detail|Phòng pháp lý yêu cầu đồng ý của từng khách trước khi ghi âm; vì chưa có đồng ý nên chưa bật chép lời tự động.
P3-G19-Q2|p3-next|Người phụ nữ sẽ thêm thông báo xin phép vào thư mời và nhờ quản lý khách hàng xác nhận với khách.
P3-G19-Q3|p3-detail|Sau khi quản lý trả lời, người đàn ông sẽ đặt tự xóa bản ghi sau ba mươi ngày; không nói xóa ngay.
P3-G20-Q1|p3-overview|Hai trụ sạc xe trong nhà để xe đang offline vì hư hại do nước; đây là vấn đề chính.
P3-G20-Q2|p3-detail|Hội thảo sáng thứ năm có khách đi xe điện. Người đàn ông lo họ cần sạc trong lúc chờ linh kiện sửa chữa.
P3-G20-Q3|p3-next|Người phụ nữ sẽ đặt bốn chỗ tại bãi sạc công cộng bên kia đường và gửi kèm bản đồ.
P3-G21-Q1|p3-detail|Mười hai máy quét cũ không cài được cập nhật bảo mật. Thử nghiệm trên thiết bị mới đã hoạt động.
P3-G21-Q2|p3-detail|Leased replacements… arrive Tuesday cho biết thiết bị thay thế thuê sẽ tới thứ ba.
P3-G21-Q3|p3-next|Người đàn ông sẽ cấp temporary security keys cho ca đêm dùng tạm, kèm bảng ký nhận với giám sát.
P4-G16-Q1|p4-purpose|Thông báo giới thiệu quy trình quét nhãn kệ bằng drone sau giờ đóng kho và các hướng dẫn an toàn liên quan.
P4-G16-Q2|p4-action|Keep the main aisles clear by eight thirty P.M. yêu cầu dọn thông lối chính trước 8 giờ 30 tối.
P4-G16-Q3|p4-detail|Kiểm đếm thủ công tiếp tục trong refrigerated zone cho tới khi kiểm tra an toàn hoàn tất; đó là khu lạnh.
P4-G17-Q1|p4-purpose|Câu mở đầu xác định người nhận là nhà cung cấp tham gia chương trình bao bì tái sử dụng.
P4-G17-Q2|p4-action|Return the empty container within ten business days yêu cầu trả thùng rỗng trong mười ngày làm việc, không phải trả hóa đơn.
P4-G17-Q3|p4-detail|Sau mỗi lần trả thùng hoàn tất, ưu đãi bao bì xuất hiện trên hóa đơn tiếp theo; không phải giảm ngay trên chuyến hiện tại.
P4-G18-Q1|p4-purpose|Ứng dụng tạm dừng để cài security upgrade. Giá vé và tuyến đường sắt mới không phải nguyên nhân.
P4-G18-Q2|p4-detail|Ticket kiosks… remain in service cho biết máy bán vé tại ga vẫn hoạt động trong thời gian ứng dụng ngừng.
P4-G18-Q3|p4-detail|Bản cập nhật cung cấp cảnh báo khi departure platform thay đổi, tức đổi sân ga khởi hành.
P3-G22-Q1|p3-detail|Máy quét ở sảnh đã được chuyển vì quầy bảo vệ đang sửa, nên khách dùng cửa đông trong tuần này.
P3-G22-Q2|p3-next|Người đàn ông đồng ý gửi hành trình sửa lại và yêu cầu thêm mã truy cập tạm; người phụ nữ sẽ gửi bản cập nhật.
P3-G22-Q3|p3-intent|Mã hết hạn lúc trưa, ngay sau khi chuyến tham quan kết thúc. Do đó mã còn hiệu lực suốt chuyến tham quan.
P3-G23-Q1|p3-overview|Báo giá phụ đề chỉ gồm tiếng Anh, trong khi một khách cần tiếng Nhật; vấn đề là thiếu ngôn ngữ cần thiết.
P3-G23-Q2|p3-intent|Văn phòng Tokyo có thông dịch viên. Nhắc đến văn phòng này nhằm đề xuất người hỗ trợ dịch phần hỏi đáp từ xa.
P3-G23-Q3|p3-intent|Nếu thông dịch viên rảnh, họ giữ nhà cung cấp cho phần trình bày chính và không cần đổi lịch.
P4-G19-Q1|p4-purpose|Thông báo chỉ nơi nhận hành lý thường và đồ quá khổ cho hành khách chuyến 482, kèm hướng dẫn xem thông tin.
P4-G19-Q2|p4-detail|Một trạm quét đang sửa khiến ứng dụng có thể cập nhật chậm vài phút; màn hình ở băng chuyền mới là nguồn hiện hành.
P4-G19-Q3|p4-detail|Xe đạp thuộc oversized items, được đưa tới quầy dịch vụ cạnh băng chuyền số tám, không phải băng chuyền số sáu.
P4-G20-Q1|p4-purpose|Kỹ thuật viên hiệu chuẩn lại các đồng hồ đo điện mặt trời trên mái, nên cổng theo dõi tạm ngừng.
P4-G20-Q2|p4-detail|Các báo cáo hẹn trong thời gian bảo trì sẽ tạo vào sáng hôm sau; chúng được lùi lịch chứ không bị hủy.
P4-G20-Q3|p4-action|Chỉ gửi chỉ số thủ công nếu cảnh báo vẫn hiện sau khi cổng hoạt động trở lại. Việc bảo trì không cắt điện cửa hàng.
P3-G24-Q1|p3-intent|Ít người nhấp liên kết hơn nhưng nhiều người nhập mật khẩu hơn: tần suất nhấp giảm trong khi hành vi sau đó nguy hiểm hơn.
P3-G24-Q2|p3-detail|Báo cáo mới bao phủ hai tuần và một số nhân viên mới chưa được đào tạo; thời gian quan sát còn hạn chế.
P3-G24-Q3|p3-next|Separate new-hire results yêu cầu phân tích nhân viên mới thành nhóm riêng, không xóa dữ liệu mật khẩu khỏi báo cáo.
P4-G21-Q1|p4-detail|Đường hầm đi bộ đang đóng để kiểm tra, khiến tuyến đi bộ thường dùng từ ga tới cửa tây không dùng được.
P4-G21-Q2|p4-action|Bản đồ trong email xác nhận hôm qua vẫn vẽ tuyến hầm đã đóng; người nghe được yêu cầu bỏ qua bản đồ ấy.
P4-G21-Q3|p4-detail|Người có vé in được lên xe đưa đón thẳng mà không phải check-in trước tại bàn thông tin.
""")

add("""
P6-029|p6-grammar|Thiết bị được lắp đặt: can be + V3 tạo bị động. Installed là phân từ, còn installation là danh từ.
P6-030|p6-grammar|By Wednesday evening nêu hạn cuối dọn đồ khỏi tủ. Between cần hai mốc; among và onto không chỉ hạn thời gian này.
P6-031|p6-linking|During the closure nêu khoảng thời gian được dùng phòng tập chi nhánh khác. During theo sau bằng cụm danh từ.
P6-032|p6-grammar|Sau will dùng nguyên mẫu resume, nghĩa là trở lại hoạt động bình thường vào sáng thứ sáu.
P6-033|p6-grammar|Stop using nghĩa là dừng sử dụng ấm có nguy cơ quá nhiệt. Stop + V-ing diễn đạt chấm dứt hành động.
P6-034|p6-linking|If nối mệnh đề điều kiện mực nước quá thấp với khả năng ấm quá nhiệt; các giới từ còn lại không đi với mệnh đề đầy đủ.
P6-035|p6-grammar|A full refund là hoàn tiền toàn bộ. Sau a full cần danh từ refund, không dùng tính từ refundable.
P6-036|p6-grammar|Be available on our website cho biết có thể tìm thông tin trên website; available là tính từ sau is.
P6-037|p6-grammar|At no additional charge là cụm nghĩa là không thu thêm phí; charge là danh từ trong cụm cố định này.
P6-038|p6-linking|But nối hai ý tương phản: đồ ăn uống được cung cấp nhưng người tham gia tự mang kem chống nắng.
P6-039|p6-grammar|By June 13 chỉ hạn cuối điền biểu mẫu tham gia. At không dùng trực tiếp trước ngày tháng theo cách này.
P6-040|p6-grammar|Buổi dã ngoại bị hoãn nếu mưa lớn nên dùng will be postponed, cấu trúc bị động tương lai.
P6-041|p6-grammar|Easier to locate nghĩa là dễ tìm hơn. Sau to trong cấu trúc này cần động từ nguyên mẫu.
P6-042|p6-grammar|Can chi phối các động từ song song download, update và schedule; mục cuối cũng dùng nguyên mẫu.
P6-043|p6-grammar|Sau should dùng clear nguyên mẫu. Clear the browser cache là thao tác xóa bộ nhớ đệm trình duyệt.
P6-044|p6-grammar|By phone or e-mail diễn đạt phương tiện liên hệ hỗ trợ. Hai phương thức cùng phụ thuộc by.
P6-045|p6-grammar|Thursday afternoon là cụm thời gian chiều thứ năm; afternoon ở số ít vì chỉ một buổi cụ thể.
P6-046|p6-grammar|Thẻ tạm được phát ở bàn bảo vệ nên dùng will be issued. Issuer là người hoặc đơn vị phát hành.
P6-047|p6-grammar|Would + nguyên mẫu: violate company security policy nghĩa là vi phạm chính sách an ninh trong tình huống nhờ người khác mở cửa.
P6-048|p6-grammar|Has been activated là hiện tại hoàn thành bị động, cho biết hệ thống đã được kích hoạt trước khi đăng hướng dẫn bổ sung.
P6-049|p6-grammar|Packaging materials là danh từ chỉ vật liệu đóng gói. Các lựa chọn còn lại không tạo cụm danh từ phù hợp sau provider of.
P6-050|p6-grammar|Keep + tân ngữ + tính từ: keeping costs comparable to current levels, giữ chi phí tương đương mức hiện tại.
P6-051|p6-grammar|By submitting nêu cách gửi yêu cầu đặc biệt. Sau giới từ by dùng V-ing.
P6-052|p6-grammar|Supply shortages là tình trạng thiếu nguồn cung. Prevent cần tân ngữ danh từ để diễn đạt ngăn tình trạng đó.
P6-053|p6-grammar|Interdepartmental là tính từ bổ nghĩa communication, nghĩa là giao tiếp giữa các phòng ban.
P6-054|p6-grammar|Has reached capacity là hiện tại hoàn thành, cho biết buổi học đã đủ chỗ và đăng ký sẽ đóng.
P6-055|p6-grammar|Development records là hồ sơ phát triển nghề nghiệp để bổ sung chứng chỉ. Records là danh từ phù hợp ngữ cảnh hồ sơ.
P6-056|p6-grammar|Be expected to + nguyên mẫu: strengthen collaboration nghĩa là tăng cường hợp tác giữa các bộ phận.
P6-057|p6-grammar|Edge computing là thuật ngữ điện toán biên, phù hợp vị trí gần khách hàng để giảm độ trễ truyền dữ liệu.
P6-058|p6-grammar|Without + V-ing: without exposing customer records nghĩa là chuyển ứng dụng mà không làm lộ hồ sơ khách.
P6-059|p6-grammar|Immediately bổ nghĩa report, yêu cầu báo ngay tình trạng chậm bất thường để nhóm hạ tầng xử lý nhanh.
P6-060|p6-grammar|Consistent là tính từ bổ nghĩa service quality, diễn đạt duy trì chất lượng dịch vụ ổn định trong lúc giảm chi phí.
P6-061|p6-grammar|More concise summaries nghĩa là các bản tóm tắt súc tích hơn. More đi với tính từ concise; không dùng đồng thời more và conciser.
P6-062|p6-grammar|Have given là hiện tại hoàn thành của give. Give consent nghĩa là đồng ý, là điều kiện dùng công cụ trong cuộc họp.
P6-063|p6-linking|Unless nêu ngoại lệ của việc xóa tự động. Chủ ngữ a project manager số ít đi với requests ở hiện tại đơn.
P6-064|p6-linking|Before scheduling yêu cầu đọc hướng dẫn trước lần lên lịch họp đầu tiên, phù hợp đoạn thông báo quy trình sử dụng.
P6-065|p6-grammar|Actual là tính từ mô tả dữ liệu khách thật, đối lập với dữ liệu tổng hợp được dùng để thử giao diện.
P6-066|p6-grammar|Individual customers là các khách riêng lẻ; cần tính từ individual đứng trước customers.
P6-067|p6-linking|Since nêu nguyên nhân cần ghi rõ giả định: mô hình có thể tạo kiểu mua hàng không thực tế.
P6-068|p6-grammar|Wider use nghĩa là sử dụng rộng rãi hơn. Use là danh từ, cần tính từ wider thay vì trạng từ widely.
P6-069|p6-grammar|To monitor nêu mục đích thử nhãn thông minh: theo dõi độ tươi của sản phẩm. Sau to dùng nguyên mẫu.
P6-070|p6-linking|Before unloading quy định quét nhãn trước khi dỡ hàng để phát hiện sớm lô có vấn đề nhiệt độ.
P6-071|p6-grammar|Immediately là trạng từ bổ nghĩa placed. Lô có cảnh báo phải để riêng kiểm tra thay vì đưa ngay lên kệ.
P6-072|p6-grammar|In October là cụm chỉ thời gian xem kết quả thử nghiệm. Các lựa chọn khác không phải tên tháng hay mốc thời gian phù hợp.
P6-G28-Q1|p6-insertion|Một thư mục cần giữ bị đưa nhầm vào hàng chờ xóa. Câu nói nhóm tạm dừng trước khi xóa nối đúng với Accordingly và việc vô hiệu hóa chức năng.
P6-G28-Q2|p6-insertion|Câu tiếp theo cho quản lý hai ngày để báo ngoại lệ, nên phải có câu gửi danh sách tới các quản lý trước đó.
P6-G28-Q3|p6-grammar|Make + tân ngữ + tính từ: make those reviews more informative, giúp việc rà soát có thêm thông tin.
P6-G28-Q4|p6-grammar|Broader launch nhận hành động lên lịch; sau điều kiện thử nghiệm thành công dùng tương lai bị động will be scheduled.
P6-G32-Q1|p6-grammar|Be interested in là quan tâm đến việc gì. Interested mô tả nhân viên; interesting mô tả thứ gây hứng thú.
P6-G32-Q2|p6-grammar|Develop an understanding là cách kết hợp từ tự nhiên để diễn đạt xây dựng sự hiểu biết về giới hạn phê duyệt và xử lý dữ liệu.
P6-G32-Q3|p6-linking|In addition bổ sung thông tin về bài tập tình huống sau mục tiêu khóa học; đoạn không đưa sự trái ngược hay thay thế.
P6-G32-Q4|p6-insertion|Chọn buổi phù hợp trách nhiệm hiện tại nối phần giới thiệu nhiều buổi học với thông tin hạn đăng ký ở câu sau.
P6-G33-Q1|p6-grammar|Has adopted là hiện tại hoàn thành: nhóm đã áp dụng quy trình phục hồi được sửa sau sự cố.
P6-G33-Q2|p6-linking|Because nêu lý do chọn thứ tư: lưu lượng giao dịch thường thấp hơn thời điểm đó, giúp giảm gián đoạn.
P6-G33-Q3|p6-insertion|Câu về giảm gián đoạn đồng thời xác minh công cụ phục hồi tóm đúng mục đích lịch kiểm thử mới và nối sang hướng dẫn thông báo.
P6-G33-Q4|p6-linking|Tải báo cáo cần gấp trước khi cửa sổ bảo trì bắt đầu. Before nối với mệnh đề the maintenance window opens.
""")

add("""
P7-R35-Q1|p7-purpose|Email hỏi có thể giao sáu bàn chiều thứ ba thay sáng thứ tư không; mục đích là đổi lịch giao hàng.
P7-R35-Q2|p7-cross-reference|Tin nhắn nói giá để catalog ở kho khác; phiếu giao xác nhận chúng tới sáng thứ tư, không phải thứ ba.
P7-R35-Q3|p7-detail|Đội lắp đặt đã có lịch làm gần đó chiều thứ ba, nên đổi lịch bàn không làm phát sinh phí.
P7-R35-Q4|p7-detail|Mei Lin yêu cầu gửi revised delivery note cho bộ phận mua sắm; đó là phiếu giao hàng sửa lại.
P7-R36-Q1|p7-purpose|Thông báo giới thiệu tuyến xe đưa đón mới giữa ga Central và khu doanh nghiệp Lakeside, kèm giờ và điểm dừng.
P7-R36-Q2|p7-detail|Every twenty minutes là tần suất buổi sáng. 7 giờ và 9 giờ 30 là hai đầu khung phục vụ, không phải chỉ một chuyến.
P7-R36-Q3|p7-detail|Thử nghiệm một tháng dùng để quyết định có thêm dịch vụ giữa trưa hay không, khác khảo sát nhu cầu đỗ xe của HR.
P7-R36-Q4|p7-cross-reference|Email của HR nêu mục đích khảo sát xem xe đưa đón có làm giảm nhu cầu đỗ xe tại văn phòng không.
P7-R37-Q1|p7-detail|Cửa nhân viên gần căn tin sẽ mở lại thứ hai sau khi sửa sàn cuối tuần; không có việc đóng căn tin vĩnh viễn.
P7-R37-Q2|p7-detail|Nhân viên tạm dùng cửa nam và cần thêm thời gian kiểm tra an ninh, nên phải đi sớm hơn.
P7-R38-Q1|p7-purpose|Biển đèn mới giao bị nứt; Becker hỏi về thay thế trước ngày khai trương và thu hồi biển hỏng.
P7-R38-Q2|p7-detail|Thư trả lời xác nhận Wednesday morning là thời điểm giao biển thay thế. Next Friday là ngày khai trương.
P7-R38-Q3|p7-detail|Installers will take away the damaged unit at no charge xác nhận miễn phí thu hồi biển bị hỏng.
P7-R38-Q4|p7-detail|Shipping warranty chi trả việc thay thế, nên khách không nhận thêm hóa đơn; không phải vì khai trương hoãn.
P7-R39-Q1|p7-purpose|Căn tin chuyển sang thanh toán bằng thẻ nhân viên và ngừng nhận tiền mặt ở quầy từ ngày 1 tháng 8.
P7-R39-Q2|p7-detail|Cổng nhân viên cho phép đặt weekly spending limit, tức giới hạn chi tiêu theo tuần.
P7-R39-Q3|p7-cross-reference|HR yêu cầu người có thẻ lỗi đến trước 11 giờ để sửa trước cao điểm ăn trưa của hệ thống thanh toán mới.
P7-R39-Q4|p7-detail|Nhà thầu và khách vẫn mua meal vouchers ở lễ tân; email không cho họ kích hoạt thẻ nhân viên.
P7-R40-Q1|p7-purpose|Thông báo và lịch trình giải thích việc chuyển phòng tiếp thị lên tầng mười hai cùng các bố trí tạm thời.
P7-R40-Q2|p7-cross-reference|Thông báo và bảng lịch đều xác định hạn ngắt máy tính là 5 giờ chiều ngày 13 tháng 6.
P7-R40-Q3|p7-detail|Email yêu cầu họp khách ngày 14 tháng 6 tại khu tiếp tân tầng mười một; phòng đào tạo dành cho chỗ làm tạm.
P7-R40-Q4|p7-detail|Nhân viên tự mang đồ dễ vỡ như giải thưởng và đồ điện tử cá nhân thay vì cho chung vào thùng chuyển.
P7-R40-Q5|p7-detail|Phone extensions will remain the same xác nhận số máy lẻ giữ nguyên sau chuyển chỗ.
P7-R41-Q1|p7-purpose|Thông báo giới thiệu cổng trực tuyến và thủ tục nộp yêu cầu bảo hành mới, không phải thông báo thu hồi sản phẩm.
P7-R41-Q2|p7-detail|Khách phải tải hóa đơn mua hàng và số sê-ri sản phẩm lên cổng; ảnh sản phẩm không được nêu là bắt buộc.
P7-R41-Q3|p7-cross-reference|Mua ngày 18 tháng 8, hỏng ngày 5 tháng 9: trong vòng ba mươi ngày. Đối chiếu chính sách để thấy đủ điều kiện đổi.
P7-R41-Q4|p7-detail|Nhân viên giao nhận lấy máy hỏng this Friday; following Monday là ngày giao máy thay thế, tránh đổi nhầm hai mốc.
P7-R41-Q5|p7-inference|Email nói rõ You do not need to return to the store; việc lấy và giao tại chỗ giúp Park không phải quay lại cửa hàng.
P7-R42-Q1|p7-purpose|Email xác nhận lịch giao ghế và lắp đặt sau khi lô hàng được giải phóng khỏi kho bị chậm.
P7-R42-Q2|p7-detail|Tài xế tới Tuesday between 8 A.M. and 10 A.M., tức sáng thứ ba. Sáng thứ tư là lịch kỹ thuật viên.
P7-R42-Q3|p7-detail|Trong tin nhắn, Jordan yêu cầu để labeled hardware boxes trong phòng kho, tức các hộp phụ kiện đã dán nhãn.
P7-R42-Q4|p7-detail|Kỹ thuật viên sẽ kiểm tra electrical outlet trước lắp ghế; đó là ổ điện, không phải xe giao hàng.
P7-R42-Q5|p7-inference|Email nhắc shipment that was delayed at the regional warehouse; lô hàng đã chậm tại kho, không nói ghế hư.
P7-R43-Q1|p7-purpose|Sảnh đóng để thay sàn và người ra vào dùng cửa đông; thông báo giải thích thay đổi cửa tạm thời.
P7-R43-Q2|p7-detail|Khoảng đóng sảnh là July 8 through July 12. Khung 7 giờ sáng tới 7 giờ tối chỉ giờ có bảo vệ.
P7-R43-Q3|p7-detail|Email yêu cầu tài xế check in with security trước khi dỡ hàng; thang hàng vẫn hoạt động.
P7-R43-Q4|p7-cross-reference|Carlos hỏi về giao máy in và được Maya hướng dẫn báo tài xế, cho thấy ông xử lý giao hàng cho một đơn vị thuê trong tòa nhà.
P7-R43-Q5|p7-detail|9 A.M. là mốc để tài xế tới sau đó khi giấy giao hàng đã sẵn; không phải giờ mở lại sảnh.
P7-R44-Q1|p7-purpose|Email thông báo khóa đào tạo nhận diện lừa đảo dùng AI, ví dụ âm thanh/video và quy trình báo cáo.
P7-R44-Q2|p7-detail|Khóa dài 45 minutes. Hai ngày là khoảng gửi nhắc trước hạn, không phải thời lượng học.
P7-R44-Q3|p7-cross-reference|Marco xử lý hoàn tiền trực tuyến nên thuộc nhóm tiếp xúc thông tin thanh toán và phải hoàn thành trước ngày 12 tháng 8.
P7-R44-Q4|p7-detail|Hệ thống gửi lời nhắc trước hạn hai ngày; không có nội dung khóa yêu cầu hoàn tiền hay đổi mật khẩu khách.
P7-R45-Q1|p7-purpose|Công ty thử phần mềm giám sát nhà máy trên Line 4, thu nhiệt độ và cảnh báo bảo trì; đây là đợt thử phần mềm.
P7-R45-Q2|p7-detail|Trong thử nghiệm, người vận hành vẫn dùng existing inspection checklist, tức danh sách kiểm tra đang có.
P7-R46-Q1|p7-purpose|Email giới thiệu đợt thử thẻ số trong ứng dụng công ty, nêu người tham gia, chức năng và hạn phản hồi.
P7-R46-Q2|p7-detail|Hai nhóm tham gia là Facilities và Visitor Services; nhà thầu chưa nằm trong đợt thử.
P7-R46-Q3|p7-detail|Lina nói điện thoại tụt pin nhanh hơn thường lệ dù mở được cửa tây; lo ngại là tiêu hao pin.
P7-R46-Q4|p7-cross-reference|Bản cập nhật dự án hẹn low-power setting trước giai đoạn kế; tin nhắn xác nhận tính năng đó nhằm xử lý vấn đề pin của Lina.
""")

add("""
P7-R47-Q1|p7-purpose|Thông báo giải thích thử hai robot kiểm kê qua đêm ở các lối 3–8, cùng việc nhân viên cần tiếp tục làm.
P7-R47-Q2|p7-detail|Tuần đầu nhân viên vẫn thực hiện regular morning count để có số kiểm kê đối chiếu với robot.
P7-R47-Q3|p7-detail|Email ghi aisle 6 had several blocked locations: một số vị trí ở lối sáu bị chắn, không phải mọi nhãn đều không quét được.
P7-R47-Q4|p7-cross-reference|Thứ sáu nhóm sẽ so danh sách robot tạo với kết quả kiểm kê buổi sáng rồi mới quyết định kéo dài thử nghiệm.
P7-R47-Q5|p7-detail|Pallet tạm cần đặt ngoài đường robot để tránh chặn lối quét, như vấn đề đã xảy ra ở lối sáu.
P7-R48-Q1|p7-purpose|Email thông báo thử tính năng đặt chỗ ngồi qua ứng dụng cho nhân viên tầng ba, kèm thời gian và hướng dẫn.
P7-R48-Q2|p7-detail|Up to five days in advance cho phép đặt trước tối đa năm ngày, không phải một tuần.
P7-R48-Q3|p7-cross-reference|Ravi cần hai màn hình; email và Naomi đều chỉ bàn có biểu tượng xanh đáp ứng nhu cầu đó, trong khi 3B chỉ có một màn hình.
P7-R48-Q4|p7-detail|FAQ yêu cầu đặt chỗ khách qua lễ tân vì guest access badges được xử lý riêng; không nói khách bị cấm lên tầng ba.
P7-R48-Q5|p7-detail|Hạn gửi phản hồi là October 7. October 4 là ngày kết thúc đợt thử, không phải hạn phản hồi.
P7-R50-Q1|p7-purpose|Hội thảo chuyển từ phòng B sang Lakeside Training Suite; mục đích email là báo đổi phòng.
P7-R50-Q2|p7-detail|Phòng ban đầu đang sơn lại và chỉ có thể dùng từ thứ tư, nên hội thảo thứ hai phải đổi chỗ.
P7-R50-Q3|p7-detail|Nhân viên phát digital workbook access codes sau khi kiểm tra đăng ký; người học nhận mã truy cập sách bài tập điện tử.
P7-R50-Q4|p7-inference|The agenda has not changed xác nhận chương trình giữ nguyên; đổi phòng không kéo theo đổi nội dung.
P7-R51-Q1|p7-detail|Xe sân bay tạm đón ở lối xe phía đông từ 12–16 tháng 7 vì công trình cửa chính.
P7-R51-Q2|p7-cross-reference|Email làm rõ departure times remain the same; địa điểm đón đổi nhưng giờ khởi hành giữ nguyên.
P7-R51-Q3|p7-detail|Lối phía đông xa thang máy hơn, nên khách cần tới sớm năm phút; xe không khởi hành sớm hơn.
P7-R51-Q4|p7-inference|Chữ ký ghi Operations Manager và Luis hướng dẫn nhóm lễ tân trả lời khách, phù hợp vai trò quản lý vận hành khách sạn.
P7-R52-Q1|p7-purpose|Priya yêu cầu ảnh sản phẩm mới trước chiều thứ năm để kịp chốt bản nháp catalog thứ sáu.
P7-R52-Q2|p7-detail|Ảnh hiện tại vẫn thể hiện older power switch, tức công tắc kiểu cũ; vấn đề không nằm ở độ sáng ảnh.
P7-R52-Q3|p7-detail|Mẫu bạc đang thử nên tuần sau mới chụp được. Marcus đề xuất tạm dùng bản vẽ, không đề xuất bỏ sản phẩm.
P7-R52-Q4|p7-cross-reference|Quy định sản xuất yêu cầu bản vẽ trong catalog kèm chú thích rằng hình thức cuối có thể khác đôi chút; áp dụng cho đề xuất của Marcus.
P7-R53-Q1|p7-purpose|Bản ghi nhớ giải thích quy trình hoàn chi phí công tác qua cổng điện tử thay cho email, kèm dữ liệu bắt buộc.
P7-R53-Q2|p7-detail|Receipts should be uploaded as PDF files: hóa đơn được tải lên dưới dạng PDF.
P7-R53-Q3|p7-detail|Yêu cầu thiếu mã dự án bị returned for correction, tức trả lại để sửa; không tự động duyệt.
P7-R53-Q4|p7-detail|Khoản hoàn được chuyển trong vòng năm ngày làm việc sau khi phê duyệt; không phải ngay lúc nộp.
P6-G20-Q1|p7-purpose|Thông báo sửa quy tắc đặt bàn: phải xác nhận trước 8 giờ 30 trong ngày dùng, nếu không sẽ nhường cho danh sách chờ.
P6-G20-Q2|p7-detail|Bàn chưa xác nhận đúng hạn sẽ được released to employees on the waiting list, tức cấp cho người chờ.
P6-G20-Q3|p7-detail|Các bộ phận báo bàn đã đặt nhưng bỏ trống, nên công ty thêm bước xác nhận để tránh lãng phí chỗ.
P6-G20-Q4|p7-detail|Người hay đi gặp khách vẫn được đặt trước hai tuần nhưng cần hủy sớm những lượt không dùng.
P6-G21-Q1|p7-purpose|Thư trả lời thắc mắc về lô thiết bị bị chậm và giải thích việc kiểm tra thêm hộp bảo vệ.
P6-G21-Q2|p7-detail|Protective cases bị giữ để kiểm tra chất lượng bổ sung do nhà cung cấp báo vấn đề bao bì; máy quét và đế sạc đã sẵn sàng.
P6-G21-Q3|p7-detail|Rather than sending a partial shipment cho biết công ty không gửi từng phần mà chờ gom đủ ba món.
P6-G21-Q4|p7-detail|Khách sẽ nhận new tracking number khi hộp bảo vệ qua kiểm tra; đó là mã theo dõi giao hàng mới.
P6-G22-Q1|p7-detail|Câu mở đầu mời local store owners, tức chủ cửa hàng địa phương; không giới hạn chỉ chuyên gia quyền riêng tư.
P6-G22-Q2|p7-purpose|Diễn đàn tập trung sử dụng dữ liệu khách hàng có trách nhiệm khi cải thiện dịch vụ trực tuyến.
P6-G22-Q3|p7-detail|Hai nhà bán lẻ sẽ kể cách họ redesigned loyalty programs sau phản hồi khách, tức thiết kế lại chương trình khách hàng thân thiết.
P6-G22-Q4|p7-detail|Tham gia miễn phí nhưng mỗi doanh nghiệp chỉ có một đại diện; giới hạn nằm ở số người, không phải phí tăng.
P6-G23-Q1|p7-purpose|Trước đây giám sát duyệt trước kế toán; nay hệ thống kiểm tra trước giám sát. Thay đổi chính là thứ tự xét yêu cầu.
P6-G23-Q2|p7-detail|Hệ thống kiểm tra ba trường project code, date và vendor name: mã dự án, ngày và tên nhà cung cấp.
P6-G23-Q3|p7-detail|Giám sát chỉ xem yêu cầu đã vượt bước kiểm tra đầu tiên của hệ thống; yêu cầu thiếu trường chưa được chuyển tới.
P6-G23-Q4|p7-detail|Quy trình mới được kỳ vọng giảm số hồ sơ chưa đủ thông tin bị trả về cuối tháng.
P6-G24-Q1|p7-detail|Khách mua LX-40 trước ngày 15 tháng 1 đủ điều kiện xin cập nhật miễn phí; không phải mọi người tải ứng dụng.
P6-G24-Q2|p7-detail|Cập nhật cải thiện điều chỉnh nhiệt độ khi cửa sổ mở ngắn, không đổi màu màn hình hay thời hạn bảo hành.
P6-G24-Q3|p7-detail|Thông báo nói rõ không đổi display hoặc mobile-app layout; trong các lựa chọn, giao diện ứng dụng là chi tiết được xác nhận giữ nguyên.
P6-G24-Q4|p7-detail|Khách nhập serial number ở mặt sau thiết bị lên trang hỗ trợ để nhận cập nhật.
P6-G25-Q1|p7-purpose|Nhóm nghiên cứu lý do đơn buổi tối dễ giao muộn dựa trên ba tháng dữ liệu kho.
P6-G25-Q2|p7-detail|Phần lớn chậm trễ xảy ra after 7 P.M., khi ít người phụ trách đóng gói hơn.
P6-G25-Q3|p7-detail|Thêm máy quét không giúp đáng kể vì công nhân vẫn phải chờ shipping labels, tức nhãn giao hàng.
P6-G25-Q4|p7-detail|Nhóm đề xuất chuyển máy in nhãn gần khu đóng gói và thử hai tuần trước khi tính thuê thêm người.
""")

add("""
P6-G26-Q1|p7-detail|Giảng viên dùng câu trả lời để chia người học thành các nhóm có mục tiêu tương tự; bảng hỏi phục vụ xếp nhóm.
P6-G26-Q2|p7-detail|Người muốn luyện thêm cách dùng công cụ trực quan mang một bộ slide ngắn tới buổi đầu, không bắt buộc mọi người.
P6-G26-Q3|p7-detail|Văn phòng khóa học cung cấp laptops and projectors; người học tự mang bộ chuyển nếu máy riêng cần.
P6-G26-Q4|p7-inference|For private review only giới hạn bản ghi cho xem lại riêng, nên không dùng để chia sẻ công khai.
P6-G27-Q1|p7-detail|Thay thao tác vuốt trái bằng nút có nhãn rõ để hiện mã QR; chức năng mã QR vẫn được giữ.
P6-G27-Q2|p7-detail|Người thử có hạn chế vận động tay thấy vuốt khó, nên đội thiết kế điều chỉnh để dễ tiếp cận hơn.
P6-G27-Q3|p7-detail|Nhóm kỹ thuật đã có nút tương tự ở màn hình hoàn tiền, nên tái sử dụng không làm chậm lịch ra mắt.
P6-G27-Q4|p7-detail|A final usability test được lên lịch thứ năm tới; đây là kiểm tra tính dễ dùng, chưa phải ra mắt công khai.
P7-R54-Q1|p7-purpose|Bài viết giới thiệu cảm biến đếm lượt khách mà không lưu mặt hay video, kèm thông báo và rà soát quyền riêng tư.
P7-R54-Q2|p7-detail|Cảm biến chỉ gửi hourly totals lên bảng chung: tổng lượt theo giờ, không gửi video hay tên khách.
P7-R54-Q3|p7-detail|Thương nhân phàn nàn xếp nhân sự cuối tuần chủ yếu dựa vào phỏng đoán; hệ thống cung cấp dữ liệu để quyết định tốt hơn.
P7-R54-Q4|p7-detail|Mỗi cửa hàng tham gia phải niêm yết thông báo giải thích thông tin được thu thập, theo yêu cầu hiệp hội.
P7-R55-Q1|p7-purpose|Helena yêu cầu hai sửa đổi báo cáo trước khi gửi khách, nên email là yêu cầu chỉnh sửa, chưa phê duyệt bản cuối.
P7-R55-Q2|p7-detail|Phần pin trộn kết quả trong nhà và ngoài trời, làm thiết bị trông kém tin cậy hơn so với kết quả trong nhà thực tế.
P7-R55-Q3|p7-detail|Customer interview summary cần chuyển tới appendix, tức phụ lục; kết quả kỹ thuật giữ ở phần chính.
P7-R55-Q4|p7-inference|Khách muốn technical findings trong báo cáo chính và supporting comments cuối tài liệu, cho thấy ưu tiên kết quả kỹ thuật trước.
P7-R56-Q1|p7-purpose|Chương trình cho cư dân mượn dụng cụ sửa nhà nhỏ tối đa bảy ngày; không phải khóa học sửa nhà có thu phí.
P7-R56-Q2|p7-detail|Cư dân cần chứng minh địa chỉ và hoàn tất thỏa thuận an toàn trước khi mượn; không bắt buộc quyên góp dụng cụ.
P7-R56-Q3|p7-detail|Được gia hạn một lần nếu không có người khác yêu cầu dụng cụ đó; thứ bảy đầu tháng là lịch nhận quyên góp.
P7-R56-Q4|p7-detail|Tạm đình chỉ thay vì phạt tiền giúp dịch vụ vẫn dễ tiếp cận về chi phí, đồng thời khuyến khích trả đúng hạn.
P7-R57-Q1|p7-detail|Nhân viên bán hàng nhập ghi chú lần gặp vào cổng trong hai ngày làm việc; đây là yêu cầu lưu thông tin kịp thời.
P7-R57-Q2|p7-detail|Ghi chú gồm mục tiêu hiện tại, mối quan tâm và next action promised của đội; tránh chi tiết cá nhân không liên quan.
P7-R57-Q3|p7-detail|Thông tin chung giúp nhóm dịch vụ phản hồi nhất quán khi đại diện bán hàng vắng mặt, đồng thời tìm vấn đề chung giữa vùng.
P7-R57-Q4|p7-inference|Ghi chú riêng vẫn được giữ, nhưng bản nhập trên cổng mới được coi là hồ sơ chính thức.
P7-R58-Q1|p7-purpose|Thư viện mở thêm giờ để hỗ trợ sinh viên ôn kỳ thi chứng chỉ; không phải để tổ chức giao đồ ăn tối.
P7-R58-Q2|p7-detail|Nhóm từ ba người phải đặt trước; người học riêng có thể dùng chỗ trống mà không đặt.
P7-R58-Q3|p7-detail|Sau 8 giờ tối không nhận food deliveries. Gọi điện phải ra sảnh là quy tắc khác, không phải đáp án trong lựa chọn.
P7-R58-Q4|p7-detail|Bàn thông tin có thêm dây sạc cho người học; laptop không được cho mượn vào khung giờ tối.
P7-R59-Q1|p7-detail|Trạm Central thay máy thanh toán vào thứ hai; việc dự kiến xong trước 4 giờ chiều, không phải xóa vĩnh viễn toàn bộ xe.
P7-R59-Q2|p7-cross-reference|Trong lúc thay máy chỉ mở khóa bằng ứng dụng, nhưng một khách của Dana không có điện thoại thông minh; hai thông tin tạo ra trở ngại.
P7-R59-Q3|p7-detail|Dana dự định thuê hai xe lúc 10 giờ sáng thứ hai. 11 giờ là tour bảo tàng; 4 giờ là hạn xong sửa trạm.
P7-R59-Q4|p7-detail|Dana hỏi có thể nhận xe ở another nearby station, tức một trạm gần khác, bên cạnh khả năng đặt trước.
P7-R60-Q1|p7-purpose|Vị trí đào tạo nhân viên phòng khám sử dụng phần mềm quản lý tồn kho, không phải trực tiếp giao vật tư y tế.
P7-R60-Q2|p7-detail|Ứng viên cần hồ sơ kinh nghiệm và sample training outline, tức đề cương đào tạo mẫu, trước ngày 8 tháng 9.
P7-R60-Q3|p7-detail|Amira đang hoàn thành chứng chỉ tại địa phương nên muốn tránh chuyến qua đêm tới tháng mười một; cô không từ chối mọi chuyến đi.
P7-R60-Q4|p7-cross-reference|Cô làm video giải thích quy trình đặt hàng cho lễ tân phòng khám, đáp ứng kinh nghiệm giải thích kỹ thuật cho người không chuyên.
P7-R61-Q1|p7-detail|Khách nói máy ngừng bơm nước sau tám tháng. Vẫn có hóa đơn và chỉ dùng ở nhà, nên các lựa chọn còn lại trái lời khách.
P7-R61-Q2|p7-detail|Thẻ bảo hành loại trừ hư hại do sửa chữa không được phép; lỗi điện và bơm nằm trong phạm vi được nêu.
P7-R61-Q3|p7-cross-reference|Nhân viên giải thích dùng giấm được phép nếu theo hướng dẫn; việc đó tự nó không loại yêu cầu bảo hành của khách.
P7-R61-Q4|p7-detail|Nhân viên yêu cầu ảnh số sê-ri để bắt đầu xử lý; không yêu cầu hóa đơn sửa từ cửa hàng khác.
P7-R62-Q1|p7-detail|Keynote từ 9 giờ 30 tới 10 giờ 15 có tên Designing Services for Older Customers, không phải hai phiên breakout sau đó.
P7-R62-Q2|p7-cross-reference|Rina cần nhân viên giải thích dịch vụ số rõ hơn; Breakout B dạy đưa chỉ dẫn rõ, phù hợp trực tiếp vấn đề.
P7-R62-Q3|p7-inference|Ngân hàng đã có phần mềm thanh toán dễ tiếp cận, nên Accessible Payment Tools ít cấp thiết hơn buổi luyện giao tiếp cho nhân viên.
P7-R62-Q4|p7-detail|Bảng lịch đặt Panel Discussion từ 11 giờ 30 tới 12 giờ 15; giờ bắt đầu là 11 giờ 30.
P7-R63-Q1|p7-detail|Gói thuê bao gồm unlimited online training, không bao gồm workshop tại chỗ; cần đọc cả phần ngoại lệ.
P7-R63-Q2|p7-detail|Keiko yêu cầu đổi cost center từ 41-A sang 47-C trước thanh toán; không đổi ngày bắt đầu thuê bao.
P7-R63-Q3|p7-detail|Nhóm hỗ trợ khách muốn học vào second week of July, tức tuần thứ hai tháng bảy.
P7-R63-Q4|p7-inference|Before we process payment cho thấy mới duyệt phí nhưng chưa xử lý trả tiền, đang chờ sửa thông tin hóa đơn.
""")

add("""
P7-R64-Q1|p7-detail|Ứng dụng cho cư dân báo vỉa hè hư hỏng bằng ảnh và vị trí, không phải đặt dịch vụ sửa căn hộ.
P7-R64-Q2|p7-detail|Kỹ sư phân nhóm sửa theo safety risk, tức rủi ro an toàn, chứ không chỉ thứ tự nhận báo cáo.
P7-R64-Q3|p7-detail|Cư dân muốn ứng dụng giải thích vì sao báo cáo đã xem nhưng ngày sửa vẫn pending; họ không phản đối ưu tiên tình huống khẩn.
P7-R64-Q4|p7-inference|Reviewed nhưng repair date pending cho thấy báo cáo đã được kiểm tra, chưa có lịch sửa cụ thể.
P7-R65-Q1|p7-detail|Quy định áp dụng nhóm xử lý hồ sơ khách hàng; đoạn cuối miễn học lại cho người đã hoàn thành cùng khóa trong tháng một.
P7-R65-Q2|p7-detail|Chỉ nhân viên đang làm từ xa vào ngày buổi học được dự online; không phải ai thích sáng thứ ba cũng chọn được.
P7-R65-Q3|p7-detail|Điều phối viên phải gửi attendance lists trước chiều thứ sáu, tức danh sách tham dự.
P7-R65-Q4|p7-detail|Người đã học tháng một không học lại nhưng vẫn ghi tên trên danh sách, kèm chú thích completed in January.
P7-R66-Q1|p7-purpose|Từ ngày 1 tháng 6, khách cuối tuần đặt vé theo giờ vào bảo tàng; không có thay đổi thành chỉ mở ngày thường.
P7-R66-Q2|p7-cross-reference|Đoàn trường từ mười lăm người dùng group request form theo email, là ngoại lệ của cách đặt vé cuối tuần thông thường.
P7-R66-Q3|p7-detail|Education office xếp giờ đến sau khi xem lịch xe buýt của đoàn, không để giáo viên tự chọn giờ bất kỳ.
P7-R66-Q4|p7-detail|Hướng dẫn biểu mẫu yêu cầu ghi whether the group plans to attend a workshop, tức đoàn có dự workshop hay không.
P7-R67-Q1|p7-detail|Trang sản phẩm nêu adjustable armrests, tay vịn điều chỉnh được. Bảo hành khung năm năm, không phải vải mười năm.
P7-R67-Q2|p7-detail|Văn phòng đặt mười hai ghế xám nhưng nhận hai ghế xanh; họ liên hệ vì giao sai màu.
P7-R67-Q3|p7-detail|Báo sai màu cần order number và ảnh món nhận được trong bảy ngày; không yêu cầu hóa đơn sửa.
P7-R67-Q4|p7-cross-reference|Chính sách miễn phí giao món thay khi lỗi được xác nhận, nên văn phòng không cần trả thêm phí giao hai ghế thay màu.
P7-R68-Q1|p7-purpose|Thử đặt trước nhằm giảm hàng chờ giờ trưa, phù hợp khảo sát 62 phần trăm than phiền hàng dài.
P7-R68-Q2|p7-detail|Đặt trước 10 giờ sáng; khoảng trưa tới 1 giờ chiều là giờ nhận món, không phải hạn đặt.
P7-R68-Q3|p7-cross-reference|Khảo sát chỉ ra thứ ba và thứ năm đông; quản lý cũng nhấn mạnh hai ngày đó cần nhiều người dùng thử.
P7-R68-Q4|p7-inference|Người quên đặt vẫn được mua trực tiếp nhưng có thể phải xếp hàng lâu; không bị cấm vào căn tin.
P7-R69-Q1|p7-purpose|Ứng dụng thêm thông tin mức đông theo thời gian thực, ước lượng độ đầy của từng toa tàu.
P7-R69-Q2|p7-detail|FAQ nhấn mạnh không nhận dạng cá nhân và không thu tên, số vé hoặc vị trí điện thoại.
P7-R69-Q3|p7-detail|Jordan dùng xe lăn và cần chọn toa có không gian cửa phù hợp; thông tin từng toa hữu ích hơn con số chung cả tàu.
P7-R69-Q4|p7-detail|FAQ nói rõ không thu phone locations. Câu hỏi yêu cầu thông tin bị loại trừ rõ ràng, không yêu cầu suy đoán đầu vào thuật toán.
P7-R70-Q1|p7-detail|Hoạt động gồm dọn rác, trồng hoa và báo biển đường hư; báo cáo hư hại không đồng nghĩa tự sửa tất cả biển.
P7-R70-Q2|p7-detail|Ban tổ chức cấp dụng cụ và găng; tình nguyện viên tự mang refillable water bottles, bình nước nạp lại.
P7-R70-Q3|p7-cross-reference|May chỉ tham gia sau khi mở cửa hàng lúc 9 giờ, trong khi nhóm trồng hoa rời đi đầu tiên để tránh nóng.
P7-R70-Q4|p7-detail|May mong ba người được chấp nhận để Chen Books có tên trên website, đúng điều kiện doanh nghiệp gửi ít nhất ba tình nguyện viên.
P7-R71-Q1|p7-detail|Up to six days per month là tối đa sáu ngày mỗi tháng làm ở chi nhánh khác theo quy định thông thường.
P7-R71-Q2|p7-detail|Đặt trong ngày chỉ được khi quản lý xác nhận chuyến đi liên quan yêu cầu khách khẩn cấp; bàn trống không tự tạo ngoại lệ.
P7-R71-Q3|p7-detail|Nhân viên dự đào tạo đã lên lịch được Learning Department đặt chỗ tự động nên không tự dùng hệ thống bàn làm việc.
P7-R71-Q4|p7-detail|Ở lại làm việc riêng sau đào tạo phải book the additional time separately, đặt riêng thời gian kéo dài.
P7-R72-Q1|p7-detail|Bước đầu là tải tệp dự án đang làm lên thư mục chuyển an toàn trước khi hoàn trả laptop.
P7-R72-Q2|p7-detail|Ngay sau nộp biểu mẫu hoàn trả, hệ thống tạo tracking label. Biên nhận chỉ xuất hiện khi đơn vị vận chuyển quét nhãn.
P7-R72-Q3|p7-detail|Laptop và adapter gửi đi, nhưng external keyboards phải để lại văn phòng; đọc đối lập sau but.
P7-R72-Q4|p7-detail|IT chỉ đóng hồ sơ sau xác nhận máy khởi động bình thường và phụ kiện đầy đủ; nhận biên lai giao hàng chưa đủ.
P7-R73-Q1|p7-cross-reference|Giờ giao cũ 8 giờ nằm trong kiểm tra điện 7–9 giờ, lúc thang hoạt động hạn chế; đối chiếu thông báo để hiểu lý do đổi.
P7-R73-Q2|p7-detail|Email đổi giờ nhóm lắp đặt từ 8 giờ 30 sang 10 giờ 30; 10 giờ là lịch giao thiết bị.
P7-R73-Q3|p7-detail|Bến vẫn mở cho lô y tế và thực phẩm khẩn cấp; thiết bị sân khấu cho diễn tập chiều không thuộc ngoại lệ.
P7-R73-Q4|p7-cross-reference|Thiết bị được hẹn giao 10 giờ, trước nhóm lắp đặt 10 giờ 30, nên việc giao sẽ diễn ra trước khi nhóm tới.
P7-R74-Q1|p7-detail|Sau thử nghiệm, chat chờ hai phút, điện thoại sáu phút và email chín giờ. Chat có thời gian trung bình ngắn nhất.
P7-R74-Q2|p7-detail|Thêm hai nhân viên chat từ trưa đến 3 giờ chiều; nhân sự điện thoại và email giữ nguyên.
P7-R74-Q3|p7-detail|Khách email vẫn không biết nhân viên đã bắt đầu xem thư hay chưa, dù thời gian trả lời đã cải thiện.
P7-R74-Q4|p7-detail|Nhóm đề nghị trạng thái under review hiển thị rõ trước khi tăng nhân viên email; giải pháp nhắm vào thiếu thông tin tiến độ.
P7-R75-Q1|p7-purpose|Email giải thích kết quả diễn tập lừa đảo và các workshop tiếp theo, không công bố kỷ luật cá nhân.
P7-R75-Q2|p7-detail|Kết quả phục vụ học tập ở cấp phòng ban; quản lý chỉ nhận tóm tắt chủ đề nên không có tên từng nhân viên.
P7-R75-Q3|p7-detail|Buổi đầu nhấn mạnh bấm nút báo cáo ngay khi thư có dấu hiệu lạ, không chờ hỏi đồng nghiệp trước.
P7-R75-Q4|p7-detail|Chỉ bảy phần trăm nhập thông tin; ba mươi tám phần trăm là tỷ lệ mở thư, cần phân biệt hai hành động.
""")

add("""
P7-R76-Q1|p7-detail|Chủ cửa hàng phản đối ban đầu vì khách dùng mười chỗ đỗ đó cho lượt ghé ngắn; thay thành khu giao hàng sẽ ảnh hưởng việc ghé mua.
P7-R76-Q2|p7-detail|Thành phố đồng ý cho xe cá nhân dùng sau 6 giờ chiều và công bố dữ liệu tuần, giúp hiệp hội chấp nhận thử nghiệm.
P7-R76-Q3|p7-inference|Support is temporary and depends on… xác định sự ủng hộ có thời hạn và phụ thuộc kết quả, không phải đồng ý vĩnh viễn.
P7-R76-Q4|p7-detail|Nếu ít cải thiện, hiệp hội sẽ yêu cầu khôi phục cách bố trí đỗ xe trước đây, không phải kéo dài thử nghiệm.
P7-R77-Q1|p7-detail|Risk summary phải nêu loại dữ liệu công ty mà dịch vụ xử lý và khả năng con người ghi đè đầu ra; doanh thu nhà cung cấp không được yêu cầu.
P7-R77-Q2|p7-purpose|Cho muốn xác định biểu mẫu tóm tắt rủi ro mới có áp dụng cho lần gia hạn của nhóm hay không.
P7-R77-Q3|p7-cross-reference|Nền tảng gia hạn ngày 28 tháng 8, trước chính sách bắt đầu ngày 1 tháng 9; điều này chưa tự xác nhận đã được phê duyệt.
P7-R78-Q1|p7-detail|Nhóm bền vững so energy use per kilometer giữa xe điện và xe diesel để đánh giá thử nghiệm.
P7-R78-Q2|p7-detail|Báo cáo loại hai xe dùng đào tạo lái, nên tổng 420 km thấp hơn 510 km trên bảng tuyến.
P7-R78-Q3|p7-cross-reference|Điện của xe đào tạo được tính nhưng quãng đường bị thiếu, có thể làm năng lượng mỗi km trông cao hơn và bất lợi cho xe điện.
P7-R79-Q1|p7-detail|Tax seminar ngày 14 tháng 8 là ngoại lệ streamed online only; các workshop tối khác chuyển tới Harbor Room.
P7-R79-Q2|p7-cross-reference|Đặt bàn 5–8 giờ chiều nhưng khu đóng lúc 6 giờ: còn 5–6 giờ, hai giờ bị cắt được hoàn phí.
P7-R79-Q3|p7-purpose|Wu muốn làm rõ cả phần đặt bàn còn lại lẫn nơi tham dự hội thảo thuế; email liên quan hai kế hoạch.
P7-R80-Q1|p7-detail|Chỉ chậm do sơ tán tòa nhà có chứng từ mới bị loại khỏi cách tính hiệu suất theo điều khoản được nêu.
P7-R80-Q2|p7-cross-reference|Loại năm chuyến sơ tán khỏi 250, giữ 237 đúng giờ: 237 chia 245 nhân 100 xấp xỉ 96,7 phần trăm.
P7-R80-Q3|p7-cross-reference|Tỷ lệ điều chỉnh khoảng 96,7 phần trăm vượt ngưỡng 96, nên hóa đơn toàn bộ phí phù hợp; 94,8 là tỷ lệ chưa loại ngoại lệ.
P7-R89-Q1|p7-inference|Nina nói tàu của kỹ thuật viên chậm và cô sẽ tới Fairview Station, cho thấy cô đang đi bằng tàu.
P7-R89-Q2|p7-vocabulary|That should still work đáp lại việc chỉ cần nối máy và kiểm tra mạng, hàm ý vẫn đủ thời gian chuẩn bị trước lượt khách 4 giờ.
P7-R89-Q3|p7-vocabulary|Cửa giao hàng đang khóa vì thi công giải thích vì sao phải dùng sảnh tây; không phải yêu cầu Omar mở khóa thiết bị.
P7-R90-Q1|p7-detail|Nhóm phi lợi nhuận địa phương đủ điều kiện dùng bảng miễn phí tối đa ba tuần; quảng cáo thương mại bị loại.
P7-R90-Q2|p7-detail|Có yêu cầu khổ A4, ngày trưng bày và duyệt trước; đoạn không yêu cầu chữ ký giám đốc nhóm.
P7-R90-Q3|p7-detail|Mang final printed notice tới lễ tân, tức bản in hoàn chỉnh; bản viết tay sẽ bị trả lại.
P7-R90-Q4|p7-insertion|Vị trí [2] nối câu có also vào danh sách yêu cầu của thông báo; sau đó mới chuyển sang trường hợp bị trả lại.
P7-R91-Q1|p7-vocabulary|Adjacent tones nói các sắc độ gần nhau để so màu; nghĩa phù hợp là nearby, không phải đắt hoặc phổ biến.
P7-R91-Q2|p7-detail|Màu màn hình có thể lệch nên khách được khuyên đặt nhiều mẫu có sắc độ gần nhau để so trước khi chọn.
P7-R91-Q3|p7-cross-reference|Đơn ghi express shipping; trang sản phẩm quy định express tới trong hai ngày làm việc, nên đối chiếu hai tài liệu để chọn.
P7-R91-Q4|p7-detail|Ortiz yêu cầu Harbor Blue và nói I like that shade, xác định màu thích là xanh Harbor, dù nhận nhầm Fog Gray.
P7-R91-Q5|p7-detail|Nhãn ghi Harbor Blue nhưng ba hộp bên trong là Fog Gray; vấn đề là giao sai màu tấm.
P7-R92-Q1|p7-detail|Portfolio trực tuyến dùng để so giọng, phong cách nói và giọng vùng, nên khách vào nghe mẫu giọng.
P7-R92-Q2|p7-cross-reference|Raman thấy listing trên Westside Business Newsletter, cho thấy studio quảng cáo trong ấn phẩm kinh doanh địa phương.
P7-R92-Q3|p7-inference|Dòng From ghi Director, Harbor Health Clinic; Raman là người quản lý phòng khám, không phải diễn viên lồng tiếng.
P7-R92-Q4|p7-detail|Cô có kịch bản đã chốt và chỉ cần ghi âm, nên không yêu cầu chỉnh sửa kịch bản; vẫn cần giọng chuyên nghiệp song ngữ.
P7-R92-Q5|p7-cross-reference|Studio hẹn phản hồi yêu cầu trong một ngày làm việc; Raman sẽ được đại diện liên hệ, chưa có cam kết giao bản ghi cuối ngay.
P7-R98-Q1|p7-cross-reference|L18 tới 8 giờ 50 nhưng đóng check-in 8 giờ 40, nên tàu ban đầu tới quá muộn.
P7-R98-Q2|p7-cross-reference|Earlier express phù hợp E12 đi 7 giờ 10, tới 8 giờ 05; E20 tới 9 giờ 10 không kịp check-in.
P7-R98-Q3|p7-detail|Hart sẽ gặp trợ lý gần Glendale ticket gates, tức cửa soát vé tại ga đến, không phải ở ga Eastport.
P7-R98-Q4|p7-cross-reference|Hart đổi sang E12; hàng E12 trong bảng ghi Platform 3 là sân ga khởi hành.
P7-R99-Q1|p7-cross-reference|Gián đoạn xác nhận kéo dài 2 giờ 18 phút vượt hai giờ; theo chính sách được giảm 10 phần trăm tổng dịch vụ, tức 34 đô la.
P7-R99-Q2|p7-detail|Bốn chỗ người dùng thêm có tổng giá 60 đô la; 60 chia 4 bằng 15 đô la mỗi chỗ.
P7-R99-Q3|p7-detail|No action is required nghĩa là giảm phí tự áp dụng. Chỉ liên hệ nếu khoản giảm không xuất hiện trên hóa đơn.
P7-R99-Q4|p7-detail|Trước giảm là service subtotal 340 đô la; sau trừ 34 còn 306, cần phân biệt tổng trước và sau giảm.
P7-R100-Q1|p7-detail|Tỷ lệ tự xử lý tăng liên tục 82, 85, 88, 90 phần trăm. Thời gian phản hồi không giảm liên tục vì tăng ở Q4.
P7-R100-Q2|p7-detail|Phản hồi đầu tăng từ 4,6 giờ ở Q3 lên 4,9 giờ ở Q4, tức chậm hơn dù tỷ lệ tự phục vụ tăng.
P7-R100-Q3|p7-detail|Ghi chú nêu holiday product launch gây tăng tổng yêu cầu quý bốn. Không suy từ đó rằng số ca đến nhân viên chắc chắn tăng.
P7-R100-Q4|p7-detail|Ghi chú hẹn thêm hai nhân viên trong các tuần phát hành, cùng sửa hướng dẫn; trung tâm kiến thức vẫn hoạt động.
""")

add("""
P7-R101-Q1|p7-cross-reference|Khách duyệt sáu Stand S nhưng phiếu đóng có một Stand E, trong khi thay thế phải xin phép; đây là món thay chưa được duyệt.
P7-R101-Q2|p7-detail|Khách yêu cầu all six displays must match, nên cần cùng mẫu trước khi lắp thứ hai.
P7-R101-Q3|p7-cross-reference|Quy định bắt buộc customer approval trước gửi món thay; đối chiếu email cho thấy khách chỉ chấp thuận mẫu S.
P7-R101-Q4|p7-inference|Nhà cung cấp cần xác nhận có thêm Stand S đúng mẫu tới kịp thứ hai không; lịch nhập Stand P không giải quyết yêu cầu này.
P7-R102-Q1|p7-detail|Leo nói xác nhận đầu tiên ghi Customer Journey Lab; anh đang ở danh sách chờ buổi trình diễn.
P7-R102-Q2|p7-detail|Mina chuyển đăng ký sang Automation Demonstration khi có chỗ và gửi xác nhận mới, không gia hạn hạn đăng ký chung.
P7-R102-Q3|p7-cross-reference|Buổi trình diễn bắt đầu 11 giờ 30; Mina yêu cầu sớm mười phút, nên cần tới Hall A lúc 11 giờ 20.
P7-R102-Q4|p7-detail|Unclaimed seats will be released nghĩa là ghế chưa có người nhận có thể nhường cho người khác, nên cần tới sớm.
P7-R103-Q1|p7-cross-reference|Bữa tối khai 52 đô la nhưng giới hạn ăn uống 45 đô la mỗi ngày; khoản được hoàn là 45 theo yêu cầu quản lý.
P7-R103-Q2|p7-detail|Taxi 38 đô la có hóa đơn đầy đủ, nên giữ nguyên trên yêu cầu chi phí công tác.
P7-R103-Q3|p7-detail|Ghi chú yêu cầu chuyển phí chép lời sang project A17; thuê bao phần mềm không thuộc tài khoản công tác.
P7-R103-Q4|p7-cross-reference|Tổng công tác sửa còn 45 đô la ăn tối cộng 38 đô la taxi bằng 83. Phí thuê bao 29 chuyển riêng sang dự án.
P7-R35-Q5|p7-detail|Tài xế phải check in ở access desk và xuất trình giấy tờ trước vào khu bốc dỡ; không được tự dỡ ở khu chờ công cộng.
P7-R35-Q6|p7-inference|Bàn mở lúc 8 giờ 15 nên tài xế tới 8 giờ 20 có thể check-in trước suất 8 giờ 30; điều đó không cho phép xe vào cổng ngoài suất.
P7-R36-Q5|p7-detail|Vé tháng cần gia hạn trước ngày 28 tháng 8 để còn hiệu lực khi chương trình bắt đầu; không cần đổi thẻ vật lý.
P7-R36-Q6|p7-detail|Airport express và tàu ghế đặt trước không được bao gồm; lựa chọn airport express khớp ngoại lệ được nêu.
P7-R43-Q6|p7-detail|Duyệt sửa trong bảy ngày theo lịch thì phí kiểm tra 45 đô la được cấn vào hóa đơn cuối; không phải bảy ngày làm việc.
P7-R43-Q7|p7-detail|Cảm biến chưa có sẵn, dự kiến ba ngày làm việc mới tới; sửa chỉ bắt đầu sau cả phê duyệt và nhận linh kiện.
P7-R46-Q5|p7-detail|Workshop chiều yêu cầu đã học nền tảng hoặc đào tạo tương đương, nên người có kinh nghiệm đào tạo tương đương được đăng ký.
P7-R46-Q6|p7-detail|Người tham gia mang laptop công ty đã cài bản phần mềm phân tích hiện hành, nên cần chuẩn bị cài đặt trước.
P7-R48-Q6|p7-detail|Hàng tiêu chuẩn chưa mở, giao mười ngày trước còn trong hạn mười bốn ngày; đồ đặt in riêng và nội thất đã lắp chỉ ngoại lệ khi hư lúc nhận.
P7-R48-Q7|p7-detail|Trước gửi trả, khách xin return authorization number qua cổng doanh nghiệp; kiểm tra kho diễn ra sau khi hàng về.
""")
