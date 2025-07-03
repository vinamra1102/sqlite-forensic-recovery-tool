import sqlite3

db_path = "sample_dbs/messages.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    
    print("[ℹ️] Messages before delete:")
    for row in cursor.execute("SELECT * FROM messages;"):
        print(row)

    
    cursor.execute("DELETE FROM messages WHERE id = 199;")
    conn.commit()

    print("\n[🗑️] Deleted message with ID = 199.")

    
    print("\n[📄] Messages after delete:")
    for row in cursor.execute("SELECT * FROM messages;"):
        print(row)

    conn.close()

except Exception as e:
    print(f"[❌] Error: {e}")
