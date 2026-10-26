> Cập nhật 27/10/2026 (chưa publish): enrollment cần `consent`; mark cần `probe_frame`; response dùng hợp đồng backend hiện hành. Xem [hướng dẫn nâng cấp](../../docs/UPGRADE_2026_10.md). Bản npm đã phát hành trước đây có thể chưa chứa các sửa đổi này.

# @maitamdev/smartattend-client

> Typed client SDK for the Smart Attendance FastAPI backend, supporting Node.js, browsers, and mobile runtimes.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

`@maitamdev/smartattend-client` provides a robust, strongly-typed HTTP client for consuming the Smart Attendance API across web applications, administrative dashboards, kiosk devices, and background scripts.

Features:
- Unified modules: `auth`, `persons`, `sessions`, `attendance`, `dashboard`, `reports`, and `diagnostics`
- Automatic JWT Bearer token injection with support for legacy `X-API-Key`
- Pluggable storage adapters (memory, sessionStorage, localStorage, or custom)
- Automatic FormData multipart handling for biometric face photos
- Clean, structured error handling via `ApiError`

---

## Installation

```bash
# Via GitHub Packages
npm install @maitamdev/smartattend-client
```

Ensure your `.npmrc` is configured for the `@maitamdev` scope:
```ini
@maitamdev:registry=https://npm.pkg.github.com
```

---

## Quick Start

```ts
import { SmartAttendClient } from "@maitamdev/smartattend-client";

const client = new SmartAttendClient({
  baseUrl: "https://api.smartattend.example.com",
});

// 1. Authenticate operator or administrator
const auth = await client.auth.login("operator_user", "SecurePassword123!");
console.log(`Logged in as ${auth.username} (${auth.role})`);

// 2. Query active sessions
const sessions = await client.sessions.list({ active: true });

// 3. Mark attendance with a captured camera frame
const attendanceReport = await client.attendance.mark({
  session_id: sessions[0].id,
  photo: capturedImageBlob,
  probe_frame: laterCameraFrameBlob,
});

console.log(`Marked ${attendanceReport.new_records} attendees.`);
```

---

## API Reference

- `client.auth.login(username, password)`
- `client.auth.me()`
- `client.persons.list(query?)`
- `client.persons.get(personId)`
- `client.persons.enroll({ name, consent, student_id?, person_id?, email?, department?, photos })`
- `client.persons.delete(personId)`
- `client.sessions.create({ label, department? })`
- `client.sessions.list(query?)`
- `client.sessions.end(sessionId)`
- `client.attendance.identify(photoBlob)`
- `client.attendance.mark({ session_id, photo, probe_frame })`
- `client.attendance.list(query?)`
- `client.attendance.exportCsv(sessionId?)`
- `client.dashboard.getMetrics()`
- `client.reports.getDailyStats(days?)`

---

## License

MIT © [Mai Tam (maitamdev)](https://github.com/maitamdev)

## Live contract smoke

Sau khi build package, chạy với backend và DB thử **localhost riêng**:

```powershell
$env:SMARTATTEND_TEST_BASE_URL='http://127.0.0.1:8018'
$env:SMARTATTEND_TEST_KEY='<admin key của môi trường thử>'
node packages/smartattend-client/test/live-api.smoke.js
```

Smoke tạo phiên/tài khoản thử và kiểm tra API thật, gửi ảnh trống tới model thật. Không chạy trên DB chứa dữ liệu người dùng; đây không phải benchmark độ chính xác sinh trắc.
