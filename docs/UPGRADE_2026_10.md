# Hướng dẫn nâng cấp dữ liệu và vận hành — 27/10/2026

## Phạm vi bàn giao

Chỉ thay đổi mã nguồn và chạy dữ liệu thử trên máy này. Không thay đổi DB cấu hình thật, không publish package, không deploy và không push. Bản sao các sửa đổi đã tồn tại trước khi sửa lỗi: `D:\project\AI-Attendance-System-before-fixes-20261027-002122`.

## Trước khi dùng DB hiện có

1. Sao lưu DB và kiểm tra có thể khôi phục. Dừng các instance đang ghi dữ liệu khi chạy migration.
2. Dùng MongoDB replica set/Atlas; standalone không hỗ trợ các transaction mới. Không tự thêm fallback ghi từng bước khi transaction lỗi.
3. Đặt `MONGODB_URL` rõ ràng và chọn đúng tên DB. Chạy dry-run:

```powershell
$env:MONGODB_URL='<URI của DB cần nâng cấp>'
python backend/scripts/migrate_integrity.py --database <ten_db>
```

Script không nạp `.env`, không in URI/mật khẩu. Nó chỉ báo ID các bản ghi trùng, điểm chưa gắn môn, phiên thiếu roster và index tên cũ. MSSV được so sánh sau trim/uppercase; attendance được so sánh sau chuẩn hóa session ObjectId. **Không tự gộp/xóa bản ghi trùng.** Phải đối chiếu hồ sơ nguồn để xử lý xung đột.

4. Sau khi hết xung đột và đã có backup:

```powershell
python backend/scripts/migrate_integrity.py --database <ten_db> --apply --backup-confirmed
```

Script chuẩn hóa MSSV/session ID trong transaction, tạo index định danh và bỏ index `name_unique_active` cũ. DDL chạy riêng, có thể chạy lại. Không gán học phần cho điểm cũ; không dựng roster quá khứ từ lớp hiện tại. Nếu dữ liệu lớn, thực hiện trên bản sao trước để đánh giá thời gian/giới hạn transaction.

5. Rà soát admin có `google_email` cũ, tài khoản demo và mật khẩu mặc định đã có trong DB. Việc ngừng tự tạo mới không xóa hay thu hồi tự động dữ liệu cũ. Công cụ `check_integrity.py` có thể báo các ID cần rà soát, nhưng mặc định đọc DB từ cấu hình; luôn đặt URI và tên DB thử rõ ràng khi nghiệm thu.
6. Khởi động backend, kiểm tra `/health`, đăng nhập và thử một luồng học phần/phiên/điểm trên dữ liệu thử trước mở lại ghi dữ liệu.

## Thay đổi hợp đồng API và hành vi

| Thay đổi | Cách cập nhật client |
|---|---|
| Enroll yêu cầu đồng ý dùng sinh trắc | Gửi multipart `consent=true` sau khi người dùng đồng ý |
| Chụp lại hồ sơ | Gửi `person_id` hoặc MSSV; không tìm danh tính theo họ tên |
| Ghi điểm danh | `POST /api/attendance/mark/{session_id}` với `frame` và `probe_frame` |
| Nhận diện không ghi | `POST /api/attendance/identify`, trường `frame` |
| Ngưỡng matching | Server luôn áp dụng sàn cấu hình; confidence là cosine thô được chặn trong 0..1 |
| Điểm | Gửi `course_id` cùng `person_id`; điểm cũ không có môn chỉ đọc |
| Bảng điểm sinh viên | `/api/academic/my-transcript`, GPA theo tín chỉ các môn đã nhập điểm |
| Phân trang | `/api/sessions` và `/api/attendance` có `offset`/`limit` |
| CSV đầy đủ | `/api/attendance/export/csv` stream cursor, không giới hạn 10.000 dòng |
| Đổi mật khẩu | `POST /api/auth/password`; trả JWT mới và vô hiệu JWT trước đó bằng auth_version |
| Trình duyệt | JWT ở sessionStorage, xóa bản localStorage cũ; cần đăng nhập lại sau đóng phiên trình duyệt |

SDK hiện tại có thay đổi phá vỡ tương thích kiểu dữ liệu cũ: bỏ vai trò/field không tồn tại, thêm consent/probe, sửa URL và response reports/heatmap. Các package **chưa đổi version hay publish**; cần quyết định version và release notes khi phát hành.

## Cấu hình cần đặt

- `JWT_SECRET`: secret riêng tối thiểu 32 ký tự trong production.
- `DEFAULT_ADMIN_PASSWORD`: tối thiểu 12 ký tự cho bootstrap mới; không ghi đè mật khẩu tài khoản đã có.
- `SEED_DEMO_ACCOUNTS=false`; production bỏ qua yêu cầu seed demo.
- `ALLOWED_ORIGINS`: danh sách origin đầy đủ, không wildcard và không chứa path; cấu hình này thay thế defaults cho HTTP và WebSocket.
- `GOOGLE_CLIENT_ID`: cấu hình riêng cho mỗi triển khai; đặt rõ giá trị rỗng để tắt Google. Riêng dịch vụ đang vận hành `eduface-system.onrender.com` giữ public Client ID đã sử dụng trước nâng cấp trong `backend/data/deployment-public.json`, đối chiếu `RENDER_EXTERNAL_HOSTNAME` do Render cấp. Biến môi trường luôn được ưu tiên; máy local, fork và dịch vụ khác không tự dùng Client ID này. Đây là định danh OAuth công khai, không phải client secret. Xem [biến môi trường Render](https://render.com/docs/environment-variables).
- Microsoft cần client/tenant do đơn vị cấu hình; chưa thử đăng nhập tenant thật trong lần sửa này.
- `STORE_ENROLLMENT_PHOTOS=false` mặc định. Khi bật, upload ảnh chạy sau commit, ghi photo_url nếu hồ sơ còn hoạt động; nếu đã xóa thì thêm công việc cleanup. Upload không có hàng đợi retry bền vững; thiếu ảnh không làm mất embedding/hồ sơ đã lưu.
- `AZURE_STORAGE_CONNECTION_STRING` và container chỉ cần khi lưu/xóa ảnh trên Blob. Worker retry xóa mỗi 60 giây, tối đa 50 job/lượt. Giám sát job pending/attempts; cloud soft-delete/versioning/backups cần policy riêng.

## Những gì chưa thể khẳng định

- Heuristic texture/motion hai frame chưa ngăn được mọi replay/deepfake. Chưa ràng buộc nguồn capture bằng camera đáng tin cậy/challenge server; cần đánh giá PAD riêng.
- Chưa có validation người thật cho FAR/FRR hoặc độ trễ dưới tải. `evaluate_similarity.py` chỉ là công cụ tính toán từ dữ liệu có nhãn.
- Operator vẫn là nhân viên toàn hệ thống. Không cấp vai trò này cho người chỉ được phép xem một lớp cho đến khi triển khai phân công lớp và kiểm thử đầy đủ.
- CORS/JWT/transaction không thay thế kiểm định độc lập, quản lý secret, quyền DB, backup/restore và quan trắc.
- UI nạp nhiều trang cho danh sách đầy đủ, nhưng vẫn giữ dữ liệu trên bộ nhớ client; báo cáo tổng hợp vẫn có thể tốn tài nguyên với DB rất lớn. CSV đã stream và không cắt âm thầm.
- Cache embedding hiện có TTL 5 giây trong mỗi tiến trình. Docker mặc định một worker; nhiều instance cần invalidation liên tiến trình nếu yêu cầu thay đổi có hiệu lực tức thì.
- Một số audit chạy sau thao tác chính và ghi lỗi nếu kho audit gặp sự cố; chưa bảo đảm log bất biến hoặc giao dịch audit với mọi thay đổi.

## Nghiệm thu trước triển khai

Kiểm tra migration trên bản sao, tài khoản và liên kết OAuth, người trùng tên/MSSV, chuyển lớp, hai môn khác học kỳ, quét đồng thời, đóng phiên, rollback khi DB lỗi, CSV lớn, model/camera mục tiêu và xóa ảnh cloud. Đối chiếu [báo cáo khắc phục](reports/2026-10-27/BAO_CAO_KHAC_PHUC.md) để xem phạm vi đã chạy thực tế.
