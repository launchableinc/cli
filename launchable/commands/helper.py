from time import time


def time_ns():
    # time.time_ns() method is new in Python version 3.7
    # As a workaround, we convert time.time() to nanoseconds.
    return int(time() * 1e9)
