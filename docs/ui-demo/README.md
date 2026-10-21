# AuraAttend UI demo

## Current version: operational layout

The second revision removes the lavender panels, marketing banner, decorative icon tiles, avatars and slogans. It uses a neutral sidebar, a single metric strip, session rows and an attendance ledger. The ledger supports accent-insensitive search across the latest names, departments and session labels. A compact daily bar chart follows the operational sections.

- [Current desktop interface](dashboard-v2-desktop.jpg)
- [Current mobile dark theme](dashboard-v2-mobile-dark.jpg)
- [Current login form](login-v2-desktop.jpg)

Second revision validation: production build passed; desktop/mobile and dark theme inspected; accent-insensitive search (`le phuong`) returned the matching Vietnamese name; a nonmatching query displayed the empty search state; clearing restored all sample rows.

The earlier concept images and screenshots below are retained for comparison and no longer describe the current layout.

The frontend refresh is implemented in the shared application shell, dashboard and login page. Other operational pages inherit the new shell, self-hosted typography and primary button treatment.

## Open the implementation

```powershell
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173/design-preview>. This route is available only in the development server. It uses clearly labeled fictional data and supports Admin/Operator, sample/empty data, Vietnamese/English and light/dark themes. Operational links still require normal authentication and a backend. The preview fixture and route component are excluded from the production bundle.

## Images

- [First revision AI concept](aura-attend-concept.png): generated with the built-in ImageGen tool. This is archived concept artwork for the earlier lavender layout, not the current interface.
- [Actual desktop dashboard](dashboard-desktop.jpg).
- [Actual attendance table](dashboard-activity.jpg).
- [Actual desktop login](login-desktop.jpg).
- [Actual mobile dark theme](dashboard-mobile-dark.jpg).
- Exact generation prompts: [initial prompt](imagegen-prompt.txt), [table refinement](imagegen-refinement.txt).

## Verification completed

- `npm run build`: TypeScript project build and Vite production build passed.
- Desktop 1440px and mobile 390px: inspected in browser; no page-level horizontal overflow. Attendance table scrolls inside its container.
- 7/14-day chart controls update totals and chart labels.
- Vietnamese/English and light/dark toggles update the interface.
- Admin/Operator and sample/empty preview states render correctly.
- Mobile navigation opens, Escape closes it, and focus returns to the menu button.
- Login quick-fill, password visibility, associated input labels and autocomplete checked.
- No browser runtime errors observed. Existing React Router future-version warnings remain.
- Backend was unavailable locally, so real authentication, camera recognition and database actions were not exercised.

The original generated concept version is retained as `aura-attend-concept-v1.png`. Use `dashboard-v2-desktop.jpg` as the current visual reference.
