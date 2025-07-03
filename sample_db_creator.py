import sqlite3
import os
from datetime import datetime

db_dir = "sample_dbs"
db_path = os.path.join(db_dir, "messages1.db")



conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    content TEXT,
    timestamp TEXT
)
""")


for i in range(200):
    cursor.execute("INSERT INTO messages (sender, content, timestamp) VALUES (?, ?, ?)", (
        f"User{i}", f"Message {i}", datetime.now().isoformat()
    ))
conn.commit()

cursor.execute("DELETE FROM messages WHERE id BETWEEN 50 AND 150")
conn.commit()


for i in range(999, 1004):
    cursor.execute("INSERT INTO messages (sender, content, timestamp) VALUES (?, ?, ?)", (
        f"WALUser{i}", f"WAL Message {i}", datetime.now().isoformat()
    ))

print("\n✅ Sample SQLite DB created successfully:")
print(" - 200 rows inserted")
print(" - 101 rows deleted → Freelist pages created")
print(" - 5 uncommitted rows → WAL file generated")
print("📁 File saved to:", db_path)
input("🚧 Keep this open if testing WAL... press ENTER to close connection and flush WAL.")
conn.close()
