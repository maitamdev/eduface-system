# Danh mục API thực tế — 27/10/2026

Trích từ decorator trong mã nguồn đang có trên máy; gồm 52 HTTP operations và 1 WebSocket. Swagger có 45 HTTP path khác nhau. `Public` nghĩa là không có dependency xác thực tại route.

| Method | Đường dẫn | Quyền tối thiểu | Rate limit khai báo | Mã nguồn |
|---|---|---|---|---|
| GET | `/` | Public | - | [main.py:210](D:/project/AI-Attendance-System/backend/main.py:210) |
| GET | `/api/academic/announcements` | Student/Operator/Admin | - | [academic.py:475](D:/project/AI-Attendance-System/backend/routers/academic.py:475) |
| POST | `/api/academic/announcements` | Operator/Admin | - | [academic.py:508](D:/project/AI-Attendance-System/backend/routers/academic.py:508) |
| DELETE | `/api/academic/announcements/{ann_id}` | Operator/Admin | - | [academic.py:538](D:/project/AI-Attendance-System/backend/routers/academic.py:538) |
| GET | `/api/academic/courses` | Student/Operator/Admin | - | [academic.py:217](D:/project/AI-Attendance-System/backend/routers/academic.py:217) |
| POST | `/api/academic/courses` | Operator/Admin | - | [academic.py:247](D:/project/AI-Attendance-System/backend/routers/academic.py:247) |
| DELETE | `/api/academic/courses/{course_id}` | Operator/Admin | - | [academic.py:270](D:/project/AI-Attendance-System/backend/routers/academic.py:270) |
| GET | `/api/academic/grades` | Operator/Admin | - | [academic.py:281](D:/project/AI-Attendance-System/backend/routers/academic.py:281) |
| PUT | `/api/academic/grades` | Operator/Admin | - | [academic.py:307](D:/project/AI-Attendance-System/backend/routers/academic.py:307) |
| POST | `/api/academic/import-students` | Operator/Admin | - | [academic.py:549](D:/project/AI-Attendance-System/backend/routers/academic.py:549) |
| GET | `/api/academic/leaves` | Student/Operator/Admin | - | [academic.py:334](D:/project/AI-Attendance-System/backend/routers/academic.py:334) |
| POST | `/api/academic/leaves` | Student/Operator/Admin | - | [academic.py:369](D:/project/AI-Attendance-System/backend/routers/academic.py:369) |
| PATCH | `/api/academic/leaves/{leave_id}` | Operator/Admin | - | [academic.py:423](D:/project/AI-Attendance-System/backend/routers/academic.py:423) |
| GET | `/api/academic/my-grade` | Student/Operator/Admin | - | [academic.py:289](D:/project/AI-Attendance-System/backend/routers/academic.py:289) |
| GET | `/api/attendance` | Operator/Admin | - | [attendance.py:202](D:/project/AI-Attendance-System/backend/routers/attendance.py:202) |
| GET | `/api/attendance/export/csv` | Operator/Admin | - | [attendance.py:315](D:/project/AI-Attendance-System/backend/routers/attendance.py:315) |
| POST | `/api/attendance/identify` | Operator/Admin | 20/minute | [attendance.py:68](D:/project/AI-Attendance-System/backend/routers/attendance.py:68) |
| PUT | `/api/attendance/manual` | Operator/Admin | - | [attendance.py:257](D:/project/AI-Attendance-System/backend/routers/attendance.py:257) |
| POST | `/api/attendance/mark/{session_id}` | Operator/Admin | 20/minute | [attendance.py:89](D:/project/AI-Attendance-System/backend/routers/attendance.py:89) |
| WEBSOCKET | `/api/attendance/ws/{session_id}` | Operator/Admin (auth frame) | - | [attendance.py:362](D:/project/AI-Attendance-System/backend/routers/attendance.py:362) |
| POST | `/api/auth/google` | Public | 15/minute | [google_auth.py:43](D:/project/AI-Attendance-System/backend/routers/google_auth.py:43) |
| GET | `/api/auth/google/config` | Public | - | [google_auth.py:37](D:/project/AI-Attendance-System/backend/routers/google_auth.py:37) |
| POST | `/api/auth/login` | Public | - | [auth.py:44](D:/project/AI-Attendance-System/backend/routers/auth.py:44) |
| GET | `/api/auth/me` | Student/Operator/Admin | - | [auth.py:110](D:/project/AI-Attendance-System/backend/routers/auth.py:110) |
| POST | `/api/auth/microsoft` | Public | 10/minute | [microsoft_auth.py:51](D:/project/AI-Attendance-System/backend/routers/microsoft_auth.py:51) |
| POST | `/api/auth/microsoft/challenge` | Public | 10/minute | [microsoft_auth.py:38](D:/project/AI-Attendance-System/backend/routers/microsoft_auth.py:38) |
| GET | `/api/auth/microsoft/config` | Public | - | [microsoft_auth.py:32](D:/project/AI-Attendance-System/backend/routers/microsoft_auth.py:32) |
| POST | `/api/auth/register` | Admin | - | [auth.py:75](D:/project/AI-Attendance-System/backend/routers/auth.py:75) |
| GET | `/api/auth/student-portal` | Student/Operator/Admin | - | [auth.py:225](D:/project/AI-Attendance-System/backend/routers/auth.py:225) |
| GET | `/api/auth/users` | Admin | - | [auth.py:147](D:/project/AI-Attendance-System/backend/routers/auth.py:147) |
| PATCH | `/api/auth/users/{user_id}` | Admin | - | [auth.py:170](D:/project/AI-Attendance-System/backend/routers/auth.py:170) |
| PUT | `/api/auth/users/{user_id}/google` | Admin | - | [google_auth.py:115](D:/project/AI-Attendance-System/backend/routers/google_auth.py:115) |
| PUT | `/api/auth/users/{user_id}/microsoft` | Admin | - | [microsoft_auth.py:74](D:/project/AI-Attendance-System/backend/routers/microsoft_auth.py:74) |
| GET | `/api/dashboard/activity` | Operator/Admin | - | [dashboard.py:34](D:/project/AI-Attendance-System/backend/routers/dashboard.py:34) |
| GET | `/api/dashboard/metrics` | Operator/Admin | - | [dashboard.py:19](D:/project/AI-Attendance-System/backend/routers/dashboard.py:19) |
| GET | `/api/persons` | Operator/Admin | - | [persons.py:114](D:/project/AI-Attendance-System/backend/routers/persons.py:114) |
| GET | `/api/persons/debug-config` | Admin | - | [persons.py:63](D:/project/AI-Attendance-System/backend/routers/persons.py:63) |
| GET | `/api/persons/debug-encodings` | Admin | - | [persons.py:32](D:/project/AI-Attendance-System/backend/routers/persons.py:32) |
| POST | `/api/persons/enroll` | Admin | 10/minute | [persons.py:165](D:/project/AI-Attendance-System/backend/routers/persons.py:165) |
| POST | `/api/persons/enroll/analyze` | Student/Operator/Admin | 10/minute | [persons.py:129](D:/project/AI-Attendance-System/backend/routers/persons.py:129) |
| POST | `/api/persons/self-enroll` | Student/Operator/Admin | 10/minute | [persons.py:316](D:/project/AI-Attendance-System/backend/routers/persons.py:316) |
| DELETE | `/api/persons/{person_id}` | Admin | - | [persons.py:490](D:/project/AI-Attendance-System/backend/routers/persons.py:490) |
| GET | `/api/persons/{person_id}` | Operator/Admin | - | [persons.py:427](D:/project/AI-Attendance-System/backend/routers/persons.py:427) |
| PATCH | `/api/persons/{person_id}` | Operator/Admin | - | [persons.py:435](D:/project/AI-Attendance-System/backend/routers/persons.py:435) |
| GET | `/api/reports/daily` | Operator/Admin | - | [reports.py:80](D:/project/AI-Attendance-System/backend/routers/reports.py:80) |
| GET | `/api/reports/heatmap` | Operator/Admin | - | [reports.py:127](D:/project/AI-Attendance-System/backend/routers/reports.py:127) |
| GET | `/api/reports/persons` | Operator/Admin | - | [reports.py:106](D:/project/AI-Attendance-System/backend/routers/reports.py:106) |
| GET | `/api/sessions` | Operator/Admin | - | [sessions.py:46](D:/project/AI-Attendance-System/backend/routers/sessions.py:46) |
| POST | `/api/sessions` | Operator/Admin | - | [sessions.py:66](D:/project/AI-Attendance-System/backend/routers/sessions.py:66) |
| GET | `/api/sessions/{session_id}` | Operator/Admin | - | [sessions.py:84](D:/project/AI-Attendance-System/backend/routers/sessions.py:84) |
| PATCH | `/api/sessions/{session_id}/end` | Operator/Admin | - | [sessions.py:97](D:/project/AI-Attendance-System/backend/routers/sessions.py:97) |
| GET | `/health` | Public | - | [main.py:216](D:/project/AI-Attendance-System/backend/main.py:216) |
| GET | `/metrics` | Public | - | [main.py:221](D:/project/AI-Attendance-System/backend/main.py:221) |

Lưu ý: WebSocket có bộ giới hạn riêng 20 frame/phút/IP; không ghi attendance. Phân quyền phạm vi hồ sơ sinh viên nằm trong handler, không thể thể hiện hết bằng vai trò ở bảng. Các API vận hành của operator chưa có phạm vi theo giảng viên/lớp.
