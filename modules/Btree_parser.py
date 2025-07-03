import sqlite3

def parse_varint(data, offset):
    v = 0
    for i in range(9):
        b = data[offset + i]
        v = (v << 7) | (b & 0x7F)
        if not (b & 0x80):
            return v, i + 1
    return v, 9

def parse_serial_types(header_bytes, count):
    types, off = [], 0
    for _ in range(count):
        t, n = parse_varint(header_bytes, off)
        types.append(t); off += n
    return types

def parse_record_values(data, types):
    vals, off = [], 0
    for t in types:
        if t == 0:
            vals.append(None)
        elif 1 <= t <= 6:
            size = (1,2,3,4,6,8)[t-1]
            vals.append(int.from_bytes(data[off:off+size],'big'))
            off += size
        elif t == 8:
            vals.append(0)
        elif t == 9:
            vals.append(1)
        elif t >= 13 and t%2==1:
            ln = (t-13)//2
            chunk = data[off:off+ln]
            try: vals.append(chunk.decode())
            except: vals.append(chunk)
            off += ln
        else:
            vals.append(f"<type {t}>")
    return vals

def parse_leaf_page(page, schema):
    rows = []
    cell_count = int.from_bytes(page[3:5],'big')
    ptrs = [int.from_bytes(page[8+2*i:10+2*i],'big') for i in range(cell_count)]
    for p in ptrs:
        try:
            payload_size, n1 = parse_varint(page, p)
            _, n2 = parse_varint(page, p+n1)
            hdr_sz, n3 = parse_varint(page, p+n1+n2)
            hdr = page[p+n1+n2 : p+n1+n2+n3-1]
            types = parse_serial_types(hdr, len(schema))
            content = page[p+n1+n2+n3-1 : p+n1+n2+n3-1+payload_size]
            vals = parse_record_values(content, types)
            rows.append(dict(zip(schema, vals)))
        except:
            continue
    return rows


def recover_from_freeblocks(db_path, table_name):
    """Scan every table-leaf page’s freeblocks to recover deleted rows."""
    conn = sqlite3.connect(db_path)
    schema = [r[1] for r in conn.execute(f"PRAGMA table_info('{table_name}')")]
    conn.close()

    data = open(db_path,'rb').read()
    page_size = int.from_bytes(data[16:18],'big') or 65536
    total_pages = len(data) // page_size
    recovered = []

    for pg in range(1, total_pages+1):
        off = pg * page_size
        page = data[off:off+page_size]
        if not page or page[0] != 0x0D:
            continue

        fb = int.from_bytes(page[1:3],'big')
        while fb:
            
            nxt = int.from_bytes(page[fb:fb+2],'big')
            sz  = int.from_bytes(page[fb+2:fb+4],'big')
            blob = page[fb+4 : fb+4+(sz-4)]
            try:
                
                payload, n1 = parse_varint(blob, 0)
                _, n2    = parse_varint(blob, n1)
                hdr_sz, n3 = parse_varint(blob, n1+n2)
                hdr = blob[n1+n2 : n1+n2+n3-1]
                types = parse_serial_types(hdr, len(schema))
                cont = blob[n1+n2+n3-1 : n1+n2+n3-1+payload]
                vals = parse_record_values(cont, types)
                recovered.append(dict(zip(schema, vals)))
            except:
                pass
            fb = nxt

    return recovered
