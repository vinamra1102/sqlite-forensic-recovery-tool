import sqlite3
import os


os.makedirs("sample_dbs", exist_ok=True)


db_path = "sample_dbs/messages.db"


conn = sqlite3.connect(db_path)
cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT NOT NULL,
    content TEXT,
    timestamp TEXT
);
""")


sample_data = [
    ("Alice", "Hello Bob!", "2023-01-01 10:00:00"),
    ("Bob", "Hi Alice!", "2023-01-01 10:05:00"),
    ("Charlie", "What's up?", "2023-01-01 10:10:00")
]

cursor.executemany("INSERT INTO messages (sender, content, timestamp) VALUES (?, ?, ?)", sample_data)

conn.commit()
conn.close()

print(f"[✅] Sample DB created at {db_path}")
