# Báo cáo toàn diện dự án EduFace / AI-Attendance-System

Ngày đánh giá: **27/10/2026**, múi giờ UTC+7. Thư mục: `D:/project/AI-Attendance-System`. Bản nền Git: **162a61b** — `feat(sms): transform EduFace into full AI Student & Academic Management System`.

Báo cáo đánh giá **working tree hiện tại**, bao gồm 19 tệp tracked đã thay đổi và 7 tệp chưa tracked có từ trước khi đánh giá. Vì vậy, kết quả không đồng nghĩa với chất lượng bản commit hoặc bản đang chạy trên Internet.

## 1. Kết luận điều hành

**EduFace là một ứng dụng full-stack có chức năng thực, có bộ kiểm thử và có nền tảng kỹ thuật phù hợp để phát triển tiếp. Tuy nhiên, bản hiện tại còn lỗi trực tiếp trong luồng sinh viên và sai lệch dữ liệu học vụ; chưa đủ căn cứ để nghiệm thu cho vận hành chính thức hoặc tự động ra quyết định điều kiện dự thi.**

Phần đã xây dựng tương đối đầy đủ gồm đăng nhập ba phương thức, phân quyền ba vai trò, hồ sơ sinh viên, đăng ký khuôn mặt, phiên điểm danh, quét AI, điểm danh thủ công, báo cáo, bảng điểm, đơn xin nghỉ, thông báo và nhập danh sách. Frontend có giao diện tiếng Việt/Anh, sáng/tối, camera, biểu đồ, xuất CSV và chế độ xem thử độc lập.

Các vấn đề cần giải quyết trước tiên:

1. **Sinh viên tự đăng ký khuôn mặt bị lỗi:** handler đọc `user.person_id` trong khi `AuthenticatedUser` không có thuộc tính này.
2. **Chụp lại ảnh có thể làm sai lịch sử:** đăng ký lại cập nhật `enrolled_at`, còn báo cáo dùng trường đó để loại các buổi trước ngày đăng ký.
3. **Điểm học vụ chưa gắn với học phần:** một bộ điểm được lưu theo sinh viên, chưa theo sinh viên–học phần–học kỳ; chưa thể coi đây là sổ điểm đại học đầy đủ.
4. **Dashboard có thể hiển thị trên 100%:** đếm số bản ghi có mặt rồi chia cho số người, không xử lý một người học nhiều buổi trong ngày.
5. **Bootstrap admin có liên kết Google cố định trong mã:** cần bỏ liên kết tự động này trước khi dùng cho tổ chức khác.
6. **Liveness và confidence chưa phải bằng chứng xác thực sinh trắc học đáng tin cậy:** có nhánh lỗi được cho qua, khung hình phụ tùy chọn và điểm hiển thị được biến đổi từ cosine bằng công thức tự đặt.
7. **SDK và shared contracts đã lệch API:** các kiểm thử package vẫn xanh nhưng một số lời gọi tích hợp thực tế trả 404/422.

Điểm tích cực quan trọng: **225 kiểm thử hiện có đều đạt**, frontend và các package TypeScript build thành công; quét dependency hiện tại không phát hiện lỗ hổng đã biết. Các kết quả này không phủ nhận các lỗi nêu trên vì bộ test chưa bao phủ những tình huống đã tái hiện bổ sung.

## 2. Phạm vi và phương pháp

Đã rà soát cấu trúc repository, manifest/lockfile, các router backend, mô hình Pydantic, xác thực, truy cập MongoDB, pipeline AI, frontend routes/API/hooks/pages, thư viện tái sử dụng, workflow CI/CD và các tài liệu hướng dẫn/khắc phục.

Đã thực hiện:

- Chạy bộ test backend trong Python 3.11 của dự án, với cấu hình DB thử nghiệm cục bộ; tests dùng fake/monkeypatch.
- Chạy Vitest và build frontend; typecheck, build và test các workspace TypeScript.
- Chạy các phép tái hiện riêng bằng dữ liệu tổng hợp, không dùng tài khoản hoặc dữ liệu sinh trắc học thật.
- Nạp model `buffalo_sc` đã có sẵn trên máy và inference ảnh trống tổng hợp trên CPU.
- Mở 10 màn hình bằng trình duyệt local ở chế độ `/design-preview`, kiểm tra hiển thị và console.
- Chạy `npm audit` frontend và `pip-audit` môi trường Python hiện có.
- Trích danh mục API từ mã và đối chiếu với OpenAPI được ứng dụng tạo ra.

**Giới hạn:** chưa kiểm tra MongoDB Atlas thật, index thực tế trên cluster, tenant Microsoft, Google OAuth thật, Azure Blob, camera/người thật, tấn công trình chiếu ảnh/video thực nghiệm, tải đồng thời, khôi phục backup hoặc cấu hình production. Không đăng nhập vào production, không thay đổi dữ liệu thật, không push/deploy/publish. Không công bố nội dung `.env` hay secret.

Các nhãn bằng chứng sử dụng trong báo cáo:

| Nhãn | Ý nghĩa |
|---|---|
| Đã chạy | Có kết quả lệnh, trình duyệt hoặc tái hiện bằng dữ liệu tổng hợp |
| Xác nhận từ mã | Có đường thực thi hoặc cấu trúc dữ liệu trực tiếp chứng minh; chưa thử trên hạ tầng thật |
| Cần xác minh vận hành | Phụ thuộc cấu hình hoặc dịch vụ bên ngoài repository |

## 3. Sản phẩm và người dùng

Tên hiển thị hiện tại là **EduFace**; repository, API title, package và một số storage key vẫn dùng SmartAttend/AuraAttend. Đây là nợ nhất quán tên gọi, không phải ba ứng dụng riêng.

| Vai trò | Chức năng thực tế |
|---|---|
| Admin | Quản lý tài khoản, vai trò, liên kết SSO; đăng ký/xóa khuôn mặt; chẩn đoán hệ thống; toàn bộ quyền operator |
| Operator / Giảng viên | Tạo/đóng phiên, quét/ghi/sửa điểm danh, xem/sửa hồ sơ, xuất CSV, xem báo cáo; quản lý học phần, điểm, đơn nghỉ, thông báo, nhập sinh viên |
| Student | Đăng nhập; xem hồ sơ, lịch sử chuyên cần, điểm, lịch học và thông báo theo liên kết tài khoản; gửi đơn nghỉ; giao diện tự đăng ký/chụp lại ảnh |

Sinh viên đã có các kiểm soát chống lấy hồ sơ người khác qua query ở student portal, điểm và đơn nghỉ. Tuy nhiên operator hiện là quyền vận hành toàn hệ thống; chưa có cơ chế chỉ được quản lý lớp mình phụ trách.

## 4. Kiến trúc thực tế

Luồng tổng quát:

```text
Trình duyệt React
  ├─ REST JSON / multipart + Bearer JWT hoặc X-API-Key
  ├─ Camera → JPEG → FastAPI → InsightFace/ONNX/OpenCV
  └─ WebSocket → xác thực ở message đầu → nhận diện, trả kết quả

FastAPI
  ├─ Auth/RBAC, validation, rate limit, request ID
  ├─ Router nghiệp vụ: persons, sessions, attendance, reports, academic
  ├─ Motor async → MongoDB
  ├─ Thread pool → xử lý ảnh và inference CPU
  └─ Azure Blob tùy chọn → ảnh đăng ký
```

Đây là **backend đơn khối có chia module**, không phải hệ thống microservice độc lập. Phần lớn logic nghiệp vụ nằm trực tiếp trong router. AI nặng được đưa sang thread pool, còn truy vấn Motor chạy bất đồng bộ.

Nguồn: [main.py](D:/project/AI-Attendance-System/backend/main.py), [database.py](D:/project/AI-Attendance-System/backend/core/database.py), [azure_face.py](D:/project/AI-Attendance-System/backend/core/azure_face.py).

### Công nghệ và phiên bản đã đối chiếu

| Thành phần | Phiên bản/cấu hình quan sát được |
|---|---|
| Python backend đang kiểm thử | 3.11.15; Python mặc định của máy là 3.14.3 |
| FastAPI / Starlette | 0.156.1 / 1.9.0 trong virtualenv |
| Motor / PyMongo | 3.7.1 / 4.19.0, có pin trong requirements |
| Pydantic / NumPy / Pillow | 2.14.1 / 2.4.6 / 13.0.0 trong virtualenv |
| PyJWT | 2.15.1 trong virtualenv |
| AI runtime / model | InsightFace 2.1, ONNX Runtime 1.31.0 trong virtualenv; model `buffalo_sc`, CPU provider, vector 512 chiều |
| React / ReactDOM | 18.3.1 — README ghi React 19 là không khớp |
| Vite / Vitest | 8.3.5 / 5.0.5 trong lockfile frontend |
| TypeScript | Frontend lockfile 5.9.3; workspace root 7.0.2 |
| Tailwind CSS / MSAL | 4.3.3 / 5.25.1 |
| Node / npm đã chạy | 22.20.0 / 10.9.3 |
| Định hướng hosting trong mã/tài liệu | Vercel frontend, Render Docker backend, MongoDB Atlas; chưa xác minh trạng thái live |

Backend requirements dùng nhiều ràng buộc `>=`, do đó một lần cài mới có thể khác virtualenv được kiểm tra. Frontend có lockfile riêng; root npm workspace chỉ bao gồm `packages/*`, không bao gồm frontend.

### Tổ chức thư mục

| Khu vực | Vai trò | Quy mô tham khảo |
|---|---|---|
| Backend | API, auth, AI, DB, scripts, tests | 48 tệp văn bản/code được thống kê, 8.027 dòng |
| Frontend | SPA, pages, context, hooks, API client, CSS và cấu hình | 44 tệp, 6.120 dòng |
| Packages | 5 thư viện TS và 1 thư viện Python | 29 tệp, 2.289 dòng |
| Wiki | Hướng dẫn kiến trúc/nghiệp vụ/API | 17 tệp, 1.827 dòng |
| GitHub workflows | Backend/frontend/packages CI, publish và keepalive | 5 tệp, 314 dòng |

Số dòng là số dòng vật lý theo các đuôi code/tài liệu/cấu hình đã chọn, gồm tests và tài liệu; không phải LOC logic. Không tính dependencies, virtualenv, cache, build output, lockfile, ảnh hoặc báo cáo mới tạo.

## 5. Chức năng và luồng nghiệp vụ

### Đăng nhập và tài khoản

- Mật khẩu được băm `scrypt` với salt ngẫu nhiên; có nhánh tương thích bcrypt nếu thư viện đó được cài.
- JWT HS256 mặc định 12 giờ, mang ID, username, role và `auth_version`.
- Mỗi request JWT kiểm tra lại trạng thái user trong DB. Khóa tài khoản/đổi mật khẩu tăng phiên bản để thu hồi phiên; vai trò lấy từ DB hiện tại.
- API key admin/operator vẫn được hỗ trợ, có nhiều key cho xoay vòng. Các key chung không cung cấp định danh từng người.
- Google xác minh token rồi tìm/liên kết theo email hoặc khởi tạo student mới.
- Microsoft xác minh issuer/audience/tenant/chữ ký/nonce; challenge dùng một lần; tài khoản phải được admin liên kết trước bằng Object ID.
- Chưa thấy endpoint tự đổi/quên mật khẩu, refresh token hoặc logout thu hồi token phía server. Logout frontend chủ yếu xóa token local.

### Hồ sơ và đăng ký khuôn mặt

- Hồ sơ có tên, MSSV, lớp/khoa, email, điện thoại, ngày sinh, giới tính, khóa, ngành, cố vấn và trạng thái học vụ.
- Admin gửi 1–10 ảnh; sinh viên tự gửi 1–5 ảnh; có API kiểm tra trước chất lượng ảnh.
- Chống đăng ký trùng bằng so khớp khuôn mặt; admin nhập lại cùng tên có thể cập nhật embedding tại ID cũ.
- Đăng ký admin mới có rollback embedding nếu ghi `persons` thất bại.
- Xóa hồ sơ: xóa embedding và đánh dấu `persons.is_active=False`; không phải xóa toàn bộ lịch sử hoặc ảnh Blob.
- Luồng self-enroll hiện lỗi trước bước xác định chủ hồ sơ, xem F01.

### Phiên và điểm danh

- Phiên có tên, chuỗi lớp/khoa, giờ mở/đóng, trạng thái và ngưỡng đi muộn mặc định 15 phút.
- Quét HTTP chỉ ghi vào phiên đang mở; có chống trùng ở DB bằng unique `(person_id, session_id)`.
- Trạng thái gồm `present`, `late`, `excused`, `absent`.
- Đóng phiên cố gắng tạo bản ghi vắng cho người chưa có bản ghi trong lớp; lỗi vòng xử lý này đang bị nuốt.
- Operator được sửa trạng thái thủ công, kể cả phiên đã đóng. Việc sửa ghi lại `marked_at`, làm mất ý nghĩa thời điểm quét gốc nếu không có trường riêng.
- Frontend quét tự động theo chu kỳ chờ 3,5 giây sau lượt quét; khi bật liveness hai ảnh cách nhau khoảng 280 ms.
- **WebSocket hiện chỉ nhận diện và trả kết quả**, không ghi điểm danh. Nó được UI đưa vào chế độ nhận diện.

### Báo cáo chuyên cần

- Ngày báo cáo theo UTC+7 và thời điểm bắt đầu phiên; hỗ trợ lọc lớp.
- Một phiên áp dụng khi cùng department hoặc phiên không gán department; ngày phiên không trước ngày `enrolled_at` hiện tại.
- Phiên đóng được đánh giá; phiên mở đã có trạng thái attended cũng được đánh giá. Phiên mở chưa có bản ghi không tự bị tính là vắng.
- `present`, `late`, `excused` đều được tính vào số buổi đạt chuyên cần.
- Cảnh báo khi tỷ lệ dưới 75% và đã có buổi đánh giá.
- Heatmap: ngày chỉ đạt khi đủ tất cả buổi được đánh giá của ngày đó; thiếu một buổi là vắng; không có buổi phù hợp là trung tính.
- Report không có buổi trả tỷ lệ 0%; portal/grade có hồ sơ nhưng chưa có buổi đánh giá dùng 100%. UI đã có diễn giải ở một số nơi nhưng quy ước dữ liệu chưa hoàn toàn đồng nhất.

Nguồn quy tắc: [attendance_policy.py](D:/project/AI-Attendance-System/backend/core/attendance_policy.py), [reports.py](D:/project/AI-Attendance-System/backend/routers/reports.py), [auth.py](D:/project/AI-Attendance-System/backend/routers/auth.py:224).

### Học vụ

| Phân hệ | Đã có | Giới hạn |
|---|---|---|
| Học phần | Tạo/xem/xóa, mã, tín chỉ, giảng viên, lịch, phòng, học kỳ | Chưa có liên kết khóa ngoại giữa học phần với phiên/điểm; lịch là text |
| Bảng điểm | Giữa kỳ, cuối kỳ, điểm cộng, chuyên cần, hệ 10/4/chữ | Lưu theo `person_id`; chưa có điểm từng học phần/học kỳ và GPA tích lũy theo tín chỉ |
| Nghỉ phép | Sinh viên gửi, operator duyệt/từ chối, bảo vệ quyết định đồng thời | Đơn không có session chỉ được duyệt hành chính, không tự gán các buổi theo ngày |
| Thông báo | Nội dung, mức ưu tiên, lớp hoặc toàn hệ thống | Chưa có trạng thái đã đọc, lịch gửi, sửa thông báo hoặc lịch sử phiên bản |
| Import | Tối đa 500 sinh viên/lần, kiểm tra xung đột, tạo account tùy chọn | Chưa có transaction toàn batch; CSV frontend tách bằng dấu phẩy đơn giản |

Công thức đang được mã hóa: `điểm CC = tỷ lệ chuyên cần / 10`; `tổng = 10% × CC + 30% × giữa kỳ + 60% × cuối kỳ + bonus`, giới hạn 0–10. Chỉ có tổng khi cả điểm giữa và cuối kỳ đã nhập. Quy đổi A/B+/B/C+/C/D+/D/F theo mốc 8,5/8/7/6,5/5,5/5/4. Đây là chính sách trong code, chưa phải bằng chứng khớp quy chế chính thức của đơn vị sử dụng.

## 6. Mô hình dữ liệu và tính nhất quán

| Collection | ID / quan hệ | Nội dung |
|---|---|---|
| `users` | ObjectId; `person_id` trỏ profile | Đăng nhập, hash, role, active, auth_version, liên kết Google/Microsoft |
| `persons` | UUID string | Hồ sơ hành chính, lớp hiện tại, thời điểm đăng ký, trạng thái |
| `face_encodings` | Cùng UUID với persons | Tên và các vector embedding |
| `sessions` | ObjectId | Phiên, department, thời gian, late threshold |
| `attendance` | ObjectId; person UUID; session ObjectId | Trạng thái, thời điểm, confidence, người ghi |
| `auth_challenges` | Chuỗi ngẫu nhiên | Nonce hash và thời hạn Microsoft |
| `courses` | ObjectId | Danh mục học phần/lịch học |
| `grades` | ObjectId, tra cứu bằng person_id | Bộ điểm của sinh viên |
| `leave_requests` | ObjectId; person_id, session_id tùy chọn | Đơn nghỉ, quyết định, lý do, bằng chứng dạng URL |
| `announcements` | ObjectId | Thông báo và phạm vi lớp |
| `audit_logs` | ObjectId | Sự kiện audit, hiện mới ghi rõ ở quét điểm danh HTTP |

**Index đã khai báo:** tên/active của persons; active/started_at của sessions; unique person–session, marked_at/status của attendance; username unique; Google email unique dạng partial; Microsoft tenant+oid unique dạng partial; TTL expires_at của challenge; tên face_encodings.

**Khoảng trống:** chưa có unique MSSV chuẩn hóa, course code, grade key và khóa duy nhất cho liên kết person–account; chưa có index phù hợp cho nhiều truy vấn học vụ. Index tên persons đang dùng `TEXT` với `unique=True` và bắt lỗi rồi tiếp tục; không nên coi cấu hình này là bằng chứng đã bảo đảm duy nhất tên theo so sánh chính xác không phân biệt hoa/thường. Chưa kiểm tra việc tạo index đó trên MongoDB thật.

Chưa có collection roster/lớp học phần theo kỳ. Việc chuyển `department`, đổi `enrolled_at` hoặc soft-delete profile có thể làm thay đổi cách báo cáo diễn giải dữ liệu cũ. Đây là vấn đề mô hình lịch sử, không chỉ lỗi giao diện.

Một số code đọc tương thích session ID string cũ, trong khi list/export dùng `$lookup` ObjectId trực tiếp. Đã có script migration nhưng chưa chạy trên DB thật trong đợt đánh giá này. Migration cần xử lý trước các bản ghi trùng giữa string và ObjectId để tránh va chạm unique index.

## 7. Pipeline AI và giới hạn chất lượng

1. Kiểm tra MIME, tối đa 10 MiB/ảnh, Pillow verify và kích thước tối đa 6.000 px mỗi chiều.
2. Chuyển RGB→BGR, giảm ảnh khi chiều rộng lớn hơn 1.280 px.
3. CLAHE mềm với `clipLimit=1.4`, phối trộn 25% ảnh tăng sáng và 75% ảnh gốc.
4. InsightFace `buffalo_sc`, detector size 640×640, `det_thresh=0.3`.
5. Khi đăng ký: score phát hiện tối thiểu 0,60; mặt tối thiểu 60×60; kiểm tra mắt/landmark/che khuất và vị trí trong khung.
6. Có fusion embedding ảnh lật khi phù hợp, kiểm tra nhất quán giữa ảnh với ngưỡng 0,52; tạo thêm centroid chuẩn hóa cho người có ít nhất hai vector khi dựng ma trận.
7. Khi nhận diện: tải gallery từ MongoDB, dựng ma trận chuẩn hóa, nhân dot product với embedding truy vấn, lấy ứng viên cao nhất.
8. Tính điểm hiển thị từ cosine và áp dụng điều kiện nhận; sau đó kiểm tra texture/glare/chrominance và chuyển động hai frame nếu có.

**Các điểm cần hiểu đúng:**

- Tên `azure_face.py` là di sản đặt tên; nhận diện hiện chạy InsightFace local. Azure Blob chỉ tùy chọn lưu ảnh.
- Có biến `_matrix_cache` và `invalidate_cache`, nhưng đường identify/duplicate vẫn gọi `_load_all()` và dựng ma trận mỗi lần; cache chưa được sử dụng để tránh tải/dựng lại.
- Enrollment chọn mặt có diện tích lớn nhất khi ảnh có nhiều mặt, chưa bắt buộc chính xác một mặt ở backend. Package quality độc lập có quy tắc một mặt nhưng không được backend sử dụng.
- Enrollment có quality gate mạnh hơn identify; không thể mặc định mọi tiêu chí đăng ký đều áp dụng lúc quét.
- Không có tập đánh giá, confusion matrix, FAR/FRR, ROC, kiểm thử theo ánh sáng/thiết bị hoặc chống ảnh/video thật trong repository được rà soát.
- `confidence` hiển thị không phải xác suất đã được kiểm định. Điểm raw 0,40 được đổi thành khoảng 66,70%; raw 0,55 thành 81,73%.
- Thử model thật với ảnh trống: nạp **15,802 giây**, một inference **1,592 giây**, phát hiện **0 mặt**. Đây là một phép smoke trên máy đang có tác vụ khác; không phải benchmark production hay đánh giá nhận diện. Không đủ căn cứ cho tuyên bố `<300ms` trong README.

**Giấy phép model:** repository có MIT cho mã của dự án. Tài liệu chính chủ InsightFace Model Zoo nêu model phát hành sẵn dành cho nghiên cứu phi thương mại; `buffalo_sc` nằm trong danh sách model. Cần xác nhận quyền dùng model cho mục đích triển khai cụ thể, không suy từ MIT của repository rằng weights có cùng quyền sử dụng. [Nguồn chính chủ InsightFace](https://github.com/deepinsight/insightface/blob/master/model_zoo/README.md).

## 8. Frontend và trải nghiệm sử dụng

| Route | Chức năng |
|---|---|
| `/login` | Mật khẩu, Google, Microsoft |
| `/` | Dashboard, phiên mở, hoạt động, biểu đồ |
| `/scanner` | Camera, ngưỡng, hai-frame liveness, âm báo, tự quét, nhận diện WebSocket |
| `/sessions` | Tạo/đóng phiên, ngưỡng muộn, danh sách phiên |
| `/records` | Lọc bản ghi, sửa thủ công, xuất CSV |
| `/people` | Danh bạ, tìm/lọc/phân trang, sửa profile, lịch sử, xuất hồ sơ |
| `/enroll` | Đăng ký/cập nhật face, camera/upload, hướng dẫn tư thế |
| `/reports` | Daily chart, tỷ lệ cá nhân, heatmap, CSV |
| `/academic` | Điểm, đơn nghỉ, học phần, thông báo, import |
| `/system` | User/role/SSO và chẩn đoán cấu hình |
| `/student` | Portal cá nhân và self-enroll |
| `/design-preview/*` | Xem thử dữ liệu trong RAM, chỉ có ở development |

Điểm tốt: chia tải theo trang bằng lazy import; có error boundary; `useResource` bỏ phản hồi cũ; camera dừng track khi unmount; dispose object URL; thông báo lỗi/thành công; native dialog; label, skip link và bảng cuộn có accessibility role.

Build production đã thành công. Một số kích thước bundle: main JS **197,16 kB** / gzip **65,32 kB**, chart chunk **368,31 kB** / gzip **98,21 kB**, CSS **44,36 kB** / gzip **9,64 kB**. Đây là số đo build hiện tại, không phải số đo thời gian tải mạng.

Đã kiểm tra 10 màn hình preview trên trình duyệt desktop; không thấy error boundary hoặc console error trong phiên. Chưa kiểm tra đầy đủ responsive, keyboard-only, screen reader, thiết bị di động, camera thật hoặc thao tác ghi dữ liệu qua backend thật. Preview thành công chỉ xác nhận tầng giao diện với dữ liệu mẫu.

Ảnh thực tế của trang học vụ trong chế độ dữ liệu mẫu:

![Trang học vụ đã kiểm tra trên trình duyệt local](D:/project/AI-Attendance-System/docs/reports/2026-10-27/ui-academic-preview.png)

## 9. Thư viện dùng chung và mức độ tích hợp

| Package | Mục đích | Đánh giá |
|---|---|---|
| `face-matching-core` TS | Normalize, cosine, ranking, top match | Có kiểm thử toán học; không tự chạy model |
| `face-quality-gates` | Quy tắc quality độc lập | Có test, nhưng thông số/logic đã khác backend |
| `attendance-domain-core` | Quy tắc phiên và chống trùng | Có test; default status viết hoa khác backend |
| `attendance-contracts` | Các interface TS | Không có validator runtime; thiếu vai trò student và nhiều schema mới |
| `smartattend-client` | HTTP SDK | Có retry/error/transport và test mock, nhưng endpoint/payload bị lệch |
| `smartattend-face-matching` Python | Cosine/normalize/rank | Có mã độc lập; chưa thấy suite/CI riêng hoặc backend import nó |

Frontend dùng client/types tự khai báo trong [client.ts](D:/project/AI-Attendance-System/frontend/src/api/client.ts), không dùng SDK trên. Router backend gọi `azure_face` trực tiếp; `VisionEngine` mới là lớp wrapper chưa trở thành điểm tích hợp thực tế.

Các khác biệt có bằng chứng:

| SDK/shared contracts | Backend hiện tại |
|---|---|
| Identify multipart field `photo` | Bắt buộc `frame` → probe trả 422 |
| POST `/api/attendance/mark`, session trong form | POST `/api/attendance/mark/{session_id}` → probe trả 404 |
| GET `/api/attendance/export` | GET `/api/attendance/export/csv` |
| GET `/api/reports/rates` | GET `/api/reports/persons` |
| Query sessions `active_only` | Query `active` |
| UserRole chỉ admin/operator | Có cả student |
| Daily `total_attendees`, `avg_attendance_rate` | `total_present`, `attendance_rate` |
| Heatmap mảng date/hour/count | Object `{dates, persons}` |
| Status `Present`... | `present`... |

Kiểm thử contracts hiện chủ yếu tạo object mẫu, serialize/parse JSON và assert vài giá trị; chưa kiểm tra response FastAPI thật hoặc so schema. Vì vậy việc package test đạt không chứng minh SDK tương thích backend.

## 10. Kết quả kiểm chứng thực tế

| Hạng mục | Kết quả | Giới hạn |
|---|---|---|
| Backend `python -m pytest -q` | **170 passed**, 1 warning, 83,85 giây | Fakes, không phải Atlas/model end-to-end |
| Frontend Vitest | **24 passed / 4 files**, khoảng 63,36 giây | Có log lỗi chủ động từ test error boundary; suite vẫn đạt |
| Frontend `npm run build` | **Đạt**, có TypeScript build | Không kiểm chứng hosting thực |
| Root `npm run typecheck` | **Đạt** cho 5 package TS | Không thay thế frontend typecheck |
| Root `npm run build` | **Đạt** | Không publish |
| Root `npm test`, sau build | **31 passed** = 1+8+9+7+6 | Mock/logic đơn vị |
| Frontend `npm audit --json` | **0** advisory đã biết, gồm dev dependency | Theo dữ liệu audit tại thời điểm chạy |
| Backend `pip-audit` virtualenv | **86 package**, 0 vulnerability, 0 skipped | Môi trường hiện tại; không phải lock của image production |
| OpenAPI | **45 paths / 52 HTTP operations** | Thêm 1 WebSocket ngoài OpenAPI |
| Model CPU, ảnh trống | **Nạp và inference được**, 0 mặt | Không đánh giá accuracy/liveness |
| 10 màn hình preview | **Hiển thị được**, không console error quan sát được | Dữ liệu giả lập |
| CLI tạo user theo README | **Lỗi `ModuleNotFoundError: core`** ngay ở `--help` | Chưa ghi user/DB |

Các warning không làm test thất bại: FastAPI TestClient cảnh báo cơ chế httpx; plugin Vite gợi ý chuyển React plugin; build có thông tin thời gian plugin. Không nên nhầm log lỗi chủ động của test `PageErrorBoundary` với frontend test bị fail.

### Phép tái hiện bổ sung

| Probe | Quan sát |
|---|---|
| Gọi self-enroll với `AuthenticatedUser` thật, ảnh/model/DB stub | `AttributeError: 'AuthenticatedUser' object has no attribute 'person_id'` |
| Admin đăng ký lại cùng hồ sơ, buổi học cũ trước ngày cập nhật | `session_applies_to_person`: trước `true`, sau `false` |
| Dashboard 10 sinh viên, 2 phiên, 20 lượt present | `attendance_rate = 200.0` |
| Liveness ảnh đồng nhất hoặc đối tượng face lỗi | Hàm trả `is_live = true` |
| Không gửi probe frame | Motion check trả cho qua |
| Payload/path SDK identify và mark | HTTP 422 và 404 |
| Preflight từ origin Vercel không liên quan | HTTP 200, origin được phản chiếu, credentials=true |
| `/health` khi không chạy lifespan/DB | Vẫn HTTP 200, `{status: healthy}` |

Probe liveness chỉ chứng minh hành vi hàm xử lý, **không chứng minh một ảnh trống có thể qua toàn bộ detector và điểm danh**. Probe CORS không chứng minh website bất kỳ tự lấy được JWT; tác động phụ thuộc nơi giữ và truyền credential.

## 11. Phát hiện và thứ tự ưu tiên

Ưu tiên **P1**: cần xử lý trước khi dùng chính thức. **P2**: ảnh hưởng độ tin cậy, tính đúng hoặc mở rộng; lên kế hoạch ngay sau P1. **P3**: cải thiện tài liệu/vận hành. Đây là phân loại sửa lỗi của báo cáo, không phải điểm CVSS.

### F01 — P1: Self-enroll không hoạt động

**Đã chạy.** [persons.py:351](D:/project/AI-Attendance-System/backend/routers/persons.py:351) truy cập `user.person_id`; [auth.py](D:/project/AI-Attendance-System/backend/core/auth.py) không khai báo/truyền thuộc tính đó. Sinh viên đi qua validation và khởi tạo AI sẽ gặp exception không xử lý, tương ứng lỗi 500 trong HTTP thông thường.

**Hướng sửa:** lấy liên kết từ account trong DB như `_linked_person_id`; kiểm tra role/ownership rõ ràng. Không chỉ thêm `getattr(..., None)`: nhánh fallback kế tiếp đang tìm profile theo email người gọi nhập, có thể dẫn tới sửa profile không thuộc tài khoản khi lỗi đầu đã được bỏ qua. Bổ sung test HTTP cho tài khoản chưa/đã có profile và trường hợp nhập email người khác.

### F02 — P1: Chụp lại khuôn mặt làm sai lịch sử chuyên cần

**Đã chạy.** [persons.py:252](D:/project/AI-Attendance-System/backend/routers/persons.py:252) cập nhật `enrolled_at` khi đăng ký lại; policy coi ngày đó là ngày bắt đầu tính học. Nhánh self-enroll cập nhật tương tự tại dòng 398. Các buổi cũ không bị xóa vật lý nhưng bị loại khỏi portal/báo cáo/điểm chuyên cần.

**Hướng sửa:** giữ thời điểm tham gia học bất biến, thêm `face_updated_at`, phân biệt ngày nhập hồ sơ với ngày vào lớp. Test rằng lịch sử/tỷ lệ không thay đổi sau cập nhật ảnh.

### F03 — P1: Sổ điểm không phân biệt học phần/học kỳ

**Xác nhận từ mã.** [academic.py:306](D:/project/AI-Attendance-System/backend/routers/academic.py:306) upsert chỉ bằng `person_id`; [schemas.py](D:/project/AI-Attendance-System/backend/core/schemas.py) không có course_id trong GradeUpsert/SessionCreate. Sinh viên học hai môn không có hai bộ điểm độc lập. Chuyên cần gộp theo department, có thể cộng cả phiên chung.

**Hướng sửa:** định danh lớp học phần/đợt mở môn, enrollment roster, session.course_offering_id và grade unique theo enrollment. GPA tích lũy phải là bài toán riêng có tín chỉ và chính sách học lại; không dùng quy đổi một bộ điểm làm GPA toàn khóa.

### F04 — P1: Admin được tự liên kết với email Google cố định

**Xác nhận từ mã.** [database.py:111](D:/project/AI-Attendance-System/backend/core/database.py:111) gán email cá nhân cố định khi tạo admin hoặc khi admin cũ thiếu liên kết. Điều này xảy ra cả nhánh production nếu bootstrap đủ điều kiện, vì lệnh `if production: return` nằm sau phần tạo/liên kết admin. Google exchange cấp JWT theo tài khoản đã liên kết.

**Hướng sửa:** bỏ dữ liệu danh tính cá nhân khỏi bootstrap; liên kết SSO admin phải được cấu hình/kiểm chứng có chủ đích. Kiểm tra tài khoản đã seed trong môi trường thật. Báo cáo không kết luận có ai đã khai thác quyền này.

### F05 — P1: Mật khẩu mặc định dùng chung và login không giới hạn tần suất

**Xác nhận từ mã.** Import mặc định `123456`; enrollment admin cũng có fallback này. [auth.py:43](D:/project/AI-Attendance-System/backend/routers/auth.py:43) không có limiter; chưa thấy middleware global thay thế. Băm scrypt đúng không khắc phục mật khẩu chung yếu hoặc thử đăng nhập liên tục.

**Hướng sửa:** thông tin kích hoạt riêng từng account, buộc đổi mật khẩu đầu tiên, giới hạn theo IP+tài khoản và audit thất bại. `APP_ENV` mặc định development còn cho seed tài khoản demo; kiểm tra việc đặt production trước triển khai.

### F06 — P1: Chống giả mạo có nhánh cho qua khi lỗi

**Đã chạy ở mức hàm.** [azure_face.py:385](D:/project/AI-Attendance-System/backend/core/azure_face.py:385) trả live khi variance=0 hoặc exception; motion check cho qua khi thiếu probe. REST nhận ảnh multipart bất kỳ, nên việc frontend khóa nút upload ở chế độ mark không cưỡng chế nguồn camera ở server. Liveness hai-frame có thể tắt tại UI.

**Hướng sửa:** bỏ ngoại lệ dành cho mock khỏi đường production; lỗi xác thực phải dẫn tới từ chối/kiểm tra thủ công; xác định chính sách probe/challenge phía server. Đánh giá bằng tập ảnh in, màn hình, replay video và người thật trước khi quảng bá bảo đảm chống giả mạo.

### F07 — P1: Ngưỡng nhận diện và điểm hiển thị chưa đồng nghĩa với cosine

**Đã chạy phép biến đổi; xác nhận điều kiện từ mã.** [azure_face.py:646](D:/project/AI-Attendance-System/backend/core/azure_face.py:646) chấp nhận theo raw tối thiểu `min(threshold, 0.38)` và điểm đã biến đổi. Ngưỡng UI 0,60 vẫn có thể nhận raw 0,38 vì điểm hiển thị khoảng 0,6247. API cho operator hạ threshold tới 0,10; default query 0,40 cũng khiến MIN_CONFIDENCE môi trường không tự trở thành sàn bắt buộc.

**Hướng sửa:** lưu raw similarity riêng, đặt sàn backend rõ ràng, hiệu chỉnh từ dữ liệu validation có nhãn. Không dùng phần trăm hiển thị làm lời khẳng định xác suất nhận đúng.

### F08 — P2: Dashboard sai mẫu số và bỏ trạng thái đi muộn/có phép

**Đã chạy.** [dashboard.py:20](D:/project/AI-Attendance-System/backend/routers/dashboard.py:20) lấy count attendance chia count persons; [database.py:200](D:/project/AI-Attendance-System/backend/core/database.py:200) chỉ đếm `present`. Mười sinh viên học hai phiên có thể cho 200%; cách tính khác các báo cáo chuyên cần.

**Hướng sửa:** định nghĩa rõ chỉ số số người duy nhất hay lượt/buổi đủ điều kiện; dùng chung policy, hiển thị đúng đơn vị.

### F09 — P1 cho người tích hợp SDK: SDK/contracts không tương thích API

**Đã chạy 404/422 và đối chiếu mã.** Xem bảng ở mục 9 và [SDK index.ts](D:/project/AI-Attendance-System/packages/smartattend-client/src/index.ts:264).

**Hướng sửa:** tạo types từ OpenAPI hoặc contract một nguồn, sửa endpoint/form field/query, bổ sung contract tests chạy với FastAPI app. Mở rộng student/academic/SSO khi công bố hỗ trợ chúng. Package test giả lập không được xem là xác nhận tích hợp.

### F10 — P2: Quyền operator rất rộng, chưa có phạm vi lớp

**Xác nhận từ mã; cần chốt yêu cầu nghiệp vụ.** Operator được sửa hồ sơ, điểm, duyệt đơn, import và xóa course/announcement trên mọi lớp. Session không có owner/assigned lecturer. Endpoint mark/manual cũng không kiểm tra `session_applies_to_person` trước ghi nên có thể ghi người ngoài lớp; báo cáo sau đó lại bỏ qua bản ghi này.

**Hướng sửa:** nếu mỗi giảng viên chỉ phụ trách lớp riêng, thêm phân công và kiểm tra quyền theo đối tượng. Dùng chung policy khi ghi và khi thống kê. Nếu operator là giáo vụ toàn trường theo chủ ý, cần mô tả rõ quyền đó và giữ giảng viên thường thành vai trò khác.

### F11 — P2: Ràng buộc DB và cập nhật nhiều bước chưa đủ

**Xác nhận từ mã.** Check-then-write của MSSV, course code, grade chưa được unique index tương ứng bảo vệ. Import kiểm tra trước toàn bộ input nhưng ghi từng dòng; lỗi giữa chừng vẫn có thể để lại một phần dữ liệu. Self-enroll chưa có rollback như enroll admin mới; cập nhật lại face và person không phải giao dịch chung. Tên người đang bị coi gần như khóa định danh, gây khó cho người trùng họ tên.

**Hướng sửa:** unique key chuẩn hóa theo nghiệp vụ, transaction hoặc cơ chế idempotency/compensation có kiểm thử fault injection; cho phép trùng tên, dùng MSSV/ID ổn định. Xác minh index thực tế trên cluster.

### F12 — P2: CORS chấp nhận mọi subdomain vercel.app

**Đã chạy preflight.** [main.py:193](D:/project/AI-Attendance-System/backend/main.py:193) cho origin Vercel không liên quan. Guard chống chuỗi `*` không làm chính sách trở thành danh sách origin riêng của dự án. Với token trong localStorage, đây không tự động là đánh cắp token hoặc CSRF thành công; vẫn là mở rộng trust không cần thiết.

**Hướng sửa:** danh sách production origin cụ thể; preview deployments cần quy tắc được sở hữu/kiểm soát. Đồng bộ cấu hình HTTP và WebSocket: allowlist WS mặc định hiện không bao gồm mọi domain production được HTTP hỗ trợ.

### F13 — P1 nếu build Docker từ máy có secret: thiếu .dockerignore

**Xác nhận từ cấu hình.** [Dockerfile:31](D:/project/AI-Attendance-System/backend/Dockerfile:31) dùng `COPY . .`; không thấy `.dockerignore`. Máy hiện có backend `.env` và `.venv`. `.gitignore` không phải bộ lọc Docker build context, nên build local theo context backend có thể đưa những tệp đó vào image. Chưa build/push image và chưa kiểm chứng image đang deploy chứa gì.

**Hướng sửa:** `.dockerignore` cho secret, venv, cache/test output; copy mã cần thiết; tạo non-root user; pin/lock dependency phù hợp. Đây là nguy cơ phụ thuộc cách build, không phải kết luận secret đã bị phát tán.

### F14 — P2: CSV hồ sơ chưa áp dụng bảo vệ công thức

**Xác nhận từ mã.** [PeoplePage.tsx:130](D:/project/AI-Attendance-System/frontend/src/pages/PeoplePage.tsx:130) tự quote cell nhưng không trung hòa ký tự công thức, trong khi reports/grades đã dùng helper CSV. Trường text do người dùng nhập có thể bắt đầu `=`, `+`, `-`, `@`; quote CSV đơn thuần không chuyển nó thành text an toàn trong mọi spreadsheet.

**Hướng sửa:** dùng [csv.ts](D:/project/AI-Attendance-System/frontend/src/lib/csv.ts) chung cho mọi export và kiểm thử trên phần mềm bảng tính mục tiêu, cả khi lưu/mở lại; helper hiện tại chưa phải bảo đảm an toàn cho mọi ứng dụng. Import đang dùng `split(',')`, cần parser hỗ trợ quoted comma/newline; không được âm thầm bỏ dòng lỗi. Nguồn về formula injection và giới hạn các cách escape: [OWASP](https://community.owasp.org/attacks/CSV_Injection).

### F15 — P2: Dữ liệu bị giới hạn nhưng chưa có phân trang đầy đủ

**Xác nhận từ mã.** Grade load tối đa 2.000 persons, 2.000 sessions, 50.000 attendance; CSV lấy 10.000 bản ghi rồi mới lọc department; records UI lấy 500 và phân trang client; student portal chỉ trả 100 dòng chi tiết; sessions API tối đa 200. Ở quy mô lớn, có thể thiếu kết quả hoặc sai mẫu số mà client không nhận biết.

**Hướng sửa:** phân trang server/cursor và total/has_more; filter trước limit; aggregation cho thống kê; export streaming theo cursor và báo rõ phạm vi. Giới hạn trình bày heatmap 14 ngày/50 người đã được UI nói rõ, nên khác với cắt âm thầm trong tính điểm.

### F16 — P2: Cache, metrics và health chưa phản ánh sẵn sàng thực

**Đã chạy health; đối chiếu lời gọi trong mã.** `_matrix_cache` chưa được dùng; `record_inference_duration`/`set_enrolled_subjects` có định nghĩa nhưng không có call site từ pipeline. `prometheus_client` không nằm trong requirements; fallback không phát histogram bucket mà Grafana đang query. Counter rejected chưa được tăng ở nhánh spoof. `/health` luôn healthy dù DB/model chưa sẵn sàng.

**Hướng sửa:** cache có invalidation thật, đo duration đúng đường xử lý, kết nối gauge/counter, thêm dependency nếu dùng histogram, tách liveness và readiness. Không dùng dashboard giám sát đang rỗng làm bằng chứng SLA.

### F17 — P2: Audit và quản lý vòng đời dữ liệu chưa đầy đủ

**Xác nhận từ mã; cấu hình cloud chưa kiểm tra.** Audit hiện có insert thông thường, không thấy cơ chế chống sửa/xóa bất biến; chỉ được gọi rõ ở HTTP mark mới. Đổi điểm, manual attendance, xóa/đổi profile, liên kết SSO và thay quyền chưa có audit tương đương. Delete face không xóa ảnh Blob; chưa thấy retention job, ghi nhận consent hoặc yêu cầu xóa dữ liệu hoàn chỉnh.

**Hướng sửa:** audit cho các thay đổi ảnh hưởng học vụ/định danh, lưu before/after và actor thật, bảo vệ quyền ghi/xóa log; thiết kế vòng đời embeddings/ảnh/backups. Chưa thể xác nhận các tuyên bố tuân thủ hoặc “immutable” chỉ từ tài liệu hiện có.

### F18 — P2: Lỗi ở một số panel sinh viên bị biến thành dữ liệu trống

**Xác nhận từ mã.** [StudentPortalPage.tsx:149](D:/project/AI-Attendance-System/frontend/src/pages/StudentPortalPage.tsx:149) dùng `.catch(() => null/[])` ở grade, leaves, announcement, courses. Khi backend lỗi, người dùng có thể nhìn thấy trạng thái không có dữ liệu thay vì biết dữ liệu chưa tải được.

**Hướng sửa:** để `useResource` giữ lỗi, thêm thông báo và retry; không đổi lỗi mạng thành “chưa có điểm/chưa có đơn”. JWT localStorage và VITE_API_KEY fallback cũng cần được xem xét trong thiết kế bảo mật trình duyệt: không đặt khóa chung nhạy cảm trong bundle công khai.

### F19 — P2: Đóng phiên/sửa điểm danh có thể làm mất tính truy vết

**Xác nhận từ mã.** Đóng phiên cập nhật is_active trước rồi mới ghi absences, nuốt mọi exception. Một thao tác có thể báo thành công khi chưa hoàn tất phần dữ liệu đi kèm; đóng lại thì bị từ chối. Manual update đổi luôn `marked_at` và không có lịch sử sửa riêng.

**Hướng sửa:** close workflow idempotent và quan sát được, bulk/transaction theo khả năng DB; phân biệt `checked_in_at`, `updated_at`, `updated_by`, lý do điều chỉnh. Kiểm thử race close-vs-mark và lỗi DB giữa chừng.

### F20 — P2/P3: Tài liệu, CLI và quy trình phát hành còn lệch

**Đã chạy CLI, các điểm khác xác nhận từ mã.** Lệnh `python scripts/create_user.py --help` từ backend trả `ModuleNotFoundError: core`. README/wiki có endpoint `/api/auth/token` không tồn tại, quyền cũ, React 19, số test cũ, Docker multi-stage trong khi Dockerfile chỉ một stage, claim package tích hợp/cache/telemetry chưa đúng.

Workflow publish chạy khi push `main`, không dựa trên release thủ công; `npm publish ... || echo` có thể che lỗi thật. `.changeset` có cấu hình nhưng root chưa có CLI/scripts phát hành tương ứng. Packages CI dùng `npm install` thay vì `npm ci`; chưa có CI riêng cho Python package. Trong môi trường hiện tại, lệnh `npx --no-install typescript --version` trả 7.0.2, nên **không** kết luận lệnh TypeScript trong workflow đang lỗi chỉ dựa vào cú pháp.

**Hướng sửa:** sửa entrypoint CLI/hướng dẫn, sinh API docs từ nguồn thật, xác định một quy trình version/release có kiểm soát và không nuốt lỗi publish. Người thực hiện báo cáo không chạy workflow hay publish.

## 12. Bảo mật: điểm đã làm tốt và phần cần bổ sung

Các biện pháp đã có bằng chứng tốt trong mã/tests:

- JWT có kiểm tra chữ ký, hạn và các claim bắt buộc; production yêu cầu secret đủ dài.
- Xác thực lại user từ DB và thu hồi phiên bằng auth_version.
- RBAC backend, không chỉ ẩn nút frontend.
- So sánh API key constant-time và hỗ trợ xoay vòng nhiều key.
- Google/Microsoft xác minh token với nhà cung cấp; Microsoft có single-use nonce.
- Ảnh được kiểm tra nội dung, dung lượng và kích thước; không chỉ tin MIME.
- Rate limit inference/SSO/WebSocket; WebSocket không đặt credential vào URL.
- Unique attendance và xử lý DuplicateKeyError.
- CORS literal wildcard bị từ chối; các header chống MIME sniff/frame đã có.
- `.env` không được Git track tại thời điểm kiểm tra.
- CSV ở reports/grades và backend export đã có bước xử lý chuỗi công thức.

Còn thiếu/không xác nhận được: phạm vi lớp, auth login throttling, activation/password reset, audit đầy đủ, retention, backup thật, encryption-at-rest trên cloud, CSP phía hosting, giới hạn tổng request body ở proxy, quyền DB tối thiểu, xử lý khi hệ thống định danh cloud lỗi. Không kết luận có XSS thực tế chỉ vì dùng localStorage; đây là bề mặt hậu quả cần quản lý nếu XSS xuất hiện.

Không thấy bộ đo coverage nên **không có cơ sở công bố phần trăm test coverage**. Bộ test hiện mạnh hơn ở auth/validation/idempotency và yếu hơn ở self-enroll, Google account linking, đóng phiên, dashboard, SDK thực và lỗi nhiều bước trong MongoDB thật.

## 13. Triển khai, vận hành và khôi phục

Backend image hiện dùng Python 3.11 slim, cài system libraries, pip requirements, tải model lúc build và Uvicorn một worker. Chưa có user non-root, Docker HEALTHCHECK hay docker-compose trong repository. Một worker có thể phù hợp demo nhưng không chứng minh đủ năng lực nhiều lớp quét đồng thời.

Có ba cơ chế ping: frontend mỗi 4 phút khi tab hiển thị, backend Render mỗi 8 phút, GitHub workflow mỗi 10 phút. Chúng không thay thế readiness, alert, autoscaling hoặc SLA; trạng thái dịch vụ trả healthy không chứng minh DB/AI sẵn sàng.

Runbook backup/restore và secret rotation đã tồn tại. Checklist rotation còn trống trong file, không có nghĩa chắc chắn chưa làm ngoài hệ thống; cần người vận hành cung cấp bằng chứng. Runbook chỉ tập trung các collection cũ, chưa bao phủ đầy đủ grades/courses/leaves/announcements và hành vi tái đăng ký mới.

Các cấu hình cần xác minh ở môi trường chạy thật, không ghi giá trị secret vào báo cáo:

| Nhóm | Biến |
|---|---|
| Môi trường/JWT | `APP_ENV`, `JWT_SECRET`, `JWT_EXPIRY_HOURS` |
| DB | `MONGODB_URL`, `MONGODB_DB_NAME` |
| API key tùy chọn | `API_KEY_ADMIN`, `API_KEY_OPERATOR`, `API_KEY` legacy |
| Origin | `ALLOWED_ORIGINS` và allowlist WS |
| Google | `GOOGLE_CLIENT_ID`; code có giá trị mặc định, `.env.example` backend chưa mô tả |
| Microsoft | `MICROSOFT_CLIENT_ID`, `MICROSOFT_TENANT_ID` |
| AI | `MIN_CONFIDENCE`, `DUPLICATE_THRESHOLD`; cần giải quyết việc query override |
| Blob | `AZURE_STORAGE_CONNECTION_STRING`, `AZURE_BLOB_CONTAINER` |
| Bootstrap | `DEFAULT_ADMIN_USERNAME`, `DEFAULT_ADMIN_PASSWORD` |
| Frontend | `VITE_API_URL`; tránh dùng secret chung trong `VITE_API_KEY` của bản public |

## 14. Hướng dẫn chạy và kiểm tra tại máy

Các lệnh dưới đây là hướng dẫn; phần chạy ứng dụng thật sẽ đọc cấu hình DB của môi trường. Không chạy migration/seed vào DB thật nếu chưa xác định rõ đích.

Backend hiện có virtualenv Python 3.11:

```powershell
Set-Location D:/project/AI-Attendance-System/backend
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Frontend, sau khi đặt `VITE_API_URL` phù hợp:

```powershell
Set-Location D:/project/AI-Attendance-System/frontend
npm ci
npm run dev
```

Bộ kiểm tra backend dùng cấu hình thử nghiệm:

```powershell
Set-Location D:/project/AI-Attendance-System/backend
$env:MONGODB_URL = 'mongodb://127.0.0.1:27017/attendance_audit_test'
$env:MONGODB_DB_NAME = 'attendance_audit_test'
$env:APP_ENV = 'test'
.\.venv\Scripts\python.exe -m pytest -q
```

Frontend và libraries:

```powershell
Set-Location D:/project/AI-Attendance-System/frontend
npm test
npm run build
Set-Location D:/project/AI-Attendance-System
npm run typecheck
npm run build
npm test
```

Các probe audit có thể chạy lại, không kết nối DB/model thật:

```powershell
Set-Location D:/project/AI-Attendance-System
.\backend\.venv\Scripts\python.exe docs/reports/2026-10-27/verify_audit.py
```

Script audit ghi kết quả JSON trong cùng thư mục và sử dụng ngày hệ thống cho phép thử cập nhật ảnh. Khi tái chạy ở thời điểm khác cần đọc kết quả cùng snapshot mã; đây không phải test suite được tích hợp CI.

## 15. Lộ trình khắc phục đề xuất

| Giai đoạn | Công việc | Tiêu chí hoàn thành |
|---|---|---|
| 1 — Sửa luồng hỏng và danh tính | F01/F02/F04/F05; kiểm tra email fallback, bỏ admin email cố định, tách face_updated_at | Self-enroll chạy đúng ownership; chụp lại không đổi lịch sử; tài khoản mới không dùng mật khẩu chung; test hồi quy đạt |
| 2 — Bảo đảm số liệu | F03/F08/F10/F11/F19; chốt mô hình lớp học phần và policy attended/late/excused | Hai môn/học kỳ độc lập; dashboard không vượt 100% khi biểu diễn tỷ lệ người; ghi và báo cáo dùng cùng roster; phục hồi thao tác nhiều bước |
| 3 — Xác thực AI | F06/F07; khóa sàn server; bỏ fail-open; tập validation và PAD | Có số đo FAR/FRR và lỗi chống giả mạo trên camera mục tiêu; độ trễ p50/p95; tài liệu giới hạn rõ |
| 4 — Tích hợp và vận hành | F09/F12–F18/F20; contract tests, Docker, metrics, pagination, CSV, tài liệu | SDK smoke với backend thật; image không chứa env/venv; readiness phản ánh DB/model; export đủ dữ liệu; báo lỗi đúng |
| 5 — Nghiệm thu staging | Dữ liệu phi production, OAuth, camera, concurrency, backup restore | Checklist nghiệp vụ được chủ hệ thống chấp thuận, có log bằng chứng và kế hoạch rollback |

Không ước lượng ngày công cố định khi chưa chốt quy mô lớp, số người quét đồng thời, chính sách chuyên cần, yêu cầu SSO, thời hạn giữ sinh trắc và mô hình học phần. Sửa một vài dòng để test xanh không thay thế việc giải quyết các quan hệ dữ liệu còn thiếu.

### Bộ tình huống nghiệm thu cần có

1. Admin/operator/student đăng nhập, bị khóa, đổi quyền, đổi mật khẩu, token cũ và WebSocket đang mở.
2. Self-enroll mới, chụp lại, trùng MSSV, trùng tên khác người, email không thuộc tài khoản và ảnh chứa nhiều người.
3. Sinh viên đổi lớp/học kỳ nhưng giữ đúng lịch sử; hai môn cùng lớp có chuyên cần/điểm riêng.
4. Nhiều người điểm danh đồng thời; cùng người gửi lại; đóng phiên trùng lúc quét; DB lỗi giữa thao tác.
5. Đi muộn, có phép, vắng thủ công; đơn nghỉ có/không session; duyệt đồng thời và lỗi cập nhật attendance.
6. Dataset lớn vượt các ngưỡng 2.000/10.000/50.000; xuất CSV có quoted comma/newline và ô bắt đầu công thức.
7. Ảnh in, màn hình điện thoại, video replay, thiếu sáng, kính/khẩu trang, người giống nhau; đo false acceptance/rejection.
8. Khôi phục bản sao DB/ảnh lên môi trường riêng; so khớp attendance/grades/person/embedding sau restore.

## 16. Tài liệu hiện tại cần chỉnh

| Tài liệu/khẳng định | Kết quả đối chiếu |
|---|---|
| README React 19 | Manifest/lockfile là React 18.3.1 |
| README nhận diện `<300ms` | Chưa có benchmark chứng minh; smoke máy local không đạt mốc này ở ảnh trống |
| Wiki API `/api/auth/token` | Endpoint thực là `/api/auth/login` |
| Wiki nhiều API chỉ admin | Thực tế operator được dùng nhiều chức năng hơn |
| Backend README 63 tests | Lần chạy này 170 backend tests |
| Backend README Docker multi-stage | Dockerfile đang một stage |
| Wiki package quality/domain/matching đã tích hợp app | Chưa có import tương ứng trong ứng dụng |
| Tuyên bố cache/telemetry đầy đủ | Cache chưa dùng, nhiều metric chưa có call site |
| Wiki một mặt/enrollment | Backend chọn mặt lớn nhất khi nhiều mặt |
| Claim embedding tuyệt đối không thể suy ngược/tuân thủ đầy đủ | Chưa có chứng cứ đánh giá trong repo; cần bỏ khẳng định tuyệt đối và mô tả giới hạn |
| Runbook mất encodings luôn tạo ID mới | Enroll hiện hỗ trợ cập nhật ID cũ theo tên; hướng dẫn cần sửa |
| Secret rotation đã được giải quyết | File chỉ là checklist; chưa xác minh vận hành |

Wiki có các cặp tệp tên `and` và `&`, làm tăng nguy cơ hai phiên bản hướng dẫn lệch nhau. Nên giữ một nguồn nội dung và một bộ tài liệu được sinh/kiểm tra cùng API.

## 17. Hồ sơ bàn giao và kết luận sử dụng

| Tệp | Nội dung |
|---|---|
| [Báo cáo này](D:/project/AI-Attendance-System/docs/reports/2026-10-27/BAO_CAO_TOAN_DIEN.md) | Toàn bộ phân tích sản phẩm/kỹ thuật, 20 nhóm phát hiện và lộ trình |
| [API_INVENTORY.md](D:/project/AI-Attendance-System/docs/reports/2026-10-27/API_INVENTORY.md) | 52 HTTP operations và 1 WebSocket, quyền/rate limit/vị trí mã |
| [verification.json](D:/project/AI-Attendance-System/docs/reports/2026-10-27/verification.json) | Kết quả tái hiện lỗi và danh mục OpenAPI |
| [RUN_RESULTS.json](D:/project/AI-Attendance-System/docs/reports/2026-10-27/RUN_RESULTS.json) | Tổng hợp kết quả lệnh đã quan sát và SHA-256 mã nguồn để nhận diện snapshot được đánh giá |
| [verify_audit.py](D:/project/AI-Attendance-System/docs/reports/2026-10-27/verify_audit.py) | Mã tái hiện dùng synthetic data, không ghi DB thật |
| [frontend-npm-audit.json](D:/project/AI-Attendance-System/docs/reports/2026-10-27/frontend-npm-audit.json) | Kết quả dependency audit frontend |
| [backend-pip-audit.json](D:/project/AI-Attendance-System/docs/reports/2026-10-27/backend-pip-audit.json) | Kết quả dependency audit 86 package Python |
| [packages-tests.txt](D:/project/AI-Attendance-System/docs/reports/2026-10-27/packages-tests.txt) | Log 31 package tests sau build |
| [ui-smoke.json](D:/project/AI-Attendance-System/docs/reports/2026-10-27/ui-smoke.json) | Snapshot tóm tắt 7 màn hình kiểm tra theo vòng lặp; dashboard/học vụ/reports đã kiểm tra riêng |
| [Ảnh kiểm chứng học vụ](D:/project/AI-Attendance-System/docs/reports/2026-10-27/ui-academic-preview.png) | Ảnh chụp browser thật, dữ liệu mẫu |

**Khuyến nghị sử dụng hiện tại:** phù hợp làm nền tảng phát triển/demo có giải thích rõ giới hạn. Cần sửa các lỗi luồng và số liệu trước pilot có người dùng thật; cần thêm nghiệm thu định danh, sinh trắc, dữ liệu lịch sử và vận hành trước dùng làm hệ thống học vụ chính thức. Những cảnh báo dự thi trong giao diện chưa nên được coi là quyết định cuối cùng khi mô hình học phần và các sai lệch lịch sử chưa được xử lý.

Đợt đánh giá này chỉ bổ sung báo cáo/bằng chứng và chạy kiểm tra/build. Không sửa mã nghiệp vụ, không thay đổi dữ liệu production, không commit/push/deploy/publish.
