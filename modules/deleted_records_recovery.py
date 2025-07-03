import sqlite3
import struct

def recover_deleted_records(db_path, table_name):
    try:
        recovered_rows = []

        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(f"PRAGMA table_info('{table_name}')")
        columns_info = cursor.fetchall()
        col_names = [col[1] for col in columns_info]
        conn.close()

        
        with open(db_path, 'rb') as f:
            data = f.read()

        page_size = int.from_bytes(data[16:18], 'big')
        if page_size == 1:
            page_size = 65536

        first_trunk = int.from_bytes(data[32:36], 'big')
        if first_trunk == 0:
            return []

        visited = set()
        current_page = first_trunk

        while current_page != 0 and current_page not in visited:
            visited.add(current_page)
            offset = current_page * page_size
            if offset >= len(data): break

            page = data[offset:offset + page_size]
            next_trunk = int.from_bytes(page[0:4], 'big')
            leaf_count = int.from_bytes(page[4:8], 'big')

            cell_offset = 8  
            while cell_offset < page_size:
                
                try:
                    row_data = extract_record_from_bytes(page[cell_offset:], len(col_names))
                    if row_data:
                        recovered_rows.append(dict(zip(col_names, row_data)))
                except:
                    pass
                cell_offset += 10  

            current_page = next_trunk

        return recovered_rows

    except Exception as e:
        print(f"[❌] Recovery failed: {e}")
        return []

def extract_record_from_bytes(data, col_count):
    """
    Try to decode a row from raw bytes (simplified, assumes mostly TEXT).
    """
    
    values = []
    offset = 0

    for _ in range(col_count):
        if offset >= len(data): break
        length = data[offset]
        offset += 1
        value = data[offset:offset+length]
        try:
            values.append(value.decode('utf-8'))
        except:
            values.append(str(value))
        offset += length

    return values if values else None
