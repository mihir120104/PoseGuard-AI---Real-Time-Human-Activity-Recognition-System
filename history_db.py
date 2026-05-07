# # # history_db.py

# # import sqlite3
# # from datetime import datetime

# # DB_PATH = "history.db"

# # def init_history_db():
# #     """Create the history table if it doesn't exist."""
# #     conn = sqlite3.connect(DB_PATH)
# #     c = conn.cursor()
# #     c.execute("""
# #         CREATE TABLE IF NOT EXISTS history (
# #             id         INTEGER PRIMARY KEY AUTOINCREMENT,
# #             activity   TEXT    NOT NULL,
# #             confidence REAL    NOT NULL,
# #             timestamp  TEXT    NOT NULL
# #         )
# #     """)
# #     conn.commit()
# #     conn.close()


# # def save_history(activity: str, confidence: float):
# #     """Insert one activity record with current timestamp."""
# #     conn = sqlite3.connect(DB_PATH)
# #     c = conn.cursor()
# #     c.execute(
# #         "INSERT INTO history (activity, confidence, timestamp) VALUES (?, ?, ?)",
# #         (activity, round(float(confidence), 4), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
# #     )
# #     conn.commit()
# #     conn.close()


# # def get_history():
# #     """Return all rows as a list of tuples: (id, activity, confidence, timestamp)."""
# #     conn = sqlite3.connect(DB_PATH)
# #     c = conn.cursor()
# #     c.execute("SELECT id, activity, confidence, timestamp FROM history ORDER BY id DESC")
# #     rows = c.fetchall()
# #     conn.close()
# #     return rows


# # def delete_record(record_id: int):
# #     """Delete a single record by ID."""
# #     conn = sqlite3.connect(DB_PATH)
# #     conn.execute("DELETE FROM history WHERE id=?", (record_id,))
# #     conn.commit()
# #     conn.close()


# # def update_record(record_id: int, activity: str, confidence: float):
# #     """Update activity and confidence for a given record."""
# #     conn = sqlite3.connect(DB_PATH)
# #     conn.execute(
# #         "UPDATE history SET activity=?, confidence=? WHERE id=?",
# #         (activity, round(float(confidence), 4), record_id)
# #     )
# #     conn.commit()
# #     conn.close()


# # def clear_all():
# #     """Delete every row in the history table."""
# #     conn = sqlite3.connect(DB_PATH)
# #     conn.execute("DELETE FROM history")
# #     conn.commit()
# #     conn.close()


# # # Auto-initialise on import
# # init_history_db()

# """
# history_db.py — Production
# Activity history database with per-user support.
# """
# import sqlite3
# from datetime import datetime

# DB_PATH = "history.db"


# def init_history_db():
#     conn = sqlite3.connect(DB_PATH)
#     conn.execute("""
#         CREATE TABLE IF NOT EXISTS history (
#             id         INTEGER PRIMARY KEY AUTOINCREMENT,
#             username   TEXT    NOT NULL DEFAULT 'unknown',
#             activity   TEXT    NOT NULL,
#             confidence REAL    NOT NULL,
#             timestamp  TEXT    NOT NULL
#         )
#     """)
#     # Add username column if upgrading from old schema
#     try:
#         conn.execute("ALTER TABLE history ADD COLUMN username TEXT NOT NULL DEFAULT 'unknown'")
#     except Exception:
#         pass
#     conn.commit()
#     conn.close()


# def save_history(activity: str, confidence: float, username: str = "unknown"):
#     conn = sqlite3.connect(DB_PATH)
#     conn.execute(
#         "INSERT INTO history (username, activity, confidence, timestamp) VALUES (?, ?, ?, ?)",
#         (username, activity, round(float(confidence), 4),
#          datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
#     )
#     conn.commit()
#     conn.close()


# def get_history(username: str = None):
#     """Return all rows or rows for a specific user."""
#     conn = sqlite3.connect(DB_PATH)
#     if username and username != "admin":
#         rows = conn.execute(
#             "SELECT id, activity, confidence, timestamp FROM history "
#             "WHERE username=? ORDER BY id DESC", (username,)
#         ).fetchall()
#     else:
#         rows = conn.execute(
#             "SELECT id, activity, confidence, timestamp FROM history ORDER BY id DESC"
#         ).fetchall()
#     conn.close()
#     return rows


# def get_history_with_users():
#     """Admin only — returns all records with username column."""
#     conn = sqlite3.connect(DB_PATH)
#     rows = conn.execute(
#         "SELECT id, username, activity, confidence, timestamp FROM history ORDER BY id DESC"
#     ).fetchall()
#     conn.close()
#     return rows


# def delete_record(record_id: int):
#     conn = sqlite3.connect(DB_PATH)
#     conn.execute("DELETE FROM history WHERE id=?", (record_id,))
#     conn.commit()
#     conn.close()


# def update_record(record_id: int, activity: str, confidence: float):
#     conn = sqlite3.connect(DB_PATH)
#     conn.execute(
#         "UPDATE history SET activity=?, confidence=? WHERE id=?",
#         (activity, round(float(confidence), 4), record_id)
#     )
#     conn.commit()
#     conn.close()


# def clear_all():
#     conn = sqlite3.connect(DB_PATH)
#     conn.execute("DELETE FROM history")
#     conn.commit()
#     conn.close()


# def clear_user(username: str):
#     conn = sqlite3.connect(DB_PATH)
#     conn.execute("DELETE FROM history WHERE username=?", (username,))
#     conn.commit()
#     conn.close()


# def get_user_summary():
#     """Admin — activity count per user."""
#     conn = sqlite3.connect(DB_PATH)
#     rows = conn.execute(
#         "SELECT username, COUNT(*) as total, "
#         "MAX(timestamp) as last_seen "
#         "FROM history GROUP BY username ORDER BY total DESC"
#     ).fetchall()
#     conn.close()
#     return rows


# init_history_db()

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
Activity history database with per-user support.
"""
import sqlite3
from datetime import datetime

DB_PATH = "history.db"


def init_history_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT    NOT NULL DEFAULT 'unknown',
            activity   TEXT    NOT NULL,
            confidence REAL    NOT NULL,
            timestamp  TEXT    NOT NULL
        )
    """)
    # Add username column if upgrading from old schema
    try:
        conn.execute("ALTER TABLE history ADD COLUMN username TEXT NOT NULL DEFAULT 'unknown'")
    except Exception:
        pass
    conn.commit()
    conn.close()


def save_history(activity: str, confidence: float,
                 username: str = "unknown",
                 mobile: str = ""):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO history (username, activity, confidence, timestamp) VALUES (?, ?, ?, ?)",
        (username, activity, round(float(confidence), 4),
         datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


def get_history(username: str = None, mobile: str = None):
    """Return all rows or rows for a specific user."""
    conn = sqlite3.connect(DB_PATH)
    if username and username != "admin":
        rows = conn.execute(
            "SELECT id, activity, confidence, timestamp FROM history "
            "WHERE username=? ORDER BY id DESC", (username,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, activity, confidence, timestamp FROM history ORDER BY id DESC"
        ).fetchall()
    conn.close()
    return rows


def get_history_with_users():
    """Admin only — returns all records with username column."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, username, activity, confidence, timestamp FROM history ORDER BY id DESC"
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


def get_user_summary():
    """Admin — activity count per user."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT username, COUNT(*) as total, "
        "MAX(timestamp) as last_seen "
        "FROM history GROUP BY username ORDER BY total DESC"
    ).fetchall()
    conn.close()
    return rows


init_history_db()
def register_user(name: str, mobile: str):
    pass


def update_last_seen(mobile: str):
    pass