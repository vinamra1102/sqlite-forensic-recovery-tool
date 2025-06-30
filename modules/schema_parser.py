import sqlite3

def get_tables_and_columns(db_path):
    table_schema = {}
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for (table_name,) in tables:
            cursor.execute(f"PRAGMA table_info('{table_name}');")
            columns = cursor.fetchall()
            col_names = [col[1] for col in columns]
            table_schema[table_name] = col_names

        conn.close()
        return table_schema
    except Exception as e:
        print(f"[ERROR] Failed to extract schema: {e}")
        return {}
