# # history_db.py

# import sqlite3
# from datetime import datetime

# DB_PATH = "history.db"

# def init_history_db():
#     """Create the history table if it doesn't exist."""
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("""
#         CREATE TABLE IF NOT EXISTS history (
#             id         INTEGER PRIMARY KEY AUTOINCREMENT,
#             activity   TEXT    NOT NULL,
#             confidence REAL    NOT NULL,
#             timestamp  TEXT    NOT NULL
#         )
#     """)
#     conn.commit()
#     conn.close()


# def save_history(activity: str, confidence: float):
#     """Insert one activity record with current timestamp."""
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute(
#         "INSERT INTO history (activity, confidence, timestamp) VALUES (?, ?, ?)",
#         (activity, round(float(confidence), 4), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
#     )
#     conn.commit()
#     conn.close()


# def get_history():
#     """Return all rows as a list of tuples: (id, activity, confidence, timestamp)."""
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("SELECT id, activity, confidence, timestamp FROM history ORDER BY id DESC")
#     rows = c.fetchall()
#     conn.close()
#     return rows


# def delete_record(record_id: int):
#     """Delete a single record by ID."""
#     conn = sqlite3.connect(DB_PATH)
#     conn.execute("DELETE FROM history WHERE id=?", (record_id,))
#     conn.commit()
#     conn.close()


# def update_record(record_id: int, activity: str, confidence: float):
#     """Update activity and confidence for a given record."""
#     conn = sqlite3.connect(DB_PATH)
#     conn.execute(
#         "UPDATE history SET activity=?, confidence=? WHERE id=?",
#         (activity, round(float(confidence), 4), record_id)
#     )
#     conn.commit()
#     conn.close()


# def clear_all():
#     """Delete every row in the history table."""
#     conn = sqlite3.connect(DB_PATH)
#     conn.execute("DELETE FROM history")
#     conn.commit()
#     conn.close()


# # Auto-initialise on import
# init_history_db()

"""
history_db.py — Production
Activity history + user registration (name + mobile).
"""
import sqlite3
from datetime import datetime

DB_PATH = "history.db"


def init_history_db():
    conn = sqlite3.connect(DB_PATH)

    # Activity history table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL DEFAULT 'unknown',
            mobile     TEXT NOT NULL DEFAULT '',
            activity   TEXT NOT NULL,
            confidence REAL NOT NULL,
            timestamp  TEXT NOT NULL
        )
    """)

    # Registered users table (filled from Vercel form)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS registered_users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            mobile     TEXT NOT NULL UNIQUE,
            registered TEXT NOT NULL,
            last_seen  TEXT NOT NULL
        )
    """)

    # Safe migration for old schema
    for col, default in [("mobile", "''"), ("username", "'unknown'")]:
        try:
            conn.execute(f"ALTER TABLE history ADD COLUMN {col} TEXT NOT NULL DEFAULT {default}")
        except Exception:
            pass

    conn.commit()
    conn.close()


def register_user(name: str, mobile: str):
    """Save user from Vercel form. Updates if mobile already exists."""
    conn = sqlite3.connect(DB_PATH)
    now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("""
        INSERT INTO registered_users (name, mobile, registered, last_seen)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(mobile) DO UPDATE SET
            name      = excluded.name,
            last_seen = excluded.last_seen
    """, (name.strip(), mobile.strip(), now, now))
    conn.commit()
    conn.close()


def update_last_seen(mobile: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE registered_users SET last_seen=? WHERE mobile=?",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), mobile.strip())
    )
    conn.commit()
    conn.close()


def save_history(activity: str, confidence: float,
                 username: str = "unknown", mobile: str = ""):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO history (username, mobile, activity, confidence, timestamp) "
        "VALUES (?, ?, ?, ?, ?)",
        (username, mobile, activity,
         round(float(confidence), 4),
         datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


def get_history(username: str = None, mobile: str = None):
    conn = sqlite3.connect(DB_PATH)
    if username == "admin" or (not username and not mobile):
        rows = conn.execute(
            "SELECT id, activity, confidence, timestamp "
            "FROM history ORDER BY id DESC"
        ).fetchall()
    elif mobile:
        rows = conn.execute(
            "SELECT id, activity, confidence, timestamp "
            "FROM history WHERE mobile=? ORDER BY id DESC", (mobile,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, activity, confidence, timestamp "
            "FROM history WHERE username=? ORDER BY id DESC", (username,)
        ).fetchall()
    conn.close()
    return rows


def get_history_with_users():
    """Admin — all records with username + mobile."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, username, mobile, activity, confidence, timestamp "
        "FROM history ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return rows


def get_registered_users():
    """Admin — all users who filled the Vercel form."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, name, mobile, registered, last_seen "
        "FROM registered_users ORDER BY last_seen DESC"
    ).fetchall()
    conn.close()
    return rows


def get_user_summary():
    """Admin — activity count per user grouped by mobile."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT username, mobile, COUNT(*) as total, MAX(timestamp) as last_seen "
        "FROM history GROUP BY mobile ORDER BY total DESC"
    ).fetchall()
    conn.close()
    return rows


def delete_record(record_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM history WHERE id=?", (record_id,))
    conn.commit()
    conn.close()


def update_record(record_id: int, activity: str, confidence: float):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE history SET activity=?, confidence=? WHERE id=?",
        (activity, round(float(confidence), 4), record_id)
    )
    conn.commit()
    conn.close()


def clear_all():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM history")
    conn.commit()
    conn.close()


def clear_user(username: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM history WHERE username=?", (username,))
    conn.commit()
    conn.close()


init_history_db()