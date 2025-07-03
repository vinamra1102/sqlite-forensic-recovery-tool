import sqlite3

def parse_varint(data, offset):
    value = 0
    for i in range(9):
        byte = data[offset + i]
        value = (value << 7) | (byte & 0x7F)
        if not (byte & 0x80):
            return value, i + 1
    return value, 9

def parse_serial_types(header_bytes, count):
    types = []
    offset = 0
    for _ in range(count):
        serial_type, size = parse_varint(header_bytes, offset)
        types.append(serial_type)
        offset += size
    return types

def parse_record_values(data, types):
    values = []
    offset = 0
    for t in types:
        if t == 0:
            values.append(None)
        elif t == 1:
            values.append(int.from_bytes(data[offset:offset+1], 'big'))
            offset += 1
        elif t == 2:
            values.append(int.from_bytes(data[offset:offset+2], 'big'))
            offset += 2
        elif t == 3:
            values.append(int.from_bytes(data[offset:offset+3], 'big'))
            offset += 3
        elif t == 4:
            values.append(int.from_bytes(data[offset:offset+4], 'big'))
            offset += 4
        elif t == 5:
            values.append(int.from_bytes(data[offset:offset+6], 'big'))
            offset += 6
        elif t == 6:
            values.append(int.from_bytes(data[offset:offset+8], 'big'))
            offset += 8
        elif t == 8:
            values.append(0)
        elif t == 9:
            values.append(1)
        elif t >= 13 and t % 2 == 1:
            length = (t - 13) // 2
            try:
                values.append(data[offset:offset+length].decode('utf-8'))
            except:
                values.append(data[offset:offset+length])
            offset += length
        else:
            values.append(f"<unhandled type {t}>")
    return values

def parse_leaf_page(page_data, schema):
    results = []
    num_cells = int.from_bytes(page_data[3:5], 'big')
    cell_ptrs = [int.from_bytes(page_data[8 + 2*i: 10 + 2*i], 'big') for i in range(num_cells)]
    col_count = len(schema)

    for ptr in cell_ptrs:
        try:
            payload_size, n = parse_varint(page_data, ptr)
            rowid, m = parse_varint(page_data, ptr + n)
            header_size, h = parse_varint(page_data, ptr + n + m)
            header_bytes = page_data[ptr + n + m : ptr + n + m + header_size - 1]
            serial_types = parse_serial_types(header_bytes, col_count)
            content_start = ptr + n + m + header_size - 1
            content_bytes = page_data[content_start: content_start + payload_size]
            row = parse_record_values(content_bytes, serial_types)
            results.append(dict(zip(schema, row)))
        except Exception:
            continue
    return results

def recover_deleted_rows(db_path, table_name):
    try:
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
        recovered_rows = []

        while current_page != 0 and current_page not in visited:
            visited.add(current_page)
            offset = current_page * page_size
            if offset >= len(data):
                break

            page = data[offset:offset + page_size]
            next_trunk = int.from_bytes(page[0:4], 'big')
            leaf_count = int.from_bytes(page[4:8], 'big')

            leaf_ptrs = []
            for i in range(leaf_count):
                start = 8 + (i * 4)
                ptr = int.from_bytes(page[start:start+4], 'big')
                if ptr not in visited:
                    leaf_ptrs.append(ptr)

            for leaf_page in leaf_ptrs:
                off = leaf_page * page_size
                if off + page_size > len(data):
                    continue
                page_data = data[off:off + page_size]
                page_type = page_data[0]
                if page_type == 0x0D:
                    rows = parse_leaf_page(page_data, col_names)
                    recovered_rows.extend(rows)

            current_page = next_trunk

        return recovered_rows

    except Exception as e:
        print(f"[❌] Structured deleted recovery failed: {e}")
        return []
