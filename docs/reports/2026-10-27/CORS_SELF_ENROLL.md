# Lỗi CORS khi sinh viên tự đăng ký — 27/10/2026

Trạng thái lúc lập báo cáo: đã sửa và kiểm thử mã nguồn local, chưa push/deploy. **Cập nhật sau khi được chủ dự án cho phép:** đã triển khai và kiểm tra CORS trên production ngày 27/10/2026; xem [báo cáo triển khai](DEPLOYMENT.md). Các mô tả điều tra bên dưới ghi lại trạng thái trước triển khai.

## Kết quả kiểm tra hệ thống đang chạy

Kiểm tra bằng HTTP GET/OPTIONS, không gửi tài khoản, token hoặc ảnh sinh viên:

| Yêu cầu tới `https://eduface-system.onrender.com` | Kết quả quan sát |
| --- | --- |
| `OPTIONS /api/persons/self-enroll`, Origin `https://www.dhv-edu.tech`, method POST, headers authorization/content-type | 200; `Access-Control-Allow-Origin: https://www.dhv-edu.tech`; credentials true |
| Cùng preflight với Origin `https://dhv-edu.tech` | 200; cho phép đúng origin này |
| `GET /health` với Origin www | 200, `{"status":"healthy"}`; có CORS |
| `GET /live` với Origin www | 404; có CORS |
| `GET /openapi.json` | 200; chưa có `/api/toeic/catalog` |

Tại thời điểm kiểm tra, hai domain đã được cho phép. Thêm wildcard không giải quyết nguyên nhân đã tái hiện. Bản đang chạy chưa phản ánh toàn bộ mã nguồn hiện tại: local có `/live`, API TOEIC và thông tin readiness chi tiết hơn ở `/health`.

Thông báo trình duyệt chưa đủ xác định ngoại lệ của lần POST cụ thể. Cần log Render tương ứng để phân biệt lỗi ứng dụng 500 với lỗi gateway/timeout/process bị dừng. Header do ứng dụng bổ sung không thể sửa phản hồi 502/504 được proxy tạo ra khi yêu cầu không tới được ứng dụng.

## Lỗi đã tái hiện và bản sửa

1. Trước sửa, một route thử nghiệm ném ngoại lệ không được xử lý trả 500 dạng text, **không có `Access-Control-Allow-Origin` hoặc `X-Request-ID`**. Hai kiểm thử hồi quy thất bại đúng tại các header này.
2. `backend/core/http_app.py` đặt CORS bên ngoài toàn bộ middleware xử lý lỗi, giữ nguyên API của đối tượng FastAPI như `state`, `dependency_overrides`, OpenAPI và router. Cách đặt CORS ngoài bộ xử lý lỗi tuân theo [hướng dẫn chính thức Starlette](https://starlette.dev/middleware/#corsmiddleware-global-enforcement).
3. `backend/main.py` trả JSON 500 với thông báo chung và `request_id`, đồng thời ghi traceback vào log server. Không trả chi tiết nội bộ cho trình duyệt. Phản hồi database chưa sẵn sàng cũng nhận header bảo mật và `Cache-Control: no-store`.
4. `backend/core/logging_context.py` dùng middleware ASGI bao ngoài, duy trì mã yêu cầu cho cả preflight, lỗi startup và lỗi 500. Chỉ nhận mã do client cung cấp gồm chữ, số, dấu chấm/gạch ngang/gạch dưới, tối đa 64 ký tự; giá trị khác được thay bằng mã sinh mới.
5. `frontend/src/api/client.ts` hiển thị mã yêu cầu trong thông báo lỗi server để đối chiếu log. Không tự gửi lại yêu cầu ghi dữ liệu. Đã kiểm tra việc gửi consent, ảnh multipart và Authorization của self-enroll.
6. `backend/.env.example` minh họa rõ cả domain gốc và www. `ALLOWED_ORIGINS` được cấu hình sẽ thay danh sách mặc định; giữ các origin hợp lệ đang sử dụng khi cập nhật cấu hình. Không thay file `.env` thật trong lần sửa này.

Luồng self-enroll cũ trong HEAD truy cập `user.person_id`, trong khi `AuthenticatedUser` không có thuộc tính này. Bản local đã sửa từ đợt trước để đọc liên kết hồ sơ từ tài khoản trong DB; kiểm thử bảo toàn danh tính học vụ và ngăn nhận hồ sơ bằng email đã đạt. Đây là một nguyên nhân khả dĩ cho lỗi POST trên bản cũ, **chưa phải kết luận từ log production**.

## Kiểm chứng

| Kiểm tra | Kết quả |
| --- | --- |
| Toàn bộ backend, gồm integration với MongoDB replica set 8.0.34 trên localhost:27028 | 233 passed, không skip |
| Kiểm thử CORS mới | 11 passed: 500, 401, 409, 503, preflight www/apex, origin lạ, mã truy vết, lifespan và WebSocket |
| Toàn bộ frontend | 43 passed |
| `npm run build` gồm TypeScript và Vite production | Thành công |
| `git diff --check` các file đang sửa có tracking | Thành công |

Mongo integration chỉ tạo/xóa DB thử có tên ngẫu nhiên `eduface_integration_*` trên localhost. Nhận diện ảnh AI trong các kiểm thử được mock; chưa xác nhận một lần đăng ký ảnh thật trên production. Dịch vụ Mongo thử nghiệm được dừng sau kiểm tra.

Chạy lại backend từ thư mục `backend`, với môi trường thử riêng:

```powershell
$env:APP_ENV='test'
$env:MONGODB_URL='mongodb://127.0.0.1:27028/?replicaSet=eduface-test'
$env:MONGODB_INTEGRATION_URI=$env:MONGODB_URL
$env:JWT_SECRET='local-regression-only-not-production'
.\.venv\Scripts\python.exe -m pytest -q
```

Cần replica set thử đang chạy ở cổng trên. Frontend: chạy `npm test` và `npm run build` trong thư mục `frontend`.

## Đưa bản sửa lên hệ thống

Việc triển khai chưa được thực hiện, theo yêu cầu không tự push/deploy. Khi triển khai được cho phép:

1. Triển khai đúng bộ source đã kiểm thử, bao gồm module mới `core/http_app.py` và các file mới của những đợt nâng cấp trước; không chép riêng `main.py` vì file này có các import mới. Với DB hiện có, đọc [hướng dẫn nâng cấp trước đó](../../UPGRADE_2026_10.md).
2. Xác nhận allowlist chứa `https://www.dhv-edu.tech` và `https://dhv-edu.tech`, giữ các origin hợp lệ khác nếu còn dùng. Không cần thay thành wildcard.
3. Triển khai frontend tương ứng để gửi consent và hiển thị mã yêu cầu; không dùng frontend cũ thiếu consent với backend mới.
4. Kiểm tra `/live`, `/health` và preflight. Với một lần đăng ký được người dùng chủ động thực hiện, ghi lại status và mã yêu cầu nếu thất bại rồi đối chiếu log Render. Nếu phản hồi do gateway tạo và không có mã yêu cầu, kiểm tra log restart, giới hạn bộ nhớ, model khởi động và thời gian xử lý của instance.

Lệnh kiểm tra preflight, không làm thay đổi dữ liệu:

```powershell
curl.exe -i -X OPTIONS "https://eduface-system.onrender.com/api/persons/self-enroll" -H "Origin: https://www.dhv-edu.tech" -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: authorization,content-type"
```
