import time as _time

def now(): return _time.time()
def sleep(seconds): _time.sleep(seconds)
def millis(): return int(_time.time() * 1000)
