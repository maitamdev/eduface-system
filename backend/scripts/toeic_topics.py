"""DHV-authored Vietnamese strategy guides; examples are original study material."""
TOPICS = []


def topic(tid, part, title, cue, rules, steps, traps, example, explanation):
    TOPICS.append({"id": tid, "part": part, "title": title, "recognition": cue,
        "rules": rules.split("|"), "steps": steps.split("|"), "traps": traps.split("|"),
        "example": {"text": example, "explanation": explanation},
        "source_ids": ["format", "ets"] if part != 5 else ["bc-reference", "bc-b1"]})


topic("p1-actions", 1, "Người và hành động đang diễn ra",
 "Hình có một hoặc nhiều người: nghe chủ thể, động tác và vật chịu tác động.",
 "S + be + V-ing mô tả hành động đang diễn ra; chú ý bàn tay, tư thế và hướng nhìn.|Phân biệt wearing (đang mặc sẵn) và putting on (đang đưa đồ lên người), holding và handing.|Câu đúng chỉ cần mô tả một chi tiết nhìn thấy; không cần kể toàn bộ hình.",
 "Quan sát người và đồ vật trong vài giây.|Dự đoán 2–3 động từ có thể mô tả.|Nghe đủ từng câu rồi đối chiếu cả chủ thể lẫn động tác.",
 "Một danh từ trùng hình không cứu được động từ sai.|Không suy ra nghề nghiệp, mục đích hoặc cuộc hẹn từ trang phục.",
 "A worker is fastening a strap around a carton.", "Cần thấy người đang siết dây quanh thùng; a worker is opening a carton sai nếu không có thao tác mở.")
topic("p1-scene", 1, "Đồ vật, trạng thái và vị trí",
 "Hình ít người hoặc không có người: đồ đạc, đường phố, khu vực làm việc.",
 "Be + V3 có thể mô tả trạng thái kết quả: chairs are arranged; be being + V3 nhấn mạnh hành động đang được thực hiện.|There is/are xác nhận sự hiện diện; không tự thêm người đang thao tác.|Beside, beneath, along, across và facing phải khớp quan hệ giữa các vật.",
 "Xác định vật nổi bật và số lượng.|Phân biệt trạng thái đứng yên với hành động đang diễn ra.|Kiểm tra vị trí và vật nhỏ trong câu mô tả.",
 "Being installed không đúng chỉ vì thiết bị đã có ở đó.|Facing the screen khác behind the screen.",
 "Several chairs have been placed beneath the awning.", "Câu mô tả vị trí và kết quả sắp xếp; không yêu cầu nhìn thấy người đang đặt ghế.")
topic("p2-wh", 2, "Who / Where / When / What / How / Why",
 "Từ hỏi báo trước loại thông tin cần nghe, nhưng câu trả lời có thể gián tiếp.",
 "Who hỏi người; where hỏi nơi; when hỏi thời điểm. How long hỏi thời lượng, how often hỏi tần suất.|Why có thể được đáp bằng mục đích to + V hoặc nguyên nhân, không bắt buộc because.|What time và which floor phải được nghe như cả cụm; đừng chỉ bắt từ đầu.",
 "Giữ lại từ hỏi và động từ chính.|Dự đoán loại thông tin.|Chọn câu đáp hợp tình huống, kể cả lời chỉ dẫn nơi tìm thông tin.",
 "Âm giống không phải nghĩa giống: floor/four.|Câu đáp đúng ngữ pháp nhưng trả lời một câu hỏi khác vẫn sai.",
 "When will the revised roster be available? — Check the noticeboard after lunch.", "Lời đáp chỉ thời điểm xem được lịch; không cần lặp will hoặc available.")
topic("p2-yesno", 2, "Yes/No, câu phủ định và câu hỏi đuôi",
 "Do/Does/Did, Have/Has, Is/Are, Won't… hoặc một mệnh đề kèm isn't it / didn't you.",
 "Trả lời theo sự việc thực tế; không chọn máy móc Yes cho câu khẳng định hay No cho câu phủ định.|Câu hỏi đuôi thường xin xác nhận; lời đáp có thể sửa thông tin thay vì nói yes/no.|Have you finished? hỏi kết quả đến hiện tại; Did you finish yesterday? gắn mốc quá khứ.",
 "Xác định việc đang được xác nhận.|Nghe động từ, chủ thể và mốc thời gian.|Kiểm tra lời đáp xác nhận, bác bỏ hay giải thích việc chưa làm.",
 "Yes, it does không phù hợp câu hỏi người đã làm việc gì.|Đáp lại bằng một chi tiết hợp lý có thể đúng hơn yes/no máy móc.",
 "You haven't sent the invoice yet, have you? — I'm waiting for the purchase number.", "Người đáp giải thích vì sao chưa gửi; đây là câu đáp gián tiếp phù hợp.")
topic("p2-choice", 2, "Câu hỏi lựa chọn A or B",
 "Người nói đưa ra hai phương án về thời gian, địa điểm hoặc hành động.",
 "Có thể chọn A, chọn B, cả hai, không cái nào hoặc nêu phương án khác nếu phù hợp.|Either works nghĩa là phương án nào cũng được; neither phủ định cả hai.|Or ở giữa hai danh từ không tự biến mọi câu thành câu hỏi lựa chọn; cần hiểu toàn câu.",
 "Nhớ hai lựa chọn.|Nghe người đáp đang chọn, từ chối hay chuyển quyền quyết định.|Kiểm tra câu đáp có giải quyết lựa chọn đang đặt ra không.",
 "Yes không thường đủ để trả lời A hay B.|Lựa chọn lặp lại một từ nghe được nhưng đổi đối tượng là bẫy.",
 "Should we print the agenda or send a link? — Let's save paper this time.", "Save paper hàm ý gửi đường dẫn; phải suy ra từ hai lựa chọn có sẵn.")
topic("p2-request", 2, "Yêu cầu, đề nghị và lời mời",
 "Could you…, Would you mind…, Why don't we…, Let's… hoặc Would you like…",
 "Could you thường là nhờ làm việc, không chỉ hỏi khả năng.|Would you mind + V-ing là lời nhờ lịch sự; Not at all thường thể hiện đồng ý.|Why don't we đề xuất một hành động; lời đáp nên chấp nhận, từ chối hoặc đưa phương án khác.",
 "Nhận diện chức năng giao tiếp.|Xác định ai cần làm việc gì.|Chọn lời đáp lịch sự và phù hợp điều kiện của người nói.",
 "Why don't we không luôn yêu cầu nêu nguyên nhân.|No có thể đồng ý với Would you mind, tùy phần giải thích sau đó.",
 "Could you cover the reception desk at noon? — I can, once my call ends.", "Người đáp nhận hỗ trợ nhưng có điều kiện về thời gian; không phải từ chối hoàn toàn.")
topic("p2-indirect", 2, "Phản hồi gián tiếp và câu phát biểu",
 "Lời đầu là thông báo, phàn nàn hoặc câu hỏi mà người đáp không trả lời thẳng.",
 "Một thông báo có thể được đáp bằng hành động khắc phục, lời cảm ơn hoặc câu hỏi tiếp.|I thought… có thể sửa một giả định; you'll have to ask… chuyển đến người biết thông tin.|Chỉ suy luận một bước từ ngữ cảnh; không tự dựng một câu chuyện ngoài lời nói.",
 "Xác định nhu cầu ẩn sau câu đầu.|Tìm phản hồi giúp tiếp tục cuộc trao đổi.|Loại đáp án chỉ liên quan từ vựng nhưng không có quan hệ giao tiếp.",
 "Lặp từ trong câu hỏi là bẫy phổ biến.|Không loại câu hỏi ngược chỉ vì nó không phải câu trần thuật.",
 "The projector won't start. — Is the power cable connected?", "Câu hỏi ngược đề xuất kiểm tra nguyên nhân, nên đáp lại vấn đề hợp lý.")
topic("p3-overview", 3, "Hội thoại: chủ đề, địa điểm và vai trò",
 "What are the speakers discussing? Where are they? Who most likely is the woman?",
 "Chủ đề thường được xác lập sớm rồi triển khai thành vấn đề và giải pháp.|Vai trò phải dựa vào việc người đó làm hoặc cung cấp, không chỉ một danh từ nghề nghiệp.|Kết hợp hai dấu hiệu địa điểm nếu có: prescription + pharmacist mạnh hơn từ counter đơn lẻ.",
 "Đọc nhanh ba câu hỏi trước khi nghe.|Ghi mối quan hệ người nói và vấn đề chính.|Đối chiếu câu trả lời ở mức khái quát vừa đủ.",
 "Chi tiết phụ ở cuối không nhất thiết là chủ đề.|Một người nhắc đến nhà hàng chưa có nghĩa đang ở nhà hàng.",
 "The replacement lenses arrived. Could you come in for a fitting tomorrow?", "Replacement lenses và fitting gợi dịch vụ kính; người gọi đang sắp lịch thử kính.")
topic("p3-detail", 3, "Hội thoại: chi tiết, nguyên nhân và thay đổi",
 "Hỏi giờ, giá, tên, vật dụng, lý do hoặc điều gì đã thay đổi.",
 "Đáp án thường diễn đạt lại thông tin: out of stock → unavailable.|Thông tin sửa sau but, actually, instead có thể thay thế kế hoạch ban đầu.|Lưu mối liên hệ giữa con số và đối tượng: giá cũ, giá mới, ngày đặt và ngày nhận.",
 "Xác định loại chi tiết cần nghe.|Ghi từ khóa thay cho cả câu.|Kiểm tra lần nhắc cuối cùng áp dụng cho đối tượng nào.",
 "Con số nghe rõ nhất chưa chắc được hỏi.|Đừng áp dụng một thay đổi cho cả những điều người nói không sửa.",
 "We originally booked Tuesday, but the engineer can only come on Thursday.", "Lịch thực hiện đã chuyển sang Thursday; Tuesday là phương án ban đầu.")
topic("p3-next", 3, "Hội thoại: hành động tiếp theo",
 "What will the man do next? What is the woman asked to do?",
 "Phân biệt việc đã làm, đang làm, dự định và được nhờ làm.|I'll, let me, please và could you thường đánh dấu việc tiếp theo; kiểm tra đúng người.|Nếu hành động có điều kiện, giữ điều kiện đó trong cách diễn đạt của đáp án.",
 "Xác định người được hỏi.|Theo dõi lời chốt nhiệm vụ.|Loại hoạt động đã hoàn tất trước cuộc gọi.",
 "Đáp án mô tả việc của người còn lại.|Cần làm sau khi được duyệt không đồng nghĩa sẽ làm ngay.",
 "I'll reserve the room once you confirm the guest count.", "Người nói sẽ đặt phòng sau khi người kia xác nhận số khách, không phải tự đếm khách.")
topic("p3-intent", 3, "Hội thoại: hàm ý và mục đích câu nói",
 "What does the speaker mean when saying…? Why does the speaker say…?",
 "Ý định cần được giải thích bằng câu trước và câu sau đoạn trích.|Một lời nhận xét có thể là yêu cầu gián tiếp hoặc thể hiện sự do dự.|Mức độ chắc chắn phải giữ nguyên: might không đồng nghĩa definitely.",
 "Xác định vấn đề ngay trước lời nói.|Nghe phản hồi và hành động sau đó.|Chọn chức năng giao tiếp, không chỉ nghĩa từ điển.",
 "Diễn giải quá mạnh một lời gợi ý.|Chọn câu đúng nghĩa đen nhưng không giải thích vì sao nói lúc đó.",
 "The shipment can arrive Friday. — That gives us some breathing room.", "Lời đáp thể hiện có thêm thời gian chuẩn bị, không nói về không khí hay phòng ốc.")
topic("p3-graphic", 3, "Hội thoại kết hợp bảng hoặc lịch",
 "Look at the graphic: cần nối dữ kiện nghe với một hàng trong bảng.",
 "Bảng cung cấp dữ kiện tĩnh; audio thường cho điều kiện để xác định hàng đúng.|Đọc tên cột, đơn vị và chú thích trước; chỉ nhìn số mà quên đơn vị dễ chọn sai.|Nếu audio thông báo điều chỉnh, áp dụng đúng mục bị thay đổi rồi tìm kết quả trong bảng.",
 "Đọc câu hỏi và tên cột.|Nghe điều kiện lọc: sức chứa, giờ, giá hoặc loại vé.|Đối chiếu từng điều kiện rồi chọn đúng ô.",
 "Chọn hàng có một điều kiện đúng nhưng điều kiện khác sai.|Tính tổng trước khi xác định giá là theo người hay theo nhóm.",
 "Room Cedar: 20 seats; Room Elm: 35 seats. Audio: We need space for 28 guests.", "Cedar không đủ chỗ; Elm phù hợp nếu không có điều kiện khác trong audio.")
topic("p4-purpose", 4, "Bài nói: mục đích, người nghe và bối cảnh",
 "Thông báo, voicemail, quảng cáo, giới thiệu hoặc hướng dẫn công việc.",
 "Phần mở đầu thường cho biết người nói và mục đích; phần cuối nêu hành động cần làm.|Phân biệt quảng cáo một dịch vụ với thông báo thay đổi dịch vụ đã đặt.|Đối tượng nghe được xác định bằng nghĩa vụ/quyền lợi của họ trong bài.",
 "Nhận dạng loại bài nói.|Tóm tắt bằng một động từ: announce, explain, invite, apologize.|Kiểm tra đáp án có bao quát toàn bài không.",
 "Một sản phẩm được nhắc đến không tự biến bài thành quảng cáo.|Chọn một chi tiết kỹ thuật làm mục đích chung.",
 "This message concerns the new entrance procedure for contractors.", "Mục đích là giải thích quy trình vào tòa nhà cho nhà thầu, không phải tuyển nhà thầu.")
topic("p4-detail", 4, "Bài nói: điều kiện và thông tin cụ thể",
 "Hỏi thời hạn, vị trí, ưu đãi, nguyên nhân hay ngoại lệ.",
 "Only, except, unless và at least giới hạn phạm vi của thông tin.|Đáp án đúng giữ cả thông tin chính lẫn điều kiện áp dụng.|Một danh sách có thể chứa các nhóm khác nhau; ghép đúng đối tượng với quyền lợi.",
 "Khoanh loại dữ kiện được hỏi.|Nghe cụm hạn chế ngay trước hoặc sau số liệu.|So lại đáp án xem có bỏ mất điều kiện không.",
 "Miễn phí cho thành viên không phải miễn phí cho mọi người.|By Friday và on Friday khác nhau.",
 "Express delivery is free for orders above eighty dollars, excluding furniture.", "Đơn vượt 80 đô la vẫn không được ưu đãi này nếu là đồ nội thất.")
topic("p4-action", 4, "Bài nói: yêu cầu và bước tiếp theo",
 "What should listeners do? What will happen next?",
 "Hướng dẫn thường có thứ tự: đăng ký, nhận xác nhận, rồi đến địa điểm.|Please, remember to, be sure to và contact… nêu hành động cụ thể.|Phân biệt việc người nghe phải làm với việc ban tổ chức sẽ làm.",
 "Tìm chủ thể của hành động.|Ghi bước bắt buộc và hạn chót.|Ưu tiên lời hướng dẫn trực tiếp ở cuối bài.",
 "Đến nơi trước khi xác nhận dù audio yêu cầu xác nhận trước.|Đọc một hành động tùy chọn thành bắt buộc.",
 "To change your delivery slot, reply to this message before four.", "Người muốn đổi lịch phải trả lời tin nhắn trước 4 giờ; không áp dụng cho người giữ lịch cũ.")
topic("p4-graphic", 4, "Bài nói kết hợp bảng giá và lịch trình",
 "Một bài nói cung cấp điều kiện cần nối với thông tin trực quan.",
 "Bảng có thể chứa giá cơ bản, phụ phí hoặc khung giờ, cần đọc đúng tiêu đề.|Khi audio nói dịch vụ được thay thế, xác định dòng mới thay vì dùng lịch cũ.|Tính toán chỉ ở mức cần thiết; TOEIC chủ yếu kiểm tra hiểu thông tin tiếng Anh.",
 "Quét bảng và câu hỏi trước.|Ghi điều kiện từ audio.|Dùng đúng hàng/cột và kiểm tra đơn vị.",
 "Nhầm giờ đến với giờ khởi hành.|Cộng phí đã bao gồm trong giá.",
 "Shuttle: 08:00 North / 08:20 West. Audio: West passengers should use the later bus.", "Tìm giờ 08:20 tương ứng tuyến West; không chọn chuyến đầu chỉ vì được đọc trước.")

topic("p5-word-form", 5, "Từ loại và vị trí trong câu",
 "Các lựa chọn chung gốc: efficient / efficiently / efficiency / efficiencies.",
 "Xác định ô trống cần danh từ, động từ, tính từ hay trạng từ từ cấu trúc xung quanh.|A/an/the + (tính từ) + danh từ; trạng từ có thể đứng giữa trợ động từ và phân từ.|Sau động từ nối như seem/remain/become thường là tính từ, không tự động chọn trạng từ sau mọi động từ.",
 "Đọc cả cụm chứa chỗ trống.|Tìm từ mà chỗ trống bổ nghĩa.|Chọn từ loại rồi kiểm tra nghĩa và số ít/số nhiều.",
 "Đuôi -ly không phải lúc nào cũng là trạng từ: friendly là tính từ.|Từ đứng sát danh từ chưa chắc là tính từ nếu giữa chúng có giới từ.",
 "The technician checked the connection carefully.", "Carefully bổ nghĩa hành động checked; careful cần bổ nghĩa một danh từ hoặc đứng sau động từ nối.")
topic("p5-tense", 5, "Thì và mốc thời gian",
 "Các lựa chọn là những dạng chia khác nhau của cùng động từ.",
 "Past simple thường gắn mốc quá khứ kết thúc; present perfect nối quá khứ với hiện tại.|Past perfect nêu hành động xảy ra trước một mốc quá khứ khác, không dùng chỉ vì thấy before.|By the time + mốc tương lai có thể đi với future perfect nếu hành động đã hoàn tất trước mốc đó.",
 "Tìm mốc và trình tự sự kiện.|Xác định hành động còn liên quan hiện tại không.|Kiểm tra hòa hợp chủ ngữ sau khi chọn thì.",
 "Since có thể là liên từ chỉ lý do trong ngữ cảnh khác.|Tomorrow không bắt buộc will: lịch trình có thể dùng hiện tại đơn.",
 "By the time the courier arrived, we had sealed the boxes.", "Việc niêm phong đã xong trước khi người giao hàng đến: had sealed.")
topic("p5-agreement", 5, "Hòa hợp chủ ngữ – động từ",
 "Bẫy danh từ số nhiều trong cụm giới từ hoặc chủ ngữ nối either/neither.",
 "Động từ hòa hợp với danh từ trung tâm của chủ ngữ, không phải danh từ gần nhất bất kỳ.|Each/every + danh từ số ít thường dùng động từ số ít; a number of + số nhiều dùng số nhiều.|Với either…or / neither…nor, kiểm tra danh từ gần động từ và quy tắc ngữ cảnh sử dụng.",
 "Gạch bỏ cụm bổ nghĩa xen giữa.|Xác định chủ ngữ trung tâm.|Đối chiếu số và thì của từng phương án.",
 "The number of khác a number of.|Together with không có vai trò như and trong việc tạo chủ ngữ ghép.",
 "The list of replacement parts is on the desk.", "List là chủ ngữ số ít; of replacement parts chỉ bổ nghĩa nên dùng is.")
topic("p5-passive", 5, "Chủ động và bị động",
 "Chủ ngữ nhận hành động: invoices, applications, equipment, requests.",
 "Bị động thường là be + past participle; modal + be + V3; have/has been + V3.|Giữ thì ở trợ động từ, không đổi phân từ sang động từ nguyên mẫu.|Không phải động từ nào cũng có tân ngữ để chuyển bị động: arrive/happen thường không dùng bị động.",
 "Hỏi chủ ngữ làm hay nhận hành động.|Tìm dấu hiệu thì hoặc modal.|Kiểm tra động từ có thể mang nghĩa bị động không.",
 "By Friday là thời hạn, không phải tác nhân.|Be interested là mô tả trạng thái, cần hiểu nghĩa thay vì gán mọi V3 là hành động bị động.",
 "All applications must be reviewed before Friday.", "Applications nhận hành động xét duyệt; modal must cần be reviewed.")
topic("p5-pronouns", 5, "Đại từ và sở hữu",
 "I/me/my/mine, they/them/their/theirs, hoặc đại từ phản thân.",
 "Đại từ chủ ngữ đứng làm chủ thể; đại từ tân ngữ sau động từ/giới từ.|Tính từ sở hữu cần danh từ theo sau; đại từ sở hữu có thể thay cả cụm danh từ.|Đại từ phản thân dùng khi tân ngữ cùng người với chủ ngữ hoặc để nhấn mạnh, không thay thế mọi tân ngữ.",
 "Xác định chức năng chỗ trống.|Tìm danh từ đi kèm nếu có.|Kiểm tra đại từ tham chiếu đúng người và số.",
 "Its là sở hữu, it's = it is/has.|Their và theirs không dùng cùng vị trí.",
 "Please send the revised estimate to her, not to me.", "Sau giới từ to cần đại từ tân ngữ her/me; không dùng she/I.")
topic("p5-preposition", 5, "Giới từ và cụm cố định",
 "Giới từ chỉ thời gian, vị trí hoặc theo sau một tính từ/động từ.",
 "By nêu hạn cuối, until nêu trạng thái kéo dài đến một mốc, within nêu khoảng giới hạn.|Giới từ đi với danh từ hoặc V-ing; to có thể là giới từ trong look forward to.|Học cả cụm: responsible for, interested in, comply with, on behalf of.",
 "Phân biệt giới từ nghĩa tự do và cụm cố định.|Đọc thành phần ngay sau chỗ trống.|Kiểm tra quan hệ thời gian hoặc nghĩa của cả cụm.",
 "During + danh từ; while + mệnh đề trong cách dùng thông thường.|Không chọn to chỉ vì thấy dạng nguyên mẫu trong các cụm giới từ.",
 "Please keep the receipt until the warranty expires.", "Keep diễn tả duy trì việc giữ; until xác định thời điểm kết thúc.")
topic("p5-conjunction", 5, "Liên từ và quan hệ logic",
 "Because/because of; although/despite; unless/if; however/therefore.",
 "Because/although + mệnh đề; because of/despite + cụm danh từ hoặc V-ing.|Unless diễn tả ngoại lệ/điều kiện phủ định, không thay if trong mọi câu.|However và therefore là trạng từ liên kết; xem dấu câu để tránh nối hai mệnh đề độc lập bằng dấu phẩy sai.",
 "Xác định sau chỗ trống là cụm hay mệnh đề.|Tìm quan hệ nguyên nhân, tương phản, điều kiện hoặc mục đích.|Đọc lại câu với nghĩa đã chọn.",
 "Although và despite giống quan hệ nghĩa nhưng khác cấu trúc.|Even if là điều kiện giả định, even though là nhượng bộ về điều được nêu là thực.",
 "Although the delivery was late, the client accepted the shipment.", "Sau Although là mệnh đề có chủ ngữ và động từ; despite không đứng trực tiếp trước cấu trúc này.")
topic("p5-relative", 5, "Mệnh đề quan hệ và rút gọn",
 "Who/whom/whose/which/that, hoặc V-ing/V3 ngay sau danh từ.",
 "Who thường chỉ người, which chỉ vật; whose thể hiện sở hữu và đi với danh từ.|Xem đại từ đóng vai chủ ngữ hay tân ngữ trong mệnh đề phụ trước khi chọn.|Rút gọn chủ động thường dùng V-ing; bị động dùng V3, nhưng chỉ khi cấu trúc và nghĩa cho phép.",
 "Tìm danh từ được bổ nghĩa.|Xác định mệnh đề đang thiếu thành phần gì.|Kiểm tra chủ động/bị động và dấu phẩy.",
 "Không dùng that sau giới từ đặt ngay trước đại từ quan hệ.|V3 sau danh từ không tự là thì quá khứ của mệnh đề chính.",
 "The documents attached to the message contain the revised prices.", "Attached rút gọn which are attached; contain mới là động từ chính.")
topic("p5-quantity", 5, "Từ chỉ lượng và danh từ đếm được",
 "Much/many, fewer/less, few/little, each/every và lượng thông tin.",
 "Many/few/fewer đi với danh từ đếm được số nhiều; much/little/less thường đi với không đếm được.|A few/a little thường mang ý có một lượng; few/little thường nhấn mạnh không nhiều hoặc chưa đủ.|Information, equipment, advice thường không đếm được; dùng piece/item để diễn tả đơn vị.",
 "Xác định danh từ đếm được không.|Kiểm tra số ít/số nhiều.|Đọc sắc thái đủ/thiếu và so sánh.",
 "Không thêm -s vào equipment trong cách dùng thông thường.|Each dùng với danh từ số ít nhưng each of đi với cụm số nhiều, động từ chính thường số ít.",
 "We need a little more information before approving the request.", "Information không đếm được nên dùng a little; many không phù hợp.")
topic("p5-infinitive", 5, "To V, V-ing và dạng nguyên mẫu",
 "Sau động từ, giới từ, tính từ hoặc động từ khuyết thiếu.",
 "Modal + V nguyên mẫu; agree/plan/decide + to V; avoid/consider + V-ing.|Sau giới từ thường dùng V-ing; phân biệt to giới từ với to của nguyên mẫu.|Một số động từ thay đổi nghĩa theo dạng theo sau: stop doing và stop to do.",
 "Xác định từ chi phối chỗ trống.|Đối chiếu mẫu bổ ngữ của từ đó.|Kiểm tra nghĩa của hai hành động.",
 "Can to submit sai: modal không cần to.|Be used to doing khác used to do.",
 "The team postponed installing the update until Friday.", "Postpone nhận V-ing; installing là hoạt động bị hoãn.")
topic("p5-comparison", 5, "So sánh, mức độ và song song",
 "Than, as…as, the most…, hoặc hai cấu trúc cần tương ứng.",
 "So sánh hơn thường có -er/more và than; không dùng more với một dạng đã có -er.|As + tính từ/trạng từ gốc + as; chọn tính từ hay trạng từ theo chức năng.|Much/far/considerably có thể bổ nghĩa so sánh hơn; very thường không dùng trực tiếp trước better.",
 "Tìm đối tượng được so sánh.|Xác định khung cấu trúc.|Kiểm tra từ loại và sự song song.",
 "Most efficient và more efficient có phạm vi so sánh khác nhau.|So sánh phải cùng loại đối tượng: costs với costs, không costs với company.",
 "The new process runs considerably faster than the old one.", "Considerably bổ nghĩa faster; faster bổ nghĩa runs.")
topic("p5-vocabulary", 5, "Từ vựng ngữ cảnh và collocation",
 "Các lựa chọn cùng từ loại, đều đúng ngữ pháp nhưng khác nghĩa.",
 "Khi cấu trúc không loại được đáp án, đọc cả câu để xác định mục đích và đối tượng.|Học kết hợp từ: meet a deadline, place an order, raise a concern, issue a refund.|Một từ nhiều nghĩa phải được hiểu theo ngành và tình huống, không theo nghĩa học đầu tiên.",
 "Xác nhận các lựa chọn cùng loại từ.|Xác định quan hệ nghĩa với danh từ/động từ bên cạnh.|Thử diễn đạt lại cả câu.",
 "Nghĩa gần nhau không đồng nghĩa mọi kết hợp đều tự nhiên.|Không dựa riêng vào một bản dịch tiếng Việt chung.",
 "The manager raised a concern about the revised schedule.", "Raise a concern là nêu quan ngại; rise là nội động từ nên không dùng với tân ngữ a concern.")
topic("p5-advanced", 5, "Điều kiện, đảo ngữ và giả định",
 "Had/Were/Should đứng đầu, not only, hoặc recommend that…",
 "Had + S + V3 có thể thay if + past perfect trong điều kiện không thực ở quá khứ.|Sau recommend/require/insist that, dạng giả định thường dùng động từ nguyên mẫu theo nghĩa yêu cầu.|Cụm mở đầu phủ định như Not until/Only after có thể yêu cầu đảo trợ động từ ở mệnh đề chính.",
 "Xác định mẫu cấu trúc thay vì dịch từng từ.|Tách mệnh đề điều kiện khỏi kết quả.|Kiểm tra cả nghĩa thời gian và dạng động từ.",
 "Không đảo mệnh đề nằm trong cụm Only after; đảo mệnh đề chính.|Không dùng một công thức giả định cho mọi nghĩa của insist.",
 "The supervisor requested that each file be checked twice.", "Request mang nghĩa yêu cầu; be là dạng nguyên mẫu trong mệnh đề giả định, không đổi theo each file.")

topic("p6-grammar", 6, "Part 6: ngữ pháp trong đoạn văn",
 "Chỗ trống từ loại, thì, chủ động/bị động hoặc từ vựng trong email/thông báo.",
 "Dùng ngữ pháp câu gần chỗ trống nhưng kiểm tra thì và đối tượng trong cả đoạn.|Một câu trước có thể xác định sự việc đã diễn ra hay mới dự kiến.|Các chỗ trống cùng thuộc một văn bản; đáp án không được làm mâu thuẫn trình tự chung.",
 "Đọc người gửi, người nhận và mục đích.|Giải các khoảng trống đủ bằng chứng cục bộ.|Đọc lại cả đoạn sau khi điền.",
 "Không chọn thì chỉ từ một trạng từ khi đoạn đã xác lập mốc khác.|Đừng bỏ qua chủ thể của câu bị động.",
 "We inspected the units yesterday. Three items have been ____ for replacement. (selected/selecting)", "Have been selected là bị động: ba món đã được chọn, phù hợp hành động kiểm tra trước đó.")
topic("p6-linking", 6, "Part 6: từ nối và tham chiếu",
 "However/therefore/otherwise, this change, these items hoặc đại từ.",
 "Từ nối biểu thị quan hệ giữa hai ý, không chỉ giữa hai từ đứng sát nhau.|This/these/such cần một nội dung phù hợp đã được giới thiệu; kiểm tra số lượng và nghĩa.|Otherwise thường nêu hệ quả nếu điều kiện trước không được thực hiện.",
 "Tóm tắt hai câu bằng tiếng Việt ngắn.|Xác định quan hệ logic.|Thay từ nối vào và đọc mạch hoàn chỉnh.",
 "Một câu nối ngữ pháp đúng có thể đảo sai quan hệ nguyên nhân.|These không thể chỉ một danh từ số ít nếu không có ý tập hợp phù hợp.",
 "Return the badge before leaving. Otherwise, a replacement fee will be charged.", "Otherwise nối yêu cầu với hậu quả nếu không trả thẻ; không phải một ví dụ minh họa.")
topic("p6-insertion", 6, "Part 6: điền cả câu",
 "Các phương án là câu hoàn chỉnh cho một khoảng trống trong văn bản.",
 "Câu đúng cần nối được cả phía trước lẫn phía sau, cùng chủ đề chưa đủ.|Tìm chuỗi yêu cầu → điều kiện → hệ quả và đại từ chỉ ngược.|Không thêm một cam kết, khoản phí hoặc ngoại lệ mà phần còn lại phủ nhận.",
 "Đọc ít nhất một câu trước và sau.|Xác định khoảng trống đang thiếu chức năng gì.|Thử từng phương án và loại mâu thuẫn.",
 "Câu có cùng từ khóa nhưng làm đứt mạch.|Chọn chi tiết hợp lý ngoài đời dù đoạn không nói đến.",
 "The workshop is full. [____] These applicants will be contacted if a seat becomes available.", "Câu chèn cần giới thiệu người trong danh sách chờ để These applicants có đối tượng tham chiếu.")
topic("p7-purpose", 7, "Part 7: mục đích và ý chính",
 "Why was the email sent? What is the main purpose of the notice?",
 "Xác định hành động giao tiếp: thông báo, yêu cầu, xác nhận, quảng bá hay xin lỗi.|Tiêu đề là dấu hiệu nhưng thân bài và lời chốt quyết định mục đích.|Câu trả lời quá rộng hoặc chỉ nói một chi tiết phụ đều có thể sai.",
 "Đọc loại văn bản, người gửi và chủ đề.|Tóm tắt chức năng trong một câu.|Đối chiếu tất cả phương án.",
 "Một hóa đơn đính kèm không có nghĩa email chỉ yêu cầu trả tiền.|Không chọn một mục đích hợp ngành nhưng không xuất hiện trong bài.",
 "Your reservation is confirmed. Please review the attached arrival instructions.", "Mục đích chính là xác nhận đặt chỗ và cung cấp hướng dẫn, không phải quảng cáo giảm giá.")
topic("p7-detail", 7, "Part 7: chi tiết, NOT/EXCEPT và tham chiếu",
 "Hỏi ai, khi nào, ở đâu, điều kiện nào; hoặc thông tin không được nêu.",
 "Tìm bằng từ khóa nhưng so nghĩa toàn cụm, vì đáp án thường paraphrase.|NOT/EXCEPT yêu cầu đối chiếu cả bốn phương án; ba phương án được hỗ trợ không có nghĩa phương án cuối là điều trái ngược.|Theo dõi đại từ, đơn vị, hạn chót và phạm vi của only/all/some.",
 "Đọc kỹ từ phủ định trong câu hỏi.|Khoanh dòng bằng chứng.|Kiểm tra đối tượng và điều kiện của thông tin.",
 "Thông tin không được nêu khác với thông tin bị bài phủ định.|Tên hoặc ngày trùng chưa đủ nếu gắn với người/sự kiện khác.",
 "Members may borrow up to four devices for seven days.", "Giới hạn đồng thời có hai điều kiện: tối đa bốn thiết bị và thời hạn bảy ngày.")
topic("p7-inference", 7, "Part 7: suy luận và hành động dự kiến",
 "What is implied/suggested? What will most likely happen?",
 "Suy luận đúng là kết luận được bằng chứng hỗ trợ, không phải một khả năng tưởng tượng.|Phân biệt kế hoạch, yêu cầu và xác nhận đã thực hiện.|Mức độ chắc chắn của đáp án phải phù hợp với từ may, likely, confirmed trong văn bản.",
 "Chỉ ra ít nhất một bằng chứng cụ thể.|Nối dữ kiện bằng suy luận ngắn.|Loại phương án cần thêm giả định chưa được nói.",
 "Requested a refund không có nghĩa received a refund.|Most likely không cho phép chọn bất kỳ câu hợp lý ngoài đời.",
 "Please retain the original packaging until your inspection appointment.", "Người nhận sẽ cần bao bì ít nhất đến buổi kiểm tra; chưa có bằng chứng sản phẩm chắc chắn được hoàn tiền.")
topic("p7-vocabulary", 7, "Part 7: nghĩa từ và dụng ý trong ngữ cảnh",
 "Closest in meaning, hoặc tác giả muốn nói gì qua một câu trích.",
 "Chọn nghĩa giữ được ý của câu và mạch đoạn, không chỉ nghĩa phổ biến nhất.|Từ thay thế phải phù hợp chức năng ngữ pháp và collocation.|Với tin nhắn, đọc lượt trước/sau để hiểu lời đồng ý, từ chối hoặc sửa thông tin.",
 "Đọc toàn câu chứa từ.|Diễn đạt lại nghĩa theo ngữ cảnh.|Thử thay bằng từng phương án.",
 "Issue có thể là phát hành, vấn đề hoặc số tạp chí.|Một từ đồng nghĩa từ điển vẫn có thể sai sắc thái trong câu.",
 "We can accommodate the revised delivery window.", "Accommodate ở đây là đáp ứng/điều chỉnh cho phù hợp, không phải cung cấp phòng ở.")
topic("p7-cross-reference", 7, "Part 7: hai và ba văn bản",
 "Email + lịch, quảng cáo + đơn hàng, chính sách + hóa đơn + cập nhật.",
 "Gắn mỗi văn bản với chức năng và thời điểm: quy định, giao dịch, thay đổi cuối.|Một câu có thể cần hai nguồn bằng chứng; ghi rõ nguồn nào cung cấp điều kiện, nguồn nào cung cấp dữ kiện.|Thông tin mới chỉ thay thế phần nó sửa; các điều kiện cũ còn lại có thể vẫn áp dụng.",
 "Lập bản đồ văn bản trước khi đọc sâu.|Theo dõi cùng người/đơn hàng giữa các nguồn.|Đối chiếu điều kiện và mốc cập nhật trước khi tính hoặc suy luận.",
 "Cộng một khoản thay thế như thể là khoản bổ sung.|Áp ưu đãi trước hạn cho một đơn đặt sau hạn.",
 "Policy: orders placed by 12 May get free delivery. Email: order placed on 14 May.", "Đơn không đáp ứng thời hạn ưu đãi; việc giao sau hay trước ngày 12 không phải điều kiện được nêu.")
topic("p7-insertion", 7, "Part 7: chọn vị trí chèn câu",
 "Văn bản có vị trí [1]–[4]; chọn nơi một câu mới phù hợp nhất.",
 "Đại từ và từ chỉ ngược trong câu mới cần tiền đề rõ ràng.|Câu mới có thể giới thiệu một ý được giải thích ở câu sau, nên phải kiểm tra hai phía.|Mạch thường đi từ thông báo chung sang chi tiết, điều kiện và hành động.",
 "Đọc câu cần chèn và gạch từ tham chiếu.|Tìm vị trí có tiền đề phù hợp.|Đọc ba câu liên tiếp sau khi chèn.",
 "Chủ đề giống nhau chưa đủ nếu thời gian hoặc logic đứt đoạn.|Không đặt This alternative trước khi phương án thay thế được giới thiệu.",
 "The west entrance is closed. Guests should use the garden gate. [2] A temporary ramp has been installed there.", "Câu mô tả lợi ích của lối đi thay thế phù hợp sau garden gate và trước chi tiết ramp nếu tham chiếu nhất quán.")
