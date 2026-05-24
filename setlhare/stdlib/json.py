import json as _json

def parse(text): return _json.loads(text)
def stringify(value, pretty=False): return _json.dumps(value, indent=2 if pretty else None)
