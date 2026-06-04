"""
history_db.py — Production (IST timezone fix)
Saves all timestamps in India Standard Time (UTC+5:30)
"""
import sqlite3, os
from datetime import datetime, timezone, timedelta

DB_PATH = "history.db"
HF_API  = "https://mihir1201-poseguard-api.hf.space"

# India Standard Time = UTC + 5:30
IST = timezone(timedelta(hours=5, minutes=30))

def now_ist():
    """Return current time in IST as string."""
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")

IS_HF     = bool(os.environ.get("SPACE_ID"))
IS_RENDER = not IS_HF


def init_history_db():
    conn = sqlite3.connect(DB_PATH)
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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS registered_users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            mobile     TEXT NOT NULL UNIQUE,
            registered TEXT NOT NULL,
            last_seen  TEXT NOT NULL
        )
    """)
    for col, default in [("mobile", "''"), ("username", "'unknown'")]:
        try:
            conn.execute(f"ALTER TABLE history ADD COLUMN {col} TEXT NOT NULL DEFAULT {default}")
        except:
            pass
    conn.commit()
    conn.close()


def register_user(name: str, mobile: str):
    conn = sqlite3.connect(DB_PATH)
    now  = now_ist()
    conn.execute("""
        INSERT INTO registered_users (name, mobile, registered, last_seen)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(mobile) DO UPDATE SET name=excluded.name, last_seen=excluded.last_seen
    """, (name.strip(), mobile.strip(), now, now))
    conn.commit()
    conn.close()


def update_last_seen(mobile: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE registered_users SET last_seen=? WHERE mobile=?",
        (now_ist(), mobile.strip())
    )
    conn.commit()
    conn.close()


def save_history(activity: str, confidence: float,
                 username: str = "unknown", mobile: str = ""):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO history (username, mobile, activity, confidence, timestamp) VALUES (?,?,?,?,?)",
        (username, mobile, activity, round(float(confidence), 4), now_ist())
    )
    conn.commit()
    conn.close()


def _fetch_hf(endpoint: str, params: dict = None):
    try:
        import requests
        r = requests.get(f"{HF_API}{endpoint}", params=params, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"HF fetch error: {e}")
    return None


def get_history(username: str = None, mobile: str = None):
    if IS_RENDER:
        params = {}
        if username and username != "admin": params["username"] = username
        if mobile: params["mobile"] = mobile
        data = _fetch_hf("/db/history", params)
        if data and "rows" in data:
            return [tuple(r) for r in data["rows"]]
        return []
    conn = sqlite3.connect(DB_PATH)
    if username == "admin" or (not username and not mobile):
        rows = conn.execute(
            "SELECT id, activity, confidence, timestamp FROM history ORDER BY id DESC"
        ).fetchall()
    elif mobile:
        rows = conn.execute(
            "SELECT id, activity, confidence, timestamp FROM history "
            "WHERE mobile=? ORDER BY id DESC", (mobile,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, activity, confidence, timestamp FROM history "
            "WHERE username=? ORDER BY id DESC", (username,)
        ).fetchall()
    conn.close()
    return rows


def get_history_with_users():
    if IS_RENDER:
        data = _fetch_hf("/db/history_with_users")
        if data and "rows" in data:
            return [tuple(r) for r in data["rows"]]
        return []
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, username, mobile, activity, confidence, timestamp "
        "FROM history ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return rows


def get_registered_users():
    if IS_RENDER:
        data = _fetch_hf("/db/registered_users")
        if data and "rows" in data:
            return [tuple(r) for r in data["rows"]]
        return []
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, name, mobile, registered, last_seen "
        "FROM registered_users ORDER BY last_seen DESC"
    ).fetchall()
    conn.close()
    return rows


def get_user_summary():
    if IS_RENDER:
        data = _fetch_hf("/db/user_summary")
        if data and "rows" in data:
            return [tuple(r) for r in data["rows"]]
        return []
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
    conn.commit(); conn.close()


def update_record(record_id: int, activity: str, confidence: float):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE history SET activity=?, confidence=? WHERE id=?",
        (activity, round(float(confidence), 4), record_id)
    )
    conn.commit(); conn.close()


def clear_all():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM history")
    conn.commit(); conn.close()


def clear_user(username: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM history WHERE username=?", (username,))
    conn.commit(); conn.close()


init_history_db()