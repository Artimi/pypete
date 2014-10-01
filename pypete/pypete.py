from __future__ import division
import timeit as ti
from functools import wraps, partial
from nose.plugins.base import Plugin
import logging


log = logging.getLogger('nose.plugins.pypete')

def timeit(repeat=3, number=100):
    def decorator(f):
        @wraps(f)
        def wrapped_function(*args, **kwargs):
            f_measure = partial(f, *args, **kwargs)
            result = ti.repeat(f_measure, repeat=repeat, number=number)
            return result
        return wrapped_function
    return decorator

def test_class(cls):
    '''
    Class decorator that states that this class should be tested
    '''
    class NewClass(cls):
        pypete_testing = True
    return NewClass


class Pypete(Plugin):
    '''
    Nose plugin for handling performance testing
    '''
    name = 'pypete'

    def options(self, parser, env):
        super(Pypete, self).options(parser, env)
        # TODO add options

    def configure(self, options, conf):
        super(Pypete, self).configure(options, conf)
        self.repeat = 3
        self.number = 10

    def prepareTestCase(self, test):
        # TODO: add running timeit
        timing = ti.repeat(test.test, setup=test.test.setUp,
                           repeat=self.repeat, number=self.number)
        stats = self.process_timing(timing, self.repeat, self.number)
        log.info(stats)

    def process_timing(self, timing, repeat, number):
        stats = {'best': min(timing)/number,
                 'worst': max(timing)/number,
                 'average': sum(timing)/repeat/number}
        return stats

    def report(self, stream):
        # TODO: show every test performance statistics
        pass

