import mysql.connector
from mysql.connector import IntegrityError
from al_hash import simple_hash, verify_password
from config import DB_CONFIG


def _conn():
    return mysql.connector.connect(**DB_CONFIG)


def init_db() -> None:
    """Create database and users table if they don't exist."""
    # First connect without specifying the database to create it if needed
    cfg = {k: v for k, v in DB_CONFIG.items() if k != "database"}
    con = mysql.connector.connect(**cfg)
    cur = con.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}` "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cur.execute(f"USE `{DB_CONFIG['database']}`")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            username   VARCHAR(150) NOT NULL UNIQUE,
            hashed     BLOB         NOT NULL,
            salt       BLOB         NOT NULL,
            signature  BLOB         NOT NULL,
            role       VARCHAR(20)  NOT NULL DEFAULT 'employee',
            created_at DATETIME     DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.commit()
    cur.close()
    con.close()


def register_user(username: str, password: str) -> bool:
    """Register a new user. Returns False if username already exists."""
    hashed, salt, signature = simple_hash(password)
    try:
        con = _conn()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO users (username, hashed, salt, signature) VALUES (%s, %s, %s, %s)",
            (username, hashed, salt, signature),
        )
        con.commit()
        return True
    except IntegrityError:
        return False
    finally:
        cur.close()
        con.close()


def login_user(username: str, password: str) -> bool:
    """Verify credentials. Returns True if valid."""
    con = _conn()
    cur = con.cursor()
    cur.execute(
        "SELECT salt, signature FROM users WHERE username = %s",
        (username,),
    )
    row = cur.fetchone()
    cur.close()
    con.close()

    if row is None:
        return False

    salt, signature = row
    return verify_password(password, bytes(salt), bytes(signature))


def delete_user(username: str) -> bool:
    """Delete a user. Returns True if deleted."""
    con = _conn()
    cur = con.cursor()
    cur.execute("DELETE FROM users WHERE username = %s", (username,))
    con.commit()
    affected = cur.rowcount
    cur.close()
    con.close()
    return affected > 0


def user_exists(username: str) -> bool:
    """Check if a username is already registered."""
    con = _conn()
    cur = con.cursor()
    cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
    row = cur.fetchone()
    cur.close()
    con.close()
    return row is not None