# HR Portal DRF Backend

This backend converts the original `hash_project` desktop HR portal into a Django + DRF API layer.

## Important security note

The original password security algorithm in `al_hash.py` is preserved:

1. `scrypt(password + HASH_PEPPER)`
2. random salt
3. `HMAC-SHA256` signature over the scrypt hash
4. storage of `hashed`, `salt`, and `signature`

Django's default password hashing is **not** used for authentication. The custom user model calls the original `simple_hash()` and `verify_password()` functions.

## Default admin

A custom admin user is automatically created/updated after migrations:

- username: `salar`
- password: `12345678`
- role: `admin`
- approved: `true`

This account can use both Django admin at `/django-admin/` and the custom admin-panel API at `/api/admin-panel/`.

## Run locally

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py ensure_default_admin  # optional; migrations already do this automatically
python manage.py runserver
```

By default the backend uses SQLite for easy local development. To use MySQL:

```bash
export DJANGO_DB_ENGINE=mysql
export MYSQL_DATABASE=hr_portal
export MYSQL_USER=root
export MYSQL_PASSWORD=12345678
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
python manage.py migrate
```

## Auth flow

### Register

`POST /api/auth/register/`

```json
{
  "username": "employee1",
  "password": "123456",
  "password_confirm": "123456",
  "full_name": "Employee One",
  "email": "employee@example.com"
}
```

New users are created with `is_approved=false` and cannot enter the app until admin approval.

### Login

`POST /api/auth/login/`

```json
{
  "username": "salar",
  "password": "12345678"
}
```

Successful approved login returns both authentication types:

```json
{
  "access": "JWT access token",
  "refresh": "JWT refresh token",
  "token": "DRF TokenAuthentication token",
  "token_type": "Bearer",
  "user": {}
}
```

Use JWT:

```http
Authorization: Bearer <access>
```

Or DRF token:

```http
Authorization: Token <token>
```

If the password is correct but the account is pending admin approval, API returns `403` with `status=pending_approval`.

## Main employee endpoints

- `GET /api/auth/me/`
- `PATCH /api/auth/me/`
- `POST /api/auth/change-password/`
- `POST /api/attendance/clock-in/`
- `POST /api/attendance/clock-out/`
- `GET /api/attendance/today/`
- `GET /api/attendance/weekly/?week_start=YYYY-MM-DD`
- `GET /api/schedules/my/?week_start=YYYY-MM-DD`
- `GET /api/tasks/`
- `GET /api/tasks/{id}/`
- `PATCH /api/tasks/{id}/status/`
- `GET /api/calendar/`

## Custom admin-panel API

This is separate from Django's own admin panel.

- `GET /api/admin-panel/dashboard/stats/`
- `GET /api/admin-panel/charts/weekly/?week_start=YYYY-MM-DD`
- `GET /api/admin-panel/members/`
- `POST /api/admin-panel/members/`
- `GET /api/admin-panel/members/{id}/`
- `PATCH /api/admin-panel/members/{id}/`
- `DELETE /api/admin-panel/members/{id}/`
- `POST /api/admin-panel/members/{id}/approve/`
- `POST /api/admin-panel/members/{id}/reject/`
- `POST /api/admin-panel/members/{id}/set-password/`
- `GET /api/admin-panel/members/{id}/full-info/?week_start=YYYY-MM-DD`
- `CRUD /api/admin-panel/attendance/`
- `CRUD /api/admin-panel/schedules/`
- `CRUD /api/admin-panel/tasks/`
- `CRUD /api/admin-panel/calendar-events/`

## API docs

- OpenAPI schema: `/api/schema/`
- Swagger UI: `/api/docs/`
