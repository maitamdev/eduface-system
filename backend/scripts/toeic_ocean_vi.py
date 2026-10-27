"""Vietnamese teaching explanations and reviewed topic labels for MIT adaptations.

Keys refer to the pinned upstream snapshot; no automatic translation service is
used at runtime. Rejected source questions remain documented, never published.
"""
EXCLUDED = {
    "P5-022": "Completing and Having completed allow defensible readings without a clearer time constraint.",
    "P5-066": "Different than and different from are both used; unsuitable as a one-answer item.",
    "P5-073": "Upstream key 'was it' creates a double subject before 'the building'.",
    "P5-076": "Both will complete and will have completed are possible with this deadline.",
    "P5-095": "No temporal evidence distinguishes verifies, verified, and will verify.",
    "P5-099": "Subscribed/subscribing both admit interpretations; the key is not uniquely justified.",
    "P2-018": "Tomorrow is a holiday is also a defensible indirect recommendation to call now.",
    "P2-056": "They were on the conference table can also imply that badges have been printed.",
    "P3-G10-Q1": "Incorrect temperature does not establish too warm rather than too cold; exclude the complete group.",
    "P3-G10-Q2": "Context group excluded with P3-G10-Q1.",
    "P3-G10-Q3": "Context group excluded with P3-G10-Q1.",
    **{f"P7-R108-Q{n}": "The August 7 message assumes a help desk is available after its stated August 5-6 window; complete group excluded." for n in range(1, 5)},
}
REVIEWS = {}


def add(rows):
    for line in rows.strip().splitlines():
        qid, topic, explanation = line.split("|", 2)
        assert qid not in REVIEWS, qid
        REVIEWS[qid] = {"topic": topic, "explanation": explanation}


add("""
P5-001|p5-preposition|By Friday đặt hạn chót: phải nộp chậm nhất thứ Sáu. On chỉ một ngày, during đi với một khoảng thời gian.
P5-002|p5-preposition|Responsible for + danh từ/V-ing nghĩa là chịu trách nhiệm về việc gì; for training là cụm cần điền.
P5-003|p5-preposition|Interested in + danh từ/V-ing: quan tâm đến chương trình thành viên. Các giới từ còn lại không thuộc kết hợp này.
P5-004|p5-infinitive|Of là giới từ trong capable of, nên theo sau bằng V-ing: processing. Không dùng to process sau of.
P5-005|p5-tense|Since last January nêu thời điểm bắt đầu một trạng thái còn tiếp tục. Has been là hiện tại hoàn thành, phù hợp chủ ngữ số ít.
P5-006|p5-conjunction|Heavy rain là cụm danh từ, nên nguyên nhân dùng because of. Because cần mệnh đề; despite diễn tả nhượng bộ, không phù hợp nguyên nhân hủy sự kiện ở đây.
P5-007|p5-conjunction|Whereas đối chiếu hai lịch hoạt động trái nhau: chi nhánh trung tâm mở, chi nhánh sân bay đóng sớm.
P5-008|p5-word-form|Highly là trạng từ bổ nghĩa cho recommended; highly recommended nghĩa là được đánh giá/giới thiệu rất tốt.
P5-009|p5-infinitive|Expect + tân ngữ + to V: expects online sales to increase. Sau to của nguyên mẫu dùng increase.
P5-010|p5-relative|Applicants chỉ người; chỗ trống làm chủ ngữ của have nên cần who. Whom là dạng tân ngữ; whose cần danh từ theo sau.
P5-011|p5-conjunction|Unless đưa ra ngoại lệ: hàng đến đúng hạn trừ khi thời tiết trở nên khắc nghiệt. Despite không đi trực tiếp với mệnh đề này.
P5-012|p5-conjunction|Several delays là cụm danh từ nên dùng Despite để diễn tả dù có chậm trễ vẫn hoàn tất trong ngân sách.
P5-013|p5-word-form|Final bổ nghĩa một danh từ làm chủ ngữ của is required: approval, sự phê duyệt. Approve là động từ.
P5-014|p5-word-form|Chỗ trống bổ nghĩa locate nên dùng trạng từ efficiently; more efficiently là hiệu quả hơn.
P5-015|p5-infinitive|Be scheduled to V nghĩa là được lên lịch làm gì; dùng to begin sau is scheduled.
P5-016|p5-agreement|Với either…or, động từ ở đây theo assistants đứng gần, số nhiều: are attending. Không chọn is theo manager ở xa hơn.
P5-017|p5-agreement|Copy machines là thành phần gần động từ trong neither…nor và ở số nhiều: are functioning.
P5-018|p5-word-form|Time management là cụm danh từ quản lý thời gian, song song với customer service sau not only…but also.
P5-019|p5-agreement|Information không đếm được, dùng động từ số ít is. Không chia theo cảm giác có nhiều thông tin.
P5-020|p5-tense|Việc chọn ứng viên xảy ra trước lúc quản lý đến trong quá khứ: had already selected, quá khứ hoàn thành.
P5-021|p5-infinitive|To reduce diễn tả mục đích lắp đèn tiết kiệm năng lượng: để giảm chi phí điện.
P5-023|p5-relative|Policy chỉ vật và mệnh đề có dấu phẩy là bổ sung thông tin; which làm chủ ngữ của was announced.
P5-024|p5-relative|Whose nối customers với orders để thể hiện đơn hàng của họ. Who không thể đứng trực tiếp trước danh từ orders theo cấu trúc này.
P5-025|p5-relative|At which thay cho at the meeting. Sau giới từ đặt trước, không dùng that; where không đi cùng at theo cấu trúc này.
P5-026|p5-advanced|Trong giả định trái thực tế ở hiện tại theo văn phong trang trọng, If I were… đi với would revise. Had been sẽ chuyển giả định sang quá khứ.
P5-027|p5-advanced|Had we known là đảo ngữ của If we had known, phù hợp kết quả would have taken trong điều kiện quá khứ.
P5-028|p5-passive|Applications là thứ được nộp. Sau must cần be submitted, không phải submit chủ động hoặc submitted thiếu be.
P5-029|p5-comparison|So trong nhóm ba ứng viên cần dạng cao nhất the most qualified. More dùng cho so sánh hơn.
P5-030|p5-quantity|Steps đếm được số nhiều và có than nên dùng fewer. Less thường đi với danh từ không đếm được.
P5-031|p5-quantity|Time chỉ lượng thời gian không đếm được; very little nhấn mạnh còn rất ít thời gian.
P5-032|p5-pronouns|Another + danh từ số ít chỉ một cái khác. Other cần từ hạn định hoặc danh từ số nhiều trong cách dùng tương ứng.
P5-033|p5-agreement|Chủ ngữ trung tâm là Each, không phải participants; động từ số ít receives.
P5-034|p5-quantity|Responses là danh từ đếm được số nhiều, nên dùng many; much/a little/less không phù hợp ở đây.
P5-035|p5-preposition|During + cụm danh từ working hours diễn tả trong giờ làm. While thường cần mệnh đề trong dạng đối chiếu này.
P5-036|p5-preposition|Within ten business days đặt giới hạn trong vòng mười ngày làm việc. Between cần hai đầu mốc hoặc phạm vi khác.
P5-037|p5-preposition|According to + nguồn thông tin nghĩa là theo dự báo thời tiết. Because cần mệnh đề; In spite thiếu of.
P5-038|p5-preposition|In addition to the base salary nêu khoản bổ sung ngoài lương cơ bản: phụ cấp đi lại.
P5-039|p5-preposition|In response to customer feedback nghĩa là đáp lại phản hồi khách hàng; phù hợp lý do chỉnh chính sách.
P5-040|p5-preposition|On behalf of nghĩa là thay mặt. Người nhận giải đại diện cho toàn đội thiết kế.
P5-041|p5-preposition|Eligible for + danh từ chỉ quyền lợi đủ điều kiện nhận: health insurance benefits.
P5-042|p5-preposition|Một người familiar with một hệ thống là quen thuộc với hệ thống đó. Familiar to dùng theo hướng đối tượng quen thuộc đối với ai.
P5-043|p5-preposition|Similar to là giống với; so mẫu hiện tại với mẫu phát hành năm trước.
P5-044|p5-preposition|Aware of + vấn đề nghĩa là biết về vấn đề. Dùng of trước technical issue.
P5-045|p5-preposition|Satisfied with là hài lòng với đề xuất. Đây là cụm cần học cùng giới từ.
P5-046|p5-preposition|Due to + cụm danh từ nêu nguyên nhân: sự cố thiết bị gây chậm trễ.
P5-047|p5-preposition|Regardless of + danh từ nghĩa là bất kể; cửa hàng vẫn mở dù đang có sửa chữa.
P5-048|p5-preposition|Prior to + danh từ/V-ing nghĩa là trước khi. To là giới từ nên entering vẫn ở dạng V-ing.
P5-049|p5-conjunction|Whether…or… dẫn lựa chọn chưa được quyết định: tổ chức trong nhà hay ngoài trời.
P5-050|p5-conjunction|So that + mệnh đề nêu mục đích viết lại hướng dẫn: để người mới hiểu dễ hơn.
P5-051|p5-vocabulary|Negotiate with suppliers nghĩa là thương lượng với nhà cung cấp trước khi ký hợp đồng. Decorate/celebrate không phù hợp mục đích này.
P5-052|p5-vocabulary|Postponed là bị hoãn; người thuyết trình bị ốm nên hội thảo phải hoãn. Be postponed cũng đúng cấu trúc bị động.
P5-053|p5-vocabulary|Inventory là lượng hàng tồn kho cần kiểm tra để tránh thiếu. Itinerary là lịch trình; invoice là hóa đơn.
P5-054|p5-vocabulary|Travel reimbursement là hoàn trả chi phí đi công tác, cần đính kèm hóa đơn. Các danh từ khác không mang nghĩa hoàn chi phí.
P5-055|p5-vocabulary|Warranty là bảo hành; covering parts and labor giải thích phạm vi gồm linh kiện và công sửa chữa.
P5-056|p5-vocabulary|Shipment là lô hàng được vận chuyển và có thời điểm đến. Các từ kết thúc bằng -ship còn lại không mang nghĩa này.
P5-057|p5-vocabulary|Acquire a competitor là mua lại đối thủ. Require là yêu cầu; inquire là hỏi, không phải mua lại doanh nghiệp.
P5-058|p5-vocabulary|Annual revenue là doanh thu hằng năm, đại lượng có thể tăng 12%. Review là đánh giá, renewal là gia hạn.
P5-059|p5-vocabulary|Applicant là người ứng tuyển có thể nộp résumé. Application là đơn, không phải người thực hiện hành động nộp.
P5-060|p5-vocabulary|Product brochure là tập giới thiệu sản phẩm được lấy ở bàn thông tin. Branch/budget không phải loại ấn phẩm này.
P5-061|p5-preposition|Become familiar with diễn tả trở nên quen thuộc với các quy trình an toàn mới.
P5-062|p5-infinitive|To trong committed to là giới từ nên dùng reducing. Reduction cần of trước energy consumption, nên không phù hợp câu hiện tại.
P5-063|p5-infinitive|Accustomed to + V-ing là quen với việc gì. Working là bổ ngữ phù hợp sau to của cụm này.
P5-064|p5-infinitive|Be required to V nghĩa là được yêu cầu làm gì; khách cần to wear thẻ nhận diện.
P5-065|p5-infinitive|Be likely to increase nghĩa là có khả năng tăng. Sau likely dùng to V trong cấu trúc này.
P5-067|p5-preposition|Inclusive of nghĩa là đã bao gồm: phí hội nghị có cả bữa trưa và tài liệu in.
P5-068|p5-word-form|Carefully bổ nghĩa động từ read. Careful là tính từ, carefulness là danh từ, không dùng để mô tả cách đọc ở đây.
P5-069|p5-word-form|Response cần tính từ bổ nghĩa: prompt response là phản hồi nhanh. Promptly là trạng từ.
P5-070|p5-agreement|Chủ ngữ trung tâm là A list, số ít; of approved vendors chỉ bổ nghĩa, nên dùng is.
P5-071|p5-relative|Mệnh đề the components are assembled đã có chủ ngữ/động từ, thiếu thông tin nơi chốn: where = at/in which.
P5-072|p5-relative|Consultant là người; sau giới từ to đặt trước dùng whom theo văn phong trang trọng. Whose chỉ sở hữu.
P5-074|p5-relative|Bàn thông tin được đặt gần lối vào, dùng phân từ quá khứ Located. Chủ thể của cụm phân từ phải khớp information desk.
P5-075|p5-tense|So far this year nối khoảng thời gian từ đầu năm đến hiện tại; has opened phù hợp hiện tại hoàn thành.
P5-077|p5-comparison|Than yêu cầu so sánh hơn: more reliable. Considerably nhấn mạnh mức độ đáng kể của chênh lệch.
P5-078|p5-pronouns|Trước danh từ schedule cần tính từ sở hữu their. Theirs thay cả cụm danh từ nên không đứng trước schedule.
P5-079|p5-conjunction|Được đánh giá tốt nhưng bán dưới kỳ vọng là tương phản: however. Therefore sẽ diễn tả hệ quả, không đúng quan hệ ở đây.
P5-080|p5-vocabulary|Allocate funds to training là phân bổ tiền cho đào tạo. Locate là xác định vị trí; calculate là tính toán.
P5-081|p5-preposition|Be divided into + số phần: tài liệu được chia thành năm phần. Among chỉ sự phân bố giữa các bên.
P5-082|p5-preposition|Acceptable to someone nghĩa là được người đó chấp nhận. To nối lịch đề xuất với các quản lý đánh giá nó.
P5-083|p5-relative|Invoices received là dạng rút gọn invoices that are received. Hóa đơn nhận hành động nên dùng received.
P5-084|p5-conjunction|If + mệnh đề nêu điều kiện: nếu dự kiến có khách thì báo lễ tân. Các lựa chọn còn lại không đứng trực tiếp trước mệnh đề này.
P5-085|p5-advanced|Only after đứng đầu tạo đảo ngữ ở mệnh đề chính: did the error disappear. Disappear giữ nguyên mẫu sau did.
P5-086|p5-vocabulary|Reimburse guests for charges là hoàn lại cho khách khoản thu sai. Recruit là tuyển dụng, relocate là di dời.
P5-087|p5-word-form|Financial planning là việc lập kế hoạch tài chính. Plan đếm được số ít sẽ cần từ hạn định; planning phù hợp trực tiếp sau careful financial.
P5-088|p5-pronouns|Có đúng hai đề xuất đã xác định, nên đề xuất còn lại là the other. Another là một cái khác chưa xác định như vậy.
P5-089|p5-preposition|For three years diễn tả thời lượng hiệu lực. Since cần mốc bắt đầu; until cần mốc kết thúc.
P5-090|p5-preposition|Rest with + người/tổ chức nghĩa là thuộc quyền hoặc trách nhiệm quyết định của bên đó.
P5-091|p5-preposition|Applicable to là áp dụng đối với; quy định áp dụng cho mọi chi nhánh ở nước ngoài.
P5-092|p5-preposition|Express concern about là bày tỏ quan ngại về một vấn đề: thay đổi lịch đề xuất.
P5-093|p5-word-form|Complimentary là tính từ mang nghĩa miễn phí, bổ nghĩa transportation. Không nhầm với compliment nghĩa là lời khen.
P5-094|p5-word-form|Detailed là tính từ trước analysis: phân tích chi tiết hơn. Details là danh từ số nhiều.
P5-096|p5-tense|This is the first time thường đi với hiện tại hoàn thành để nói trải nghiệm tính đến hiện tại: has hosted.
P5-097|p5-relative|Several of whom: of đứng trước đại từ chỉ người applicants; dùng whom theo cấu trúc này.
P5-098|p5-conjunction|Whether dẫn mệnh đề danh từ về việc liệu có cần thêm kinh phí. Which không có danh từ/đối tượng lựa chọn phù hợp ở đây.
P5-100|p5-relative|Having submitted diễn tả hoàn tất nộp tài liệu trước khi đi đến phòng phỏng vấn. Chủ thể của cả hai hành động là applicant.
P5-101|p5-quantity|A few + danh từ đếm được số nhiều employees. Little/much/less không phù hợp kiểu danh từ ở đây.
P5-102|p5-comparison|Visitors được so sánh bằng than; more visitors nghĩa là nhiều khách hơn. Most là dạng cao nhất.
P5-103|p5-vocabulary|Replace damaged items nghĩa là thay sản phẩm hỏng. Release là phát hành/thả ra, không diễn tả thay thế ở đây.
P5-104|p5-vocabulary|Assess potential risks là đánh giá rủi ro. Access là truy cập; assist là hỗ trợ; assign là phân công.
P5-105|p5-preposition|In advance là cụm cố định chỉ việc làm trước, ở đây là trả phí đăng ký trước.
P5-106|p5-preposition|In accordance with nghĩa là theo đúng quy định. Cả cụm đi với local safety regulations.
P5-107|p5-preposition|Be composed of nghĩa là được cấu thành bởi. Of nối ủy ban với các đại diện thành viên.
P5-108|p5-preposition|Mindful of là lưu tâm/cẩn trọng với điều gì. Ở đây cần chú ý thông tin bảo mật khi làm việc từ xa.
P5-109|p5-word-form|Official là tính từ bổ nghĩa danh từ opening. Officially là trạng từ; office là văn phòng.
P5-110|p5-word-form|Clear and organized cùng là tính từ bổ nghĩa manner. Organization là danh từ nên không song song với clear ở đây.
P5-111|p5-tense|Trong mệnh đề thời gian as soon as nói về tương lai, dùng hiện tại đơn returns; will đặt ở mệnh đề chính.
P5-112|p5-tense|By next January đặt mốc tương lai; for ten years nhấn mạnh thời lượng tính đến mốc đó: will have worked.
P5-113|p5-relative|Loading area là nơi trucks can park; mệnh đề đã có chủ ngữ/động từ nên cần trạng từ quan hệ where.
P5-114|p5-relative|The details of which liên hệ details với proposal. Sau of không dùng that, và whom dùng cho người.
P5-115|p5-relative|Products purchased online là sản phẩm được mua trực tuyến, rút gọn từ that were purchased. Purchasing sẽ mang nghĩa sản phẩm tự mua.
P5-116|p5-relative|Having reviewed diễn tả xem xét số liệu xong trước khi chỉnh dự báo. Chủ thể analyst thực hiện cả hai hành động.
P5-117|p5-conjunction|In case diễn tả phòng khi có nhu cầu hoàn tiền; giữ hóa đơn trước để sẵn sàng cho khả năng đó.
P5-118|p5-infinitive|In order to + V nêu mục đích kéo dài giờ mở cửa: phục vụ khách dịp lễ.
P5-119|p5-pronouns|Neither of the two rooms được dùng số ít với has; its own projector chỉ máy chiếu riêng của mỗi phòng.
P5-120|p5-pronouns|Some…others…: một số nhân viên chọn sáng, những người khác chọn chiều. Others đứng độc lập thay danh từ số nhiều.
P5-121|p5-comparison|Runs cần trạng từ; than cần so sánh hơn: more smoothly. Smooth là tính từ, smoothest là cao nhất.
P5-122|p5-advanced|Rarely đứng đầu gây đảo trợ động từ: do we receive. Không giữ trật tự we receive trong cấu trúc này.
P5-123|p5-vocabulary|Conduct an audit là tiến hành kiểm toán/kiểm tra. Construct là xây dựng; contact là liên hệ.
P5-124|p5-vocabulary|Absorb the cost là chịu chi phí, ở đây là phí gửi thiết bị thay thế. Observe/reserve/preserve mang nghĩa khác.
""")

add("""
P2-001|p2-wh|Who hỏi người phụ trách thuyết trình. Ms. Park from the sales department chỉ đúng người; hai phương án còn lại trả lời giờ và địa điểm.
P2-002|p2-wh|Where hỏi nơi đặt hợp đồng: trên kệ trên cùng cạnh máy in. Signed và pages không chỉ vị trí.
P2-003|p2-wh|When cần thời điểm: sometime before noon, trước trưa. Loading dock là địa điểm.
P2-004|p2-wh|Why hỏi nguyên nhân hoãn họp. Chuyến bay của giám đốc bị chậm giải thích được lý do; phòng họp và thời lượng không trả lời why.
P2-005|p2-wh|How often hỏi tần suất: once every three months, mỗi ba tháng một lần. By a technician là người thực hiện.
P2-006|p2-request|Would you mind là lời nhờ. Not at all thể hiện không phiền và I'll send it right away xác nhận sẽ gửi ngay.
P2-007|p2-yesno|Câu hỏi phủ định vẫn trả lời theo thực tế. No kèm printer stopped working giải thích vì sao hóa đơn chưa được gửi.
P2-008|p2-request|Certainly nhận lời đặt bàn; câu hỏi về giờ giúp hoàn tất yêu cầu. Nhắc vật liệu bàn hoặc sáu người hôm qua không đáp ứng việc đặt tối nay.
P2-009|p2-wh|Which route hỏi đường đi. The expressway is usually faster đề xuất đường cao tốc; giờ bay không chỉ ra tuyến đường.
P2-010|p2-yesno|Giờ đóng cửa và we still have time xác nhận quán còn mở. Window là bẫy lặp động từ open với đối tượng khác.
P2-011|p2-request|Why don't we là lời đề nghị xem đề xuất sau bữa trưa. That sounds like a good idea đồng ý, không yêu cầu giải thích lý do.
P2-012|p2-wh|How many copies hỏi số bản in: Twenty should be enough. Nơi đặt máy photocopy không trả lời số lượng.
P2-013|p2-yesno|No, he has another appointment phủ nhận việc tham dự và nêu lý do. Nghề nghiệp của ông ấy không xác nhận việc dự hội chợ.
P2-014|p2-wh|Whose hỏi chủ sở hữu. Belongs to Ms. Lee trả lời ai có chiếc ô, không phải thời tiết hay trạng thái cửa.
P2-015|p2-request|Người khách xin ghế sát lối đi. Check what is available là phản hồi dịch vụ phù hợp trước khi xác nhận ghế.
P2-016|p2-wh|What do you think of hỏi ý kiến. Easier to move around đánh giá lợi ích cách bố trí mới; không hỏi tầng văn phòng.
P2-017|p2-wh|Where can I find hỏi nơi tra thông tin: trên trang cuối. Two years trả lời thời hạn bảo hành, không phải vị trí thông tin.
P2-019|p2-wh|How was your interview hỏi trải nghiệm. Better than expected là đánh giá phù hợp, còn corporate office là địa điểm.
P2-020|p2-yesno|Has…approved hỏi đã duyệt chưa. Not yet phản ánh trạng thái chưa xong và bổ sung dự kiến hoàn tất hôm nay.
P2-021|p2-wh|When hỏi lúc có catalog mới: early next month. Front desk là nơi, blue cover là đặc điểm.
P2-022|p2-request|Would you like me to là đề nghị giúp đỡ. Yes, that would be helpful nhận lời hỗ trợ sao hóa đơn.
P2-023|p2-yesno|Người đáp nói chưa thay vì phụ tùng thay thế chưa đến. Chi phí phụ tùng không xác nhận nó đã được thay hay chưa.
P2-024|p2-wh|Who should I contact hỏi người liên hệ. Accounting department là bộ phận giải quyết hoàn chi phí công tác.
P2-025|p2-request|Dời quầy trưng bày gần cửa là đề xuất. Attract more customers đánh giá lợi ích và thể hiện đồng tình.
P2-026|p2-wh|How long hỏi thời lượng cài đặt. Forty-five minutes phù hợp; every office computer là phạm vi máy cần cài.
P2-027|p2-wh|Câu hỏi lịch sự chứa where: cần địa điểm buổi định hướng. Auditorium on the first floor chỉ đúng nơi.
P2-028|p2-yesno|Shouldn't we gợi ý đặt thêm giấy. Yes và add it to the supply order đồng ý rồi nêu hành động.
P2-029|p2-wh|Which candidate hỏi ứng viên cụ thể. The one who worked in Toronto xác định người; six years ago là thời điểm.
P2-030|p2-yesno|Has…confirmed hỏi việc xác nhận đã hoàn tất chưa. Not yet kèm gửi email nhắc lại trả lời đúng trạng thái.
P2-031|p2-wh|Where should I leave cần nơi đặt biểu mẫu: khay cạnh bàn. Ngày hoàn thành không phải vị trí.
P2-032|p2-request|Đây là yêu cầu gia hạn. Hỏi quản lý dự án là bước cần để kiểm tra khả năng chấp thuận, chưa phải lời hứa chắc chắn.
P2-033|p2-wh|Who approved cần người phê duyệt. The finance director did lược lại approved và chỉ đúng chủ thể.
P2-034|p2-wh|Why hasn't…arrived hỏi lý do chưa đến. Shipped to the wrong address giải thích việc gửi nhầm và chậm giao.
P2-035|p2-wh|How much hỏi giá. An additional twelve dollars là phụ phí; giờ giao và quầy dịch vụ là thông tin khác.
P2-036|p2-yesno|Yes, if we start before lunch trả lời có đủ thời gian với điều kiện bắt đầu trước trưa, không cam kết vô điều kiện.
P2-037|p2-yesno|I tried, but it was already booked giải thích vì sao chưa đặt được phòng. Câu đáp không cần yes/no trực tiếp.
P2-038|p2-wh|When hỏi ngày bắt đầu của thực tập sinh. First Monday in June là mốc rõ ràng; four interns là số lượng.
P2-039|p2-request|Why don't I… là chủ động đề nghị gửi bảng giá. Thanks, that would be useful nhận lời giúp đỡ.
P2-040|p2-wh|Which elevator hỏi thang máy cụ thể. The one on the far left chỉ đúng thang, không phải giờ hay mức đông của nhà hàng.
P2-041|p2-request|Could you check là lời nhờ kiểm tra. Sure, I'll call this afternoon nhận việc và nêu cách thực hiện.
P2-042|p2-wh|How did you hear about hỏi nguồn thông tin tuyển dụng. A former colleague told me chỉ người cung cấp tin.
P2-043|p2-yesno|Người đáp giới hạn phần cần in màu: chỉ các biểu đồ. Điều này giải quyết trực tiếp câu hỏi có in màu tài liệu không.
P2-044|p2-wh|Where cần nơi gửi hành lý. Reception desk là vị trí; cân nặng vali và phương tiện đến không trả lời câu hỏi.
P2-045|p2-yesno|No và another hour cho biết kiểm tra chưa xong, cần thêm một giờ. New equipment không chứng minh cuộc kiểm tra đã kết thúc.
P2-046|p2-wh|How many people hỏi số người: nearly sixty, gần sáu mươi. Two days là thời lượng.
P2-047|p2-choice|Câu hỏi lựa chọn hóa đơn in hay email. An e-mail copy, please chọn rõ một trong hai phương án.
P2-048|p2-wh|Why hỏi nguyên nhân đóng lối vào. Floor is being repaired nêu công việc sửa sàn đang diễn ra.
P2-049|p2-request|Cards can't be shared từ chối yêu cầu mượn thẻ theo quy định. Vị trí đầu đọc thẻ không giải quyết lời nhờ.
P2-050|p2-wh|What time hỏi giờ mở bàn dịch vụ: at eight thirty. Main lobby chỉ vị trí.
P2-051|p2-wh|Where hỏi vị trí bãi xe khách: sau tòa nhà chính. Miễn phí hôm nay là phí, không phải nơi đỗ.
P2-052|p2-request|Would you be able to là lời nhờ xem dự toán hôm nay. Have time after lunch cho biết thời điểm có thể làm.
P2-053|p2-wh|Who hỏi bên chịu trách nhiệm cập nhật website. Digital marketing team chỉ đúng nhóm phụ trách.
P2-054|p2-wh|Why hỏi nguyên nhân bị từ chối gia hạn. Incomplete payment information là thiếu thông tin thanh toán.
P2-055|p2-wh|How soon hỏi chậm nhất khi nào hoàn thành. By the end of the day xác định thời hạn trong hôm nay.
P2-057|p2-wh|Which floor hỏi tầng: seventh floor. Vị trí thang máy không phải tầng của phòng pháp chế.
P2-058|p2-request|Certainly, if you have the receipt đồng ý đổi kích cỡ có điều kiện xuất trình hóa đơn. Giảm giá không trả lời việc đổi hàng.
P2-059|p2-wh|When hỏi thời gian giao ghế: Thursday afternoon. Loading dock là nơi nhận, không phải thời điểm.
P2-060|p2-request|Not at all đáp lại Would you mind theo nghĩa không phiền; review them now xác nhận đồng ý kiểm tra số liệu.
P2-061|p2-wh|Where hỏi nơi Ms. Ito để thẻ khách. Reception counter là đáp án vị trí; left at five nói giờ cô ấy rời đi.
P2-062|p2-wh|Why hỏi lý do chưa duyệt nội dung quảng cáo. Legal team requested a revision cho biết đang phải sửa theo yêu cầu pháp chế.
P2-063|p2-wh|How often hỏi tần suất thử báo cháy: twice a year. By the safety officer chỉ người làm.
P2-064|p2-yesno|Yes và khoảng bốn mươi khách giải thích vì sao cần đặt phòng lớn hơn, phù hợp câu hỏi xin quyết định.
P2-065|p2-wh|Who can authorize hỏi người có quyền duyệt. Finance manager là người; three days là thời gian xử lý.
P2-066|p2-yesno|No, the pickup was rescheduled cho biết chưa lấy vào sáng nay vì đã đổi lịch. Trọng lượng kiện hàng không trả lời việc lấy đã diễn ra chưa.
P2-067|p2-wh|Which version hỏi phiên bản cần in. The one marked final xác định bản đánh dấu cuối cùng.
P2-068|p2-request|Yêu cầu dời lịch cần kiểm tra lịch tư vấn viên trước. Let me check phản hồi phù hợp mà không hứa khi chưa xác nhận.
""")

add("""
P3-011|p3-overview|Khách đổi buổi giới thiệu sản phẩm từ 10 giờ sáng sang 2 giờ chiều; phần còn lại bàn việc cập nhật theo thay đổi đó.
P3-012|p3-next|Người nam nói sẽ cập nhật đặt phòng và báo nhóm thiết kế. Hai hành động đều được nêu trong I'll update…and notify…
P3-013|p3-detail|Người nữ yêu cầu bring the revised brochures: mang tập giới thiệu đã sửa, không phải bản cũ.
P3-021|p3-overview|Đặt phòng theo tên, đến sau nửa đêm và bố trí xe sân bay cùng gợi bối cảnh khách sạn.
P3-022|p3-detail|Người nam nói chuyến bay đến sau nửa đêm nên lo việc đến nhận phòng muộn; không nói đặt sai tên.
P3-023|p3-detail|Người nữ đề nghị airport transportation và người nam đồng ý. Đây là dịch vụ xe đưa đón sân bay.
P3-031|p3-detail|Because of a storm là nguyên nhân ghế giao chậm; đáp án paraphrase thành severe weather.
P3-032|p3-detail|The new employees start on Thursday: thứ Năm nhân viên mới bắt đầu. Ghế chỉ đến thứ Sáu.
P3-033|p3-next|Người nữ đề xuất tạm lấy ghế từ phòng đào tạo, không nói mua ngay ghế mới.
P3-041|p3-overview|Trao đổi về résumé, kinh nghiệm và vòng gặp phó chủ tịch là phỏng vấn tuyển dụng.
P3-042|p3-detail|Người nữ nói đã giúp tăng doanh thu khu vực 18%; số 12 là quy mô đội, không phải mức tăng.
P3-043|p3-next|The next step là cuộc phỏng vấn video với phó chủ tịch, tức sẽ có thêm một vòng phỏng vấn.
P3-051|p3-detail|Máy pha cà phê bị rò nước trở lại. Đây là sự cố thiết bị, không phải hết cà phê.
P3-052|p3-next|I'll call the repair company cho biết người nam sẽ liên hệ bên sửa chữa; thời điểm họ đến chưa chắc trước ngày mai.
P3-053|p3-next|Người nữ đề xuất chuyển máy nhỏ từ tầng hai, cùng với việc treo biển báo.
P3-061|p3-overview|Quảng cáo thu hút nhiều lượt xem nhưng ít người mua; lo ngại chính là tỷ lệ chuyển thành giao dịch thấp.
P3-062|p3-next|Người nữ cho rằng quy trình thanh toán phức tạp và đề nghị đội web kiểm tra checkout process.
P3-063|p3-detail|Người nam sẽ so giá của mình với đối thủ. Việc kiểm tra thanh toán là đề nghị của người nữ.
P3-071|p3-overview|Người nữ muốn đổi số sổ tay từ 20 thành 30 trong đơn 7615, tức điều chỉnh số lượng đặt hàng.
P3-072|p3-detail|Người nam nói ngày giao có thể chuyển từ thứ Ba sang thứ Tư khi tăng số lượng.
P3-073|p3-detail|As long as the boxes arrive before noon là điều kiện chấp nhận ngày giao mới: phải đến trước trưa.
P3-081|p3-detail|The image is still too dark nêu vấn đề hình chiếu quá tối ở phòng C, không phải phòng đã kín lịch.
P3-082|p3-next|Người nữ đề nghị chuyển sang phòng A có máy chiếu lớn hơn. Đây là thay phòng, không phải đổi ngày.
P3-083|p3-next|I'll tell the attendees… xác nhận người nam sẽ báo cho người tham dự về việc đổi phòng.
P3-G09-Q1|p3-overview|Buổi đào tạo gần đầy nên họ bàn mở phiên thứ hai vào tuần tới. Đây là mở thêm buổi, không hủy buổi cũ.
P3-G09-Q2|p3-detail|Wednesday afternoon is open chỉ chiều thứ Tư phòng còn trống.
P3-G09-Q3|p3-next|Người nữ sẽ nhờ nhân sự gửi thêm thông báo, theo I'll ask Human Resources to send another announcement.
P3-G11-Q1|p3-overview|Họ so sánh hai chuyến bay đến Osaka để kịp bữa tối hội nghị, nên đang sắp xếp chuyến bay.
P3-G11-Q2|p3-detail|That's early phản ứng với chuyến 6:10. Người nam tìm chuyến muộn hơn vì giờ khởi hành đầu quá sớm.
P3-G11-Q3|p3-detail|Chuyến 9 giờ giá cao hơn 30 đô la và đến trưa. Không nhầm giờ khởi hành với giờ đến.
P3-G12-Q1|p3-overview|Vấn đề là ảnh sản phẩm trên website bị mờ khi xem bằng điện thoại.
P3-G12-Q2|p3-next|Người nữ nêu hai việc: đổi kích cỡ ảnh và thử trang trên nhiều kích thước màn hình. Phương án kiểm thử màn hình khớp lời nói.
P3-G12-Q3|p3-detail|Người nam yêu cầu hoàn tất trước đợt bán hàng trực tuyến bắt đầu ngày mai, không phải cuối tuần.
P3-G13-Q1|p3-detail|Nhóm kế toán chuyển lên tầng sáu vào thứ Hai. Chỉ nhóm này được nêu, không phải cả công ty.
P3-G13-Q2|p3-next|Người nam nói cần cập nhật directory ở sảnh để phản ánh vị trí mới của nhóm kế toán.
P3-G13-Q3|p3-next|Người nữ sẽ nhắn các công ty giao hàng thường xuyên để họ biết nhóm đã chuyển tầng.
P3-G14-Q1|p3-overview|Ảnh catalog mùa đông được lên lịch thứ Năm và họ đang chờ áo mẫu, nên đang chuẩn bị buổi chụp catalog.
P3-G14-Q2|p3-detail|Nhà cung cấp báo áo sẽ giao tomorrow morning. Thursday là ngày chụp, không phải mốc giao được nói.
P3-G14-Q3|p3-next|Please check every item as soon as the boxes arrive yêu cầu kiểm tra từng món ngay khi nhận thùng.
P3-G15-Q1|p3-detail|Tập giới thiệu bị thiếu logo ở trang sau; không có thông tin sai giá hay thiếu số lượng.
P3-G15-Q2|p3-next|Người nam sẽ liên hệ the printer, trong bối cảnh này là đơn vị in ấn, không phải máy in như đồ vật.
P3-G15-Q3|p3-detail|Bản sửa phải đến chậm nhất chiều thứ Sáu để kịp sự kiện thứ Hai. By là hạn cuối.
P3-G16-Q1|p3-detail|Khách muốn xem reporting feature trong cuộc gọi video ngày mai: tính năng lập báo cáo.
P3-G16-Q2|p3-detail|Test account rather than real customer data nhằm tránh dùng dữ liệu khách thật để trình diễn.
P3-G16-Q3|p3-next|Người nam sẽ chuẩn bị báo cáo mẫu và gửi thông tin đăng nhập. Câu hỏi chỉ hỏi phần sẽ gửi.
P3-G17-Q1|p3-detail|Quầy trưng bày mùa hè đang chắn tầm nhìn khu hàng mới, không phải quá ít ánh sáng.
P3-G17-Q2|p3-next|Người nam đề xuất vị trí beside the escalator vì ở đó rộng hơn.
P3-G17-Q3|p3-detail|Evening staff sẽ chuyển quầy after closing: sau khi cửa hàng đóng cửa.
P4-011|p4-purpose|Bài thông báo chuyến tàu đi Riverside bị chậm 20 phút và đưa phương án thay thế, nên mục đích chính là báo trễ tàu.
P4-012|p4-detail|Because maintenance crews are inspecting the tracks giải thích nguyên nhân: đường ray đang được kiểm tra.
P4-013|p4-action|Vé hiện tại được dùng cho tàu nhanh 8:30 mà không trả thêm. Đây là lựa chọn được cho phép, không bắt buộc mua vé mới.
P4-021|p4-purpose|Người gọi nêu mã đơn 5842 và hai phương án xử lý thiếu hàng, nên đang trao đổi về đơn đặt hàng.
P4-022|p4-detail|Blue folders temporarily out of stock: bìa hồ sơ xanh dương hết tạm thời. Màu xanh lá có thể gửi hôm nay.
P4-023|p4-action|Người nhận cần gọi trước 4 giờ chiều để chọn gửi màu xanh lá ngay hay đợi xanh dương đến thứ Hai.
P4-031|p4-purpose|Tên City Design Museum cùng exhibit/galleries/tours cho biết thông báo ở bảo tàng.
P4-032|p4-detail|Triển lãm ảnh mở lúc 10:30. Guided tours mỗi giờ là lịch hoạt động khác.
P4-033|p4-detail|Food and beverages are not permitted: cấm thức ăn và đồ uống trong phòng trưng bày.
P4-041|p4-detail|West stairwell đóng để kiểm tra an toàn từ 9 giờ đến 13 giờ. Không phải toàn bộ lối vào tòa nhà.
P4-042|p4-action|Nhân viên dùng thang máy gần căng tin hoặc cầu thang phía đông trong thời gian đóng cầu thang tây.
P4-043|p4-action|Giao hàng phải vào loading dock trên Pine Street, tách với hướng đi của nhân viên.
P4-051|p4-detail|Khu đồ gia dụng chuyển từ tầng ba sang tầng hai vừa sửa. Không đảo chiều chuyển tầng.
P4-052|p4-detail|Chỉ small kitchen appliances được giảm 15%. Không mở rộng ưu đãi sang mọi mặt hàng trong cửa hàng.
P4-053|p4-detail|Through Sunday nghĩa là chương trình kéo dài đến hết Chủ nhật.
P4-061|p4-action|Trước khi bắt đầu, người học cần ký danh sách điểm danh gần cửa rồi nhận sổ đào tạo.
P4-062|p4-detail|Phiên sáng kết thúc 11:45, sau đó ăn trưa ở căng tin. Buổi minh họa ngoài trời là hoạt động chiều.
P4-063|p4-detail|Bài nói liên hệ việc mang thẻ với buổi minh họa ngoài trời vào chiều đó; không nêu yêu cầu trả phí bằng thẻ.
P4-G07-Q1|p4-detail|Nước tầng bốn tạm ngắt từ 10 giờ đến trưa để thay ống. Không phải ngắt nước mọi tầng cả ngày.
P4-G07-Q2|p4-detail|Nhà vệ sinh tầng ba và năm vẫn dùng được; tầng bốn là tầng chịu ảnh hưởng.
P4-G07-Q3|p4-action|Câu chốt yêu cầu gửi thắc mắc đến facilities department, bộ phận cơ sở vật chất.
P4-G08-Q1|p4-detail|Keynote speech diễn ra ở Grand Hall lúc 9:30; các phòng nhỏ dành cho workshop sau đó.
P4-G08-Q2|p4-action|Sau bài phát biểu, người tham gia được chọn một trong ba workshop nhỏ.
P4-G08-Q3|p4-detail|Lịch và sơ đồ phòng nằm bên trong name badge holder, bao đựng thẻ tên.
P4-G09-Q1|p4-detail|Phòng trưng bày mở từ thứ Hai đến thứ Bảy, nên Chủ nhật là ngày không mở theo lịch nêu.
P4-G09-Q2|p4-action|To schedule a design consultation, press two: bấm phím 2 để đặt tư vấn thiết kế.
P4-G09-Q3|p4-action|Giữ máy để nói với nhân viên phụ trách hóa đơn. Phím 1 dành cho thông tin giao hàng đã có.
P4-G10-Q1|p4-action|Hành khách chuyến 482 đến Vancouver cần đến Gate 16. Số chuyến bay không phải số cửa.
P4-G10-Q2|p4-detail|Máy bay đến muộn nên giờ lên máy bay đổi từ 5:20 sang 5:40. Không nhầm với giờ khởi hành đã được xác nhận.
P4-G10-Q3|p4-action|Người cần hỗ trợ có thể hỏi nhân viên tại quầy dịch vụ cạnh cửa lên máy bay.
P4-G11-Q1|p4-detail|Bàn thông tin đóng lúc 4 giờ để nhân viên đi đào tạo, không phải do sự cố thiết bị.
P4-G11-Q2|p4-action|Khách đến sau 4 giờ cần đăng ký với bảo vệ ở cửa nam, thay cho bàn thông tin sảnh chính.
P4-G11-Q3|p4-detail|Bàn thông tin sẽ mở lại vào giờ bình thường sáng mai, không phải tối cùng ngày.
P4-G12-Q1|p4-action|Trước lần dùng đầu, phải tháo lớp bọc bảo vệ bộ lọc. Đừng hiểu nhầm thành tháo bỏ bộ lọc.
P4-G12-Q2|p4-detail|Thiết bị cách tường ít nhất 30 centimet. At least là giới hạn tối thiểu, không phải tối đa.
P4-G12-Q3|p4-detail|Đèn cam báo bộ lọc cần thay; đặt bộ lọc mới được hướng dẫn qua website.
P4-G13-Q1|p4-detail|Khu tự học tầng hai đóng từ 13–15 giờ vì lắp đèn mới, không phải đóng cả ngày.
P4-G13-Q2|p4-action|Người đến có thể dùng quiet room ở tầng một thay thế trong thời gian đó.
P4-G13-Q3|p4-detail|Group study rooms không bị ảnh hưởng và vẫn mở. Chỉ khu tự học tầng hai được thông báo tạm đóng.
P4-G14-Q1|p4-detail|Bữa sáng phục vụ tại Garden Restaurant; east lobby là chỗ gặp tài xế, không phải nơi ăn sáng.
P4-G14-Q2|p4-action|Người đặt xe sân bay phải gặp tài xế trước giờ đi 10 phút. Không đợi đến đúng giờ khởi hành mới có mặt.
P4-G14-Q3|p4-action|Muốn trả phòng muộn cần liên hệ lễ tân trước 11 giờ sáng. Đây là hạn gửi yêu cầu, không tự là giờ trả phòng mới.
P4-G15-Q1|p4-detail|Điểm tập trung là bãi xe phía bắc lúc 8:30, sau đó xe buýt đưa mọi người đến công viên.
P4-G15-Q2|p4-detail|Ban tổ chức cung cấp găng tay và túi rác. Nước uống do người tham gia tự mang.
P4-G15-Q3|p4-action|Volunteers should bring drinking water: tự mang nước uống, đồng thời đi giày thoải mái.
""")

add("""
P7-011|p7-purpose|Subject và đoạn đầu thông báo kiểm tra thang máy phía đông. Các hướng dẫn đi lại là hệ quả của đợt kiểm tra này.
P7-012|p7-detail|Khoảng kiểm tra là between 9:00 A.M. and noon, nên kết thúc lúc trưa. 9 giờ là bắt đầu.
P7-013|p7-detail|Công ty giao hàng được chỉ định dùng loading dock elevator vì thang này vẫn phục vụ; không phải thang phía đông đang kiểm tra.
P7-021|p7-purpose|Quảng cáo gói phòng họp vào thứ Bảy hoặc Chủ nhật, kèm Internet, cà phê và ưu đãi phòng nghỉ.
P7-022|p7-detail|Free parking for the event organizer chỉ miễn phí đỗ xe cho người tổ chức. Phòng nghỉ chỉ giảm 15%, không miễn phí.
P7-023|p7-detail|At least ten days in advance yêu cầu đặt trước ít nhất mười ngày. Không có điều kiện bắt buộc hơn 20 khách.
P7-031|p7-purpose|Câu đầu thông báo kế hoạch mở trung tâm nghiên cứu ở Taichung đầu năm sau; các câu sau giải thích hoạt động và tuyển dụng.
P7-032|p7-detail|Địa điểm được chọn vì tiếp cận nhân lực kỹ thuật và đối tác sản xuất gần đó. Giá thuê rẻ không được nêu.
P7-033|p7-detail|Approximately 120 employees là khoảng 120 người trong năm đầu; approximately không phải một con số bảo đảm tuyệt đối.
P7-041|p7-purpose|Ông Wu báo chân bàn bị hỏng và thiếu hướng dẫn lắp, đồng thời yêu cầu gửi thay thế. Đây là báo vấn đề với đơn hàng.
P7-042|p7-detail|Assembly instructions were missing: thiếu hướng dẫn lắp ráp. Chân kim loại có nhưng bị hư, không phải bị thiếu.
P7-043|p7-detail|I have attached photographs of the damaged part xác nhận ảnh bộ phận hỏng được đính kèm.
P7-051|p7-purpose|Workshop nói về reducing office waste, gồm giảm giấy và tổ chức vật dụng tái sử dụng.
P7-052|p7-detail|A light lunch will be provided xác nhận có bữa trưa nhẹ. Chứng chỉ và phụ cấp không được nêu.
P7-053|p7-detail|Because seating is limited to 35 people là lý do phải đăng ký sớm; không phải do tăng phí.
P7-061|p7-detail|Thư viện đóng sớm để lắp thiết bị máy tính mới, theo so that…can be installed.
P7-062|p7-cross-reference|Thông báo thư viện đóng 18 giờ mâu thuẫn với kế hoạch gặp 19 giờ; email đề nghị chuyển sang quán cà phê đối diện.
P7-063|p7-detail|Quán sẽ đông sau bữa tối, nên nhóm cần đến sớm. Quán không được nói là đóng trước bữa tối.
P7-071|p7-detail|Manage website updates là nhiệm vụ ghi rõ trong mô tả công việc. Các công việc còn lại không thuộc vị trí được đăng.
P7-072|p7-detail|Basic HTML được ghi preferred but not required. Hai năm kinh nghiệm và kỹ năng viết được nêu ở phần yêu cầu.
P7-073|p7-detail|Hồ sơ nhận chậm nhất ngày 18/3 được ưu tiên. Không có yêu cầu nộp trực tiếp hay chấp nhận lương thấp.
P7-081|p7-detail|Có hai bàn phím, mỗi chiếc 68 đô la: 2 × 68 = 136. 178 là tổng có thêm chuột, không phải chỉ hai bàn phím.
P7-082|p7-detail|Standard delivery — Free xác nhận giao tiêu chuẩn không tính phí. Các con số khác thuộc hàng hóa hoặc thời hạn.
P7-083|p7-detail|Hàng trả phải chưa dùng và còn bao bì gốc, trong 30 ngày sau giao. Không tính 30 ngày từ một mốc tùy ý khác.
P7-091|p7-purpose|Từ tháng sau yêu cầu vật tư phải gửi qua purchasing portal mới; thay đổi là phương thức nộp yêu cầu.
P7-092|p7-detail|Nếu món cần mua không có trên cổng, thông báo yêu cầu liên hệ Purchasing, không tự đặt qua tài khoản cá nhân.
P7-101|p7-detail|Khóa kéo dài four weeks. Monday through Thursday là các ngày học mỗi tuần, không phải tổng thời lượng bốn ngày.
P7-102|p7-detail|Đăng ký trước hoặc vào 20/5 được giảm 10%. Phỏng vấn đầu vào vẫn bắt buộc, không phải thứ có thể bỏ để giảm phí.
P7-111|p7-detail|Hoàn tiền cho khoản mua trên 300 đô la cần quản lý khu vực duyệt. Đổi sản phẩm vẫn theo chính sách hiện có.
P7-112|p7-detail|Destroy unused copies of the previous form by Friday yêu cầu loại bỏ mẫu cũ chưa sử dụng chậm nhất thứ Sáu.
P7-121|p7-detail|Nhà hát mở lại thứ Bảy sau sáu tháng sửa chữa; đó không phải ngày bắt đầu sửa.
P7-122|p7-detail|Most of the original interior design was preserved: phần lớn thiết kế nội thất cũ được giữ. Ghế và âm thanh đã được nâng cấp.
P7-131|p7-detail|Due to road construction nêu nguyên nhân tuyến 18 bỏ trạm Central Market từ 3–7/7.
P7-132|p7-cross-reference|Thông báo chỉ trạm tạm Oak Street; tin nhắn của Jon xác nhận sẽ gặp Mia ở đó lúc 1:15, cạnh hiệu thuốc.
P7-14-Q1|p7-purpose|Sự kiện cung cấp tư vấn công nghệ miễn phí 30 phút: email, cập nhật bảo mật, sắp xếp ảnh. Không phải bán máy giảm giá.
P7-14-Q2|p7-detail|Người tham gia được yêu cầu mang thiết bị của mình và dây sạc. Trung tâm không thông báo thu phí thành viên.
P7-15-Q1|p7-detail|Chỉ địa điểm chuyển từ văn phòng trung tâm sang cơ sở sản xuất của khách; giờ bắt đầu vẫn 10 giờ.
P7-15-Q2|p7-detail|Security registration may take up to twenty minutes giải thích việc cần có mặt 9:30. Cuộc họp không đổi thành 9:30.
P7-R20-Q1|p7-detail|Khách yêu cầu thêm thời gian tham quan kho trước buổi trình diễn nên giờ được lùi 30 phút.
P7-R20-Q2|p7-detail|Nhân viên phải có mặt ở phòng 2 chậm nhất 1:15. 1:30 là giờ trình diễn bắt đầu, không phải giờ yêu cầu có mặt.
P7-R21-Q1|p7-detail|Gói 39 đô la có safety check cùng chỉnh phanh, kiểm lốp và làm sạch xích. Phụ tùng thay thế bị loại khỏi ưu đãi.
P7-R21-Q2|p7-detail|Appointments are recommended on Saturdays: nên đặt hẹn thứ Bảy. Recommended không có nghĩa bắt buộc trong mọi ngày.
P7-R22-Q1|p7-purpose|Công ty vừa hoàn thành lắp các tấm pin mặt trời ở trung tâm phân phối lớn nhất, không phải xây nhà máy mới.
P7-R22-Q2|p7-detail|Mục đích nêu là giảm chi phí vận hành và phát thải khí nhà kính. Mở rộng tuyển dụng không được đề cập.
P7-R23-Q1|p7-detail|Có xe shuttle miễn phí giữa các địa điểm tham gia Art Walk. Không có thông tin vé tàu giảm giá.
P7-R23-Q2|p7-detail|Some workshops require advance registration; vào các phòng trưng bày là miễn phí và không được nói là phải đăng ký trước.
P7-R24-Q1|p7-detail|Nhân viên phải loại bỏ vật liệu hết hạn trước kiểm tra. Không chỉ dán lại nhãn hoặc mang ra hành lang.
P7-R24-Q2|p7-detail|Checklist đã điền đặt vào bìa xanh bên ngoài phòng 214, chậm nhất 9/6. Đồ hết hạn không phải thứ đặt ở đó.
P7-R25-Q1|p7-detail|Cần chữ ký vì kiện hàng có thiết bị điện tử trị giá trên 500 đô la. Đây là lý do được nêu trực tiếp.
P7-R25-Q2|p7-detail|Muốn thay đổi giao hàng phải thao tác trước 20 giờ thứ Năm. Thứ Sáu là dự kiến giao, không phải hạn yêu cầu đổi.
P7-R26-Q1|p7-detail|Trợ lý phụ trách điều phối đặt phòng học và lịch sự kiện. Biết bảng tính là kỹ năng, không phải nhiệm vụ dạy bảng tính.
P7-R26-Q2|p7-detail|Kinh nghiệm làm ở cơ sở giáo dục được ghi preferred; chứng chỉ giảng dạy không xuất hiện trong yêu cầu.
P7-R27-Q1|p7-cross-reference|Thông báo đổi giờ mở ngày thường từ 8 giờ sang 7 giờ; tin nhắn tận dụng thay đổi này để đặt bữa sáng trước họp.
P7-R27-Q2|p7-detail|Owen yêu cầu hai suất chay và giao đến phòng 5 trước 8:15. Số phòng 5 không phải số ứng dụng hay số suất chay.
P7-R28-Q1|p7-detail|Sáng thứ Tư máy in màu cạnh phòng A được thay mới. Máy dự kiến dùng được lại vào chiều đó.
P7-R28-Q2|p7-detail|Việc in màu gấp gửi đến copy center tầng hai trước 17 giờ thứ Ba. Portal dùng đăng hướng dẫn kết nối, không nhận bản in.
P7-R29-Q1|p7-detail|Phí 75 đô la bao gồm nguyên liệu và dụng cụ. Giày kín mũi là đồ người học phải mang.
P7-R29-Q2|p7-detail|Đăng ký cùng bạn thì mỗi người giảm 10 đô la. Đến trễ hoặc mang dụng cụ riêng không được nêu là điều kiện giảm phí.
P7-R30-Q1|p7-detail|Kho có kiểm soát nhiệt độ dành cho thực phẩm và sản phẩm y tế cần điều kiện bảo quản ổn định.
P7-R30-Q2|p7-detail|Công ty dự kiến rút ngắn thời gian giao cho khách ở miền nam Đài Loan. Không có thông tin cắt lương nhân viên.
P7-R31-Q1|p7-detail|Mẫu mới bổ sung phần ghi các hành động theo dõi sau khiếu nại. Nó vẫn dùng cho khiếu nại dịch vụ.
P7-R31-Q2|p7-detail|Bản giấy cũ phải được tái chế trước hết tuần, không lưu thêm một năm hay gửi khách.
P7-R32-Q1|p7-detail|Lịch ngày 15/7 là Preparing for Video Interviews. Ngày 8/7 nói résumé, ngày 22/7 nói đàm phán đề nghị việc làm.
P7-R32-Q2|p7-detail|Bản ghi dành cho người đã đăng ký, trong bảy ngày sau mỗi webinar; không công khai vô thời hạn cho mọi khách xem website.
P7-R33-Q1|p7-detail|Bàn được giữ 15 phút sau 19:30, tức đến 19:45 theo thông tin xác nhận. Câu hỏi hỏi thời lượng, không hỏi giờ liên hệ đổi số khách.
P7-R33-Q2|p7-detail|Đổi số khách phải gọi chậm nhất trưa cùng ngày đặt bàn. Khoảng 15 phút là thời gian giữ bàn, không phải hạn thay đổi.
P7-R34-Q1|p7-detail|Bể Eastside đóng để sửa gạch từ 4–8/8. Thành viên có thể sang Northside với thẻ thành viên.
P7-R34-Q2|p7-cross-reference|Email của Nora chuyển buổi bơi đến chi nhánh thay thế và nói sẽ đến sớm giữ tủ đồ. Cô không nói hủy buổi bơi.
""")

add("""
P6-G34-Q1|p6-grammar|Vendor has submitted tạo hiện tại hoàn thành: nhà cung cấp đã nộp giấy chứng nhận. Has cần phân từ quá khứ, không phải danh từ submission.
P6-G34-Q2|p6-linking|Giấy cập nhật cần nộp trước khi gia hạn được duyệt, nên dùng before. Despite cần cụm danh từ, không phải mệnh đề này.
P6-G34-Q3|p6-insertion|Câu về đối chiếu thời hạn bảo hiểm giới thiệu hoạt động để This additional review ở câu sau có tiền đề, đồng thời nối đúng việc kiểm tra bảo hiểm trước gia hạn.
P6-G34-Q4|p6-grammar|Should chi phối hai động từ song song record…and notify. Notify the legal team là thông báo cho pháp chế; notice/notification không thay được động từ ở đây.
P6-G35-Q1|p6-grammar|Đơn vị làm mát tạm bị tắt để kiểm tra cảm biến: be shut down. Các cụm còn lại không diễn tả việc dừng thiết bị này.
P6-G35-Q2|p6-linking|When liên hệ after midnight với thời điểm demand is normally lowest; đây là mệnh đề nói nhu cầu thấp lúc nào.
P6-G35-Q3|p6-insertion|Câu về khả năng xử lý chậm hơn trong thời gian kiểm tra giải thích vì sao cấp trên phải xác nhận mọi đội đã nhận lịch sửa đổi. Các câu về picnic/màn hình/báo cáo không nối mạch.
P6-G35-Q4|p6-grammar|Has received dùng phân từ quá khứ để xác nhận đã nhận lịch. Receipt là danh từ; receptive là tính từ.
P6-G36-Q1|p6-grammar|Intended to cần động từ nguyên mẫu evaluate: thử nghiệm nhằm đánh giá khả năng giảm công việc hành chính.
P6-G36-Q2|p6-linking|Bản nháp phải được người phụ trách xem trước khi chia sẻ, nên before diễn tả đúng quy trình. During/despite không đứng trước mệnh đề này.
P6-G36-Q3|p6-insertion|Việc lưu trên máy chủ ngoài tạo lý do cho cảnh báo For that reason về tên khách bảo mật. Những câu khác không giải thích cảnh báo đó.
P6-G36-Q4|p6-grammar|Provide feedback on corrections là đưa phản hồi về các sửa đổi. Permission/attendance/equipment không diễn tả ý kiến về quá trình sửa.
P6-G37-Q1|p6-grammar|Containers nhận hành động trả lại; sau must be dùng returned. Returning sẽ mang nghĩa chủ động không phù hợp.
P6-G37-Q2|p6-linking|Otherwise nêu hệ quả nếu không trả trong bảy ngày: có thể bị tính phí thay thế. Similarly không thể hiện quan hệ điều kiện này.
P6-G37-Q3|p6-insertion|Câu về xe thu gom đến hai lần mỗi tuần giới thiệu lịch thu gom để câu sau hướng dẫn quét mã xem lần tiếp theo.
P6-G37-Q4|p6-grammar|Reported cần trạng từ chỉ cách/thời điểm báo: promptly, kịp thời. Promptness là danh từ.
P6-G38-Q1|p6-grammar|Serve customers cần trạng từ bổ nghĩa: consistently. Consistent là tính từ, consistency là danh từ.
P6-G38-Q2|p6-linking|Because giải thích lý do thay đổi chỉ tạm thời: quản lý cần dữ liệu bốn tuần trước khi duyệt lịch lâu dài.
P6-G38-Q3|p6-insertion|Câu về luân phiên phân công ca sớm nối nội dung bố trí nhân sự ở trước với giờ kết thúc ca ở sau. Các câu về xe, hóa đơn, picnic lạc mạch.
P6-G38-Q4|p6-grammar|Should + động từ nguyên mẫu: submit a request, nộp yêu cầu điều chỉnh lịch. Không dùng submitted hay submission sau should.
P7-R104-Q1|p7-inference|Hợp đồng tự gia hạn nếu không có thông báo chấm dứt. Email nói tiếp tục thêm năm, nên ngày 1/7 sẽ gia hạn thêm 12 tháng.
P7-R104-Q2|p7-detail|Phí cơ bản năm 14.400 đô la chia bốn quý: 14.400 ÷ 4 = 3.600. Phí địa điểm mới không thuộc base payment.
P7-R104-Q3|p7-cross-reference|Hai chi nhánh kích hoạt 15/7; điều khoản tính từ tháng đầy đủ đầu tiên sau kích hoạt, nên bắt đầu tháng Tám.
P7-R104-Q4|p7-detail|Điều khoản ghi after-hours emergency service billed separately: hỗ trợ khẩn cấp ngoài giờ có phí riêng.
P7-R105-Q1|p7-cross-reference|Khoản đủ loại chi phí được hỗ trợ là học phí 420 + phí thi bắt buộc 80 = 500 đô la. 60 tiền đi lại bị loại; số tiền thực nhận còn phụ thuộc hạn mức năm đã sử dụng.
P7-R105-Q2|p7-detail|Travel costs are not covered trực tiếp loại khoản 60 đô la đi lại. Không phải vì khoản này vượt giới hạn 600.
P7-R105-Q3|p7-cross-reference|Hồ sơ ghi full-time 14 months, thỏa yêu cầu làm toàn thời gian tối thiểu sáu tháng. Chưa có bằng chứng đã hoàn thành khóa hay còn nguyên hạn mức năm.
P7-R105-Q4|p7-detail|Sau khóa, cần chứng minh hoàn thành thành công trong 30 ngày. Preapproval là bước trước khóa, không phải tài liệu mới phải xin sau đó.
P7-R106-Q1|p7-cross-reference|Giờ khách đề xuất 13 giờ thứ Ba trùng phỏng vấn nhà cung cấp trong lịch. Cuộc gọi remote nên phòng 2 không phải trở ngại.
P7-R106-Q2|p7-cross-reference|Tin nhắn cuối chốt 14:30, rút còn 30 phút: kết thúc 15 giờ. Không dùng thời lượng 45 phút của lịch cũ.
P7-R106-Q3|p7-inference|Diego nói cần rời lúc 15 giờ để chuẩn bị sprint review lúc 15:30, nên sau cuộc gọi sẽ chuẩn bị buổi review.
P7-R106-Q4|p7-detail|Lịch và tin nhắn đều nói cuộc gọi remote, không cần phòng họp. Nó đã được chuyển lịch, không bị hủy.
P7-R107-Q1|p7-detail|Tháng Ba Search advertising có 510 leads, cao hơn 300, 280 và 210 của các kênh còn lại.
P7-R107-Q2|p7-detail|Cộng referral partners ba tháng: 260 + 255 + 300 = 815. 300 chỉ riêng tháng Ba.
P7-R107-Q3|p7-cross-reference|Webinars có tỷ lệ chuyển đổi 18%, cao nhất và gấp đôi email 9%. Đây là lý do chuyển ngân sách, dù search có số leads lớn hơn.
P7-R107-Q4|p7-detail|Ghi chú nói sẽ thử a new information kit cho referral partners. Không có thông tin chấm dứt kênh đối tác.
P7-R109-Q1|p7-cross-reference|Chính sách loại idle-time penalties; trên hóa đơn khoản này là idle-time fee 6 đô la. Không loại toàn bộ phiên sạc.
P7-R109-Q2|p7-detail|Marcus nói chưa đưa vào khoản valet 12 đô la tối đầu. Khoản tự đỗ 24 đô la đã được đính kèm.
P7-R109-Q3|p7-cross-reference|Chính sách cần ngày sạc, điện năng và tổng trả; hóa đơn có 14/11, 32 kWh và 20,52 đô la, đủ ba loại thông tin.
P7-R109-Q4|p7-cross-reference|Chuyến đi kết thúc 15/11; hạn là mười ngày làm việc sau ngày đó, không tính từ ngày sạc 14/11 và không dùng ngày lịch.
P7-R110-Q1|p7-detail|Customer Support thử 60 tài liệu, nhiều hơn Sales 40, Legal 25 và Product 35.
P7-R110-Q2|p7-detail|Chấp nhận không sửa 45 trên tổng 60: 45 ÷ 60 × 100 = 75%. 45 là số tài liệu, không phải tỷ lệ phần trăm.
P7-R110-Q3|p7-cross-reference|Tin nhắn 09:18 nói hợp đồng vẫn hay cần sửa từ ngữ, nên Legal chỉ giữ quyền reviewer. 11 phút tiết kiệm thuộc Support.
P7-R110-Q4|p7-inference|Chuỗi tin chọn Customer Support nhận mười giấy phép; Omar sẽ nhờ IT kích hoạt thứ Hai. Phải nối hai lượt trao đổi để biết bên nhận.
P1-009|p1-actions|Người phụ nữ cầm điện thoại ở bàn tiếp tân. Không có người ký biểu mẫu, chuyển ghế hay đóng máy tính vào thùng.
P1-010|p1-actions|Kỹ thuật viên đang kiểm tra dãy pin mặt trời bằng dụng cụ. Không có tuyết, sơn mái hoặc xe tải đang nhận hàng.
P1-011|p1-actions|Người làm dùng máy quét hướng vào nhãn kiện hàng trên bàn. Không phải buộc nơ hay trưng bày thùng trong tủ lạnh.
P1-012|p1-actions|Người phụ nữ đang tưới chậu cây trong sảnh. Potted plants khác cây trồng ngoài đất; hình không thể hiện lau đồ gỗ hay đợi thang máy.
P1-013|p1-actions|Cáp sạc đang được nối vào xe. Câu bị động đang diễn ra is being connected mô tả đúng thao tác, không phải rửa kính hay thay lốp.
P1-014|p1-actions|Nhân viên buồng phòng đang gấp khăn cạnh xe đẩy. Hình không có việc chuyển giường, hút bụi hoặc xe đầy thùng carton.
P1-015|p1-actions|Người đứng trên thang đặt thùng lên kệ cao. Kệ không trống hoàn toàn và thang đang mở để sử dụng.
P1-016|p1-actions|Hai người đang nhìn bản đồ giao thông họ cùng cầm. Không cần suy ra họ đang đi làm hay đối chiếu với bản đồ trên tường; không thấy họ lên tàu hoặc mua vé ở máy.
P1-017|p1-actions|Thước dây căng ngang khung cửa cho thấy đang đo chiều rộng. Không có thao tác treo rèm, lau kính hay quét sơn.
P1-018|p1-scene|Ghế được xếp chồng cạnh bàn cà phê. Mái che đang mở; không có khách được phục vụ hoặc khăn trải trên bàn.
""")
