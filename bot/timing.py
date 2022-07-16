from functools import wraps
from time import time


def timing_wrap(results: list[float]):
    def timing(f):
        @wraps(f)
        def wrap(*args, **kw):
            ts = time()
            result = f(*args, **kw)
            te = time()
            results.append(te - ts)
            return result
        return wrap
    return timing
