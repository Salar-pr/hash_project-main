import mysql.connector
from datetime import datetime, date
from typing import Optional

from connect_DATABASE import init_db
from config import DB_CONFIG


def _conn():
    return mysql.connector.connect(**DB_CONFIG)


def init_extended_db() -> None:
    """Initialize all tables required by the HR application."""
    init_db()

    con = _conn()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id        INT AUTO_INCREMENT PRIMARY KEY,
            username  VARCHAR(150) NOT NULL,
            work_date DATE         NOT NULL,
            clock_in  DATETIME,
            clock_out DATETIME,
            UNIQUE KEY uq_user_date (username, work_date),
            FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            username    VARCHAR(150) NOT NULL,
            week_start  DATE         NOT NULL,
            day_of_week VARCHAR(20)  NOT NULL,
            shift_start VARCHAR(10)  NOT NULL,
            shift_end   VARCHAR(10)  NOT NULL,
            UNIQUE KEY uq_sched (username, week_start, day_of_week),
            FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
        )
    """)

    con.commit()
    cur.close()
    con.close()


# ---------------------------------------------------------------------------
# User / Role
# ---------------------------------------------------------------------------

def get_user_role(username: str) -> Optional[str]:
    con = _conn()
    cur = con.cursor()
    cur.execute("SELECT role FROM users WHERE username = %s", (username,))
    row = cur.fetchone()
    cur.close()
    con.close()
    return row[0] if row else None


def set_user_role(username: str, role: str) -> bool:
    if role not in ("admin", "employee"):
        return False
    con = _conn()
    cur = con.cursor()
    cur.execute("UPDATE users SET role = %s WHERE username = %s", (role, username))
    con.commit()
    affected = cur.rowcount
    cur.close()
    con.close()
    return affected > 0


def get_all_users() -> list[dict]:
    con = _conn()
    cur = con.cursor()
    cur.execute(
        "SELECT id, username, role, created_at FROM users ORDER BY created_at DESC"
    )
    rows = cur.fetchall()
    cur.close()
    con.close()
    return [
        {"id": r[0], "username": r[1], "role": r[2], "created_at": r[3]}
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Attendance
# ---------------------------------------------------------------------------

def clock_in(username: str) -> tuple[bool, str]:
    today = date.today()
    now   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    con   = _conn()
    cur   = con.cursor()

    cur.execute(
        "SELECT clock_in FROM attendance WHERE username = %s AND work_date = %s",
        (username, today),
    )
    existing = cur.fetchone()

    if existing and existing[0]:
        cur.close(); con.close()
        return False, f"Already clocked in at {str(existing[0])[11:16]}"

    cur.execute("""
        INSERT INTO attendance (username, work_date, clock_in)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE clock_in = VALUES(clock_in)
    """, (username, today, now))
    con.commit()
    cur.close()
    con.close()
    return True, f"Clocked in at {now[11:16]}"


def clock_out(username: str) -> tuple[bool, str]:
    today = date.today()
    now   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    con   = _conn()
    cur   = con.cursor()

    cur.execute(
        "SELECT clock_in, clock_out FROM attendance WHERE username = %s AND work_date = %s",
        (username, today),
    )
    existing = cur.fetchone()

    if not existing or not existing[0]:
        cur.close(); con.close()
        return False, "You have not clocked in today"
    if existing[1]:
        cur.close(); con.close()
        return False, f"Already clocked out at {str(existing[1])[11:16]}"

    cur.execute(
        "UPDATE attendance SET clock_out = %s WHERE username = %s AND work_date = %s",
        (now, username, today),
    )
    con.commit()
    cur.close()
    con.close()
    return True, f"Clocked out at {now[11:16]}"


def get_weekly_attendance(username: str, week_start: date) -> list[dict]:
    week_end = date.fromordinal(week_start.toordinal() + 6)
    con = _conn()
    cur = con.cursor()
    cur.execute("""
        SELECT work_date, clock_in, clock_out
        FROM attendance
        WHERE username = %s AND work_date BETWEEN %s AND %s
        ORDER BY work_date
    """, (username, week_start, week_end))
    rows = cur.fetchall()
    cur.close()
    con.close()

    results = []
    for r in rows:
        ci = str(r[1])[11:16] if r[1] else "--:--"
        co = str(r[2])[11:16] if r[2] else "--:--"
        hours = round(
            (datetime.fromisoformat(str(r[2])) - datetime.fromisoformat(str(r[1]))).total_seconds() / 3600, 2
        ) if r[1] and r[2] else 0.0
        results.append({"date": str(r[0]), "clock_in": ci, "clock_out": co, "hours": hours})
    return results


def get_today_attendance(username: str) -> Optional[dict]:
    today = date.today()
    con = _conn()
    cur = con.cursor()
    cur.execute(
        "SELECT work_date, clock_in, clock_out FROM attendance WHERE username = %s AND work_date = %s",
        (username, today),
    )
    row = cur.fetchone()
    cur.close()
    con.close()

    if not row:
        return None

    ci    = str(row[1])[11:16] if row[1] else "--:--"
    co    = str(row[2])[11:16] if row[2] else "--:--"
    hours = round(
        (datetime.fromisoformat(str(row[2])) - datetime.fromisoformat(str(row[1]))).total_seconds() / 3600, 2
    ) if row[1] and row[2] else 0.0
    return {"date": str(row[0]), "clock_in": ci, "clock_out": co, "hours": hours}


def get_all_attendance_this_week(week_start: date) -> list[dict]:
    week_end = date.fromordinal(week_start.toordinal() + 6)
    con = _conn()
    cur = con.cursor()
    cur.execute("""
        SELECT username, work_date, clock_in, clock_out
        FROM attendance
        WHERE work_date BETWEEN %s AND %s
        ORDER BY work_date, username
    """, (week_start, week_end))
    rows = cur.fetchall()
    cur.close()
    con.close()

    results = []
    for r in rows:
        ci    = str(r[2])[11:16] if r[2] else "--:--"
        co    = str(r[3])[11:16] if r[3] else "--:--"
        hours = round(
            (datetime.fromisoformat(str(r[3])) - datetime.fromisoformat(str(r[2]))).total_seconds() / 3600, 2
        ) if r[2] and r[3] else 0.0
        results.append({"username": r[0], "date": str(r[1]), "clock_in": ci, "clock_out": co, "hours": hours})
    return results


# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def set_schedule(username: str, week_start: date, day: str, shift_start: str, shift_end: str) -> bool:
    if day not in DAYS:
        return False
    con = _conn()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO schedule (username, week_start, day_of_week, shift_start, shift_end)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE shift_start = VALUES(shift_start), shift_end = VALUES(shift_end)
    """, (username, week_start, day, shift_start, shift_end))
    con.commit()
    cur.close()
    con.close()
    return True


def get_weekly_schedule(username: str, week_start: date) -> list[dict]:
    con = _conn()
    cur = con.cursor()
    cur.execute("""
        SELECT day_of_week, shift_start, shift_end
        FROM schedule
        WHERE username = %s AND week_start = %s
        ORDER BY id
    """, (username, week_start))
    rows = cur.fetchall()
    cur.close()
    con.close()
    return [{"day": r[0], "shift_start": r[1], "shift_end": r[2]} for r in rows]