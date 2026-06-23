# HR Portal Premium Frontend

Next.js + React frontend for the Django DRF backend.

## Features

- Premium responsive UI/UX inspired by the original PyQt desktop app, but redesigned for web.
- Persian RTL interface.
- JWT access/refresh authentication matched with `/api/auth/login/`.
- Approval-aware login flow: pending users see the waiting message.
- Employee dashboard: attendance, weekly chart, schedule, tasks, calendar.
- Custom admin panel: members, salary in ruble, approval, attendance, schedules, tasks, calendar, weekly charts.
- No external UI kit dependency; the design system is implemented in `app/globals.css`.

## Run

Start backend first:

```bash
cd ..
python manage.py migrate
python manage.py runserver
```

Start frontend:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

Default backend API base:

```text
http://127.0.0.1:8000/api
```

To change it:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api npm run dev
```

Default admin:

```text
username: salar
password: 12345678
```
