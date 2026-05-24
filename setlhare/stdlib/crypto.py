import hashlib

def sha256(text): return hashlib.sha256(str(text).encode()).hexdigest()
def hash(text): return sha256(text)
