import sqlite3

db_path = "sample_dbs/chinook_test.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()


cur.execute("SELECT * FROM Customer WHERE CustomerId = 12")
row = cur.fetchone()
print("Before delete:", row)


cur.execute("DELETE FROM Customer WHERE CustomerId = 12")
conn.commit()


cur.execute("SELECT * FROM Customer WHERE CustomerId = 12")
deleted = cur.fetchone()
print("After delete:", deleted)

conn.close()
exit()
