"""
clean_labels.py
Run ONCE to normalize all existing activity labels in history.db.
Fixes: "no" / "no_activity" / "No Activity" all become "No Activity"
       "Drinking" / "drinking" both become "Drinking"  etc.

Run: python clean_labels.py
"""
import sqlite3

DB = "history.db"

NORMALIZE = {
    "no":             "no_activity",
    "No Activity":    "no_activity",
    "no activity":    "no_activity",
    "No_Activity":    "no_activity",
    "drinking":       "Drinking",
    "Eating":         "eating",
    "Exercise":       "exercise",
    "Fighting":       "fighting",
    "Typing":         "Typing",
    "writingonboard": "WritingOnBoard",
    "Writing on Board":"WritingOnBoard",
    "writing on board":"WritingOnBoard",
}

conn = sqlite3.connect(DB)
fixed = 0
for old, new in NORMALIZE.items():
    cur = conn.execute(
        "UPDATE history SET activity=? WHERE activity=?", (new, old)
    )
    if cur.rowcount > 0:
        print(f"  {old!r:25} → {new!r}  ({cur.rowcount} rows)")
        fixed += cur.rowcount

conn.commit()
conn.close()
print(f"\n {fixed} records normalized. Restart Streamlit to see the fix.")