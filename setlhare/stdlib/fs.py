from pathlib import Path

def read_text(path): return Path(path).read_text(encoding="utf-8")
def write_text(path, text): Path(path).write_text(text, encoding="utf-8"); return None
def exists(path): return Path(path).exists()
def lines(path): return read_text(path).splitlines()
