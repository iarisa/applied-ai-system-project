"""
Small terminal spinner so a blocking network call (the Agent's Gemini
request) shows visible activity instead of looking like the terminal froze.
"""

import itertools
import threading
import time
from contextlib import contextmanager

_SPINNER_FRAMES = "|/-\\"
_TICK_SECONDS = 0.1


@contextmanager
def spinner(message: str):
    stop = threading.Event()

    def _spin():
        for frame in itertools.cycle(_SPINNER_FRAMES):
            if stop.is_set():
                break
            print(f"\r{message} {frame}", end="", flush=True)
            time.sleep(_TICK_SECONDS)
        print(f"\r{' ' * (len(message) + 2)}\r", end="", flush=True)

    thread = threading.Thread(target=_spin, daemon=True)
    thread.start()
    try:
        yield
    finally:
        stop.set()
        thread.join()
