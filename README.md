# EduFace — Điểm danh và quản lý học vụ

EduFace hỗ trợ hồ sơ sinh viên, đăng ký khuôn mặt, phiên điểm danh, sổ điểm theo học phần, đơn nghỉ phép và báo cáo chuyên cần. Tác giả dự án: [maitamdev](https://github.com/maitamdev).

Bản cập nhật ngày 27/10/2026 đã được push lên `main` và triển khai trên Vercel/Render theo yêu cầu chủ dự án. Đã kiểm tra health, CORS, cấu hình Google và API TOEIC trên production; xem [báo cáo triển khai](docs/reports/2026-10-27/DEPLOYMENT.md), [báo cáo khắc phục](docs/reports/2026-10-27/BAO_CAO_KHAC_PHUC.md) và [hướng dẫn nâng cấp](docs/UPGRADE_2026_10.md). Các package chưa phát hành lên registry.

## TOEIC cùng DHV

Tab `/toeic` dành cho mọi tài khoản đã đăng nhập: lộ trình 56 buổi, 27 bài, 727 câu có giải thích tiếng Việt, 38 chuyên đề ôn dạng bài, 200 thẻ từ FSRS và 188 đoạn audio có sẵn. Mục Luyện tập gồm ôn theo dạng, 8 mã đề cố định (2 toàn phần, 4 mini, 1 Listening, 1 Reading), sổ câu sai từ 50 lượt nộp gần nhất và luyện từng Part. Có lưu bài đang làm, chấm điểm phía server và tiến độ riêng. Audio điều khiển thủ công, kết quả không quy đổi điểm TOEIC chính thức.

459 câu bổ sung gồm 399 câu MIT đã chọn lọc/chuyển thể từ TOEIC Question Ocean và 60 câu DHV mới. Học liệu nằm ở `backend/data/toeic/course.json`, các mã đề ở `backend/data/toeic/exam-forms.json`, media ở `frontend/public/toeic/`. Không cần API AI hoặc seed học liệu vào MongoDB. Xem [hướng dẫn ôn tập, nguồn và cách tái tạo](docs/toeic/MO_RONG_ON_TAP.md), [sổ tay 38 dạng bài](docs/toeic/SO_TAY_DANG_BAI.md) và [thông báo giấy phép](docs/toeic/CONTENT_LICENSES.md).

Xem [hướng dẫn chạy và mở rộng](docs/toeic/README.md), [nguồn tham khảo và khóa học](docs/toeic/SOURCES.md), [báo cáo bàn giao](docs/toeic/BAO_CAO.md). Đây là học liệu luyện tập tự biên soạn, không phải đề ETS hoặc cam kết đạt 900; audio tổng hợp và hình minh họa được ghi rõ trong ứng dụng.

## Công nghệ và phạm vi

- Frontend: React 18, TypeScript, Vite 8; giao diện Việt/Anh, sáng/tối.
- Backend: Python 3.11, FastAPI, Motor/PyMongo, JWT và API key theo vai trò.
- Dữ liệu: MongoDB replica set hoặc Atlas. Các luồng ghi nhiều collection dùng transaction, commit trước khi trả thành công.
- AI: InsightFace `buffalo_sc`, ONNX Runtime, OpenCV; embedding 512 chiều và cosine similarity. Không có số liệu accuracy/FAR/FRR trên tập camera mục tiêu trong lần bàn giao này.
- Ảnh gốc trên Azure Blob là tùy chọn, mặc định tắt; embedding vẫn cần cho nhận diện.

## Vai trò

| Vai trò | Phạm vi |
|---|---|
| Admin | Quản trị tài khoản, đăng ký/xóa hồ sơ và toàn bộ vận hành |
| Operator | Nhân viên vận hành toàn hệ thống; chưa phải vai trò giảng viên bị giới hạn theo lớp được phân công |
| Student | Chỉ truy cập hồ sơ/học vụ được liên kết bằng `users.person_id`; không suy ra quyền từ email liên hệ |

Google dùng `GOOGLE_CLIENT_ID`; riêng dịch vụ DHV trên Render giữ cấu hình OAuth công khai hiện có trong `backend/data/deployment-public.json`, chỉ áp dụng khi hostname do Render cấp khớp chính xác. Biến môi trường được ưu tiên, giá trị rỗng tắt Google. Tài khoản mới có vai trò student; quyền trên tài khoản đã tồn tại chỉ được nhận qua liên kết Google do admin thiết lập. Mật khẩu tài khoản tạo mới tối thiểu 12 ký tự. CSV nhập sinh viên cấp mật khẩu ngẫu nhiên riêng cho từng người; người vận hành tải thông tin cấp tài khoản một lần.

## Chạy cục bộ

Cần Python 3.11, Node.js đáp ứng Vite 8 và MongoDB replica set/Atlas. Xem hướng dẫn nâng cấp trước khi mở một DB đã có dữ liệu.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
Copy-Item .env.example .env
# Điền MONGODB_URL, MONGODB_DB_NAME, JWT_SECRET, DEFAULT_ADMIN_PASSWORD,
# API_KEY_ADMIN/API_KEY_OPERATOR nếu dùng tích hợp, và ALLOWED_ORIGINS.
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Ở terminal khác:

```powershell
cd frontend
npm ci
$env:VITE_API_URL='http://localhost:8000'
npm run dev
```

`/live` kiểm tra tiến trình; `/health` chỉ trả 200 khi MongoDB và mô hình đã sẵn sàng. Lần đầu cần tải model. Trong production, đặt secret riêng, origin chính xác và không bật `SEED_DEMO_ACCOUNTS`. Không đưa API key quản trị vào bundle frontend; bản production bỏ qua `VITE_API_KEY`.

## Quy tắc dữ liệu

- MSSV là định danh duy nhất trong hồ sơ đang hoạt động; trùng họ tên được phép.
- Chụp lại cập nhật `face_updated_at`, giữ `enrolled_at` và hồ sơ giáo vụ đã liên kết.
- Phiên mới chụp danh sách `roster_ids` khi tạo; chuyển lớp sau đó không đổi lịch sử phiên này.
- Điểm lưu theo `(person_id, course_id)`; học phần có lớp và học kỳ. Điểm cũ chưa xác định học phần chỉ xem, không tự chuyển sang một môn giả định.
- `present`, `late`, `excused` tính là đã tham dự. Phiên chưa đóng và chưa có bản ghi chưa tính là vắng.
- Dashboard đếm số sinh viên hoạt động có mặt trong ngày, không đếm lặp một người qua nhiều phiên.
- Quét để ghi điểm danh cần hai frame và các kiểm tra ảnh/chuyển động. Đây là heuristic, chưa phải PAD được kiểm định.
- Cosine là độ tương đồng, không phải xác suất nhận đúng. Không có cam kết tốc độ <300ms hoặc độ chính xác cố định.

## Kiểm thử và tích hợp

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
# Để chạy cả kiểm thử transaction trên DB thử localhost riêng:
$env:MONGODB_INTEGRATION_URI='mongodb://127.0.0.1:27028/?replicaSet=eduface-test'
.\.venv\Scripts\python.exe -m pytest -q
```

Các ca integration tạo DB tên ngẫu nhiên `eduface_integration_*` và chỉ xóa DB đó. AI được mock trong bộ transaction; smoke SDK riêng đã gọi model thật bằng ảnh trống, không đánh giá độ chính xác nhận người.

```powershell
cd frontend
npm test
npm run build
# Tại thư mục gốc
npm ci
npm run typecheck
npm run build
npm test
```

SDK: [hướng dẫn client](packages/smartattend-client/README.md). API chính xác theo `/docs`/`/openapi.json` của backend đang chạy. Công cụ `backend/scripts/evaluate_similarity.py` tính FAR/FRR và p50/p95 từ CSV đã gán nhãn; không thay thế việc thu thập validation độc lập.

## Vận hành và giới hạn

Docker chạy tài khoản không phải root, loại `.env`/venv khỏi build context, readiness theo `PORT`. Chưa build Docker/Linux trong lần kiểm tra Windows này. CI đã bổ sung kiểm thử MongoDB transaction và package Python, nhưng chưa có kết quả GitHub Actions từ các thay đổi chưa push.

Audit ghi actor/action và một số giá trị trước/sau; chưa phải kho log bất biến. Xóa hồ sơ loại embedding trong transaction, giữ lịch sử học vụ và đưa ảnh Blob vào hàng đợi xóa có retry. Backup, versioning/soft-delete của cloud cần chính sách lưu giữ riêng.

Giấy phép mã nguồn không đồng nghĩa giấy phép trọng số mô hình. Kiểm tra [điều kiện sử dụng mô hình InsightFace](https://github.com/deepinsight/insightface#license) trước sử dụng ngoài phạm vi được cấp phép. Cần nghiệm thu với camera thật, dữ liệu được đồng ý sử dụng, OAuth tenant và Blob Storage của đơn vị trước triển khai.
