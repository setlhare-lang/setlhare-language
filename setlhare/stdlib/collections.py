from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor

class List(list):
    def map(self, fn): return List(fn(x) for x in self)
    def filter(self, fn): return List(x for x in self if fn(x))
    def reduce(self, fn, initial=None):
        it = iter(self)
        acc = next(it) if initial is None else initial
        for x in it: acc = fn(acc, x)
        return acc
    def sum(self): return sum(self)
    def parallel(self, n=4): return ParallelList(self, n)

class ParallelList(List):
    def __init__(self, values, workers=4):
        super().__init__(values); self.workers = workers
    def map(self, fn):
        with ThreadPoolExecutor(max_workers=self.workers) as ex:
            return List(ex.map(fn, self))

def list_of(*items): return List(items)
def parallel(items, n=4): return ParallelList(items, n)
