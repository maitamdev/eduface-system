# Triển khai production — 27/10/2026

Đã triển khai theo yêu cầu trực tiếp của chủ dự án: “deploy push hết lên đi”. Kiểm tra hoàn tất khoảng 08:03, múi giờ Asia/Bangkok (UTC+7).

## Mã nguồn và dịch vụ

- Repository: [maitamdev/eduface-system](https://github.com/maitamdev/eduface-system), nhánh `main`.
- [97af97b](https://github.com/maitamdev/eduface-system/commit/97af97bb59f572c007006ff0c414b715d56e08f4): 244 file, gồm nâng cấp điểm danh/học vụ, CORS, TOEIC, dữ liệu/audio, kiểm thử và tài liệu.
- [28f1d33](https://github.com/maitamdev/eduface-system/commit/28f1d33aec53bc8d8fd75db1543e14226615f594): khôi phục cấu hình đăng nhập Google cho đúng dịch vụ DHV.
- Frontend: [www.dhv-edu.tech](https://www.dhv-edu.tech), [Vercel deployment](https://vercel.com/tammai147258369-7911s-projects/face-dhv-edu/9tdX2zZRaN6sbN4CwA5pDGvqxXRJ), trạng thái thành công.
- Backend: [eduface-system.onrender.com](https://eduface-system.onrender.com), đã nhận mã mới qua tích hợp Git và vượt qua kiểm tra trực tiếp.

## Sự cố Google và cách xử lý

Bản nâng cấp đầu tiên bỏ Client ID Google mặc định trong code, nhưng Render chưa cấu hình `GOOGLE_CLIENT_ID`. API vì thế trả `enabled: false` và giao diện vô hiệu hóa nút Google. Đây là thiếu sót khi chuyển cấu hình trong lần triển khai này.

Đã chuyển public Client ID vốn được dịch vụ sử dụng trước nâng cấp sang `backend/data/deployment-public.json`. Cấu hình chỉ áp dụng khi `RENDER_EXTERNAL_HOSTNAME` khớp chính xác `eduface-system.onrender.com`; không dựa vào Host/Origin gửi bởi trình duyệt. Render cung cấp [biến môi trường này](https://render.com/docs/environment-variables) cho dịch vụ. `GOOGLE_CLIENT_ID` được đặt rõ sẽ luôn ghi đè; giá trị rỗng vẫn tắt Google. Local và các fork/dịch vụ khác phải cấu hình riêng.

Client ID OAuth là định danh công khai mà trình duyệt cần dùng; file này không chứa client secret, JWT secret, API key hoặc chuỗi kết nối DB.

## Kiểm tra production

| Kiểm tra | Kết quả |
| --- | --- |
| `GET /live` | 200, alive |
| `GET /health` | 200, healthy; database=true, model=true |
| `GET /api/auth/google/config` | 200, enabled=true, đúng Client ID đã dùng trước đó |
| Google exchange với token cố ý không hợp lệ | 401 với thông báo token không hợp lệ; giữ CORS, không còn lỗi thiếu cấu hình |
| CORS self-enroll với domain gốc và www | OPTIONS 200, trả đúng origin tương ứng |
| CORS với origin ngoài danh sách | OPTIONS 400, không cấp allow-origin |
| Mã truy vết | Có X-Request-ID; trình duyệt được phép đọc header này |
| Đăng nhập EduFace bằng thông tin quản trị đã cấu hình | 200; `/api/auth/me` trả đúng vai trò admin |
| TOEIC catalog bằng JWT vừa đăng nhập | 200, 20 bài học, 268 câu hỏi |
| Chi tiết bài học `f01` | 200 |
| Frontend JS, một WAV và một SVG production | HTTP 200, SHA-256 khớp file từ build local đã kiểm thử |

Việc trao đổi token Google hợp lệ bằng tài khoản cá nhân và thao tác chụp ảnh thật chưa được thực hiện thay người dùng. Cấu hình nút Google đã được xác minh trên production; người dùng đang giữ trang cũ cần tải lại trang để lấy cấu hình mới.

## Kiểm thử và CI

- Backend sau hotfix: [CI thành công](https://github.com/maitamdev/eduface-system/actions/runs/40429999895), 225 kiểm thử không cần DB thực đạt; 18 integration được chạy ở bước MongoDB riêng và đều đạt. Tổng cộng 243 kiểm thử khác nhau.
- Frontend: [CI thành công](https://github.com/maitamdev/eduface-system/actions/runs/40421475307), 43 kiểm thử, TypeScript và production build đạt. Hotfix Google không thay mã frontend.
- Packages: [CI thành công](https://github.com/maitamdev/eduface-system/actions/runs/40429999769).
- Kiểm tra dependency trên CI đạt. Trước push đã kiểm tra không có giá trị secret từ `.env` local lẫn vào các file trong repository.

## Dữ liệu

- Đã sao lưu 7 collection, 37 document cùng index tại `D:\project\eduface-db-backup-20261027-063940`, ngoài repository. Kiểm tra checksum và thử khôi phục dữ liệu/index vào MongoDB replica set riêng trên localhost thành công; DB phục hồi thử đã được xóa.
- Kiểm tra trước triển khai không có nhóm MSSV/tài khoản/môn/điểm/điểm danh trùng cản trở index mới. Không cần chuẩn hóa MSSV hoặc chuyển kiểu session ID của bản ghi hiện có.
- Backend đã tạo index mới, gồm index định danh và TOEIC. Đã bỏ `name_unique_active` sau đối chiếu định nghĩa với backup để cho phép các sinh viên khác nhau trùng họ tên. Hồ sơ trước/sau thao tác giống nhau; giữ index MSSV duy nhất.
- Không xóa hồ sơ, không tự gộp tài khoản, không dựng danh sách lớp lịch sử từ lớp hiện tại. Năm phiên cũ thiếu snapshot roster vẫn được giữ nguyên.
- Backup không được commit/upload. Không publish package npm/PyPI.
