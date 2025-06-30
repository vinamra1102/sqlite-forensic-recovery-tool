import hashlib

def is_valid_sqlite(file_path):
    try:
        with open(file_path, 'rb') as f:
            magic = f.read(16)
        return magic.startswith(b'SQLite format 3')
    except:
        return False

def get_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(block)
    return sha256_hash.hexdigest()
