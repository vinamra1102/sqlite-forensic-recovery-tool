import sqlite3

db_path = "sample_dbs/messages.db"

def add_message(sender, content, timestamp):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO messages (sender, content, timestamp)
            VALUES (?, ?, ?)
        """, (sender, content, timestamp))

        conn.commit()
        conn.close()
        print("[✅] Message added successfully.")

    except Exception as e:
        print(f"[❌] Failed to add message: {e}")

if __name__ == "__main__":
    print("Add a new message to the messages table:")
    sender = input("Sender: ")
    content = input("Content: ")
    timestamp = input("Timestamp (YYYY-MM-DD HH:MM:SS): ")

    add_message(sender, content, timestamp)
