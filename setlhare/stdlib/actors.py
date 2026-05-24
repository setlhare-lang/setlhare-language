from __future__ import annotations

import queue
import threading
from dataclasses import dataclass


@dataclass
class Task:
    thread: threading.Thread

    def join(self):
        self.thread.join()


class Actor:
    def __init__(self):
        self.mailbox = queue.Queue()
        self.alive = True

    def send(self, message):
        self.mailbox.put(message)
        return self

    def receive(self, timeout=None):
        return self.mailbox.get(timeout=timeout)


def spawn(fn, *args, **kwargs):
    t = threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True)
    t.start()
    return Task(t)


def go(fn, *args, **kwargs):
    return spawn(fn, *args, **kwargs)
