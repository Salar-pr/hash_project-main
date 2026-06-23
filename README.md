# HR Portal — Secure Hash-Based Workforce Management Platform

A modern, full-stack HR/workforce management platform built from the original `hash_project` desktop application and upgraded into a production-ready web architecture with **Django REST Framework**, **JWT/Token authentication**, and a premium **Next.js + React** frontend.

The core password security algorithm from the original project is intentionally preserved: passwords are protected using **scrypt + pepper + salt + HMAC-SHA256 signature**.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Security Model](#security-model)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Default Admin Account](#default-admin-account)
- [Authentication Flow](#authentication-flow)
- [API Overview](#api-overview)
- [Environment Variables](#environment-variables)
- [Development Commands](#development-commands)
- [Production Notes](#production-notes)
- [License](#license)

---

## Overview

HR Portal is a secure and responsive workforce management system designed for managing employees, attendance, weekly schedules, tasks, calendar events, and admin approvals.

The original repository started as a PyQt desktop HR application using MySQL and a custom password hashing mechanism. This version keeps the original security logic and extends the project into a web-based full-stack application:

- **Backend:** Django + Django REST Framework
- **Frontend:** Next.js + React + TypeScript
- **Authentication:** JWT access/refresh tokens + DRF TokenAuthentication
- **Security:** Original `scrypt + pepper + salt + HMAC` password verification
- **Admin:** Custom admin panel separate from Django Admin

---

## Key Features

### Authentication & Security

- Secure registration and login
- JWT access and refresh token support
- DRF token support
- Approval-aware authentication
- Users cannot access the system until approved by an admin
- Passwords are hashed using the original custom algorithm
- Token invalidation on password changes or account rejection

### Employee Panel

- Personal dashboard
- Clock-in and clock-out
- Daily attendance status
- Weekly attendance reports
- Weekly work-hours chart
- Weekly schedule view
- Assigned tasks view
- Task status update
- Personal and public calendar events

### Custom Admin Panel

The project includes a custom admin panel for business operations, separate from Django's built-in admin interface.

Admins can:

- View all members
- Add new members
- Edit member profiles
- Delete members
- Approve or reject users
- Manage salaries in rubles
- Manage roles: `admin` / `employee`
- View complete member details
- View login/attendance data
- Manage weekly schedules
- Create and manage tasks
- Create public or user-specific calendar events
- View weekly charts and statistics

### Frontend UX

- Fully responsive UI
- Persian RTL interface
- Premium dashboard design
- Desktop sidebar navigation
- Mobile bottom navigation
- Clean cards, tables, modals, and forms
- No external UI framework dependency
- Built with modern Next.js App Router

---

## Architecture

```text
Client Browser
     |
     |  JWT / Token Auth
     v
Next.js Frontend
     |
     |  REST API
     v
Django REST Framework Backend
     |
     |  ORM
     v
SQLite / MySQL Database
```

The system is split into two main layers:

1. **Django DRF Backend**
   - Handles authentication, authorization, business logic, and database operations.

2. **Next.js Frontend**
   - Provides the user interface for employees and admins.

---

## Tech Stack

### Backend

- Python
- Django
- Django REST Framework
- Simple JWT
- DRF TokenAuthentication
- django-cors-headers
- drf-spectacular
- SQLite for local development
- MySQL support for production or legacy compatibility

### Frontend

- Next.js 15
- React 19
- TypeScript
- App Router
- CSS custom design system
- Responsive RTL layout

### Original Desktop App

The original PyQt files are still present in the repository for reference and backward compatibility:

- `main.py`
- `ui/`
- `db/`
- `connect_DATABASE.py`
- `al_hash.py`

---

## Security Model

The most important security requirement of this project is preserving the original hashing algorithm.

The password flow is:

```text
password + HASH_PEPPER
        |
        v
hashlib.scrypt(..., salt=random_salt)
        |
        v
HMAC-SHA256(hashed_password, HMAC_KEY)
        |
        v
store: hashed, salt, signature
```

Verification uses:

```python
verify_password(password, salt, original_signature)
```

The custom Django user model stores:

- `hashed`
- `salt`
- `signature`

Django's default password hasher is not used for authentication. Instead, the custom user model calls the original `simple_hash()` and `verify_password()` functions from `al_hash.py`.

---

## Project Structure

```text
hash_project/
|
|-- al_hash.py                  # Original password hashing/security algorithm
|-- connect_DATABASE.py          # Original desktop database auth helpers
|-- config.py                    # Original MySQL configuration
|-- main.py                      # Original PyQt desktop entrypoint
|-- manage.py                    # Django entrypoint
|-- requirements.txt             # Python/backend dependencies
|
|-- backend/                     # Django project settings
|   |-- settings.py
|   |-- urls.py
|   |-- asgi.py
|   `-- wsgi.py
|
|-- hr/                          # Django HR application
|   |-- models.py                # Custom user, attendance, schedules, tasks, calendar
|   |-- serializers.py
|   |-- views.py
|   |-- urls.py
|   |-- permissions.py
|   |-- authentication.py
|   |-- admin.py
|   |-- signals.py
|   |-- migrations/
|   `-- management/commands/
|
|-- frontend/                    # Next.js frontend
|   |-- app/
|   |   |-- login/
|   |   |-- register/
|   |   |-- dashboard/
|   |   |-- attendance/
|   |   |-- schedule/
|   |   |-- tasks/
|   |   |-- calendar/
|   |   `-- admin/
|   |
|   |-- components/
|   |-- lib/
|   |-- package.json
|   |-- tsconfig.json
|   `-- README.md
|
|-- ui/                          # Original PyQt UI
|-- db/                          # Original desktop database layer
|-- API_BACKEND_README.md         # Backend-specific notes
`-- README.md                    # Main GitHub README
```

---

## Quick Start

Run the backend and frontend in two separate terminals.

### Terminal 1 — Backend

```bash
cd hash_project
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Backend will run at:

```text
http://127.0.0.1:8000
```

### Terminal 2 — Frontend

```bash
cd hash_project/frontend
npm install
npm run dev
```

Frontend will run at:

```text
http://localhost:3000
```

---

## Backend Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run migrations

```bash
python manage.py migrate
```

The default admin account is created automatically after migrations.

You can also force-create/update it manually:

```bash
python manage.py ensure_default_admin
```

### 3. Run development server

```bash
python manage.py runserver
```

### 4. API documentation

OpenAPI schema:

```text
http://127.0.0.1:8000/api/schema/
```

Swagger UI:

```text
http://127.0.0.1:8000/api/docs/
```

Django Admin:

```text
http://127.0.0.1:8000/django-admin/
```

---

## Frontend Setup

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Run development server

```bash
npm run dev
```

### 3. Build for production

```bash
npm run build
npm run start
```

### 4. Frontend API base URL

By default, the frontend uses:

```text
http://127.0.0.1:8000/api
```

To override it:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api npm run dev
```

---

## Default Admin Account

A default admin user is automatically created or updated after migrations:

```text
Username: salar
Password: 12345678
Role:     admin
Approved: true
```

This user can access:

- Custom admin panel: `http://localhost:3000/admin`
- Django Admin: `http://127.0.0.1:8000/django-admin/`

---

## Authentication Flow

### Registration

New users register through:

```http
POST /api/auth/register/
```

Example request:

```json
{
  "username": "employee1",
  "password": "123456",
  "password_confirm": "123456",
  "full_name": "Employee One",
  "email": "employee@example.com"
}
```

New users are created with:

```text
is_approved = false
```

They cannot access the app until an admin approves them.

### Login

```http
POST /api/auth/login/
```

Example request:

```json
{
  "username": "salar",
  "password": "12345678"
}
```

Successful response:

```json
{
  "user": {},
  "access": "jwt-access-token",
  "refresh": "jwt-refresh-token",
  "token": "drf-token",
  "token_type": "Bearer"
}
```

### Pending Approval Response

If credentials are correct but the account is not approved:

```json
{
  "status": "pending_approval",
  "detail": "Your account is waiting for admin approval.",
  "user": {}
}
```

### Authorization Headers

JWT:

```http
Authorization: Bearer <access_token>
```

DRF Token:

```http
Authorization: Token <token>
```

---

## API Overview

### Auth APIs

```text
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/logout/
GET  /api/auth/me/
PATCH /api/auth/me/
POST /api/auth/change-password/
POST /api/auth/jwt/refresh/
POST /api/auth/jwt/verify/
```

### Employee APIs

```text
GET  /api/attendance/today/
POST /api/attendance/clock-in/
POST /api/attendance/clock-out/
GET  /api/attendance/weekly/?week_start=YYYY-MM-DD

GET  /api/schedules/my/?week_start=YYYY-MM-DD

GET  /api/tasks/
GET  /api/tasks/{id}/
PATCH /api/tasks/{id}/status/

GET  /api/calendar/
GET  /api/calendar/{id}/
```

### Custom Admin Panel APIs

```text
GET /api/admin-panel/dashboard/stats/
GET /api/admin-panel/charts/weekly/?week_start=YYYY-MM-DD
```

Members:

```text
GET    /api/admin-panel/members/
POST   /api/admin-panel/members/
GET    /api/admin-panel/members/{id}/
PATCH  /api/admin-panel/members/{id}/
DELETE /api/admin-panel/members/{id}/
POST   /api/admin-panel/members/{id}/approve/
POST   /api/admin-panel/members/{id}/reject/
POST   /api/admin-panel/members/{id}/set-password/
GET    /api/admin-panel/members/{id}/full-info/?week_start=YYYY-MM-DD
```

Attendance:

```text
GET    /api/admin-panel/attendance/
POST   /api/admin-panel/attendance/
GET    /api/admin-panel/attendance/{id}/
PATCH  /api/admin-panel/attendance/{id}/
DELETE /api/admin-panel/attendance/{id}/
```

Schedules:

```text
GET    /api/admin-panel/schedules/
POST   /api/admin-panel/schedules/
GET    /api/admin-panel/schedules/{id}/
PATCH  /api/admin-panel/schedules/{id}/
DELETE /api/admin-panel/schedules/{id}/
```

Tasks:

```text
GET    /api/admin-panel/tasks/
POST   /api/admin-panel/tasks/
GET    /api/admin-panel/tasks/{id}/
PATCH  /api/admin-panel/tasks/{id}/
DELETE /api/admin-panel/tasks/{id}/
```

Calendar Events:

```text
GET    /api/admin-panel/calendar-events/
POST   /api/admin-panel/calendar-events/
GET    /api/admin-panel/calendar-events/{id}/
PATCH  /api/admin-panel/calendar-events/{id}/
DELETE /api/admin-panel/calendar-events/{id}/
```

---

## Environment Variables

### Backend

| Variable | Default | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | development key | Django secret key |
| `DJANGO_DEBUG` | `1` | Enables debug mode |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,*` | Allowed hosts |
| `DJANGO_TIME_ZONE` | `UTC` | Django timezone |
| `DJANGO_DB_ENGINE` | `sqlite` | Use `sqlite` or `mysql` |
| `MYSQL_DATABASE` | `hr_portal` | MySQL database name |
| `MYSQL_USER` | `root` | MySQL user |
| `MYSQL_PASSWORD` | `12345678` | MySQL password |
| `MYSQL_HOST` | `localhost` | MySQL host |
| `MYSQL_PORT` | `3306` | MySQL port |
| `JWT_ACCESS_MINUTES` | `60` | JWT access token lifetime |
| `JWT_REFRESH_DAYS` | `7` | JWT refresh token lifetime |
| `CORS_ALLOW_ALL_ORIGINS` | `1` | Allow all CORS origins in development |
| `CORS_ALLOWED_ORIGINS` | empty | Comma-separated allowed origins |
| `HASH_PEPPER` | auto-generated | Pepper used by original hash algorithm |
| `HMAC_KEY` | auto-generated | HMAC key used by original hash algorithm |

### Frontend

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | `http://127.0.0.1:8000/api` | Backend API base URL |

---

## MySQL Setup

The backend uses SQLite by default for local development. To use MySQL:

```bash
export DJANGO_DB_ENGINE=mysql
export MYSQL_DATABASE=hr_portal
export MYSQL_USER=root
export MYSQL_PASSWORD=12345678
export MYSQL_HOST=localhost
export MYSQL_PORT=3306

python manage.py migrate
python manage.py runserver
```

---

## Development Commands

### Backend

```bash
python manage.py check
python manage.py migrate
python manage.py runserver
python manage.py ensure_default_admin
```

### Frontend

```bash
npm run dev
npm run build
npm run start
npm run typecheck
```

---

## Production Notes

Before deploying to production, update the following:

1. Set a strong `DJANGO_SECRET_KEY`.
2. Set `DJANGO_DEBUG=0`.
3. Configure `DJANGO_ALLOWED_HOSTS`.
4. Restrict CORS origins.
5. Use a production database such as MySQL or PostgreSQL.
6. Store `.env` securely and never commit it.
7. Use HTTPS.
8. Change the default admin password immediately.
9. Configure a production WSGI/ASGI server.
10. Build and serve the Next.js frontend using a production deployment platform.

---

## Notes About the Original Project

The original PyQt desktop implementation is still included. This makes it easier to compare the old desktop workflow with the new web-based system.

The new web backend does not remove or rewrite the original hashing logic. It wraps the original security algorithm inside a Django custom user model and exposes the HR functionality through REST APIs.

---

## License

This project is provided as part of the `hash_project` repository. Add your preferred license before publishing or distributing the project.
