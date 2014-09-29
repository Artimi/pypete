import unittest
import timeit as ti
from functools import wraps, partial


def timeit(repeat=3, number=100):
    def decorator(f):
        @wraps(f)
        def wrapped_function(*args, **kwargs):
            f_measure = partial(f, *args, **kwargs)
            result = ti.repeat(f_measure, repeat=repeat, number=number)
            return result
        return wrapped_function
    return decorator


