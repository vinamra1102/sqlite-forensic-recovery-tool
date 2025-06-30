import sqlite3

def read_table_records(db_path, table_name, limit=50):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        query = f"SELECT * FROM {table_name} LIMIT {limit};"
        cursor.execute(query)

        column_names = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        conn.close()

        result = [dict(zip(column_names, row)) for row in rows]
        return result

    except Exception as e:
        print(f"[ERROR] Failed to read table: {e}")
        return []
