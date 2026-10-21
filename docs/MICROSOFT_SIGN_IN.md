# Đăng nhập Microsoft cho trường / công ty

Đã tích hợp đăng nhập một tổ chức (single tenant) bằng MSAL, Authorization Code + PKCE. Microsoft xác thực danh tính; EduFace giữ vai trò Admin / Operator / Student và hồ sơ sinh viên hiện có. Chức năng này chưa đồng bộ dữ liệu Microsoft 365, Teams, Outlook hay OneDrive.

## Cấu hình lần đầu

1. Trong Microsoft Entra admin center → App registrations → New registration, chọn **Accounts in this organizational directory only**. Người cấu hình cần quyền tạo ứng dụng trong tenant của trường/công ty.
2. Trong Authentication, thêm nền tảng **Single-page application (SPA)** với redirect URI chính xác:
   - `http://localhost:5173/microsoft-redirect.html` nếu truy cập bằng localhost.
   - `http://127.0.0.1:5173/microsoft-redirect.html` nếu truy cập bằng địa chỉ này.
   - `https://TEN-MIEN-THAT/microsoft-redirect.html` khi triển khai.
3. Không bật implicit grant và không tạo client secret cho frontend. Luồng đăng nhập chỉ yêu cầu `openid`, `profile`, không sử dụng quyền Microsoft Graph. Nếu app registration tự thêm `User.Read`, chức năng này không cần quyền đó.
4. Sao chép **Application (client) ID** và **Directory (tenant) ID** từ Overview vào `backend/.env`:

   ```dotenv
   MICROSOFT_CLIENT_ID=GUID_CUA_UNG_DUNG
   MICROSOFT_TENANT_ID=GUID_CUA_TRUONG_HOAC_CONG_TY
   ```

5. Khởi động lại backend. MongoDB phải hoạt động để tạo index và lưu challenge đăng nhập. Frontend đọc cấu hình từ API, không cần nhập ID vào mã nguồn.
6. Đăng nhập bằng tài khoản Admin EduFace → **Tài khoản & Hệ thống → Đăng nhập Microsoft**. Liên kết một tài khoản EduFace có sẵn với **Object ID của người dùng** trong Entra → Users → người dùng → Overview. Đây không phải Client ID, email hay mã sinh viên. Khi tạo tài khoản Student, liên kết thêm hồ sơ sinh viên tại biểu mẫu tạo tài khoản.
7. Thử đăng nhập Microsoft bằng người dùng đã liên kết. Tài khoản chưa liên kết bị từ chối; người dùng không được tự tạo tài khoản hoặc tự nâng quyền. Chính sách tenant, MFA và user assignment vẫn có thể yêu cầu quản trị viên xử lý.

## Vận hành

- Thiếu/sai định dạng hai ID: nút Microsoft bị vô hiệu hóa và hiển thị trạng thái chưa cấu hình; đăng nhập EduFace vẫn hoạt động.
- Backend kiểm tra chữ ký RSA, issuer, audience, tenant, thời hạn, Object ID và nonce. Challenge dùng một lần, hết hạn sau 10 phút; index TTL dọn bản ghi cũ.
- Không ghép tài khoản theo email/tên. Vai trò lấy từ tài khoản EduFace được quản trị viên liên kết.
- Đăng xuất EduFace xóa phiên ứng dụng cục bộ; không đăng xuất toàn bộ Microsoft Office trên thiết bị. Lần đăng nhập tiếp theo hiển thị chọn tài khoản.
- MSAL 5 dùng trang bridge riêng `microsoft-redirect.html`. Vite đã cấu hình build cả trang này. Hosting phải phục vụ đúng HTML đó trước quy tắc SPA fallback; Vercel đã có rewrite riêng. Không thêm header `Cross-Origin-Opener-Policy` cho trang bridge.
- Production phải dùng HTTPS và `APP_ENV=production` cùng `JWT_SECRET` ngẫu nhiên tối thiểu 32 ký tự. Cấu hình CORS đúng origin frontend.

## Kiểm tra trước khi sử dụng thật

Đăng nhập tài khoản đã liên kết của từng vai trò; kiểm tra sai tenant, tài khoản chưa liên kết, người dùng bị khóa, MFA, quay lại trang đích và đăng nhập lại sau đăng xuất. Bộ kiểm thử tự động dùng khóa RSA và database giả, không thay thế kiểm thử trên tenant thật. Chưa có Tenant ID / Client ID thật trong phiên làm việc này nên chưa xác nhận đăng nhập Microsoft thực tế.

Tài liệu chính thức: [Authorization Code + PKCE](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-auth-code-flow), [kiểm tra claims](https://learn.microsoft.com/en-us/entra/identity-platform/claims-validation), [MSAL redirect bridge](https://learn.microsoft.com/en-us/entra/msal/javascript/browser/redirect-bridge).
