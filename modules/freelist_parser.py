def extract_freelist_pages(db_path):
    try:
        with open(db_path, 'rb') as f:
            data = f.read()

        page_size = int.from_bytes(data[16:18], byteorder='big')
        if page_size == 1:
            page_size = 65536

        first_trunk = int.from_bytes(data[32:36], byteorder='big')
        if first_trunk == 0:
            return []

        results = []
        visited = set()
        current = first_trunk

        while current != 0 and current not in visited:
            visited.add(current)
            offset = current * page_size
            if offset >= len(data): break

            page = data[offset:offset + page_size]
            next_trunk = int.from_bytes(page[0:4], 'big')
            leaf_count = int.from_bytes(page[4:8], 'big')

            ascii_preview = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in page[:200])
            results.append({
                'page': current,
                'leaf_count': leaf_count,
                'ascii_preview': ascii_preview
            })

            current = next_trunk

        return results
    except Exception as e:
        print(f"[ERROR] Freelist parsing failed: {e}")
        return []
