import os
from modules.btree_parser import parse_leaf_page

def extract_wal_frames(wal_path, page_size=1024):
    with open(wal_path, "rb") as f:
        header = f.read(32)
        if not header.startswith(b"WAL\0"):
            raise ValueError("Invalid WAL header")

        wal_version = int.from_bytes(header[4:8], 'big')
        if wal_version != 3007000:
            raise ValueError("Unsupported WAL version")

        frame_count = int.from_bytes(header[24:28], 'big')

        frames = []
        for _ in range(frame_count):
            frame_header = f.read(24)
            if len(frame_header) < 24:
                break

            db_page = f.read(page_size)
            if len(db_page) < page_size:
                break

            frames.append({
                "page_no": int.from_bytes(frame_header[0:4], 'big'),
                "data": db_page
            })

        return frames

def recover_from_wal(wal_path, schema):
    try:
        page_size = 1024
        frames = extract_wal_frames(wal_path, page_size)
        recovered = []

        for frame in frames:
            data = frame["data"]
            if data[0] == 0x0D:
                rows = parse_leaf_page(data, schema)
                recovered.extend(rows)

        return recovered

    except Exception as e:
        print(f"[❌] WAL recovery failed: {e}")
        return []
