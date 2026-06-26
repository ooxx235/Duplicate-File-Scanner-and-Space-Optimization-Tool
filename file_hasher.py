import hashlib

def calculate_sha256(filepath, chunk_size=65536):
    sha256_hash = hashlib.sha256()
    try:
        # 必須使用 'rb' (Read Binary) 模式，以最底層的位元組來解讀檔案
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        return None
