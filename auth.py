"""
auth.py  —  Production
SHA-256 password hashing. Auto-creates table with correct schema on import.
"""
import sqlite3
import hashlib

DB_PATH = "users.db"


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    _migrate_if_needed()


def _migrate_if_needed():
    """Add 'id' column if old schema is detected."""
    conn = sqlite3.connect(DB_PATH)
    cols = [r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
    conn.close()
    if "id" not in cols:
        conn = sqlite3.connect(DB_PATH)
        try:
            rows = conn.execute("SELECT username, password FROM users").fetchall()
        except Exception:
            rows = []
        conn.execute("ALTER TABLE users RENAME TO _users_old")
        conn.execute("""
            CREATE TABLE users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        for u, p in rows:
            # keep existing hash or re-hash plain-text passwords
            pw = p if len(p) == 64 else _hash(p)
            try:
                conn.execute("INSERT INTO users (username,password) VALUES (?,?)", (u, pw))
            except Exception:
                pass
        conn.execute("DROP TABLE _users_old")
        conn.commit()
        conn.close()


def register(username: str, password: str) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username.strip(), _hash(password))
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def login(username: str, password: str) -> bool:
    conn  = sqlite3.connect(DB_PATH)
    row   = conn.execute(
        "SELECT password FROM users WHERE username=?", (username.strip(),)
    ).fetchone()
    conn.close()
    if row is None:
        return False
    stored = row[0]
    # Support both hashed and legacy plain-text passwords
    return stored == _hash(password) or stored == password


def change_password(username: str, new_password: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.execute(
        "UPDATE users SET password=? WHERE username=?",
        (_hash(new_password), username.strip())
    )
    conn.commit()
    conn.close()
    return cur.rowcount > 0


def delete_user(username: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.execute("DELETE FROM users WHERE username=?", (username.strip(),))
    conn.commit()
    conn.close()
    return cur.rowcount > 0


def list_users() -> list:
    conn  = sqlite3.connect(DB_PATH)
    rows  = conn.execute("SELECT username FROM users ORDER BY id").fetchall()
    conn.close()
    return [r[0] for r in rows]


# Auto-init on import
init_db()