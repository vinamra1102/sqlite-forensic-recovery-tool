import sqlite3

def extract_freeblocks(db_path, table_name, max_preview=200):
    """
    Scan every table-leaf page’s internal freeblock chain and return
    a list of dicts with page#, freeblock offset, block size, and ascii preview.
    """
    
    conn = sqlite3.connect(db_path)
    cols = [r[1] for r in conn.execute(f"PRAGMA table_info('{table_name}')")]
    conn.close()

    
    with open(db_path, "rb") as f:
        data = f.read()
    page_size = int.from_bytes(data[16:18], "big") or 65536
    total_pages = len(data) // page_size

    results = []
    
    for pageno in range(1, total_pages + 1):
        offset = pageno * page_size
        page = data[offset : offset + page_size]
        if not page or page[0] != 0x0D:
            continue  

        
        fb = int.from_bytes(page[1:3], "big")
        while fb:
            next_fb = int.from_bytes(page[fb : fb + 2], "big")
            size    = int.from_bytes(page[fb + 2 : fb + 4], "big")

            raw     = page[fb + 4 : fb + 4 + min(size - 4, max_preview)]
            preview = "".join(chr(b) if 32 <= b <= 126 else "." for b in raw)

            results.append({
                "page": pageno,
                "freeblock_offset": fb,
                "size": size,
                "ascii_preview": preview
            })
            fb = next_fb

    return results
