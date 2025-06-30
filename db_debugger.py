import sqlite3

db_path = "sample_dbs/messages.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM messages;")
    rows = cursor.fetchall()

    print(f"[✅] {len(rows)} rows found in 'messages' table:")
    for row in rows:
        print(row)

    conn.close()
except Exception as e:
    print(f"[❌] Error reading DB: {e}")
